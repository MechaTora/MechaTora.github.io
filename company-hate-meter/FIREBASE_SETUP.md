# 🔥 Firebase設定ガイド

## 1. Firebaseプロジェクト作成

1. [Firebase Console](https://console.firebase.google.com/)にアクセス
2. 「プロジェクトを追加」をクリック
3. プロジェクト名：`company-hate-meter`
4. Google Analyticsを有効にする（推奨）

## 2. Realtime Database設定

1. Firebase Console で「Realtime Database」を選択
2. 「データベースを作成」をクリック
3. **テストモードで開始**を選択（後でルールを設定）
4. ロケーション：`asia-southeast1`（シンガポール）を推奨

## 3. セキュリティルール設定

Realtime Database のルールを以下に設定：

```json
{
  "rules": {
    "posts": {
      ".read": false,
      ".write": true,
      "$postId": {
        ".validate": "newData.hasChildren(['timestamp', 'location']) && newData.child('timestamp').isString()"
      }
    },
    "statistics": {
      ".read": true,
      ".write": true
    },
    "prefectures": {
      ".read": true,
      ".write": true,
      "$prefecture": {
        ".validate": "newData.hasChildren(['name', 'total', 'last24h'])"
      }
    },
    "ip_restrictions": {
      ".read": false,
      ".write": true,
      "$ipHash": {
        ".validate": "newData.hasChildren(['lastPost', 'count'])"
      }
    }
  }
}
```

## 4. Web アプリの設定

1. Firebase Console で「プロジェクトの設定」→「全般」
2. 「アプリ」セクションで Web アイコン（`</>`）をクリック
3. アプリのニックネーム：`company-hate-meter-web`
4. 「Firebase Hosting の設定」はスキップ（GitHub Pages使用のため）
5. 設定をコピーして `firebase-config.js` に貼り付け

## 5. firebase-config.js 更新

```javascript
const firebaseConfig = {
    apiKey: "YOUR_ACTUAL_API_KEY",
    authDomain: "company-hate-meter.firebaseapp.com",
    databaseURL: "https://company-hate-meter-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "company-hate-meter",
    storageBucket: "company-hate-meter.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef123456789012"
};
```

## 6. データベース構造

```
company-hate-meter-db/
├── posts/
│   └── post_timestamp_randomid/
│       ├── id: "post_timestamp_randomid"
│       ├── timestamp: "2025-08-08T12:00:00.000Z"
│       ├── location: {
│       │   ├── prefecture: "東京都"
│       │   ├── type: "manual" | "gps"
│       │   ├── lat: 35.67 (GPS時のみ)
│       │   └── lng: 139.65 (GPS時のみ)
│       │   }
│       ├── userAgent: "Mozilla/5.0..."
│       ├── hour: 12
│       ├── dayOfWeek: 1
│       └── isWeekend: false
├── statistics/
│   ├── totalPosts: 1500
│   ├── last24h: 234
│   ├── today: {
│   │   "2025-08-08": 123
│   │   }
│   └── lastUpdated: "2025-08-08T12:00:00.000Z"
├── prefectures/
│   └── 東京都/
│       ├── name: "東京都"
│       ├── total: 567
│       ├── last24h: 89
│       ├── today: {
│       │   "2025-08-08": 45
│       │   }
│       └── lastUpdated: "2025-08-08T12:00:00.000Z"
└── ip_restrictions/
    └── [ip_hash]/
        ├── lastPost: "2025-08-08T12:00:00.000Z"
        └── count: 1
```

## 7. 自動データクリーンアップ

Firebase Functions（有料プランが必要）で以下の処理を実装：

- 24時間以上古い投稿データを削除
- 24時間以上古いIP制限データを削除
- 月次統計の更新

## 8. 本番デプロイ前チェックリスト

- [ ] セキュリティルールが適切に設定されている
- [ ] API キーが正しく設定されている
- [ ] データベース構造が想定通りに動作する
- [ ] 自動削除機能が動作する
- [ ] 統計データが正しく更新される

## 9. 監視・メンテナンス

- Firebase Console で使用量を監視
- 月間読み取り・書き込み数を確認
- 無料枠（1GB転送、100同時接続）の範囲内で運用

## トラブルシューティング

### よくあるエラー

1. **Permission denied**: セキュリティルールを確認
2. **Network error**: Firebase設定とネットワーク接続を確認  
3. **Quota exceeded**: 使用量制限に達している

### デバッグ方法

```javascript
// ブラウザコンソールで確認
console.log('Firebase接続状態:', firebase.app().name);
console.log('Database URL:', firebase.app().options.databaseURL);
```

---

**更新日**: 2025年8月8日  
**作成者**: 会社行きたくないメーター開発チーム