#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
楽天商品検索・アフィリエイトリンク生成モジュール
requests + BeautifulSoupを使用した楽天商品検索
"""

import time
import re
import urllib.parse
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RakutenScraper:
    def __init__(self, affiliate_id: str, api_key: str = "", search_interval: float = 2.0):
        """
        楽天検索スクレーパーを初期化
        
        Args:
            affiliate_id (str): 楽天アフィリエイトID
            api_key (str): 楽天API キー（オプション）
            search_interval (float): 検索間隔（秒）
        """
        self.affiliate_id = affiliate_id
        self.api_key = api_key
        self.search_interval = search_interval
        
        # セッション設定
        self.session = requests.Session()
        
        # リトライ設定（urllib3バージョン互換性対応）
        try:
            # urllib3 v2.0以降の新しいAPI
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        except TypeError:
            try:
                # urllib3 v1.x の古いAPI
                retry_strategy = Retry(
                    total=3,
                    status_forcelist=[429, 500, 502, 503, 504],
                    method_whitelist=["HEAD", "GET", "OPTIONS"],
                    backoff_factor=1
                )
            except Exception as e:
                # フォールバック: シンプルなリトライ設定
                print(f"⚠️ リトライ設定エラー、基本設定を使用: {str(e)}")
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1
                )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # ヘッダー設定
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # タイムアウト設定
        self.timeout = 30
        
        print(f"✅ 楽天スクレーパー初期化完了 (アフィリエイトID: {affiliate_id[:10]}...)")
    
    def search_product(self, product_name: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        商品を検索してアイテムコードとURLを取得
        
        Args:
            product_name (str): 検索する商品名
            max_results (int): 最大取得件数
            
        Returns:
            List[Dict]: 商品情報のリスト
        """
        try:
            print(f"🔍 楽天検索中: {product_name}")
            
            # 検索クエリの準備
            encoded_query = urllib.parse.quote_plus(product_name)
            search_url = f"https://search.rakuten.co.jp/search/mall/{encoded_query}/"
            
            # 検索実行
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            
            if response.status_code != 200:
                print(f"❌ 楽天検索エラー: HTTP {response.status_code}")
                return []
            
            # HTMLパース
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 商品要素の取得（複数のセレクターを試行）
            product_elements = []
            
            # パターン1: メイン商品エリア
            products_1 = soup.select('div[data-iteam-info]')
            product_elements.extend(products_1)
            
            # パターン2: 商品リスト
            if not product_elements:
                products_2 = soup.select('.searchresultitem')
                product_elements.extend(products_2)
            
            # パターン3: 商品カード
            if not product_elements:
                products_3 = soup.select('[data-testid="item"]')
                product_elements.extend(products_3)
                
            # パターン4: 一般的なセレクター
            if not product_elements:
                products_4 = soup.select('div[class*="item"]')
                product_elements.extend(products_4[:20])  # 多すぎる場合は制限
            
            if not product_elements:
                print(f"❌ 検索結果が見つかりません: {product_name}")
                return []
            
            print(f"🔍 {len(product_elements)}個の商品要素を発見")
            
            products = []
            processed_count = 0
            
            for element in product_elements:
                try:
                    if processed_count >= max_results:
                        break
                    
                    # 商品リンクの取得
                    link_element = element.find('a', href=True)
                    if not link_element:
                        continue
                    
                    product_url = link_element.get('href')
                    if not product_url:
                        continue
                    
                    # 相対URLの場合は絶対URLに変換
                    if product_url.startswith('/'):
                        product_url = 'https://item.rakuten.co.jp' + product_url
                    elif not product_url.startswith('http'):
                        continue
                    
                    # 楽天商品URLの検証
                    if 'item.rakuten.co.jp' not in product_url:
                        continue
                    
                    # 商品タイトル取得
                    title = ""
                    title_selectors = [
                        link_element.get('title'),
                        link_element.find('img', alt=True),
                        element.find(class_=re.compile(r'title|name')),
                        element.find('h2'),
                        element.find('h3')
                    ]
                    
                    for selector in title_selectors:
                        if selector:
                            if hasattr(selector, 'get_text'):
                                title = selector.get_text(strip=True)
                            elif hasattr(selector, 'get'):
                                title = selector.get('alt', '') or selector.get('title', '')
                            else:
                                title = str(selector).strip()
                            
                            if title:
                                break
                    
                    if not title:
                        title = "商品名不明"
                    
                    # アイテムコード抽出
                    item_code = self._extract_item_code(product_url)
                    
                    # アフィリエイトリンク生成
                    affiliate_url = self._generate_affiliate_link(product_url, item_code)
                    
                    products.append({
                        'item_code': item_code,
                        'title': title[:100],  # タイトル長制限
                        'url': product_url,
                        'affiliate_url': affiliate_url
                    })
                    processed_count += 1
                    
                except Exception as e:
                    # 個別商品の処理エラーは継続
                    continue
            
            print(f"✅ 楽天検索完了: {len(products)}件の商品を取得")
            
            # 検索間隔の待機
            if self.search_interval > 0:
                time.sleep(self.search_interval)
            
            return products
            
        except requests.RequestException as e:
            print(f"❌ 楽天検索ネットワークエラー: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ 楽天検索エラー: {str(e)}")
            return []
    
    def _extract_item_code(self, url: str) -> str:
        """
        商品URLからアイテムコードを抽出
        
        Args:
            url (str): 商品URL
            
        Returns:
            str: アイテムコード
        """
        try:
            # パターン1: /shop/store_id/item_code/
            pattern1 = re.search(r'item\.rakuten\.co\.jp/([^/]+)/([^/?]+)', url)
            if pattern1:
                shop_id = pattern1.group(1)
                item_id = pattern1.group(2)
                return f"{shop_id}:{item_id}"
            
            # パターン2: URLパラメータから取得
            if '?' in url:
                from urllib.parse import parse_qs, urlparse
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                # よくあるパラメータ名
                for param_name in ['iid', 'item_id', 'item']:
                    if param_name in params and params[param_name]:
                        return params[param_name][0]
            
            # パターン3: URLパスから推測
            path_parts = url.split('/')
            if len(path_parts) >= 2:
                for i, part in enumerate(path_parts):
                    if 'item.rakuten.co.jp' in part and i + 2 < len(path_parts):
                        return f"{path_parts[i+1]}:{path_parts[i+2]}"
            
            # デフォルトはURL全体のハッシュを使用
            import hashlib
            return hashlib.md5(url.encode()).hexdigest()[:16]
            
        except Exception as e:
            print(f"⚠️ アイテムコード抽出エラー: {str(e)}")
            return "unknown"
    
    def _generate_affiliate_link(self, original_url: str, item_code: str) -> str:
        """
        アフィリエイトリンクを生成
        
        Args:
            original_url (str): 元のURL
            item_code (str): アイテムコード
            
        Returns:
            str: アフィリエイトリンク
        """
        try:
            # 既存のパラメータを保持
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            parsed = urlparse(original_url)
            params = parse_qs(parsed.query)
            
            # アフィリエイトパラメータを追加
            params['iasid'] = [self.affiliate_id]
            
            # 他の有用なパラメータも追加可能
            # params['icm'] = ['1']  # 成果報酬型
            
            # URL再構築
            new_query = urlencode(params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            affiliate_url = urlunparse(new_parsed)
            
            return affiliate_url
            
        except Exception as e:
            print(f"❌ 楽天アフィリエイトリンク生成エラー: {str(e)}")
            # エラー時は元のURLにアフィリエイトIDを単純追加
            separator = '&' if '?' in original_url else '?'
            return f"{original_url}{separator}iasid={self.affiliate_id}"
    
    def get_best_match(self, product_name: str) -> Optional[Dict[str, str]]:
        """
        最適な商品を1件取得
        
        Args:
            product_name (str): 商品名
            
        Returns:
            Optional[Dict]: 商品情報またはNone
        """
        products = self.search_product(product_name, max_results=1)
        
        if products:
            return products[0]
        else:
            return None
    
    def test_connection(self) -> bool:
        """
        楽天接続テスト
        
        Returns:
            bool: 接続成功時True
        """
        try:
            print("🔍 楽天接続テスト中...")
            response = self.session.get("https://www.rakuten.co.jp", timeout=self.timeout)
            response.raise_for_status()
            
            if response.status_code == 200:
                print("✅ 楽天接続テスト成功")
                return True
            else:
                print(f"❌ 楽天接続テスト失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 楽天接続テストエラー: {str(e)}")
            return False
    
    def close(self):
        """リソースのクリーンアップ"""
        try:
            if self.session:
                self.session.close()
                print("✅ 楽天セッション終了完了")
        except Exception as e:
            print(f"⚠️ 楽天セッション終了エラー: {str(e)}")
    
    def __enter__(self):
        """コンテキストマネージャー - 開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー - 終了"""
        self.close()


def test_rakuten_scraper():
    """楽天 Scraperのテスト"""
    print("=== 楽天 Scraper テスト ===")
    
    # テスト用のアフィリエイトID（実際のIDに置き換えてください）
    test_affiliate_id = "123456789"
    
    try:
        with RakutenScraper(affiliate_id=test_affiliate_id) as scraper:
            # 接続テスト
            if not scraper.test_connection():
                print("❌ 接続テスト失敗")
                return
            
            # 商品検索テスト
            test_products = ["iPhone", "マウス", "コーヒー"]
            
            for product in test_products:
                print(f"\n--- {product} の検索テスト ---")
                results = scraper.search_product(product, max_results=3)
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title'][:50]}...")
                    print(f"   アイテムコード: {result['item_code']}")
                    print(f"   URL: {result['affiliate_url'][:80]}...")
                    print()
    
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")


if __name__ == "__main__":
    test_rakuten_scraper()