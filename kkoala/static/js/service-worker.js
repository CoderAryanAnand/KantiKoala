const CACHE_NAME = 'kantikoala-v3';
const ASSETS_TO_CACHE = [
    '/static/img/KantiKoalaLogoVar2.png',
    '/static/manifest.json',
    '/static/output.css',
    '/static/js/darkmode.js',
    '/offline'
];

// Install event: Cache critical assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Fetch event: Serve from cache, network, or offline page
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            // Return cached response if found
            if (response) {
                return response;
            }
            
            // Otherwise try network
            return fetch(event.request).catch(() => {
                // If network fails and it's a navigation request (HTML page), show offline page
                if (event.request.mode === 'navigate') {
                    return caches.match('/offline');
                }
            });
        })
    );
});