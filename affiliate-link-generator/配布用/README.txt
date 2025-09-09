==========================================
🛍️ アフィリエイトリンク自動生成ツール v1.0
==========================================

【🚀 クイックスタート】
1. START_APP.bat をダブルクリック
2. エラーが出たら AUTO_SETUP.bat → FORCE_FIX_TKINTER.bat の順に実行
3. sample_products.xlsx を参考にExcelファイルを作成
4. アプリでファイルを読み込んでリンクを生成

==========================================

【📋 初回セットアップ（必須）】

1. AUTO_SETUP.bat を実行
   → 必要なPythonパッケージを自動インストール

2. FORCE_FIX_TKINTER.bat を実行  
   → tkinter（GUI）の問題を修復

3. CHROME_AUTO_INSTALL.bat を実行（Amazon検索を使う場合）
   → Google Chrome + ChromeDriverを自動設定

4. START_APP.bat で起動テスト

==========================================

【📱 アプリケーションの使用方法】

1. 【Excelファイル準備】
   - sample_products.xlsx を参考に作成
   - B列（商品名列）に検索したい商品名を入力
   - A列：商品番号、C列：Amazon結果、D列：楽天結果

2. 【アプリ起動】
   - START_APP.bat をダブルクリック

3. 【設定】
   - 「設定」メニューを開く
   - Amazon Associate ID を入力（Amazon検索用）
   - 楽天アフィリエイトID を入力（楽天検索用）

4. 【ファイル処理】
   - 「ファイルを選択」でExcelファイルを選択
   - 検索エンジン（Amazon/楽天）を選択
   - 「処理開始」をクリック
   - 自動でリンクがExcelファイルに追加される

==========================================

【📁 フォルダ構成】

📁 source_code/     - アプリケーション本体
📁 config/          - 設定ファイル保存場所
📄 sample_products.xlsx - サンプルExcelファイル

起動ファイル：
📄 START_APP.bat    - メイン起動（推奨）
📄 SAFE_START.bat   - 代替起動方法
📄 CLICK_ME.bat     - シンプル起動

セットアップ：
📄 AUTO_SETUP.bat           - 自動セットアップ
📄 FORCE_FIX_TKINTER.bat    - tkinter修復
📄 CHROME_AUTO_INSTALL.bat  - Chrome自動設定

その他：
📄 CREATE_SAMPLE.bat - サンプルファイル再作成
📄 start_app.py     - Python起動スクリプト
📄 auto_setup.py    - 自動セットアップスクリプト

==========================================

【⚠️ トラブルシューティング】

🔧 起動しない場合：
1. START_APP.bat → SAFE_START.bat → CLICK_ME.bat の順で試す
2. AUTO_SETUP.bat を実行してパッケージ再インストール
3. FORCE_FIX_TKINTER.bat でGUI問題を修復

🔧 「tkinter」エラー:
- FORCE_FIX_TKINTER.bat を実行
- それでもダメならPython再インストール（tcl/tk含む）

🔧 「Chrome/ChromeDriver」エラー:
- CHROME_AUTO_INSTALL.bat を実行
- 楽天検索のみでも利用可能

🔧 文字化け・コマンド認識エラー:
- START_APP.bat を使用（最も安全）
- コマンドプロンプトの文字エンコーディング問題

🔧 Excel読み込みエラー:
- WPS Office/LibreOfficeファイルも自動対応
- sample_products.xlsx と同じ形式で作成

==========================================

【✅ サポートされるファイル形式】
- Excel .xlsx ファイル
- Excel .xls ファイル（古い形式）
- WPS Office ファイル（自動検出・変換）
- LibreOffice Calc ファイル

【✅ 主要機能】
- Amazon商品検索 + アフィリエイトリンク生成
- 楽天商品検索 + アフィリエイトリンク生成
- 短縮URL生成（オプション）
- バッチ処理（複数商品一括処理）
- Excel自動更新・保存
- エラーハンドリング・続行機能

==========================================

【💡 使用のコツ】

1. 商品名は具体的に記述（「iPhone 15 Pro 128GB」など）
2. 検索間隔を調整してサイト負荷を軽減
3. Amazon検索にはChromeが必要、楽天は不要
4. 処理中は他の作業可能（バックグラウンド実行）
5. エラーが出ても楽天/Amazonどちらか片方だけでも動作

==========================================