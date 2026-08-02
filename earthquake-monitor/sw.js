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
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (_) {}

  const shindo = data.shindo || '';
  const place = data.place || '地震情報';
  const mag = data.mag ? `（M${data.mag}）` : '';
  const time = data.time || '';

  const title = shindo ? `【震度${shindo}】${place}で地震${mag}` : `${place}${mag}`;
  const body = time
    ? `${time}頃、${place}で最大震度${shindo}を観測。詳しい震源・各地の震度を確認 →`
    : '最新の地震情報を確認 →';

  event.waitUntil(self.registration.showNotification(title, {
    body,
    icon: '/earthquake-monitor/icons/icon-192.png',
    badge: '/earthquake-monitor/icons/badge-72.png',
    tag: data.id || 'quake',
    renotify: true,
    requireInteraction: Number(shindo) >= 5,
    vibrate: [200, 100, 200],
    data: { url: data.url || '/earthquake-monitor/?utm_source=push' },
  }));
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
