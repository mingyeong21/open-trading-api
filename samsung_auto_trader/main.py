from auth import get_access_token
from config import load_config
from kis_client import KISClient
from logger import logger
from strategy import MovingAverageStrategy
from trader import Trader


def main() -> None:
    config = load_config()

    logger.info("Samsung Auto Trader started.")
    logger.info("Mode: mock trading only, REST only, no WebSocket.")
    logger.info("Target stock: %s (%s)", config.stock_name, config.stock_code)

    access_token = get_access_token(config)

    client = KISClient(
        config=config,
        access_token=access_token,
    )

    strategy = MovingAverageStrategy(
        short_window=config.short_window,
        long_window=config.long_window,
        take_profit_rate=config.take_profit_rate,
        stop_loss_rate=config.stop_loss_rate,
    )

    trader = Trader(
        config=config,
        client=client,
        strategy=strategy,
    )

    trader.run()


if __name__ == "__main__":
    main()