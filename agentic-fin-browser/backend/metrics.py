
from typing import List, Dict, Any, Optional

def compute_metrics(years: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute working capital and solvency metrics."""
    out = []
    for i, row in enumerate(years):
        prev = years[i - 1] if i > 0 else None
        
        rev = row.get("revenue")
        ar = row.get("ar")
        cash = row.get("cash")
        debt = row.get("debt")
        equity = row.get("equity")
        
        # Days Sales Outstanding (DSO)
        dso = (ar / rev * 365) if rev and ar else None
        
        # Cash to AR ratio
        cash_ar = (cash / ar) if cash and ar else None
        
        # Cash to Debt ratio
        cash_debt = (cash / debt) if cash and debt else None
        
        # Revenue YoY growth
        rev_yoy = ((rev - prev["revenue"]) / prev["revenue"] * 100) if prev and prev.get("revenue") else None
        
        # AR growth
        ar_yoy = ((ar - prev.get("ar", ar)) / prev.get("ar", ar) * 100) if prev and ar and prev.get("ar") else None
        
        out.append({
            **row,
            "dso": round(dso, 2) if dso else None,
            "cash_ar": round(cash_ar, 2) if cash_ar else None,
            "cash_debt": round(cash_debt, 2) if cash_debt else None,
            "rev_yoy": round(rev_yoy, 2) if rev_yoy else None,
            "ar_yoy": round(ar_yoy, 2) if ar_yoy else None,
        })
    return out
