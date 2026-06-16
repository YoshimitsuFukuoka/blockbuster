from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict, context: Any) -> dict:
    from blockbuster.config import load_config
    from blockbuster.data.fetcher import DataFetcher
    from blockbuster.engine.paper_trader import PaperTrader, within_tse_trading_hours
    from blockbuster.portfolio.portfolio import Portfolio
    from blockbuster.reporting.email_sender import EmailSender
    from blockbuster.reporting.reporter import Reporter
    from blockbuster.storage.dynamodb import DynamoDBStore
    from blockbuster.strategies.combined import CombinedStrategy

    if not within_tse_trading_hours():
        logger.info("Outside TSE trading hours, skipping tick")
        return {"statusCode": 200, "status": "outside_trading_hours"}

    config_path = os.environ.get("CONFIG_PATH", None)
    config = load_config(config_path)

    # Load or initialize portfolio state from DynamoDB
    db = DynamoDBStore(config.aws.dynamodb_table, config.aws.region)
    state = None
    try:
        state = db.load_portfolio()
    except Exception as exc:
        logger.warning("DynamoDB load failed (starting fresh): %s", exc)

    if state:
        portfolio = Portfolio.from_state(state)
    else:
        portfolio = Portfolio(
            initial_capital=config.portfolio.initial_capital,
            commission_rate=config.portfolio.commission_rate,
        )

    strategy = CombinedStrategy(config.strategy)
    fetcher = DataFetcher()
    trader = PaperTrader(config, strategy, portfolio, fetcher)
    trades_executed = trader.tick()

    # Persist updated portfolio state
    try:
        db.save_portfolio(portfolio.to_state())
    except Exception as exc:
        logger.warning("DynamoDB save failed: %s", exc)

    # Send trade alert email if trades occurred
    if trades_executed and config.aws.ses_sender and config.aws.ses_recipient:
        reporter = Reporter()
        current_prices = {t.ticker: t.price for t in trades_executed}
        snapshot = portfolio.snapshot(current_prices)
        html = reporter.build_trade_alert(trades_executed, snapshot)
        email_sender = EmailSender(
            config.aws.region, config.aws.ses_sender, config.aws.ses_recipient
        )
        email_sender.send(
            subject=f"【Blockbuster】{len(trades_executed)}件の取引が発生しました",
            html_body=html,
        )

    return {
        "statusCode": 200,
        "trades_executed": len(trades_executed),
        "portfolio_value": portfolio.cash,
    }
