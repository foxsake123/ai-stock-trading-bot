"""
Generate Weekly Deep Research Prompt for ChatGPT
Creates the properly formatted prompt with current portfolio data
"""

from alpaca.trading.client import TradingClient
from datetime import datetime
import json

# API credentials
DEE_BOT_KEY = "PK6FZK4DAQVTD7DYVH78"
DEE_BOT_SECRET = "JKHXnsi4GeZV5GiA06kGyMhRrvrfEjOzw5X7bHBt"

SHORGAN_BOT_KEY = "PKJRLSB2MFEJUSK6UK2E"
SHORGAN_BOT_SECRET = "QBpREJmZ7HgHS1tHptvHgwjH4MtjFSoEcQ0wmGic"

def get_portfolio_state(api_key, secret_key, bot_name):
    """Get current portfolio state for a bot"""

    client = TradingClient(api_key, secret_key, paper=True)
    account = client.get_account()
    positions = client.get_all_positions()

    portfolio = {
        'cash': float(account.cash),
        'total_equity': float(account.equity),
        'positions': []
    }

    for pos in positions:
        portfolio['positions'].append({
            'symbol': pos.symbol,
            'qty': int(pos.qty),
            'avg_cost': float(pos.avg_entry_price),
            'current_price': float(pos.current_price),
            'unrealized_pnl': float(pos.unrealized_pl),
            'market_value': float(pos.market_value)
        })

    return portfolio

def generate_weekly_prompt(bot_type='shorgan'):
    """Generate the weekly deep research prompt"""

    # Calculate week number (assuming start date of Sept 1, 2025)
    start_date = datetime(2025, 9, 1)
    current_date = datetime.now()
    week_number = ((current_date - start_date).days // 7) + 1
    day_of_week = current_date.strftime('%A')

    # Get portfolio data
    if bot_type == 'dee':
        portfolio = get_portfolio_state(DEE_BOT_KEY, DEE_BOT_SECRET, 'DEE-BOT')
        strategy = "Beta-Neutral S&P 100 Defense"
        universe = "S&P 100 large-cap stocks for defensive positioning"
    else:
        portfolio = get_portfolio_state(SHORGAN_BOT_KEY, SHORGAN_BOT_SECRET, 'SHORGAN-BOT')
        strategy = "Catalyst-Driven Micro-Cap Offense"
        universe = "U.S. micro-caps under 300M market cap with catalysts"

    # Format holdings block
    holdings_lines = []
    for pos in portfolio['positions']:
        holdings_lines.append(
            f"{pos['symbol']}: {pos['qty']} shares @ ${pos['avg_cost']:.2f}, "
            f"current ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pnl']:.2f}"
        )
    holdings_block = '\n'.join(holdings_lines) if holdings_lines else "No current positions"

    # Format snapshot block
    snapshot_block = f"""Cash Available: ${portfolio['cash']:,.2f}
Total Equity: ${portfolio['total_equity']:,.2f}
Number of Positions: {len(portfolio['positions'])}
Strategy: {strategy}"""

    # Last thesis (placeholder - would read from storage)
    last_thesis = """Previous thesis: Maintain defensive positioning in large-cap tech while
monitoring catalyst opportunities in micro-cap space. Focus on FDA decisions, earnings
catalysts, and momentum plays."""

    # Generate the prompt
    prompt = f"""SYSTEM MESSAGE

You are a professional-grade portfolio analyst operating in Deep Research Mode for {bot_type.upper()}-BOT. Your job is to reevaluate the portfolio and produce a complete action plan with exact orders. Optimize risk-adjusted return under strict constraints. Begin by restating the rules to confirm understanding, then deliver your research, decisions, and orders.

Core Rules
- Budget discipline: no new capital beyond what is shown. Track cash precisely.
- Execution limits: full shares only. No options, shorting, leverage, margin, or derivatives. Long-only.
- Universe: {universe}
- Risk control: respect provided stop-loss levels and position sizing. Flag any breaches immediately.
- Cadence: this is the weekly deep research window. You may add new names, exit, trim, or add to positions.
- Complete freedom: you have complete control to act in your best interest to generate alpha.

Deep Research Requirements
- Reevaluate current holdings and consider new candidates.
- Build a clear rationale for every keep, add, trim, exit, and new entry.
- Provide exact order details for every proposed trade.
- Confirm liquidity and risk checks before finalizing orders.
- End with a short thesis review summary for next week.

Order Specification Format
Action: buy or sell
Ticker: symbol
Shares: integer (full shares only)
Order type: limit preferred, or market with reasoning
Limit price: exact number
Time in force: DAY or GTC
Intended execution date: {current_date.strftime('%Y-%m-%d')}
Stop loss (for buys): exact number and placement logic
Special instructions: if needed
One-line rationale

USER MESSAGE

Context
It is Week {week_number} {day_of_week} of a 6-month live experiment.

Cash Available
${portfolio['cash']:,.2f}

Current Portfolio State
[ Holdings ]
{holdings_block}

[ Snapshot ]
{snapshot_block}

Last Analyst Thesis For Current Holdings
{last_thesis}

Execution Policy
Orders will be executed via Alpaca API as limit DAY orders placed for the next trading session.

Constraints And Reminders To Enforce
- Hard budget. Use only available cash shown above. No new capital.
- Full shares only. No options/shorting/margin/derivatives.
- {universe}
- Be sure to use up-to-date stock data for pricing details.
- Maintain or set stop-losses on all long positions.
- This is the weekly deep research window. You should present complete decisions and orders now.

What I Want From Your Reply
- Restated Rules
- Research Scope
- Current Portfolio Assessment
- Candidate Set
- Portfolio Actions
- Exact Orders
- Risk And Liquidity Checks
- Monitoring Plan
- Thesis Review Summary
- Cash After Trades

Please provide your complete weekly deep research analysis now."""

    return prompt

def save_prompt(prompt, bot_type):
    """Save prompt to file"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'../../weekly-reports/prompts/weekly_prompt_{bot_type}_{timestamp}.txt'

    # Create directory
    import os
    os.makedirs('../../weekly-reports/prompts', exist_ok=True)

    with open(filename, 'w') as f:
        f.write(prompt)

    return filename

def main():
    """Generate weekly prompts for both bots"""

    print("="*70)
    print("    WEEKLY DEEP RESEARCH PROMPT GENERATOR")
    print("="*70)
    print(f"\nGenerating prompts for week ending {datetime.now().strftime('%Y-%m-%d')}")

    # Generate DEE-BOT prompt
    print("\n[1/2] Generating DEE-BOT prompt...")
    dee_prompt = generate_weekly_prompt('dee')
    dee_file = save_prompt(dee_prompt, 'dee')
    print(f"  Saved to: {dee_file}")

    # Generate SHORGAN-BOT prompt
    print("\n[2/2] Generating SHORGAN-BOT prompt...")
    shorgan_prompt = generate_weekly_prompt('shorgan')
    shorgan_file = save_prompt(shorgan_prompt, 'shorgan')
    print(f"  Saved to: {shorgan_file}")

    print("\n" + "="*70)
    print("INSTRUCTIONS:")
    print("="*70)
    print("1. Open the saved prompt files")
    print("2. Copy the entire content")
    print("3. Paste into ChatGPT (use appropriate GPT for each bot)")
    print("4. Copy ChatGPT's response")
    print("5. Run: python chatgpt_weekly_extractor.py")
    print("6. Paste the response and type 'DONE'")

    print("\n[TIP] The prompts include current portfolio positions and cash!")

    # Show quick summary
    print("\n" + "-"*70)
    print("CURRENT PORTFOLIO SUMMARY")
    print("-"*70)

    try:
        dee_portfolio = get_portfolio_state(DEE_BOT_KEY, DEE_BOT_SECRET, 'DEE-BOT')
        print(f"\nDEE-BOT:")
        print(f"  Cash: ${dee_portfolio['cash']:,.2f}")
        print(f"  Positions: {len(dee_portfolio['positions'])}")
        print(f"  Total Equity: ${dee_portfolio['total_equity']:,.2f}")
    except:
        print("  [Error fetching DEE-BOT data]")

    try:
        shorgan_portfolio = get_portfolio_state(SHORGAN_BOT_KEY, SHORGAN_BOT_SECRET, 'SHORGAN-BOT')
        print(f"\nSHORGAN-BOT:")
        print(f"  Cash: ${shorgan_portfolio['cash']:,.2f}")
        print(f"  Positions: {len(shorgan_portfolio['positions'])}")
        print(f"  Total Equity: ${shorgan_portfolio['total_equity']:,.2f}")
    except:
        print("  [Error fetching SHORGAN-BOT data]")

if __name__ == "__main__":
    main()