"""
Verify DEE-BOT API Trading Permissions
Tests if API keys have proper trading permissions
"""

import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

def verify_dee_trading():
    """Test DEE-BOT API trading permissions"""

    print("=" * 80)
    print("DEE-BOT API PERMISSION VERIFICATION")
    print("=" * 80)
    print()

    # Load credentials
    load_dotenv()
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

    print(f"API Key: {api_key[:10]}... (DEE-BOT)")
    print(f"Base URL: {base_url}")
    print()

    # Initialize API
    try:
        api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        print("✅ API client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return False

    # Test 1: Get Account (Read Permission)
    print()
    print("Test 1: Account Read Permission")
    print("-" * 80)
    try:
        account = api.get_account()
        print(f"✅ Account Status: {account.status}")
        print(f"✅ Cash: ${float(account.cash):,.2f}")
        print(f"✅ Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   Trading Blocked: {account.trading_blocked}")
        print(f"   Account Blocked: {account.account_blocked}")

        if account.trading_blocked:
            print("❌ WARNING: Trading is BLOCKED on this account!")
            return False

        if account.account_blocked:
            print("❌ WARNING: Account is BLOCKED!")
            return False

    except Exception as e:
        print(f"❌ Failed to read account: {e}")
        return False

    # Test 2: List Positions (Read Permission)
    print()
    print("Test 2: Positions Read Permission")
    print("-" * 80)
    try:
        positions = api.list_positions()
        print(f"✅ Positions retrieved: {len(positions)} positions")
        if positions:
            for p in positions[:3]:
                print(f"   - {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):.2f}")
    except Exception as e:
        print(f"❌ Failed to read positions: {e}")
        return False

    # Test 3: Get Orders (Read Permission)
    print()
    print("Test 3: Orders Read Permission")
    print("-" * 80)
    try:
        orders = api.list_orders(status='open', limit=10)
        print(f"✅ Orders retrieved: {len(orders)} open orders")
        if orders:
            for o in orders[:3]:
                print(f"   - {o.symbol}: {o.side} {o.qty} @ ${float(o.limit_price) if o.limit_price else 'market'}")
    except Exception as e:
        print(f"❌ Failed to read orders: {e}")
        return False

    # Test 4: Submit Order (TRADING Permission) - DRY RUN
    print()
    print("Test 4: Trading Permission (Dry Run)")
    print("-" * 80)
    print("Testing order submission with SPY (will cancel immediately)...")

    try:
        # Submit a small test order
        test_order = api.submit_order(
            symbol='SPY',
            qty=1,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=1.00  # Intentionally low - won't fill
        )
        print(f"✅ TEST ORDER SUBMITTED: {test_order.id}")
        print(f"   Symbol: {test_order.symbol}")
        print(f"   Side: {test_order.side}")
        print(f"   Qty: {test_order.qty}")
        print(f"   Status: {test_order.status}")

        # Cancel immediately
        try:
            api.cancel_order(test_order.id)
            print(f"✅ TEST ORDER CANCELLED: {test_order.id}")
        except:
            print(f"⚠️  Could not cancel (may have filled or already cancelled)")

    except Exception as e:
        error_msg = str(e)
        if 'unauthorized' in error_msg.lower():
            print(f"❌ TRADING PERMISSION DENIED: {e}")
            print()
            print("=" * 80)
            print("DIAGNOSIS: API keys are READ-ONLY")
            print("=" * 80)
            print("Your API keys can read data but CANNOT place trades.")
            print()
            print("FIX:")
            print("1. Go to https://app.alpaca.markets/ (DEE-BOT account)")
            print("2. Navigate to API Keys section")
            print("3. Generate NEW API key with 'Trading' permission ENABLED")
            print("4. Run: python update_dee_keys.py")
            print("5. Run this script again to verify")
            print()
            return False
        else:
            print(f"❌ Order submission failed: {e}")
            return False

    # All tests passed
    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED - API HAS FULL TRADING PERMISSIONS")
    print("=" * 80)
    print()
    print("You can now execute DEE-BOT orders with these credentials.")
    print("Run: python execute_dee_orders.py")
    print()
    return True

if __name__ == '__main__':
    success = verify_dee_trading()
    exit(0 if success else 1)
