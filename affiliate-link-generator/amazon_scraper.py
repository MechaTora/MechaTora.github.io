#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon商品検索・アフィリエイトリンク生成モジュール
Seleniumを使用したAmazon商品検索
"""

import time
import re
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException, WebDriverException, 
    NoSuchElementException, ElementClickInterceptedException
)


class AmazonScraper:
    def __init__(self, associate_id: str, headless: bool = True, search_interval: float = 2.0):
        """
        Amazon検索スクレーパーを初期化
        
        Args:
            associate_id (str): Amazon アソシエイトID
            headless (bool): ヘッドレスモードを使用するか
            search_interval (float): 検索間隔（秒）
        """
        self.associate_id = associate_id
        self.headless = headless
        self.search_interval = search_interval
        self.driver = None
        self.is_initialized = False
        
    def initialize_driver(self) -> bool:
        """
        WebDriverを初期化
        
        Returns:
            bool: 初期化成功時True
        """
        try:
            print("🔧 Chrome WebDriver を初期化中...")
            
            # Chrome オプション設定
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # 安定性向上のためのオプション
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # 画像読み込み無効化で高速化
            chrome_options.add_argument('--disable-javascript')  # JS無効化
            
            # User-Agent設定
            user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # ログレベル設定
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # WebDriverの作成
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # タイムアウト設定
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # 自動化検知回避
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome WebDriver 初期化完了")
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ WebDriver初期化エラー: {str(e)}")
            if "chrome" in str(e).lower():
                print("   → Google Chromeが正しくインストールされているか確認してください")
            elif "chromedriver" in str(e).lower():
                print("   → ChromeDriverの自動ダウンロードに失敗しました")
            return False
    
    def search_product(self, product_name: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        商品を検索してASINとURLを取得
        
        Args:
            product_name (str): 検索する商品名
            max_results (int): 最大取得件数
            
        Returns:
            List[Dict]: 商品情報のリスト
        """
        if not self.is_initialized or not self.driver:
            print("❌ WebDriverが初期化されていません")
            return []
        
        try:
            print(f"🔍 Amazon検索中: {product_name}")
            
            # 検索クエリのエンコード
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(product_name)
            search_url = f"https://www.amazon.co.jp/s?k={encoded_query}&ref=nb_sb_noss"
            
            print(f"🔗 検索URL: {search_url}")
            self.driver.get(search_url)
            
            # ページ読み込み待機
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # 複数のセレクターで検索結果を待機
                selectors = [
                    '[data-component-type="s-search-result"]',  # 新しいセレクター
                    '.s-result-item',  # 古いセレクター
                    '[data-cy="title-recipe-title"]',  # 代替セレクター
                    '.s-card-border'  # さらに代替
                ]
                
                element_found = None
                for selector in selectors:
                    try:
                        element_found = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        print(f"✅ 検索結果セレクター確認: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not element_found:
                    print(f"⚠️ 検索結果の読み込みがタイムアウトしました: {product_name}")
                    return []
                    
            except Exception as e:
                print(f"⚠️ 検索結果待機エラー: {str(e)}")
                return []
            
            # 複数のセレクターで商品要素を取得
            product_elements = []
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-cy="title-recipe-title"]',
                '.s-card-border'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_elements = elements
                    print(f"✅ 商品要素取得成功: {selector} ({len(elements)}件)")
                    break
            
            if not product_elements:
                print(f"❌ 検索結果が見つかりません: {product_name}")
                # デバッグ情報
                print("🔍 ページのHTMLタイトル確認中...")
                try:
                    page_title = self.driver.title
                    print(f"📄 ページタイトル: {page_title}")
                    
                    # ページソースの一部を確認
                    page_source = self.driver.page_source[:500]
                    print(f"📝 ページ内容（最初の500文字）: {page_source}")
                except Exception as e:
                    print(f"⚠️ デバッグ情報取得エラー: {str(e)}")
                return []
            
            products = []
            processed_count = 0
            
            for element in product_elements[:max_results * 2]:  # 余裕を持って多めに取得
                try:
                    if processed_count >= max_results:
                        break
                    
                    # ASIN取得（複数の方法を試行）
                    asin = None
                    asin_methods = [
                        lambda el: el.get_attribute('data-asin'),
                        lambda el: el.get_attribute('data-uuid'),
                        lambda el: self._extract_asin_from_element(el)
                    ]
                    
                    for method in asin_methods:
                        try:
                            asin = method(element)
                            if asin and asin.strip():
                                break
                        except:
                            continue
                    
                    if not asin:
                        continue
                    
                    # 商品タイトル取得（複数のセレクターを試行）
                    title = "商品名不明"
                    title_selectors = [
                        'h2 a span',
                        '[data-cy="title-recipe-title"]',
                        '.s-size-mini .s-link-style a',
                        'h2 span',
                        '.s-color-base'
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_element = element.find_element(By.CSS_SELECTOR, selector)
                            if title_element and title_element.text.strip():
                                title = title_element.text.strip()
                                break
                        except:
                            continue
                    
                    # 商品URL取得（複数のセレクターを試行）
                    product_url = None
                    link_selectors = [
                        'h2 a',
                        '[data-cy="title-recipe-title"]',
                        '.s-link-style a',
                        'a[href*="/dp/"]'
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, selector)
                            product_url = link_element.get_attribute('href')
                            if product_url and '/dp/' in product_url:
                                break
                        except:
                            continue
                    
                    if asin and product_url:
                        # アフィリエイトリンク生成
                        affiliate_url = self._generate_affiliate_link(asin, product_url)
                        
                        products.append({
                            'asin': asin,
                            'title': title,
                            'url': product_url,
                            'affiliate_url': affiliate_url
                        })
                        processed_count += 1
                        
                except Exception as e:
                    # 個別商品の処理エラーは継続
                    continue
            
            print(f"✅ Amazon検索完了: {len(products)}件の商品を取得")
            
            # 検索間隔の待機
            if self.search_interval > 0:
                time.sleep(self.search_interval)
            
            return products
            
        except Exception as e:
            print(f"❌ Amazon検索エラー: {str(e)}")
            return []
    
    def _extract_asin_from_element(self, element) -> str:
        """要素からASINを抽出する補助メソッド"""
        try:
            # href属性からASINを抽出
            links = element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href')
                if href and '/dp/' in href:
                    # /dp/ASIN/ の形式からASINを抽出
                    import re
                    match = re.search(r'/dp/([A-Z0-9]{10})/', href)
                    if match:
                        return match.group(1)
            
            # data属性を全て確認
            for attr in ['data-asin', 'data-uuid', 'data-itemid']:
                value = element.get_attribute(attr)
                if value and len(value) == 10:
                    return value
            
            return None
        except:
            return None
    
    def _generate_affiliate_link(self, asin: str, original_url: str) -> str:
        """
        アフィリエイトリンクを生成
        
        Args:
            asin (str): Amazon ASIN
            original_url (str): 元のURL
            
        Returns:
            str: アフィリエイトリンク
        """
        try:
            # 基本的なアフィリエイトリンク形式
            base_url = "https://www.amazon.co.jp/dp"
            affiliate_params = f"tag={self.associate_id}"
            
            affiliate_url = f"{base_url}/{asin}?{affiliate_params}"
            
            return affiliate_url
            
        except Exception as e:
            print(f"❌ アフィリエイトリンク生成エラー: {str(e)}")
            return original_url
    
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
        Amazon接続テスト
        
        Returns:
            bool: 接続成功時True
        """
        if not self.is_initialized or not self.driver:
            return False
        
        try:
            print("🔍 Amazon接続テスト中...")
            self.driver.get("https://www.amazon.co.jp")
            
            # タイトル確認
            wait = WebDriverWait(self.driver, 10)
            wait.until(lambda driver: "Amazon" in driver.title)
            
            print("✅ Amazon接続テスト成功")
            return True
            
        except Exception as e:
            print(f"❌ Amazon接続テストエラー: {str(e)}")
            return False
    
    def close(self):
        """リソースのクリーンアップ"""
        try:
            if self.driver:
                print("🔧 WebDriver終了中...")
                self.driver.quit()
                self.driver = None
                self.is_initialized = False
                print("✅ WebDriver終了完了")
        except Exception as e:
            print(f"⚠️ WebDriver終了エラー: {str(e)}")
    
    def __enter__(self):
        """コンテキストマネージャー - 開始"""
        if self.initialize_driver():
            return self
        else:
            raise RuntimeError("WebDriverの初期化に失敗しました")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー - 終了"""
        self.close()


def test_amazon_scraper():
    """Amazon Scraperのテスト"""
    print("=== Amazon Scraper テスト ===")
    
    # テスト用のアソシエイトID（実際のIDに置き換えてください）
    test_associate_id = "test-22"
    
    try:
        with AmazonScraper(associate_id=test_associate_id, headless=True) as scraper:
            # 接続テスト
            if not scraper.test_connection():
                print("❌ 接続テスト失敗")
                return
            
            # 商品検索テスト
            test_products = ["iPhone", "マウス"]
            
            for product in test_products:
                print(f"\n--- {product} の検索テスト ---")
                results = scraper.search_product(product, max_results=3)
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title'][:50]}...")
                    print(f"   ASIN: {result['asin']}")
                    print(f"   URL: {result['affiliate_url'][:80]}...")
                    print()
    
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")


if __name__ == "__main__":
    test_amazon_scraper()