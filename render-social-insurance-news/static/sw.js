// Service Worker - PWA対応 (安全バージョン)
const CACHE_NAME = 'social-insurance-news-v3';
const urlsToCache = [
  '/static/manifest.json'  // 静的ファイルのみキャッシュ
];

// Install - 通常のライフサイクル
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate - 穏やかなキャッシュクリーンアップ
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch - ネットワークファーストで動的コンテンツを保証
self.addEventListener('fetch', function(event) {
  // 静的ファイルのみキャッシュから提供
  if (event.request.url.includes('/static/')) {
    event.respondWith(
      caches.match(event.request)
        .then(function(response) {
          if (response) {
            return response;
          }
          return fetch(event.request);
        })
    );
  } else {
    // 動的ページ（/）はネットワークファースト
    event.respondWith(
      fetch(event.request)
        .catch(function() {
          // ネットワークエラー時のみキャッシュから提供
          return caches.match(event.request);
        })
    );
  }
});