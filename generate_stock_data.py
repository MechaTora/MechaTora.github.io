 #!/usr/bin/env python3
  import json
  import os
  from datetime import datetime, timezone
  import random

  # 25銘柄維持
  STOCKS = {
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

  def main():
      print("📊 Generating 25 Japanese stocks data...")

      stocks = []
      for symbol, info in STOCKS.items():
          price = round(random.uniform(1600, 2400), 2)
          change_pct = round(random.uniform(-3, 3), 2)
          change = round(price * (change_pct / 100), 2)

          stocks.append({
              'symbol': symbol,
              'name': info['name'],
              'country': info['country'],
              'category': info['category'],
              'price': price,
              'change': change,
              'changePercent': change_pct,
              'volume': random.randint(100000, 2000000),
              'lastUpdate': datetime.now(timezone.utc).isoformat()
          })

      os.makedirs('stock-monitor-pro/data', exist_ok=True)

      output = {
          'success': True,
          'timestamp': datetime.now(timezone.utc).isoformat(),
          'total': len(stocks),
          'data': stocks
      }

      with open('stock-monitor-pro/data/stocks.json', 'w', encoding='utf-8') as f:
          json.dump(output, f, ensure_ascii=False, indent=2)

      print(f"✅ Generated {len(stocks)} Japanese stocks")

  if __name__ == '__main__':
      main()
