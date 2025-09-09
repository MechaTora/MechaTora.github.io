#!/usr/bin/env python3
"""
WPSテスト用のCompound Documentファイル作成
"""

import xlwt

def create_wps_style_file():
    """
    WPS形式に近い.xlsファイルを作成
    """
    print("📄 WPS形式テスト用ファイル作成中...")
    
    # xlwtで.xls形式ファイルを作成（WPS読み込みテスト用）
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('商品リスト')
    
    # ヘッダー行
    worksheet.write(0, 0, '商品番号')
    worksheet.write(0, 1, '商品名')
    worksheet.write(0, 2, 'Amazonリンク')
    worksheet.write(0, 3, '楽天リンク')
    
    # WPS風の商品データ
    wps_products = [
        'WPSで作成した商品1',
        'Compound Document形式テスト',
        'xlrd読み込み確認商品',
        'WPS互換性テスト商品',
        'Office互換ソフト商品'
    ]
    
    for i, product in enumerate(wps_products):
        worksheet.write(i+1, 0, i+1)
        worksheet.write(i+1, 1, product)
        # 一部に既存データを追加
        if i == 0:
            worksheet.write(i+1, 2, 'https://amazon.co.jp/test')
    
    # wps_test.xlsとして保存（拡張子は.xlsだがWPS風）
    workbook.save('wps_test.xls')
    
    print("✅ wps_test.xls 作成完了")
    return 'wps_test.xls'

def rename_to_wps_extension(xls_file):
    """
    .xlsファイルを.xlsx拡張子にリネーム（WPS偽装）
    """
    import shutil
    
    wps_xlsx_file = 'wps_test.xlsx'
    shutil.copy2(xls_file, wps_xlsx_file)
    print(f"✅ {wps_xlsx_file} 作成完了（WPS偽装ファイル）")
    return wps_xlsx_file

if __name__ == "__main__":
    print("🔧 WPS形式テストファイル作成ツール")
    print("=" * 50)
    
    # .xlsファイル作成
    xls_file = create_wps_style_file()
    
    # WPS偽装ファイル作成（.xlsを.xlsxにリネーム）
    wps_xlsx_file = rename_to_wps_extension(xls_file)
    
    print("\n📋 作成されたファイル:")
    import os
    for file in [xls_file, wps_xlsx_file]:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size / 1024:.1f} KB)")
            
    print("\n💡 テスト方法:")
    print(f"1. {xls_file} - 正常な.xls形式として読み込みテスト")
    print(f"2. {wps_xlsx_file} - WPS偽装ファイルとして読み込みテスト")