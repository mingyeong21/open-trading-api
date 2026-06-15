from dataclasses import dataclass

from logger import logger


@dataclass
class StrategyDecision:
    action: str
    reason: str


class MovingAverageStrategy:
    """
    Simple moving-average momentum strategy.

    Buy:
    - no current holding
    - short moving average > long moving average

    Sell:
    - take profit
    - stop loss
    - trend reversal
    """

    def __init__(
        self,
        short_window: int,
        long_window: int,
        take_profit_rate: float,
        stop_loss_rate: float,
    ):
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window")

        self.short_window = short_window
        self.long_window = long_window
        self.take_profit_rate = take_profit_rate
        self.stop_loss_rate = stop_loss_rate
        self.price_history: list[int] = []

    def update_price(self, price: int) -> None:
        self.price_history.append(price)

        if len(self.price_history) > self.long_window:
            self.price_history.pop(0)

        logger.info("Price history: %s", self.price_history)

    def has_enough_data(self) -> bool:
        return len(self.price_history) >= self.long_window

    def _average(self, values: list[int]) -> float:
        return sum(values) / len(values)

    def get_signal(self) -> str:
        if not self.has_enough_data():
            return "HOLD"

        short_ma = self._average(self.price_history[-self.short_window:])
        long_ma = self._average(self.price_history[-self.long_window:])

        logger.info(
            "Short MA(%s)=%.2f, Long MA(%s)=%.2f",
            self.short_window,
            short_ma,
            self.long_window,
            long_ma,
        )

        if short_ma > long_ma:
            return "BUY_SIGNAL"

        if short_ma < long_ma:
            return "SELL_SIGNAL"

        return "HOLD"

    def decide(
        self,
        *,
        current_price: int,
        holding_qty: int,
        entry_price: int | None,
    ) -> StrategyDecision:
        """
        Decide whether to buy, sell, or hold.
        """
        signal = self.get_signal()

        if not self.has_enough_data():
            return StrategyDecision(
                action="HOLD",
                reason="Not enough price history",
            )

        if holding_qty <= 0:
            if signal == "BUY_SIGNAL":
                return StrategyDecision(
                    action="BUY",
                    reason="Short moving average is above long moving average",
                )

            return StrategyDecision(
                action="HOLD",
                reason="No holding and no buy signal",
            )

        if entry_price is None:
            return StrategyDecision(
                action="HOLD",
                reason="Holding exists but entry price is unknown",
            )

        profit_rate = (current_price - entry_price) / entry_price

        logger.info("Profit rate: %.3f%%", profit_rate * 100)

        if profit_rate >= self.take_profit_rate:
            return StrategyDecision(
                action="SELL",
                reason="Take profit condition met",
            )

        if profit_rate <= self.stop_loss_rate:
            return StrategyDecision(
                action="SELL",
                reason="Stop loss condition met",
            )

        if signal == "SELL_SIGNAL":
            return StrategyDecision(
                action="SELL",
                reason="Trend reversal detected",
            )

        return StrategyDecision(
            action="HOLD",
            reason="No sell condition met",
        )