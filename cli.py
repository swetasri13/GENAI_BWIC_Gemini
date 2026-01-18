"""
Command-line interface for BWIC Win Probability Analysis Agent
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from bwic_agent import (
    BWICAgent,
    BWICDetails,
    MarketContext,
    ValuationData,
    TraderConstraints
)


def load_json_file(filepath: str) -> dict:
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="BWIC Win Probability Analysis Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze from JSON file
  python cli.py --input bwic_data.json

  # Analyze with inline data
  python cli.py --bond "Apple Inc 3.5% 2030" --size 25 --deadline "+2h"

  # Save output to file
  python cli.py --input bwic_data.json --output results.txt
        """
    )
    
    # Input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i',
        type=str,
        help='Path to JSON file with BWIC data'
    )
    input_group.add_argument(
        '--interactive', '-I',
        action='store_true',
        help='Interactive mode (prompts for input)'
    )
    
    # Quick input options
    parser.add_argument('--bond', type=str, help='Bond name')
    parser.add_argument('--cusip', type=str, help='Bond CUSIP')
    parser.add_argument('--size', type=float, help='Size in millions')
    parser.add_argument('--deadline', type=str, help='Deadline (ISO format or +Nh for N hours)')
    
    # Output options
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Model options
    parser.add_argument('--model', type=str, default='gpt-4o-mini', 
                       choices=['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                       help='OpenAI model to use')
    
    return parser.parse_args()


def parse_deadline(deadline_str: str) -> str:
    """Parse deadline string (ISO format or +Nh for N hours)"""
    if deadline_str.startswith('+'):
        # Relative time (e.g., +2h for 2 hours from now)
        hours = int(deadline_str[1:-1])
        return (datetime.now() + timedelta(hours=hours)).isoformat()
    else:
        # Assume ISO format
        return deadline_str


def create_bwic_from_args(args) -> BWICDetails:
    """Create BWICDetails from command line arguments"""
    if not all([args.bond, args.size, args.deadline]):
        raise ValueError("--bond, --size, and --deadline required for quick input")
    
    return BWICDetails(
        bond_cusip=args.cusip or "UNKNOWN",
        bond_name=args.bond,
        size=args.size,
        deadline=parse_deadline(args.deadline),
        bond_type=None
    )


def create_from_json(data: dict) -> tuple:
    """Create all data structures from JSON"""
    bwic = BWICDetails(**data.get('bwic', {}))
    
    market = MarketContext(**data.get('market', {}))
    
    valuation = ValuationData(**data.get('valuation', {}))
    
    constraints = TraderConstraints(**data.get('constraints', {}))
    
    return bwic, market, valuation, constraints


def interactive_input():
    """Interactive input mode"""
    print("BWIC Win Probability Analysis - Interactive Mode")
    print("=" * 60)
    
    # BWIC Details
    print("\nBWIC Details:")
    bond_name = input("Bond Name: ")
    cusip = input("CUSIP (optional): ") or "UNKNOWN"
    size = float(input("Size (millions): "))
    deadline_input = input("Deadline (ISO format or +Nh, e.g., +2h): ")
    deadline = parse_deadline(deadline_input)
    seller = input("Seller (optional): ") or None
    bond_type = input("Bond Type (optional): ") or None
    
    bwic = BWICDetails(
        bond_cusip=cusip,
        bond_name=bond_name,
        size=size,
        deadline=deadline,
        seller=seller,
        bond_type=bond_type
    )
    
    # Market Context
    print("\nMarket Context:")
    print("Enter yield curve data (format: 2Y:4.5,5Y:4.2,10Y:4.0):")
    curve_input = input("Curve: ")
    curve_data = {}
    if curve_input:
        for pair in curve_input.split(','):
            key, value = pair.split(':')
            curve_data[key.strip()] = float(value.strip())
    
    market = MarketContext(curve_data=curve_data)
    
    # Valuation
    print("\nValuation:")
    fair_value = float(input("Fair Value: "))
    valuation = ValuationData(fair_value=fair_value)
    
    # Constraints
    print("\nTrader Constraints:")
    risk_appetite = input("Risk Appetite (Low/Medium/High) [Medium]: ") or "Medium"
    inventory = input("Inventory Level (Low/Medium/High/Full) [Medium]: ") or "Medium"
    
    constraints = TraderConstraints(
        risk_appetite=risk_appetite,
        inventory_level=inventory
    )
    
    return bwic, market, valuation, constraints


def main():
    """Main CLI entry point"""
    args = parse_args()
    
    try:
        # Initialize agent
        agent = BWICAgent(model=args.model)
        
        # Get input data
        if args.input:
            # Load from JSON file
            data = load_json_file(args.input)
            bwic, market, valuation, constraints = create_from_json(data)
        elif args.interactive:
            # Interactive mode
            bwic, market, valuation, constraints = interactive_input()
        else:
            # Quick input from command line
            bwic = create_bwic_from_args(args)
            # Use minimal defaults for other inputs
            market = MarketContext(curve_data={})
            valuation = ValuationData(fair_value=100.0)
            constraints = TraderConstraints(
                risk_appetite="Medium",
                inventory_level="Medium"
            )
        
        # Perform analysis
        print("Analyzing BWIC...", file=sys.stderr)
        analysis = agent.analyze(bwic, market, valuation, constraints)
        
        # Output results
        if args.json:
            # JSON output
            output = {
                "summary": analysis.summary,
                "seller_intent": analysis.seller_intent,
                "urgency_assessment": analysis.urgency_assessment,
                "auction_dynamics": analysis.auction_dynamics,
                "bid_scenarios": [
                    {
                        "bid_price": s.bid_price,
                        "win_probability_range": s.win_probability_range,
                        "expected_pnl": s.expected_pnl,
                        "expected_pnl_range": s.expected_pnl_range
                    }
                    for s in analysis.bid_scenarios
                ],
                "commentary": analysis.commentary,
                "risks_caveats": analysis.risks_caveats
            }
            result = json.dumps(output, indent=2)
        else:
            # Formatted text output
            result = agent.format_analysis(analysis)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

