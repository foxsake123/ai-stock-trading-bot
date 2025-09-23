"""
Selenium-based ChatGPT report fetcher
Automatically logs in and retrieves daily reports
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import os
import time
from datetime import datetime
import logging
from typing import Optional, Dict
import pickle

class ChatGPTSeleniumFetcher:
    def __init__(self, conversation_url: str = None):
        """
        Initialize the fetcher
        
        Args:
            conversation_url: Direct URL to your TradingAgents conversation
        """
        self.research_dir = '02_data/research/reports/pre_market_daily'
        os.makedirs(self.research_dir, exist_ok=True)
        
        # You'll need to set this to your specific conversation URL
        self.conversation_url = conversation_url or os.getenv('CHATGPT_CONVERSATION_URL')
        
        # Cookie storage for session persistence
        self.cookie_file = '02_data/config/chatgpt_cookies.pkl'
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with options"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Optional: Run headless (without browser window)
        # options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def save_cookies(self, driver):
        """Save cookies for future sessions"""
        cookies = driver.get_cookies()
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(cookies, f)
        self.logger.info("Cookies saved")
    
    def load_cookies(self, driver):
        """Load saved cookies"""
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            self.logger.info("Cookies loaded")
            return True
        return False
    
    def login_if_needed(self, driver, wait):
        """Check if login is needed and wait for manual login"""
        try:
            # Check if we're already logged in
            driver.get('https://chatgpt.com')
            time.sleep(3)
            
            # Try to find the main chat interface
            if driver.find_elements(By.CSS_SELECTOR, '[data-testid="conversation-panel"]'):
                self.logger.info("Already logged in")
                return True
            
            # Wait for manual login
            self.logger.info("Please log in to ChatGPT manually...")
            self.logger.info("Waiting for login (60 seconds timeout)...")
            
            # Wait for successful login indicator
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-panel"], main'))
            )
            
            self.save_cookies(driver)
            self.logger.info("Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
    
    def navigate_to_conversation(self, driver):
        """Navigate to the specific conversation"""
        if self.conversation_url:
            driver.get(self.conversation_url)
            time.sleep(3)
            self.logger.info(f"Navigated to conversation: {self.conversation_url}")
        else:
            # Navigate to chats and find TradingAgents
            driver.get('https://chatgpt.com')
            time.sleep(3)
            
            # You might need to search for your specific conversation
            self.logger.info("Please navigate to your TradingAgents conversation")
            input("Press Enter when you're in the right conversation...")
    
    def extract_latest_report(self, driver) -> Optional[Dict]:
        """Extract the latest trading report from the conversation"""
        try:
            # Find all assistant messages
            messages = driver.find_elements(By.CSS_SELECTOR, '[data-message-author-role="assistant"]')
            
            if not messages:
                self.logger.error("No assistant messages found")
                return None
            
            # Get the latest message
            latest_message = messages[-1]
            message_text = latest_message.text
            
            # Check if it's a trading report
            if not self.is_trading_report(message_text):
                self.logger.warning("Latest message is not a trading report")
                # Try previous messages
                for msg in reversed(messages[:-1]):
                    if self.is_trading_report(msg.text):
                        message_text = msg.text
                        break
                else:
                    return None
            
            # Parse the report
            report = self.parse_report(message_text)
            return report
            
        except Exception as e:
            self.logger.error(f"Error extracting report: {e}")
            return None
    
    def is_trading_report(self, text: str) -> bool:
        """Check if text is a trading report"""
        keywords = ['symbol', 'entry', 'stop', 'target', 'trade', 'RCAT', 'position']
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower) >= 3
    
    def parse_report(self, text: str) -> Dict:
        """Parse report text into structured format"""
        import re
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': 'ChatGPT TradingAgents (Selenium)',
            'trades': [],
            'raw_text': text
        }
        
        lines = text.split('\n')
        current_trade = {}
        
        for line in lines:
            # Symbol extraction
            if 'symbol' in line.lower() or re.match(r'^[A-Z]{1,5}:', line):
                symbols = re.findall(r'\b[A-Z]{1,5}\b', line)
                if symbols and symbols[0] not in ['USD', 'AM', 'PM', 'ET']:
                    if current_trade and 'symbol' in current_trade:
                        report['trades'].append(current_trade)
                    current_trade = {'symbol': symbols[0]}
            
            # Price extraction
            if current_trade:
                if 'entry' in line.lower():
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['entry'] = float(price.group(1))
                
                if 'stop' in line.lower():
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['stop'] = float(price.group(1))
                
                if 'target' in line.lower():
                    price = re.search(r'\$?([\d.]+)', line)
                    if price:
                        current_trade['target'] = float(price.group(1))
                
                if 'long' in line.lower():
                    current_trade['action'] = 'long'
                elif 'short' in line.lower():
                    current_trade['action'] = 'short'
        
        # Add last trade
        if current_trade and 'symbol' in current_trade:
            report['trades'].append(current_trade)
        
        return report
    
    def save_report(self, report: Dict) -> str:
        """Save report to JSON file"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{timestamp}_chatgpt_report.json"
        filepath = os.path.join(self.research_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Report saved to {filepath}")
        return filepath
    
    def fetch_daily_report(self) -> Optional[str]:
        """Main method to fetch daily report"""
        driver = None
        try:
            # Setup driver
            driver = self.setup_driver()
            wait = WebDriverWait(driver, 10)
            
            # Load cookies
            driver.get('https://chatgpt.com')
            self.load_cookies(driver)
            driver.refresh()
            time.sleep(3)
            
            # Login if needed
            if not self.login_if_needed(driver, wait):
                return None
            
            # Navigate to conversation
            self.navigate_to_conversation(driver)
            
            # Extract report
            report = self.extract_latest_report(driver)
            
            if report and report['trades']:
                # Save report
                filepath = self.save_report(report)
                self.logger.info(f"Successfully fetched report with {len(report['trades'])} trades")
                return filepath
            else:
                self.logger.error("No valid report found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching report: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()


def main():
    """Run the fetcher"""
    import sys
    
    # Get conversation URL from command line or environment
    conversation_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    fetcher = ChatGPTSeleniumFetcher(conversation_url)
    filepath = fetcher.fetch_daily_report()
    
    if filepath:
        print(f"Report saved to: {filepath}")
    else:
        print("Failed to fetch report")


if __name__ == "__main__":
    main()