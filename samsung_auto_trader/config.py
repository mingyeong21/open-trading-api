import os
from dataclasses import dataclass
from datetime import time as dtime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


load_dotenv()

KST = ZoneInfo("Asia/Seoul")

@dataclass(frozen=True)
class Config:
    """
    Project configuration.

    Credentials are loaded from environment variables.
    Do not hardcode secrets in source code.
    """

    app_key: str
    app_secret: str
    account: str
    base_url: str

    stock_code: str = "005930"
    stock_name: str = "Samsung Electronics"

    trading_start: dtime = dtime(9, 10)
    trading_end: dtime = dtime(15, 30)

    poll_interval_seconds: int = 120
    order_confirm_wait_seconds: int = 10

    short_window: int = 3
    long_window: int = 8

    take_profit_rate: float = 0.004
    stop_loss_rate: float = -0.003

    order_quantity: int = 1


def load_config() -> Config:
    app_key = os.getenv("GH_APPKEY", "").strip()
    app_secret = os.getenv("GH_APPSECRET", "").strip()
    account = os.getenv("GH_ACCOUNT", "").strip()
    base_url = os.getenv(
        "KIS_BASE_URL",
        "https://openapivts.koreainvestment.com:29443",
    ).strip()

    missing = []

    if not app_key:
        missing.append("GH_APPKEY")
    if not app_secret:
        missing.append("GH_APPSECRET")
    if not account:
        missing.append("GH_ACCOUNT")

    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return Config(
        app_key=app_key,
        app_secret=app_secret,
        account=account,
        base_url=base_url,
    )


def split_account(account: str) -> tuple[str, str]:
    """
    Split KIS account number into:
    - CANO: first 8 digits
    - ACNT_PRDT_CD: last 2 digits

    Accepts:
    - 12345678-01
    - 1234567801
    """
    cleaned = account.replace("-", "").replace(" ", "")

    if not cleaned.isdigit():
        raise ValueError("GH_ACCOUNT must contain only digits and optional hyphen.")

    if len(cleaned) != 10:
        raise ValueError(
            "GH_ACCOUNT must be 10 digits including product code. "
            "Example: 12345678-01 or 1234567801"
        )

    return cleaned[:8], cleaned[8:10]