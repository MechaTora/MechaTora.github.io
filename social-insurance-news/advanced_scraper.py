#!/usr/bin/env python3
"""
社会保険ニュース高度スクレイピングシステム
サイト別専用クラス + 統合管理
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import hashlib
from typing import List, Dict, Optional

class BaseScraper:
    """スクレイピングベースクラス"""
    
    def __init__(self, base_url: str, name: str):
        self.base_url = base_url
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SocialInsuranceBot/1.0; +https://github.com/social-insurance-news)'
        })
        
        self.social_keywords = [
            '健康保険', '厚生年金', '雇用保険', '労災保険', '介護保険',
            '社会保険', '保険料', '年金', '給付', '適用拡大', '制度改正',
            '被保険者', '事業主', '保険者', '協会けんぽ', '国民年金',
            # 追加キーワード
            '老齢年金', '障害年金', '遺族年金', '失業給付', '育児休業給付',
            '介護休業給付', '教育訓練給付', '労働災害', '業務災害', '通勤災害',
            '労災給付', '要介護', '要支援', '介護給付', '介護報酬',
            'メリット制', '被扶養者', '保険給付', '月次納付率', '施行状況',
            '特例', '日本年金機構', '組合健保', '国民健康保険'
        ]
    
    def is_social_insurance_related(self, text: str) -> bool:
        """社会保険関連判定"""
        return any(keyword in text for keyword in self.social_keywords)
    
    def clean_text(self, text: str) -> str:
        """テキストクリーニング"""
        # 改行・タブ・余分なスペース除去
        text = re.sub(r'\s+', ' ', text)
        # HTMLエンティティデコード
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text.strip()
    
    def extract_date(self, text: str) -> Optional[str]:
        """日付抽出"""
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'令和(\d+)年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if '令和' in pattern:
                    # 令和年を西暦に変換
                    reiwa_year = int(match.group(1))
                    year = 2018 + reiwa_year
                    return f"{year}年{match.group(2)}月{match.group(3)}日"
                else:
                    return match.group(0)
        
        return None
    
    def generate_hash(self, url: str, title: str) -> str:
        """記事のユニークハッシュ生成"""
        content = f"{url}_{title}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def safe_request(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """安全なHTTPリクエスト"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ {self.name} リクエストエラー ({url}): {e}")
            return None

class MHLWScraper(BaseScraper):
    """厚生労働省専用スクレイパー"""
    
    def __init__(self):
        super().__init__("https://www.mhlw.go.jp", "厚生労働省")
        # 月別報道発表一覧ページを使用
        self.monthly_urls = [
            "/stf/houdou/houdou_list_202501.html",  # 2025年1月
            "/stf/houdou/houdou_list_202412.html",  # 2024年12月
        ]
    
    def scrape_news(self, days_back: int = 30) -> List[Dict]:
        """月別報道発表一覧からニュース収集"""
        print(f"🏛️ {self.name} ニュース収集開始...")
        news_list = []
        
        for monthly_url in self.monthly_urls:
            print(f"  📅 {monthly_url} を調査中...")
            soup = self.safe_request(self.base_url + monthly_url)
            if not soup:
                continue
            
            # 全リンクから社会保険関連ニュースを抽出
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                try:
                    title = self.clean_text(link.get_text())
                    href = link.get('href')
                    
                    if not title or not href or len(title) < 10:
                        continue
                    
                    # ニュース記事URLパターンチェック
                    if not (('/stf/houdou/' in href or '/newpage_' in href) and 
                           '.html' in href and
                           'list' not in href and 
                           'index' not in href):
                        continue
                    
                    # 社会保険関連フィルタ
                    if not self.is_social_insurance_related(title):
                        continue
                    
                    full_url = urljoin(self.base_url, href)
                    
                    # 重複チェック
                    if any(news.get('url') == full_url for news in news_list):
                        continue
                    
                    # 記事詳細取得
                    article_data = self.get_article_details(full_url, title)
                    if article_data:
                        news_list.append(article_data)
                        print(f"  ✅ 収集: {title[:60]}...")
                    
                    # 礼儀正しい間隔
                    time.sleep(1)
                    
                    # 制限（1つの月から最大10件）
                    monthly_count = sum(1 for n in news_list if monthly_url in str(n.get('scraped_at', '')))
                    if monthly_count >= 10:
                        break
                        
                except Exception as e:
                    print(f"  ❌ エラー: {e}")
                    continue
        
        print(f"🏛️ {self.name}: {len(news_list)}件収集完了")
        return news_list
    
    def get_article_details(self, url: str, title: str) -> Optional[Dict]:
        """記事詳細情報取得"""
        soup = self.safe_request(url)
        if not soup:
            return None
        
        try:
            # 本文抽出
            content_selectors = [
                '.main-content', '.article-body', '.content-area',
                '#main', '.section-content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = self.clean_text(content_elem.get_text())[:2000]
                    break
            
            # 日付抽出
            date_text = soup.get_text()
            published_date = self.extract_date(date_text)
            
            return {
                'id': self.generate_hash(url, title),
                'title': title,
                'url': url,
                'content': content,
                'source': self.name,
                'published_date': published_date or datetime.now().strftime('%Y年%m月%d日'),
                'scraped_at': datetime.now().isoformat(),
                'content_length': len(content)
            }
            
        except Exception as e:
            print(f"記事詳細取得エラー: {e}")
            return None

class NenkinScraper(BaseScraper):
    """日本年金機構専用スクレイパー"""
    
    def __init__(self):
        super().__init__("https://www.nenkin.go.jp", "日本年金機構")
        self.news_url = "/oshirase/"
    
    def scrape_news(self, days_back: int = 3) -> List[Dict]:
        """お知らせ一覧からニュース収集"""
        print(f"💰 {self.name} ニュース収集開始...")
        news_list = []
        
        soup = self.safe_request(self.base_url + self.news_url)
        if not soup:
            return news_list
        
        # お知らせリスト取得
        news_items = soup.find_all('li', class_=re.compile(r'news|item'))
        if not news_items:
            # 代替セレクタ
            news_items = soup.find_all('a', href=re.compile(r'/oshirase/'))
        
        for item in news_items[:15]:
            try:
                # タイトルとリンク抽出
                link_elem = item.find('a') if item.name != 'a' else item
                if not link_elem:
                    continue
                
                title = self.clean_text(link_elem.get_text())
                if not self.is_social_insurance_related(title):
                    continue
                
                href = link_elem.get('href')
                full_url = urljoin(self.base_url, href)
                
                # 記事データ構築
                article_data = {
                    'id': self.generate_hash(full_url, title),
                    'title': title,
                    'url': full_url,
                    'content': title,  # 詳細は後で取得
                    'source': self.name,
                    'published_date': datetime.now().strftime('%Y年%m月%d日'),
                    'scraped_at': datetime.now().isoformat()
                }
                
                news_list.append(article_data)
                print(f"  ✅ 収集: {title[:50]}...")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        print(f"💰 {self.name}: {len(news_list)}件収集完了")
        return news_list

class SocialInsuranceNewsCollector:
    """統合ニュース収集管理"""
    
    def __init__(self):
        self.scrapers = [
            MHLWScraper(),
            NenkinScraper()
        ]
        self.collected_news = []
        self.seen_hashes = set()
    
    def collect_all_news(self) -> List[Dict]:
        """全サイトからニュース収集"""
        print("🌅 社会保険ニュース一括収集開始")
        start_time = datetime.now()
        
        all_news = []
        for scraper in self.scrapers:
            try:
                news_list = scraper.scrape_news()
                
                # 重複除去
                for news in news_list:
                    if news['id'] not in self.seen_hashes:
                        self.seen_hashes.add(news['id'])
                        all_news.append(news)
                        
            except Exception as e:
                print(f"❌ {scraper.name} 収集エラー: {e}")
                continue
        
        # 日付でソート (新しい順)
        all_news.sort(key=lambda x: x['scraped_at'], reverse=True)
        
        duration = (datetime.now() - start_time).seconds
        print(f"🎉 収集完了: {len(all_news)}件 ({duration}秒)")
        
        self.collected_news = all_news
        return all_news
    
    def save_raw_data(self, filename: str = 'raw_news_data.json'):
        """生データ保存"""
        output_data = {
            'collection_time': datetime.now().isoformat(),
            'total_count': len(self.collected_news),
            'sources': list(set(news['source'] for news in self.collected_news)),
            'news': self.collected_news
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 生データ保存: {filename}")
        return output_data

if __name__ == "__main__":
    # テスト実行
    collector = SocialInsuranceNewsCollector()
    news_data = collector.collect_all_news()
    collector.save_raw_data()
    
    print(f"\n📊 収集結果:")
    for news in news_data[:3]:
        print(f"- {news['title'][:60]}... ({news['source']})")