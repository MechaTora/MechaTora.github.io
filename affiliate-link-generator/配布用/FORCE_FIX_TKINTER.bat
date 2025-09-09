@echo off
echo ========================================
echo 🔧 強制的にtkinter問題を修復します
echo ========================================
echo.

echo 1. 代替パッケージインストール中...
python -m pip install --upgrade pip
python -m pip install tk
python -m pip install tkinter-page
echo.

echo 2. Python環境診断中...
python -c "import sys; print('Python:', sys.version)"
python -c "try: import tkinter; print('✅ tkinter OK'); except: print('❌ tkinter NG')"
echo.

echo 3. tkinterテスト...
python -c "
try:
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    print('✅ tkinter GUI テスト成功')
except Exception as e:
    print('❌ tkinter GUI テスト失敗:', e)
    print()
    print('🔧 Python再インストールが必要です:')
    print('https://www.python.org/downloads/')
    print('インストール時に tcl/tk and IDLE にチェック！')
    import webbrowser
    webbrowser.open('https://www.python.org/downloads/')
"
echo.

echo 4. アプリケーション起動テスト...
python source_code/run_app.py
pause