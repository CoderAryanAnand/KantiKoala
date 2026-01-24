// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Subscribe function
async function subscribeUserToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported');
        return;
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        // Check current subscription
        let subscription = await registration.pushManager.getSubscription();
        
        // If we have a subscription, we should check if it's valid or just recreate it to be safe
        // given we had VAPID key issues.
        if (subscription) {
            console.log('Unsubscribing old subscription to ensure fresh start...');
            await subscription.unsubscribe();
        }

        // Fetch the public key from server or env
        const VAPID_PUBLIC_KEY = window.VAPID_PUBLIC_KEY; 
        if (!VAPID_PUBLIC_KEY) {
            console.error('VAPID Public Key not found');
            return;
        }

        const convertedVapidKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);

        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: convertedVapidKey
        });
        console.log('User is subscribed:', subscription);

        // Send subscription to server (ALWAYS convert to JSON properly)
        // Note: JSON.stringify(subscription) returns a string with keys, endpoint etc.
        await fetch('/notifications/subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        alert('Benachrichtigungen erfolgreich aktiviert (neu synchronisiert)!');

    } catch (err) {
        console.error('Failed to subscribe the user: ', err);
        alert('Fehler beim Aktivieren der Benachrichtigungen.');
    }
}
