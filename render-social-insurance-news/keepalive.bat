@echo off
REM Render サイト自動Keep-Alive（Windows用）
REM 10分間隔でサイトにアクセス

echo 🚀 Render Keep-Alive開始
echo 対象: https://social-insurance-news-render-1.onrender.com
echo 間隔: 10分

:loop
echo.
echo [%date% %time%] サイトにアクセス中...

REM PowerShellでHTTPリクエスト送信
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://social-insurance-news-render-1.onrender.com/health' -TimeoutSec 30; Write-Host '✅ 成功 - Status:' $response.StatusCode } catch { Write-Host '❌ エラー:' $_.Exception.Message }"

echo 😴 10分待機...
timeout /t 600 /nobreak >nul

goto loop