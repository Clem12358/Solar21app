# modules/geocoder.py

import requests

# Map canton abbreviations -> full names used in ELECTRICITY_PRICES
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
    Returns the Swiss canton *full name* (e.g. "Vaud", "Geneva", "St. Gallen").
    Falls back to '' if not found.

    Logic:
      1) Use GeoAdmin SearchServer to geocode the address -> LV95 coords (x,y).
      2) Use GeoAdmin identify service on canton layer
         ch.swisstopo.swissboundaries3d-kanton-flaeche.fill
         to find which canton polygon contains that point.
      3) Map canton abbreviation ("VD", "BE", ...) to full name
         via CANTON_ABBR_TO_NAME.
    """
    # 1) Geocode the address (locations search, restricted to addresses)
    search_url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

    try:
        search_params = {
            "searchText": address,
            "type": "locations",
            "origins": "address",
            "sr": 2056,   # LV95 coordinates
            "limit": 1,
        }
        r = requests.get(search_url, params=search_params, timeout=5)
        r.raise_for_status()
        payload = r.json()

        results = payload.get("results") or []
        if not results:
            return ""

        attrs = results[0].get("attrs", {})
        x = attrs.get("x")
        y = attrs.get("y")
        if x is None or y is None:
            return ""

        # 2) Identify canton polygon at that point
        identify_url = "https://api3.geo.admin.ch/rest/services/all/MapServer/identify"
        identify_params = {
            "geometry": f"{x},{y}",
            "geometryType": "esriGeometryPoint",
            "sr": 2056,
            "layers": "all:ch.swisstopo.swissboundaries3d-kanton-flaeche.fill",
            "tolerance": 0,
            # Big bounding box over CH (LV95), standard from docs/forum examples
            "mapExtent": "2180000,1047000,3140000,1333000",
            "imageDisplay": "1920,1080,96",
            "lang": "en",
            "geometryFormat": "geojson",
        }

        r2 = requests.get(identify_url, params=identify_params, timeout=5)
        r2.raise_for_status()
        data2 = r2.json()

        canton_abbr = ""

        # Depending on options, the API can return "results" or "features"
        if "results" in data2 and data2["results"]:
            attrs2 = data2["results"][0].get("attributes", {})
            canton_abbr = attrs2.get("ak", "")  # "ak" = canton code
        elif "features" in data2 and data2["features"]:
            props2 = data2["features"][0].get("properties", {})
            canton_abbr = props2.get("ak", "")

        if not canton_abbr:
            return ""

        canton_abbr = str(canton_abbr).upper()
        return CANTON_ABBR_TO_NAME.get(canton_abbr, "")

    except Exception:
        # Any network / JSON / key error → just say "not found"
        return ""
