#!/usr/bin/env python3
"""
Debug script to test multi-agent validation system
Shows detailed agent-by-agent analysis
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from scripts.automation.report_parser import ExternalReportParser, StockRecommendation
from scripts.automation.generate_todays_trades_v2 import MultiAgentTradeValidator

def test_validation():
    """Test validation on a sample trade"""

    # Create a sample recommendation
    test_rec = StockRecommendation(
        ticker="AAPL",
        action="BUY",
        shares=50,
        entry_price=175.0,
        stop_loss=160.0,
        target_price=200.0,
        rationale="Strong fundamentals, AI growth catalyst",
        conviction="MEDIUM",
        bot="DEE-BOT"
    )

    print("=" * 80)
    print("MULTI-AGENT VALIDATION DEBUG")
    print("=" * 80)
    print(f"\nTest Trade: {test_rec.action} {test_rec.shares} {test_rec.ticker} @ ${test_rec.entry_price}")
    print(f"Conviction: {test_rec.conviction}")
    print(f"Rationale: {test_rec.rationale}")
    print()

    # Initialize validator
    print("[*] Initializing MultiAgentTradeValidator...")
    validator = MultiAgentTradeValidator()

    # Check agents
    print(f"[*] Agents initialized: {len(validator.agents)}")
    for agent_id, agent in validator.agents.items():
        print(f"    - {agent_id:15s}: {type(agent).__name__}")
    print()

    # Get agent analyses
    print("[*] Requesting agent analyses...")
    print()

    analyses = validator.coordinator.get_agent_analyses(
        test_rec.ticker,
        test_rec.action
    )

    print(f"[*] Received {len(analyses)} analyses")
    print()

    # Show each agent's analysis
    print("-" * 80)
    print("AGENT-BY-AGENT ANALYSIS")
    print("-" * 80)

    if not analyses:
        print("[ERROR] No agent analyses returned!")
        print("This means agents are NOT being called or are failing silently")
    else:
        for agent_id, analysis in analyses.items():
            print(f"\n{agent_id.upper()}:")
            print(f"  Type: {type(analysis)}")

            # Try to extract action and confidence
            if isinstance(analysis, dict):
                recommendation = analysis.get('recommendation', {})
                if isinstance(recommendation, dict):
                    action = recommendation.get('action', 'UNKNOWN')
                    confidence = recommendation.get('confidence', 0)
                    reasoning = recommendation.get('reasoning', 'N/A')
                else:
                    action = analysis.get('action', 'UNKNOWN')
                    confidence = analysis.get('confidence', 0)
                    reasoning = analysis.get('reasoning', 'N/A')

                print(f"  Action: {action}")
                print(f"  Confidence: {confidence:.0%}")
                print(f"  Reasoning: {reasoning[:150]}")
            elif hasattr(analysis, 'action') and hasattr(analysis, 'confidence'):
                print(f"  Action: {analysis.action.value if hasattr(analysis.action, 'value') else analysis.action}")
                print(f"  Confidence: {analysis.confidence:.0%}")
                if hasattr(analysis, 'reasoning'):
                    print(f"  Reasoning: {analysis.reasoning[:150]}")
            else:
                print(f"  Unknown format: {analysis}")

    # Make decision
    print()
    print("-" * 80)
    print("CONSENSUS DECISION")
    print("-" * 80)

    decision = validator.coordinator.make_decision(test_rec.ticker, analyses)
    print(f"  Consensus Action: {decision.action.value}")
    print(f"  Internal Confidence: {decision.confidence:.0%}")
    print()

    # Show hybrid scoring
    print("-" * 80)
    print("HYBRID SCORING LOGIC")
    print("-" * 80)

    conviction_map = {
        'HIGH': 0.85,
        'MEDIUM': 0.70,
        'LOW': 0.55
    }
    external_confidence = conviction_map.get(test_rec.conviction, 0.70)
    internal_confidence = decision.confidence

    print(f"  External Confidence: {external_confidence:.2f} (from {test_rec.conviction} conviction)")
    print(f"  Internal Confidence: {internal_confidence:.2f} (from agent consensus)")
    print()

    # Calculate veto penalty
    if internal_confidence < 0.20:
        veto_penalty = 0.70
        penalty_reason = "Strong agent disagreement or missing data"
    elif internal_confidence < 0.30:
        veto_penalty = 0.80
        penalty_reason = "Weak agent consensus"
    elif internal_confidence < 0.50:
        veto_penalty = 0.90
        penalty_reason = "Moderate agent disagreement"
    else:
        veto_penalty = 1.0
        penalty_reason = "Agents agree"

    combined_confidence = external_confidence * veto_penalty

    print(f"  Veto Penalty: {veto_penalty:.2f} ({penalty_reason})")
    print(f"  Combined Confidence: {combined_confidence:.2f}")
    print()

    # Check approval
    APPROVAL_THRESHOLD = 0.55
    approved = combined_confidence >= APPROVAL_THRESHOLD

    print("-" * 80)
    print("FINAL DECISION")
    print("-" * 80)
    print(f"  Threshold: {APPROVAL_THRESHOLD:.2f}")
    print(f"  Score: {combined_confidence:.2f}")
    print(f"  Status: {'✓ APPROVED' if approved else '✗ REJECTED'}")
    print()

    # Explain why
    if approved:
        print(f"  Reason: Score {combined_confidence:.2f} >= threshold {APPROVAL_THRESHOLD:.2f}")
    else:
        gap = APPROVAL_THRESHOLD - combined_confidence
        print(f"  Reason: Score {combined_confidence:.2f} < threshold {APPROVAL_THRESHOLD:.2f}")
        print(f"  Gap: {gap:.3f} points below threshold")

    print()
    print("=" * 80)

    return approved, combined_confidence, analyses

if __name__ == "__main__":
    try:
        approved, score, analyses = test_validation()

        print("\nSUMMARY:")
        print(f"  Agents Responded: {len(analyses)}")
        print(f"  Final Score: {score:.2f}")
        print(f"  Approved: {approved}")

        if len(analyses) == 0:
            print("\n[CRITICAL] NO AGENTS RESPONDED!")
            print("This is why validation is rubber-stamping (100% approval)")
            print("Check agent initialization and coordinator setup")
        elif score > 0.70:
            print("\n[WARNING] Very high approval score")
            print("Agents may be agreeing too much or not being critical enough")

        sys.exit(0 if approved else 1)

    except Exception as e:
        print(f"\n[ERROR] Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
