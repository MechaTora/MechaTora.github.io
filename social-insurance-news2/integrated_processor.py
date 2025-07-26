#!/usr/bin/env python3
"""
統合ニュース処理システム
スクレイピング → AI要約 → データ構造化 → HTML生成
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
from dataclasses import dataclass, asdict
from advanced_scraper import SocialInsuranceNewsCollector
from scraper_controller import ControlledScraper
from free_ai_summary import FreeNewsSummarizer
from news_site_scraper import SocialInsuranceNewsAggregator

@dataclass
class ProcessedNews:
    """処理済みニュース構造"""
    id: str
    title: str
    url: str
    source: str
    category: str
    summary: str
    importance: str
    published_date: str
    scraped_at: str
    keywords: List[str]
    related_categories: List[str]
    content_length: int
    confidence_score: float

class EnhancedSummarizer(FreeNewsSummarizer):
    """強化版AI要約システム"""
    
    def __init__(self):
        super().__init__()
        
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
            "高": ["法改正", "制度改正", "新設", "廃止", "施行", "公布", "省令", "告示"],
            "中": ["改定", "変更", "見直し", "拡大", "縮小", "料率変更", "基準変更"],
            "低": ["手続き", "様式", "お知らせ", "案内", "説明会", "パンフレット"]
        }
    
    def enhanced_categorization(self, title: str, content: str) -> Tuple[str, List[str], float]:
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
        
        # 関連カテゴリ（スコア0.3以上）
        for cat, data in category_scores.items():
            if cat != primary_category and data["score"] >= 1.0:
                related_categories.append(cat)
        
        return primary_category, related_categories, confidence
    
    def determine_importance(self, title: str, content: str) -> str:
        """重要度判定"""
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
    
    def extract_enhanced_keywords(self, title: str, content: str) -> List[str]:
        """強化キーワード抽出"""
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
            r'\d+\.?\d*%',  # パーセント
            r'\d+円',       # 金額
            r'\d+万円',     # 万円単位
            r'\d+年\d+月',  # 年月
        ]
        
        for pattern in numeric_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches[:3])  # 最大3個まで
        
        return list(set(keywords))[:10]  # 重複除去・上位10個
    
    def generate_enhanced_summary(self, news_data: Dict) -> ProcessedNews:
        """強化版要約生成"""
        title = news_data.get('title', '')
        content = news_data.get('content', '')
        
        # カテゴリ分類
        category, related_categories, confidence = self.enhanced_categorization(title, content)
        
        # 重要度判定  
        importance = self.determine_importance(title, content)
        
        # キーワード抽出
        keywords = self.extract_enhanced_keywords(title, content)
        
        # 要約文生成（より詳細に）
        summary = self.create_detailed_summary(title, content, category, keywords)
        
        return ProcessedNews(
            id=news_data.get('id', ''),
            title=title,
            url=news_data.get('url', ''),
            source=news_data.get('source', ''),
            category=category,
            summary=summary,
            importance=importance,
            published_date=news_data.get('published_date', ''),
            scraped_at=news_data.get('scraped_at', ''),
            keywords=keywords,
            related_categories=related_categories,
            content_length=len(content),
            confidence_score=confidence
        )
    
    def create_detailed_summary(self, title: str, content: str, category: str, keywords: List[str]) -> str:
        """詳細要約文作成"""
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
        
        # 実施時期抽出
        date_match = re.search(r'(\d{4}年\d{1,2}月|\d{1,2}月\d{1,2}日|令和\d+年)', content)
        if date_match:
            summary_parts.append(f"[{date_match.group(1)}]")
        
        summary = " ".join(summary_parts)
        return summary[:120]  # 120文字制限

class IntegratedNewsProcessor:
    """統合ニュース処理システム"""
    
    def __init__(self):
        self.collector = SocialInsuranceNewsCollector()
        self.controller = ControlledScraper() 
        self.news_aggregator = SocialInsuranceNewsAggregator()
        self.summarizer = EnhancedSummarizer()
        self.processed_news = []
    
    def run_full_pipeline(self) -> List[ProcessedNews]:
        """フルパイプライン実行（政府サイト + ニュースサイト統合）"""
        print("🚀 統合ニュース処理パイプライン開始")
        
        # 1. 政府サイトスクレイピング実行
        print("🏛️ 政府サイトからニュース収集中...")
        gov_news = self.controller.run_controlled_collection(self.collector)
        
        # 2. ニュースサイトスクレイピング実行
        print("📰 ニュースサイトから社会保険情報収集中...")
        news_sites_data = []
        try:
            news_sites_data = self.news_aggregator.collect_all_news()
        except Exception as e:
            print(f"❌ ニュースサイト収集エラー: {e}")
        
        # 3. データ統合
        all_raw_news = (gov_news or []) + (news_sites_data or [])
        
        if not all_raw_news:
            print("❌ 全てのニュース収集に失敗")
            return []
        
        print(f"✅ 合計{len(all_raw_news)}件のニュースを収集（政府:{len(gov_news or [])}件、ニュース:{len(news_sites_data or [])}件）")
        
        # 4. AI要約・分類処理
        print("🤖 AI要約処理中...")
        processed_news = []
        
        for news in all_raw_news:
            try:
                processed = self.summarizer.generate_enhanced_summary(news)
                processed_news.append(processed)
                print(f"  ✅ 処理完了: {processed.title[:40]}...")
                
            except Exception as e:
                print(f"  ❌ 処理エラー: {e}")
                continue
        
        print(f"🎉 {len(processed_news)}件の要約生成完了")
        
        # 5. データ保存
        self.save_processed_data(processed_news)
        
        self.processed_news = processed_news
        return processed_news
    
    def save_processed_data(self, processed_news: List[ProcessedNews]):
        """処理済みデータ保存"""
        # 構造化データ
        structured_data = {
            "last_updated": datetime.now().isoformat(),
            "total_count": len(processed_news),
            "categories": self.group_by_category(processed_news),
            "importance_distribution": self.get_importance_stats(processed_news),
            "news": [asdict(news) for news in processed_news]
        }
        
        # メインデータファイル
        with open('processed_news.json', 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        
        # カテゴリ別ファイル
        for category, news_list in structured_data["categories"].items():
            filename = f'category_{category.replace("/", "_")}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "category": category,
                    "count": len(news_list),
                    "news": news_list
                }, f, ensure_ascii=False, indent=2)
        
        print("💾 処理済みデータ保存完了")
    
    def group_by_category(self, news_list: List[ProcessedNews]) -> Dict:
        """カテゴリ別グループ化"""
        categories = {}
        for news in news_list:
            category = news.category
            if category not in categories:
                categories[category] = []
            categories[category].append(asdict(news))
        return categories
    
    def get_importance_stats(self, news_list: List[ProcessedNews]) -> Dict:
        """重要度統計"""
        importance_count = {"高": 0, "中": 0, "低": 0}
        for news in news_list:
            importance_count[news.importance] += 1
        return importance_count
    
    def generate_daily_report(self) -> Dict:
        """日次レポート生成"""
        if not self.processed_news:
            return {}
        
        report = {
            "date": datetime.now().strftime('%Y年%m月%d日'),
            "summary": {
                "total_news": len(self.processed_news),
                "high_importance": len([n for n in self.processed_news if n.importance == "高"]),
                "categories": list(set(n.category for n in self.processed_news)),
                "top_keywords": self.get_top_keywords()
            },
            "highlights": [
                asdict(news) for news in self.processed_news 
                if news.importance == "高"
            ][:5]
        }
        
        with open('daily_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def get_top_keywords(self) -> List[str]:
        """頻出キーワード抽出"""
        all_keywords = []
        for news in self.processed_news:
            all_keywords.extend(news.keywords)
        
        keyword_count = {}
        for keyword in all_keywords:
            keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        return sorted(keyword_count.keys(), key=keyword_count.get, reverse=True)[:10]

if __name__ == "__main__":
    # テスト実行
    processor = IntegratedNewsProcessor()
    results = processor.run_full_pipeline()
    
    if results:
        report = processor.generate_daily_report()
        print(f"\n📊 処理結果: {len(results)}件")
        print(f"📈 重要ニュース: {report['summary']['high_importance']}件")
        print(f"📋 カテゴリ: {', '.join(report['summary']['categories'])}")
    else:
        print("❌ 処理失敗")