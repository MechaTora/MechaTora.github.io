# B案：x-algo を審査対象から一時退避する手順

作成日: 2026-09-18
目的: mechatora.com の AdSense 承認を先に取るため、薄い x-algo を一時的に審査導線から外す。
承認後に全部戻す前提の、可逆的な変更のみ。

---

## 本体（mechatora-pages）側：対応済み

| ファイル | 変更 |
|---|---|
| `index.html` | 姉妹サイトの「🚀 Xアルゴリズム追跡」をコメントアウト |
| `earthquake-monitor/contact.html` | 「⚡ Xアルゴ」をコメントアウト |

どちらも `<!-- AdSense承認まで一時的に非表示` というコメントで囲んであるので、
承認後はコメント記号だけ消せば元に戻る。

---

## x-algo リポジトリ側：これから実施

### 1. 全ページを noindex にする

Next.js なら `app/layout.tsx`（または各 `generateMetadata`）の `metadata` に追加。

```ts
export const metadata: Metadata = {
  // ...既存の設定
  robots: {
    index: false,
    follow: false,
  },
};
```

ページ個別に `robots: 'index, follow'` を上書きしている箇所があれば、そちらも潰す。
実測では以下のページすべてに `<meta name="robots" content="index, follow">` が出ている。

- `/ja`, `/en`
- `/ja/about`, `/ja/contact`, `/ja/privacy`
- `/ja/article/*`（3本）
- `/ja/guide/*`（16本）
- `/ja/tag/*`

### 2. AdSense のアカウントメタタグを削除

全ページの `<head>` に以下が入っている。これを消す。

```html
<meta name="google-adsense-account" content="ca-pub-1184134440246706">
```

Next.js の場合は `metadata.other` か、`layout.tsx` の直書きのどちらか。

> 実測では **AdSense の広告ユニット（`adsbygoogle`）は見当たらない**。
> 入っているのは A8 のアフィリエイトバナー1枠のみ。
> つまり実質、このメタタグを消すだけで AdSense との紐付けは切れる。

### 3. sitemap.xml を送信解除

Search Console の x-algo プロパティで、送信済みサイトマップを削除。
サイト側の `sitemap.xml` 自体は消さなくてよい（noindex が効くので）。

### 4. ads.txt はそのままでよい

実測で正常に配信されている（`text/plain` で正しい1行）。触らない。

---

## odai リポジトリ側：ads.txt がまだ壊れている

4サブドメインのうち、**odai だけ `/ads.txt` が空レスポンス**（2026-09-18 実測）。
他の3つ（x-algo / sharonabi / kimochi）は修正済み。

`public/ads.txt` に以下1行を置いて、SPA のルーティングより先に静的配信されるようにする。

```
google.com, pub-1184134440246706, DIRECT, f08c47fec0942fa0
```

Content-Type が `text/plain` で返ることを、デプロイ後に必ず確認する。

---

## 承認が出たあとに戻す作業

1. 本体の2ファイルのコメントアウトを解除
2. x-algo の `robots` を `index, follow` に戻す
3. x-algo に `google-adsense-account` メタタグを戻す
4. Search Console で x-algo のサイトマップを再送信

ただし、戻す前に **x-algo の記事を増やしておくこと**。
2026-07 の監査時点で1本、現在3本。テンプレート構成が3本とも同一で、
「高影響」「5分で読める」も全記事同じ値になっている。
本体で同じ問題（読了時間が全記事「約10分」）を直したのと同じ手当てが要る。

---

## 検証コマンド（デプロイ後）

```powershell
# noindex が効いているか
curl.exe -s "https://x-algo.mechatora.com/ja" | Select-String "robots"

# AdSense メタタグが消えているか（何も出なければOK）
curl.exe -s "https://x-algo.mechatora.com/ja" | Select-String "adsense"

# odai の ads.txt
curl.exe -s -i "https://odai.mechatora.com/ads.txt"
```
