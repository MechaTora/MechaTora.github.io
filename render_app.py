from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# 日本時間設定
JST = pytz.timezone('Asia/Tokyo')

def load_news_data():
    """ニュースデータを読み込み"""
    try:
        with open('processed_news.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_category_data(category_name):
    """カテゴリ別データを読み込み"""
    filename = f'category_{category_name}.json'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/')
def index():
    """メインページ"""
    # index.htmlファイルを読み込んでそのまま返す
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>社会保険ニュースサイト</h1><p>データを読み込み中...</p>"

@app.route('/api/news')
def api_news():
    """ニュースAPI"""
    news_data = load_news_data()
    return jsonify(news_data)

@app.route('/api/categories')
def api_categories():
    """カテゴリ一覧API"""
    categories = [
        'その他', '介護保険', '健康保険', '労災保険', 
        '厚生年金', '社会保険全般', '雇用保険'
    ]
    return jsonify(categories)

@app.route('/api/category/<category_name>')
def api_category(category_name):
    """カテゴリ別ニュースAPI"""
    category_data = load_category_data(category_name)
    return jsonify(category_data)

@app.route('/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(JST).isoformat(),
        'service': '社会保険ニュース'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)