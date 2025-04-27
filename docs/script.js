// Collect and send data to the API
async function logData() {
    const data = {
        fingerprint: await getFingerprint(),
        screen: `${screen.width}x${screen.height}`,
        userAgent: navigator.userAgent
    };
    
    // Send to backend API
    fetch('https://api.cookieless.3192693-wd09907.twc1.net/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

// Example: Browser fingerprinting (simplified)
async function getFingerprint() {
    return 'anon-' + Math.random().toString(36).substr(2, 9);
}

// Initialize
logData();