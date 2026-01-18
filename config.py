"""
Configuration for BWIC Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = 'AIzaSyC0IuEDArH7ZioNVGufTV9x1B83A8ZNrKE'
DEFAULT_MODEL = 'gemini-2.5-flash' #os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")  # Gemini: "gemini-2.5-flash" (higher free tier quota), "gemini-2.5-pro" | OpenAI: "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"

# Analysis Parameters
DEFAULT_TEMPERATURE = 0.3  # Lower for more consistent analytical output
MAX_TOKENS = 2000  # Adjust based on model limits

# Output Formatting
TABLE_WIDTH = 80
MAX_BID_SCENARIOS = 5

