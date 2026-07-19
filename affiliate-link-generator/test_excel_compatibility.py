#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel互換性テストスクリプト
様々な形式のExcelファイルの読み込みをテスト
"""

import os
import sys
import traceback
from excel_manager import ExcelManager

def test_excel_file(file_path, description):
    """
    Excelファイルの読み込みテスト
    """
    print(f"\n{'='*60}")
    print(f"📄 テスト: {description}")
    print(f"📁 ファイル: {file_path}")
    print(f"{'='*60}")
    
    # ファイルの存在確認
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return False
    
    # ファイル情報表示
    file_size = os.path.getsize(file_path)
    print(f"📊 ファイルサイズ: {file_size / 1024:.1f} KB")
    
    # ExcelManagerでテスト
    manager = ExcelManager()
    
    try:
        success = manager.load_file(file_path)
        
        if success:
            print("✅ ファイル読み込み成功!")
            
            # 統計情報表示
            stats = manager.get_statistics()
            if stats:
                print(f"📈 統計情報:")
                print(f"   商品総数: {stats.get('total_products', 0)}")
                print(f"   Amazonリンク: {stats.get('amazon_links', 0)}")
                print(f"   楽天リンク: {stats.get('rakuten_links', 0)}")
            
            # 商品データの一部を表示
            products = manager.get_products()
            if products:
                print(f"📝 商品データサンプル（最初の3件）:")
                for i, product in enumerate(products[:3], 1):
                    print(f"   {i}. {product.get('product_name', 'N/A')}")
            
            return True
        else:
            print("❌ ファイル読み込み失敗")
            return False
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        traceback.print_exc()
        return False
    
    finally:
        manager.close()

def main():
    """
    メイン関数
    """
    print("🔍 Excel互換性テスト開始")
    print("=" * 60)
    
    # テスト対象ファイルリスト
    test_files = [
        ("sample_products.xlsx", "サンプルファイル（xlsx）"),
        ("test.xlsx", "テスト用xlsxファイル"),
        ("test.xls", "テスト用xlsファイル"), 
        ("test.et", "WPS Spreadsheetsファイル"),
        ("a.xlsx", "問題のあったファイル"),
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for file_name, description in test_files:
        file_path = os.path.join(os.getcwd(), file_name)
        if test_excel_file(file_path, description):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 テスト結果サマリー")
    print(f"{'='*60}")
    print(f"成功: {success_count}/{total_count} ファイル")
    print(f"失敗: {total_count - success_count}/{total_count} ファイル")
    
    if success_count == total_count:
        print("🎉 すべてのテストが成功しました！")
    else:
        print("⚠️ 一部のファイルで問題が発生しました")
    
    # 追加の互換性テスト
    print(f"\n{'='*60}")
    print("🔧 追加の互換性チェック")
    print(f"{'='*60}")
    
    # openpyxlバージョン確認
    try:
        import openpyxl
        print(f"📦 openpyxl バージョン: {openpyxl.__version__}")
    except Exception as e:
        print(f"❌ openpyxl 情報取得エラー: {e}")
    
    # Pythonバージョン確認
    print(f"🐍 Python バージョン: {sys.version}")

if __name__ == "__main__":
    main()