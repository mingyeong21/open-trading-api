import json
from datetime import datetime
from pathlib import Path

import requests

from config import Config, KST
from logger import logger


TOKEN_CACHE_PATH = Path("token_cache.json")


def load_cached_token() -> str | None:
    """
    Reuse token during the same day.

    This reduces unnecessary token issuance requests.
    """
    if not TOKEN_CACHE_PATH.exists():
        return None

    try:
        data = json.loads(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    today = datetime.now(KST).strftime("%Y-%m-%d")

    if data.get("date") == today and data.get("access_token"):
        logger.info("Reusing cached access token.")
        return data["access_token"]

    return None


def save_token(access_token: str) -> None:
    data = {
        "date": datetime.now(KST).strftime("%Y-%m-%d"),
        "access_token": access_token,
    }

    TOKEN_CACHE_PATH.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )


def get_access_token(config: Config) -> str:
    cached_token = load_cached_token()

    if cached_token:
        return cached_token

    logger.info("Requesting new access token.")

    url = f"{config.base_url}/oauth2/tokenP"

    body = {
        "grant_type": "client_credentials",
        "appkey": config.app_key,
        "appsecret": config.app_secret,
    }

    response = requests.post(url, json=body, timeout=30)

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError(f"Token response is not JSON: {response.text}")

    if response.status_code != 200:
        raise RuntimeError(f"Token request failed: {response.status_code}, {data}")

    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(f"Access token not found in response: {data}")

    save_token(access_token)
    logger.info("New access token saved.")

    return access_token