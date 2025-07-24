#!/bin/bash

echo "📈 日本株リアルタイム監視システム起動中..."
echo ""

# 現在のディレクトリに移動
cd "$(dirname "$0")"

# 依存関係確認・インストール
echo "🔧 依存関係をチェック中..."
pip3 install -r requirements_jp_stock.txt

echo ""
echo "⚠️  重要: API Keyを設定してください！"
echo "   jp_stock_trading_hours.py の8行目を編集"
echo "   API_KEY = \"ここにあなたのAPI Key\""
echo ""

read -p "API Keyは設定済みですか？ (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 サーバーを起動します..."
    python3 jp_stock_trading_hours.py
else
    echo "❌ 先にAPI Keyを設定してください"
    echo "1. jp_stock_trading_hours.py をテキストエディタで開く"
    echo "2. 8行目の API_KEY = \"...\" を編集"
    echo "3. 再度このスクリプトを実行"
fi

read -p "Enterキーを押して終了..."