from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from blockbuster.portfolio.portfolio import TradeRecord


class Reporter:
    def compute_metrics(
        self,
        equity_curve: pd.Series,
        trades: list[TradeRecord],
        risk_free_rate: float = 0.001,
    ) -> dict[str, Any]:
        if equity_curve.empty:
            return {}

        initial = float(equity_curve.iloc[0])
        final = float(equity_curve.iloc[-1])
        total_return_pct = (final - initial) / initial * 100

        daily_returns = equity_curve.pct_change().dropna()
        n_days = len(daily_returns)
        trading_days = 245  # TSE approx

        ann_return_pct = 0.0
        if n_days > 0:
            ann_return_pct = ((1 + total_return_pct / 100) ** (trading_days / n_days) - 1) * 100

        sharpe = 0.0
        if n_days > 1 and daily_returns.std() > 0:
            rf_daily = risk_free_rate / trading_days
            excess = daily_returns - rf_daily
            sharpe = float(excess.mean() / excess.std() * math.sqrt(trading_days))

        rolling_max = equity_curve.cummax()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown_pct = float(drawdown.min() * 100)

        sell_trades = [t for t in trades if t.action == "SELL" and t.pnl is not None]
        total_trades = len(sell_trades)
        win_trades = [t for t in sell_trades if (t.pnl or 0) > 0]
        win_rate = len(win_trades) / total_trades * 100 if total_trades > 0 else 0.0

        gross_profit = sum(t.pnl for t in sell_trades if (t.pnl or 0) > 0)
        gross_loss = abs(sum(t.pnl for t in sell_trades if (t.pnl or 0) < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        total_pnl = sum(t.pnl or 0 for t in sell_trades)

        calmar = ann_return_pct / abs(max_drawdown_pct) if max_drawdown_pct != 0 else 0.0

        return {
            "total_return_pct": round(total_return_pct, 2),
            "annualized_return_pct": round(ann_return_pct, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "calmar_ratio": round(calmar, 3),
            "win_rate_pct": round(win_rate, 1),
            "profit_factor": round(profit_factor, 3) if not math.isinf(profit_factor) else None,
            "total_trades": total_trades,
            "total_pnl_jpy": round(total_pnl, 0),
            "initial_capital_jpy": round(initial, 0),
            "final_value_jpy": round(final, 0),
        }

    def build_html_report(
        self,
        metrics: dict[str, Any],
        trades: list[TradeRecord],
        period: str = "",
    ) -> str:
        sell_trades = [t for t in trades if t.action == "SELL"]
        trade_rows = "".join(
            f"<tr><td>{t.timestamp[:10]}</td><td>{t.ticker}</td>"
            f"<td style='color:{'green' if (t.pnl or 0) >= 0 else 'red'}'>"
            f"{'▲' if (t.pnl or 0) >= 0 else '▼'} ¥{(t.pnl or 0):+,.0f}</td>"
            f"<td>{t.shares}</td><td>¥{t.price:,.0f}</td></tr>"
            for t in sell_trades[-50:]
        )

        pf = metrics.get("profit_factor")
        pf_str = f"{pf:.3f}" if pf is not None else "∞"
        total_return = metrics.get("total_return_pct", 0)
        return_color = "green" if total_return >= 0 else "red"

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Blockbuster 株自動売買レポート</title>
<style>
  body {{ font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
  .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
  h2 {{ color: #16213e; margin-top: 30px; }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
  .metric-card {{ background: #f8f9fa; border-radius: 6px; padding: 15px; text-align: center; border-left: 4px solid #e94560; }}
  .metric-value {{ font-size: 24px; font-weight: bold; color: #1a1a2e; }}
  .metric-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
  .positive {{ color: green !important; }}
  .negative {{ color: red !important; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
  th {{ background: #1a1a2e; color: white; padding: 10px; text-align: left; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f8f9fa; }}
  .footer {{ margin-top: 30px; color: #999; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>📈 Blockbuster 株自動売買レポート</h1>
  <p>対象期間: {period} &nbsp;|&nbsp; 戦略: 移動平均クロス + RSI逆張り + MACD (加重合成)</p>

  <h2>パフォーマンスサマリー</h2>
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value {'positive' if total_return >= 0 else 'negative'}">{total_return:+.2f}%</div>
      <div class="metric-label">総リターン</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{metrics.get('annualized_return_pct', 0):+.2f}%</div>
      <div class="metric-label">年率リターン</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{metrics.get('sharpe_ratio', 0):.3f}</div>
      <div class="metric-label">シャープレシオ</div>
    </div>
    <div class="metric-card">
      <div class="metric-value negative">{metrics.get('max_drawdown_pct', 0):.2f}%</div>
      <div class="metric-label">最大ドローダウン</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{metrics.get('win_rate_pct', 0):.1f}%</div>
      <div class="metric-label">勝率</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{pf_str}</div>
      <div class="metric-label">プロフィットファクター</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{metrics.get('total_trades', 0)}</div>
      <div class="metric-label">総取引数</div>
    </div>
    <div class="metric-card">
      <div class="metric-value {'positive' if metrics.get('total_pnl_jpy', 0) >= 0 else 'negative'}">¥{metrics.get('total_pnl_jpy', 0):+,.0f}</div>
      <div class="metric-label">総損益 (JPY)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">¥{metrics.get('final_value_jpy', 0):,.0f}</div>
      <div class="metric-label">最終資産額</div>
    </div>
  </div>

  <h2>取引履歴 (直近50件の決済)</h2>
  <table>
    <thead><tr><th>日付</th><th>銘柄</th><th>損益</th><th>株数</th><th>価格</th></tr></thead>
    <tbody>{trade_rows if trade_rows else '<tr><td colspan="5" style="text-align:center;color:#999">取引なし</td></tr>'}</tbody>
  </table>

  <div class="footer">
    Blockbuster 自動売買システム &copy; 2026 &nbsp;|&nbsp;
    初期資本: ¥{metrics.get('initial_capital_jpy', 0):,.0f}
  </div>
</div>
</body>
</html>"""
        return html

    def build_trade_alert(
        self,
        trades: list[TradeRecord],
        portfolio_snapshot: dict,
    ) -> str:
        rows = "".join(
            f"<tr><td>{t.ticker}</td><td>{t.action}</td>"
            f"<td>{t.shares}株</td><td>¥{t.price:,.0f}</td>"
            f"<td>{'¥{:+,.0f}'.format(t.pnl) if t.pnl is not None else '-'}</td></tr>"
            for t in trades
        )
        snap = portfolio_snapshot
        return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>取引アラート</title>
<style>body{{font-family:sans-serif;padding:20px;}}table{{border-collapse:collapse;width:100%;}}
th{{background:#1a1a2e;color:white;padding:8px;}}td{{padding:8px;border-bottom:1px solid #eee;}}</style>
</head><body>
<h2>🔔 Blockbuster 取引アラート</h2>
<table><thead><tr><th>銘柄</th><th>売買</th><th>数量</th><th>価格</th><th>損益</th></tr></thead>
<tbody>{rows}</tbody></table>
<hr>
<p>現在の資産: ¥{snap.get('total_value', 0):,.0f} &nbsp;|&nbsp;
現金: ¥{snap.get('cash', 0):,.0f} &nbsp;|&nbsp;
リターン: {snap.get('return_pct', 0):+.2f}%</p>
</body></html>"""
