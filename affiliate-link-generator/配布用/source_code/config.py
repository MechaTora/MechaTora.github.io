#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール
アプリケーションの設定を管理
"""

import os
import json
from typing import Dict, Any


class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings: Dict[str, Any] = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "amazon": {
                "associate_id": "",
                "search_interval": 3.0,  # 規約遵守: Seleniumスクレイピングのため安全マージン
                "max_search_results": 5,
                "use_selenium": True
            },
            "rakuten": {
                "affiliate_id": "",
                "api_key": "",
                "search_interval": 1.5,  # 規約遵守: 1秒/リクエスト制限+安全マージン
                "max_search_results": 5
            },
            "general": {
                "create_backup": True,
                "use_short_urls": False,
                "concurrent_processing": False,
                "log_level": "INFO"
            },
            "ui": {
                "window_width": 800,
                "window_height": 600,
                "theme": "default"
            }
        }
    
    def load_config(self) -> bool:
        """設定ファイルを読み込む"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                
                # デフォルト設定に保存済み設定をマージ
                self._merge_config(self.settings, saved_config)
                print(f"✅ 設定ファイル読み込み完了: {self.config_file}")
                return True
            else:
                print(f"📄 設定ファイルが見つかりません。デフォルト設定を使用します: {self.config_file}")
                return False
                
        except Exception as e:
            print(f"⚠️ 設定ファイル読み込みエラー: {str(e)}")
            print("デフォルト設定を使用します")
            return False
    
    def _merge_config(self, default: Dict[str, Any], saved: Dict[str, Any]):
        """設定をマージする"""
        for key, value in saved.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def save_config(self) -> bool:
        """設定をファイルに保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"💾 設定保存完了: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 設定保存エラー: {str(e)}")
            return False
    
    def get(self, category: str, key: str = None, default=None):
        """設定値を取得"""
        try:
            if key is None:
                return self.settings.get(category, default)
            else:
                return self.settings.get(category, {}).get(key, default)
        except Exception:
            return default
    
    def set(self, category: str, key: str, value: Any) -> bool:
        """設定値を更新（規約違反値は自動補正）"""
        try:
            if category not in self.settings:
                self.settings[category] = {}
            
            # 検索間隔の規約遵守チェックと自動補正
            if key == "search_interval":
                if category == "amazon":
                    if value < 3.0:
                        print(f"⚠️ Amazon検索間隔 {value}秒 は規約違反のため 3.0秒 に自動補正されました")
                        value = 3.0
                elif category == "rakuten":
                    if value < 1.0:
                        print(f"⚠️ 楽天検索間隔 {value}秒 は規約違反のため 1.0秒 に自動補正されました")
                        value = 1.0
            
            self.settings[category][key] = value
            return True
            
        except Exception as e:
            print(f"❌ 設定更新エラー: {str(e)}")
            return False
    
    def is_amazon_configured(self) -> bool:
        """Amazon設定が完了しているかチェック"""
        associate_id = self.get("amazon", "associate_id", "")
        return bool(associate_id and associate_id.strip())
    
    def is_rakuten_configured(self) -> bool:
        """楽天設定が完了しているかチェック"""
        affiliate_id = self.get("rakuten", "affiliate_id", "")
        return bool(affiliate_id and affiliate_id.strip())
    
    def get_validation_errors(self) -> list:
        """設定の検証エラーを取得"""
        errors = []
        
        # Amazon設定チェック
        associate_id = self.get("amazon", "associate_id", "")
        if not associate_id or not associate_id.strip():
            errors.append("Amazon アソシエイトIDが設定されていません")
        elif not associate_id.endswith("-22"):
            errors.append("Amazon アソシエイトIDの形式が正しくない可能性があります（例: yoursite-22）")
        
        # 楽天設定チェック
        affiliate_id = self.get("rakuten", "affiliate_id", "")
        if not affiliate_id or not affiliate_id.strip():
            errors.append("楽天 アフィリエイトIDが設定されていません")
        
        # 検索間隔チェック（規約遵守）- 設定時に自動補正されるため通常はエラーなし
        amazon_interval = self.get("amazon", "search_interval", 3.0)
        if amazon_interval < 3.0:
            errors.append(f"❌ Amazon検索間隔 {amazon_interval}秒 は規約違反です（最小値: 3.0秒）")
        
        rakuten_interval = self.get("rakuten", "search_interval", 1.5)
        if rakuten_interval < 1.0:
            errors.append(f"❌ 楽天検索間隔 {rakuten_interval}秒 は規約違反です（最小値: 1.0秒）")
        
        return errors