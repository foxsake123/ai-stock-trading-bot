// Background service worker for ChatGPT Trading Report Extractor

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'notification') {
        // Show notification when report is saved
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icon48.png',
            title: 'Trading Report Saved',
            message: message.message
        });
    }
});

// Handle installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('ChatGPT Trading Report Extractor installed');
    
    // Set default settings
    chrome.storage.local.set({
        autoMode: true,
        serverUrl: 'http://localhost:8888'
    });
});