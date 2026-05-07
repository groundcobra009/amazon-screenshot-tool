#!/bin/bash
set -e

echo "============================================"
echo "  Kindle Screenshot Tool - セットアップ"
echo "============================================"
echo ""

# Python確認
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python3がインストールされていません。"
    echo "  brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python ${PYTHON_VERSION} を検出"

# Homebrew確認
if ! command -v brew &> /dev/null; then
    echo "エラー: Homebrewがインストールされていません。"
    echo "  https://brew.sh からインストールしてください。"
    exit 1
fi
echo "✓ Homebrew を検出"

# tkinter確認・インストール
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "tkinterが見つかりません。インストールします..."
    brew install python-tk@${PYTHON_VERSION}
    echo "✓ python-tk をインストール"
else
    echo "✓ tkinter 利用可能"
fi

# venv作成
echo ""
echo "仮想環境を作成しています..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ 依存パッケージをインストール"

# Amazon Kindle確認
if [ -d "/Applications/Amazon Kindle.app" ]; then
    echo "✓ Amazon Kindle.app を検出"
else
    echo ""
    echo "⚠ Amazon Kindle.app が見つかりません。"
    echo "  App StoreまたはAmazonからインストールしてください。"
fi

# 権限案内
echo ""
echo "============================================"
echo "  macOS権限の設定が必要です"
echo "============================================"
echo ""
echo "以下の権限をターミナルアプリに付与してください:"
echo ""
echo "1. アクセシビリティ"
echo "   システム設定 → プライバシーとセキュリティ → アクセシビリティ"
echo "   → ターミナル（またはiTerm）を許可"
echo ""
echo "2. 画面収録"
echo "   システム設定 → プライバシーとセキュリティ → 画面収録"
echo "   → ターミナル（またはiTerm）を許可"
echo ""
echo "============================================"
echo "  セットアップ完了!"
echo "============================================"
echo ""
echo "起動コマンド:"
echo "  source .venv/bin/activate && python main.py"
echo ""
