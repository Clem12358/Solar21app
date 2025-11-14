import requests

def detect_canton(address: str) -> str:
    """
    Returns the Swiss canton abbreviation (e.g. 'VD', 'GE', 'ZH').
    Falls back to '' if not found.
    """
    url = (
        "https://api3.geo.admin.ch/rest/services/api/SearchServer"
        f"?searchText={address}&type=locations&limit=1"
    )
    try:
        r = requests.get(url, timeout=5).json()
        if "results" in r and len(r["results"]) > 0:
            attrs = r["results"][0].get("attrs", {})
            return attrs.get("kanton", "")
    except:
        pass
    
    return ""
