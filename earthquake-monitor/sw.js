/* 地震モニター Service Worker
 * ①オフライン用シェルのキャッシュ ②Web Push受信・表示 ③通知タップの着地制御
 */
const VERSION = 'quake-v1';
const SHELL = `shell-${VERSION}`;

const ASSETS = [
  '/earthquake-monitor/',
  '/earthquake-monitor/offline.html',
  '/earthquake-monitor/manifest.json',
  '/earthquake-monitor/icons/icon-192.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL)
      .then((c) => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
      .catch((e) => console.warn('[sw] precache', e))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 地震APIは常に最新を優先し、失敗時のみ直近キャッシュ
  if (url.hostname === 'api.p2pquake.net') {
    event.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(SHELL).then((c) => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // ページ遷移はネット優先、オフライン時のみ代替ページ
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/earthquake-monitor/offline.html'))
    );
    return;
  }

  event.respondWith(caches.match(req).then((c) => c || fetch(req)));
});

// ---- Push受信 ----
// 通知にペイロードは載っていない（暗号化不要にするための設計）。
// ここで最新の地震情報を取得し、通知文を組み立てる。取得に失敗しても必ず通知は出す。
const SCALE_LABEL = { 10:'1', 20:'2', 30:'3', 40:'4', 45:'5弱', 46:'5弱以上', 50:'5強', 55:'6弱', 60:'6強', 70:'7' };

self.addEventListener('push', (event) => {
  event.waitUntil((async () => {
    let title = '地震が発生しました';
    let body = '最新の地震情報を確認 →';
    let tag = 'quake';
    let strong = false;

    try {
      const res = await fetch('https://api.p2pquake.net/v2/history?codes=551&limit=1', { cache: 'no-store' });
      const [q] = await res.json();
      const e = q && q.earthquake;
      if (e) {
        const shindo = SCALE_LABEL[e.maxScale] || '';
        const place = (e.hypocenter && e.hypocenter.name) || '日本';
        const mag = (e.hypocenter && e.hypocenter.magnitude > 0) ? `（M${e.hypocenter.magnitude}）` : '';
        const time = (e.time || '').split(' ')[1] || '';
        title = shindo ? `【震度${shindo}】${place}で地震${mag}` : `${place}で地震${mag}`;
        body = time
          ? `${time}頃発生。各地の震度と震源を確認 →`
          : '各地の震度と震源を確認 →';
        tag = q.id || 'quake';
        strong = ['45','5弱','50','5強','55','6弱','60','6強','70','7'].includes(String(e.maxScale)) || e.maxScale >= 45;
      }
    } catch (_) { /* 取得失敗時は既定の文面で通知する */ }

    await self.registration.showNotification(title, {
      body,
      icon: '/earthquake-monitor/icons/icon-192.png',
      badge: '/earthquake-monitor/icons/badge-72.png',
      tag,
      renotify: true,
      requireInteraction: strong,
      vibrate: [200, 100, 200],
      data: { url: '/earthquake-monitor/?utm_source=push' },
    });
  })());
});

// ---- 通知タップ ----
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || '/earthquake-monitor/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((list) => {
      for (const c of list) {
        if (c.url.includes('/earthquake-monitor/') && 'focus' in c) {
          c.navigate(target);
          return c.focus();
        }
      }
      return self.clients.openWindow(target);
    })
  );
});
