@echo off
echo ========================================
echo 🔧 Google Chrome 自動インストール
echo ========================================
echo.

echo 1. Google Chrome の存在確認中...
where chrome.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Google Chrome が見つかりました
) else (
    echo ⚠️ Google Chrome が見つかりません
    echo.
    echo 2. Google Chrome を自動ダウンロード中...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi' -OutFile '%TEMP%\chrome_installer.msi'}"
    
    if exist "%TEMP%\chrome_installer.msi" (
        echo 3. Google Chrome をインストール中...
        msiexec /i "%TEMP%\chrome_installer.msi" /quiet /norestart
        echo ✅ Google Chrome インストール完了
        del "%TEMP%\chrome_installer.msi"
    ) else (
        echo ❌ ダウンロードに失敗しました
        echo 手動でインストールしてください: https://www.google.com/chrome/
        start https://www.google.com/chrome/
    )
)

echo.
echo 4. ChromeDriver の自動更新中...
python -m pip install --upgrade webdriver-manager

echo.
echo 5. テスト実行中...
python source_code/run_app.py
pause