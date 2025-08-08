// Firebase設定ファイル
// 本番環境では環境変数から取得することを推奨

const firebaseConfig = {
    // TODO: 実際のFirebaseプロジェクトを作成後、以下の値を更新してください
    apiKey: "YOUR_API_KEY_HERE",
    authDomain: "company-hate-meter.firebaseapp.com", 
    databaseURL: "https://company-hate-meter-default-rtdb.firebaseio.com",
    projectId: "company-hate-meter",
    storageBucket: "company-hate-meter.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef123456789012"
};

// Firebase初期化
firebase.initializeApp(firebaseConfig);

// Realtime Database参照
const database = firebase.database();

// エクスポート
window.firebaseApp = firebase;
window.database = database;

console.log('🔥 Firebase初期化完了');