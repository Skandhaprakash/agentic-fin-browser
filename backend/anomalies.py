
from typing import List, Dict, Any
from config import DSO_WARNING, CASH_DEBT_WARNING, CASH_AR_WARNING, SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO

def detect_anomalies(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect anomalies in financial metrics."""
    flags: List[Dict[str, Any]] = []
    
    for i, r in enumerate(rows):
        year = r.get("label") or r.get("year") or f"Year {i}"
        
        # DSO anomaly
        dso = r.get("dso")
        if dso and dso > DSO_WARNING:
            flags.append({
                "year": year,
                "color": SEVERITY_CRITICAL,
                "condition": f"DSO = {dso:.0f} days (>120)",
                "interpretation": "High receivables cycle indicates slow collections or aggressive credit policies."
            })
        
        # Cash to Debt anomaly
        cash_debt = r.get("cash_debt")
        if cash_debt and cash_debt < CASH_DEBT_WARNING:
            flags.append({
                "year": year,
                "color": SEVERITY_WARNING,
                "condition": f"Cash/Debt = {cash_debt:.2f}x (<0.2)",
                "interpretation": "Limited cash relative to debt; liquidity buffers are thin."
            })
        
        # High DSO + Low Cash/AR combination
        cash_ar = r.get("cash_ar")
        if dso and dso > 100 and cash_ar and cash_ar < CASH_AR_WARNING:
            flags.append({
                "year": year,
                "color": SEVERITY_CRITICAL,
                "condition": "High DSO + Low Cash/AR",
                "interpretation": "Receivables are slow and not backed by strong cash position. Collections risk is elevated."
            })
        
        # AR growing faster than revenue
        rev_yoy = r.get("rev_yoy")
        ar_yoy = r.get("ar_yoy")
        if rev_yoy and ar_yoy and ar_yoy > rev_yoy + 10:
            flags.append({
                "year": year,
                "color": SEVERITY_WARNING,
                "condition": f"AR growth {ar_yoy:.1f}% >> Sales growth {rev_yoy:.1f}%",
                "interpretation": "Receivables growing much faster than sales; may indicate loose credit or aggressive accounting."
            })
        
        # Negative revenue growth (decline)
        if rev_yoy and rev_yoy < -5:
            flags.append({
                "year": year,
                "color": SEVERITY_WARNING,
                "condition": f"Revenue declined {abs(rev_yoy):.1f}%",
                "interpretation": "Year-on-year revenue decline; investigate business headwinds or market conditions."
            })
    
    return flags
