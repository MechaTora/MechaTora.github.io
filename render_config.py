import os
from datetime import datetime
import pytz

# アプリケーション設定
class Config:
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'social-insurance-news-secret-key'
    
    # 日本時間設定
    TIMEZONE = pytz.timezone('Asia/Tokyo')
    
    # ニュース設定
    NEWS_UPDATE_INTERVAL = 24 * 60 * 60  # 24時間（秒）
    MAX_NEWS_COUNT = 100
    
    # カテゴリ設定
    NEWS_CATEGORIES = [
        {'id': 'その他', 'name': 'その他', 'emoji': '📄'},
        {'id': '介護保険', 'name': '介護保険', 'emoji': '🏥'},
        {'id': '健康保険', 'name': '健康保険', 'emoji': '💊'},
        {'id': '労災保険', 'name': '労災保険', 'emoji': '⚠️'},
        {'id': '厚生年金', 'name': '厚生年金', 'emoji': '💰'},
        {'id': '社会保険全般', 'name': '社会保険全般', 'emoji': '📋'},
        {'id': '雇用保険', 'name': '雇用保険', 'emoji': '💼'},
    ]
    
    # 重要度設定
    IMPORTANCE_LEVELS = {
        '高': {'emoji': '🚨', 'color': '#dc3545'},
        '中': {'emoji': '⚠️', 'color': '#fd7e14'},
        '低': {'emoji': 'ℹ️', 'color': '#6c757d'}
    }
    
    @staticmethod
    def get_current_time():
        return datetime.now(Config.TIMEZONE)
    
    @staticmethod
    def format_japanese_date(dt):
        return dt.strftime('%Y年%m月%d日 %H:%M')