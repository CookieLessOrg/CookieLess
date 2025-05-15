// data collection code
async function logData() {
    const data = {
        fingerprint: await getFingerprint(),
        screen: `${screen.width}x${screen.height}`,
        userAgent: navigator.userAgent
    };
    
    fetch('https://147.45.139.11:7881/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

// stats fetching functionality
document.getElementById('showStats').addEventListener('click', fetchStats);

async function fetchStats() {
    try {
        const response = await fetch('https://147.45.139.11:7881/get');
        const data = await response.json();
        displayStats(data);
    } catch (error) {
        console.error('Error fetching stats:', error);
        displayError();
    }
}

function displayStats(stats) {
    const container = document.getElementById('analytics-data');
    container.innerHTML = `
        <h2>Some Statistics</h2>
        <div class="stat-item">
            <span class="stat-label">Total Visitors:</span>
            <span class="stat-value">${stats}</span>
        </div>
        <!-- Add more stats as needed -->
    `;
}

function displayError() {
    const container = document.getElementById('analytics-data');
    container.innerHTML = '<p class="error">Failed to load statistics. Please try again later.</p>';
}

// Fingerprint and initialization
async function getFingerprint() {
    return 'anon-' + Math.random().toString(36).substr(2, 9);
}

// Initialize data collection
logData();
