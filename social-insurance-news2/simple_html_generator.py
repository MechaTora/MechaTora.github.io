#!/usr/bin/env python3
"""
簡単HTMLジェネレータ（最新データ用）
"""

import json
from datetime import datetime

def generate_html():
    # データ読み込み
    with open('processed_news.json', 'r') as f:
        data = json.load(f)
    
    total_news = data['total_count']
    categories = data['categories']
    news_list = data['news']
    
    # 重要度・統計計算
    high_importance = len([n for n in news_list if n.get('importance') == '高'])
    category_count = len(categories)
    today_updates = len([n for n in news_list if '2025年07月25日' in str(n.get('published_date', ''))])
    
    # HTMLテンプレート
    html_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>社会保険ニュース - 最新情報まとめ</title>
    <meta name="description" content="社会保険に関する最新ニュースを自動収集・要約してお届けします。健康保険、厚生年金、雇用保険などの重要な変更情報をわかりやすく整理。">
    
    <!-- AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1184134440246706"
            crossorigin="anonymous"></script>
    
    <style>
:root {
    --primary-color: #4A90E2;
    --accent-color: #FF8C42;
    --background: #F7F9FC;
    --surface: #FFFFFF;
    --text-primary: #2C3E50;
    --text-secondary: #7B8794;
    --border-color: #E1E8ED;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --radius-lg: 12px;
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}

body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--background);
    color: var(--text-primary);
    line-height: 1.5;
    font-size: 14px;
    margin: 0;
    padding: 0;
}

.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, #2E5A87 100%);
    color: white;
    padding: var(--spacing-xl) 0;
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 8px;
}

.last-updated {
    background: rgba(255, 255, 255, 0.15);
    padding: 8px 16px;
    border-radius: var(--radius-lg);
    display: inline-block;
    margin-top: 8px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-xl) var(--spacing-lg);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.stat-card {
    background: var(--surface);
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    text-align: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 8px;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    text-transform: uppercase;
}

.news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
    gap: var(--spacing-lg);
}

.news-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    transition: transform 0.3s ease;
}

.news-card:hover {
    transform: translateY(-2px);
}

.news-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
}

.news-meta {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    flex-wrap: wrap;
}

.category-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

.category-健康保険 { background: #E6F7FF; color: #1890FF; }
.category-厚生年金 { background: #F6FFED; color: #52C41A; }
.category-雇用保険 { background: #FFF7E6; color: #FA8C16; }
.category-労災保険 { background: #FFF1F0; color: #FF4D4F; }
.category-介護保険 { background: #F9F0FF; color: #722ED1; }
.category-社会保険全般 { background: #F0F0F0; color: #595959; }
.category-その他 { background: #F0F0F0; color: #8C8C8C; }

.importance-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

.importance-高 { background: #FFE7E7; color: #FF4D4F; }
.importance-中 { background: #FFF7E6; color: #FA8C16; }
.importance-低 { background: #F6FFED; color: #52C41A; }

.source-tag {
    background: var(--background);
    color: var(--text-secondary);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
}

.news-title {
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.3;
    margin: 0;
}

.news-title a {
    color: var(--text-primary);
    text-decoration: none;
}

.news-title a:hover {
    color: var(--primary-color);
}

.news-body {
    padding: var(--spacing-md);
}

.news-summary {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-md);
}

.news-keywords {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: var(--spacing-md);
}

.keyword-tag {
    background: var(--background);
    color: var(--text-secondary);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    border: 1px solid var(--border-color);
}

.news-footer {
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--background);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--border-color);
}

.read-more-btn {
    background: var(--primary-color);
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: background 0.2s ease;
}

.read-more-btn:hover {
    background: #2E5A87;
}

.published-date {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

@media (max-width: 1024px) {
    .news-grid {
        grid-template-columns: 1fr;
    }
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
    }
    .container {
        padding: var(--spacing-lg);
    }
    .stats-grid {
        grid-template-columns: 1fr;
    }
    .news-meta {
        flex-direction: column;
        align-items: flex-start;
    }
    .news-footer {
        flex-direction: column;
        gap: var(--spacing-md);
        align-items: flex-start;
    }
}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1>🏛️ 社会保険ニュース <span style="font-size: 0.6em; color: rgba(255,255,255,0.8); font-weight: 400;">毎朝4時に更新</span></h1>
            <p>厚生労働省・年金機構・ニュースサイトからの最新情報を自動収集・要約</p>
            <div class="last-updated">
                最終更新: {current_time}
            </div>
        </div>
    </header>

    <!-- AdSense Header -->
    <div style="text-align: center; margin: 16px 0;">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-1184134440246706"
             data-ad-slot="5863584162"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
    </div>

    <!-- Main Content -->
    <main class="container">
        <!-- Statistics -->
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_news}</div>
                <div class="stat-label">総ニュース数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{high_importance}</div>
                <div class="stat-label">重要ニュース</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{category_count}</div>
                <div class="stat-label">カテゴリ数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{today_updates}</div>
                <div class="stat-label">本日更新</div>
            </div>
        </section>

        <!-- News Grid -->
        <section class="news-grid">
            {news_cards}
        </section>

        <!-- AdSense Middle -->
        <div style="text-align: center; margin: 32px 0;">
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-1184134440246706"
                 data-ad-slot="8547296385"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
        </div>
    </main>

    <!-- Footer -->
    <footer style="background: var(--surface); border-top: 1px solid var(--border-color); margin-top: 32px; padding: 32px; text-align: center; color: var(--text-secondary);">
        <p>&copy; 2025 社会保険ニュース. データソース: 厚生労働省・日本年金機構・Yahoo!ニュース</p>
        <p style="margin-top: 8px; font-size: 0.9rem;">
            このサイトは公的機関・ニュースサイトの発表情報を自動収集・要約したものです。詳細は元記事をご確認ください。
        </p>
    </footer>

    <!-- AdSense 初期化 -->
    <script>
        (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</body>
</html>'''
    
    # ニュースカード生成（Yahoo!ニュースを優先表示）
    yahoo_news = [n for n in news_list if n.get('source') == 'Yahoo!ニュース'][:15]
    gov_news = [n for n in news_list if n.get('source') in ['厚生労働省', '日本年金機構']][:5]
    
    # Yahoo!ニュースを上、政府ニュースを下に配置
    ordered_news = yahoo_news + gov_news
    
    news_cards = ""
    for news in ordered_news:
        category = news.get('category', 'その他')
        importance = news.get('importance', '低')
        
        # キーワードタグ生成
        keywords_html = ""
        for keyword in news.get('keywords', [])[:5]:
            keywords_html += f'<span class="keyword-tag">{keyword}</span>'
        
        news_card = f'''
            <article class="news-card">
                <header class="news-header">
                    <div class="news-meta">
                        <span class="category-badge category-{category}">
                            {get_category_icon(category)} {category}
                        </span>
                        <span class="importance-badge importance-{importance}">
                            {get_importance_icon(importance)} {importance}
                        </span>
                        <span class="source-tag">{news.get('source', '')}</span>
                    </div>
                    <h2 class="news-title">
                        <a href="{news.get('url', '#')}" target="_blank" rel="noopener">
                            {news.get('title', '')[:80]}...
                        </a>
                    </h2>
                </header>
                
                <div class="news-body">
                    <p class="news-summary">{news.get('summary', '')[:100]}...</p>
                    
                    <div class="news-keywords">
                        {keywords_html}
                    </div>
                </div>
                
                <footer class="news-footer">
                    <span class="published-date">{news.get('published_date', '日付不明')}</span>
                    <a href="{news.get('url', '#')}" target="_blank" rel="noopener" class="read-more-btn">
                        元記事を読む
                    </a>
                </footer>
            </article>
        '''
        news_cards += news_card
    
    # HTML生成
    current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    html_content = html_template.replace('{current_time}', current_time)\
                                      .replace('{total_news}', str(total_news))\
                                      .replace('{high_importance}', str(high_importance))\
                                      .replace('{category_count}', str(category_count))\
                                      .replace('{today_updates}', str(today_updates))\
                                      .replace('{news_cards}', news_cards)
    
    # ファイル保存
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 最新HTMLサイト生成完了")
    print(f"📊 総ニュース数: {total_news}件")
    print(f"🔥 重要ニュース: {high_importance}件")
    print(f"📂 カテゴリ数: {category_count}")
    print(f"📅 更新時刻: {current_time}")

def get_category_icon(category):
    icons = {
        '健康保険': '🏥',
        '厚生年金': '💰',
        '雇用保険': '👔',
        '労災保険': '⚠️',
        '介護保険': '🏠',
        '社会保険全般': '📋',
        'その他': '📄'
    }
    return icons.get(category, '📄')

def get_importance_icon(importance):
    icons = {
        '高': '🚨',
        '中': '⚠️',
        '低': 'ℹ️'
    }
    return icons.get(importance, 'ℹ️')

if __name__ == "__main__":
    generate_html()