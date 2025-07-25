#!/usr/bin/env python3
"""
スクレイピング制御・監視システム
レート制限、エラー処理、ログ管理
"""

import time
import logging
from datetime import datetime, timedelta
import json
from typing import Dict, List
import traceback

class ScrapingController:
    """スクレイピング制御・監視"""
    
    def __init__(self, config_file: str = 'scraping_config.json'):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.error_count = {}
        self.request_times = {}
        
    def load_config(self, config_file: str) -> Dict:
        """設定ファイル読み込み"""
        default_config = {
            "rate_limits": {
                "mhlw.go.jp": 2.0,      # 2秒間隔
                "nenkin.go.jp": 2.0,    # 2秒間隔
                "kyoukaikenpo.or.jp": 3.0  # 3秒間隔
            },
            "retry_config": {
                "max_retries": 3,
                "retry_delay": 5,
                "backoff_factor": 2
            },
            "timeout_config": {
                "connect_timeout": 10,
                "read_timeout": 30
            },
            "error_thresholds": {
                "max_errors_per_site": 5,
                "max_total_errors": 15
            }
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            # デフォル設定で設定ファイル作成
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
                
        return default_config
    
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraping.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_rate_limit(self, domain: str) -> bool:
        """レート制限チェック"""
        now = datetime.now()
        
        if domain in self.request_times:
            last_request = self.request_times[domain]
            required_interval = self.config["rate_limits"].get(domain, 2.0)
            
            elapsed = (now - last_request).total_seconds()
            if elapsed < required_interval:
                wait_time = required_interval - elapsed
                self.logger.info(f"⏳ {domain} レート制限: {wait_time:.1f}秒待機")
                time.sleep(wait_time)
        
        self.request_times[domain] = now
        return True
    
    def handle_error(self, site: str, error: Exception, url: str = "") -> bool:
        """エラー処理"""
        if site not in self.error_count:
            self.error_count[site] = 0
        
        self.error_count[site] += 1
        
        error_msg = f"❌ {site} エラー({self.error_count[site]}): {error}"
        if url:
            error_msg += f" - URL: {url}"
            
        self.logger.error(error_msg)
        
        # エラー閾値チェック
        max_site_errors = self.config["error_thresholds"]["max_errors_per_site"] 
        max_total_errors = self.config["error_thresholds"]["max_total_errors"]
        
        total_errors = sum(self.error_count.values())
        
        if self.error_count[site] >= max_site_errors:
            self.logger.warning(f"⚠️ {site} エラー上限到達: スキップ")
            return False
            
        if total_errors >= max_total_errors:
            self.logger.error(f"🚨 総エラー数上限到達: 処理中断")
            return False
            
        return True
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """指数バックオフでリトライ"""
        max_retries = self.config["retry_config"]["max_retries"]
        base_delay = self.config["retry_config"]["retry_delay"]
        backoff_factor = self.config["retry_config"]["backoff_factor"]
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                delay = base_delay * (backoff_factor ** attempt)
                self.logger.info(f"🔄 リトライ {attempt + 1}/{max_retries} ({delay}秒後)")
                time.sleep(delay)
    
    def generate_report(self) -> Dict:
        """実行レポート生成"""
        total_errors = sum(self.error_count.values())
        
        report = {
            "execution_time": datetime.now().isoformat(),
            "error_summary": {
                "total_errors": total_errors,
                "errors_by_site": dict(self.error_count),
                "success_rate": max(0, 100 - (total_errors * 10))
            },
            "rate_limit_compliance": "OK",
            "recommendations": []
        }
        
        # 推奨事項生成
        if total_errors > 5:
            report["recommendations"].append("エラー率が高いです。サイト構造変更を確認してください")
        
        if any(count > 3 for count in self.error_count.values()):
            report["recommendations"].append("特定サイトでエラー多発。robots.txt・利用規約を再確認してください")
        
        return report
    
    def save_report(self, report: Dict, filename: str = 'scraping_report.json'):
        """レポート保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📋 実行レポート保存: {filename}")

# 使用例の統合クラス      
class ControlledScraper:
    """制御機能付きスクレイパー"""
    
    def __init__(self):
        self.controller = ScrapingController()
        
    def controlled_request(self, scraper_func, site_name: str, *args, **kwargs):
        """制御付きリクエスト実行"""
        # ドメイン抽出
        if hasattr(scraper_func, '__self__'):
            domain = scraper_func.__self__.base_url.replace('https://', '').replace('http://', '')
        else:
            domain = site_name
        
        # レート制限チェック
        self.controller.check_rate_limit(domain)
        
        try:
            # リトライ付き実行
            result = self.controller.retry_with_backoff(scraper_func, *args, **kwargs)
            return result
            
        except Exception as e:
            # エラー処理
            continue_scraping = self.controller.handle_error(site_name, e)
            if not continue_scraping:
                raise Exception(f"サイト {site_name} でエラー上限到達")
            return None
    
    def run_controlled_collection(self, collector):
        """制御付きニュース収集実行"""
        try:
            self.controller.logger.info("🌅 制御付きニュース収集開始")
            
            # 各スクレイパーを制御付きで実行
            all_news = []
            for scraper in collector.scrapers:
                try:
                    news_list = self.controlled_request(
                        scraper.scrape_news, 
                        scraper.name
                    )
                    if news_list:
                        all_news.extend(news_list)
                        
                except Exception as e:
                    self.controller.logger.error(f"❌ {scraper.name} 完全失敗: {e}")
                    continue
            
            # レポート生成・保存
            report = self.controller.generate_report()
            self.controller.save_report(report)
            
            self.controller.logger.info(f"✅ 制御付き収集完了: {len(all_news)}件")
            return all_news
            
        except Exception as e:
            self.controller.logger.error(f"🚨 収集プロセス完全失敗: {e}")
            self.controller.logger.error(traceback.format_exc())
            return []

if __name__ == "__main__":
    # テスト実行
    from advanced_scraper import SocialInsuranceNewsCollector
    
    collector = SocialInsuranceNewsCollector()
    controlled_scraper = ControlledScraper()
    
    news_data = controlled_scraper.run_controlled_collection(collector)
    print(f"📊 最終結果: {len(news_data)}件のニュースを収集")