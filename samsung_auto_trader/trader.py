import time
from datetime import datetime

from config import Config, KST
from kis_client import KISClient
from logger import logger
from strategy import MovingAverageStrategy


class Trader:
    """
    Main trading engine.

    This class connects:
    - KIS API client
    - trading strategy
    - execution confirmation logic
    """

    def __init__(
        self,
        config: Config,
        client: KISClient,
        strategy: MovingAverageStrategy,
    ):
        self.config = config
        self.client = client
        self.strategy = strategy

        # This simple project tracks entry price in memory.
        # A more advanced version should read actual average purchase price
        # from account/holding API or saved trade history.
        self.entry_price: int | None = None

    def is_trading_time(self) -> bool:
        now = datetime.now(KST).time()
        return self.config.trading_start <= now <= self.config.trading_end

    def should_stop(self) -> bool:
        now = datetime.now(KST).time()
        return now > self.config.trading_end

    def run_one_cycle(self) -> None:
        """
        One conservative trading cycle.

        API usage:
        - current price: 1 call
        - holdings before order: 1 call
        - holdings after order: only if order submitted
        """
        current_price = self.client.get_current_price()
        self.strategy.update_price(current_price)

        holding_before = self.client.get_holding_quantity()
        logger.info("Holding before decision: %s", holding_before)

        # If the program starts while holding stock, but entry price is unknown,
        # use current price as temporary reference for this educational demo.
        if holding_before > 0 and self.entry_price is None:
            self.entry_price = current_price
            logger.info(
                "Entry price was unknown. Temporarily set to current price: %s",
                self.entry_price,
            )

        decision = self.strategy.decide(
            current_price=current_price,
            holding_qty=holding_before,
            entry_price=self.entry_price,
        )

        logger.info("Decision: %s, reason: %s", decision.action, decision.reason)

        if decision.action == "HOLD":
            return

        if decision.action == "BUY":
            self.client.submit_market_order(
                side="BUY",
                quantity=self.config.order_quantity,
            )

            time.sleep(self.config.order_confirm_wait_seconds)

            holding_after = self.client.get_holding_quantity()
            logger.info("Holding after BUY: %s", holding_after)

            if holding_after > holding_before:
                self.entry_price = current_price
                logger.info("BUY execution seems confirmed.")
            else:
                logger.info("BUY execution not confirmed yet.")

            return

        if decision.action == "SELL":
            self.client.submit_market_order(
                side="SELL",
                quantity=self.config.order_quantity,
            )

            time.sleep(self.config.order_confirm_wait_seconds)

            holding_after = self.client.get_holding_quantity()
            logger.info("Holding after SELL: %s", holding_after)

            if holding_after < holding_before:
                self.entry_price = None
                logger.info("SELL execution seems confirmed.")
            else:
                logger.info("SELL execution not confirmed yet.")

            return

        logger.warning("Unknown decision action: %s", decision.action)

    def run(self) -> None:
        logger.info("Trading engine started.")
        logger.info(
            "Trading window: %s ~ %s",
            self.config.trading_start,
            self.config.trading_end,
        )

        while True:
            if self.should_stop():
                logger.info("Trading window ended. Program will stop.")
                break

            if not self.is_trading_time():
                logger.info("Outside trading window. Waiting.")
                time.sleep(60)
                continue

            try:
                self.run_one_cycle()
            except Exception as error:
                logger.error("Trading cycle error: %s", error)

            logger.info(
                "Sleeping for %s seconds to reduce API calls.",
                self.config.poll_interval_seconds,
            )
            time.sleep(self.config.poll_interval_seconds)