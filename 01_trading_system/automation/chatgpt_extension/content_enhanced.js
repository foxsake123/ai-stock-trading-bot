// ChatGPT Trading Report Extractor - Enhanced for Table Format
// Optimized for TradingAgents table format reports

console.log('[ChatGPT Extractor] Enhanced extension loaded at', new Date().toISOString());

// Configuration
const LOCAL_SERVER = 'http://localhost:8888';
let serverConnected = false;
let lastExtractedHash = '';

// Test server connection
async function testServerConnection() {
    try {
        const response = await fetch(`${LOCAL_SERVER}/health`, {
            method: 'GET',
            mode: 'cors'
        });

        if (response.ok) {
            serverConnected = true;
            console.log('[ChatGPT Extractor] Server connected');
            updateStatusIndicator(true);
            return true;
        }
    } catch (error) {
        serverConnected = false;
        console.error('[ChatGPT Extractor] Server offline:', error.message);
        updateStatusIndicator(false);
    }
    return false;
}

// Visual status indicator
function updateStatusIndicator(connected) {
    const existingIndicator = document.getElementById('extractor-status');
    if (existingIndicator) existingIndicator.remove();

    const indicator = document.createElement('div');
    indicator.id = 'extractor-status';
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 10001;
        padding: 8px 12px;
        background: ${connected ? '#10a37f' : '#ff4444'};
        color: white;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        cursor: pointer;
    `;
    indicator.innerHTML = connected ?
        '🟢 Bot Connected' :
        '🔴 Bot Disconnected';

    indicator.onclick = testServerConnection;
    document.body.appendChild(indicator);

    // Auto-fade if connected
    if (connected) {
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.style.opacity = '0.3';
            }
        }, 5000);
    }
}

// Enhanced extraction for table format
function extractTableTrades(element) {
    const trades = [];

    // Find all tables in the element
    const tables = element.querySelectorAll('table');

    for (const table of tables) {
        const rows = table.querySelectorAll('tr');

        // Skip header row
        for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].querySelectorAll('td');
            if (cells.length < 4) continue;

            // Parse table row - expected format:
            // Ticker | Catalyst | Position Size | Entry | Stop-Loss | Target 1 | Target 2 | Options
            const trade = {};

            // Extract ticker (first cell, remove extra text)
            const tickerCell = cells[0].textContent.trim();
            const tickerMatch = tickerCell.match(/([A-Z]{1,5})/);
            if (tickerMatch) {
                trade.symbol = tickerMatch[1];
            }

            // Find cells with prices (look for $ or numbers)
            for (let j = 1; j < cells.length; j++) {
                const cellText = cells[j].textContent.trim();

                // Position size
                if (cellText.includes('%')) {
                    const sizeMatch = cellText.match(/(\d+)%/);
                    if (sizeMatch) trade.size_pct = parseInt(sizeMatch[1]);
                }

                // Entry price
                if ((cellText.toLowerCase().includes('long') || cellText.includes('~')) && !trade.entry) {
                    const priceMatch = cellText.match(/\$?([\d.]+)/);
                    if (priceMatch) {
                        trade.entry = parseFloat(priceMatch[1]);
                        trade.action = cellText.toLowerCase().includes('short') ? 'SHORT' : 'LONG';
                    }
                }

                // Stop loss
                if (cellText.includes('–') && cellText.includes('%')) {
                    const priceMatch = cellText.match(/\$?([\d.]+)/);
                    if (priceMatch && !trade.stop) {
                        trade.stop = parseFloat(priceMatch[1]);
                    }
                }

                // Targets
                if (cellText.includes('+') && cellText.includes('%')) {
                    const priceMatch = cellText.match(/\$?([\d.]+)/);
                    if (priceMatch) {
                        if (!trade.target) {
                            trade.target = parseFloat(priceMatch[1]);
                        } else if (!trade.target2) {
                            trade.target2 = parseFloat(priceMatch[1]);
                        }
                    }
                }

                // Catalyst info
                if (j === 1) { // Usually second column
                    trade.catalyst = cellText.substring(0, 100);
                }
            }

            // Validate and add trade
            if (trade.symbol && trade.entry) {
                // Set defaults if missing
                if (!trade.stop) trade.stop = trade.entry * 0.92;
                if (!trade.target) trade.target = trade.entry * 1.15;
                if (!trade.size_pct) trade.size_pct = 5;
                if (!trade.action) trade.action = 'LONG';

                trades.push(trade);
                console.log(`[ChatGPT Extractor] Extracted trade: ${trade.symbol} @ $${trade.entry}`);
            }
        }
    }

    return trades;
}

// Alternative extraction for non-table format
function extractTextTrades(text) {
    const trades = [];
    const lines = text.split('\n');

    // Pattern for: "SYMBOL (Company) - Entry: $X, Stop: $Y, Target: $Z"
    const tradePattern = /([A-Z]{1,5}).*?(?:Entry|@|Buy at).*?\$?([\d.]+).*?(?:Stop|SL).*?\$?([\d.]+).*?(?:Target|TP).*?\$?([\d.]+)/gi;
    const matches = text.matchAll(tradePattern);

    for (const match of matches) {
        trades.push({
            symbol: match[1],
            entry: parseFloat(match[2]),
            stop: parseFloat(match[3]),
            target: parseFloat(match[4]),
            action: 'LONG',
            size_pct: 5
        });
    }

    // Also try line-by-line parsing
    let currentTrade = null;
    for (const line of lines) {
        // New trade start
        if (/^\d+\./.test(line) || /^[A-Z]{1,5}\b/.test(line)) {
            if (currentTrade && currentTrade.symbol && currentTrade.entry) {
                trades.push(currentTrade);
            }
            const symbolMatch = line.match(/([A-Z]{1,5})/);
            if (symbolMatch) {
                currentTrade = {
                    symbol: symbolMatch[1],
                    action: 'LONG',
                    size_pct: 5
                };
            }
        }

        // Extract data for current trade
        if (currentTrade) {
            // Entry price
            if (line.toLowerCase().includes('entry') || line.includes('~$')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.entry = parseFloat(price[1]);
            }
            // Stop loss
            if (line.toLowerCase().includes('stop')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.stop = parseFloat(price[1]);
            }
            // Target
            if (line.toLowerCase().includes('target')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.target = parseFloat(price[1]);
            }
            // Size
            if (line.includes('%')) {
                const size = line.match(/(\d+)%/);
                if (size) currentTrade.size_pct = parseInt(size[1]);
            }
        }
    }

    // Add last trade
    if (currentTrade && currentTrade.symbol && currentTrade.entry) {
        trades.push(currentTrade);
    }

    return trades;
}

// Main extraction function
function extractReport() {
    console.log('[ChatGPT Extractor] Scanning for trading reports...');

    // Find ChatGPT messages
    const selectors = [
        '[data-message-author-role="assistant"]',
        '.markdown.prose',
        '.agent-turn',
        'div.group:has(.markdown)'
    ];

    let messages = null;
    for (const selector of selectors) {
        messages = document.querySelectorAll(selector);
        if (messages.length > 0) break;
    }

    if (!messages || messages.length === 0) {
        console.log('[ChatGPT Extractor] No messages found');
        return null;
    }

    // Check recent messages for trading content
    for (let i = messages.length - 1; i >= Math.max(0, messages.length - 5); i--) {
        const message = messages[i];
        const text = message.innerText || message.textContent;

        // Quick check for trading keywords
        if (!text || text.length < 100) continue;

        const keywords = ['ticker', 'entry', 'stop', 'target', 'catalyst', 'position size', 'INCY', 'SRRK', 'FBIO', 'RIVN', 'HELE'];
        const hasKeywords = keywords.some(kw => text.toLowerCase().includes(kw.toLowerCase()));

        if (!hasKeywords) continue;

        console.log(`[ChatGPT Extractor] Potential report found in message ${i + 1}`);

        // Try table extraction first
        let trades = extractTableTrades(message);

        // Fallback to text extraction
        if (trades.length === 0) {
            trades = extractTextTrades(text);
        }

        if (trades.length > 0) {
            console.log(`[ChatGPT Extractor] Extracted ${trades.length} trades`);

            return {
                text: text.substring(0, 10000), // Limit size
                trades: trades,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                messageIndex: i
            };
        }
    }

    console.log('[ChatGPT Extractor] No valid trading reports found');
    return null;
}

// Send to server
async function sendReportToServer(report) {
    if (!serverConnected) {
        await testServerConnection();
        if (!serverConnected) {
            console.error('[ChatGPT Extractor] Server offline');
            // Save locally
            localStorage.setItem('pending_report', JSON.stringify(report));
            showNotification('Server offline - Report saved locally', 'error');
            return false;
        }
    }

    try {
        const response = await fetch(`${LOCAL_SERVER}/save_report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            mode: 'cors',
            body: JSON.stringify(report)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('[ChatGPT Extractor] Report saved:', result);
            showNotification(`Saved ${result.trades?.length || 0} trades!`, 'success');

            // Clear any pending reports
            localStorage.removeItem('pending_report');
            return true;
        }
    } catch (error) {
        console.error('[ChatGPT Extractor] Send failed:', error);
        serverConnected = false;
    }

    return false;
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 10002;
        padding: 12px 20px;
        background: ${type === 'success' ? '#10a37f' : type === 'error' ? '#ff4444' : '#0066cc'};
        color: white;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Extract button
function addExtractButton() {
    if (document.getElementById('extract-button')) return;

    const button = document.createElement('button');
    button.id = 'extract-button';
    button.innerHTML = '📊 Extract Trades';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    `;

    button.onclick = async () => {
        button.disabled = true;
        button.innerHTML = '⏳ Extracting...';

        const report = extractReport();
        if (report) {
            const success = await sendReportToServer(report);
            button.innerHTML = success ? '✅ Saved!' : '⚠️ Saved Locally';
        } else {
            button.innerHTML = '❌ No Trades Found';
        }

        setTimeout(() => {
            button.innerHTML = '📊 Extract Trades';
            button.disabled = false;
        }, 3000);
    };

    document.body.appendChild(button);
}

// Auto-detection
function startAutoDetection() {
    setInterval(async () => {
        const report = extractReport();
        if (report) {
            // Generate hash to avoid duplicates
            const hash = btoa((report.trades.map(t => t.symbol).join('') + report.trades.length).substring(0, 20));
            if (hash !== lastExtractedHash) {
                console.log('[ChatGPT Extractor] New report auto-detected');
                lastExtractedHash = hash;
                await sendReportToServer(report);
            }
        }
    }, 10000); // Check every 10 seconds
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

// Initialize
async function initialize() {
    console.log('[ChatGPT Extractor] Initializing enhanced extractor...');

    // Connect to server
    await testServerConnection();

    // Add UI elements
    setTimeout(addExtractButton, 2000);

    // Start monitoring
    startAutoDetection();

    // Check for pending reports
    const pending = localStorage.getItem('pending_report');
    if (pending && serverConnected) {
        try {
            const report = JSON.parse(pending);
            await sendReportToServer(report);
        } catch (e) {
            console.error('Failed to send pending report:', e);
        }
    }

    // Reconnect attempts
    setInterval(async () => {
        if (!serverConnected) {
            await testServerConnection();
        }
    }, 30000);
}

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extract') {
        const report = extractReport();
        sendResponse({ success: !!report, report: report });
        if (report) sendReportToServer(report);
        return true;
    }
});

// Start
initialize();
console.log('[ChatGPT Extractor] Enhanced extension ready');