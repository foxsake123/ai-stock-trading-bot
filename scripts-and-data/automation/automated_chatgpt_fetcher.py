"""
Automated ChatGPT Trade Fetcher using Selenium
Automates the process of getting daily trade recommendations from ChatGPT
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutomatedChatGPTFetcher:
    def __init__(self, headless=False):
        """Initialize the automated ChatGPT fetcher"""
        self.project_root = Path(__file__).parent.parent.parent
        self.json_dir = self.project_root / 'scripts-and-data' / 'daily-json' / 'chatgpt'
        self.json_dir.mkdir(parents=True, exist_ok=True)

        # Chrome profile path for persistent login
        self.profile_dir = self.project_root / 'chrome_profile'
        self.profile_dir.mkdir(exist_ok=True)

        self.headless = headless
        self.driver = None

        # Trading prompt template
        self.trading_prompt = """You are TradingAgents, an expert AI trading system. Please analyze the market and provide today's trading recommendations in the following format:

## MARKET ANALYSIS
Brief market overview and key catalysts for today.

## DEE-BOT TRADES (S&P 100 Defensive)
Strategy: Beta-neutral, LONG-ONLY
| Symbol | Action | Shares | Entry | Stop | Target | Rationale |
|--------|--------|--------|-------|------|--------|-----------|
| [5 defensive stock recommendations]

## SHORGAN-BOT TRADES (Catalyst Trading)
Strategy: Event-driven momentum
| Symbol | Action | Shares | Entry | Stop | Target | Catalyst |
|--------|--------|--------|-------|------|--------|----------|
| [7-10 catalyst-driven recommendations]

Focus on:
- DEE-BOT: Dividend aristocrats, low volatility, beta ~1.0
- SHORGAN-BOT: Earnings, FDA events, short squeezes, momentum breakouts
- All prices should be realistic based on current market
- Include specific entry, stop loss, and target prices
- Position sizes appropriate for $100K portfolio each bot"""

    def setup_driver(self):
        """Setup Chrome driver with anti-detection and persistent profile"""
        try:
            # Use undetected Chrome to bypass anti-bot measures
            options = uc.ChromeOptions()

            # Use persistent profile to maintain login
            options.add_argument(f'--user-data-dir={str(self.profile_dir)}')
            options.add_argument('--profile-directory=Default')

            # Other options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')

            if self.headless:
                options.add_argument('--headless=new')

            # Window size for proper rendering
            options.add_argument('--window-size=1920,1080')

            # Initialize driver
            self.driver = uc.Chrome(options=options, version_main=None)
            self.wait = WebDriverWait(self.driver, 30)

            logging.info("Chrome driver initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to setup driver: {e}")
            return False

    def login_to_chatgpt(self):
        """Check if logged in to ChatGPT, prompt for manual login if needed"""
        try:
            logging.info("Navigating to ChatGPT...")
            self.driver.get("https://chatgpt.com")
            time.sleep(5)

            # Check if already logged in by looking for new chat button
            try:
                new_chat = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'New chat')]"))
                )
                logging.info("Already logged in to ChatGPT")
                return True
            except TimeoutException:
                pass

            # Check for login button
            try:
                login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
                logging.info("Not logged in. Manual login required.")

                if self.headless:
                    logging.error("Cannot login in headless mode. Please run without headless first.")
                    return False

                # Click login and wait for user to complete
                login_button.click()

                print("\n" + "="*60)
                print("MANUAL LOGIN REQUIRED")
                print("="*60)
                print("Please complete the login process in the browser window.")
                print("After logging in successfully, press ENTER here to continue...")
                print("="*60)

                input()  # Wait for user to complete login

                # Verify login successful
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'New chat')]"))
                    )
                    logging.info("Login successful!")
                    return True
                except TimeoutException:
                    logging.error("Login verification failed")
                    return False

            except NoSuchElementException:
                # Might already be on chat page
                return True

        except Exception as e:
            logging.error(f"Login process failed: {e}")
            return False

    def send_prompt_and_get_response(self):
        """Send trading prompt to ChatGPT and get response"""
        try:
            # Start new chat
            try:
                new_chat_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'New chat')]")
                new_chat_btn.click()
                time.sleep(2)
            except:
                pass  # Already in new chat

            # Find message input
            logging.info("Sending trading prompt...")

            # Multiple possible selectors for the input field
            input_selectors = [
                "//textarea[@id='prompt-textarea']",
                "//textarea[contains(@placeholder, 'Send a message')]",
                "//div[@contenteditable='true']"
            ]

            text_input = None
            for selector in input_selectors:
                try:
                    text_input = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if not text_input:
                logging.error("Could not find message input field")
                return None

            # Send prompt
            text_input.clear()
            text_input.send_keys(self.trading_prompt)
            time.sleep(1)
            text_input.send_keys(Keys.RETURN)

            logging.info("Waiting for ChatGPT response...")

            # Wait for response to complete (look for stop generating button to disappear)
            time.sleep(10)  # Initial wait

            # Wait until generation is complete
            max_wait = 60
            start_time = time.time()

            while time.time() - start_time < max_wait:
                try:
                    # Check if still generating
                    stop_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Stop generating')]")
                    time.sleep(2)  # Still generating, wait
                except:
                    # No stop button means generation complete
                    break

            time.sleep(3)  # Extra wait for render

            # Extract response
            response_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'markdown')]")

            if not response_elements:
                logging.error("No response found")
                return None

            # Get the last response (most recent)
            response_text = response_elements[-1].text

            logging.info(f"Received response with {len(response_text)} characters")

            return response_text

        except Exception as e:
            logging.error(f"Failed to get response: {e}")
            import traceback
            traceback.print_exc()
            return None

    def parse_trades_from_response(self, response_text):
        """Parse trade recommendations from ChatGPT response"""
        trades = []

        if not response_text:
            return trades

        lines = response_text.split('\n')

        for line in lines:
            if '|' not in line or line.startswith('|--'):
                continue

            parts = [p.strip() for p in line.split('|')]

            # Skip header rows
            if any(header in parts[0].upper() for header in ['SYMBOL', 'ACTION', 'TICKER']):
                continue

            if len(parts) >= 6:
                # Extract symbol (skip first empty element from split)
                symbol = parts[1] if len(parts) > 1 else ''

                # Validate symbol (1-5 uppercase letters)
                import re
                if re.match(r'^[A-Z]{1,5}$', symbol):
                    try:
                        trade = {
                            'symbol': symbol,
                            'action': parts[2] if len(parts) > 2 else 'BUY',
                            'shares': int(''.join(filter(str.isdigit, parts[3]))) if len(parts) > 3 else 100,
                            'entry': float(re.sub(r'[^0-9.]', '', parts[4])) if len(parts) > 4 else 0,
                            'stop': float(re.sub(r'[^0-9.]', '', parts[5])) if len(parts) > 5 else 0,
                            'target': float(re.sub(r'[^0-9.]', '', parts[6])) if len(parts) > 6 else 0,
                            'rationale': parts[7] if len(parts) > 7 else ''
                        }

                        # Validate prices
                        if trade['entry'] > 0:
                            trades.append(trade)

                    except (ValueError, IndexError):
                        continue

        logging.info(f"Parsed {len(trades)} trades from response")
        return trades

    def save_report(self, response_text, trades):
        """Save the ChatGPT report to JSON"""
        timestamp = datetime.now()

        report = {
            'date': timestamp.strftime('%Y-%m-%d'),
            'time': timestamp.strftime('%H:%M:%S'),
            'source': 'ChatGPT TradingAgents (Automated)',
            'trades': trades,
            'trade_count': len(trades),
            'raw_response': response_text[:50000],  # Limit size
            'extracted_at': timestamp.isoformat(),
            'automated': True
        }

        # Daily file (overwrites)
        daily_file = self.json_dir / f"chatgpt_report_{timestamp.strftime('%Y-%m-%d')}.json"
        with open(daily_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Timestamped backup
        backup_file = self.json_dir / f"chatgpt_report_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Report saved to {daily_file}")
        return daily_file

    def run(self):
        """Main execution function"""
        try:
            print("="*60)
            print("AUTOMATED CHATGPT TRADE FETCHER")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)

            # Setup driver
            if not self.setup_driver():
                return False

            # Login to ChatGPT
            if not self.login_to_chatgpt():
                return False

            # Send prompt and get response
            response = self.send_prompt_and_get_response()
            if not response:
                logging.error("Failed to get response from ChatGPT")
                return False

            # Parse trades
            trades = self.parse_trades_from_response(response)

            # Save report
            filepath = self.save_report(response, trades)

            print("\n" + "="*60)
            print("FETCH COMPLETE")
            print(f"Extracted {len(trades)} trades")
            print(f"Report saved to: {filepath}")
            print("="*60)

            # Display trades
            if trades:
                print("\nExtracted Trades:")
                for i, trade in enumerate(trades[:10], 1):
                    print(f"{i}. {trade['symbol']}: {trade['action']} @ ${trade.get('entry', 'N/A')}")

            return True

        except Exception as e:
            logging.error(f"Automation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.driver:
                self.driver.quit()

def schedule_daily_fetch():
    """Schedule the fetcher to run at specific times"""
    import schedule

    def job():
        fetcher = AutomatedChatGPTFetcher(headless=False)
        fetcher.run()

    # Schedule for 6:45 AM and 8:45 AM
    schedule.every().day.at("06:45").do(job)
    schedule.every().day.at("08:45").do(job)

    print("Scheduled ChatGPT fetcher for 6:45 AM and 8:45 AM daily")
    print("Press Ctrl+C to stop...")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        schedule_daily_fetch()
    else:
        # Run once immediately
        fetcher = AutomatedChatGPTFetcher(headless=False)
        success = fetcher.run()
        sys.exit(0 if success else 1)