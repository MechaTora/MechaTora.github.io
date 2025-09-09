#!/usr/bin/env python3
"""
Yahoo!ニュース スクレイピング デバッグ用スクリプト
関連性判定の動作を詳しく確認する
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

class YahooNewsDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 拡張された社会保険関連キーワード
        self.relevant_keywords = [
            # 基本的な社会保険制度
            '健康保険', '厚生年金', '国民年金', '雇用保険', '労災保険', '介護保険',
            '社会保険', '被保険者', '保険料', '年金', '医療保険', '失業給付',
            '労働災害', '介護給付', '保険適用', '制度改正', '法改正',
            
            # 組織・制度名
            '協会けんぽ', '年金機構', '社労士', '給付金', '適用拡大',
            '厚生労働省', 'ハローワーク', '年金事務所', '社会保険労務士',
            
            # 関連する社会問題・政策
            '医療費', '高齢者', '障害者', '育児', '出産', '療養費',
            '扶養', '賃金', '労働者', '事業主', '保険制度', '社会保障',
            '福祉', '医療制度', '退職', '就職', '職業訓練',
            '休業補償', '通勤災害', '業務災害', '要介護', '要支援',
            
            # より幅広い関連キーワード
            '働き方改革', '少子高齢化', 'マイナンバー', '電子申請',
            '定年延長', '非正規雇用', '正社員化', 'DX', 'デジタル化',
            '手続き簡素化', '窓口', '相談', '申請', '給付',
            '認定', '審査', '支給', '受給', '納付', '徴収'
        ]
    
    def is_social_insurance_relevant_loose(self, title):
        """緩和版 社会保険関連判定"""
        if len(title.strip()) < 5:
            return False
        
        # 除外キーワード（関係ないもの）
        exclude_keywords = [
            'JavaScript', 'Cookie', 'PDF', 'システム', 'メンテナンス',
            'ブラウザ', 'Internet Explorer', 'アクセシビリティ',
            'スポーツ', '芸能', 'エンタメ', '天気', '占い', 'ゲーム',
            '株価', '為替', '競馬', '宝くじ', 'パチンコ'
        ]
        
        # 除外キーワードチェック
        for exclude in exclude_keywords:
            if exclude in title:
                return False
        
        # 関連キーワードチェック（1つでも含まれていればOK）
        title_lower = title.lower()
        for keyword in self.relevant_keywords:
            if keyword in title:
                return True
        
        # 部分キーワードもチェック（より緩い条件）
        partial_keywords = [
            '保険', '年金', '給付', '制度', '労働', '医療', '福祉',
            '働く', '仕事', '雇用', '退職', '就職', '病気', '介護',
            '子育て', '出産', '育児', '障害', '高齢', '申請', '手続き'
        ]
        
        matched_partials = 0
        for keyword in partial_keywords:
            if keyword in title:
                matched_partials += 1
        
        # 1個以上の部分キーワードがあれば関連とする（より緩い設定）
        if matched_partials >= 1:
            return True
        
        return False
    
    def test_yahoo_search(self, search_terms):
        """Yahoo!ニュース検索テスト"""
        total_found = 0
        total_relevant = 0
        
        for term in search_terms:
            print(f"\n🔍 検索語: '{term}'")
            try:
                search_url = f"https://news.yahoo.co.jp/search?p={term}&ei=UTF-8"
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # より幅広いセレクターを試す
                selectors = [
                    'article',
                    'div[class*="sc-"]',
                    'div[class*="newsFeed"]',
                    'li[class*="topics"]',
                    'div.contentMain',
                    '.searchResult li',
                    '.newsList li',
                    '.topicsList li'
                ]
                
                articles = []
                for selector in selectors:
                    found = soup.select(selector)
                    if found:
                        print(f"  📄 セレクター '{selector}' で {len(found)}件発見")
                        articles = found
                        break
                
                if not articles:
                    # より広範囲にリンク要素を探す
                    all_links = soup.find_all('a', href=True)
                    print(f"  📄 全リンク要素: {len(all_links)}件")
                    articles = all_links[:50]  # 最初の50件をチェック
                
                found_count = 0
                relevant_count = 0
                
                print(f"  📋 解析対象: {len(articles)}件")
                
                for i, article in enumerate(articles[:20]):  # 最初の20件を詳細チェック
                    try:
                        # タイトル抽出（複数の方法を試行）
                        title = None
                        
                        if article.name == 'a':
                            title = article.get_text(strip=True)
                        else:
                            # 子要素からリンクを探す
                            link = article.find('a', href=True)
                            if link:
                                title = link.get_text(strip=True)
                        
                        if not title or len(title) < 10:
                            continue
                        
                        found_count += 1
                        
                        # 関連性判定（デバッグ出力付き）
                        is_relevant = self.is_social_insurance_relevant_loose(title)
                        
                        if is_relevant:
                            relevant_count += 1
                            print(f"    ✅ [関連] {title[:60]}...")
                        else:
                            print(f"    ❌ [無関係] {title[:60]}...")
                            
                    except Exception as e:
                        print(f"    ⚠️ 記事解析エラー: {e}")
                        continue
                
                print(f"  📊 結果: 発見 {found_count}件 / 関連 {relevant_count}件")
                total_found += found_count
                total_relevant += relevant_count
                
                time.sleep(2)  # レート制限
                
            except Exception as e:
                print(f"  ❌ 検索エラー: {e}")
                continue
        
        print(f"\n📈 総合結果:")
        print(f"   総発見数: {total_found}件")
        print(f"   関連記事: {total_relevant}件")
        print(f"   関連率: {(total_relevant/total_found*100):.1f}%" if total_found > 0 else "   関連率: N/A")
        
        return total_relevant

def main():
    """メイン実行"""
    debugger = YahooNewsDebugger()
    
    print("🔍 Yahoo!ニュース スクレイピング デバッグ開始")
    print("=" * 60)
    
    # 検索語リスト（現在使用しているもの）
    search_terms = [
        '社会保険', '厚生年金', '健康保険', '雇用保険', '年金改正',
        '介護保険', '労災保険', '年金制度', '医療保険制度', '保険料改正'
    ]
    
    relevant_count = debugger.test_yahoo_search(search_terms)
    
    print("\n💡 改善提案:")
    if relevant_count < 20:
        print("   - 検索語を追加（例：働き方改革、社会保障、給付金）")
        print("   - 関連性判定をより緩和")
        print("   - セレクターの拡充")
    else:
        print("   - 現在の設定で十分な件数を取得済み")
    
    print(f"\n⏰ 実行完了: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

if __name__ == "__main__":
    main()