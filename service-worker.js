/**
 * Service Worker for Telugu News Aggregator
 * 
 * Provides offline support by caching static assets and news data.
 * Implements Cache First strategy for static files and Network First for data.
 */

const CACHE_NAME = 'telugu-news-v1';
const DATA_CACHE_NAME = 'telugu-news-data-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/main.css',
  '/js/main.js',
  '/js/app.js',
  '/js/utils/data-loader.js',
  'https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Install');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activate');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== DATA_CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle data requests (API or JSON files)
  if (url.pathname.startsWith('/data/') || url.pathname.startsWith('/api/')) {
    event.respondWith(
      // Network First strategy for data
      fetch(request)
        .then((response) => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DATA_CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Fallback to cache if network fails
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              console.log('[ServiceWorker] Serving from cache:', request.url);
              return cachedResponse;
            }
            // Return offline page or error response
            return new Response(
              JSON.stringify({
                error: 'Offline - no cached data available',
                offline: true
              }),
              {
                headers: { 'Content-Type': 'application/json' },
                status: 503
              }
            );
          });
        })
    );
    return;
  }
  
  // Handle static assets
  event.respondWith(
    // Cache First strategy for static assets
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        console.log('[ServiceWorker] Serving from cache:', request.url);
        return cachedResponse;
      }
      
      // Not in cache, fetch from network
      return fetch(request).then((response) => {
        // Cache successful responses to static assets
        if (response.ok && request.method === 'GET') {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      });
    })
  );
});

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync:', event.tag);
  
  if (event.tag === 'sync-news') {
    event.waitUntil(
      // Attempt to fetch latest news
      fetch('/data/index.json')
        .then((response) => response.json())
        .then((data) => {
          console.log('[ServiceWorker] Background sync successful');
          // Notify clients
          return self.clients.matchAll().then((clients) => {
            clients.forEach((client) => {
              client.postMessage({
                type: 'SYNC_SUCCESS',
                data: data
              });
            });
          });
        })
        .catch((error) => {
          console.error('[ServiceWorker] Background sync failed:', error);
        })
    );
  }
});

// Push notifications (future feature)
self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push notification received');
  
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Telugu News Update';
  const options = {
    body: data.body || 'New news available',
    icon: '/icon-192.png',
    badge: '/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification click:', event.notification.tag);
  
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});
