#!/usr/bin/env python3
"""
GitHub Actions用株価データ生成スクリプト
Alpha Vantage APIから株価データを取得してJSONファイルを生成
"""

import requests
import json
import os
import time
from datetime import datetime, timezone, timedelta

# Alpha Vantage API設定
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = "https://www.alphavantage.co/query"

# 監視銘柄リスト
STOCKS_TO_MONITOR = {
    # 日本株
    "7203.T": {"name": "トヨタ自動車", "country": "JP", "category": "automotive"},
    "9984.T": {"name": "ソフトバンクグループ", "country": "JP", "category": "telecom"},
    "6758.T": {"name": "ソニーグループ", "country": "JP", "category": "electronics"},
    "9433.T": {"name": "KDDI", "country": "JP", "category": "telecom"},
    "6861.T": {"name": "キーエンス", "country": "JP", "category": "industrial"},
    "8035.T": {"name": "東京エレクトロン", "country": "JP", "category": "tech"},
    "4755.T": {"name": "楽天グループ", "country": "JP", "category": "ecommerce"},
    "4502.T": {"name": "武田薬品工業", "country": "JP", "category": "pharma"},
    "8001.T": {"name": "伊藤忠商事", "country": "JP", "category": "trading"},
    "7974.T": {"name": "任天堂", "country": "JP", "category": "gaming"},
    
    # アメリカ株
    "AAPL": {"name": "Apple Inc.", "country": "US", "category": "tech"},
    "GOOGL": {"name": "Alphabet Inc.", "country": "US", "category": "tech"},
    "MSFT": {"name": "Microsoft Corporation", "country": "US", "category": "tech"},
    "AMZN": {"name": "Amazon.com Inc.", "country": "US", "category": "ecommerce"},
    "TSLA": {"name": "Tesla Inc.", "country": "US", "category": "automotive"},
    "META": {"name": "Meta Platforms Inc.", "country": "US", "category": "social"},
    "NVDA": {"name": "NVIDIA Corporation", "country": "US", "category": "tech"},
    "NFLX": {"name": "Netflix Inc.", "country": "US", "category": "entertainment"},
    "UBER": {"name": "Uber Technologies", "country": "US", "category": "transport"},
    "PYPL": {"name": "PayPal Holdings", "country": "US", "category": "fintech"}
}

def fetch_stock_data(symbol):
    """Alpha Vantage APIから個別銘柄データを取得"""
    try:
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                'volume': int(quote.get('06. volume', 0)),
                'last_update': datetime.now(timezone.utc).isoformat()
            }
        else:
            print(f"API Error for {symbol}: {data}")
            return None
            
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def generate_mock_data():
    """APIが利用できない場合のモックデータ生成"""
    import random
    
    stocks = []
    for symbol, info in STOCKS_TO_MONITOR.items():
        base_price = 100 if info['country'] == 'US' else 2000
        price_variation = random.uniform(0.8, 1.2)
        price = round(base_price * price_variation, 2)
        
        change_percent = random.uniform(-3, 3)
        change = round(price * (change_percent / 100), 2)
        
        stocks.append({
            'symbol': symbol,
            'name': info['name'],
            'country': info['country'],
            'category': info['category'],
            'price': price,
            'change': change,
            'changePercent': change_percent,
            'volume': random.randint(100000, 2000000),
            'lastUpdate': datetime.now(timezone.utc).isoformat()
        })
    
    return stocks

def main():
    """メイン処理"""
    print("📊 Stock data generation started...")
    
    if not API_KEY or API_KEY == 'YOUR_ALPHA_VANTAGE_API_KEY_HERE':
        print("⚠️ No Alpha Vantage API key found, generating mock data...")
        stocks = generate_mock_data()
    else:
        print("🔗 Fetching real data from Alpha Vantage API...")
        stocks = []
        
        for symbol, info in STOCKS_TO_MONITOR.items():
            print(f"  Fetching {symbol}...")
            
            stock_data = fetch_stock_data(symbol)
            
            if stock_data:
                stocks.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'country': info['country'],
                    'category': info['category'],
                    'price': stock_data['price'],
                    'change': stock_data['change'],
                    'changePercent': stock_data['change_percent'],
                    'volume': stock_data.get('volume', 0),
                    'lastUpdate': stock_data['last_update']
                })
                
                # API制限対策: ギリギリ速度 (5 API calls/minute = 12秒間隔)
                time.sleep(12.1)
            else:
                print(f"  Failed to fetch {symbol}, skipping...")
    
    # データファイル保存
    output_dir = 'stock-monitor-pro/data'
    os.makedirs(output_dir, exist_ok=True)
    
    output_data = {
        'success': True,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total': len(stocks),
        'data': stocks
    }
    
    output_file = os.path.join(output_dir, 'stocks.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated data for {len(stocks)} stocks")
    print(f"📁 Saved to: {output_file}")

if __name__ == '__main__':
    main()