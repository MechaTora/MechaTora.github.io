#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon・楽天アフィリエイトリンク自動生成ツール
メインGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import time
from typing import Optional, Dict, Any

from config import Config
from excel_manager import ExcelManager
from amazon_scraper import AmazonScraper
from rakuten_scraper import RakutenScraper

try:
    import pyshorteners
    SHORTENER_AVAILABLE = True
except ImportError:
    SHORTENER_AVAILABLE = False
    print("⚠️ pyshorteners が見つかりません。短縮URL機能は無効です")


class AffiliateApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # 設定とマネージャーの初期化
        self.config = Config()
        self.excel_manager = ExcelManager()
        
        # 処理状態管理
        self.current_file = ""
        self.products_data = []
        self.is_processing = False
        self.processing_thread = None
        
        # 進捗管理
        self.progress_queue = queue.Queue()
        self.total_products = 0
        self.processed_count = 0
        
        # UI構築
        self.create_widgets()
        self.setup_menu()
        
        # 進捗更新の定期実行
        self.root.after(100, self.check_progress_queue)
        
        print("🚀 アフィリエイトリンク生成ツール起動完了")
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("Amazon・楽天アフィリエイトリンク自動生成ツール v1.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # アイコン設定（ファイルが存在する場合）
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def create_widgets(self):
        """UIウィジェットの作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ファイル選択セクション
        file_frame = ttk.LabelFrame(main_frame, text="📁 Excelファイル", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="📂 ファイル選択", command=self.select_file).grid(row=0, column=0, padx=(0, 10))
        
        self.file_path_var = tk.StringVar(value="ファイルが選択されていません")
        self.file_label = ttk.Label(file_frame, textvariable=self.file_path_var, foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # ファイル統計表示
        self.stats_var = tk.StringVar()
        self.stats_label = ttk.Label(file_frame, textvariable=self.stats_var, foreground="blue")
        self.stats_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W), pady=(5, 0))
        
        # 処理設定セクション
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 処理設定", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # URL形式選択
        ttk.Label(settings_frame, text="URL形式:").grid(row=0, column=0, sticky=tk.W)
        self.url_format_var = tk.StringVar(value="full")
        ttk.Radiobutton(settings_frame, text="フルURL", variable=self.url_format_var, value="full").grid(row=0, column=1, sticky=tk.W)
        
        if SHORTENER_AVAILABLE:
            ttk.Radiobutton(settings_frame, text="短縮URL", variable=self.url_format_var, value="short").grid(row=0, column=2, sticky=tk.W)
        else:
            short_radio = ttk.Radiobutton(settings_frame, text="短縮URL（無効）", variable=self.url_format_var, value="short")
            short_radio.grid(row=0, column=2, sticky=tk.W)
            short_radio.configure(state='disabled')
        
        # 処理対象選択
        ttk.Label(settings_frame, text="処理対象:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.amazon_var = tk.BooleanVar(value=True)
        self.rakuten_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Amazon", variable=self.amazon_var).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(settings_frame, text="楽天", variable=self.rakuten_var).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        # 実行ボタンセクション
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="🚀 リンク生成開始", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="💾 保存", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)
        
        # 進捗表示セクション
        progress_frame = ttk.LabelFrame(main_frame, text="📊 進捗状況", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 進捗テキスト
        self.progress_text_var = tk.StringVar(value="待機中...")
        self.progress_text = ttk.Label(progress_frame, textvariable=self.progress_text_var)
        self.progress_text.grid(row=1, column=0, sticky=tk.W)
        
        # ログ表示セクション
        log_frame = ttk.LabelFrame(main_frame, text="📝 ログ", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # スクロール可能なログ表示
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ログクリアボタン
        ttk.Button(log_frame, text="🗑️ ログクリア", command=self.clear_log).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def setup_menu(self):
        """メニューバーの設定"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="📂 Excelファイル選択", command=self.select_file)
        file_menu.add_separator()
        file_menu.add_command(label="📄 サンプルファイル作成", command=self.create_sample_file)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 終了", command=self.on_closing)
        
        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="🛒 Amazon設定", command=self.open_amazon_settings)
        settings_menu.add_command(label="🛍️ 楽天設定", command=self.open_rakuten_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="⚙️ 全般設定", command=self.open_general_settings)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="❓ 使い方", command=self.show_help)
        help_menu.add_command(label="ℹ️ バージョン情報", command=self.show_about)
    
    def select_file(self):
        """Excelファイルの選択"""
        file_types = [
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Excelファイルを選択",
            filetypes=file_types
        )
        
        if file_path:
            self.load_excel_file(file_path)
    
    def load_excel_file(self, file_path: str):
        """Excelファイルの読み込み"""
        try:
            self.log_message(f"📖 ファイル読み込み開始: {os.path.basename(file_path)}")
            
            # ファイル読み込み
            success = self.excel_manager.load_file(file_path)
            
            if success:
                self.current_file = file_path
                self.products_data = self.excel_manager.get_products()
                
                # UI更新
                self.file_path_var.set(os.path.basename(file_path))
                self.file_label.configure(foreground="black")
                
                # 統計情報表示
                stats = self.excel_manager.get_statistics()
                stats_text = (f"📊 商品数: {stats['total_products']} | "
                            f"Amazon: {stats['amazon_links']} | "
                            f"楽天: {stats['rakuten_links']}")
                self.stats_var.set(stats_text)
                
                # ボタン状態更新
                self.start_button.configure(state=tk.NORMAL)
                self.save_button.configure(state=tk.NORMAL)
                
                self.log_message(f"✅ ファイル読み込み完了: {stats['total_products']}個の商品データ")
                
            else:
                self.log_message("❌ ファイル読み込みに失敗しました")
                messagebox.showerror("エラー", "Excelファイルの読み込みに失敗しました")
                
        except Exception as e:
            error_msg = f"❌ ファイル読み込みエラー: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("エラー", error_msg)
    
    def start_processing(self):
        """リンク生成処理の開始"""
        # 設定チェック
        errors = self.validate_settings()
        if errors:
            error_msg = "設定に問題があります:" + " ".join(errors) + " 設定メニューから設定してください。"
            messagebox.showwarning("設定エラー", error_msg)
            return
        
        if not self.products_data:
            messagebox.showwarning("ファイル未選択", "処理対象のExcelファイルを選択してください")
            return
        
        # 処理対象チェック
        if not self.amazon_var.get() and not self.rakuten_var.get():
            messagebox.showwarning("処理対象未選択", "Amazon または 楽天 のどちらかを選択してください")
            return
        
        # UI状態変更
        self.is_processing = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.DISABLED)
        
        # 進捗初期化
        self.total_products = len(self.products_data)
        self.processed_count = 0
        self.progress_var.set(0)
        self.progress_text_var.set("処理開始...")
        
        # 処理スレッド開始
        self.processing_thread = threading.Thread(target=self.processing_worker, daemon=True)
        self.processing_thread.start()
        
        self.log_message(f"🚀 処理開始: {self.total_products}個の商品を処理します")
    
    def processing_worker(self):
        """バックグラウンド処理ワーカー"""
        amazon_scraper = None
        rakuten_scraper = None
        
        try:
            # スクレーパー初期化
            amazon_scraper = None
            rakuten_scraper = None
            
            if self.amazon_var.get():
                associate_id = self.config.get("amazon", "associate_id")
                search_interval = self.config.get("amazon", "search_interval", 2.0)
                amazon_scraper = AmazonScraper(associate_id=associate_id, headless=True, search_interval=search_interval)
                
                if not amazon_scraper.initialize_driver():
                    self.progress_queue.put(("warning", "⚠️ Amazon WebDriverの初期化に失敗しました"))
                    self.progress_queue.put(("info", "💡 楽天検索のみで続行します"))
                    amazon_scraper = None  # Amazon検索を無効化
                else:
                    self.progress_queue.put(("info", "✅ Amazon スクレーパー初期化完了"))
            
            if self.rakuten_var.get():
                affiliate_id = self.config.get("rakuten", "affiliate_id")
                search_interval = self.config.get("rakuten", "search_interval", 2.0)
                api_key = self.config.get("rakuten", "api_key", "")
                rakuten_scraper = RakutenScraper(affiliate_id=affiliate_id, api_key=api_key, search_interval=search_interval)
                
                self.progress_queue.put(("info", "✅ 楽天 スクレーパー初期化完了"))
            
            # 両方とも初期化に失敗した場合のみエラー
            if not amazon_scraper and not rakuten_scraper:
                self.progress_queue.put(("error", "❌ すべての検索エンジンの初期化に失敗しました"))
                return
            
            # 商品処理
            for i, product in enumerate(self.products_data):
                if not self.is_processing:  # 停止チェック
                    break
                
                product_name = product['product_name']
                row = product['row']
                
                self.progress_queue.put(("progress", f"処理中: {product_name}"))
                
                # Amazon処理
                if self.amazon_var.get() and amazon_scraper:
                    try:
                        result = amazon_scraper.get_best_match(product_name)
                        if result:
                            affiliate_url = result['affiliate_url']
                            
                            # 短縮URL処理
                            if self.url_format_var.get() == "short" and SHORTENER_AVAILABLE:
                                affiliate_url = self.shorten_url(affiliate_url)
                            
                            # Excel更新
                            self.excel_manager.update_product_link(row, "amazon", affiliate_url)
                            self.progress_queue.put(("info", f"✅ Amazon: {product_name[:30]}..."))
                        else:
                            self.progress_queue.put(("warning", f"⚠️ Amazon: {product_name[:30]}... が見つかりません"))
                    except Exception as e:
                        self.progress_queue.put(("error", f"❌ Amazon処理エラー ({product_name[:20]}...): {str(e)}"))
                
                # 楽天処理
                if self.rakuten_var.get() and rakuten_scraper:
                    try:
                        result = rakuten_scraper.get_best_match(product_name)
                        if result:
                            affiliate_url = result['affiliate_url']
                            
                            # 短縮URL処理
                            if self.url_format_var.get() == "short" and SHORTENER_AVAILABLE:
                                affiliate_url = self.shorten_url(affiliate_url)
                            
                            # Excel更新
                            self.excel_manager.update_product_link(row, "rakuten", affiliate_url)
                            self.progress_queue.put(("info", f"✅ 楽天: {product_name[:30]}..."))
                        else:
                            self.progress_queue.put(("warning", f"⚠️ 楽天: {product_name[:30]}... が見つかりません"))
                    except Exception as e:
                        self.progress_queue.put(("error", f"❌ 楽天処理エラー ({product_name[:20]}...): {str(e)}"))
                
                # 進捗更新
                self.processed_count += 1
                progress_percent = (self.processed_count / self.total_products) * 100
                self.progress_queue.put(("progress_update", progress_percent))
            
            if self.is_processing:
                self.progress_queue.put(("complete", "🎉 すべての処理が完了しました"))
                # 処理完了後に自動保存
                self.progress_queue.put(("auto_save", "💾 自動保存中..."))
            else:
                self.progress_queue.put(("stopped", "⏹️ 処理を停止しました"))
        
        except Exception as e:
            self.progress_queue.put(("error", f"❌ 処理中にエラーが発生しました: {str(e)}"))
        
        finally:
            # リソースクリーンアップ
            if amazon_scraper:
                amazon_scraper.close()
            if rakuten_scraper:
                rakuten_scraper.close()
            
            self.progress_queue.put(("finished", None))
    
    def stop_processing(self):
        """処理の停止"""
        self.is_processing = False
        self.log_message("🛑 処理停止要求を送信しました...")
    
    def save_file(self):
        """ファイルの保存"""
        if not self.excel_manager or not self.current_file:
            messagebox.showwarning("保存エラー", "保存対象のファイルがありません")
            return
        
        try:
            create_backup = self.config.get("general", "create_backup", True)
            success = self.excel_manager.save_file(create_backup=create_backup)
            
            if success:
                self.log_message("💾 ファイル保存完了")
                messagebox.showinfo("保存完了", "ファイルが正常に保存されました")
            else:
                self.log_message("❌ ファイル保存に失敗")
                messagebox.showerror("保存エラー", "ファイル保存に失敗しました")
                
        except Exception as e:
            error_msg = f"❌ 保存エラー: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("保存エラー", error_msg)
    
    def create_sample_file(self):
        """サンプルファイルの作成"""
        file_path = filedialog.asksaveasfilename(
            title="サンプルファイルの保存先",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                success = self.excel_manager.create_sample_file(file_path)
                if success:
                    self.log_message(f"📄 サンプルファイル作成完了: {os.path.basename(file_path)}")
                    messagebox.showinfo("作成完了", f"サンプルファイルを作成しました: {os.path.basename(file_path)}")
                else:
                    self.log_message("❌ サンプルファイル作成に失敗")
                    messagebox.showerror("作成エラー", "サンプルファイル作成に失敗しました")
            except Exception as e:
                error_msg = f"❌ サンプルファイル作成エラー: {str(e)}"
                self.log_message(error_msg)
                messagebox.showerror("作成エラー", error_msg)
    
    def validate_settings(self) -> list:
        """設定の検証"""
        errors = []
        
        if self.amazon_var.get() and not self.config.is_amazon_configured():
            errors.append("・Amazon設定が未完了")
        
        if self.rakuten_var.get() and not self.config.is_rakuten_configured():
            errors.append("・楽天設定が未完了")
        
        return errors
    
    def shorten_url(self, url: str) -> str:
        """URLの短縮"""
        if not SHORTENER_AVAILABLE:
            return url
        
        try:
            s = pyshorteners.Shortener()
            short_url = s.tinyurl.short(url)
            return short_url
        except Exception as e:
            self.progress_queue.put(("warning", f"⚠️ URL短縮エラー: {str(e)}"))
            return url
    
    def check_progress_queue(self):
        """進捗キューの確認"""
        try:
            while True:
                msg_type, msg_content = self.progress_queue.get_nowait()
                
                if msg_type == "info":
                    self.log_message(msg_content)
                elif msg_type == "warning":
                    self.log_message(msg_content)
                elif msg_type == "error":
                    self.log_message(msg_content)
                elif msg_type == "progress":
                    self.progress_text_var.set(msg_content)
                elif msg_type == "progress_update":
                    self.progress_var.set(msg_content)
                    self.progress_text_var.set(f"進捗: {self.processed_count}/{self.total_products} ({msg_content:.1f}%)")
                elif msg_type == "complete":
                    self.log_message(msg_content)
                    self.progress_text_var.set("処理完了")
                    self.progress_var.set(100)
                elif msg_type == "auto_save":
                    self.log_message(msg_content)
                    self.progress_text_var.set("自動保存中...")
                    # 自動保存実行
                    try:
                        create_backup = self.config.get("general", "create_backup", True)
                        success = self.excel_manager.save_file(create_backup=create_backup)
                        if success:
                            self.progress_queue.put(("info", "✅ 自動保存完了"))
                        else:
                            self.progress_queue.put(("error", "❌ 自動保存に失敗"))
                    except Exception as e:
                        self.progress_queue.put(("error", f"❌ 自動保存エラー: {str(e)}"))
                elif msg_type == "stopped":
                    self.log_message(msg_content)
                    self.progress_text_var.set("処理停止")
                elif msg_type == "finished":
                    # 処理完了時のUI状態復旧
                    self.is_processing = False
                    self.start_button.configure(state=tk.NORMAL)
                    self.stop_button.configure(state=tk.DISABLED)
                    self.save_button.configure(state=tk.NORMAL)
                    
        except queue.Empty:
            pass
        
        # 定期実行
        self.root.after(100, self.check_progress_queue)
    
    def log_message(self, message: str):
        """ログメッセージの表示"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        print(log_entry)  # コンソールにも出力
    
    def clear_log(self):
        """ログのクリア"""
        self.log_text.delete(1.0, tk.END)
    
    # 設定ダイアログ
    def open_amazon_settings(self):
        """Amazon設定ダイアログ"""
        AmazonSettingsDialog(self.root, self.config)
    
    def open_rakuten_settings(self):
        """楽天設定ダイアログ"""
        RakutenSettingsDialog(self.root, self.config)
    
    def open_general_settings(self):
        """全般設定ダイアログ"""
        GeneralSettingsDialog(self.root, self.config)
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
🛍️ Amazon・楽天アフィリエイトリンク自動生成ツール

【使い方】
1. 設定メニューからアフィリエイトIDを設定
2. ExcelファイルのB列に商品名を入力
3. ファイル選択でExcelファイルを読み込み
4. 処理対象（Amazon/楽天）を選択
5. リンク生成開始をクリック
6. 完了後、保存をクリック

【注意事項】
・各サービスの利用規約を遵守してください
・過度なアクセスは避けてください
・アフィリエイトプログラムへの登録が必要です
        """
        messagebox.showinfo("使い方", help_text)
    
    def show_about(self):
        """バージョン情報表示"""
        about_text = """
🛍️ Amazon・楽天アフィリエイトリンク自動生成ツール

バージョン: 1.0
開発: Claude Code Assistant
対応OS: Windows 10/11

【機能】
・Amazon商品検索とアフィリエイトリンク生成
・楽天商品検索とアフィリエイトリンク生成
・Excel一括処理
・URL短縮対応
・進捗表示
        """
        messagebox.showinfo("バージョン情報", about_text)
    
    def on_closing(self):
        """アプリケーション終了時の処理"""
        if self.is_processing:
            if messagebox.askokcancel("終了確認", "処理中です。終了しますか？"):
                self.is_processing = False
                self.root.destroy()
        else:
            self.root.destroy()


# 設定ダイアログクラス群

class AmazonSettingsDialog:
    def __init__(self, parent, config: Config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
    
    def setup_dialog(self):
        self.dialog.title("Amazon設定")
        self.dialog.geometry("400x300")
        self.dialog.transient()
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # アソシエイトID
        ttk.Label(main_frame, text="アソシエイトID:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.associate_id_var = tk.StringVar(value=self.config.get("amazon", "associate_id", ""))
        ttk.Entry(main_frame, textvariable=self.associate_id_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(main_frame, text="例: yoursite-22", foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # 検索間隔（規約遵守のため制限付き）
        ttk.Label(main_frame, text="検索間隔 (秒):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.interval_var = tk.DoubleVar(value=self.config.get("amazon", "search_interval", 3.0))
        interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=30)
        interval_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 入力値のリアルタイム検証
        def validate_amazon_interval(*args):
            try:
                value = self.interval_var.get()
                if value < 3.0:
                    self.interval_var.set(3.0)
                    interval_entry.configure(foreground="red")
                    self.root.after(1000, lambda: interval_entry.configure(foreground="black"))
                else:
                    interval_entry.configure(foreground="black")
            except tk.TclError:
                pass
        
        self.interval_var.trace('w', validate_amazon_interval)
        
        ttk.Label(main_frame, text="最小値: 3.0秒（規約遵守）", foreground="red").grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # 最大検索結果数
        ttk.Label(main_frame, text="最大検索結果数:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.max_results_var = tk.IntVar(value=self.config.get("amazon", "max_search_results", 5))
        ttk.Entry(main_frame, textvariable=self.max_results_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
    
    def save_settings(self):
        try:
            self.config.set("amazon", "associate_id", self.associate_id_var.get().strip())
            # 規約遵守のため最小3.0秒を強制
            interval = max(3.0, self.interval_var.get())
            self.config.set("amazon", "search_interval", interval)
            self.config.set("amazon", "max_search_results", max(1, self.max_results_var.get()))
            
            if self.config.save_config():
                messagebox.showinfo("保存完了", "Amazon設定を保存しました")
                self.dialog.destroy()
            else:
                messagebox.showerror("保存エラー", "設定の保存に失敗しました")
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存エラー: {str(e)}")


class RakutenSettingsDialog:
    def __init__(self, parent, config: Config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
    
    def setup_dialog(self):
        self.dialog.title("楽天設定")
        self.dialog.geometry("400x350")
        self.dialog.transient()
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # アフィリエイトID
        ttk.Label(main_frame, text="アフィリエイトID:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.affiliate_id_var = tk.StringVar(value=self.config.get("rakuten", "affiliate_id", ""))
        ttk.Entry(main_frame, textvariable=self.affiliate_id_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # APIキー（オプション）
        ttk.Label(main_frame, text="APIキー (オプション):").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.api_key_var = tk.StringVar(value=self.config.get("rakuten", "api_key", ""))
        ttk.Entry(main_frame, textvariable=self.api_key_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 5))
        
        ttk.Label(main_frame, text="未入力でもOK", foreground="gray").grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # 検索間隔（規約遵守のため制限付き）
        ttk.Label(main_frame, text="検索間隔 (秒):").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.interval_var = tk.DoubleVar(value=self.config.get("rakuten", "search_interval", 1.5))
        interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=30)
        interval_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 入力値のリアルタイム検証
        def validate_rakuten_interval(*args):
            try:
                value = self.interval_var.get()
                if value < 1.0:
                    self.interval_var.set(1.0)
                    interval_entry.configure(foreground="red")
                    self.root.after(1000, lambda: interval_entry.configure(foreground="black"))
                else:
                    interval_entry.configure(foreground="black")
            except tk.TclError:
                pass
        
        self.interval_var.trace('w', validate_rakuten_interval)
        
        ttk.Label(main_frame, text="最小値: 1.0秒（API制限遵守）", foreground="red").grid(row=4, column=1, sticky=tk.W, pady=(0, 10))
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
    
    def save_settings(self):
        try:
            self.config.set("rakuten", "affiliate_id", self.affiliate_id_var.get().strip())
            self.config.set("rakuten", "api_key", self.api_key_var.get().strip())
            # 規約遵守のため最小1.0秒を強制
            interval = max(1.0, self.interval_var.get())
            self.config.set("rakuten", "search_interval", interval)
            
            if self.config.save_config():
                messagebox.showinfo("保存完了", "楽天設定を保存しました")
                self.dialog.destroy()
            else:
                messagebox.showerror("保存エラー", "設定の保存に失敗しました")
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存エラー: {str(e)}")


class GeneralSettingsDialog:
    def __init__(self, parent, config: Config):
        self.config = config
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
    
    def setup_dialog(self):
        self.dialog.title("全般設定")
        self.dialog.geometry("400x300")
        self.dialog.transient()
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # バックアップ作成
        self.backup_var = tk.BooleanVar(value=self.config.get("general", "create_backup", True))
        ttk.Checkbutton(main_frame, text="元ファイルのバックアップを作成", variable=self.backup_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 短縮URL使用
        self.short_url_var = tk.BooleanVar(value=self.config.get("general", "use_short_urls", False))
        short_url_check = ttk.Checkbutton(main_frame, text="デフォルトで短縮URLを使用", variable=self.short_url_var)
        short_url_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        if not SHORTENER_AVAILABLE:
            short_url_check.configure(state='disabled')
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def save_settings(self):
        try:
            self.config.set("general", "create_backup", self.backup_var.get())
            self.config.set("general", "use_short_urls", self.short_url_var.get())
            
            if self.config.save_config():
                messagebox.showinfo("保存完了", "全般設定を保存しました")
                self.dialog.destroy()
            else:
                messagebox.showerror("保存エラー", "設定の保存に失敗しました")
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存エラー: {str(e)}")


def main():
    """メイン関数"""
    root = tk.Tk()
    app = AffiliateApp(root)
    
    # 終了時の処理設定
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # アプリケーション開始
    root.mainloop()


if __name__ == "__main__":
    main()