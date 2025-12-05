"""Simple in-memory store for user OAuth tokens and temporary auth codes.

This is intentionally minimal for demo purposes. For production you should
store tokens in a secure persistent store and associate them with user
accounts. Additionally, auth codes should be short-lived and one-time-use.
"""
from typing import Optional, Dict, Any
import time
import uuid

# session_id -> tokens
_TOKEN_STORE: Dict[str, Dict[str, Any]] = {}

# auth_code -> { tokens, expires_at }
_AUTH_CODE_STORE: Dict[str, Dict[str, Any]] = {}

# User org info (org_id, domain) - fetched from portals API
_USER_ORG_INFO: Dict[str, Any] = {"org_id": None, "domain": None}


def store_tokens(session_id: str, tokens: dict) -> None:
    _TOKEN_STORE[session_id] = tokens


def get_tokens(session_id: str) -> Optional[dict]:
    return _TOKEN_STORE.get(session_id)


def clear_tokens(session_id: str) -> None:
    _TOKEN_STORE.pop(session_id, None)


def store_user_org_info(org_id: str, domain: str) -> None:
    """Store user's org ID and domain fetched from portals API.
    
    NOTE: This is a global store for MVP. In production, associate
    org info with the user session or account.
    
    Args:
        org_id: Organization ID from portals.json response
        domain: TrainerCentral domain (e.g., https://testingtrainercentral.trainercentral.in)
    """
    global _USER_ORG_INFO
    _USER_ORG_INFO["org_id"] = org_id
    _USER_ORG_INFO["domain"] = domain


def get_user_org_info() -> Dict[str, Any]:
    """Get stored org ID and domain.
    
    Returns:
        dict with keys 'org_id' and 'domain'
    """
    return _USER_ORG_INFO.copy()


def create_auth_code(tokens: dict, expires_in: int = 60) -> str:
    """Create a one-time auth code that can be exchanged for tokens.

    Returns the auth code string.
    """
    code = uuid.uuid4().hex
    expires_at = time.time() + expires_in
    _AUTH_CODE_STORE[code] = {"tokens": tokens, "expires_at": expires_at}
    return code


def consume_auth_code(code: str) -> Optional[dict]:
    """Consume (validate + remove) an auth code and return associated tokens.

    Returns None if code is invalid or expired.
    """
    entry = _AUTH_CODE_STORE.pop(code, None)
    if not entry:
        return None
    if entry.get("expires_at", 0) < time.time():
        return None
    return entry.get("tokens")
