// ChatGPT Trading Report Extractor - Enhanced Content Script
// Monitors ChatGPT for trading reports and sends to local server

console.log('[ChatGPT Extractor] Extension loaded at', new Date().toISOString());

// Configuration
const KEYWORDS = ['trade', 'entry', 'stop', 'target', 'symbol', 'TradingAgents', 'buy', 'sell', 'long', 'short'];
const LOCAL_SERVER = 'http://localhost:8888';

// Server connection status
let serverConnected = false;

// Test server connection on load
async function testServerConnection() {
    try {
        const response = await fetch(`${LOCAL_SERVER}/health`, {
            method: 'GET',
            mode: 'cors'
        });

        if (response.ok) {
            serverConnected = true;
            console.log('[ChatGPT Extractor] ✅ Server connected at', LOCAL_SERVER);
            updateStatusIndicator(true);
            return true;
        }
    } catch (error) {
        serverConnected = false;
        console.error('[ChatGPT Extractor] ❌ Server connection failed:', error.message);
        updateStatusIndicator(false);
    }
    return false;
}

// Update visual connection indicator
function updateStatusIndicator(connected) {
    const existingIndicator = document.getElementById('extractor-status');
    if (existingIndicator) {
        existingIndicator.remove();
    }

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
    `;
    indicator.innerHTML = connected ?
        '🟢 Server Connected' :
        '🔴 Server Disconnected - Check localhost:8888';

    document.body.appendChild(indicator);

    // Auto-hide if connected
    if (connected) {
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.style.opacity = '0.3';
            }
        }, 5000);
    }
}

// Enhanced trading report detection
function isTradingReport(text) {
    if (!text || text.length < 50) return false;

    const lowerText = text.toLowerCase();

    // Count keyword matches
    let keywordMatches = 0;
    for (const keyword of KEYWORDS) {
        if (lowerText.includes(keyword.toLowerCase())) {
            keywordMatches++;
        }
    }

    // Need at least 2 keywords
    if (keywordMatches < 2) return false;

    // Look for stock symbols (1-5 uppercase letters)
    const symbolPattern = /\b[A-Z]{1,5}\b/g;
    const symbols = text.match(symbolPattern);
    const validSymbols = symbols ? symbols.filter(s =>
        !['USD', 'ET', 'AM', 'PM', 'US', 'UK', 'EU', 'NYSE', 'NASDAQ'].includes(s)
    ) : [];

    // Look for prices
    const pricePattern = /\$?\d+\.?\d*/g;
    const prices = text.match(pricePattern);

    // Must have at least one symbol and one price
    return validSymbols.length > 0 && prices && prices.length > 0;
}

// Extract report with better parsing
function extractReport() {
    console.log('[ChatGPT Extractor] Checking for trading reports...');

    // Try multiple selectors for ChatGPT messages
    const selectors = [
        '[data-message-author-role="assistant"]',
        '.markdown.prose',
        '.agent-turn',
        '.message-content'
    ];

    let messages = null;
    for (const selector of selectors) {
        messages = document.querySelectorAll(selector);
        if (messages.length > 0) {
            console.log(`[ChatGPT Extractor] Found ${messages.length} messages using selector: ${selector}`);
            break;
        }
    }

    if (!messages || messages.length === 0) {
        console.log('[ChatGPT Extractor] No messages found on page');
        return null;
    }

    // Check the last few messages for trading content
    for (let i = messages.length - 1; i >= Math.max(0, messages.length - 3); i--) {
        const message = messages[i];
        const messageText = message.innerText || message.textContent;

        if (isTradingReport(messageText)) {
            console.log('[ChatGPT Extractor] ✅ Trading report detected in message', i + 1);

            // Extract structured data
            const trades = extractTradesFromText(messageText);

            return {
                text: messageText,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                conversationId: window.location.pathname.split('/').pop(),
                trades: trades,
                messageIndex: i
            };
        }
    }

    console.log('[ChatGPT Extractor] No trading reports found in recent messages');
    return null;
}

// Extract structured trade data
function extractTradesFromText(text) {
    const trades = [];
    const lines = text.split('\n');

    let currentTrade = {};

    for (const line of lines) {
        const upperLine = line.toUpperCase();

        // Extract symbol
        if (line.includes('Symbol:') || line.includes('SYMBOL:')) {
            const match = line.match(/[A-Z]{1,5}/);
            if (match) {
                if (Object.keys(currentTrade).length > 0) {
                    trades.push(currentTrade);
                }
                currentTrade = { symbol: match[0] };
            }
        }

        // Extract prices
        if (currentTrade.symbol) {
            if (line.toLowerCase().includes('entry')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.entry = parseFloat(price[1]);
            }
            if (line.toLowerCase().includes('stop')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.stop = parseFloat(price[1]);
            }
            if (line.toLowerCase().includes('target')) {
                const price = line.match(/\$?([\d.]+)/);
                if (price) currentTrade.target = parseFloat(price[1]);
            }

            // Extract action
            if (line.toLowerCase().includes('long') || line.toLowerCase().includes('buy')) {
                currentTrade.action = 'LONG';
            } else if (line.toLowerCase().includes('short') || line.toLowerCase().includes('sell')) {
                currentTrade.action = 'SHORT';
            }
        }
    }

    // Add last trade
    if (Object.keys(currentTrade).length > 0) {
        trades.push(currentTrade);
    }

    console.log(`[ChatGPT Extractor] Extracted ${trades.length} trades:`, trades);
    return trades;
}

// Send report to server with retry
async function sendReportToServer(report) {
    // Test connection first
    if (!serverConnected) {
        const connected = await testServerConnection();
        if (!connected) {
            console.error('[ChatGPT Extractor] Cannot send report - server not connected');
            // Store locally for later
            chrome.storage.local.set({
                'pending_report': report,
                'saved_at': new Date().toISOString()
            });
            showNotification('❌ Server offline - Report saved locally', 'error');
            return false;
        }
    }

    try {
        console.log('[ChatGPT Extractor] Sending report to server...');

        const response = await fetch(`${LOCAL_SERVER}/save_report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify(report)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('[ChatGPT Extractor] ✅ Report saved successfully:', result);
            showNotification(`✅ ${result.trades?.length || 0} trades saved!`, 'success');
            return true;
        } else {
            const error = await response.text();
            console.error('[ChatGPT Extractor] Server error:', error);
            showNotification('❌ Server error - Check console', 'error');
            return false;
        }
    } catch (error) {
        console.error('[ChatGPT Extractor] Failed to send report:', error);
        serverConnected = false;
        updateStatusIndicator(false);

        // Store locally
        chrome.storage.local.set({
            'pending_report': report,
            'saved_at': new Date().toISOString()
        });

        showNotification('❌ Connection failed - Report saved locally', 'error');
        return false;
    }
}

// Show notification
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
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Enhanced extract button
function addExtractButton() {
    const existingButton = document.getElementById('extract-button');
    if (existingButton) return;

    const button = document.createElement('button');
    button.id = 'extract-button';
    button.innerHTML = '📊 Extract Trading Report';
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

    button.onmouseover = () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 20px rgba(0,0,0,0.3)';
    };

    button.onmouseout = () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
    };

    button.addEventListener('click', async () => {
        button.disabled = true;
        button.innerHTML = '⏳ Extracting...';

        const report = extractReport();
        if (report) {
            const success = await sendReportToServer(report);
            button.innerHTML = success ? '✅ Report Saved!' : '⚠️ Saved Locally';
            button.style.background = success ? '#10a37f' : '#ff9800';
        } else {
            button.innerHTML = '❌ No Report Found';
            button.style.background = '#ff4444';
        }

        setTimeout(() => {
            button.innerHTML = '📊 Extract Trading Report';
            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            button.disabled = false;
        }, 3000);
    });

    document.body.appendChild(button);
}

// Auto-detection with deduplication
let lastReportHash = '';
let checkInterval;

function startAutoDetection() {
    checkInterval = setInterval(async () => {
        if (!serverConnected) {
            await testServerConnection();
        }

        const report = extractReport();
        if (report) {
            const hash = btoa(report.text.substring(0, 200));
            if (hash !== lastReportHash) {
                console.log('[ChatGPT Extractor] New report detected via auto-detection');
                lastReportHash = hash;
                await sendReportToServer(report);
            }
        }
    }, 5000);
}

// Initialize extension
async function initialize() {
    console.log('[ChatGPT Extractor] Initializing...');

    // Test server connection
    await testServerConnection();

    // Add extract button after delay
    setTimeout(addExtractButton, 2000);

    // Start auto-detection
    startAutoDetection();

    // Check for pending reports
    chrome.storage.local.get(['pending_report'], async (result) => {
        if (result.pending_report && serverConnected) {
            console.log('[ChatGPT Extractor] Found pending report, attempting to send...');
            const success = await sendReportToServer(result.pending_report);
            if (success) {
                chrome.storage.local.remove(['pending_report']);
            }
        }
    });

    // Retry connection every 30 seconds if disconnected
    setInterval(async () => {
        if (!serverConnected) {
            await testServerConnection();
        }
    }, 30000);
}

// Message listener for popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extract') {
        const report = extractReport();
        if (report) {
            sendReportToServer(report).then(success => {
                sendResponse({success: success, report: report});
            });
        } else {
            sendResponse({success: false, message: 'No trading report found'});
        }
        return true; // Keep channel open for async response
    }

    if (request.action === 'test_connection') {
        testServerConnection().then(connected => {
            sendResponse({connected: connected});
        });
        return true;
    }
});

// Start everything
initialize();

console.log('[ChatGPT Extractor] Extension fully loaded and monitoring for reports');