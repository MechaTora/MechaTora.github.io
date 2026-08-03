/**
 * 地震モニター プッシュ通知 Worker（Cloudflare Workers + D1）
 *
 * 役割
 *   1. POST /subscribe   … 購読の登録・更新（しきい値・地域）
 *   2. POST /unsubscribe … 購読の解除
 *   3. cron（毎分）       … 気象庁の地震情報をP2P経由で取得し、条件に合う購読者へ通知
 *
 * 設計メモ
 *   通知に「ペイロードを載せない」方式を採用している。
 *   Web Pushのペイロード暗号化(aes128gcm)が不要になるため、必要なのはVAPID署名だけで済み、
 *   コード量とCPU時間が大きく減る。通知を受け取ったService Worker側が、
 *   自分で最新の地震情報を取得して通知文を組み立てる（sw.jsのpushハンドラ）。
 */

const P2P_API = 'https://api.p2pquake.net/v2/history?codes=551&limit=1';

// 都道府県 → 地域（購読者の地域フィルタ用）
const REGION_OF = {
  '北海道': 'hokkaido',
  '青森県': 'tohoku', '岩手県': 'tohoku', '宮城県': 'tohoku', '秋田県': 'tohoku', '山形県': 'tohoku', '福島県': 'tohoku',
  '茨城県': 'kanto', '栃木県': 'kanto', '群馬県': 'kanto', '埼玉県': 'kanto', '千葉県': 'kanto', '東京都': 'kanto', '神奈川県': 'kanto',
  '新潟県': 'chubu', '富山県': 'chubu', '石川県': 'chubu', '福井県': 'chubu', '山梨県': 'chubu', '長野県': 'chubu',
  '岐阜県': 'chubu', '静岡県': 'chubu', '愛知県': 'chubu',
  '三重県': 'kinki', '滋賀県': 'kinki', '京都府': 'kinki', '大阪府': 'kinki', '兵庫県': 'kinki', '奈良県': 'kinki', '和歌山県': 'kinki',
  '鳥取県': 'chugoku', '島根県': 'chugoku', '岡山県': 'chugoku', '広島県': 'chugoku', '山口県': 'chugoku',
  '徳島県': 'shikoku', '香川県': 'shikoku', '愛媛県': 'shikoku', '高知県': 'shikoku',
  '福岡県': 'kyushu', '佐賀県': 'kyushu', '長崎県': 'kyushu', '熊本県': 'kyushu', '大分県': 'kyushu',
  '宮崎県': 'kyushu', '鹿児島県': 'kyushu', '沖縄県': 'kyushu',
};

// ---------- 共通 ----------
const b64urlToBytes = (s) => {
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (s.length % 4)) % 4);
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
};
const bytesToB64url = (buf) =>
  btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

function cors(env) {
  return {
    'Access-Control-Allow-Origin': env.ALLOW_ORIGIN || '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}
const json = (obj, env, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors(env) },
  });

// ---------- VAPID ----------
// web-pushが出力するbase64url形式の鍵ペアからCryptoKeyを組み立てる
async function importVapidKey(publicKeyB64, privateKeyB64) {
  const pub = b64urlToBytes(publicKeyB64);   // 65バイト: 0x04 || X(32) || Y(32)
  const priv = b64urlToBytes(privateKeyB64); // 32バイト
  const jwk = {
    kty: 'EC',
    crv: 'P-256',
    x: bytesToB64url(pub.slice(1, 33)),
    y: bytesToB64url(pub.slice(33, 65)),
    d: bytesToB64url(priv),
    ext: true,
  };
  return crypto.subtle.importKey('jwk', jwk, { name: 'ECDSA', namedCurve: 'P-256' }, false, ['sign']);
}

// aud（プッシュサービスのオリジン）ごとにJWTを作る。同一オリジン分は使い回せる。
async function makeVapidJwt(key, audience, subject) {
  const header = bytesToB64url(new TextEncoder().encode(JSON.stringify({ typ: 'JWT', alg: 'ES256' })));
  const payload = bytesToB64url(new TextEncoder().encode(JSON.stringify({
    aud: audience,
    exp: Math.floor(Date.now() / 1000) + 12 * 60 * 60,
    sub: subject,
  })));
  const data = new TextEncoder().encode(`${header}.${payload}`);
  const sig = await crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, key, data);
  return `${header}.${payload}.${bytesToB64url(sig)}`;
}

// ---------- 通知送信 ----------
async function sendBarePush(endpoint, key, publicKey, subject, jwtCache) {
  const aud = new URL(endpoint).origin;
  if (!jwtCache[aud]) jwtCache[aud] = await makeVapidJwt(key, aud, subject);
  return fetch(endpoint, {
    method: 'POST',
    headers: {
      TTL: '600',
      Urgency: 'high',
      'Content-Length': '0',
      Authorization: `vapid t=${jwtCache[aud]}, k=${publicKey}`,
    },
  });
}

// ---------- HTTPハンドラ ----------
async function handleSubscribe(request, env) {
  const body = await request.json().catch(() => null);
  const endpoint = body?.subscription?.endpoint;
  if (!endpoint || !/^https:\/\//.test(endpoint)) return json({ error: 'invalid subscription' }, env, 400);

  const minScale = [30, 40, 45].includes(Number(body?.prefs?.minScale)) ? Number(body.prefs.minScale) : 40;
  const region = String(body?.prefs?.region || 'all').slice(0, 20);
  const now = Math.floor(Date.now() / 1000);

  await env.DB.prepare(
    `INSERT INTO subscriptions (endpoint, min_scale, region, created_at)
     VALUES (?1, ?2, ?3, ?4)
     ON CONFLICT(endpoint) DO UPDATE SET min_scale = ?2, region = ?3`
  ).bind(endpoint, minScale, region, now).run();

  return json({ ok: true }, env, 201);
}

async function handleUnsubscribe(request, env) {
  const body = await request.json().catch(() => null);
  const endpoint = body?.endpoint;
  if (!endpoint) return json({ error: 'endpoint required' }, env, 400);
  await env.DB.prepare('DELETE FROM subscriptions WHERE endpoint = ?1').bind(endpoint).run();
  return json({ ok: true }, env);
}

// ---------- cron本体 ----------
async function checkAndNotify(env) {
  const res = await fetch(P2P_API, { cf: { cacheTtl: 0 } });
  if (!res.ok) return;
  const [quake] = await res.json();
  if (!quake || !quake.earthquake) return;

  const maxScale = Number(quake.earthquake.maxScale || -1);
  const minScale = Number(env.MIN_SCALE || 30);
  if (maxScale < minScale) return;

  // 既に通知済みなら何もしない
  const dup = await env.DB.prepare('SELECT 1 FROM sent_quakes WHERE quake_id = ?1').bind(quake.id).first();
  if (dup) return;

  // 揺れた地域を集計
  const prefs = new Set((quake.points || []).map((p) => p.pref));
  const regions = new Set([...prefs].map((p) => REGION_OF[p]).filter(Boolean));
  const place = quake.earthquake.hypocenter?.name || '日本';

  // 先に記録しておく（同時実行での二重送信を防ぐ）
  await env.DB.prepare(
    'INSERT OR IGNORE INTO sent_quakes (quake_id, sent_at, max_scale, place) VALUES (?1, ?2, ?3, ?4)'
  ).bind(quake.id, Math.floor(Date.now() / 1000), maxScale, place).run();

  // 対象購読者を抽出
  const { results } = await env.DB.prepare(
    'SELECT endpoint, region FROM subscriptions WHERE min_scale <= ?1'
  ).bind(maxScale).all();
  const targets = (results || []).filter((r) => r.region === 'all' || regions.has(r.region));
  if (!targets.length) return;

  const key = await importVapidKey(env.VAPID_PUBLIC_KEY, env.VAPID_PRIVATE_KEY);
  const jwtCache = {};
  const dead = [];

  // 一度に投げすぎないよう小分けに送る
  for (let i = 0; i < targets.length; i += 50) {
    const chunk = targets.slice(i, i + 50);
    const rs = await Promise.allSettled(
      chunk.map((t) => sendBarePush(t.endpoint, key, env.VAPID_PUBLIC_KEY, env.VAPID_SUBJECT, jwtCache))
    );
    rs.forEach((r, j) => {
      if (r.status === 'fulfilled' && (r.value.status === 404 || r.value.status === 410)) {
        dead.push(chunk[j].endpoint); // 失効した購読
      }
    });
  }

  // 失効分の掃除
  for (const e of dead) {
    await env.DB.prepare('DELETE FROM subscriptions WHERE endpoint = ?1').bind(e).run();
  }

  // 古い記録の整理（30日より前）
  await env.DB.prepare('DELETE FROM sent_quakes WHERE sent_at < ?1')
    .bind(Math.floor(Date.now() / 1000) - 30 * 86400).run();
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors(env) });
    if (request.method === 'POST' && pathname === '/subscribe') return handleSubscribe(request, env);
    if (request.method === 'POST' && pathname === '/unsubscribe') return handleUnsubscribe(request, env);
    if (pathname === '/health') return json({ ok: true }, env);
    return json({ error: 'not found' }, env, 404);
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(checkAndNotify(env));
  },
};
