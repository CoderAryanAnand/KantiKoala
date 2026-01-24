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
    self.skipWaiting(); // Force new service worker to activate immediately
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate event: Claim clients immediately
self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
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

// Push Notification Event
self.addEventListener('push', function(event) {
    if (event.data) {
        let data = {};
        try {
            data = event.data.json();
        } catch (e) {
            data = { title: "KantiKoala", body: event.data.text() };
        }

        const options = {
            body: data.body,
            icon: '/static/img/KantiKoalaLogoVar2.png',
            badge: '/static/img/KantiKoalaLogoVar2.png',
            vibrate: [100, 50, 100],
            data: {
                dateOfArrival: Date.now(),
                url: data.url || '/'
            }
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification Click Event
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});