from __future__ import annotations

import getpass

SERVICE = "JARVIS-GoogleAI"
USERNAME = "default"


def load_api_key() -> str | None:
    try:
        import keyring
        return keyring.get_password(SERVICE, USERNAME)
    except Exception:
        return None


def save_api_key(api_key: str) -> None:
    try:
        import keyring
        keyring.set_password(SERVICE, USERNAME, api_key)
    except Exception as exc:
        raise RuntimeError("Windows credential storage is unavailable") from exc


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}…{api_key[-4:]}"
