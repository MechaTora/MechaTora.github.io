@echo off
echo 📈 日本株リアルタイム監視システム起動中...
echo.

REM 現在のディレクトリに移動
cd /d "%~dp0"

REM 依存関係確認・インストール
echo 🔧 依存関係をチェック中...
pip install -r requirements_jp_stock.txt

echo.
echo ⚠️  重要: API Keyを設定してください！
echo    jp_stock_trading_hours.py の8行目を編集
echo    API_KEY = "ここにあなたのAPI Key"
echo.

pause

REM サーバー起動
echo 🚀 サーバーを起動します...
python jp_stock_trading_hours.py

pause