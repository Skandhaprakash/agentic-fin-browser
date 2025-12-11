
import os
from dotenv import load_dotenv

load_dotenv()

# LANGCHAIN + Google Gemini (FREE API)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-pro")  # or gemini-1.5-pro for better results

# Proxy/VPN settings
PROXY_URL = os.getenv("PROXY_URL", None)
USE_PROXY = PROXY_URL is not None

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# Financial data thresholds
DSO_WARNING = 120
CASH_DEBT_WARNING = 0.2
CASH_AR_WARNING = 0.5

# Anomaly severity levels
SEVERITY_CRITICAL = "red"
SEVERITY_WARNING = "orange"
SEVERITY_INFO = "yellow"
