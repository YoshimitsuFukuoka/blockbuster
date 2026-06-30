# Blockbuster - 株自動売買システム

東京証券取引所（TSE）の日本株を対象としたペーパートレード自動売買システム。
AWS Lambda + EventBridge で定期実行し、Amazon SES で分析結果をメール送信する。

## 戦略

3つの戦略を加重合成して売買判断を行う：

| 戦略 | 重み | ロジック |
|------|------|---------|
| 移動平均クロス | 30% | ゴールデンクロス→買い、デッドクロス→売り |
| RSI逆張り | 35% | RSI<30→買い、RSI>70→売り (比例スコア) |
| MACDクロス | 35% | MACDがシグナルを上抜け→買い、下抜け→売り |

合成スコアが +0.40 以上で買い、-0.40 以下で売り、それ以外はホールド。

## アーキテクチャ

```
EventBridge (毎日 16:00 JST)  ->  Lambda: バックテスト  ->  SES メール送信
EventBridge (平日 5分毎)      ->  Lambda: ペーパートレード  ->  DynamoDB (状態保存)
                                                            ->  SES アラートメール
```

## セットアップ

### ローカル実行

```bash
pip install -r requirements.txt
export PYTHONPATH=src

# バックテスト実行 (AWS不要)
python -c "
from blockbuster.handlers.backtest_handler import handler
handler({}, None)
"
```

### AWS デプロイ

事前準備：
1. AWS CLI 設定済み (`aws configure`)
2. SAM CLI インストール済み
3. Amazon SES でメールアドレス認証済み (`yoshimitsu.work@gmail.com`)
4. Docker 起動済み (コンテナイメージビルドに必要)

```bash
sam build
sam deploy --guided
# SESEmailAddress: yoshimitsu.work@gmail.com
```

### 手動テスト (デプロイ後)

```bash
aws lambda invoke --function-name blockbuster-backtest --payload '{}' response.json
aws lambda invoke --function-name blockbuster-paper-trade --payload '{}' response.json
```

## 設定

`config.yaml` で以下を変更可能：

- `tickers`: 対象銘柄 (例: `7203.T` = トヨタ)
- `portfolio.initial_capital`: 仮想元本 (デフォルト: 100万円)
- `portfolio.max_position_pct`: 1銘柄あたり最大ポジション比率 (デフォルト: 10%)
- `strategy.*`: 各インジケーターのパラメータ
- `backtest_start/end`: バックテスト期間

## メール内容

**バックテストメール** (毎日 16:00 JST):
- パフォーマンスサマリー (総リターン, シャープレシオ, 最大ドローダウン, 勝率等)
- 取引履歴テーブル (直近50件)

**取引アラートメール** (取引発生時のみ):
- 発生した取引の詳細
- 現在のポートフォリオ状況
