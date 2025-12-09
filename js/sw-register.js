/**
 * Service Worker Registration
 * 
 * Registers the service worker for offline support.
 * Add this to the end of js/main.js
 */

// Check if service workers are supported
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('ServiceWorker registered:', registration.scope);
        
        // Check for updates periodically
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000); // Check every hour
        
        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker available, show update notification
              showUpdateNotification();
            }
          });
        });
      })
      .catch((error) => {
        console.error('ServiceWorker registration failed:', error);
      });
    
    // Listen for messages from service worker
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data.type === 'SYNC_SUCCESS') {
        console.log('Background sync successful, reloading news...');
        // Optionally reload news data
        if (window.App && window.App.init) {
          window.App.init();
        }
      }
    });
  });
}

function showUpdateNotification() {
  // Create a simple notification banner
  const banner = document.createElement('div');
  banner.className = 'update-banner';
  banner.innerHTML = `
    <div style="position: fixed; top: 0; left: 0; right: 0; background: #4CAF50; color: white; padding: 1rem; text-align: center; z-index: 10000;">
      <p style="margin: 0 0 0.5rem 0;">కొత్త వెర్షన్ అందుబాటులో ఉంది! (New version available!)</p>
      <button onclick="location.reload()" style="background: white; color: #4CAF50; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-weight: 600;">
        రీలోడ్ చేయండి (Reload)
      </button>
    </div>
  `;
  document.body.appendChild(banner);
}

// Request permission for push notifications (optional)
function requestNotificationPermission() {
  if ('Notification' in window && 'serviceWorker' in navigator) {
    Notification.requestPermission().then((permission) => {
      if (permission === 'granted') {
        console.log('Notification permission granted');
        // Subscribe to push notifications
        navigator.serviceWorker.ready.then((registration) => {
          return registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(
              'YOUR_VAPID_PUBLIC_KEY_HERE'
            )
          });
        });
      }
    });
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');
  
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
