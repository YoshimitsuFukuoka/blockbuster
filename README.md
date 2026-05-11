# Blockbuster — iPhone ブロック崩しゲーム

SpriteKit で作った iOS ネイティブのブロック崩しゲームです。

## 機能

- タッチでパドル操作（スワイプ追従）
- SpriteKit 物理エンジンによるリアルな反射
- レベルが上がるほどボールが速くなり、ブロック行数が増加
- ライフ制（3 機）
- スコア・ライフ・レベルの HUD 表示
- スタート画面 / ゲームオーバー画面

## ビルド方法

### 必要環境
- macOS 13+
- Xcode 15+
- iPhone 実機 or シミュレータ (iOS 16+)

### 手順

```bash
git clone <repo-url>
cd blockbuster
open Package.swift   # Xcode が自動で開く
```

Xcode でターゲットデバイスを選択し **Run (⌘R)** を押すだけです。

## プロジェクト構成

```
Sources/Blockbuster/
├── App/
│   ├── BlockbusterApp.swift   @main エントリポイント
│   └── ContentView.swift      SpriteView ラッパー + 画面遷移
├── Game/
│   ├── GameConfig.swift       定数・物理カテゴリ定義
│   └── GameScene.swift        ゲームメインシーン
├── Entities/
│   ├── Ball.swift             ボール
│   ├── Paddle.swift           パドル
│   ├── Block.swift            ブロック
│   └── Wall.swift             境界壁 / デッドゾーン
├── Logic/
│   ├── GameState.swift        スコア・ライフ・レベル管理
│   └── BlockLayout.swift      ブロック配置パターン生成
└── UI/
    ├── HUD.swift              ゲーム内 UI (スコア表示)
    ├── StartScene.swift       スタート画面
    └── GameOverScene.swift    ゲームオーバー画面
```

## ゲームプレイ

1. スタート画面をタップ → ゲーム開始
2. 画面をスワイプしてパドルを動かす
3. ボールをタップで発射
4. 全ブロックを破壊するとレベルアップ
5. ボールを落とすとライフ -1、0 になるとゲームオーバー
