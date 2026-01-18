"""
Example usage of the BWIC Win Probability Analysis Agent
"""

from bwic_agent import BWICAgent, BWICDetails, MarketContext, ValuationData, TraderConstraints
from datetime import datetime, timedelta


def main():
    # Initialize the agent
    # Make sure to set OPENAI_API_KEY environment variable or pass api_key parameter
    from config import DEFAULT_MODEL
    agent = BWICAgent(model=DEFAULT_MODEL)
    
    # Example 1: Corporate Bond BWIC
    print("Example 1: Corporate Bond BWIC Analysis\n")
    
    bwic = BWICDetails(
        bond_cusip="123456789",
        bond_name="Apple Inc 3.5% 2030",
        size=25.0,  # $25M
        deadline=(datetime.now() + timedelta(hours=2)).isoformat(),
        seller="Large Asset Manager",
        bond_type="Corporate"
    )
    
    market = MarketContext(
        curve_data={
            "2Y": 4.50,
            "5Y": 4.25,
            "10Y": 4.00,
            "30Y": 4.15
        },
        trace_data={
            "last_trade_price": 100.25,
            "last_trade_size": 5.0,
            "bid": 100.20,
            "ask": 100.30,
            "volume_30d": 150.0
        },
        liquidity_metrics={
            "bid_ask_spread": 0.10,
            "daily_volume": 10.0,
            "days_to_cover": 2.5
        },
        comparable_trades=[
            {"date": "2024-01-15", "size": 20.0, "price": 100.30, "type": "BWIC"},
            {"date": "2024-01-10", "size": 15.0, "price": 100.28, "type": "BWIC"}
        ]
    )
    
    valuation = ValuationData(
        fair_value=100.35,
        model_price=100.32,
        market_price=100.25,
        old_bwics=[
            {
                "date": "2024-01-15",
                "size": 20.0,
                "winning_bid": 100.28,
                "fair_value_at_time": 100.30,
                "number_of_bids": 8
            },
            {
                "date": "2024-01-10",
                "size": 15.0,
                "winning_bid": 100.25,
                "fair_value_at_time": 100.28,
                "number_of_bids": 5
            }
        ]
    )
    
    constraints = TraderConstraints(
        risk_appetite="Medium",
        inventory_level="Low",
        max_position_size=30.0,
        target_hold_period=5
    )
    
    # Perform analysis
    analysis = agent.analyze(bwic, market, valuation, constraints)
    
    # Display results
    print(agent.format_analysis(analysis))
    print("\n\n")
    
    # Example 2: Treasury BWIC (minimal data)
    print("Example 2: Treasury BWIC Analysis (Minimal Data)\n")
    
    bwic2 = BWICDetails(
        bond_cusip="912828XZ8",
        bond_name="UST 10Y 3.5% 2034",
        size=50.0,
        deadline=(datetime.now() + timedelta(hours=1)).isoformat(),
        bond_type="Treasury"
    )
    
    market2 = MarketContext(
        curve_data={
            "2Y": 4.50,
            "5Y": 4.25,
            "10Y": 4.00,
            "30Y": 4.15
        }
    )
    
    valuation2 = ValuationData(
        fair_value=99.75
    )
    
    constraints2 = TraderConstraints(
        risk_appetite="High",
        inventory_level="Medium"
    )
    
    analysis2 = agent.analyze(bwic2, market2, valuation2, constraints2)
    print(agent.format_analysis(analysis2))


if __name__ == "__main__":
    main()

