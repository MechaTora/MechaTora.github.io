@echo off
chcp 65001 > nul

echo 📄 サンプルExcelファイルを作成します...
echo.

python -c "
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# 新規ワークブック作成
wb = openpyxl.Workbook()
ws = wb.active
ws.title = '商品リスト'

# ヘッダー設定
headers = ['商品番号', '商品名', 'Amazonリンク', '楽天リンク']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=11)
    cell.fill = PatternFill(start_color='E6E6FA', end_color='E6E6FA', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center')

# サンプルデータ
sample_products = [
    'iPhone 15 Pro 128GB',
    'ワイヤレスマウス Bluetooth',  
    'Python プログラミング本',
    'コーヒーメーカー 全自動',
    'Bluetoothスピーカー',
    'ノートパソコン 15インチ',
    'ワイヤレスイヤホン',
    'デスクチェア オフィス',
    'LED デスクライト',
    'USB-C ハブ'
]

for row, product in enumerate(sample_products, 2):
    ws.cell(row=row, column=1, value=row-1)  # 商品番号
    ws.cell(row=row, column=2, value=product)  # 商品名

# 列幅調整
ws.column_dimensions['A'].width = 10
ws.column_dimensions['B'].width = 35
ws.column_dimensions['C'].width = 30
ws.column_dimensions['D'].width = 30

# 保存
wb.save('サンプル商品リスト.xlsx')
print('✅ サンプルExcelファイル「サンプル商品リスト.xlsx」を作成しました')
print('📝 このファイルをテンプレートとして使用してください')
"

pause