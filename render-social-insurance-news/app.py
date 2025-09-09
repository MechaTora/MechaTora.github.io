#!/usr/bin/env python3
"""
Render版 社会保険ニュースサイト - Flask App
スマホ特化・i-mobile/Zucks広告対応
"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import subprocess
import sys

app = Flask(__name__)

# 設定
app.config['JSON_AS_ASCII'] = False

class SocialInsuranceNewsApp:
    """Render版ニュースアプリ"""
    
    def __init__(self):
        # 絶対パスを使用してファイル読み込みを確実にする
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(base_dir, 'data', 'processed_news.json')
        self.report_file = os.path.join(base_dir, 'data', 'daily_report.json')
    
    def load_news_data(self):
        """ニュースデータ読み込み"""
        try:
            print(f"データファイルパス: {self.data_file}")
            print(f"ファイル存在チェック: {os.path.exists(self.data_file)}")
            print(f"現在の作業ディレクトリ: {os.getcwd()}")
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"データ読み込み成功: {len(data.get('news', []))}件")
                return data
            else:
                print("データファイルが存在しません")
                # フォールバック用のサンプルデータを提供
                return {
                    'news': [{
                        'title': 'データ準備中',
                        'url': '#',
                        'source': 'システム',
                        'category': 'その他', 
                        'importance': '低',
                        'summary': '現在ニュースデータを準備中です。しばらくお待ちください。',
                        'keywords': ['準備中'],
                        'published_date': datetime.now().strftime('%Y年%m月%d日'),
                        'scraped_at': datetime.now().isoformat()
                    }],
                    'total_count': 1,
                    'categories': {'その他': 1}
                }
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return {'news': [], 'total_count': 0, 'categories': {}}
    
    def load_report_data(self):
        """レポートデータ読み込み"""
        try:
            if os.path.exists(self.report_file):
                with open(self.report_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'summary': {'high_importance': 0, 'categories': [], 'top_keywords': []}}
        except Exception as e:
            print(f"レポート読み込みエラー: {e}")
            return {'summary': {'high_importance': 0, 'categories': [], 'top_keywords': []}}
    
    def update_news(self):
        """ニュース更新（手動実行用）"""
        try:
            # メインの自動化スクリプトを実行（絶対パス使用）
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, 'scripts', 'main_automation.py')
            print(f"自動化スクリプトパス: {script_path}")
            print(f"スクリプト存在確認: {os.path.exists(script_path)}")
            
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=300)
            
            print(f"スクリプト実行結果 - returncode: {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            
            if result.returncode == 0:
                return {
                    "status": "success", 
                    "message": "ニュース更新完了",
                    "stdout": result.stdout,
                    "debug_info": {
                        "script_path": script_path,
                        "script_exists": os.path.exists(script_path),
                        "working_dir": os.getcwd()
                    }
                }
            else:
                return {
                    "status": "error", 
                    "message": f"更新エラー: returncode={result.returncode}",
                    "stderr": result.stderr,
                    "stdout": result.stdout,
                    "debug_info": {
                        "script_path": script_path,
                        "script_exists": os.path.exists(script_path),
                        "working_dir": os.getcwd(),
                        "python_path": sys.executable
                    }
                }
                
        except subprocess.TimeoutExpired as e:
            return {
                "status": "error", 
                "message": "更新タイムアウト（5分）",
                "error_details": str(e)
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"更新エラー: {str(e)}",
                "error_type": type(e).__name__,
                "debug_info": {
                    "script_path": script_path if 'script_path' in locals() else "未定義",
                    "working_dir": os.getcwd()
                }
            }

# アプリインスタンス
news_app = SocialInsuranceNewsApp()

@app.route('/')
def index():
    """メインページ"""
    news_data = news_app.load_news_data()
    report_data = news_app.load_report_data()
    
    # スマホ特化のコンテキスト準備
    context = {
        'news': news_data.get('news', [])[:20],  # スマホ表示用に20件に制限
        'total_count': news_data.get('total_count', 0),
        'categories': news_data.get('categories', {}),
        'high_importance': report_data.get('summary', {}).get('high_importance', 0),
        'category_count': len(news_data.get('categories', {})),
        'top_keywords': report_data.get('summary', {}).get('top_keywords', [])[:5],
        'last_updated': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
        'today_count': len([n for n in news_data.get('news', []) 
                           if n.get('published_date', '').startswith(datetime.now().strftime('%Y'))]),
    }
    
    return render_template('index.html', **context)

@app.route('/privacy')
def privacy():
    """プライバシーポリシーページ"""
    return render_template('privacy.html')

@app.route('/api/news')
def api_news():
    """ニュースAPI（JSON）"""
    news_data = news_app.load_news_data()
    return jsonify(news_data)

@app.route('/api/update')
def api_update():
    """手動更新API"""
    result = news_app.update_news()
    return jsonify(result)

@app.route('/health')
def health_check():
    """ヘルスチェック（Render用）"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "social-insurance-news"
    })

if __name__ == '__main__':
    # 開発環境
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Render環境（Gunicorn使用）
    application = app