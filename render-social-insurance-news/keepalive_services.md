# Render スリープ回避サービス一覧

## 1. UptimeRobot（推奨・無料）
- URL: https://uptimerobot.com/
- 無料プラン: 50監視まで、5分間隔
- 設定URL: `https://social-insurance-news-render-1.onrender.com/health`

## 2. Cron-job.org（無料）
- URL: https://cron-job.org/
- 無料プラン: 無制限、1分間隔可能
- 設定URL: `https://social-insurance-news-render-1.onrender.com`

## 3. Ping-o-Matic（無料）
- URL: https://pingomatic.com/
- 手動またはAPI経由でping送信

## 4. ローカルスクリプト（Windows）
- バッチファイルで定期実行
- タスクスケジューラー使用

## 推奨設定
- 監視間隔: 10-15分
- タイムアウト: 30秒
- 対象URL: `/health` エンドポイント（軽量）