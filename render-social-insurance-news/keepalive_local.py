#!/usr/bin/env python3
"""
Render サイト自動スリープ回避スクリプト
10分間隔でサイトにアクセスしてスリープを防ぐ
"""

import requests
import time
import logging
from datetime import datetime

# 設定
SITE_URL = "https://social-insurance-news-render-1.onrender.com"
HEALTH_URL = f"{SITE_URL}/health"
PING_INTERVAL = 600  # 10分（秒）
TIMEOUT = 30

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keepalive.log'),
        logging.StreamHandler()
    ]
)

def ping_site():
    """サイトにpingを送信"""
    try:
        # ヘルスチェックエンドポイントにアクセス
        response = requests.get(HEALTH_URL, timeout=TIMEOUT)
        
        if response.status_code == 200:
            logging.info(f"✅ サイト生存確認成功 - Status: {response.status_code}")
            return True
        else:
            logging.warning(f"⚠️ 異常なレスポンス - Status: {response.status_code}")
            # メインページも試す
            main_response = requests.get(SITE_URL, timeout=TIMEOUT)
            if main_response.status_code == 200:
                logging.info("✅ メインページ経由で生存確認成功")
                return True
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ ping失敗: {e}")
        return False

def main():
    """メイン実行ループ"""
    logging.info(f"🚀 Render Keep-Alive開始 - 対象: {SITE_URL}")
    logging.info(f"📅 間隔: {PING_INTERVAL//60}分")
    
    while True:
        try:
            ping_site()
            logging.info(f"😴 {PING_INTERVAL//60}分待機...")
            time.sleep(PING_INTERVAL)
            
        except KeyboardInterrupt:
            logging.info("⏹️ Keep-Alive停止")
            break
        except Exception as e:
            logging.error(f"❌ 予期しないエラー: {e}")
            time.sleep(60)  # 1分待機後に再試行

if __name__ == "__main__":
    main()