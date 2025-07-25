#!/usr/bin/env python3
"""
社会保険ニュース自動化メインスクリプト
完全自動化パイプライン - スクレイピング→AI要約→HTML生成
"""

import sys
import traceback
from datetime import datetime
from integrated_processor import IntegratedNewsProcessor
from enhanced_generator import WebsiteManager

class SocialInsuranceNewsAutomation:
    """社会保険ニュース完全自動化システム"""
    
    def __init__(self):
        self.processor = IntegratedNewsProcessor()
        self.website_manager = WebsiteManager()
        self.start_time = datetime.now()
    
    def run_complete_automation(self):
        """完全自動化実行"""
        print("🤖 社会保険ニュース完全自動化開始")
        print(f"⏰ 開始時刻: {self.start_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
        print("-" * 60)
        
        try:
            # Step 1: ニュース収集・AI処理
            print("📡 Step 1: ニュース収集・AI要約処理")
            processed_news = self.processor.run_full_pipeline()
            
            if not processed_news:
                print("❌ ニュース処理に失敗しました")
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
            
            # Step 3: スタイリッシュWebサイト生成
            print("🎨 Step 3: スタイリッシュWebサイト生成")
            build_result = self.website_manager.build_complete_site('processed_news.json')
            
            if build_result.get('status') == 'success':
                print(f"🌐 {build_result['files_generated']}ファイル生成完了")
                print(f"📄 総ニュース数: {build_result['total_news']}")
                print(f"📂 カテゴリ数: {build_result['categories']}")
            else:
                print(f"❌ Webサイト生成エラー: {build_result.get('error', 'Unknown error')}")
                return False
            
            print("-" * 40)
            
            # Step 4: 実行サマリー
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            print("🎉 完全自動化処理完了")
            print(f"⏱️  処理時間: {duration.total_seconds():.1f}秒")
            print(f"📅 完了時刻: {end_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
            
            # 成功ログ保存
            self.save_execution_log(True, processed_news, build_result, duration)
            return True
            
        except Exception as e:
            print(f"❌ 予期しないエラーが発生: {e}")
            print("📋 エラー詳細:")
            traceback.print_exc()
            
            # エラーログ保存
            self.save_execution_log(False, [], {}, None, str(e))
            return False
    
    def save_execution_log(self, success: bool, processed_news: list, 
                          build_result: dict, duration, error: str = None):
        """実行ログ保存"""
        import json
        
        log_data = {
            "timestamp": self.start_time.isoformat(),
            "success": success,
            "duration_seconds": duration.total_seconds() if duration else 0,
            "processed_news_count": len(processed_news),
            "build_result": build_result,
            "error": error
        }
        
        log_filename = f"execution_log_{self.start_time.strftime('%Y%m%d_%H%M')}.json"
        
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            print(f"📝 実行ログ保存: {log_filename}")
        except Exception as e:
            print(f"⚠️ ログ保存エラー: {e}")

def main():
    """メイン実行関数"""
    automation = SocialInsuranceNewsAutomation()
    
    # 完全自動化実行
    success = automation.run_complete_automation()
    
    # 終了コード設定（GitHub Actionsでのエラー検知用）
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()