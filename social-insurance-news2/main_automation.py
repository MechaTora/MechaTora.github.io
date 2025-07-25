#!/usr/bin/env python3
"""
社会保険ニュース自動化メインスクリプト（修正版）
完全自動化パイプライン - スクレイピング→AI要約→HTML生成
"""

import sys
import traceback
import json
from datetime import datetime
from integrated_processor import IntegratedNewsProcessor

class SocialInsuranceNewsAutomation:
    """社会保険ニュース完全自動化システム"""
    
    def __init__(self):
        self.processor = IntegratedNewsProcessor()
        self.start_time = datetime.now()
    
    def run_complete_automation(self):
        """完全自動化実行"""
        try:
            print("🌅 制御付きニュース収集開始")
            print(f"⏰ 開始時刻: {self.start_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            print("-" * 60)
            
            # Step 1: ニュース収集・AI要約処理
            print("📡 Step 1: ニュース収集・AI要約処理")
            processed_news = self.processor.run_full_pipeline()
            
            if not processed_news:
                print("❌ ニュース収集に失敗しました")
                return False
            
            print(f"✅ {len(processed_news)}件のニュースを処理完了")
            print("-" * 40)
            
            # Step 2: 日次レポート生成
            print("📊 Step 2: 日次レポート生成")
            report = self.processor.generate_daily_report()
            
            if report:
                print(f"📈 重要ニュース: {report['summary']['high_importance']}件")
                print(f"📋 カテゴリ: {', '.join(report['summary']['categories'])}")
                print(f"🔤 頻出キーワード: {', '.join(report['summary']['top_keywords'][:5])}")
            
            print("-" * 40)
            
            # Step 3: HTMLサイト生成
            print("🎨 Step 3: スタイリッシュWebサイト生成")
            self.generate_website()
            
            # 実行時間計算
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            print("-" * 60)
            print(f"🎉 完全自動化処理完了!")
            print(f"⏱️  実行時間: {duration.total_seconds():.1f}秒")
            print(f"📊 処理件数: {len(processed_news)}件")
            print(f"🕐 完了時刻: {end_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 自動化処理エラー: {e}")
            print("📋 詳細エラー情報:")
            traceback.print_exc()
            return False
    
    def generate_website(self):
        """Webサイト生成（simple_html_generatorを使用）"""
        try:
            # simple_html_generatorを直接実行
            from simple_html_generator import generate_html
            generate_html()
            print("✅ Webサイト生成完了")
            
        except Exception as e:
            print(f"❌ Webサイト生成エラー: {e}")
            # フォールバック: 基本的なHTMLを生成
            self.generate_basic_html()
    
    def generate_basic_html(self):
        """基本的なHTML生成（フォールバック）"""
        try:
            # processed_news.jsonから基本HTMLを生成
            with open('processed_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
            total_news = data.get('total_count', 0)
            
            basic_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>社会保険ニュース - 最新情報まとめ</title>
</head>
<body>
    <h1>🏛️ 社会保険ニュース</h1>
    <p>最終更新: {current_time}</p>
    <p>総ニュース数: {total_news}件</p>
    <p>システムが正常に動作しました。</p>
</body>
</html>'''
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(basic_html)
            
            print("✅ 基本HTML生成完了（フォールバック）")
            
        except Exception as e:
            print(f"❌ 基本HTML生成もエラー: {e}")

def main():
    """メイン実行関数"""
    automation = SocialInsuranceNewsAutomation()
    success = automation.run_complete_automation()
    
    if success:
        print("\n🎊 社会保険ニュース自動化成功!")
        sys.exit(0)
    else:
        print("\n💥 社会保険ニュース自動化失敗!")
        sys.exit(1)

if __name__ == "__main__":
    main()