# 開発ログ - Kindle Screenshot Tool

このドキュメントは、本ツールの開発過程を時系列でまとめたものです。

---

## 1. 要件定義

### 目的
macOS上でAmazon Kindleアプリの画面を自動でスクリーンショット撮影し、PDFにまとめるローカルアプリを作成する。個人利用を前提とする。

### 初期要件
- Kindleアプリを自分で起動した状態で、ツールからKindleをアクティブにして操作
- フルスクリーンにしてスクリーンショットを撮影
- ページ送り（右めくり/左めくり）を自動化
- 画面に変化がなくなったら自動停止
- 撮影した画像をPDFにまとめる
- 本の名前はユーザー入力

### 追加要件（議論で追加）
- **デュアルディスプレイ対応**: 当初はディスプレイ選択方式を検討 → Mac内蔵ディスプレイに固定する方針に変更（Macのインチ数を聞いて案内する方式）
- **テスト撮影モード**: 5枚だけ撮影して動作確認できるモード

---

## 2. 技術スタック選定

| 用途 | 選定技術 | 理由 |
|------|----------|------|
| 言語 | Python 3.10+ | macOS APIとの連携が容易 |
| GUI | tkinter | Python標準ライブラリ、追加依存なし |
| ウィンドウ制御 | AppleScript（osascript） | macOSネイティブ、確実 |
| ウィンドウID取得 | Quartz API（pyobjc） | AppleScriptでは取得できないケースに対応 |
| スクリーンショット | screencapture -l（ウィンドウ指定） | メニューバー除外が可能 |
| 画像比較 | Pillow + NumPy | ピクセル差分で変化検出 |
| PDF生成 | img2pdf | 画質劣化なしでPDF化 |

---

## 3. 初回実装（CLI版）

### ファイル構成
```
main.py              # エントリーポイント（CLI対話型）
kindle_controller.py # AppleScriptでKindle制御
screenshot.py        # screencapture -D 1（画面全体キャプチャ）
page_compare.py      # 画像比較
pdf_generator.py     # PDF生成
config.py            # 設定管理
```

### 問題点
- `input()`を使うCLIのため、Claude Code内のBashでは実行不可（EOFError）
- ターミナルから直接実行する必要があった

---

## 4. GUI版への移行

### 変更内容
- tkinterでGUIウィンドウを実装
- ドロップダウン、テキスト入力、ボタンで操作
- フローティングウィンドウ（常に最前面 `-topmost`）
- 画面右上に配置（Kindleの邪魔にならない）
- バックグラウンドスレッドで撮影ループ実行

### tkinterインストール問題
- Python 3.14に`_tkinter`モジュールがなかった
- `brew install python-tk@3.14`で解決

---

## 5. Kindleアプリ名の修正

### エラー
```
AppleScript error: application "Kindle"を取り出すことはできません。(-1728)
```

### 原因
- macOS上のアプリ名が「Kindle」ではなく **「Amazon Kindle」** だった
- `ls /Applications/ | grep -i kindle` → `Amazon Kindle.app`

### 修正
- `activate`コマンドのアプリ名を `"Amazon Kindle"` に変更
- `System Events`のプロセス名は `"Kindle"` のままで正しい（変更不要）

---

## 6. メニューバー映り込み問題

### 問題
- `screencapture -D 1`（画面全体キャプチャ）だとメニューバーやGUIツールも映り込む

### 解決策
- Quartz APIでKindleのウィンドウIDを取得
- `screencapture -x -o -l <windowID>` でウィンドウ単体をキャプチャ
- `-o`オプションでウィンドウの影も除外

### 技術的詳細
```python
import Quartz
# CGWindowListCopyWindowInfo でウィンドウ一覧取得
# KindleのPIDとLayer=0でフィルタしてWindowNumber取得
```

- `pyobjc-framework-Quartz`を依存に追加

---

## 7. ページ送りが効かない問題

### 問題
- フルスクリーン自動化後、キー送信がKindleに届かない
- 全ページが同じ画像 → 「変化なし」で即停止

### 原因
- フルスクリーン切り替え後にフォーカスが変わっている可能性
- AppleScriptのフルスクリーン制御が不安定

### 解決策
1. **フルスクリーン自動化を廃止** → ユーザーに事前にフルスクリーンにしてもらう
2. **ページ送り前に毎回`activate_kindle()`** → キー送信先を確実にKindleにする

```python
# 撮影ループ内
activate_kindle()    # 毎回アクティブ化
time.sleep(0.3)
send_page_key(...)   # キー送信
```

---

## 8. セットアップスクリプト作成

### 目的
他の人のMacでも簡単に環境構築できるようにする。

### setup.sh の処理
1. Python3の存在確認
2. Homebrewの存在確認
3. tkinterの確認・インストール
4. venv作成・依存パッケージインストール
5. Amazon Kindleアプリの確認
6. macOS権限設定の案内表示

---

## 9. GitHubリポジトリ

- リポジトリ: https://github.com/groundcobra009/amazon-screenshot-tool
- パブリックリポジトリとして公開
- 個人利用前提、Kindle利用規約の確認を案内

### コミット履歴
1. **Initial commit** - CLI版の初回実装
2. **GUI版に移行、ウィンドウキャプチャ対応、セットアップスクリプト追加** - 全面改修

---

## 10. 解決した主な課題まとめ

| 課題 | 原因 | 解決策 |
|------|------|--------|
| Claude Code内でCLI実行不可 | `input()`がEOFError | tkinter GUI版に移行 |
| Kindleアクティブ化失敗 | アプリ名が「Amazon Kindle」 | AppleScript内のアプリ名修正 |
| メニューバーが映り込む | 画面全体キャプチャだった | Quartz APIでウィンドウID取得→ウィンドウ単体キャプチャ |
| ウィンドウID取得失敗 | AppleScriptの`id`が非対応 | Quartz `CGWindowListCopyWindowInfo`に変更 |
| ページ送りが効かない | フルスクリーン後のフォーカス問題 | 手動フルスクリーン＋毎回activate |
| tkinterが見つからない | Python 3.14にバンドルされていない | `brew install python-tk@3.14` |

---

## 11. 今後の改善候補

- Notionにセットアップガイドページを作成（スクリーンショット付き）
- OCRで本の名前を自動取得
- 撮影速度の最適化（ページ描画完了の検出）
- .appバンドル化（ダブルクリックで起動）
