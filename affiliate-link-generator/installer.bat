@echo off
chcp 65001 > nul
title アフィリエイトリンク生成ツール - 自動セットアップ

echo.
echo ==========================================
echo 🛍️ アフィリエイトリンク生成ツール v1.0
echo     自動セットアップ & インストーラー
echo ==========================================
echo.

REM 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 管理者権限が必要です
    echo 右クリック→「管理者として実行」してください
    pause
    exit /b 1
)

echo 🔍 システム環境をチェック中...
echo.

REM Pythonインストールチェック
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python が見つかりません
    echo.
    echo 📥 Python を自動インストールしますか？
    echo    1. はい（推奨）
    echo    2. いいえ（手動でインストール）
    echo.
    set /p choice="選択してください (1 または 2): "
    
    if "!choice!"=="1" (
        echo.
        echo 🌐 Python インストーラーをダウンロード中...
        
        REM Python インストーラーダウンロード
        powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python_installer.exe'}"
        
        if exist python_installer.exe (
            echo ✅ ダウンロード完了
            echo 🚀 Python をインストール中...
            echo    ※ インストール画面で「Add Python to PATH」にチェックしてください
            
            python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
            
            echo ⏳ インストール完了を待機中...
            timeout /t 30 /nobreak
            
            REM インストール後の確認
            python --version >nul 2>&1
            if !errorlevel! neq 0 (
                echo ❌ Python インストールに失敗しました
                echo 手動でインストールしてください: https://www.python.org/downloads/
                pause
                exit /b 1
            )
            
            echo ✅ Python インストール完了
            del python_installer.exe
        ) else (
            echo ❌ ダウンロードに失敗しました
            echo 手動でインストールしてください: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo 📌 手動インストール手順:
        echo 1. https://www.python.org/downloads/ にアクセス
        echo 2. 最新版をダウンロード
        echo 3. インストール時に「Add Python to PATH」にチェック
        echo 4. インストール後、このファイルを再実行
        pause
        exit /b 1
    )
)

echo ✅ Python: インストール済み
python --version

REM Google Chrome チェック
echo.
echo 🔍 Google Chrome をチェック中...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome: インストール済み
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome: インストール済み
) else (
    echo ❌ Google Chrome が見つかりません
    echo.
    echo 📥 Google Chrome を自動インストールしますか？
    set /p chrome_choice="インストールする場合は Y を入力: "
    
    if /i "!chrome_choice!"=="Y" (
        echo 🌐 Google Chrome インストーラーをダウンロード中...
        powershell -Command "& {Invoke-WebRequest -Uri 'https://dl.google.com/chrome/install/chrome_installer.exe' -OutFile 'chrome_installer.exe'}"
        
        if exist chrome_installer.exe (
            echo 🚀 Google Chrome をインストール中...
            chrome_installer.exe /silent /install
            timeout /t 20 /nobreak
            del chrome_installer.exe
            echo ✅ Google Chrome インストール完了
        )
    )
)

echo.
echo 📦 必要なパッケージをインストール中...
python -m pip install --upgrade pip
python -m pip install selenium openpyxl requests beautifulsoup4 pyshorteners webdriver-manager tkinter-tooltip

echo.
echo 🎉 セットアップ完了！
echo.
echo 📋 使用方法:
echo 1. run_app.py をダブルクリックでアプリを起動
echo 2. 設定メニューでアフィリエイトIDを設定
echo 3. ExcelファイルのB列に商品名を入力して処理実行
echo.
echo 🚀 アプリケーションを起動しますか？
set /p start_choice="起動する場合は Y を入力: "

if /i "!start_choice!"=="Y" (
    python run_app.py
)

echo.
echo ✨ セットアップが完了しました！
pause