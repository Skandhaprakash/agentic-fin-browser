
import re
import time
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from config import PROXY_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

class ScrapingError(Exception):
    pass

def get_request_session():
    """Create a requests session with proxy if configured."""
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    session.headers.update(headers)
    
    if PROXY_URL:
        session.proxies = {
            "http": PROXY_URL,
            "https": PROXY_URL
        }
    return session

def fetch_financial_page(url: str, retry: int = 0) -> str:
    """Fetch HTML from URL with retry logic and proxy support."""
    session = get_request_session()
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        if retry < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return fetch_financial_page(url, retry + 1)
        raise ScrapingError(f"Failed to fetch {url}: {str(e)}")

def extract_numbers(text: str) -> Optional[float]:
    """Extract numeric value from text, handling formats like 12,345.67 or 1.2M"""
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Handle "M" (millions) or "B" (billions)
    multiplier = 1
    if text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]
    
    # Remove commas and other non-numeric chars except decimal point
    text = re.sub(r"[^\d\.-]", "", text)
    
    try:
        return float(text) * multiplier if text else None
    except ValueError:
        return None

def parse_bse_financials(html: str, symbol: str) -> List[Dict[str, Any]]:
    """Parse financials from BSE website."""
    soup = BeautifulSoup(html, "html.parser")
    years = []
    
    # This is a placeholder parser. You will need to adjust selectors
    # based on actual BSE website HTML structure.
    tables = soup.find_all("table")
    if not tables:
        raise ScrapingError("No tables found in BSE page")
    
    # Look for financial table
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 5:
            continue
        
        # Try to detect header row
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        if not headers:
            headers = [td.get_text(strip=True) for td in rows[0].find_all("td")]
        
        for tr in rows[1:]:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            
            row_label = tds[0].get_text(strip=True)
            values = [td.get_text(strip=True) for td in tds[1:]]
            
            # Skip non-data rows
            if "Currency" in row_label or "Note" in row_label:
                continue
            
            if "Revenue" in row_label or "Sales" in row_label:
                years.append({"label": f"FY{values[0][-2:] if values else 'XX'}", 
                             "revenue": extract_numbers(values[0]) if values else None})
    
    return years if years else [{"label": "N/A", "revenue": None}]

def parse_generic_financials(html: str) -> List[Dict[str, Any]]:
    """Generic parser for financial tables from any source."""
    soup = BeautifulSoup(html, "html.parser")
    years = []
    
    tables = soup.find_all("table", limit=3)
    if not tables:
        return [{"label": "No Data", "revenue": None, "ar": None, "cash": None}]
    
    for table in tables:
        rows = table.find_all("tr")
        for i, tr in enumerate(rows[1:5]):  # Check first 5 rows
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue
            
            year_text = tds[0].get_text(strip=True)
            year_match = re.search(r"20\d{2}", year_text)
            if not year_match:
                continue
            
            year = year_match.group()
            years.append({
                "label": f"FY{year[-2:]}",
                "year": year,
                "revenue": extract_numbers(tds[1].get_text() if len(tds) > 1 else None),
                "ar": extract_numbers(tds[2].get_text() if len(tds) > 2 else None),
                "cash": extract_numbers(tds[3].get_text() if len(tds) > 3 else None),
                "debt": extract_numbers(tds[4].get_text() if len(tds) > 4 else None),
            })
    
    return years if years else [{"label": "No Data Found"}]
