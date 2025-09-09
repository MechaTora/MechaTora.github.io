#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon・楽天アフィリエイトリンク自動生成ツール
起動スクリプト - 環境チェックとアプリケーション起動
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# 必要なパッケージのリスト
REQUIRED_PACKAGES = {
    'selenium': '4.15.0',
    'openpyxl': '3.1.2', 
    'webdriver_manager': '4.0.1',
    'requests': '2.31.0',
    'beautifulsoup4': '4.12.2',
    'pyshorteners': '1.0.1'
}

OPTIONAL_PACKAGES = {
    # 'tkinter-tooltip': '2.1.0'  # 不要なため削除
}

def print_banner():
    """アプリケーション起動時のバナー表示"""
    print("=" * 60)
    print("🛍️ Amazon・楽天アフィリエイトリンク自動生成ツール v1.0")
    print("=" * 60)
    print()

def check_python_version():
    """Pythonバージョンのチェック"""
    print("🔍 Python環境をチェック中...")
    
    # Pythonバージョン
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8以上が必要です (現在: {version.major}.{version.minor}.{version.micro})")
        return False
    
    print(f"✅ Python バージョン: {version.major}.{version.minor}.{version.micro}")
    return True

def check_and_install_tkinter():
    """tkinterの確認と自動インストール"""
    print("🔍 tkinter をチェック中...")
    
    try:
        import tkinter
        print("✅ tkinter は利用可能です")
        return True
    except ImportError:
        print("⚠️ tkinter が見つかりません - 自動インストールを試行中...")
        
        # Windows環境での自動修復を試行
        try:
            import platform
            if platform.system().lower() == "windows":
                print("🔧 Windows環境でtkinter修復を試行中...")
                
                # 代替パッケージの試行
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "tk"], 
                                 capture_output=True, check=True)
                    print("✅ tk パッケージをインストールしました")
                    return True
                except:
                    pass
                
                print("❌ tkinter自動インストールに失敗")
                print("📋 解決方法:")
                print("   1. https://www.python.org/downloads/ からPython最新版をダウンロード")
                print("   2. インストール時に 'tcl/tk and IDLE' にチェック")
                print("   3. 'Add Python to PATH' にチェック")
                
                # 自動でブラウザを開く
                try:
                    import webbrowser
                    webbrowser.open("https://www.python.org/downloads/")
                    print("🌐 Pythonダウンロードページを開きました")
                except:
                    pass
                
                return False
                
            else:
                print("❌ Linux/macOS環境では手動インストールが必要です:")
                print("   Ubuntu/Debian: sudo apt-get install python3-tk")
                print("   CentOS/RHEL: sudo yum install tkinter")
                return False
                
        except Exception as e:
            print(f"❌ tkinterチェック中にエラー: {e}")
            return False

def check_chrome_browser():
    """Google Chromeの存在確認"""
    print("🔍 Google Chrome をチェック中...")
    
    # Windows用のChrome確認
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_found = True
            print(f"✅ Google Chrome: 見つかりました ({path})")
            break
    
    if not chrome_found:
        print("⚠️ Google Chrome が見つかりません")
        print("   https://www.google.com/chrome/ からダウンロードしてください")
        return False
    
    return True

def check_package(package_name, required_version=None):
    """パッケージの存在確認"""
    try:
        __import__(package_name)
        
        if required_version:
            try:
                import pkg_resources
                installed_version = pkg_resources.get_distribution(package_name).version
                print(f"✅ {package_name}: {installed_version}")
            except:
                print(f"✅ {package_name}: インストール済み")
        else:
            print(f"✅ {package_name}: インストール済み")
        return True
        
    except ImportError:
        print(f"❌ {package_name}: 見つかりません")
        return False

def install_package(package_name, version=None):
    """パッケージのインストール"""
    try:
        if version:
            package_spec = f"{package_name}=={version}"
        else:
            package_spec = package_name
        
        print(f"📦 {package_spec} をインストール中...")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_spec
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {package_spec} インストール完了")
            return True
        else:
            print(f"❌ {package_spec} インストール失敗:")
            print(f"   {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {package_name} インストールタイムアウト")
        return False
    except Exception as e:
        print(f"❌ {package_name} インストールエラー: {str(e)}")
        return False

def check_and_install_packages():
    """必要なパッケージの確認とインストール"""
    print("📦 必要なパッケージをチェック中...")
    
    missing_packages = []
    
    # 必須パッケージのチェック
    for package, version in REQUIRED_PACKAGES.items():
        # 特別な名前のパッケージの処理
        import_name = package
        if package == 'beautifulsoup4':
            import_name = 'bs4'
        elif package == 'webdriver_manager':
            import_name = 'webdriver_manager'
        
        if not check_package(import_name, version):
            missing_packages.append((package, version))
    
    # オプションパッケージのチェック
    for package, version in OPTIONAL_PACKAGES.items():
        check_package(package.replace('-', '_'), version)
    
    # 不足パッケージのインストール
    if missing_packages:
        print()
        print("🔧 不足しているパッケージを自動インストールします...")
        
        for package, version in missing_packages:
            success = install_package(package, version)
            if not success:
                print(f"❌ {package} の自動インストールに失敗しました")
                print("手動でインストールしてください:")
                print(f"   pip install {package}=={version}")
                return False
        
        print("✅ 全てのパッケージのインストールが完了しました")
    else:
        print("✅ 必要なパッケージは全てインストール済みです")
    
    return True

def create_sample_file():
    """サンプルExcelファイルの作成"""
    sample_file = "sample_products.xlsx"
    
    if os.path.exists(sample_file):
        print(f"📄 サンプルファイルは既に存在します: {sample_file}")
        return True
    
    try:
        print(f"📄 サンプルファイルを作成中: {sample_file}")
        
        # excel_managerモジュールを使用してサンプルファイル作成
        from excel_manager import ExcelManager
        
        excel_manager = ExcelManager()
        success = excel_manager.create_sample_file(sample_file)
        
        if success:
            print(f"✅ サンプルファイル作成完了: {sample_file}")
            return True
        else:
            print(f"❌ サンプルファイル作成失敗: {sample_file}")
            return False
            
    except ImportError:
        print("⚠️ サンプルファイル作成をスキップ（excel_manager未インストール）")
        return True
    except Exception as e:
        print(f"❌ サンプルファイル作成エラー: {str(e)}")
        return True  # エラーでも継続

def check_config_file():
    """設定ファイルの確認"""
    config_file = "config.json"
    
    if os.path.exists(config_file):
        print(f"⚙️ 設定ファイル: 既に存在 ({config_file})")
    else:
        print(f"⚙️ 設定ファイル: 初回起動時に作成されます ({config_file})")
    
    return True

def run_main_application():
    """メインアプリケーションの起動"""
    try:
        print("🚀 アプリケーションを起動中...")
        print()
        
        # メインアプリケーションのインポートと起動
        from main_app import main
        main()
        
    except ImportError as e:
        print(f"❌ アプリケーション起動エラー: {str(e)}")
        print("必要なモジュールが見つかりません")
        return False
    except KeyboardInterrupt:
        print("⏹️ ユーザーによって中断されました")
        return True
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_startup_tips():
    """起動時のヒント表示"""
    print("💡 使用前のヒント:")
    print("   1. 設定メニューでアフィリエイトIDを設定してください")
    print("   2. ExcelファイルのB列に商品名を入力してください")
    print("   3. sample_products.xlsx を参考にしてください")
    print()

def main():
    """メイン関数"""
    try:
        # バナー表示
        print_banner()
        
        # 環境チェック
        print("🔍 環境チェックを実行中...")
        
        # Pythonバージョンチェック
        if not check_python_version():
            input("Enterを押して終了...")
            return
        
        # tkinterチェック
        if not check_and_install_tkinter():
            input("Enterを押して終了...")
            return
        
        # Google Chromeチェック
        if not check_chrome_browser():
            print("⚠️ Google Chrome がインストールされていない場合、Amazon検索が動作しません")
            # 自動的に続行（GUI環境では対話的入力は無効）
            response = "y"
            if response not in ['y', 'yes']:
                return
        
        # パッケージチェック・インストール
        if not check_and_install_packages():
            input("Enterを押して終了...")
            return
        
        # サンプルファイル作成
        create_sample_file()
        
        # 設定ファイルチェック
        check_config_file()
        
        print()
        print("✅ 環境チェック完了")
        print()
        
        # 起動ヒント表示
        show_startup_tips()
        
        # 少し待機してからアプリケーション起動
        print("アプリケーションを起動します...")
        time.sleep(2)
        
        # メインアプリケーション起動
        run_main_application()
        
    except KeyboardInterrupt:
        print()
        print("⏹️ 起動処理を中断しました")
    except Exception as e:
        print(f"❌ 起動エラー: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # GUI環境では自動終了
        pass

if __name__ == "__main__":
    main()