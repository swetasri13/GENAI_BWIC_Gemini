"""
BWIC Win Probability Analysis Agent

A GEN AI agent that analyzes BWIC (Bond When-Issued Contract) auctions
and provides win probability estimates with detailed reasoning.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Try importing both OpenAI and Google Generative AI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from google import genai
    #import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class BWICDetails:
    """BWIC auction details"""
    bond_cusip: str
    bond_name: str
    size: float  # in millions
    deadline: str  # ISO format datetime
    seller: Optional[str] = None
    bond_type: Optional[str] = None  # e.g., "Corporate", "Treasury", "Muni"


@dataclass
class MarketContext:
    """Market context for analysis"""
    curve_data: Dict[str, float]  # e.g., {"2Y": 4.5, "5Y": 4.2, "10Y": 4.0}
    trace_data: Optional[Dict[str, Any]] = None  # TRACE transaction data
    liquidity_metrics: Optional[Dict[str, float]] = None  # bid-ask spread, volume, etc.
    comparable_trades: Optional[List[Dict[str, Any]]] = None


@dataclass
class ValuationData:
    """Fair value and historical BWIC data"""
    fair_value: float  # price or yield
    old_bwics: Optional[List[Dict[str, Any]]] = None  # historical BWIC results
    model_price: Optional[float] = None
    market_price: Optional[float] = None


@dataclass
class TraderConstraints:
    """Trader constraints and preferences"""
    risk_appetite: str  # "Low", "Medium", "High"
    inventory_level: str  # "Low", "Medium", "High", "Full"
    max_position_size: Optional[float] = None
    target_hold_period: Optional[int] = None  # days
    capital_constraints: Optional[Dict[str, Any]] = None


@dataclass
class BidScenario:
    """A bid scenario with probability and P&L"""
    bid_price: float
    win_probability_range: str  # e.g., "20-30%"
    expected_pnl: float
    expected_pnl_range: Optional[str] = None


@dataclass
class BWICAnalysis:
    """Complete BWIC analysis output"""
    summary: str
    bid_scenarios: List[BidScenario]
    commentary: str
    risks_caveats: str
    seller_intent: Optional[str] = None
    urgency_assessment: Optional[str] = None
    auction_dynamics: Optional[str] = None


class BWICAgent:
    """
    GEN AI agent for BWIC win probability analysis.
    Provides structured reasoning about auction dynamics and bid strategies.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the BWIC agent.
        
        Args:
            api_key: API key (OpenAI or Google Gemini)
            model: Model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo, or gemini models)
        """
        # Try to get API key from parameter, env var, or config
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            try:
                from config import OPENAI_API_KEY as config_key
                if config_key:
                    self.api_key = config_key
            except (ImportError, AttributeError):
                pass
        
        if not self.api_key:
            raise ValueError("API key required. Set OPENAI_API_KEY or GEMINI_API_KEY env var, config.py, or pass api_key parameter.")
        
        self.model = model
        
        # Detect which API to use based on model name or API key format
        self.use_gemini = (
            model.lower().startswith('gemini') or 
            (self.api_key and self.api_key.startswith('AIza'))
        )
        
        if self.use_gemini:
            if not GEMINI_AVAILABLE:
                raise ImportError("google-genai package required for Gemini. Install with: pip install google-genai")
            self.client = genai.Client(api_key='AIzaSyC0IuEDArH7ZioNVGufTV9x1B83A8ZNrKE')
        else:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package required. Install with: pip install openai")
            self.client = OpenAI(api_key=self.api_key)
    
    def _build_analysis_prompt(
        self,
        bwic: BWICDetails,
        market: MarketContext,
        valuation: ValuationData,
        constraints: TraderConstraints
    ) -> str:
        """Build the analysis prompt for the LLM"""
        
        prompt = f"""You are an expert fixed income trader analyzing a BWIC (Bond When-Issued Contract) auction. 
Your task is to provide a structured analysis of win probability with proper reasoning.

BWIC DETAILS:
- Bond: {bwic.bond_name} ({bwic.bond_cusip})
- Size: ${bwic.size:.2f}M
- Deadline: {bwic.deadline}
- Seller: {bwic.seller or 'Not specified'}
- Bond Type: {bwic.bond_type or 'Not specified'}

MARKET CONTEXT:
- Curve: {json.dumps(market.curve_data, indent=2)}
- TRACE Data: {json.dumps(market.trace_data, indent=2) if market.trace_data else 'Not provided'}
- Liquidity Metrics: {json.dumps(market.liquidity_metrics, indent=2) if market.liquidity_metrics else 'Not provided'}
- Comparable Trades: {len(market.comparable_trades) if market.comparable_trades else 0} trades provided

VALUATION:
- Fair Value: {valuation.fair_value}
- Model Price: {valuation.model_price or 'Not provided'}
- Market Price: {valuation.market_price or 'Not provided'}
- Historical BWICs: {len(valuation.old_bwics) if valuation.old_bwics else 0} previous auctions

TRADER CONSTRAINTS:
- Risk Appetite: {constraints.risk_appetite}
- Inventory Level: {constraints.inventory_level}
- Max Position Size: {constraints.max_position_size or 'Not specified'}
- Target Hold Period: {constraints.target_hold_period or 'Not specified'} days

YOUR ANALYSIS SHOULD:

1. INTERPRET SELLER INTENT & URGENCY:
   - Why is the seller running this BWIC?
   - What signals indicate urgency (size, timing, market conditions)?
   - What does the seller likely need to achieve?

2. REASON ABOUT AUCTION DYNAMICS:
   - Expected competition level (crowding effects)
   - Dealer behavior patterns (shading, aggressive bidding)
   - Market positioning and inventory levels
   - How will other participants bid?

3. EVALUATE BID STRATEGIES:
   - Consider 3-5 bid scenarios at different price levels
   - For each scenario, estimate:
     * Win probability range (e.g., "15-25%", not point estimates)
     * Expected P&L if won
     * Expected P&L range if applicable

4. PROVIDE STRUCTURED OUTPUT in JSON format:
{{
  "summary": "1-2 line summary of the opportunity and key recommendation",
  "seller_intent": "Analysis of seller motivation and urgency",
  "urgency_assessment": "Low/Medium/High with reasoning",
  "auction_dynamics": "Expected competition, dealer behavior, crowding analysis",
  "bid_scenarios": [
    {{
      "bid_price": 100.50,
      "win_probability_range": "20-30%",
      "expected_pnl": 0.25,
      "expected_pnl_range": "0.15-0.35"
    }}
  ],
  "commentary": "Detailed explanation of why these strategies work, market dynamics, and tactical considerations",
  "risks_caveats": "Adverse selection risks, overbidding concerns, market risks, model limitations"
}}

CONSTRAINTS:
- DO NOT recommend automation
- DO NOT claim certainty - use ranges and probabilities
- Be concise, factual, and desk-relevant
- Use trader language and terminology
- Highlight risks clearly
- Acknowledge model limitations and data gaps

Provide your analysis now:"""

        return prompt
    
    def analyze(
        self,
        bwic: BWICDetails,
        market: MarketContext,
        valuation: ValuationData,
        constraints: TraderConstraints
    ) -> BWICAnalysis:
        """
        Perform comprehensive BWIC analysis.
        
        Args:
            bwic: BWIC auction details
            market: Market context data
            valuation: Fair value and historical data
            constraints: Trader constraints
            
        Returns:
            BWICAnalysis object with structured results
        """
        prompt = self._build_analysis_prompt(bwic, market, valuation, constraints)
        
        try:
            if self.use_gemini:
                # Use Google Gemini API (new google.genai package)
                # Map common model names to correct Gemini model IDs (with models/ prefix)
                model_map = {
                    'gemini-2.5-flash-lite': 'models/gemini-2.5-flash',
                    'gemini-2.5-flash': 'models/gemini-2.5-flash',
                    'gemini-2.5-pro': 'models/gemini-2.5-pro',
                    'gemini-1.5-flash-lite': 'models/gemini-2.5-flash',
                    'gemini-1.5-flash': 'models/gemini-2.5-flash',
                    'gemini-flash': 'models/gemini-2.5-flash',
                    'gemini-pro': 'models/gemini-2.5-pro',
                }
                gemini_model = model_map.get(self.model.lower(), f'models/{self.model}')
                
                # Build the full prompt with system instruction
                full_prompt = """You are an expert fixed income trader with deep knowledge of BWIC auctions, market microstructure, and dealer behavior.

""" + prompt + """

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON object."""
                
                # Use the new google.genai API
                # Use models.generate_content with config parameter
                from google.genai import types
                response = self.client.models.generate_content(
                    model=gemini_model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
                
                result_text = response.text
                result_json = json.loads(result_text)
            else:
                # Use OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert fixed income trader with deep knowledge of BWIC auctions, market microstructure, and dealer behavior."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent, analytical output
                    response_format={"type": "json_object"}  # Ensure JSON output
                )
                
                result_text = response.choices[0].message.content
                result_json = json.loads(result_text)
            
            # Parse bid scenarios
            bid_scenarios = [
                BidScenario(
                    bid_price=scenario["bid_price"],
                    win_probability_range=scenario["win_probability_range"],
                    expected_pnl=scenario["expected_pnl"],
                    expected_pnl_range=scenario.get("expected_pnl_range")
                )
                for scenario in result_json.get("bid_scenarios", [])
            ]
            
            return BWICAnalysis(
                summary=result_json.get("summary", ""),
                bid_scenarios=bid_scenarios,
                commentary=result_json.get("commentary", ""),
                risks_caveats=result_json.get("risks_caveats", ""),
                seller_intent=result_json.get("seller_intent"),
                urgency_assessment=result_json.get("urgency_assessment"),
                auction_dynamics=result_json.get("auction_dynamics")
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                retry_delay = None
                if "retry in" in error_msg.lower():
                    import re
                    match = re.search(r'retry in ([\d.]+)s', error_msg.lower())
                    if match:
                        retry_delay = float(match.group(1))
                
                error_msg_detailed = f"API quota exceeded. Please check your API billing: {e}"
                if retry_delay:
                    error_msg_detailed += f"\nYou can retry in {retry_delay:.0f} seconds, or switch to gemini-2.5-flash model which may have higher quotas."
                else:
                    error_msg_detailed += "\nYou can run demo_mode.py to see the output format without API calls, or upgrade your API plan."
                
                raise RuntimeError(error_msg_detailed)
            if "API key" in error_msg or "API_KEY" in error_msg or "invalid" in error_msg.lower():
                raise RuntimeError(
                    f"Invalid API key. Please check your API key in config.py or environment variables.\n"
                    f"Error: {e}\n"
                    "For Gemini: Get API key from https://makersuite.google.com/app/apikey\n"
                    "For OpenAI: Get API key from https://platform.openai.com/api-keys"
                )
            raise RuntimeError(f"Error during analysis: {e}")
    
    def format_analysis(self, analysis: BWICAnalysis) -> str:
        """
        Format the analysis for display in trader-friendly format.
        
        Args:
            analysis: BWICAnalysis object
            
        Returns:
            Formatted string ready for display
        """
        output = []
        output.append("=" * 80)
        output.append("BWIC WIN PROBABILITY ANALYSIS")
        output.append("=" * 80)
        output.append("")
        
        # Summary
        output.append("SUMMARY:")
        output.append(analysis.summary)
        output.append("")
        
        # Seller Intent & Urgency
        if analysis.seller_intent:
            output.append("SELLER INTENT & URGENCY:")
            output.append(analysis.seller_intent)
            if analysis.urgency_assessment:
                output.append(f"Urgency: {analysis.urgency_assessment}")
            output.append("")
        
        # Auction Dynamics
        if analysis.auction_dynamics:
            output.append("AUCTION DYNAMICS:")
            output.append(analysis.auction_dynamics)
            output.append("")
        
        # Bid Scenarios Table
        output.append("BID SCENARIOS:")
        output.append("-" * 80)
        output.append(f"{'Bid Price':<15} {'Win Prob':<20} {'Expected P&L':<20} {'P&L Range':<20}")
        output.append("-" * 80)
        
        for scenario in analysis.bid_scenarios:
            pnl_range = scenario.expected_pnl_range or "N/A"
            output.append(
                f"{scenario.bid_price:<15.2f} "
                f"{scenario.win_probability_range:<20} "
                f"{scenario.expected_pnl:<20.2f} "
                f"{pnl_range:<20}"
            )
        
        output.append("-" * 80)
        output.append("")
        
        # Commentary
        output.append("COMMENTARY:")
        output.append(analysis.commentary)
        output.append("")
        
        # Risks & Caveats
        output.append("RISKS & CAVEATS:")
        output.append(analysis.risks_caveats)
        output.append("")
        
        output.append("=" * 80)
        
        return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    print("BWIC Agent initialized. See example_usage.py for usage examples.")

