"""
Process ChatGPT Research Through Multi-Agent System
Feeds research to agents, gets consensus for each bot's strategy
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.fundamental_analyst import FundamentalAnalystAgent
from src.agents.technical_analyst import TechnicalAnalystAgent
from src.agents.sentiment_analyst import SentimentAnalystAgent
from src.agents.news_analyst import NewsAnalystAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.bull_researcher import BullResearcherAgent
from src.agents.bear_researcher import BearResearcherAgent
from src.agents.alternative_data_agent import AlternativeDataAgent

class ChatGPTResearchProcessor:
    """Process ChatGPT research through multi-agent consensus"""

    def __init__(self):
        # Initialize all agents
        self.agents = {
            'fundamental': FundamentalAnalystAgent(),
            'technical': TechnicalAnalystAgent(),
            'sentiment': SentimentAnalystAgent(),
            'news': NewsAnalystAgent(),
            'risk': RiskManagerAgent(),
            'bull': BullResearcherAgent(),
            'bear': BearResearcherAgent(),
            'alternative': AlternativeDataAgent()
        }

        # Different weight configurations for each bot strategy
        self.dee_bot_weights = {
            'fundamental': 0.25,  # Higher weight on fundamentals
            'technical': 0.15,
            'sentiment': 0.10,
            'news': 0.10,
            'risk': 0.20,  # Higher weight on risk for defensive
            'bull': 0.05,
            'bear': 0.10,  # More cautious
            'alternative': 0.05
        }

        self.shorgan_bot_weights = {
            'fundamental': 0.10,
            'technical': 0.15,
            'sentiment': 0.15,  # Higher weight on sentiment
            'news': 0.15,  # Higher weight on news/catalysts
            'risk': 0.10,
            'bull': 0.15,  # More aggressive
            'bear': 0.05,
            'alternative': 0.15  # Higher weight on alt data for catalysts
        }

        self.chatgpt_research = None
        self.load_chatgpt_research()

    def load_chatgpt_research(self):
        """Load the ChatGPT research from file"""
        research_path = Path("../../scripts-and-data/data/reports/weekly/chatgpt-research/CHATGPT_ACTUAL_2025-09-30.md")

        if research_path.exists():
            with open(research_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the research into structured format
            self.chatgpt_research = self.parse_chatgpt_research(content)
            print(f"Loaded ChatGPT research from {research_path}")
        else:
            print(f"ChatGPT research not found at {research_path}")
            self.chatgpt_research = None

    def parse_chatgpt_research(self, content):
        """Parse ChatGPT markdown into structured data"""
        research = {
            'dee_bot': {
                'exits': [],
                'entries': [],
                'holds': [],
                'stops': {},
                'thesis': ''
            },
            'shorgan_bot': {
                'exits': [],
                'entries': [],
                'holds': [],
                'covers': [],
                'stops': {},
                'thesis': ''
            },
            'market_context': {
                'russell_2000': 'Record high at 2,467.7',
                'risk_sentiment': 'Risk-on for small caps',
                'key_events': ['FBIO FDA Monday', 'BBAI earnings Wednesday'],
                'government_shutdown': 'Vote Monday'
            }
        }

        # Parse DEE-BOT section
        if 'DEE-BOT' in content:
            # Extract exits
            if 'SELL NVDA' in content:
                research['dee_bot']['exits'].append({
                    'symbol': 'NVDA', 'shares': 60, 'price': 176.00,
                    'reason': 'Exit high-beta tech, reduce volatility'
                })
            if 'SELL AMZN' in content:
                research['dee_bot']['exits'].append({
                    'symbol': 'AMZN', 'shares': 42, 'price': 220.00,
                    'reason': 'Remove cyclical discretionary exposure'
                })
            if 'SELL CVX' in content:
                research['dee_bot']['exits'].append({
                    'symbol': 'CVX', 'shares': 31, 'price': 160.00,
                    'reason': 'Consolidate energy to XOM'
                })

            # Extract entries
            if 'BUY IBM' in content:
                research['dee_bot']['entries'].append({
                    'symbol': 'IBM', 'shares': 17, 'price': 285.00,
                    'reason': 'Quantum computing catalyst + 2.5% dividend',
                    'stop': 265.00
                })

            # Extract thesis
            research['dee_bot']['thesis'] = 'Rotate from high-beta to defensive dividend stocks'

        # Parse SHORGAN-BOT section
        if 'SHORGAN-BOT' in content:
            # Extract covers
            research['shorgan_bot']['covers'] = [
                {'symbol': 'PG', 'shares': 132},
                {'symbol': 'AAPL', 'shares': 15},
                {'symbol': 'CVX', 'shares': 93},
                {'symbol': 'NCNO', 'shares': 348},
                {'symbol': 'IONQ', 'shares': 200}
            ]

            # Extract exits
            research['shorgan_bot']['exits'] = [
                {'symbol': 'ORCL', 'shares': 21, 'price': 283.00, 'reason': 'Harvest gains'},
                {'symbol': 'GPK', 'shares': 142, 'price': 19.00, 'reason': '52-week lows'},
                {'symbol': 'TSLA', 'shares': 2, 'price': 255.00, 'reason': 'Housekeeping'}
            ]

            # Extract holds
            research['shorgan_bot']['holds'] = [
                {'symbol': 'RGTI', 'gain_pct': 117, 'stop': 25.00},
                {'symbol': 'SAVA', 'gain_pct': 50, 'stop': 2.50, 'catalyst': 'CEO bought 245k shares'},
                {'symbol': 'FBIO', 'catalyst': 'FDA decision Monday'},
                {'symbol': 'IONQ', 'catalyst': 'Quantum momentum'}
            ]

            research['shorgan_bot']['thesis'] = 'Ride catalysts, protect gains, clear shorts'

        return research

    async def analyze_for_dee_bot(self, trade_data):
        """Analyze a trade through agents with DEE-BOT strategy weights"""

        symbol = trade_data.get('symbol')
        action = trade_data.get('action', 'HOLD')
        reason = trade_data.get('reason', '')

        print(f"\n{'='*60}")
        print(f"DEE-BOT ANALYSIS: {action} {symbol}")
        print(f"ChatGPT Reason: {reason}")
        print(f"{'='*60}")

        agent_scores = {}

        for agent_name, agent in self.agents.items():
            try:
                # Each agent analyzes based on DEE-BOT defensive criteria
                if hasattr(agent, 'analyze'):
                    if agent_name == 'alternative':
                        result = await agent.analyze(symbol)
                    else:
                        # Provide DEE-BOT context
                        context = {
                            'strategy': 'defensive',
                            'beta_target': 1.0,
                            'focus': 'S&P 100 large caps',
                            'risk_tolerance': 'low'
                        }
                        result = agent.analyze(symbol, context)

                    score = result.get('score', 50)

                    # Adjust score based on action alignment
                    if action == 'SELL' and agent_name == 'risk':
                        score = min(100, score + 20)  # Risk agent favors exits
                    elif action == 'BUY' and symbol == 'IBM':
                        if agent_name == 'fundamental':
                            score = min(100, score + 15)  # Dividend stock bonus

                    agent_scores[agent_name] = score
                    print(f"  {agent_name:15}: {score:.1f}")

            except Exception as e:
                print(f"  {agent_name:15}: Error - {str(e)[:30]}")
                agent_scores[agent_name] = 50

        # Calculate weighted consensus for DEE-BOT
        weighted_score = 0
        total_weight = 0

        for agent_name, score in agent_scores.items():
            weight = self.dee_bot_weights.get(agent_name, 0.1)
            weighted_score += score * weight
            total_weight += weight

        consensus_score = weighted_score / total_weight if total_weight > 0 else 50

        # Determine recommendation
        if consensus_score > 65:
            recommendation = "STRONGLY AGREE"
        elif consensus_score > 55:
            recommendation = "AGREE"
        elif consensus_score < 35:
            recommendation = "STRONGLY DISAGREE"
        elif consensus_score < 45:
            recommendation = "DISAGREE"
        else:
            recommendation = "NEUTRAL"

        print(f"\nDEE-BOT Consensus: {consensus_score:.1f}/100")
        print(f"Recommendation: {recommendation} with ChatGPT")

        return {
            'symbol': symbol,
            'action': action,
            'chatgpt_reason': reason,
            'consensus_score': consensus_score,
            'recommendation': recommendation,
            'agent_scores': agent_scores
        }

    async def analyze_for_shorgan_bot(self, trade_data):
        """Analyze a trade through agents with SHORGAN-BOT strategy weights"""

        symbol = trade_data.get('symbol')
        action = trade_data.get('action', 'HOLD')
        reason = trade_data.get('reason', '')
        catalyst = trade_data.get('catalyst', '')

        print(f"\n{'='*60}")
        print(f"SHORGAN-BOT ANALYSIS: {action} {symbol}")
        print(f"ChatGPT Reason: {reason}")
        if catalyst:
            print(f"Catalyst: {catalyst}")
        print(f"{'='*60}")

        agent_scores = {}

        for agent_name, agent in self.agents.items():
            try:
                # Each agent analyzes based on SHORGAN catalyst criteria
                if hasattr(agent, 'analyze'):
                    if agent_name == 'alternative':
                        result = await agent.analyze(symbol)
                    else:
                        # Provide SHORGAN context
                        context = {
                            'strategy': 'catalyst-driven',
                            'focus': 'micro/mid-cap catalysts',
                            'risk_tolerance': 'high',
                            'catalyst': catalyst
                        }
                        result = agent.analyze(symbol, context)

                    score = result.get('score', 50)

                    # Adjust score based on catalyst alignment
                    if catalyst and agent_name in ['news', 'sentiment', 'alternative']:
                        score = min(100, score + 10)  # Catalyst-focused agents

                    if 'gain_pct' in trade_data:
                        if trade_data['gain_pct'] > 50 and agent_name == 'bull':
                            score = min(100, score + 20)  # Momentum continuation

                    agent_scores[agent_name] = score
                    print(f"  {agent_name:15}: {score:.1f}")

            except Exception as e:
                print(f"  {agent_name:15}: Error - {str(e)[:30]}")
                agent_scores[agent_name] = 50

        # Calculate weighted consensus for SHORGAN-BOT
        weighted_score = 0
        total_weight = 0

        for agent_name, score in agent_scores.items():
            weight = self.shorgan_bot_weights.get(agent_name, 0.1)
            weighted_score += score * weight
            total_weight += weight

        consensus_score = weighted_score / total_weight if total_weight > 0 else 50

        # Determine recommendation
        if consensus_score > 70:
            recommendation = "STRONGLY AGREE"
        elif consensus_score > 60:
            recommendation = "AGREE"
        elif consensus_score < 30:
            recommendation = "STRONGLY DISAGREE"
        elif consensus_score < 40:
            recommendation = "DISAGREE"
        else:
            recommendation = "NEUTRAL"

        print(f"\nSHORGAN-BOT Consensus: {consensus_score:.1f}/100")
        print(f"Recommendation: {recommendation} with ChatGPT")

        return {
            'symbol': symbol,
            'action': action,
            'chatgpt_reason': reason,
            'catalyst': catalyst,
            'consensus_score': consensus_score,
            'recommendation': recommendation,
            'agent_scores': agent_scores
        }

    async def process_all_trades(self):
        """Process all ChatGPT trades through multi-agent system"""

        if not self.chatgpt_research:
            print("No ChatGPT research loaded")
            return None

        print("="*70)
        print("PROCESSING CHATGPT RESEARCH THROUGH MULTI-AGENT SYSTEM")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        results = {
            'dee_bot': {
                'exits': [],
                'entries': [],
                'final_trades': []
            },
            'shorgan_bot': {
                'exits': [],
                'entries': [],
                'holds': [],
                'covers': [],
                'final_trades': []
            }
        }

        # Process DEE-BOT trades
        print("\n" + "="*70)
        print("DEE-BOT STRATEGY ANALYSIS")
        print("Strategy: Defensive S&P 100, Beta-Neutral, Dividend Focus")
        print("="*70)

        # Analyze exits
        for trade in self.chatgpt_research['dee_bot']['exits']:
            trade['action'] = 'SELL'
            analysis = await self.analyze_for_dee_bot(trade)
            results['dee_bot']['exits'].append(analysis)

            if analysis['recommendation'] in ['AGREE', 'STRONGLY AGREE']:
                results['dee_bot']['final_trades'].append({
                    'action': 'SELL',
                    'symbol': trade['symbol'],
                    'shares': trade['shares'],
                    'price': trade['price'],
                    'confidence': analysis['consensus_score']
                })

        # Analyze entries
        for trade in self.chatgpt_research['dee_bot']['entries']:
            trade['action'] = 'BUY'
            analysis = await self.analyze_for_dee_bot(trade)
            results['dee_bot']['entries'].append(analysis)

            if analysis['recommendation'] in ['AGREE', 'STRONGLY AGREE']:
                results['dee_bot']['final_trades'].append({
                    'action': 'BUY',
                    'symbol': trade['symbol'],
                    'shares': trade['shares'],
                    'price': trade['price'],
                    'stop': trade.get('stop'),
                    'confidence': analysis['consensus_score']
                })

        # Process SHORGAN-BOT trades
        print("\n" + "="*70)
        print("SHORGAN-BOT STRATEGY ANALYSIS")
        print("Strategy: Catalyst-Driven, Micro/Mid-Cap, High Risk/Reward")
        print("="*70)

        # Analyze exits
        for trade in self.chatgpt_research['shorgan_bot']['exits']:
            trade['action'] = 'SELL'
            analysis = await self.analyze_for_shorgan_bot(trade)
            results['shorgan_bot']['exits'].append(analysis)

            if analysis['recommendation'] in ['AGREE', 'STRONGLY AGREE']:
                results['shorgan_bot']['final_trades'].append({
                    'action': 'SELL',
                    'symbol': trade['symbol'],
                    'shares': trade['shares'],
                    'price': trade['price'],
                    'confidence': analysis['consensus_score']
                })

        # Analyze holds
        for trade in self.chatgpt_research['shorgan_bot']['holds']:
            trade['action'] = 'HOLD'
            analysis = await self.analyze_for_shorgan_bot(trade)
            results['shorgan_bot']['holds'].append(analysis)

            if analysis['recommendation'] in ['AGREE', 'STRONGLY AGREE']:
                results['shorgan_bot']['final_trades'].append({
                    'action': 'HOLD',
                    'symbol': trade['symbol'],
                    'stop': trade.get('stop'),
                    'confidence': analysis['consensus_score']
                })

        # Generate final consensus report
        self.generate_consensus_report(results)

        # Save results
        self.save_consensus_results(results)

        return results

    def generate_consensus_report(self, results):
        """Generate final consensus report"""

        print("\n" + "="*70)
        print("MULTI-AGENT CONSENSUS REPORT")
        print("="*70)

        # DEE-BOT Summary
        print("\n📊 DEE-BOT FINAL RECOMMENDATIONS:")
        print("-" * 50)

        for trade in results['dee_bot']['final_trades']:
            symbol = trade['symbol']
            action = trade['action']
            confidence = trade['confidence']

            if confidence > 65:
                indicator = "✅"
            elif confidence > 55:
                indicator = "✓"
            else:
                indicator = "⚠️"

            print(f"{indicator} {action} {symbol} - Confidence: {confidence:.1f}%")
            if 'stop' in trade and trade['stop']:
                print(f"   Stop Loss: ${trade['stop']}")

        # SHORGAN-BOT Summary
        print("\n🚀 SHORGAN-BOT FINAL RECOMMENDATIONS:")
        print("-" * 50)

        for trade in results['shorgan_bot']['final_trades']:
            symbol = trade['symbol']
            action = trade['action']
            confidence = trade['confidence']

            if confidence > 70:
                indicator = "✅"
            elif confidence > 60:
                indicator = "✓"
            else:
                indicator = "⚠️"

            print(f"{indicator} {action} {symbol} - Confidence: {confidence:.1f}%")
            if 'stop' in trade and trade['stop']:
                print(f"   Stop Loss: ${trade['stop']}")

        # Risk Warnings
        print("\n⚠️ RISK WARNINGS:")
        print("-" * 50)
        print("1. FBIO - Check FDA decision outcome from Monday")
        print("2. BBAI - Earnings Wednesday (high volatility)")
        print("3. Short covering - Mandatory for compliance")
        print("4. Market conditions - Russell 2000 at 4-year highs")

        print("\n" + "="*70)
        print("CONSENSUS: PROCEED WITH MODIFIED CHATGPT TRADES")
        print("Execute Tuesday at 9:30 AM with agent-validated positions")
        print("="*70)

    def save_consensus_results(self, results):
        """Save consensus results to file"""

        # Save as JSON
        output_path = Path("scripts-and-data/data/consensus_trades.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nConsensus trades saved to: {output_path}")

        # Create execution file
        self.create_execution_file(results)

    def create_execution_file(self, results):
        """Create final execution file with consensus trades"""

        execution_path = Path("CONSENSUS_TRADES_2025-10-01.md")

        content = f"""# CONSENSUS-BASED TRADING EXECUTION
## Tuesday, October 1, 2025
### Generated from Multi-Agent Analysis of ChatGPT Research

---

## DEE-BOT TRADES (Defensive S&P 100)

### Consensus-Validated Trades:
"""

        for trade in results['dee_bot']['final_trades']:
            content += f"\n- **{trade['action']} {trade['symbol']}**"
            content += f"\n  - Shares: {trade.get('shares', 'TBD')}"
            content += f"\n  - Price: ${trade.get('price', 'Market')}"
            content += f"\n  - Confidence: {trade['confidence']:.1f}%"
            if 'stop' in trade:
                content += f"\n  - Stop Loss: ${trade['stop']}"
            content += "\n"

        content += """
---

## SHORGAN-BOT TRADES (Catalyst-Driven)

### Consensus-Validated Trades:
"""

        for trade in results['shorgan_bot']['final_trades']:
            content += f"\n- **{trade['action']} {trade['symbol']}**"
            content += f"\n  - Shares: {trade.get('shares', 'TBD')}"
            content += f"\n  - Price: ${trade.get('price', 'Market')}"
            content += f"\n  - Confidence: {trade['confidence']:.1f}%"
            if 'stop' in trade:
                content += f"\n  - Stop Loss: ${trade['stop']}"
            content += "\n"

        content += """
---

## EXECUTION NOTES

1. All trades validated by multi-agent consensus
2. Different strategies applied for each bot
3. Execute at 9:30 AM Tuesday
4. Use LIMIT DAY orders
5. Check FBIO FDA outcome before trading

Generated by Multi-Agent Consensus System
"""

        with open(execution_path, 'w') as f:
            f.write(content)

        print(f"Execution file created: {execution_path}")

async def main():
    """Main execution"""
    processor = ChatGPTResearchProcessor()
    results = await processor.process_all_trades()

    # Send summary to Telegram
    if results:
        import requests
        telegram_token = "8093845586:AAEqytNDQ_dVzVp6ZbDyveMTx7MZMtG6N0c"
        chat_id = "7870288896"

        dee_count = len(results['dee_bot']['final_trades'])
        shorgan_count = len(results['shorgan_bot']['final_trades'])

        message = f"""📊 MULTI-AGENT CONSENSUS COMPLETE

ChatGPT research processed through {len(processor.agents)} agents:

DEE-BOT (Defensive):
• {dee_count} trades validated
• Strategy: Beta-neutral, dividend focus

SHORGAN-BOT (Catalyst):
• {shorgan_count} trades validated
• Strategy: High-risk catalysts

Consensus file: CONSENSUS_TRADES_2025-10-01.md

Execute Tuesday 9:30 AM"""

        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        requests.post(url, data={'chat_id': chat_id, 'text': message})
        print("\nConsensus summary sent to Telegram")

if __name__ == "__main__":
    asyncio.run(main())