@echo off
chcp 65001 > nul
title Amazon・楽天アフィリエイトリンク生成ツール

echo.
echo ========================================
echo 🛍️ アフィリエイトリンク生成ツール v1.0
echo ========================================
echo.

REM Pythonの存在確認
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pythonがインストールされていません
    echo    https://www.python.org/downloads/ からダウンロードしてください
    pause
    exit /b 1
)

REM アプリケーション起動
echo 🚀 アプリケーション起動中...
echo.
python run_app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ アプリケーションの起動に失敗しました
    pause
)

echo.
pause