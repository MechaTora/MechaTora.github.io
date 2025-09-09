#!/usr/bin/env python3
"""
すべてのファイル形式の包括的テスト
"""

from excel_manager import ExcelManager, XLRD_AVAILABLE
import os

def comprehensive_test():
    """
    全ファイル形式の包括的テスト
    """
    print("🔍 包括的Excel互換性テスト")
    print("=" * 60)
    
    # テスト対象ファイル
    test_files = [
        ('sample_products.xlsx', '.xlsx形式', '標準Excel形式'),
        ('test.xlsx', '.xlsx形式', '作成テストファイル'),
        ('a.xlsx', '.xlsx形式', '新しい正常ファイル'),
        ('test.xls', '.xls形式', '古いExcel形式'),
        ('wps_test.xls', '.xls形式', 'WPS風xlsファイル'),
        ('wps_test.xlsx', 'WPS偽装', '.xlsを.xlsxにリネームしたWPSファイル'),
        ('test.et', '.et形式', 'WPS専用形式（部分サポート）')
    ]
    
    success_count = 0
    total_count = 0
    results = []
    
    for file_path, file_type, description in test_files:
        if not os.path.exists(file_path):
            continue
            
        total_count += 1
        print(f"\n📄 テスト {total_count}: {description}")
        print(f"📁 ファイル: {file_path} ({file_type})")
        print("-" * 50)
        
        manager = ExcelManager()
        
        try:
            success = manager.load_file(file_path)
            
            if success:
                products = manager.get_products()
                stats = manager.get_statistics()
                success_count += 1
                
                result = {
                    'file': file_path,
                    'type': file_type,
                    'status': '✅ 成功',
                    'products': stats.get('total_products', 0),
                    'amazon_links': stats.get('amazon_links', 0),
                    'rakuten_links': stats.get('rakuten_links', 0)
                }
                
                print(f"🎯 結果: ✅ 成功")
                print(f"   商品数: {result['products']}")
                print(f"   Amazonリンク: {result['amazon_links']}")
                print(f"   楽天リンク: {result['rakuten_links']}")
                
                # 商品名の一部を表示
                for i, product in enumerate(products[:2], 1):
                    print(f"   {i}. {product.get('product_name', 'N/A')}")
                
            else:
                result = {
                    'file': file_path,
                    'type': file_type,
                    'status': '❌ 失敗',
                    'products': 0,
                    'amazon_links': 0,
                    'rakuten_links': 0
                }
                print(f"🎯 結果: ❌ 失敗")
                
            results.append(result)
            
        except Exception as e:
            print(f"🎯 結果: 💥 例外エラー - {str(e)}")
            results.append({
                'file': file_path,
                'type': file_type,
                'status': f'💥 エラー: {str(e)}',
                'products': 0,
                'amazon_links': 0,
                'rakuten_links': 0
            })
        
        finally:
            manager.close()
    
    # 総合結果表示
    print("\n" + "=" * 60)
    print("📊 包括的テスト結果サマリー")
    print("=" * 60)
    
    print(f"📈 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"📦 xlrd サポート: {'✅ 利用可能' if XLRD_AVAILABLE else '❌ 未インストール'}")
    
    print("\n📋 詳細結果:")
    total_products = 0
    total_amazon = 0
    total_rakuten = 0
    
    for result in results:
        status_icon = "✅" if "成功" in result['status'] else "❌" if "失敗" in result['status'] else "💥"
        print(f"  {status_icon} {result['file']:<20} ({result['type']:<10}) - {result['products']}商品")
        
        if "成功" in result['status']:
            total_products += result['products']
            total_amazon += result['amazon_links']
            total_rakuten += result['rakuten_links']
    
    print(f"\n📊 累計データ:")
    print(f"  総商品数: {total_products}")
    print(f"  Amazonリンク: {total_amazon}")
    print(f"  楽天リンク: {total_rakuten}")
    
    # 対応状況のまとめ
    print(f"\n💡 ファイル形式対応状況:")
    format_support = {
        '.xlsx': '✅ 完全対応',
        '.xls': '✅ 完全対応（xlrd使用）' if XLRD_AVAILABLE else '❌ xlrd未インストール',
        'WPS偽装': '✅ 完全対応（自動検出+xlrd変換）' if XLRD_AVAILABLE else '❌ xlrd未インストール',
        '.et': '⚠️ エラーガイダンス（一部読み込み可能）'
    }
    
    for fmt, status in format_support.items():
        print(f"  {status:<35} {fmt}")

if __name__ == "__main__":
    comprehensive_test()