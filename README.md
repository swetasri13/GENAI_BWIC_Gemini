# BWIC Win Probability Analysis Agent

A GEN AI agent that analyzes BWIC (Bond When-Issued Contract) auctions and provides win probability estimates with detailed reasoning for fixed income traders.

## Features

- **Comprehensive Analysis**: Interprets seller intent, urgency, and auction dynamics
- **Multiple Bid Scenarios**: Evaluates 3-5 bid strategies with probability ranges
- **Risk Assessment**: Highlights adverse selection, overbidding, and market risks
- **Trader-Focused**: Uses desk-relevant language and terminology
- **Structured Output**: Provides summary, bid scenarios table, commentary, and risks

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
# Option 1: Environment variable
export OPENAI_API_KEY="your-api-key-here"

# Option 2: Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Usage

### Basic Usage

```python
from bwic_agent import BWICAgent, BWICDetails, MarketContext, ValuationData, TraderConstraints
from datetime import datetime, timedelta

# Initialize agent
agent = BWICAgent(model="gpt-4")

# Define BWIC details
bwic = BWICDetails(
    bond_cusip="123456789",
    bond_name="Apple Inc 3.5% 2030",
    size=25.0,  # $25M
    deadline=(datetime.now() + timedelta(hours=2)).isoformat(),
    seller="Large Asset Manager",
    bond_type="Corporate"
)

# Market context
market = MarketContext(
    curve_data={"2Y": 4.50, "5Y": 4.25, "10Y": 4.00, "30Y": 4.15},
    trace_data={
        "last_trade_price": 100.25,
        "bid": 100.20,
        "ask": 100.30,
        "volume_30d": 150.0
    },
    liquidity_metrics={
        "bid_ask_spread": 0.10,
        "daily_volume": 10.0
    }
)

# Valuation data
valuation = ValuationData(
    fair_value=100.35,
    model_price=100.32,
    market_price=100.25,
    old_bwics=[...]  # Historical BWIC data
)

# Trader constraints
constraints = TraderConstraints(
    risk_appetite="Medium",
    inventory_level="Low",
    max_position_size=30.0
)

# Perform analysis
analysis = agent.analyze(bwic, market, valuation, constraints)

# Display formatted results
print(agent.format_analysis(analysis))
```

### Command-Line Interface

The CLI provides multiple ways to run analysis:

```bash
# Analyze from JSON file
python cli.py --input example_input.json

# Quick analysis with inline parameters
python cli.py --bond "Apple Inc 3.5% 2030" --size 25 --deadline "+2h" --cusip "123456789"

# Interactive mode (prompts for input)
python cli.py --interactive

# Save output to file
python cli.py --input example_input.json --output results.txt

# Output as JSON
python cli.py --input example_input.json --json

# Use different model
python cli.py --input example_input.json --model gpt-4-turbo
```

### Running Examples

```bash
python example_usage.py
```

## Input Structure

### BWICDetails
- `bond_cusip`: CUSIP identifier
- `bond_name`: Bond description
- `size`: Size in millions
- `deadline`: ISO format datetime
- `seller`: (Optional) Seller identifier
- `bond_type`: (Optional) Type of bond

### MarketContext
- `curve_data`: Dictionary of yield curve points
- `trace_data`: (Optional) TRACE transaction data
- `liquidity_metrics`: (Optional) Bid-ask spread, volume, etc.
- `comparable_trades`: (Optional) List of similar trades

### ValuationData
- `fair_value`: Fair value (price or yield)
- `model_price`: (Optional) Model-derived price
- `market_price`: (Optional) Current market price
- `old_bwics`: (Optional) Historical BWIC results

### TraderConstraints
- `risk_appetite`: "Low", "Medium", or "High"
- `inventory_level`: "Low", "Medium", "High", or "Full"
- `max_position_size`: (Optional) Maximum position in millions
- `target_hold_period`: (Optional) Target holding period in days

## Output Format

The agent provides:

1. **Summary**: 1-2 line overview of opportunity and recommendation
2. **Seller Intent & Urgency**: Analysis of seller motivation
3. **Auction Dynamics**: Expected competition and dealer behavior
4. **Bid Scenarios Table**: 
   - Bid Price
   - Win Probability Range
   - Expected P&L
   - P&L Range
5. **Commentary**: Detailed reasoning for strategies
6. **Risks & Caveats**: Adverse selection, overbidding, market risks

## Model Options

- `gpt-4`: Best quality, slower, more expensive
- `gpt-4-turbo`: Good balance of quality and speed
- `gpt-3.5-turbo`: Faster, cheaper, lower quality

## Constraints & Design Principles

- **No Automation Recommendations**: Agent provides analysis, not automation suggestions
- **No Certainty Claims**: Uses probability ranges, not point estimates
- **Desk-Relevant**: Concise, factual, trader-focused language
- **Risk-Aware**: Explicitly highlights risks and model limitations

## License

MIT License

