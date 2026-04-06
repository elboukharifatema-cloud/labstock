const CACHE = 'labstock-v1';
const PRECACHE = [
  '/',
  '/products',
  '/movements',
  '/alerts',
  '/static/css/app.css',
  '/static/js/app.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  // Network-first for API and HTML navigation
  if (request.url.includes('/api/') || request.mode === 'navigate') {
    e.respondWith(
      fetch(request)
        .then(res => { const c = res.clone(); caches.open(CACHE).then(cache => cache.put(request, c)); return res; })
        .catch(() => caches.match(request))
    );
    return;
  }
  // Cache-first for static assets
  e.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(res => {
      const c = res.clone();
      caches.open(CACHE).then(cache => cache.put(request, c));
      return res;
    }))
  );
});
