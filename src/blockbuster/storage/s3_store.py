from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from blockbuster.portfolio.portfolio import TradeRecord

logger = logging.getLogger(__name__)


class S3Store:
    def __init__(self, bucket: str, region: str) -> None:
        self.bucket = bucket
        self.region = region

    def _client(self):
        import boto3
        return boto3.client("s3", region_name=self.region)

    def save_report(self, metrics: dict[str, Any], trades: list[TradeRecord]) -> str:
        key = f"reports/{datetime.utcnow().strftime('%Y/%m/%d')}/backtest.json"
        payload = {
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "trades": [t.to_dict() for t in trades],
        }
        self._client().put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(payload, ensure_ascii=False, indent=2),
            ContentType="application/json",
        )
        logger.info("Report saved to s3://%s/%s", self.bucket, key)
        return key
