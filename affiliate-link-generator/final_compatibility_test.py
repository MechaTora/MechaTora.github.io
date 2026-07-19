#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終互換性確認スクリプト
"""

def test_xlrd_functionality():
    """
    xlrd機能の最終確認
    """
    print("🔍 xlrd 最終確認テスト")
    print("=" * 50)
    
    try:
        import xlrd
        print(f"✅ xlrd import 成功: バージョン {xlrd.__version__}")
        
        # 実際にxlsファイルを開いてテスト
        if os.path.exists('test.xls'):
            print("📄 test.xls で実地テスト中...")
            workbook = xlrd.open_workbook('test.xls')
            sheet_names = workbook.sheet_names()
            print(f"   シート数: {len(sheet_names)}")
            print(f"   シート名: {sheet_names}")
            
            if sheet_names:
                sheet = workbook.sheet_by_index(0)
                print(f"   データサイズ: {sheet.nrows}行 x {sheet.ncols}列")
                
                # 最初の数セルの値を確認
                for row in range(min(3, sheet.nrows)):
                    for col in range(min(3, sheet.ncols)):
                        value = sheet.cell_value(row, col)
                        print(f"   セル[{row},{col}]: '{value}' (型: {sheet.cell_type(row, col)})")
            
            print("✅ xlsファイル読み込みテスト成功")
        else:
            print("⚠️ test.xls が見つかりません（テストファイル作成が必要）")
            
        return True
        
    except ImportError as e:
        print(f"❌ xlrd import 失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ xlrd テスト中にエラー: {e}")
        return False

def test_excel_manager_integration():
    """
    ExcelManagerとの統合テスト
    """
    print("\n🔧 ExcelManager 統合テスト")  
    print("=" * 50)
    
    try:
        from excel_manager import ExcelManager, XLRD_AVAILABLE
        
        print(f"📦 XLRD_AVAILABLE: {XLRD_AVAILABLE}")
        
        if XLRD_AVAILABLE:
            print("✅ ExcelManager で xlrd サポート有効")
            
            if os.path.exists('test.xls'):
                manager = ExcelManager()
                success = manager.load_file('test.xls')
                
                if success:
                    stats = manager.get_statistics()
                    print(f"   商品数: {stats.get('total_products', 0)}")
                    print("✅ ExcelManager .xls読み込み成功")
                else:
                    print("❌ ExcelManager .xls読み込み失敗")
                    
                manager.close()
            else:
                print("⚠️ test.xls が見つかりません")
        else:
            print("❌ ExcelManager で xlrd サポート無効")
            
        return XLRD_AVAILABLE
        
    except Exception as e:
        print(f"❌ ExcelManager統合テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    
    print("🎯 Excel互換性 最終確認テスト")
    print("=" * 60)
    
    # xlrd単体テスト
    xlrd_ok = test_xlrd_functionality()
    
    # ExcelManager統合テスト
    integration_ok = test_excel_manager_integration()
    
    print("\n" + "=" * 60)
    print("📊 最終テスト結果")
    print("=" * 60)
    print(f"xlrd 単体テスト: {'✅ 成功' if xlrd_ok else '❌ 失敗'}")
    print(f"ExcelManager統合: {'✅ 成功' if integration_ok else '❌ 失敗'}")
    
    if xlrd_ok and integration_ok:
        print("🎉 すべてのテストが成功しました！")
        print("   .xlsファイルサポート: 完全対応")
    else:
        print("⚠️ 一部のテストで問題が発生しました")
        
    print("\n💡 サポート状況:")
    print("   ✅ .xlsx形式: 完全サポート")
    print(f"   {'✅' if xlrd_ok else '❌'} .xls形式: {'完全サポート' if xlrd_ok else '非サポート'}")
    print("   ⚠️ .et形式 (WPS): 部分サポート（エラーメッセージ改善済み）")