# Kindle Screenshot Tool

macOS上でAmazon Kindleアプリの画面を自動でスクリーンショット撮影し、PDFにまとめるGUIツールです。

## 注意事項

- **個人利用を前提としています。**
- ご利用前に [Amazon Kindleの利用規約](https://www.amazon.co.jp/gp/help/customer/display.html?nodeId=201014950) を必ずご確認ください。
- 本ツールの使用により生じたいかなる問題についても、作者は責任を負いません。
- 著作権法を遵守し、自己責任でご利用ください。

## 機能

- GUIでの操作（常に最前面に表示されるフローティングウィンドウ）
- Kindleウィンドウのみをキャプチャ（メニューバー等は映りません）
- 自動ページ送り + スクリーンショット撮影
- 最終ページ到達を自動検出して停止
- テスト撮影モード（5枚のみ）
- 撮影画像を1つのPDFにまとめて出力
- 途中停止可能（停止ボタン）

## 動作環境

- macOS Ventura以降
- Python 3.10+
- Amazon Kindle for Mac
- Homebrew

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/groundcobra009/amazon-screenshot-tool.git
cd amazon-screenshot-tool
```

### 2. セットアップスクリプトを実行

```bash
./setup.sh
```

このスクリプトが以下を自動で行います:
- Python / Homebrewの確認
- tkinterのインストール（未インストールの場合）
- 仮想環境の作成と依存パッケージのインストール
- Amazon Kindleアプリの確認
- 必要なmacOS権限の案内

### 3. macOS権限を付与

ターミナルアプリ（Terminal.app / iTerm / VS Code等）に以下の権限を付与してください:

| 権限 | 設定場所 |
|------|----------|
| アクセシビリティ | システム設定 → プライバシーとセキュリティ → アクセシビリティ |
| 画面収録 | システム設定 → プライバシーとセキュリティ → 画面収録 |

> 権限を付与するアプリは、**このツールを起動するターミナルアプリ**です。

## 使い方

### 1. 起動

```bash
cd amazon-screenshot-tool
source .venv/bin/activate
python main.py
```

### 2. Kindleを準備

- Amazon Kindleアプリを起動し、撮影したい本を開く
- **Kindleをフルスクリーン（または最大化）にしておく**

### 3. GUIで設定

| 設定項目 | 説明 |
|----------|------|
| Mac画面サイズ | お使いのMacの画面インチ数 |
| めくり方向 | 右めくり（←で次ページ）/ 左めくり（→で次ページ） |
| 本の名前 | 保存ファイル名（空欄で自動命名） |
| ページ送り待機(秒) | ページ送り後の待機時間（デフォルト: 1.5秒） |
| テスト撮影 | チェックすると5枚だけ撮影して停止 |

### 4. 撮影開始

「撮影開始」ボタンを押すと:
1. Kindleがアクティブ化される
2. 3秒のカウントダウン後、自動撮影開始
3. ページ送り → キャプチャ を繰り返す
4. 画面に変化がなくなると自動停止（または「停止」ボタンで手動停止）
5. PDFが自動生成される

### 5. 出力先

- スクリーンショット: `screenshots/{本の名前}/`
- PDF: `output/{本の名前}.pdf`

## ヒント

- **初回はテスト撮影で確認**: 「テスト撮影（5枚のみ）」にチェックして動作確認
- **画像が多い本**: ページ送り待機時間を2〜3秒に増やしてください
- **途中停止**: 「停止」ボタンでいつでも中断可能。中断時点までの画像でPDFが生成されます

## ディレクトリ構成

```
amazon-screenshot-tool/
├── main.py              # GUIアプリ（エントリーポイント）
├── kindle_controller.py # Kindleウィンドウ制御（AppleScript）
├── screenshot.py        # スクリーンショット撮影（Quartz API）
├── page_compare.py      # 画像比較（停止判定）
├── pdf_generator.py     # PDF生成
├── config.py            # 設定管理
├── setup.sh             # セットアップスクリプト
├── requirements.txt     # 依存パッケージ
├── screenshots/         # 撮影画像保存先
└── output/              # PDF出力先
```

## トラブルシューティング

### 「Kindleウィンドウが見つかりません」

- Amazon Kindleアプリが起動しているか確認
- Kindleで本を開いた状態にしてください

### ページ送りが効かない

- ターミナルに「アクセシビリティ」権限が付与されているか確認
- Kindleをフルスクリーンにしてから撮影開始してください

### スクリーンショットが撮れない

- ターミナルに「画面収録」権限が付与されているか確認
- 権限変更後はターミナルの再起動が必要な場合があります

### tkinterエラー (`No module named '_tkinter'`)

```bash
brew install python-tk@3.XX  # XXはPythonバージョン
```

## License

MIT
