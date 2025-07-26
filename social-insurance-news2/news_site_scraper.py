#!/usr/bin/env python3
"""
ニュースサイト社会保険情報スクレイパー
NHK、朝日新聞、日経新聞などから社会保険関連ニュースを収集
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import hashlib

class NewsBaseScraper:
    """ニュースサイト基底クラス"""
    
    def __init__(self, base_url: str, name: str):
        self.base_url = base_url
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 強化された社会保険キーワード
        self.social_insurance_keywords = [
            # 基本制度
            '社会保険', '健康保険', '厚生年金', '国民年金', '雇用保険', '労災保険', '介護保険',
            
            # 具体的制度・用語
            '協会けんぽ', '組合健保', '国民健康保険', '後期高齢者医療',
            '老齢年金', '障害年金', '遺族年金', '基礎年金', '厚生年金基金',
            '失業給付', '育児休業給付', '介護休業給付', '教育訓練給付',
            '労働災害', '業務災害', '通勤災害', '労災認定',
            '要介護認定', '介護サービス', '介護報酬',
            
            # 保険料・給付関連
            '保険料率', '保険料改定', '標準報酬', '賞与', '保険給付',
            '医療費', '窓口負担', '高額療養費', '傷病手当金',
            '出産育児一時金', '出産手当金', '児童手当',
            
            # 制度変更・政策
            '制度改正', '法改正', '適用拡大', '制度見直し',
            '社会保障', '医療制度改革', '年金制度改革',
            
            # 組織・機関
            '厚生労働省', '日本年金機構', '全国健康保険協会',
            '健康保険組合', '国民健康保険組合', '協会けんぽ',
            
            # 関連用語
            '被保険者', '被扶養者', '保険者', '事業主', '給与所得者',
            'マイナンバーカード', 'マイナ保険証', '健康保険証'
        ]
    
    def is_social_insurance_related(self, text: str) -> bool:
        """社会保険関連判定（強化版）"""
        text_lower = text.lower()
        return any(keyword in text for keyword in self.social_insurance_keywords)
    
    def safe_request(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """安全なHTTPリクエスト"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ {self.name} リクエストエラー ({url}): {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """テキストクリーニング"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text.strip()
    
    def extract_date_from_text(self, text: str) -> Optional[str]:
        """テキストから日付抽出"""
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})月(\d{1,2})日',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:
                    return f"{match.group(1)}年{match.group(2)}月{match.group(3)}日"
                elif len(match.groups()) == 2:
                    current_year = datetime.now().year
                    return f"{current_year}年{match.group(1)}月{match.group(2)}日"
        
        return None
    
    def generate_news_id(self, url: str, title: str) -> str:
        """ニュースID生成"""
        content = f"{url}_{title}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

class NHKScraper(NewsBaseScraper):
    """NHKニュース社会保険スクレイパー"""
    
    def __init__(self):
        super().__init__("https://www3.nhk.or.jp", "NHKニュース")
        self.search_urls = [
            "/news/cat08.html",  # 政治
            "/news/cat05.html",  # 経済
            "/news/cat07.html"   # 暮らし
        ]
    
    def scrape_news(self, days_back: int = 7) -> List[Dict]:
        """NHKニュース収集"""
        print(f"📺 {self.name} 社会保険関連ニュース収集開始...")
        news_list = []
        
        for search_url in self.search_urls:
            full_url = self.base_url + search_url
            soup = self.safe_request(full_url)
            
            if not soup:
                continue
            
            # ニュース記事リンクを取得
            news_links = soup.find_all('a', href=re.compile(r'/news/html/\d+/'))
            
            for link in news_links[:20]:  # 最新20件をチェック
                try:
                    title = self.clean_text(link.get_text())
                    href = link.get('href')
                    
                    if not title or not href:
                        continue
                    
                    # 社会保険関連かチェック
                    if not self.is_social_insurance_related(title):
                        continue
                    
                    full_article_url = urljoin(self.base_url, href)
                    
                    # 記事詳細取得
                    article_data = self.get_article_details(full_article_url, title)
                    if article_data:
                        news_list.append(article_data)
                        print(f"  ✅ NHK収集: {title[:50]}...")
                    
                    time.sleep(1)  # 礼儀正しい間隔
                    
                except Exception as e:
                    print(f"  ❌ NHKエラー: {e}")
                    continue
        
        print(f"📺 {self.name}: {len(news_list)}件収集完了")
        return news_list
    
    def get_article_details(self, url: str, title: str) -> Optional[Dict]:
        """NHK記事詳細取得"""
        soup = self.safe_request(url)
        if not soup:
            return None
        
        # 記事本文取得
        content_elem = soup.find('div', class_='content--detail-body') or soup.find('div', class_='content')
        content = self.clean_text(content_elem.get_text()) if content_elem else ""
        
        # 日付取得
        date_elem = soup.find('time') or soup.find('div', class_='content--date')
        published_date = self.extract_date_from_text(date_elem.get_text()) if date_elem else datetime.now().strftime('%Y年%m月%d日')
        
        return {
            'id': self.generate_news_id(url, title),
            'title': title,
            'url': url,
            'content': content,
            'source': self.name,
            'published_date': published_date,
            'scraped_at': datetime.now().isoformat(),
            'content_length': len(content)
        }

class YahooNewsScraper(NewsBaseScraper):
    """Yahoo!ニュース社会保険スクレイパー"""
    
    def __init__(self):
        super().__init__("https://news.yahoo.co.jp", "Yahoo!ニュース")
        self.search_keywords = [
            "社会保険", "年金", "健康保険", "雇用保険", "介護保険"
        ]
    
    def scrape_news(self, days_back: int = 7) -> List[Dict]:
        """Yahoo!ニュース収集"""
        print(f"🌐 {self.name} 社会保険関連ニュース収集開始...")
        news_list = []
        
        for keyword in self.search_keywords:
            search_url = f"{self.base_url}/search?p={keyword}&ei=UTF-8"
            soup = self.safe_request(search_url)
            
            if not soup:
                continue
            
            # 検索結果のニュースリンクを取得
            news_links = soup.find_all('a', href=re.compile(r'/articles/'))
            
            for link in news_links[:10]:  # 各キーワード10件まで
                try:
                    title = self.clean_text(link.get_text())
                    href = link.get('href')
                    
                    if not title or not href:
                        continue
                    
                    # 重複チェック
                    if any(news.get('url') == href for news in news_list):
                        continue
                    
                    full_article_url = urljoin(self.base_url, href)
                    
                    # 記事詳細取得
                    article_data = self.get_article_details(full_article_url, title)
                    if article_data:
                        news_list.append(article_data)
                        print(f"  ✅ Yahoo収集: {title[:50]}...")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ❌ Yahooエラー: {e}")
                    continue
            
            time.sleep(2)  # キーワード間の間隔
        
        print(f"🌐 {self.name}: {len(news_list)}件収集完了")
        return news_list
    
    def get_article_details(self, url: str, title: str) -> Optional[Dict]:
        """Yahoo!記事詳細取得"""
        soup = self.safe_request(url)
        if not soup:
            return None
        
        # 記事本文取得
        content_elem = soup.find('div', class_='articleBody') or soup.find('div', class_='article_body')
        content = self.clean_text(content_elem.get_text()) if content_elem else ""
        
        # 日付取得
        date_elem = soup.find('time') or soup.find('span', class_='source')
        published_date = self.extract_date_from_text(date_elem.get_text()) if date_elem else datetime.now().strftime('%Y年%m月%d日')
        
        return {
            'id': self.generate_news_id(url, title),
            'title': title,
            'url': url,
            'content': content,
            'source': self.name,
            'published_date': published_date,
            'scraped_at': datetime.now().isoformat(),
            'content_length': len(content)
        }

class SocialInsuranceNewsAggregator:
    """社会保険ニュース統合収集システム"""
    
    def __init__(self):
        self.scrapers = [
            NHKScraper(),
            YahooNewsScraper(),
        ]
    
    def collect_all_news(self) -> List[Dict]:
        """全ニュースサイトから収集"""
        print("🌟 社会保険ニュース統合収集開始")
        all_news = []
        
        for scraper in self.scrapers:
            try:
                news = scraper.scrape_news()
                all_news.extend(news)
                time.sleep(3)  # サイト間の礼儀正しい間隔
                
            except Exception as e:
                print(f"❌ {scraper.name} 収集エラー: {e}")
                continue
        
        # 重複除去
        unique_news = []
        seen_urls = set()
        
        for news in all_news:
            url = news.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(news)
        
        print(f"🎉 統合収集完了: {len(unique_news)}件（重複除去後）")
        return unique_news

if __name__ == "__main__":
    # テスト実行
    aggregator = SocialInsuranceNewsAggregator()
    news_results = aggregator.collect_all_news()
    
    print(f"\n📊 収集結果:")
    for i, news in enumerate(news_results[:10]):
        print(f"{i+1}. {news['title'][:60]}... ({news['source']})")
    
    # 結果をJSONで保存
    import json
    with open('news_sites_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'collection_time': datetime.now().isoformat(),
            'total_count': len(news_results),
            'news': news_results
        }, f, ensure_ascii=False, indent=2)