# Kindle Screenshot Tool

macOS上でAmazon Kindleアプリの画面を自動でスクリーンショット撮影し、PDFにまとめるCLIツールです。

## 注意事項

- **個人利用を前提としています。**
- ご利用前に [Amazon Kindleの利用規約](https://www.amazon.co.jp/gp/help/customer/display.html?nodeId=201014950) を必ずご確認ください。
- 本ツールの使用により生じたいかなる問題についても、作者は責任を負いません。
- 著作権法を遵守し、自己責任でご利用ください。

## 機能

- Kindleアプリのウィンドウを自動でフルスクリーン化
- 自動ページ送り＋スクリーンショット撮影
- 最終ページ到達を自動検出して停止
- 撮影画像を1つのPDFにまとめて出力

## 動作環境

- macOS Ventura以降
- Python 3.10+
- Amazon Kindle for Mac

## セットアップ

```bash
git clone https://github.com/YOUR_USERNAME/amazon-screenshot-tool.git
cd amazon-screenshot-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## macOS権限設定

ターミナル（またはiTerm）に以下の権限を付与してください:

1. システム設定 → プライバシーとセキュリティ → **アクセシビリティ**
2. システム設定 → プライバシーとセキュリティ → **画面収録**

## 使い方

1. Kindleアプリを起動し、撮影したい本を開く
2. ツールを実行:

```bash
source .venv/bin/activate
python main.py
```

3. 対話形式で設定を入力:
   - Macの画面サイズ（インチ）
   - ページめくり方向
   - 本の名前

4. 自動で撮影が開始され、最終ページで停止
5. `output/{book_name}.pdf` にPDFが出力されます

## 途中停止

`Ctrl+C` で撮影を中断できます。中断時点までの画像でPDFが生成されます。

## ディレクトリ構成

```
amazon-screenshot-tool/
├── main.py              # エントリーポイント
├── kindle_controller.py # Kindleウィンドウ制御
├── screenshot.py        # スクリーンショット撮影
├── page_compare.py      # 画像比較（停止判定）
├── pdf_generator.py     # PDF生成
├── config.py            # 設定管理
├── requirements.txt     # 依存パッケージ
├── screenshots/         # 撮影画像保存先
└── output/              # PDF出力先
```

## License

MIT
