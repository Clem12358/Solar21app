import re
import requests

# Map canton abbreviations to the names used in ELECTRICITY_PRICES
CANTON_ABBR_TO_NAME = {
    "AG": "Aargau",
    "AI": "Appenzell Innerrhoden",
    "AR": "Appenzell Ausserrhoden",
    "BE": "Bern",
    "BL": "Basel-Landschaft",
    "BS": "Basel-Stadt",
    "FR": "Fribourg",
    "GE": "Geneva",
    "GL": "Glarus",
    "GR": "Graubünden",
    "JU": "Jura",
    "LU": "Lucerne",
    "NE": "Neuchâtel",
    "NW": "Nidwalden",
    "OW": "Obwalden",
    "SG": "St. Gallen",
    "SH": "Schaffhausen",
    "SO": "Solothurn",
    "SZ": "Schwyz",
    "TG": "Thurgau",
    "TI": "Ticino",
    "UR": "Uri",
    "VD": "Vaud",
    "VS": "Valais",
    "ZG": "Zug",
    "ZH": "Zürich",
}


def detect_canton(address: str) -> str:
    """
    Best-effort canton detection from a Swiss address using GeoAdmin SearchServer.

    1. Call SearchServer with origins=address.
    2. Take the first result.
    3. Parse the canton abbreviation from the label, e.g. 'St. Gallen (SG)'.
    4. Map that abbreviation to the full canton name used in ELECTRICITY_PRICES.
       Returns "" if nothing can be detected.
    """
    base_url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

    params = {
        "searchText": address,
        "type": "locations",
        "origins": "address",  # we want address hits
        "sr": 2056,
        "limit": 1,
    }

    try:
        resp = requests.get(base_url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # Console debug – app.py will show a Streamlit warning if this returns ""
        print(f"[Geocoder] Error for '{address}': {e}")
        return ""

    results = data.get("results") or []
    if not results:
        print(f"[Geocoder] No results for '{address}'")
        return ""

    attrs = results[0].get("attrs", {}) or {}
    label = (attrs.get("label") or "").strip()
    detail = (attrs.get("detail") or "").strip()

    # Try to extract something like (SG), (VD), ...
    m = re.search(r"\(([A-Z]{2})\)", label) or re.search(r"\(([A-Z]{2})\)", detail)
    if not m:
        print(f"[Geocoder] Could not parse canton from label/detail for '{address}'. "
              f"label='{label}', detail='{detail}'")
        return ""

    abbr = m.group(1)
    canton_name = CANTON_ABBR_TO_NAME.get(abbr, "")

    if not canton_name:
        print(f"[Geocoder] Abbreviation '{abbr}' not in mapping for '{address}'")
        return ""

    return canton_name
