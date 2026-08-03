# 地震プッシュ通知 Worker — デプロイ手順

Cloudflare Workers + D1 で動きます。Supabaseは使いません。追加費用もかかりません。

> **先に1つだけ**：このフォルダはサイト公開ディレクトリの中にあります。公開されないよう、リポジトリのルートへ移動してからデプロイしてください。
> ```
> git mv earthquake-monitor/push-worker push-worker
> ```

---

## 手順（PowerShellで1行ずつ）

### 1. このフォルダへ移動して Cloudflare にログイン

```
cd push-worker
```

```
npx wrangler login
```

ブラウザが開くので承認してください。

### 2. D1データベースを作る

```
npx wrangler d1 create quake-push
```

表示された `database_id` を `wrangler.toml` の該当箇所に貼り付けます。

### 3. テーブルを作る

```
npx wrangler d1 execute quake-push --remote --file=./schema.sql
```

### 4. VAPID鍵を作る

```
npx web-push generate-vapid-keys
```

**Public Key と Private Key が表示されます。**

- **Public Key** … `wrangler.toml` の `VAPID_PUBLIC_KEY` と、`index.html` 内の `VAPID_PUBLIC_KEY` の2か所に貼る（公開して問題ない値です）
- **Private Key** … 次のコマンドで登録する。**ファイルには絶対に書かないでください**

```
npx wrangler secret put VAPID_PRIVATE_KEY
```

プロンプトが出たらPrivate Keyを貼り付けてEnter。

### 5. デプロイ

```
npx wrangler deploy
```

`https://quake-push.<あなたのサブドメイン>.workers.dev` というURLが表示されます。
この**URLを `index.html` の `API` 変数に貼り付けて**ください。

### 6. 動作確認

```
curl https://quake-push.<あなたのサブドメイン>.workers.dev/health
```

`{"ok":true}` が返ればWorkerは動いています。
そのあとサイトを開き、「通知を受け取る」→ 許可 → 「通知をオンにしました」と出れば登録完了です。

登録されたか確認するには：

```
npx wrangler d1 execute quake-push --remote --command "SELECT COUNT(*) FROM subscriptions"
```

---

## 仕組み

毎分のCron Triggerで気象庁の地震情報（P2P地震情報API経由）を確認し、最大震度が設定値以上なら、条件に合う購読者へ通知を送ります。同じ地震で二重に通知しないよう、送信済みIDを記録しています。

通知には**ペイロードを載せていません**。Web Pushのペイロード暗号化が不要になるためコードが小さく、CPU時間もほとんど使いません。通知を受け取ったService Worker（`sw.js`）が自分で最新情報を取得して通知文を組み立てます。取得に失敗しても「地震が発生しました」という通知は必ず表示されます。

## 無料枠について

- Workers：10万リクエスト/日、CPU 10ms/リクエスト
- D1：5GB、書き込み10万行/日
- Cron Triggers：1分間隔、無料プランで5個まで

毎分実行で1日1,440リクエスト。購読者が数千人規模になるまでは無料枠で足ります。超えたらWorkers有料プラン（月$5）で解決します。

## 調整できるところ

- `wrangler.toml` の `MIN_SCALE` … 通知を出す最小震度（30=震度3 / 40=震度4 / 45=震度5弱）。購読者個人のしきい値とは別に、システム全体の下限として働きます
- `ALLOW_ORIGIN` … CORSを許可するオリジン

## 注意

- 通知は**地震情報だけ**に使ってください。宣伝を混ぜると一斉に解除されます
- iPhoneは「ホーム画面に追加」しないと通知を受け取れません（サイト側で案内済み）
- 保存しているのはエンドポイントURLとしきい値・地域のみです。暗号鍵や個人情報は保存しません
