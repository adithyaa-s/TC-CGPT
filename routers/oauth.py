from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import os
import requests
import uuid

from utils.user_oauth import store_tokens, get_tokens

router = APIRouter()


@router.get("/auth/login")
async def auth_login():
    """Redirect user to Zoho authorization page.

    The redirect URI is taken from the `OAUTH_REDIRECT_URI` env var or
    falls back to `http://localhost:8000/auth/callback` for local testing.
    """
    client_id = os.getenv("CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="CLIENT_ID not configured")

    redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
    scope = os.getenv("OAUTH_SCOPE", "TrainerCentral.sessionapi.ALL,TrainerCentral.sectionapi.ALL,TrainerCentral.courseapi.ALL,TrainerCentral.userapi.ALL,TrainerCentral.talkapi.ALL")

    params = {
        "scope": scope,
        "client_id": client_id,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "redirect_uri": redirect_uri,
    }

    url = "https://accounts.zoho.in/oauth/v2/auth"
    auth_url = requests.Request('GET', url, params=params).prepare().url

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
async def auth_callback(request: Request, response: Response, code: str = None, error: str = None):
    """Exchange authorization code for tokens and return a session id.

    This endpoint stores the returned tokens in an in-memory store and sets
    a `session_id` cookie. For production you should persist tokens
    securely and tie them to a user account.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

    token_url = "https://accounts.zoho.in/oauth/v2/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    resp = requests.post(token_url, data=data)
    try:
        result = resp.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid token response")

    if "access_token" not in result:
        raise HTTPException(status_code=500, detail={"token_error": result})

    session_id = str(uuid.uuid4())
    store_tokens(session_id, result)

    # set a cookie for the session id so the UI can use it for subsequent calls
    response = JSONResponse({"message": "OAuth successful", "session_id": session_id})
    response.set_cookie("session_id", session_id, httponly=True)
    return response


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
