
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

from scraping_tools import fetch_financial_page, parse_generic_financials, ScrapingError
from metrics import compute_metrics
from anomalies import detect_anomalies
from config import GOOGLE_API_KEY, LLM_MODEL

load_dotenv()

app = FastAPI(title="Agentic Financial Browser (LangChain)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    symbol: str
    market: Optional[str] = None
    url: Optional[str] = None

class AnalyzeResponse(BaseModel):
    symbol: str
    market: Optional[str]
    years: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    narrative: str

def build_financial_url(symbol: str, market: Optional[str]) -> str:
    """Build a URL for the stock symbol."""
    if market and market.upper() in ["NSE", "BSE"]:
        return f"https://www.moneycontrol.com/india/stockpricequote/{symbol}"
    return f"https://finance.yahoo.com/quote/{symbol}"

def get_langchain_narrative(symbol: str, market: Optional[str], years: List[Dict], anomalies: List[Dict]) -> str:
    """Use LangChain + Google Gemini API (FREE) for narrative analysis."""
    
    if not GOOGLE_API_KEY:
        # Fallback if no API key
        return f"""Analysis for {symbol} ({market or 'Global'}):

The company shows the following 5-year metrics:
- Years analyzed: {len(years)}
- Anomalies detected: {len(anomalies)}

Key observations:
{chr(10).join([f'• {a["condition"]}: {a["interpretation"]}' for a in anomalies[:3]])}

Note: For LLM-powered insights, configure GOOGLE_API_KEY in .env file (Google Gemini FREE API)
        """
    
    try:
        # Initialize LangChain with Google Gemini (FREE TIER AVAILABLE)
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Build financial context
        years_str = "\n".join([
            f"{y.get('label')}: Revenue={y.get('revenue')}, DSO={y.get('dso')}, Cash/Debt={y.get('cash_debt')}"
            for y in years
        ])
        
        anomalies_str = "\n".join([
            f"{a['year']}: {a['condition']} - {a['interpretation']}"
            for a in anomalies
        ]) if anomalies else "None"
        
        # Create LangChain prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a disciplined equity analyst. Analyze financial metrics and anomalies."),
            ("human", """
 Stock: {symbol} (Market: {market})

Financial metrics (5 years):
{years_str}

Detected anomalies:
{anomalies_str}

Provide a concise analyst-style interpretation (3-4 sentences) focusing on:
1. Cash flow and liquidity health
2. Collections/working capital trends
3. Overall risk assessment

Do NOT give explicit buy/sell recommendations.
            """)
        ])
        
        # Create LangChain chain
        chain = prompt_template | llm
        
        # Invoke the chain
        result = chain.invoke({
            "symbol": symbol,
            "market": market or "Unknown",
            "years_str": years_str,
            "anomalies_str": anomalies_str
        })
        
        return result.content if hasattr(result, 'content') else str(result)
    
    except Exception as e:
        return f"LangChain analysis failed: {str(e)}. Make sure GOOGLE_API_KEY is set in .env"

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Agentic analysis: fetch data → compute metrics → detect anomalies → LangChain narrative."""
    try:
        url = req.url or build_financial_url(req.symbol, req.market)
        html = fetch_financial_page(url)
        years_raw = parse_generic_financials(html)
        years_with_metrics = compute_metrics(years_raw)
        anomalies = detect_anomalies(years_with_metrics)
        
        # Use LangChain for narrative
        narrative = get_langchain_narrative(req.symbol, req.market, years_with_metrics, anomalies)
        
        return AnalyzeResponse(
            symbol=req.symbol,
            market=req.market,
            years=years_with_metrics,
            anomalies=anomalies,
            narrative=narrative,
        )
    
    except ScrapingError as e:
        narrative = f"Scraping error: {str(e)}. Could not fetch data from {req.symbol}."
        return AnalyzeResponse(
            symbol=req.symbol,
            market=req.market,
            years=[],
            anomalies=[],
            narrative=narrative,
        )
    except Exception as e:
        narrative = f"Analysis failed: {str(e)}"
        return AnalyzeResponse(
            symbol=req.symbol,
            market=req.market,
            years=[],
            anomalies=[],
            narrative=narrative,
        )

@app.get("/health")
async def health():
    return {"status": "ok", "service": "agentic-fin-browser-langchain"}

@app.get("/")
async def root():
    return {"message": "Agentic Financial Browser with LangChain", "endpoints": ["/health", "/api/analyze"]}
