#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動セットアップスクリプト - tkinter対応版
"""

import subprocess
import sys
import os
import platform
import urllib.request
import tempfile
import webbrowser

def print_status(message, status="INFO"):
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def check_tkinter():
    """tkinterの存在確認"""
    try:
        import tkinter
        print_status("tkinter は利用可能です", "SUCCESS")
        return True
    except ImportError:
        print_status("tkinter が見つかりません", "WARNING")
        return False

def install_tkinter_windows():
    """Windows用tkinter自動インストール"""
    print_status("Windows環境でのtkinterインストールを開始します...")
    
    try:
        # pip経由でtkinter代替パッケージを試す
        print_status("代替パッケージのインストールを試行中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tkinter-page"], 
                      capture_output=True, check=True)
        print_status("tkinter-page パッケージをインストールしました", "SUCCESS")
        return True
    except:
        pass
    
    try:
        # tk パッケージを試す
        subprocess.run([sys.executable, "-m", "pip", "install", "tk"], 
                      capture_output=True, check=True)
        print_status("tk パッケージをインストールしました", "SUCCESS")
        return True
    except:
        pass
    
    # Python再インストールの案内
    print_status("自動インストールに失敗しました", "ERROR")
    print("\n" + "="*60)
    print("🔧 PYTHON 再インストールが必要です")
    print("="*60)
    print("1. https://www.python.org/downloads/ にアクセス")
    print("2. 最新のPythonをダウンロード")
    print("3. インストール時に以下にチェックを入れる:")
    print("   ✅ Add Python to PATH")
    print("   ✅ tcl/tk and IDLE")
    print("   ✅ Install for all users")
    print("="*60)
    
    # ブラウザでPythonダウンロードページを開く
    try:
        webbrowser.open("https://www.python.org/downloads/")
        print_status("Pythonダウンロードページを開きました", "INFO")
    except:
        pass
    
    return False

def install_tkinter_linux():
    """Linux用tkinter自動インストール"""
    print_status("Linux環境でのtkinterインストールを開始します...")
    
    try:
        # Ubuntu/Debian系
        result = subprocess.run(["which", "apt-get"], capture_output=True)
        if result.returncode == 0:
            print_status("apt-getを使用してtkinterをインストール中...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3-tk"], check=True)
            print_status("python3-tk をインストールしました", "SUCCESS")
            return True
    except:
        pass
    
    try:
        # CentOS/RHEL系
        result = subprocess.run(["which", "yum"], capture_output=True)
        if result.returncode == 0:
            print_status("yumを使用してtkinterをインストール中...")
            subprocess.run(["sudo", "yum", "install", "-y", "tkinter"], check=True)
            print_status("tkinter をインストールしました", "SUCCESS")
            return True
    except:
        pass
    
    print_status("Linux用自動インストールに失敗しました", "ERROR")
    print("手動で以下のコマンドを実行してください:")
    print("Ubuntu/Debian: sudo apt-get install python3-tk")
    print("CentOS/RHEL: sudo yum install tkinter")
    return False

def install_missing_packages():
    """不足パッケージの自動インストール"""
    packages = [
        "selenium",
        "openpyxl", 
        "webdriver-manager",
        "requests",
        "beautifulsoup4",
        "pyshorteners",
        "xlrd"
    ]
    
    print_status("必要パッケージの確認とインストール...")
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            try:
                print_status(f"{package} をインストール中...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print_status(f"{package} をインストールしました", "SUCCESS")
            except Exception as e:
                print_status(f"{package} のインストールに失敗: {e}", "ERROR")

def main():
    print("="*60)
    print("🚀 アフィリエイトリンク生成ツール - 自動セットアップ")
    print("="*60)
    
    # OS検出
    system = platform.system().lower()
    print_status(f"OS: {system}")
    
    # tkinter確認
    if not check_tkinter():
        print_status("tkinter の自動インストールを開始します...")
        
        if "windows" in system:
            success = install_tkinter_windows()
        elif "linux" in system:
            success = install_tkinter_linux()
        else:
            print_status(f"未対応OS: {system}", "ERROR")
            success = False
        
        if success:
            # 再確認
            if not check_tkinter():
                print_status("tkinterのインストール後も利用できません", "ERROR")
                print_status("Pythonの再起動が必要かもしれません", "WARNING")
    
    # 必要パッケージのインストール
    install_missing_packages()
    
    print("\n" + "="*60)
    print("✨ セットアップ完了！")
    print("="*60)
    print("次のコマンドでアプリケーションを起動してください:")
    print("python source_code/run_app.py")
    print("="*60)
    
    input("Enter キーを押して終了...")

if __name__ == "__main__":
    main()