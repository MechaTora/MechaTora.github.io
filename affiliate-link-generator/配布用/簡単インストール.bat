@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title Amazon・楽天アフィリエイトリンク自動生成ツール - インストーラー

echo.
echo ================================
echo 🛍️ アフィリエイトリンク生成ツール
echo ================================
echo.
echo 📦 自動インストールを開始します...
echo.

:: 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 管理者権限が必要です。
    echo 右クリック→「管理者として実行」で起動してください。
    pause
    exit /b 1
)

:: Python インストールチェック
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 🐍 Python をインストールしています...
    echo.
    
    :: Python 3.11 ダウンロード
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'"
    
    :: Python インストール
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    :: インストーラー削除
    del python-installer.exe
    
    echo ✅ Python インストール完了
    echo.
)

:: パス更新
call refreshenv

:: pip アップデート
echo 📊 pip を最新版に更新中...
python -m pip install --upgrade pip

:: 必要パッケージのインストール
echo 📦 必要なライブラリをインストール中...
echo.

:: requirements.txt から一括インストール
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    :: 個別インストール
    python -m pip install selenium
    python -m pip install webdriver-manager
    python -m pip install openpyxl
    python -m pip install requests
    python -m pip install pyshorteners
)

:: Google Chrome チェック
echo 🌐 Google Chrome の確認中...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome が見つかりました
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Google Chrome が見つかりました
) else (
    echo ⚠️ Google Chrome が見つかりません
    echo.
    echo Chrome のインストールが必要です：
    echo https://www.google.com/chrome/
    echo.
    choice /c YN /m "Chrome のダウンロードページを開きますか？ (Y/N)"
    if !errorlevel! equ 1 start https://www.google.com/chrome/
)

:: 起動スクリプト作成
echo 🚀 起動スクリプトを作成中...
echo @echo off > start.bat
echo chcp 65001 ^> nul >> start.bat
echo echo 🛍️ アフィリエイトリンク生成ツール 起動中... >> start.bat
echo python run_app.py >> start.bat
echo pause >> start.bat

echo.
echo ================================
echo ✅ インストール完了！
echo ================================
echo.
echo 🎉 準備が整いました！
echo.
echo 📋 次にやること：
echo   1. Amazon・楽天アフィリエイトプログラムに登録
echo   2. start.bat をダブルクリックして起動
echo   3. 設定メニューでアフィリエイトIDを設定
echo.
echo 📖 詳細な使い方は「インストールと使い方.html」を参照
echo.
echo 🚀 今すぐ起動しますか？
choice /c YN /m "(Y: 起動 / N: 後で起動)"
if %errorlevel% equ 1 (
    start.bat
) else (
    echo.
    echo 💡 後で「start.bat」をダブルクリックして起動してください
)

echo.
echo 🌟 ご利用ありがとうございます！
pause