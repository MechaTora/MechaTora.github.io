# WSL環境でのGUIアプリ起動方法

## 問題
WSL環境では `tkinter` が標準でインストールされておらず、GUIアプリが起動できません。

## 解決方法

### 1. tkinter のインストール
```bash
sudo apt update
sudo apt install -y python3-tk
```

### 2. X11フォワーディングの設定（必要な場合）
WSL2でGUIを表示するには、X11サーバーが必要です。

#### Windows 11の場合
- WSLg が標準でサポートされているので追加設定不要

#### Windows 10の場合
1. **VcXsrv** または **Xming** をインストール
2. 環境変数を設定：
```bash
echo 'export DISPLAY=:0' >> ~/.bashrc
source ~/.bashrc
```

### 3. アプリケーション起動
```bash
python3 run_app.py
```

## Windows版の推奨
WSLでの環境構築が複雑な場合は、**Windows版Python**での実行を推奨します：

1. Windows版Python をインストール
2. コマンドプロンプトで実行：
```cmd
python run_app.py
```

## トラブルシューティング
- GUIが表示されない → X11設定を確認
- モジュールエラー → pip install で依存関係を解決
- 権限エラー → sudo 権限を確認