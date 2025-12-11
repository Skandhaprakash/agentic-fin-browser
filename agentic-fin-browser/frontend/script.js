
const API_BASE = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.addEventListener('click', runAnalysis);
});

function setStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = 'status-message ' + type;
}

async function runAnalysis() {
    const symbol = document.getElementById('symbolInput').value.trim();
    const market = document.getElementById('marketInput').value.trim();
    const customUrl = document.getElementById('urlInput').value.trim();

    if (!symbol) {
        setStatus('Please enter a stock symbol', 'error');
        return;
    }

    setStatus('Running analysis... This may take a minute', 'loading');

    try {
        const payload = {
            symbol: symbol,
            market: market || null,
            url: customUrl || null
        };

        const response = await fetch(API_BASE + '/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);
        setStatus('Analysis complete!', 'success');
    } catch (err) {
        console.error('Analysis error:', err);
        setStatus(`Error: ${err.message}. Make sure backend is running at ${API_BASE}`, 'error');
    }
}

function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Populate financial table
    const financialTableBody = document.querySelector('#financialTable tbody');
    financialTableBody.innerHTML = '';

    if (data.years && data.years.length > 0) {
        data.years.forEach(year => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${year.label || year.year}</td>
                <td>${formatNumber(year.revenue)}</td>
                <td>${formatNumber(year.ar)}</td>
                <td>${formatNumber(year.cash)}</td>
                <td>${formatNumber(year.debt)}</td>
                <td>${year.dso ? year.dso.toFixed(1) : 'N/A'}</td>
                <td>${year.cash_ar ? year.cash_ar.toFixed(2) : 'N/A'}</td>
                <td>${year.cash_debt ? year.cash_debt.toFixed(2) : 'N/A'}</td>
            `;
            financialTableBody.appendChild(row);
        });
    } else {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="8" style="text-align: center; color: #999;">No financial data available</td>';
        financialTableBody.appendChild(row);
    }

    // Populate anomaly table
    const anomalyTableBody = document.querySelector('#anomalyTable tbody');
    anomalyTableBody.innerHTML = '';

    if (data.anomalies && data.anomalies.length > 0) {
        data.anomalies.forEach(anomaly => {
            const row = document.createElement('tr');
            row.className = anomaly.color;
            row.innerHTML = `
                <td>${anomaly.year}</td>
                <td><span class="flag-dot ${anomaly.color}"></span>${anomaly.color.toUpperCase()}</td>
                <td>${anomaly.condition}</td>
                <td>${anomaly.interpretation}</td>
            `;
            anomalyTableBody.appendChild(row);
        });
    } else {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" style="text-align: center; color: #999;">No anomalies detected</td>';
        anomalyTableBody.appendChild(row);
    }

    // Display narrative
    const narrativeEl = document.getElementById('agentNarrative');
    narrativeEl.textContent = data.narrative || 'No narrative available.';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';
    if (value >= 1000000000) {
        return (value / 1000000000).toFixed(2) + 'B';
    } else if (value >= 1000000) {
        return (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(2) + 'K';
    }
    return value.toFixed(2);
}
