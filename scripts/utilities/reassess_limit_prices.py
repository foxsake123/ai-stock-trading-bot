#!/usr/bin/env python3
"""
Reassess Open Orders with Flexible Limit Prices
Check current market prices and adjust limits for better fill probability
"""

import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

dee_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_DEE'),
    os.getenv('ALPACA_SECRET_KEY_DEE'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

shorgan_api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY_SHORGAN'),
    os.getenv('ALPACA_SECRET_KEY_SHORGAN'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)

def get_current_price(api, symbol):
    """Get current market price"""
    try:
        # Try to get latest trade
        trade = api.get_latest_trade(symbol)
        return float(trade.price)
    except:
        try:
            # Fallback to quote
            quote = api.get_latest_quote(symbol)
            bid = float(quote.bid_price)
            ask = float(quote.ask_price)
            return (bid + ask) / 2
        except Exception as e:
            print(f"  [ERROR] Could not get price for {symbol}: {e}")
            return None

def analyze_limit_adjustment(symbol, current_limit, current_price, side='buy'):
    """
    Determine if limit price should be adjusted
    Returns: (should_adjust, new_limit, reasoning)
    """
    if current_price is None:
        return False, current_limit, "No current price available"

    if side == 'buy':
        # For buys, we want to be competitive but not overpay
        pct_diff = ((current_price - current_limit) / current_limit) * 100

        if pct_diff > 5:
            # Market price is >5% above our limit - unlikely to fill
            # Suggest raising limit to 2% above current price
            new_limit = round(current_price * 1.02, 2)
            reasoning = f"Market moved {pct_diff:.1f}% above limit. Raising to {new_limit:.2f} (+2% buffer)"
            return True, new_limit, reasoning

        elif pct_diff > 2:
            # Market price is 2-5% above - might not fill
            new_limit = round(current_price * 1.01, 2)
            reasoning = f"Market {pct_diff:.1f}% above limit. Raising to {new_limit:.2f} (+1% buffer)"
            return True, new_limit, reasoning

        elif pct_diff < -3:
            # Our limit is 3%+ above market - lower it to get better price
            new_limit = round(current_price * 1.005, 2)
            reasoning = f"Limit {abs(pct_diff):.1f}% above market. Lowering to {new_limit:.2f} for better entry"
            return True, new_limit, reasoning

        else:
            # Limit is reasonable (-3% to +2%)
            return False, current_limit, f"Limit within range (market {pct_diff:+.1f}%)"

    return False, current_limit, "No adjustment needed"

def reassess_orders(api, bot_name):
    """Reassess all open orders for a bot"""
    print(f"\n{'='*80}")
    print(f"{bot_name} - LIMIT PRICE REASSESSMENT")
    print(f"{'='*80}")

    orders = api.list_orders(status='open')

    if not orders:
        print(f"\nNo open orders for {bot_name}")
        return

    print(f"\nFound {len(orders)} open order(s)")

    recommendations = []

    for order in orders:
        print(f"\n{'-'*80}")
        print(f"Order: {order.side.upper()} {order.qty} {order.symbol} @ ${order.limit_price}")
        print(f"Status: {order.status}")
        print(f"Created: {order.created_at}")

        # Get current price
        current_price = get_current_price(api, order.symbol)

        if current_price:
            print(f"Current Market Price: ${current_price:.2f}")

            # Analyze if adjustment needed
            should_adjust, new_limit, reasoning = analyze_limit_adjustment(
                order.symbol,
                float(order.limit_price),
                current_price,
                order.side
            )

            print(f"Analysis: {reasoning}")

            if should_adjust:
                recommendations.append({
                    'order': order,
                    'current_limit': float(order.limit_price),
                    'new_limit': new_limit,
                    'current_price': current_price,
                    'reasoning': reasoning
                })
                print(f"[RECOMMENDATION] Adjust limit: ${order.limit_price} -> ${new_limit:.2f}")
            else:
                print(f"[OK] Keep current limit: ${order.limit_price}")

    return recommendations

def apply_adjustments(api, recommendations, bot_name):
    """Apply recommended limit price adjustments"""
    if not recommendations:
        print(f"\n[INFO] No adjustments needed for {bot_name}")
        return

    print(f"\n{'='*80}")
    print(f"APPLYING ADJUSTMENTS - {bot_name}")
    print(f"{'='*80}")

    for rec in recommendations:
        order = rec['order']
        old_limit = rec['current_limit']
        new_limit = rec['new_limit']

        print(f"\n{order.symbol}:")
        print(f"  Current: {order.side.upper()} {order.qty} @ ${old_limit}")
        print(f"  New:     {order.side.upper()} {order.qty} @ ${new_limit:.2f}")
        print(f"  Reason:  {rec['reasoning']}")

        try:
            # Cancel old order
            api.cancel_order(order.id)
            print(f"  [1/2] Canceled old order: {order.id}")

            # Place new order with adjusted limit
            new_order = api.submit_order(
                symbol=order.symbol,
                qty=order.qty,
                side=order.side,
                type='limit',
                time_in_force='day',
                limit_price=str(new_limit)
            )
            print(f"  [2/2] Placed new order: {new_order.id}")
            print(f"  [SUCCESS] Limit adjusted: ${old_limit} -> ${new_limit:.2f}")

        except Exception as e:
            print(f"  [ERROR] Failed to adjust {order.symbol}: {e}")

def main():
    """Main execution"""
    print("="*80)
    print("OPEN ORDERS - LIMIT PRICE REASSESSMENT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*80)

    # Reassess DEE-BOT orders
    dee_recs = reassess_orders(dee_api, "DEE-BOT")

    # Reassess SHORGAN-BOT orders
    shorgan_recs = reassess_orders(shorgan_api, "SHORGAN-BOT")

    # Summary
    print("\n" + "="*80)
    print("REASSESSMENT SUMMARY")
    print("="*80)

    total_recs = (len(dee_recs) if dee_recs else 0) + (len(shorgan_recs) if shorgan_recs else 0)

    if total_recs == 0:
        print("\n[OK] All limit prices are appropriate. No adjustments needed.")
        return

    print(f"\nTotal recommendations: {total_recs}")

    # Ask for confirmation (auto-apply in this case)
    print("\nApplying adjustments...")

    if dee_recs:
        apply_adjustments(dee_api, dee_recs, "DEE-BOT")

    if shorgan_recs:
        apply_adjustments(shorgan_api, shorgan_recs, "SHORGAN-BOT")

    print("\n" + "="*80)
    print("LIMIT PRICE ADJUSTMENTS COMPLETE")
    print("="*80)
    print("\nOrders have been updated with flexible limit prices.")
    print("They will execute at market open (9:30 AM ET).")

if __name__ == "__main__":
    main()
