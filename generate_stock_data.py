 #!/usr/bin/env python3
  """
  GitHub Actions用株価データ生成スクリプト - 安全版
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

  # 監視銘柄リスト - 日本株25銘柄でAPI上限500calls完全活用
  STOCKS_TO_MONITOR = {
      # 主要日本株25銘柄
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
      "8766.T": {"name": "東京海上ホールディングス", "country": "JP", "category": "finance"},
      "9020.T": {"name": "東日本旅客鉄道", "country": "JP", "category": "transport"},
      "4568.T": {"name": "第一三共", "country": "JP", "category": "pharma"},
      "6098.T": {"name": "リクルートホールディングス", "country": "JP", "category": "services"},
      "8058.T": {"name": "三菱商事", "country": "JP", "category": "trading"},
      "6954.T": {"name": "ファナック", "country": "JP", "category": "industrial"},
      "9432.T": {"name": "日本電信電話", "country": "JP", "category": "telecom"},
      "4063.T": {"name": "信越化学工業", "country": "JP", "category": "chemicals"},
      "7267.T": {"name": "ホンダ", "country": "JP", "category": "automotive"},
      "6367.T": {"name": "ダイキン工業", "country": "JP", "category": "industrial"},
      "4519.T": {"name": "中外製薬", "country": "JP", "category": "pharma"},
      "9735.T": {"name": "セコム", "country": "JP", "category": "security"},
      "4578.T": {"name": "大塚ホールディングス", "country": "JP", "category": "pharma"},
      "6326.T": {"name": "クボタ", "country": "JP", "category": "industrial"},
      "7751.T": {"name": "キヤノン", "country": "JP", "category": "electronics"}
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
          base_price = 2000  # 日本株のベース価格
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
          print(f"📊 Processing {len(STOCKS_TO_MONITOR)} stocks...")
          stocks = []
          failed_count = 0

          for i, (symbol, info) in enumerate(STOCKS_TO_MONITOR.items(), 1):
              print(f"  [{i}/{len(STOCKS_TO_MONITOR)}] Fetching {symbol}...")

              try:
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
                      print(f"    ✅ Success: {symbol} = {stock_data['price']}")
                  else:
                      failed_count += 1
                      print(f"    ❌ Failed: {symbol}")
                      if failed_count >= 5:
                          print("⚠️ Too many failures, switching to mock data...")
                          stocks = generate_mock_data()
                          break

                  # API制限対策: より安全な間隔 (4 calls/minute = 15秒間隔)
                  if i < len(STOCKS_TO_MONITOR):  # 最後の銘柄では待機しない
                      time.sleep(15)

              except Exception as e:
                  failed_count += 1
                  print(f"    ❌ Exception for {symbol}: {e}")
                  if failed_count >= 5:
                      print("⚠️ Too many exceptions, switching to mock data...")
                      stocks = generate_mock_data()
                      break

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
