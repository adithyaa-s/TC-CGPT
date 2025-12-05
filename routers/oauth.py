from fastapi import APIRouter, Request, Response, HTTPException, Form
from fastapi.responses import RedirectResponse, JSONResponse
import os
import requests
import uuid
import json
import urllib.parse

from utils.user_oauth import store_tokens, get_tokens

router = APIRouter()


def _is_chatgpt_callback(uri: str) -> bool:
    return uri.startswith("https://chat.openai.com/aip/")


@router.get("/auth/login")
async def auth_login(redirect_uri: str | None = None, state: str | None = None):
    """Redirect user to Zoho authorization page.

    For the direct ChatGPT flow (method B) ChatGPT will open this URL and
    provide `redirect_uri` (the ChatGPT callback) and `state`. We must pass
    ChatGPT's `redirect_uri` to the provider so the provider redirects
    directly to ChatGPT after consent.
    """
    client_id = os.getenv("CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="CLIENT_ID not configured")

    if not redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri is required")

    if not _is_chatgpt_callback(redirect_uri):
        raise HTTPException(status_code=400, detail="redirect_uri must be a ChatGPT callback (https://chat.openai.com/aip/...) when using CustomGPT OAuth")

    scope = os.getenv("OAUTH_SCOPE", "TrainerCentral.sessionapi.ALL,TrainerCentral.sectionapi.ALL,TrainerCentral.courseapi.ALL,TrainerCentral.userapi.ALL,TrainerCentral.talkapi.ALL")

    params = {
        "scope": scope,
        "client_id": client_id,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "redirect_uri": redirect_uri,
    }

    if state:
        params["state"] = state

    url = "https://accounts.zoho.in/oauth/v2/auth"
    auth_url = requests.Request("GET", url, params=params).prepare().url

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
async def auth_callback(request: Request, response: Response, code: str | None = None, error: str | None = None, state: str | None = None):
    """Exchange authorization code for tokens and then redirect to ChatGPT (if provided).

    Flow:
    - Exchange Zoho `code` for access/refresh tokens.
    - Create a one-time auth code that ChatGPT (CustomGPT) can exchange.
    - If the incoming `state` contains a `chat_redirect`, redirect user to it
      with query `code=<auth_code>&state=<chat_state>`.
    - Otherwise, set `session_id` cookie and return JSON (legacy behaviour).
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    provider_callback = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

    # Exchange code with provider and return an informational response.
    provider_callback = os.getenv("OAUTH_REDIRECT_URI", "")
    token_url = "https://accounts.zoho.in/oauth/v2/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": provider_callback,
    }

    resp = requests.post(token_url, data=data)
    try:
        result = resp.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid token response from provider")

    if "access_token" not in result:
        raise HTTPException(status_code=500, detail={"token_error": result})

    # In direct ChatGPT flow the provider will redirect directly to ChatGPT
    # (we don't need to create an intermediate auth code). Return a simple
    # page indicating success — ChatGPT will receive the provider code and
    # continue the flow by calling your `/auth/token`.
    return JSONResponse({"message": "Provider callback received; tokens exchanged on token endpoint"})


@router.post("/auth/token")
async def token_exchange(grant_type: str = Form(...), code: str = Form(None), redirect_uri: str | None = Form(None), client_id: str | None = Form(None), client_secret: str | None = Form(None)):
    """Exchange a one-time auth code (created by /auth/callback) for tokens.

    This endpoint implements the token endpoint that ChatGPT will call
    when exchanging the auth code it received after user consent.
    Expected form fields (for the authorization_code grant):
      - grant_type=authorization_code
      - code=<auth_code>
      - redirect_uri (optional)
      - client_id / client_secret (optional, depending on your manifest)
    """
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="unsupported_grant_type")

    if not code:
        raise HTTPException(status_code=400, detail="missing_code")

    expected_client = os.getenv("CLIENT_ID")
    expected_secret = os.getenv("CLIENT_SECRET")
    if client_id and client_id != expected_client:
        raise HTTPException(status_code=401, detail="invalid_client")
    if client_secret and client_secret != expected_secret:
        raise HTTPException(status_code=401, detail="invalid_client")

    # Exchange the provider code with Zoho for tokens. ChatGPT sends the
    # same redirect_uri it used during the authorization request; we must
    # pass it through when exchanging the code.
    token_url = "https://accounts.zoho.in/oauth/v2/token"
    data = {
        "code": code,
        "client_id": expected_client,
        "client_secret": expected_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    resp = requests.post(token_url, data=data)
    try:
        result = resp.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid token response from provider")

    if "access_token" not in result:
        raise HTTPException(status_code=400, detail={"token_error": result})

    return {
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token"),
        "expires_in": int(result.get("expires_in", 3600)),
        "token_type": result.get("token_type", "Bearer"),
        "scope": result.get("scope"),
    }


@router.get("/auth/session_tokens")
async def session_tokens(request: Request):
    """Return stored tokens for the current session (for debugging/demo).

    In production do not expose raw tokens like this.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="No session cookie")

    tokens = get_tokens(session_id)
    if tokens is None:
        raise HTTPException(status_code=404, detail="No tokens for session")

    return {"session_id": session_id, "tokens": tokens}
