"""
Demo mode for BWIC Agent - Shows output format without API calls
Useful for testing structure and when API quota is exceeded
"""

from bwic_agent import BWICDetails, MarketContext, ValuationData, TraderConstraints, BidScenario, BWICAnalysis
from datetime import datetime, timedelta


def create_demo_analysis():
    """Create a demo analysis output to show the format"""
    
    # Create sample bid scenarios
    bid_scenarios = [
        BidScenario(
            bid_price=100.28,
            win_probability_range="20-30%",
            expected_pnl=0.25,
            expected_pnl_range="0.15-0.35"
        ),
        BidScenario(
            bid_price=100.30,
            win_probability_range="35-45%",
            expected_pnl=0.15,
            expected_pnl_range="0.10-0.20"
        ),
        BidScenario(
            bid_price=100.32,
            win_probability_range="50-60%",
            expected_pnl=0.05,
            expected_pnl_range="0.00-0.10"
        ),
        BidScenario(
            bid_price=100.35,
            win_probability_range="70-80%",
            expected_pnl=-0.10,
            expected_pnl_range="-0.15 to -0.05"
        )
    ]
    
    analysis = BWICAnalysis(
        summary="Moderate opportunity on $25M Apple bond. Fair value at 100.35 suggests competitive bidding expected. Recommend 100.30-100.32 range for balanced risk/reward.",
        bid_scenarios=bid_scenarios,
        commentary="""The $25M size and 2-hour deadline suggest moderate urgency. Seller (Large Asset Manager) likely rebalancing or taking profits. 
        
Market context shows tight bid-ask (10bps) and decent liquidity (10M daily volume). Historical BWICs show 5-8 bidders typically, with winning bids 3-7bps through fair value.

At 100.28 (7bps through fair value), win probability is low (20-30%) but offers best P&L if won. This bid targets opportunistic dealers with low inventory.

At 100.30 (5bps through), probability improves to 35-45% with still-attractive P&L. This is the sweet spot for balanced risk/reward given current market conditions.

At 100.32 (3bps through), probability jumps to 50-60% but P&L compresses. Suitable if inventory is low and need to fill position.

At 100.35 (at fair value), high win probability (70-80%) but negative expected P&L. Only bid here if desperate for inventory or have strong conviction on market direction.""",
        risks_caveats="""ADVERSE SELECTION: Seller may have negative information not reflected in market price. Large size relative to daily volume (2.5x) suggests potential information asymmetry.

OVERBIDDING RISK: Historical data shows only 2 previous BWICs. Limited sample size increases uncertainty. Recent market volatility could attract more aggressive bidders than historical patterns suggest.

LIQUIDITY RISK: Days to cover of 2.5 means position may take time to unwind if market moves against you. Consider hold period constraints.

MODEL LIMITATIONS: Fair value model may not capture all market nuances. TRACE data shows last trade at 100.25, which is 10bps below fair value - investigate this discrepancy.

TIMING RISK: 2-hour deadline is relatively short. May indicate seller urgency, but also limits time for market color gathering.""",
        seller_intent="Large Asset Manager running $25M BWIC suggests portfolio rebalancing or profit-taking. The size (moderate) and short deadline (2 hours) indicate moderate urgency - likely not distressed but wants execution certainty. Given current market levels near recent highs, profit-taking is plausible.",
        urgency_assessment="Medium - Size and deadline suggest balanced urgency. Not distressed (would be larger size or immediate deadline) but wants execution certainty.",
        auction_dynamics="Expected 6-8 bidders based on historical patterns. Competition likely moderate given size and bond quality. Dealer behavior: expect 2-3 aggressive bidders (likely those with low inventory), 3-4 at-market bidders, and 1-2 opportunistic bids. Crowding risk is low given size, but Apple bonds are popular - may attract more interest than historical comparables suggest."
    )
    
    return analysis


def main():
    """Run demo mode"""
    print("=" * 80)
    print("BWIC WIN PROBABILITY ANALYSIS - DEMO MODE")
    print("=" * 80)
    print("\nNote: This is a demo output showing the format.")
    print("For actual analysis, ensure OPENAI_API_KEY is set and has quota.\n")
    
    # Create demo analysis
    analysis = create_demo_analysis()
    
    # Use the formatter from bwic_agent
    from bwic_agent import BWICAgent
    agent = BWICAgent.__new__(BWICAgent)  # Create instance without init
    print(agent.format_analysis(analysis))
    
    print("\n" + "=" * 80)
    print("To run with actual AI analysis:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Ensure your OpenAI account has available quota")
    print("3. Run: python example_usage.py")
    print("=" * 80)


if __name__ == "__main__":
    main()

