from typing import Any

import requests

from config import Config, split_account
from logger import logger


# =========================
# KIS mock trading TR_IDs
# =========================
# These are separated here so they can be edited easily
# if KIS documentation or mock trading settings differ.

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
    """

    def __init__(self, config: Config, access_token: str):
        self.config = config
        self.access_token = access_token

    def _headers(self, tr_id: str) -> dict[str, str]:
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
        url = f"{self.config.base_url}{path}"
        headers = self._headers(tr_id)

        if body is not None and method.upper() == "POST":
            headers["hashkey"] = self.get_hashkey(body)

        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            try:
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

                if response.status_code == 200:
                    return data

                logger.error(
                    "API error: status=%s, response=%s",
                    response.status_code,
                    data,
                )

            except requests.RequestException as error:
                last_error = error
                logger.error("Request error on attempt %s: %s", attempt, error)

        raise RuntimeError(f"API request failed. Last error: {last_error}")

    def get_hashkey(self, body: dict[str, Any]) -> str:
        """
        KIS POST order APIs generally require a hashkey.
        """
        url = f"{self.config.base_url}/uapi/hashkey"

        headers = {
            "content-type": "application/json; charset=utf-8",
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret,
        }

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

        if response.status_code != 200:
            raise RuntimeError(f"Hashkey request failed: {response.status_code}, {data}")

        hashkey = data.get("HASH")

        if not hashkey:
            raise RuntimeError(f"HASH not found in hashkey response: {data}")

        return hashkey

    def get_current_price(self) -> int:
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"

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
        logger.info("Current price of %s: %s KRW", self.config.stock_code, price)

        return price

    def get_holding_quantity(self) -> int:
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
                logger.info("Holding quantity of %s: %s", self.config.stock_code, qty)
                return qty

        logger.info("No holding found for %s.", self.config.stock_code)
        return 0

    def submit_market_order(self, side: str, quantity: int) -> dict[str, Any]:
        """
        Submit a mock market order.

        side:
        - BUY
        - SELL

        ORD_DVSN = "01" means market order in the common KIS domestic stock setting.
        If your account/API rejects this value, check the latest KIS documentation.
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