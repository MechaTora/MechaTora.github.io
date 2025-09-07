#!/usr/bin/env python3
"""
Render版 社会保険ニュース自動化スクリプト
毎朝4時実行 - スクレイピング→AI要約→データ更新
"""

import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import random

# デバッグ出力
print("=== 社会保険ニュース自動化スクリプト開始 ===")
print(f"実行時刻: {datetime.now()}")
print(f"Python実行パス: {sys.executable}")
print(f"スクリプトディレクトリ: {Path(__file__).parent}")
print(f"作業ディレクトリ: {os.getcwd()}")
print("=" * 50)

# パス設定
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

class RenderNewsAutomation:
    """Render用ニュース自動化クラス（強化版）"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # データファイルパス
        self.processed_file = DATA_DIR / 'processed_news.json'
        self.report_file = DATA_DIR / 'daily_report.json'
        
        # レート制限設定
        self.rate_limits = {
            'mhlw.go.jp': 2.0,
            'nenkin.go.jp': 2.0,
            'news.yahoo.co.jp': 3.0
        }
        self.request_times = {}
        
        # エラー追跡
        self.error_count = {}
        
        # より詳細なカテゴリ定義
        self.detailed_categories = {
            "健康保険": {
                "keywords": ["健康保険", "協会けんぽ", "組合健保", "医療保険", "保険料率", "被扶養者"],
                "subcategories": ["保険料", "給付", "手続き", "制度変更"]
            },
            "厚生年金": {
                "keywords": ["厚生年金", "老齢年金", "障害年金", "遺族年金", "年金保険料", "受給"],
                "subcategories": ["保険料", "給付", "手続き", "制度変更"]
            },
            "雇用保険": {
                "keywords": ["雇用保険", "失業給付", "育児休業給付", "介護休業給付", "教育訓練給付"],
                "subcategories": ["給付", "手続き", "制度変更", "保険料"]
            },
            "労災保険": {
                "keywords": ["労災保険", "労働災害", "業務災害", "通勤災害", "労災給付"],
                "subcategories": ["給付", "認定", "手続き", "制度変更"]
            },
            "介護保険": {
                "keywords": ["介護保険", "要介護", "要支援", "介護給付", "介護報酬"],
                "subcategories": ["給付", "認定", "手続き", "制度変更"]
            },
            "社会保険全般": {
                "keywords": ["社会保険", "適用拡大", "被保険者", "事業主", "制度改正", "法改正"],
                "subcategories": ["制度変更", "適用", "手続き", "法令"]
            }
        }
        
        # 重要度判定キーワード
        self.importance_keywords = {
            "高": ["法改正", "制度改正", "新設", "廃止", "施行", "公布", "省令", "告示", "改定"],
            "中": ["見直し", "拡大", "縮小", "料率変更", "基準変更", "案", "予定"],
            "低": ["手続き", "様式", "お知らせ", "案内", "説明会", "パンフレット"]
        }
    
    def check_rate_limit(self, domain):
        """レート制限チェック"""
        now = datetime.now()
        
        if domain in self.request_times:
            last_request = self.request_times[domain]
            required_interval = self.rate_limits.get(domain, 2.0)
            
            elapsed = (now - last_request).total_seconds()
            if elapsed < required_interval:
                wait_time = required_interval - elapsed
                print(f"⏳ {domain} レート制限: {wait_time:.1f}秒待機")
                time.sleep(wait_time)
        
        self.request_times[domain] = now
    
    def scrape_mhlw_comprehensive(self):
        """厚生労働省総合ニュース取得（強化版）"""
        news_list = []
        
        try:
            print("🏛️ 厚生労働省ニュース取得開始（強化版）")
            
            # より多くの厚労省ページを対象にする
            mhlw_urls = [
                ('https://www.mhlw.go.jp/stf/houdou/houdou_list.html', 'プレスリリース'),
                ('https://www.mhlw.go.jp/stf/new-info/index.html', '新着情報'),
                ('https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/index.html', '医療保険'),
                ('https://www.nenkin.go.jp/info/index.html', '年金機構新着')
            ]
            
            for url, page_type in mhlw_urls:
                try:
                    domain = url.split('/')[2]
                    self.check_rate_limit(domain)
                    
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    print(f"  📄 {page_type}ページを解析中...")
                    
                    # より効果的なニュース項目抽出
                    links = soup.find_all('a', href=True)
                    extracted = 0
                    
                    for link in links[:50]:  # より多く検査
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        
                        # より厳格な社会保険関連フィルタリング
                        if self.is_social_insurance_relevant(title):
                            # 相対URLを絶対URLに変換
                            if href.startswith('/'):
                                if 'mhlw.go.jp' in url:
                                    full_url = 'https://www.mhlw.go.jp' + href
                                elif 'nenkin.go.jp' in url:
                                    full_url = 'https://www.nenkin.go.jp' + href
                                else:
                                    full_url = href
                            else:
                                full_url = href
                            
                            # より詳細な情報抽出
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': '年金機構' if 'nenkin.go.jp' in url else '厚生労働省',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence,
                                'content_length': len(title),
                                'page_type': page_type
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                            if extracted >= 10:  # 各ページから最大10件
                                break
                    
                    print(f"  ✅ {page_type}: {extracted}件取得")
                    
                except Exception as e:
                    print(f"  ❌ {page_type}取得エラー {url}: {e}")
                    self.error_count[url] = self.error_count.get(url, 0) + 1
                    continue
            
            print(f"✅ 厚労省総合ニュース {len(news_list)}件取得")
            return news_list
            
        except Exception as e:
            print(f"❌ 厚労省総合ニュース取得エラー: {e}")
            return []
    
    def scrape_yahoo_news(self):
        """Yahoo!ニュース 社会保険関連取得"""
        news_list = []
        
        try:
            print("📺 Yahoo!ニュース取得開始")
            
            # Yahoo!ニュース検索（社会保険関連）
            search_terms = ['社会保険', '厚生年金', '健康保険', '雇用保険', '年金改正']
            
            for term in search_terms:
                try:
                    search_url = f"https://news.yahoo.co.jp/search?p={term}&ei=UTF-8"
                    response = self.session.get(search_url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 現在のYahoo!ニュース構造に対応したセレクター
                    articles = soup.find_all('article') or soup.find_all('div', class_=lambda x: x and ('sc-' in x or 'newsFeed' in x))
                    
                    for article in articles[:5]:  # 各検索語で5件
                        try:
                            # より幅広いセレクター（現在のYahoo構造に対応）
                            link_elem = (
                                article.find('a', href=True) or 
                                article.find('a') or
                                article.find('h1')
                            )
                            
                            if not link_elem:
                                continue
                            
                            title = link_elem.get_text(strip=True)
                            url = link_elem.get('href', '') if link_elem.name == 'a' else ''
                            
                            # URLが空の場合は親要素からリンクを探す
                            if not url:
                                parent_link = article.find_parent('a') or article.find('a')
                                url = parent_link.get('href', '') if parent_link else ''
                            
                            if url.startswith('/'):
                                url = 'https://news.yahoo.co.jp' + url
                            elif not url.startswith('http'):
                                continue  # 無効なURLはスキップ
                            
                            news_item = {
                                'title': title,
                                'url': url,
                                'source': 'Yahoo!ニュース',
                                'category': self.categorize_news(title),
                                'importance': self.assess_importance(title),
                                'summary': f"【{self.categorize_news(title)}】 {title[:60]}...",
                                'keywords': self.extract_keywords(title),
                                'published_date': 'None',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            news_list.append(news_item)
                            
                        except Exception as e:
                            print(f"Yahoo記事解析エラー: {e}")
                            continue
                    
                    time.sleep(3)  # レート制限
                    
                except Exception as e:
                    print(f"Yahoo検索エラー {term}: {e}")
                    continue
            
            # 重複除去
            unique_news = []
            seen_titles = set()
            for news in news_list:
                if news['title'] not in seen_titles and len(news['title']) > 10:
                    unique_news.append(news)
                    seen_titles.add(news['title'])
            
            print(f"✅ Yahoo!ニュース {len(unique_news)}件取得（重複除去後）")
            if unique_news:
                print(f"📝 取得例: {unique_news[0]['title'][:50]}...")
            return unique_news
            
        except Exception as e:
            print(f"❌ Yahoo!ニュース取得エラー: {e}")
            return []
    
    def is_social_insurance_relevant(self, title):
        """社会保険関連の判定（大幅緩和版）"""
        if len(title.strip()) < 5:  # より短い閾値
            return False
        
        # 社会保険関連キーワード（大幅拡張版）
        relevant_keywords = [
            # 基本的な社会保険制度
            '健康保険', '厚生年金', '国民年金', '雇用保険', '労災保険', '介護保険',
            '社会保険', '被保険者', '保険料', '年金', '医療保険', '失業給付',
            '労働災害', '介護給付', '保険適用', '制度改正', '法改正',
            
            # 組織・制度名
            '協会けんぽ', '年金機構', '社労士', '給付金', '適用拡大',
            '厚生労働省', 'ハローワーク', '年金事務所', '社会保険労務士',
            
            # 関連する社会問題・政策（大幅拡張）
            '医療費', '高齢者', '障害者', '育児', '出産', '療養費',
            '扶養', '賃金', '労働者', '事業主', '保険制度', '社会保障',
            '福祉', '医療制度', '退職', '就職', '職業訓練',
            '休業補償', '通勤災害', '業務災害', '要介護', '要支援',
            
            # より幅広い関連キーワード
            '働き方改革', '少子高齢化', 'マイナンバー', '電子申請',
            '定年延長', '非正規雇用', '正社員化', 'DX', 'デジタル化',
            '手続き簡素化', '窓口', '相談', '申請', '給付',
            '認定', '審査', '支給', '受給', '納付', '徴収',
            
            # 新規追加（労働・経済関連）
            '最低賃金', '残業代', '有給休暇', '産休', '育休', '介護休暇',
            '労基法', '労働法', '労働基準', '時短勤務', 'テレワーク',
            '副業', '兼業', '転職', '就活', 'リストラ', 'リスキリング',
            '人手不足', '採用', '新卒', '中途', 'シニア', '女性活躍',
            '多様性', 'ダイバーシティ', 'インクルージョン', 'ワークライフバランス',
            
            # 経済・政策関連
            '税制改正', '所得税', '住民税', '消費税', '控除', '減税',
            '物価', 'インフレ', '景気', '経済政策', '政府', '国会',
            '予算', '財政', '補助金', '助成金', '支援策', 'コロナ支援'
        ]
        
        # 除外キーワード（関係ないもの）
        exclude_keywords = [
            'JavaScript', 'Cookie', 'PDF', 'システムメンテナンス',
            'ブラウザ', 'Internet Explorer', 'アクセシビリティ',
            'スポーツ', '芸能', 'エンタメ', '天気', '占い', 'ゲーム',
            '株価', '為替', '競馬', '宝くじ', 'パチンコ', 'アニメ', '映画'
        ]
        
        # 除外キーワードチェック
        for exclude in exclude_keywords:
            if exclude in title:
                return False
        
        # 関連キーワードチェック（1つでも含まれていればOK）
        for keyword in relevant_keywords:
            if keyword in title:
                return True
        
        # 部分キーワードもチェック（緩い条件）
        partial_keywords = [
            '保険', '年金', '給付', '制度', '労働', '医療', '福祉',
            '働', '仕事', '雇用', '退職', '就職', '病気', '介護',
            '子育て', '出産', '育児', '障害', '高齢', '申請', '手続き',
            '税', '料金', '支払い', '控除', '減免', '免除', '補助',
            '支援', '助成', '政策', '改正', '変更', '見直し'
        ]
        
        matched_partials = 0
        for keyword in partial_keywords:
            if keyword in title:
                matched_partials += 1
        
        # 1個以上の部分キーワードがあれば関連とする（大幅緩和）
        if matched_partials >= 1:
            return True
        
        return False
    
    def enhanced_categorization(self, title, content):
        """強化版カテゴリ分類"""
        text = title + " " + content
        
        category_scores = {}
        related_categories = []
        
        # 各カテゴリのスコア計算
        for category, data in self.detailed_categories.items():
            score = 0
            matched_keywords = []
            
            for keyword in data["keywords"]:
                count = text.count(keyword)
                if count > 0:
                    score += count * (len(keyword) / 3)  # 長いキーワードほど重要
                    matched_keywords.append(keyword)
            
            if score > 0:
                category_scores[category] = {
                    "score": score,
                    "keywords": matched_keywords
                }
        
        if not category_scores:
            return "その他", [], 0.0
        
        # 最高スコアのカテゴリを主カテゴリに
        primary_category = max(category_scores.keys(), key=lambda k: category_scores[k]["score"])
        confidence = min(category_scores[primary_category]["score"] / 10, 1.0)
        
        # 関連カテゴリ（スコア1.0以上）
        for cat, data in category_scores.items():
            if cat != primary_category and data["score"] >= 1.0:
                related_categories.append(cat)
        
        return primary_category, related_categories, confidence
    
    def enhanced_importance(self, title, content):
        """強化版重要度判定"""
        text = title + " " + content
        
        # 高重要度チェック
        for keyword in self.importance_keywords["高"]:
            if keyword in text:
                return "高"
        
        # 中重要度チェック
        for keyword in self.importance_keywords["中"]:
            if keyword in text:
                return "中"
        
        return "低"
    
    def enhanced_keywords(self, title, content):
        """強化版キーワード抽出"""
        import re
        text = title + " " + content
        keywords = []
        
        # 制度名・組織名抽出
        institution_patterns = [
            r'協会けんぽ', r'健康保険組合', r'年金事務所', r'年金機構',
            r'厚生労働省', r'社会保険労務士', r'労働基準監督署'
        ]
        
        for pattern in institution_patterns:
            if re.search(pattern, text):
                keywords.append(pattern)
        
        # 金額・率・期間抽出
        numeric_patterns = [
            (r'\d+\.?\d*%', 'パーセント'),
            (r'\d+(?:,\d+)*円', '金額'),
            (r'\d+(?:,\d+)*万円', '万円単位'),
            (r'\d+年\d+月', '年月'),
            (r'令和\d+年', '令和年'),
            (r'平成\d+年', '平成年')
        ]
        
        for pattern, desc in numeric_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches[:3])  # 最大3個まで
        
        return list(set(keywords))[:10]  # 重複除去・上位10個
    
    def create_summary(self, title, category, keywords):
        """詳細要約文作成"""
        import re
        
        # タイトルから重要部分抽出
        title_clean = re.sub(r'について$|に関して$|のお知らせ$', '', title)
        
        summary_parts = []
        
        # カテゴリ表示
        summary_parts.append(f"【{category}】")
        
        # 主要内容（タイトルベース）
        if len(title_clean) > 20:
            title_summary = title_clean[:30] + "..."
        else:
            title_summary = title_clean
        summary_parts.append(title_summary)
        
        # 重要キーワード追加
        if keywords:
            key_info = []
            for keyword in keywords[:3]:
                if '%' in keyword or '円' in keyword or '年' in keyword:
                    key_info.append(keyword)
            
            if key_info:
                summary_parts.append(f"({', '.join(key_info)})")
        
        summary = " ".join(summary_parts)
        return summary[:120]  # 120文字制限
    
    def generate_id(self, title, url):
        """ニュースID生成"""
        import hashlib
        return hashlib.md5((title + url).encode()).hexdigest()[:8]
    
    def scrape_news_sites_comprehensive(self):
        """ニュースサイト総合スクレイピング（強化版）"""
        news_list = []
        
        try:
            print("📰 ニュースサイト総合スクレイピング開始")
            
            # 複数のニュースサイトから収集（Yahoo復活 + 代替ソース追加）
            news_sites = [
                {
                    'name': 'Yahoo!ニュース',
                    'base_url': 'https://news.yahoo.co.jp',
                    'search_terms': ['社会保険', '厚生年金', '健康保険', '雇用保険', '年金改正', '介護保険', '労災保険', '年金制度', '医療保険制度', '保険料改正', '働き方改革', '最低賃金'],
                    'scraper': self.scrape_yahoo_simple
                },
                {
                    'name': 'NHKニュース',
                    'base_url': 'https://www3.nhk.or.jp',
                    'search_terms': ['社会保険', '年金', '医療保険', '雇用', '労働', '厚生労働省'],
                    'scraper': self.scrape_nhk_news
                },
                {
                    'name': '時事通信',
                    'base_url': 'https://www.jiji.com',
                    'search_terms': ['社会保険', '厚生年金', '健康保険', '雇用保険', '年金改正', '介護保険', '労災保険'],
                    'scraper': self.scrape_jiji_news
                },
                {
                    'name': '共同通信',
                    'base_url': 'https://www.kyodo.co.jp',
                    'search_terms': ['社会保険', '年金制度', '医療制度', '雇用制度', '労働政策'],
                    'scraper': self.scrape_kyodo_news
                },
                {
                    'name': 'ITmedia ビジネス',
                    'base_url': 'https://www.itmedia.co.jp/business',
                    'search_terms': ['社会保険', '働き方改革', '労働法', '雇用保険', '厚生年金'],
                    'scraper': self.scrape_itmedia_news
                }
            ]
            
            for site_config in news_sites:
                try:
                    print(f"  📱 {site_config['name']}からニュース収集中...")
                    site_news = site_config['scraper'](site_config)
                    
                    if site_news:
                        news_list.extend(site_news)
                        print(f"  ✅ {site_config['name']}: {len(site_news)}件取得")
                    else:
                        print(f"  ⚠️ {site_config['name']}: ニュースなし")
                    
                    time.sleep(2)  # サイト間のレート制限
                    
                except Exception as e:
                    print(f"  ❌ {site_config['name']}エラー: {e}")
                    continue
            
            # 重複除去とフィルタリング
            unique_news = []
            seen_urls = set()
            for news in news_list:
                url = news.get('url', '')
                title = news.get('title', '')
                
                if (url and url not in seen_urls and 
                    self.is_social_insurance_relevant(title)):
                    seen_urls.add(url)
                    unique_news.append(news)
            
            print(f"✅ ニュースサイト総合 {len(unique_news)}件取得（重複除去・フィルタリング後）")
            return unique_news
            
        except Exception as e:
            print(f"❌ ニュースサイト総合エラー: {e}")
            return []
    
    def scrape_yahoo_enhanced(self, site_config):
        """強化版Yahoo!ニュース スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('news.yahoo.co.jp')
            
            for term in site_config['search_terms']:
                try:
                    search_url = f"{site_config['base_url']}/search?p={term}&ei=UTF-8"
                    response = self.session.get(search_url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 強化したセレクター
                    article_selectors = [
                        'article',
                        'div[class*="sc-"]',
                        'div[class*="newsFeed"]',
                        'li[class*="topics"]',
                        'div.contentMain'
                    ]
                    
                    articles = []
                    for selector in article_selectors:
                        found = soup.select(selector)
                        if found:
                            articles = found
                            break
                    
                    extracted = 0
                    for article in articles[:10]:  # 各検索語で10件
                        try:
                            # リンクとタイトルの抽出
                            link_selectors = ['a[href*="news"]', 'a[href]', 'h1 a', 'h2 a', 'h3 a']
                            link_elem = None
                            
                            for selector in link_selectors:
                                link_elem = article.select_one(selector)
                                if link_elem:
                                    break
                            
                            if not link_elem:
                                continue
                            
                            title = link_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            if not title or len(title) < 10:
                                continue
                            
                            # URL正規化
                            if url.startswith('/'):
                                url = site_config['base_url'] + url
                            elif not url.startswith('http'):
                                continue
                            
                            # 日付抽出試み
                            date_elem = article.select_one('time, .date, [class*="date"], [class*="time"]')
                            published_date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y年%m月%d日')
                            
                            # 詳細情報生成
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, url),
                                'title': title,
                                'url': url,
                                'source': site_config['name'],
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': published_date,
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence,
                                'search_term': term
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            print(f"    Yahoo記事解析エラー: {e}")
                            continue
                    
                    print(f"    検索語 '{term}': {extracted}件")
                    time.sleep(1)  # 検索間のレート制限
                    
                except Exception as e:
                    print(f"    Yahoo検索エラー {term}: {e}")
                    continue
            
            return news_list
            
        except Exception as e:
            print(f"Yahooニュースエラー: {e}")
            return []
    
    def scrape_nhk_news(self, site_config):
        """NHKニュース スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www3.nhk.or.jp')
            
            # NHKの社会ニュースセクション（修正版）
            nhk_urls = [
                'https://www3.nhk.or.jp/news/',  # トップページ
                'https://www3.nhk.or.jp/news/catnew.html'  # 新着ニュース
            ]
            
            for url in nhk_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # NHKのニュース項目抽出
                    articles = soup.select('.content-item, .module-list li, article')
                    
                    extracted = 0
                    for article in articles[:10]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            # URL正規化
                            if href.startswith('/'):
                                full_url = 'https://www3.nhk.or.jp' + href
                            else:
                                full_url = href
                            
                            # 日付抽出
                            date_elem = article.select_one('.date, time, [class*="time"]')
                            published_date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y年%m月%d日')
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': 'NHKニュース',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': published_date,
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            print(f"    NHK記事解析エラー: {e}")
                            continue
                    
                    print(f"    NHK {url.split('/')[-1]}: {extracted}件")
                    
                except Exception as e:
                    print(f"    NHK URLエラー {url}: {e}")
                    continue
            
            return news_list
            
        except Exception as e:
            print(f"NHKニュースエラー: {e}")
            return []
    
    def scrape_sankei_news(self, site_config):
        """産経ニュース スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www.sankei.com')
            
            # 産経ニュースの検索
            for term in site_config['search_terms']:
                try:
                    search_url = f"https://www.sankei.com/search/{term}/"
                    response = self.session.get(search_url, timeout=30)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 産経の記事一覧
                    articles = soup.select('.story-list li, .article-list li, article')
                    
                    extracted = 0
                    for article in articles[:5]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://www.sankei.com' + href
                            else:
                                full_url = href
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': '産経ニュース',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence,
                                'search_term': term
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    産経 '{term}': {extracted}件")
                    time.sleep(1)
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def scrape_asahi_news(self, site_config):
        """朝日新聞デジタル スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www.asahi.com')
            
            # 朝日新聞の検索
            for term in site_config['search_terms']:
                try:
                    search_url = f"https://www.asahi.com/search/news/?query={term}"
                    response = self.session.get(search_url, timeout=30)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 朝日新聞の記事一覧
                    articles = soup.select('.SearchResult li, article, .List li')
                    
                    extracted = 0
                    for article in articles[:5]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://www.asahi.com' + href
                            else:
                                full_url = href
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': '朝日新聞デジタル',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence,
                                'search_term': term
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    朝日 '{term}': {extracted}件")
                    time.sleep(1)
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def scrape_yahoo_simple(self, site_config):
        """Yahoo!ニュース シンプルスクレイパー（RSS/トピック利用）"""
        news_list = []
        
        try:
            self.check_rate_limit('news.yahoo.co.jp')
            
            # Yahoo!のトピック一覧とRSS的なアプローチ
            yahoo_topics = [
                'https://news.yahoo.co.jp/topics/domestic',     # 国内ニュース
                'https://news.yahoo.co.jp/topics/business',     # 経済ニュース
                'https://news.yahoo.co.jp/topics/local'         # 地域ニュース
            ]
            
            for topic_url in yahoo_topics:
                try:
                    response = self.session.get(topic_url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # より広範囲にリンクを探す
                    links = soup.find_all('a', href=True)
                    
                    extracted = 0
                    for link in links:
                        try:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            # 最低限の条件チェック
                            if (not title or len(title) < 10 or 
                                not href or 'news' not in href):
                                continue
                            
                            # 関連性チェック（緩和版を使用）
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            # URL正規化
                            if href.startswith('/'):
                                full_url = 'https://news.yahoo.co.jp' + href
                            elif not href.startswith('http'):
                                continue
                            else:
                                full_url = href
                            
                            # ニュースアイテム作成
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': 'Yahoo!ニュース',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                            # 各トピックから最大5件
                            if extracted >= 5:
                                break
                                
                        except Exception as e:
                            continue
                    
                    print(f"    Yahoo {topic_url.split('/')[-1]}: {extracted}件")
                    time.sleep(2)  # レート制限
                    
                except Exception as e:
                    continue
            
            # 重複除去
            unique_news = []
            seen_titles = set()
            for news in news_list:
                if news['title'] not in seen_titles:
                    unique_news.append(news)
                    seen_titles.add(news['title'])
            
            return unique_news
            
        except Exception as e:
            print(f"Yahoo!ニュース簡易版エラー: {e}")
            return []

    def scrape_nikkei_news(self, site_config):
        """日経新聞 スクレイパー（無効化）"""
        # 日経新聞は有料会員制のため無効化
        return []
    
    def scrape_jiji_news(self, site_config):
        """時事通信 スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www.jiji.com')
            
            # 時事通信の社会セクション
            jiji_urls = [
                'https://www.jiji.com/jc/list?g=soc',  # 社会
                'https://www.jiji.com/jc/list?g=pol'   # 政治（制度関連）
            ]
            
            for url in jiji_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 時事通信の記事一覧
                    articles = soup.select('.ListNewsItem, .newslist li, article')
                    
                    extracted = 0
                    for article in articles[:15]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://www.jiji.com' + href
                            else:
                                full_url = href
                            
                            # 日付抽出
                            date_elem = article.select_one('.date, time, [class*="time"]')
                            published_date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y年%m月%d日')
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': '時事通信',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': published_date,
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    時事通信 {url.split('=')[-1]}: {extracted}件")
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def scrape_kyodo_news(self, site_config):
        """共同通信 スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www.kyodo.co.jp')
            
            # 共同通信のトップページから
            kyodo_urls = [
                'https://www.kyodo.co.jp/',
                'https://www.kyodo.co.jp/politics/',
                'https://www.kyodo.co.jp/life/'
            ]
            
            for url in kyodo_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 共同通信の記事一覧
                    articles = soup.select('.article-list li, .news-list li, article, .card')
                    
                    extracted = 0
                    for article in articles[:10]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://www.kyodo.co.jp' + href
                            elif not href.startswith('http'):
                                continue
                            else:
                                full_url = href
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': '共同通信',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    共同通信 {url.split('/')[-2] if len(url.split('/')) > 3 else 'main'}: {extracted}件")
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def scrape_itmedia_news(self, site_config):
        """ITmedia ビジネス スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('www.itmedia.co.jp')
            
            # ITmediaビジネスのトピック
            itmedia_urls = [
                'https://www.itmedia.co.jp/business/',
                'https://www.itmedia.co.jp/business/subtop/work/'
            ]
            
            for url in itmedia_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # ITmediaの記事一覧
                    articles = soup.select('.colBoxLeft li, .topicsList li, article')
                    
                    extracted = 0
                    for article in articles[:10]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://www.itmedia.co.jp' + href
                            elif not href.startswith('http'):
                                continue
                            else:
                                full_url = href
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': 'ITmedia ビジネス',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    ITmedia {url.split('/')[-2] if '/' in url else 'main'}: {extracted}件")
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def scrape_president_news(self, site_config):
        """プレジデントオンライン スクレイパー"""
        news_list = []
        
        try:
            self.check_rate_limit('president.jp')
            
            # プレジデントオンラインのカテゴリ
            president_urls = [
                'https://president.jp/list/category/business',
                'https://president.jp/list/category/money'
            ]
            
            for url in president_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # プレジデントの記事一覧
                    articles = soup.select('.article-list li, .list-item, article')
                    
                    extracted = 0
                    for article in articles[:10]:
                        try:
                            link = article.select_one('a[href]')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            
                            if not self.is_social_insurance_relevant(title):
                                continue
                            
                            if href.startswith('/'):
                                full_url = 'https://president.jp' + href
                            elif not href.startswith('http'):
                                continue
                            else:
                                full_url = href
                            
                            category, related_categories, confidence = self.enhanced_categorization(title, '')
                            importance = self.enhanced_importance(title, '')
                            keywords = self.enhanced_keywords(title, '')
                            
                            news_item = {
                                'id': self.generate_id(title, full_url),
                                'title': title,
                                'url': full_url,
                                'source': 'プレジデントオンライン',
                                'category': category,
                                'importance': importance,
                                'summary': self.create_summary(title, category, keywords),
                                'keywords': keywords,
                                'published_date': datetime.now().strftime('%Y年%m月%d日'),
                                'scraped_at': datetime.now().isoformat(),
                                'related_categories': related_categories,
                                'confidence_score': confidence
                            }
                            
                            news_list.append(news_item)
                            extracted += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"    プレジデント {url.split('/')[-1]}: {extracted}件")
                    
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            return []
    
    def categorize_news(self, title):
        """レガシーカテゴリ分類（後方互換）"""
        category, _, _ = self.enhanced_categorization(title, '')
        return category
    
    def assess_importance(self, title):
        """レガシー重要度判定（後方互換）"""
        return self.enhanced_importance(title, '')
    
    def extract_keywords(self, text):
        """レガシーキーワード抽出（後方互換）"""
        return self.enhanced_keywords(text, '')
    
    def generate_daily_report(self, news_data):
        """日次レポート生成"""
        try:
            total_news = len(news_data)
            high_importance = len([n for n in news_data if n.get('importance') == '高'])
            
            # カテゴリ別集計
            categories = {}
            for news in news_data:
                cat = news.get('category', 'その他')
                categories[cat] = categories.get(cat, 0) + 1
            
            # 頻出キーワード
            all_keywords = []
            for news in news_data:
                all_keywords.extend(news.get('keywords', []))
            
            keyword_count = {}
            for keyword in all_keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_news': total_news,
                    'high_importance': high_importance,
                    'categories': list(categories.keys()),
                    'top_keywords': [k[0] for k in top_keywords]
                },
                'categories': categories,
                'keywords': dict(top_keywords)
            }
            
            # レポート保存
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📊 日次レポート生成完了: {total_news}件")
            return report
            
        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            return None
    
    def save_processed_data(self, news_data):
        """処理済みデータ保存"""
        try:
            # 重複除去
            unique_news = []
            seen_urls = set()
            
            for news in news_data:
                url = news.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_news.append(news)
            
            # 重要度順・新しい順でソート
            importance_order = {'高': 3, '中': 2, '低': 1}
            unique_news.sort(
                key=lambda x: (
                    importance_order.get(x.get('importance', '低'), 1),
                    x.get('scraped_at', '')
                ),
                reverse=True
            )
            
            # データ構造
            processed_data = {
                'last_updated': datetime.now().isoformat(),
                'total_count': len(unique_news),
                'news': unique_news,
                'categories': {}
            }
            
            # カテゴリ別分類
            for news in unique_news:
                category = news.get('category', 'その他')
                if category not in processed_data['categories']:
                    processed_data['categories'][category] = []
                processed_data['categories'][category].append(news)
            
            # ファイル保存
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 処理済みデータ保存完了: {len(unique_news)}件")
            return True
            
        except Exception as e:
            print(f"❌ データ保存エラー: {e}")
            return False
    
    def run_automation(self):
        """自動化実行"""
        try:
            print("🚀 Render版社会保険ニュース自動化開始")
            print(f"⏰ 開始時刻: {self.start_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            print("-" * 60)
            
            # Step 1: ニュース収集
            all_news = []
            
            # 厚労省・年金機構総合ニュース
            mhlw_news = self.scrape_mhlw_comprehensive()
            all_news.extend(mhlw_news)
            
            # ニュースサイト総合スクレイピング
            news_sites_data = self.scrape_news_sites_comprehensive()
            all_news.extend(news_sites_data)
            
            if not all_news:
                print("❌ ニュース収集失敗 - フォールバックデータを作成")
                # フォールバック用サンプルデータ
                all_news = [{
                    'title': '社会保険制度の最新情報について',
                    'url': 'https://www.mhlw.go.jp',
                    'source': '厚生労働省',
                    'category': '社会保険全般',
                    'importance': '中',
                    'summary': '現在最新のニュースデータを収集中です。社会保険制度に関する重要な変更については厚生労働省の公式サイトをご確認ください。',
                    'keywords': ['社会保険', '制度変更', '厚生労働省'],
                    'published_date': datetime.now().strftime('%Y年%m月%d日'),
                    'scraped_at': datetime.now().isoformat()
                }, {
                    'title': '年金制度改正の動向',
                    'url': 'https://www.nenkin.go.jp',
                    'source': '日本年金機構',
                    'category': '厚生年金',
                    'importance': '高',
                    'summary': '年金制度の改正動向について継続的に情報収集を行っています。最新情報は日本年金機構の公式発表をご確認ください。',
                    'keywords': ['年金', '制度改正', '日本年金機構'],
                    'published_date': datetime.now().strftime('%Y年%m月%d日'),
                    'scraped_at': datetime.now().isoformat()
                }]
            
            print(f"📡 総収集件数: {len(all_news)}件")
            
            # 関連性の低いニュースを除外
            relevant_news = []
            for news in all_news:
                if self.is_social_insurance_relevant(news['title']):
                    relevant_news.append(news)
                else:
                    print(f"  🚫 関連性低く除外: {news['title'][:40]}...")
            
            all_news = relevant_news
            print(f"📋 関連ニュース: {len(all_news)}件（フィルタリング後）")
            
            # Step 2: データ処理・保存
            if not self.save_processed_data(all_news):
                print("❌ データ保存失敗")
                return False
            
            # Step 3: レポート生成
            self.generate_daily_report(all_news)
            
            # 実行時間計算
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            print("-" * 60)
            print("🎉 自動化完了!")
            print(f"⏱️  実行時間: {duration.total_seconds():.1f}秒")
            print(f"📊 処理件数: {len(all_news)}件")
            print(f"🕐 完了時刻: {end_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 自動化エラー: {e}")
            print("詳細エラー:")
            traceback.print_exc()
            return False

def main():
    """メイン実行"""
    try:
        print("\n🤖 自動化処理開始...")
        automation = RenderNewsAutomation()
        success = automation.run_automation()
        
        if success:
            print("\n✅ 社会保険ニュース自動化成功!")
            print(f"処理終了時刻: {datetime.now()}")
            sys.exit(0)
        else:
            print("\n❌ 社会保険ニュース自動化失敗!")
            print(f"処理終了時刻: {datetime.now()}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 メイン処理で予期しないエラー: {e}")
        print("エラー詳細:")
        traceback.print_exc()
        print(f"処理終了時刻: {datetime.now()}")
        sys.exit(1)

if __name__ == "__main__":
    main()