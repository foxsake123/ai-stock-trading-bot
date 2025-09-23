// ChatGPT Trading Report Extractor - Content Script
// Monitors ChatGPT for trading reports and sends to local server

console.log('ChatGPT Trading Report Extractor loaded');

// Configuration
const KEYWORDS = ['RCAT', 'trade', 'entry', 'stop', 'target', 'symbol', 'TradingAgents'];
const LOCAL_SERVER = 'http://localhost:8888/save_report';

// Function to check if message contains trading report
function isTradingReport(text) {
    if (!text) return false;
    
    const lowerText = text.toLowerCase();
    const hasTradeKeywords = KEYWORDS.some(keyword => 
        lowerText.includes(keyword.toLowerCase())
    );
    
    // Check for multiple indicators
    const hasSymbol = /\b[A-Z]{1,5}\b/.test(text);
    const hasPrice = /\$?\d+\.?\d*/.test(text);
    const hasAction = /(long|short|buy|sell)/i.test(text);
    
    return hasTradeKeywords && hasSymbol && (hasPrice || hasAction);
}

// Function to extract report from ChatGPT response
function extractReport() {
    // Find all assistant messages
    const messages = document.querySelectorAll('[data-message-author-role="assistant"]');
    
    if (messages.length === 0) {
        console.log('No assistant messages found');
        return null;
    }
    
    // Get the most recent message
    const latestMessage = messages[messages.length - 1];
    const messageText = latestMessage.innerText || latestMessage.textContent;
    
    if (!isTradingReport(messageText)) {
        console.log('Latest message is not a trading report');
        return null;
    }
    
    console.log('Trading report detected!');
    
    return {
        text: messageText,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        conversationId: window.location.pathname.split('/').pop()
    };
}

// Function to send report to local server
async function sendReportToServer(report) {
    try {
        const response = await fetch(LOCAL_SERVER, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(report)
        });
        
        if (response.ok) {
            console.log('Report sent successfully');
            // Show notification
            chrome.runtime.sendMessage({
                type: 'notification',
                message: 'Trading report saved successfully!'
            });
        } else {
            console.error('Failed to send report:', response.status);
        }
    } catch (error) {
        console.error('Error sending report:', error);
        // Store locally if server is not running
        chrome.storage.local.set({
            'pending_report': report,
            'saved_at': new Date().toISOString()
        });
    }
}

// Auto-detection mode
let lastReportHash = '';

function checkForNewReport() {
    const report = extractReport();
    
    if (report) {
        // Create hash to avoid duplicates
        const reportHash = btoa(report.text.substring(0, 100));
        
        if (reportHash !== lastReportHash) {
            lastReportHash = reportHash;
            sendReportToServer(report);
        }
    }
}

// Check every 5 seconds for new reports
setInterval(checkForNewReport, 5000);

// Manual extraction button
function addExtractButton() {
    const targetElement = document.querySelector('main');
    if (!targetElement) return;
    
    const button = document.createElement('button');
    button.innerHTML = '📊 Extract Trading Report';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        padding: 10px 20px;
        background: #10a37f;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    
    button.addEventListener('click', () => {
        const report = extractReport();
        if (report) {
            sendReportToServer(report);
            button.innerHTML = '✅ Report Saved!';
            setTimeout(() => {
                button.innerHTML = '📊 Extract Trading Report';
            }, 3000);
        } else {
            button.innerHTML = '❌ No Report Found';
            setTimeout(() => {
                button.innerHTML = '📊 Extract Trading Report';
            }, 3000);
        }
    });
    
    document.body.appendChild(button);
}

// Add button when page loads
setTimeout(addExtractButton, 2000);

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extract') {
        const report = extractReport();
        if (report) {
            sendReportToServer(report);
            sendResponse({success: true, report: report});
        } else {
            sendResponse({success: false, message: 'No trading report found'});
        }
    }
    return true;
});