from __future__ import annotations

import json
import logging
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)

_PORTFOLIO_ID = "main"


def _to_decimal(obj: Any) -> Any:
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_decimal(v) for v in obj]
    return obj


def _from_decimal(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _from_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_from_decimal(v) for v in obj]
    return obj


class DynamoDBStore:
    def __init__(self, table_name: str, region: str) -> None:
        self.table_name = table_name
        self.region = region

    def _table(self):
        import boto3
        dynamodb = boto3.resource("dynamodb", region_name=self.region)
        return dynamodb.Table(self.table_name)

    def load_portfolio(self) -> dict[str, Any] | None:
        table = self._table()
        response = table.get_item(Key={"portfolio_id": _PORTFOLIO_ID})
        item = response.get("Item")
        if item is None:
            return None
        item.pop("portfolio_id", None)
        # DynamoDB Decimal → float
        item_str = json.dumps(item, default=str)
        return json.loads(item_str)

    def save_portfolio(self, state: dict[str, Any]) -> None:
        table = self._table()
        item = _to_decimal(state)
        item["portfolio_id"] = _PORTFOLIO_ID
        table.put_item(Item=item)
        logger.info("Portfolio state saved to DynamoDB")
