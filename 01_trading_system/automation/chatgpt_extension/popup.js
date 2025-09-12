// Popup script for ChatGPT Report Extractor

document.addEventListener('DOMContentLoaded', function() {
    const extractBtn = document.getElementById('extractBtn');
    const testServerBtn = document.getElementById('testServerBtn');
    const saveSettingsBtn = document.getElementById('saveSettings');
    const statusDiv = document.getElementById('status');
    const autoModeCheckbox = document.getElementById('autoMode');
    const serverUrlInput = document.getElementById('serverUrl');
    
    // Load settings
    chrome.storage.local.get(['autoMode', 'serverUrl'], function(result) {
        autoModeCheckbox.checked = result.autoMode || false;
        serverUrlInput.value = result.serverUrl || 'http://localhost:8888';
    });
    
    // Extract button click
    extractBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'extract'}, function(response) {
                if (response && response.success) {
                    showStatus('Report extracted and sent!', 'success');
                } else {
                    showStatus(response?.message || 'No trading report found', 'error');
                }
            });
        });
    });
    
    // Test server connection
    testServerBtn.addEventListener('click', async function() {
        const serverUrl = serverUrlInput.value;
        try {
            const response = await fetch(`${serverUrl}/health`, {
                method: 'GET',
                mode: 'cors'
            });
            
            if (response.ok) {
                showStatus('Server connected successfully!', 'success');
            } else {
                showStatus('Server not responding', 'error');
            }
        } catch (error) {
            showStatus('Cannot connect to server. Make sure it\'s running.', 'error');
        }
    });
    
    // Save settings
    saveSettingsBtn.addEventListener('click', function() {
        const settings = {
            autoMode: autoModeCheckbox.checked,
            serverUrl: serverUrlInput.value
        };
        
        chrome.storage.local.set(settings, function() {
            showStatus('Settings saved!', 'success');
        });
    });
    
    // Show status message
    function showStatus(message, type) {
        statusDiv.className = `status ${type}`;
        statusDiv.textContent = message;
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = '';
        }, 3000);
    }
});