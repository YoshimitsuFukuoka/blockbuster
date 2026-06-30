from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict, context: Any) -> dict:
    from blockbuster.config import load_config
    from blockbuster.data.fetcher import DataFetcher
    from blockbuster.engine.backtest import BacktestEngine
    from blockbuster.portfolio.portfolio import Portfolio
    from blockbuster.reporting.email_sender import EmailSender
    from blockbuster.reporting.reporter import Reporter
    from blockbuster.storage.s3_store import S3Store
    from blockbuster.strategies.combined import CombinedStrategy

    config_path = os.environ.get("CONFIG_PATH", None)
    config = load_config(config_path)

    portfolio = Portfolio(
        initial_capital=config.portfolio.initial_capital,
        commission_rate=config.portfolio.commission_rate,
    )
    strategy = CombinedStrategy(config.strategy)
    fetcher = DataFetcher()

    engine = BacktestEngine(config, strategy, portfolio, fetcher)
    result = engine.run()

    reporter = Reporter()
    metrics = reporter.compute_metrics(result.equity_curve, result.trades)

    period = f"{config.backtest_start} ～ {config.backtest_end}"
    html_body = reporter.build_html_report(metrics, result.trades, period=period)

    # Save to S3
    if config.aws.s3_bucket:
        try:
            s3 = S3Store(config.aws.s3_bucket, config.aws.region)
            s3.save_report(metrics, result.trades)
        except Exception as exc:
            logger.warning("S3 save failed (skipping): %s", exc)

    # Send email via SES
    if config.aws.ses_sender and config.aws.ses_recipient:
        sender = EmailSender(config.aws.region, config.aws.ses_sender, config.aws.ses_recipient)
        total_r = metrics.get("total_return_pct", 0)
        sign = "▲" if total_r >= 0 else "▼"
        sender.send(
            subject=f"【Blockbuster】バックテスト結果 {sign}{abs(total_r):.2f}% | {period}",
            html_body=html_body,
        )
    else:
        logger.info("SES not configured, skipping email. Metrics: %s", metrics)

    return {"statusCode": 200, "metrics": metrics}
