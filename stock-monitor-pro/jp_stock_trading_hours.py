#!/usr/bin/env python3
"""
日本株特化プロキシサーバー - 取引時間限定版
前場: 09:00-11:30, 後場: 12:30-15:30のみ更新
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import time
import os
from datetime import datetime, timedelta
import threading
import sqlite3
import pytz
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)
CORS(app)

# 設定
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_API_KEY_HERE')  # 環境変数から取得
DATABASE_FILE = "jp_stock_cache.db"
JST = pytz.timezone('Asia/Tokyo')

# 日本株銘柄リスト（厳選25銘柄）
JP_STOCKS = {
    # 超大型株（時価総額上位）
    "7203.T": {"name": "トヨタ自動車", "category": "automotive", "priority": "high"},
    "9984.T": {"name": "ソフトバンクグループ", "category": "telecom", "priority": "high"},
    "6758.T": {"name": "ソニーグループ", "category": "electronics", "priority": "high"},
    "9433.T": {"name": "KDDI", "category": "telecom", "priority": "high"},
    "8306.T": {"name": "三菱UFJフィナンシャル・グループ", "category": "finance", "priority": "high"},
    
    # テクノロジー・成長株
    "6861.T": {"name": "キーエンス", "category": "industrial", "priority": "high"},
    "8035.T": {"name": "東京エレクトロン", "category": "tech", "priority": "high"},
    "4755.T": {"name": "楽天グループ", "category": "ecommerce", "priority": "high"},
    "6954.T": {"name": "ファナック", "category": "industrial", "priority": "medium"},
    "4689.T": {"name": "Zホールディングス", "category": "internet", "priority": "medium"},
    
    # 製造業大手
    "6501.T": {"name": "日立製作所", "category": "conglomerate", "priority": "medium"},
    "6752.T": {"name": "パナソニック ホールディングス", "category": "electronics", "priority": "medium"},
    "7751.T": {"name": "キヤノン", "category": "electronics", "priority": "medium"},
    "6367.T": {"name": "ダイキン工業", "category": "industrial", "priority": "medium"},
    "6594.T": {"name": "日本電産", "category": "industrial", "priority": "medium"},
    
    # 素材・化学
    "4063.T": {"name": "信越化学工業", "category": "chemical", "priority": "medium"},
    "4901.T": {"name": "富士フイルムホールディングス", "category": "chemical", "priority": "medium"},
    "6503.T": {"name": "三菱電機", "category": "electronics", "priority": "low"},
    
    # 医薬品
    "4502.T": {"name": "武田薬品工業", "category": "pharma", "priority": "medium"},
    "4578.T": {"name": "大塚ホールディングス", "category": "pharma", "priority": "medium"},
    
    # 商社・サービス
    "8001.T": {"name": "伊藤忠商事", "category": "trading", "priority": "medium"},
    "9432.T": {"name": "日本電信電話", "category": "telecom", "priority": "medium"},
    "8058.T": {"name": "三菱商事", "category": "trading", "priority": "medium"},
    
    # 小売・消費
    "9983.T": {"name": "ファーストリテイリング", "category": "retail", "priority": "medium"},
    "7974.T": {"name": "任天堂", "category": "gaming", "priority": "high"}
}

def init_database():
    """データベース初期化"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jp_stock_data (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            priority TEXT,
            price REAL,
            change_amount REAL,
            change_percent REAL,
            volume INTEGER,
            last_update TIMESTAMP,
            session TEXT,
            raw_data TEXT
        )
    ''')
    
    # 銘柄マスターデータ挿入
    for symbol, info in JP_STOCKS.items():
        cursor.execute('''
            INSERT OR REPLACE INTO jp_stock_data 
            (symbol, name, category, priority, price, change_amount, change_percent, last_update)
            VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL)
        ''', (symbol, info['name'], info['category'], info['priority']))
    
    conn.commit()
    conn.close()

def is_trading_hours():
    """取引時間内かチェック"""
    now = datetime.now(JST)
    current_time = now.time()
    weekday = now.weekday()
    
    # 土日は取引なし
    if weekday >= 5:  # 5=土曜, 6=日曜
        return False, "weekend"
    
    # 前場: 09:00-11:30
    morning_start = datetime.strptime("09:00", "%H:%M").time()
    morning_end = datetime.strptime("11:30", "%H:%M").time()
    
    # 後場: 12:30-15:30  
    afternoon_start = datetime.strptime("12:30", "%H:%M").time()
    afternoon_end = datetime.strptime("15:30", "%H:%M").time()
    
    if morning_start <= current_time <= morning_end:
        return True, "morning"
    elif afternoon_start <= current_time <= afternoon_end:
        return True, "afternoon"
    else:
        return False, "closed"

def get_update_interval():
    """優先度別更新間隔（分）"""
    is_trading, session = is_trading_hours()
    
    if not is_trading:
        return None  # 取引時間外は更新しない
    
    # 取引時間内は15分間隔で全銘柄更新
    return 15

def fetch_stock_data(symbol):
    """Alpha Vantage APIから株価データ取得"""
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                    'volume': int(float(quote.get('06. volume', 0))),
                    'raw_data': json.dumps(data)
                }
        
        print(f"Failed to fetch {symbol}: {response.text[:200]}")
        return None
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def update_stocks_batch():
    """取引時間内での株価更新"""
    is_trading, session = is_trading_hours()
    
    if not is_trading:
        print(f"Market closed ({session}). Skipping update.")
        return
    
    print(f"Starting {session} session update at {datetime.now(JST).strftime('%H:%M:%S')}")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    updated_count = 0
    
    for symbol, info in JP_STOCKS.items():
        try:
            stock_data = fetch_stock_data(symbol)
            
            if stock_data:
                cursor.execute('''
                    UPDATE jp_stock_data 
                    SET price = ?, change_amount = ?, change_percent = ?, 
                        volume = ?, last_update = ?, session = ?, raw_data = ?
                    WHERE symbol = ?
                ''', (
                    stock_data['price'],
                    stock_data['change'],
                    stock_data['change_percent'],
                    stock_data['volume'],
                    datetime.now(JST).isoformat(),
                    session,
                    stock_data['raw_data'],
                    symbol
                ))
                updated_count += 1
                print(f"Updated {symbol}: ¥{stock_data['price']:.0f} ({stock_data['change_percent']:+.2f}%)")
            
            # API制限対策: 12秒間隔
            time.sleep(12)
            
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Update completed. {updated_count}/{len(JP_STOCKS)} stocks updated.")

def trading_hours_scheduler():
    """取引時間監視スケジューラー"""
    last_update = None
    
    while True:
        try:
            is_trading, session = is_trading_hours()
            now = datetime.now(JST)
            
            if is_trading:
                interval = get_update_interval()
                
                # 初回更新または指定間隔経過
                if (last_update is None or 
                    (now - last_update).total_seconds() >= interval * 60):
                    
                    update_stocks_batch()
                    last_update = now
                    
                    print(f"Next update in {interval} minutes...")
                    time.sleep(interval * 60)
                else:
                    time.sleep(30)  # 30秒後に再チェック
            else:
                # 取引時間外は1分ごとにチェック
                print(f"Market {session}. Next check at {now.strftime('%H:%M:%S')}")
                time.sleep(60)
                
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(60)

# APIエンドポイント
@app.route('/api/jp-stocks')
def get_jp_stocks():
    """日本株データ取得API"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, name, category, priority, price, change_amount, 
                   change_percent, volume, last_update, session
            FROM jp_stock_data
            ORDER BY priority DESC, change_percent DESC
        ''')
        
        stocks = []
        for row in cursor.fetchall():
            stocks.append({
                'symbol': row[0],
                'name': row[1],
                'category': row[2],
                'priority': row[3],
                'price': row[4],
                'change': row[5],
                'changePercent': row[6],
                'volume': row[7],
                'lastUpdate': row[8],
                'session': row[9]
            })
        
        conn.close()
        
        is_trading, current_session = is_trading_hours()
        
        return jsonify({
            'success': True,
            'data': stocks,
            'timestamp': datetime.now(JST).isoformat(),
            'total': len(stocks),
            'market': {
                'isOpen': is_trading,
                'session': current_session,
                'timezone': 'Asia/Tokyo'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-status')
def get_market_status():
    """市場状況取得API"""
    try:
        is_trading, session = is_trading_hours()
        now = datetime.now(JST)
        
        # 次の取引開始/終了時刻計算
        if session == "morning":
            next_change = "11:30 (昼休み)"
        elif session == "afternoon":
            next_change = "15:30 (取引終了)"
        elif session == "closed":
            if now.time() < datetime.strptime("09:00", "%H:%M").time():
                next_change = "09:00 (前場開始)"
            elif now.time() < datetime.strptime("12:30", "%H:%M").time():
                next_change = "12:30 (後場開始)"
            else:
                next_change = "翌営業日 09:00"
        else:
            next_change = "月曜日 09:00"
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jp_stock_data WHERE price IS NOT NULL')
        stocks_with_data = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(last_update) FROM jp_stock_data')
        last_update = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'market': {
                'isOpen': is_trading,
                'session': session,
                'nextChange': next_change,
                'currentTime': now.strftime('%H:%M:%S'),
                'date': now.strftime('%Y-%m-%d')
            },
            'data': {
                'totalStocks': len(JP_STOCKS),
                'stocksWithData': stocks_with_data,
                'lastUpdate': last_update
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """ルートページ"""
    is_trading, session = is_trading_hours()
    status = "🟢 取引中" if is_trading else "🔴 取引時間外"
    
    return f"""
    <h1>📈 日本株リアルタイム監視システム</h1>
    <h2>{status} ({session})</h2>
    <p>取引時間: 前場 09:00-11:30, 後場 12:30-15:30</p>
    <ul>
        <li><a href="/api/jp-stocks">日本株データ</a></li>
        <li><a href="/api/market-status">市場状況</a></li>
    </ul>
    <p>監視銘柄: {len(JP_STOCKS)}銘柄</p>
    """

if __name__ == '__main__':
    print("🚀 日本株特化プロキシサーバー起動中...")
    
    # データベース初期化
    init_database()
    
    # 取引時間監視スケジューラー開始
    scheduler_thread = threading.Thread(target=trading_hours_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("✅ サーバー準備完了！")
    print(f"現在時刻: {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S JST')}")
    
    is_trading, session = is_trading_hours()
    print(f"市場状況: {'🟢 取引中' if is_trading else '🔴 取引時間外'} ({session})")
    
    app.run(host='0.0.0.0', port=5000, debug=True)