"""Simple in-memory store for user OAuth tokens.

This is intentionally minimal for demo purposes. For production you should
store tokens in a secure persistent store and associate them with user
accounts.
"""
from typing import Optional

_TOKEN_STORE: dict = {}


def store_tokens(session_id: str, tokens: dict) -> None:
    _TOKEN_STORE[session_id] = tokens


def get_tokens(session_id: str) -> Optional[dict]:
    return _TOKEN_STORE.get(session_id)


def clear_tokens(session_id: str) -> None:
    _TOKEN_STORE.pop(session_id, None)
