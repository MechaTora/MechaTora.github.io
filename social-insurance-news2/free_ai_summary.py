#!/usr/bin/env python3
"""
完全無料 社会保険ニュース要約システム
ローカル処理 + 限定AI活用
"""

import re
import json
from datetime import datetime
from typing import Dict, List

class FreeNewsSummarizer:
    def __init__(self):
        self.keywords = {
            "健康保険": ["健康保険", "協会けんぽ", "保険料率", "医療保険"],
            "厚生年金": ["厚生年金", "年金", "保険料", "受給"],  
            "雇用保険": ["雇用保険", "失業給付", "育児休業", "介護休業"],
            "労災保険": ["労災", "労働災害", "補償", "給付"],
            "介護保険": ["介護保険", "要介護", "介護給付", "介護報酬"],
            "社会保険全般": ["社会保険", "適用拡大", "制度改正", "法改正"]
        }
        
        self.importance_keywords = [
            "法改正", "制度変更", "料率改定", "適用拡大", 
            "新設", "廃止", "施行", "公布"
        ]
    
    def categorize_news(self, title: str, text: str) -> str:
        """ニュースのカテゴリを判定"""
        content = title + text
        
        for category, words in self.keywords.items():
            if any(word in content for word in words):
                return category
        return "その他"
    
    def extract_key_info(self, title: str, text: str) -> Dict:
        """重要情報を抽出"""
        info = {
            "dates": [],
            "amounts": [],
            "changes": [],
            "importance": "低"
        }
        
        # 日付抽出
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})年(\d{1,2})月',
            r'令和(\d+)年(\d{1,2})月'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    info["dates"].append(f"{match[0]}年{match[1]}月{match[2]}日")
                else:
                    info["dates"].append(f"{match[0]}年{match[1]}月")
        
        # 金額・率抽出
        amount_patterns = [
            r'(\d+\.?\d*)%',
            r'(\d+)円',
            r'(\d+)万円'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            info["amounts"].extend(matches)
        
        # 変更内容抽出
        change_keywords = ["改正", "変更", "新設", "廃止", "拡大", "縮小"]
        for keyword in change_keywords:
            if keyword in text:
                info["changes"].append(keyword)
        
        # 重要度判定
        if any(keyword in title + text for keyword in self.importance_keywords):
            info["importance"] = "高"
        elif any(word in title + text for word in ["変更", "改定", "見直し"]):
            info["importance"] = "中"
        
        return info
    
    def generate_summary(self, title: str, text: str) -> Dict:
        """要約生成"""
        category = self.categorize_news(title, text)
        key_info = self.extract_key_info(title, text)
        
        # 要約文生成
        summary_parts = []
        
        # カテゴリ
        summary_parts.append(f"{category}:")
        
        # 主要な変更内容
        if key_info["changes"]:
            changes = "・".join(key_info["changes"][:2])
            summary_parts.append(f"{changes}")
        
        # 実施時期
        if key_info["dates"]:
            summary_parts.append(f"({key_info['dates'][0]})")
        
        # 金額・率情報
        if key_info["amounts"]:
            amounts = "、".join(key_info["amounts"][:2])
            summary_parts.append(f"[{amounts}]")
        
        summary = " ".join(summary_parts)
        
        return {
            "title": title,
            "category": category,
            "summary": summary[:100],  # 100文字制限
            "importance": key_info["importance"],
            "dates": key_info["dates"][:2],
            "original_text_length": len(text),
            "processed_at": datetime.now().isoformat()
        }
    
    def batch_process(self, news_list: List[Dict]) -> List[Dict]:
        """複数ニュースの一括処理"""
        results = []
        
        for news in news_list:
            try:
                summary = self.generate_summary(
                    news.get("title", ""), 
                    news.get("content", "")
                )
                summary.update({
                    "url": news.get("url", ""),
                    "source": news.get("source", ""),
                    "published_date": news.get("published_date", "")
                })
                results.append(summary)
            except Exception as e:
                print(f"Error processing news: {e}")
                continue
        
        return results

if __name__ == "__main__":
    # テスト実行
    summarizer = FreeNewsSummarizer()
    
    test_news = {
        "title": "2025年度協会けんぽ健康保険料率の改定について",
        "content": "令和7年3月分から協会けんぽの健康保険料率が改定されます。全国平均で10.31%となり、都道府県別に異なる料率が適用されます。事業主と被保険者で折半負担となります。"
    }
    
    result = summarizer.generate_summary(test_news["title"], test_news["content"])
    print(json.dumps(result, ensure_ascii=False, indent=2))