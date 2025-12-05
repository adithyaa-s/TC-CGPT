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


def store_tokens(session_id: str, tokens: dict) -> None:
    _TOKEN_STORE[session_id] = tokens


def get_tokens(session_id: str) -> Optional[dict]:
    return _TOKEN_STORE.get(session_id)


def clear_tokens(session_id: str) -> None:
    _TOKEN_STORE.pop(session_id, None)


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
