# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## Project overview

**Blockbuster** is a paper-trading / backtesting automated trading system for
Japanese equities listed on the Tokyo Stock Exchange (TSE). It runs as
container-image AWS Lambda functions on a schedule (EventBridge), persists
state in DynamoDB, archives reports to S3, and emails HTML performance
reports via Amazon SES.

There are two scheduled entry points:

- **Backtest** — runs daily at 16:00 JST over a configurable historical
  window and emails a performance report (returns, Sharpe ratio, drawdown,
  win rate, etc.).
- **Paper trade** — runs every 5 minutes during TSE trading hours
  (09:00–11:30 and 12:30–15:30 JST, weekdays only), fetches the latest price
  data, generates a signal, and executes a *simulated* trade against a
  DynamoDB-persisted virtual portfolio. No real brokerage orders are placed.

Trading decisions come from `CombinedStrategy`, a weighted blend of three
sub-strategies (default weights: MA cross 30%, RSI 35%, MACD 35%). The
combined score is compared against buy/sell thresholds (default ±0.40) to
produce a `BUY` / `SELL` / `HOLD` signal per ticker.

## Directory structure

```
config.yaml                 # Default runtime configuration (tickers, capital, strategy params, AWS resources)
requirements.txt            # Python dependencies
Dockerfile                  # Lambda container image (handler selected via HANDLER build arg)
template.yaml                # AWS SAM template: Lambda functions, S3 bucket, DynamoDB table, IAM role, EventBridge schedules
src/blockbuster/
  config.py                 # Dataclass config schema + load_config() (reads YAML, env CONFIG_PATH)
  data/
    fetcher.py               # DataFetcher: yfinance-backed historical/latest OHLCV fetch, JST normalization
  indicators/
    moving_average.py        # ema/sma + golden/dead cross detection
    rsi.py                    # Wilder's-smoothed RSI
    macd.py                   # MACD line/signal/histogram
  strategies/
    base.py                   # Signal enum (BUY/HOLD/SELL), Strategy ABC, StrategyResult
    ma_cross.py                # Moving-average cross strategy
    rsi_contrarian.py          # RSI oversold/overbought contrarian strategy
    macd_cross.py               # MACD histogram cross strategy
    combined.py                 # CombinedStrategy: weighted blend + build_strategy() factory
  portfolio/
    position.py                # Position dataclass (shares, avg cost, unrealized P&L)
    portfolio.py                # Portfolio: buy/sell execution, lot-size (100 shares) rounding, commission, to_state/from_state
  engine/
    backtest.py                 # BacktestEngine: iterates historical bars, drives Portfolio + Strategy, builds equity curve
    paper_trader.py              # PaperTrader.tick() for live ticks; within_tse_trading_hours() guard
  handlers/
    backtest_handler.py          # Lambda entry point: run backtest, compute metrics, save to S3, email via SES
    paper_trade_handler.py        # Lambda entry point: one paper-trading tick, persist state to DynamoDB, email on trades
  reporting/
    reporter.py                   # Metrics computation (Sharpe, drawdown, Calmar, win rate, profit factor) + HTML report/alert builders
    storage/                      # (see below)
    email_sender.py                # SES HTML email sender
  storage/
    s3_store.py                    # Persists backtest reports as JSON under reports/YYYY/MM/DD/
    dynamodb.py                     # Persists/loads Portfolio state (float<->Decimal conversion) keyed by portfolio_id="main"
```

## Architecture flow

```
EventBridge (daily 16:00 JST)        -> blockbuster-backtest Lambda    -> S3 report + SES email
EventBridge (weekdays, every 5 min)  -> blockbuster-paper-trade Lambda -> DynamoDB state + SES alert email (only if trades occurred)
```

Both Lambdas share the same container image (`Dockerfile`); the entry point
is selected at build time via the `HANDLER` build arg / SAM
`DockerBuildArgs` (`blockbuster.handlers.backtest_handler.handler` or
`blockbuster.handlers.paper_trade_handler.handler`).

## Key conventions

- **Config-driven, not hardcoded.** All tunable parameters (tickers, capital,
  strategy thresholds, AWS resource names) live in `config.yaml` and are
  loaded into typed dataclasses via `blockbuster.config.load_config()`.
  Prefer adding new knobs to `config.yaml` + the corresponding dataclass
  over hardcoding values in strategy/engine code.
- **TSE lot size (単元株).** `Portfolio.buy()` always rounds share counts
  down to multiples of 100 (`_LOT_SIZE` in `portfolio/portfolio.py`).
- **Trading hours guard.** `within_tse_trading_hours()` in
  `engine/paper_trader.py` enforces TSE sessions (09:00–11:30,
  12:30–15:30 JST, Mon–Fri) and is checked first thing in
  `paper_trade_handler.handler` — outside those hours the handler returns
  early without fetching data or trading.
- **Strategies implement `Strategy.generate(ticker, df) -> StrategyResult`**
  (`strategies/base.py`), treating the last row of the input DataFrame as
  the current bar. New strategies should follow this interface and be wired
  into `CombinedStrategy` (and `build_strategy()`) if they should
  participate in the weighted blend.
- **All price data passes through `DataFetcher._normalize()`**, which
  flattens yfinance's MultiIndex columns, restricts to
  `Open/High/Low/Close/Volume`, and converts the index to `Asia/Tokyo`.
  Keep this normalization in the fetcher rather than re-deriving it
  downstream.
- **Lambda handlers do their imports inside the function body** (not at
  module scope) to keep cold-start import costs isolated per handler.
  Follow this pattern for new handlers.
- **State persistence:** `Portfolio.to_state()` / `Portfolio.from_state()`
  round-trip through DynamoDB (with float↔`Decimal` conversion in
  `storage/dynamodb.py`); only the last 100 trades are retained in
  persisted state.
- Comments and emails are written in Japanese (the target market and
  primary user are Japanese); keep this when extending reporting code.

## Build, run, and deploy

There is no test suite, linter, or CI configuration in this repo yet — there
is nothing to run beyond what's below.

**Local backtest run (no AWS required):**
```bash
pip install -r requirements.txt
export PYTHONPATH=src
python -c "
from blockbuster.handlers.backtest_handler import handler
handler({}, None)
"
```
With no `aws.ses_sender`/`ses_recipient`/`s3_bucket` configured (or AWS
credentials unavailable), the handler logs metrics instead of emailing and
S3 save failures are caught and logged, not raised — so this works fully
offline against Yahoo Finance data.

**AWS deployment** (requires AWS CLI configured, SAM CLI, Docker running,
and a verified SES sender address):
```bash
sam build
sam deploy --guided
# SESEmailAddress: <verified-ses-address>
```

**Manual Lambda invocation after deploy:**
```bash
aws lambda invoke --function-name blockbuster-backtest --payload '{}' response.json
aws lambda invoke --function-name blockbuster-paper-trade --payload '{}' response.json
```

## Configuration reference (`config.yaml`)

- `tickers` — TSE ticker codes in Yahoo Finance format, e.g. `7203.T` (Toyota).
- `portfolio.initial_capital` / `max_position_pct` / `commission_rate`.
- `strategy.ma|rsi|macd` — per-indicator parameters.
- `strategy.combined_weights` — must sum to a positive value (normalized in
  `CombinedStrategy.__init__`); `score_buy_threshold` /
  `score_sell_threshold` gate the combined score into BUY/SELL/HOLD.
- `backtest_start` / `backtest_end` — backtest date range.
- `aws.region`, `aws.s3_bucket`, `aws.dynamodb_table`, `aws.ses_sender`,
  `aws.ses_recipient`.

`CONFIG_PATH` env var overrides the config file location (defaults to
`config.yaml` next to the Lambda task root in the container, or the repo
root locally).

## Things to watch for when changing this code

- `BacktestEngine.run()` and `PaperTrader.tick()` both independently compute
  the warmup window (`max(ma.long_period, rsi.period + 1, macd.slow +
  macd.signal)`) — keep these in sync if you change how warmup is derived,
  or factor it out if you touch both files.
- `Portfolio.buy()` is a no-op if the ticker is already held (no
  pyramiding/averaging-in) — a strategy will only ever hold 0 or 1 position
  per ticker at a time.
- AWS resource names (`blockbuster-reports-${AccountId}`,
  `blockbuster-portfolio`) are defined in `template.yaml`; if you rename
  resources there, update the corresponding defaults in
  `config.py`/`config.yaml` to match.
