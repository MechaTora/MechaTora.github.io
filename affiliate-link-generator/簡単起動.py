#!/usr/bin/env python3
"""
WSL環境対応版 - tkinter不要の起動確認
"""
import sys
import subprocess

def main():
    print("🔧 環境確認中...")
    
    # tkinter チェック
    try:
        import tkinter
        print("✅ tkinter 利用可能")
        
        # main_app.py を直接起動
        from main_app import main
        main()
        
    except ImportError:
        print("❌ tkinter が見つかりません")
        print("")
        print("解決方法:")
        print("1. sudo apt install python3-tk")
        print("2. または Windows版Pythonで実行")
        print("")
        
        # 自動インストールを試行
        try:
            print("🔧 自動インストールを試行中...")
            result = subprocess.run(['sudo', 'apt', 'install', '-y', 'python3-tk'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ tkinter インストール完了")
                print("🚀 アプリを再起動してください")
            else:
                print("❌ 自動インストール失敗")
                print("手動でインストールしてください:")
                print("sudo apt install python3-tk")
        except Exception as e:
            print(f"❌ インストールエラー: {e}")
            
if __name__ == "__main__":
    main()