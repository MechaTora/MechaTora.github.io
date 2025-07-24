# 📊 Stock Monitor Pro

**日本株リアルタイム監視システム** - IT系プロ仕様UI with AdSense

## 🌐 Live Demo

**https://mechatora.github.io/stock-monitor-pro/**

## ✨ 特徴

- 📊 **日本株25銘柄リアルタイム監視**
- ⏰ **取引時間限定更新** (前場・後場のみ)
- 🔒 **セキュアAPIプロキシ** (API Key保護)
- 🎨 **モダンIT系UI** (サイバーパンク風)
- 📱 **完全レスポンシブ** (モバイルファースト)
- 💰 **AdSense統合済み**
- 🔍 **SEO完全対応**

## 🚀 クイックスタート

### 1. Alpha Vantage API Key取得
[Alpha Vantage](https://www.alphavantage.co/) で無料API Key取得

### 2. 環境設定
```bash
# .envファイル作成
cp .env.example .env
# .envファイルを編集してAPI Keyを設定
```

### 3. サーバー起動
```bash
# 依存関係インストール
pip install -r requirements_jp_stock.txt

# サーバー起動
python jp_stock_trading_hours.py
```

### 4. アクセス
- サーバー確認: http://localhost:5000
- メイン画面: index.html をブラウザで開く

## 📊 監視銘柄 (25銘柄)

**大型株**: トヨタ、ソフトバンクG、ソニーG、KDDI、三菱UFJ  
**テック**: キーエンス、東京エレクトロン、楽天、ファナック  
**製造**: 日立、パナソニック、キヤノン、ダイキン  
**その他**: 任天堂、武田、伊藤忠、ファストリなど

## ⚙️ システム仕様

- **API使用量**: 450回/日 (制限内)
- **更新間隔**: 15分間隔
- **稼働時間**: 平日取引時間のみ

## 🛡️ セキュリティ

- API Keyは環境変数で完全隠蔽
- サーバーサイドプロキシでフロントエンド保護
- GitHub公開でも安全

## 📱 対応環境

- Chrome/Edge (推奨)
- Firefox, Safari
- iOS/Android対応

---

📊 **Stock Monitor Pro** | [MechaTora Apps](https://mechatora.github.io/)