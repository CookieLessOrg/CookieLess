// Data collection code
async function logData() {
    const data = {
        fingerprint: await getFingerprint(),
        screen: `${screen.width}x${screen.height}`,
        userAgent: navigator.userAgent
    };
    
    try {
        await fetch('https://147.45.139.11:7881/post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        // After successful POST, fetch stats
        fetchStats();
    } catch (error) {
        console.error('Error sending data:', error);
        displayError('Failed to send analytics data');
    }
}

// Auto-fetch stats on page load
async function fetchStats() {
    try {
        const response = await fetch('https://147.45.139.11:7881/get');
        const data = await response.json();
        document.getElementById('loading').remove();
        displayStats(data);
    } catch (error) {
        console.error('Error fetching stats:', error);
        displayError('Failed to load statistics. Please try again later.');
    }
}

function displayStats(stats) {
    const container = document.getElementById('analytics-data');
    container.innerHTML = `
        <h2>Real-time Statistics</h2>
        ${createStatsSection('General Statistics', stats)}
        ${createPeriodStats(stats.periodStats)}
        ${createTimeSeriesTable('Daily Statistics', stats.dailyStats)}
        ${createTimeSeriesTable('Monthly Statistics', stats.monthlyStats)}
    `;
}

function createStatsSection(title, data) {
    return `
        <div class="stats-section">
            <h3>${title}</h3>
            <div class="stats-grid">
                ${createStatItem('Total Visitors', data.totalVisitors)}
                ${createStatItem('Unique Visitors', data.uniqueVisitors)}
            </div>
        </div>
    `;
}

function createPeriodStats(periodStats) {
    return `
        <div class="stats-section">
            <h3>Period Statistics</h3>
            <div class="stats-grid">
                ${Object.entries(periodStats).map(([period, stats]) => `
                    <div class="period-group">
                        <h4>${period.replace('_', ' ').toUpperCase()}</h4>
                        ${createStatItem('Total', stats.total)}
                        ${createStatItem('Unique', stats.unique)}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createTimeSeriesTable(title, data) {
    if (!data || data.length === 0) return '';
    
    return `
        <div class="stats-section">
            <h3>${title}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Total</th>
                        <th>Unique</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(entry => `
                        <tr>
                            <td>${entry.date || entry.month}</td>
                            <td>${entry.total}</td>
                            <td>${entry.unique}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function createStatItem(label, value) {
    return `
        <div class="stat-item">
            <span class="stat-label">${label}:</span>
            <span class="stat-value">${value}</span>
        </div>
    `;
}

function displayError(message) {
    const container = document.getElementById('analytics-data');
    container.innerHTML = `<p class="error">${message}</p>`;
}

// Fingerprint generation
async function getFingerprint() {
    return 'anon-' + Math.random().toString(36).substr(2, 9);
}

// Initialize data collection and stats loading
logData();