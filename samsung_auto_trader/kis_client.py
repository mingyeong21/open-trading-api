import time
from typing import Any

import requests

from config import Config, split_account
from logger import logger


# =========================
# KIS mock trading TR_IDs
# =========================
# Mock trading TR_ID values.
# If KIS Developers documentation changes, edit values here.

TR_ID_CURRENT_PRICE = "FHKST01010100"

TR_ID_BALANCE = "VTTC8434R"

TR_ID_BUY = "VTTC0802U"
TR_ID_SELL = "VTTC0801U"


class KISClient:
    """
    Minimal REST client for Korea Investment & Securities Open API.

    This class handles:
    - current price lookup
    - account balance lookup
    - mock stock order submission

    Safety design:
    - REST only
    - mock trading only
    - conservative rate-limit waiting
    - retry handling for temporary API errors
    """

    def __init__(self, config: Config, access_token: str):
        self.config = config
        self.access_token = access_token

    def _rate_limit_wait(self, seconds: float = 1.5) -> None:
        """
        Wait between API calls to avoid KIS mock API rate limits.

        KIS mock trading may reject too many requests in a short time.
        """
        time.sleep(seconds)

    def _headers(self, tr_id: str) -> dict[str, str]:
        """
        Create common request headers for KIS API calls.
        """
        return {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret,
            "tr_id": tr_id,
            "custtype": "P",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        tr_id: str,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        retries: int = 2,
    ) -> dict[str, Any]:
        """
        Send a REST API request with simple retry and rate-limit handling.
        """
        url = f"{self.config.base_url}{path}"
        headers = self._headers(tr_id)

        # KIS POST order APIs generally require hashkey.
        if body is not None and method.upper() == "POST":
            headers["hashkey"] = self.get_hashkey(body)

        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            try:
                self._rate_limit_wait()

                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=body,
                    timeout=30,
                )

                try:
                    data = response.json()
                except ValueError:
                    data = {"raw_text": response.text}

                # KIS often returns HTTP 200 even when rt_cd indicates failure.
                if response.status_code == 200 and data.get("rt_cd") != "1":
                    return data

                logger.error(
                    "API error on attempt %s: status=%s, response=%s",
                    attempt,
                    response.status_code,
                    data,
                )

                # EGW00201: too many requests per second.
                if data.get("msg_cd") == "EGW00201":
                    wait_seconds = 10
                    logger.info(
                        "Rate limit exceeded. Waiting %s seconds before retry.",
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

                elif attempt <= retries:
                    wait_seconds = 3 * attempt
                    logger.info(
                        "Waiting %s seconds before retry.",
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

            except requests.RequestException as error:
                last_error = error
                logger.error("Request error on attempt %s: %s", attempt, error)

                if attempt <= retries:
                    wait_seconds = 3 * attempt
                    logger.info(
                        "Waiting %s seconds before retry.",
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

        raise RuntimeError(f"API request failed. Last error: {last_error}")

    def get_hashkey(self, body: dict[str, Any]) -> str:
        """
        Get hashkey for KIS POST order request.

        The order-cash endpoint usually requires a hashkey header.
        """
        url = f"{self.config.base_url}/uapi/hashkey"

        headers = {
            "content-type": "application/json; charset=utf-8",
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret,
        }

        self._rate_limit_wait()

        response = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30,
        )

        try:
            data = response.json()
        except ValueError:
            raise RuntimeError(f"Hashkey response is not JSON: {response.text}")

        if response.status_code != 200 or data.get("rt_cd") == "1":
            raise RuntimeError(f"Hashkey request failed: {response.status_code}, {data}")

        hashkey = data.get("HASH")

        if not hashkey:
            raise RuntimeError(f"HASH not found in hashkey response: {data}")

        return hashkey

    def get_current_price(self) -> int:
        """
        Get current price of Samsung Electronics.
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"

        logger.info(
            "Requesting current price for stock_code=%s",
            self.config.stock_code,
        )

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self.config.stock_code,
        }

        data = self._request(
            "GET",
            path,
            tr_id=TR_ID_CURRENT_PRICE,
            params=params,
        )

        output = data.get("output", {})
        price_text = output.get("stck_prpr")

        if not price_text:
            raise RuntimeError(f"Current price not found in response: {data}")

        price = int(price_text)

        logger.info(
            "Current price of %s: %s KRW",
            self.config.stock_code,
            price,
        )

        return price

    def get_holding_quantity(self) -> int:
        """
        Get current holding quantity of Samsung Electronics.
        """
        cano, acnt_prdt_cd = split_account(self.config.account)

        path = "/uapi/domestic-stock/v1/trading/inquire-balance"

        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        data = self._request(
            "GET",
            path,
            tr_id=TR_ID_BALANCE,
            params=params,
        )

        output1 = data.get("output1", [])

        for item in output1:
            if item.get("pdno") == self.config.stock_code:
                qty_text = item.get("hldg_qty", "0")
                qty = int(float(qty_text))

                logger.info(
                    "Holding quantity of %s: %s",
                    self.config.stock_code,
                    qty,
                )

                return qty

        logger.info("No holding found for %s.", self.config.stock_code)
        return 0

    def submit_market_order(self, side: str, quantity: int) -> dict[str, Any]:
        """
        Submit a mock market order.

        side:
        - BUY
        - SELL

        Common domestic stock order setting:
        - ORD_DVSN = "01" means market order
        - ORD_UNPR = "0" for market order

        This project is mock trading only.
        """
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        cano, acnt_prdt_cd = split_account(self.config.account)

        path = "/uapi/domestic-stock/v1/trading/order-cash"

        tr_id = TR_ID_BUY if side == "BUY" else TR_ID_SELL

        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": self.config.stock_code,
            "ORD_DVSN": "01",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": "0",
        }

        logger.info(
            "Submitting %s market order: stock=%s, quantity=%s",
            side,
            self.config.stock_code,
            quantity,
        )

        data = self._request(
            "POST",
            path,
            tr_id=tr_id,
            body=body,
        )

        logger.info("Order response: %s", data)

        return data