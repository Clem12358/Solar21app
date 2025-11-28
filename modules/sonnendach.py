import re
import shutil
import time
import streamlit as st

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# -------------------------------
# Average electricity price by canton (CHF/kWh)
# -------------------------------
ELECTRICITY_PRICES = {
    "Nidwalden": 0.1956,
    "Zürich": 0.2239,
    "Zurich": 0.2239,  # fallback spelling
    "Geneva": 0.2422,
    "Schaffhausen": 0.2440,
    "Fribourg": 0.2535,
    "Jura": 0.2550,
    "Bern": 0.2550,
    "Aargau": 0.2587,
    "Appenzell Innerrhoden": 0.2629,
    "Appenzell Ausserrhoden": 0.2672,
    "Thurgau": 0.2752,
    "Graubünden": 0.2756,
    "Grisons": 0.2756,
    "St. Gallen": 0.2772,
    "Glarus": 0.2799,
    "Ticino": 0.2852,
    "Lucerne": 0.2885,
    "Solothurn": 0.2964,
    "Obwalden": 0.2977,
    "Valais": 0.2996,
    "Wallis": 0.2996,
    "Zug": 0.3003,
    "Uri": 0.3066,
    "Schwyz": 0.3102,
    "Basel-Landschaft": 0.3131,
    "Basel-Stadt": 0.3173,
    "Vaud": 0.3226,
    "Neuchâtel": 0.3307,
}


# -------------------------------
# Canton extraction
# -------------------------------
def extract_canton(address: str) -> str:
    """Extract canton from a Swiss address using names + abbreviations."""

    patterns = {
        "VD": "Vaud", "Vaud": "Vaud",
        "GE": "Geneva", "Geneva": "Geneva", "Genève": "Geneva",
        "ZH": "Zürich", "Zurich": "Zürich", "Zürich": "Zürich",
        "FR": "Fribourg",
        "NE": "Neuchâtel",
        "BE": "Bern", "Bern": "Bern",
        "JU": "Jura",
        "SG": "St. Gallen",
        "TI": "Ticino", "Tessin": "Ticino",
        "VS": "Valais", "Wallis": "Valais",
        "AG": "Aargau",
        "SO": "Solothurn",
        "BL": "Basel-Landschaft",
        "BS": "Basel-Stadt",
        "GR": "Graubünden", "Grisons": "Graubünden",
        "TG": "Thurgau",
        "GL": "Glarus",
        "LU": "Lucerne",
        "OW": "Obwalden",
        "NW": "Nidwalden",
        "SZ": "Schwyz",
        "ZG": "Zug",
        "UR": "Uri",
        "AI": "Appenzell Innerrhoden",
        "AR": "Appenzell Ausserrhoden",
    }

    for key, val in patterns.items():
        if re.search(rf"\b{re.escape(key)}\b", address, re.IGNORECASE):
            return val

    return None


# -------------------------------
# Helper: safe float parsing
# -------------------------------
def to_float(x):
    if not x:
        return None
    try:
        return float(x.replace("'", "").replace(",", "."))
    except Exception:
        return None


# -------------------------------
# Selenium scraping
# -------------------------------
def _build_chrome_driver():
    """Provision a Chrome driver with best-effort auto-install and clear errors."""

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    # Prefer an existing Chrome/Chromium binary if one is available
    for candidate in [
        st.secrets.get("chrome_path") if hasattr(st, "secrets") else None,
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]:
        if candidate:
            options.binary_location = candidate
            break

    try:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except WebDriverException as exc:  # pragma: no cover - depends on host binaries
        raise RuntimeError(
            "Chrome/Chromedriver could not start. "
            "If you're running locally, execute `./scripts/bootstrap_browser.sh` "
            "to install a compatible headless Chrome stack."
        ) from exc


def get_sonnendach_info(address: str) -> dict:
    """Launch Selenium, query Sonnendach, scrape PV + roof values."""

    try:
        driver = _build_chrome_driver()
    except Exception as exc:
        return {
            "address": address,
            "error": f"Unable to start browser: {exc}",
            "suitability": None,
            "pv_full_kwh": None,
            "roof_pitch_deg": None,
            "roof_heading_deg": None,
            "surface_area_m2": None,
        }

    wait = WebDriverWait(driver, 40)

    try:
        driver.get("https://www.uvek-gis.admin.ch/BFE/sonnendach/?lang=en")
        time.sleep(2)

        search = wait.until(EC.presence_of_element_located((By.ID, "searchTypeahead1")))
        search.send_keys(address)
        time.sleep(2)

        # click first suggestion
        result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".tt-suggestion")))
        result.click()
        time.sleep(3)

        # wait for roof data
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.actions.uniform.show-roof")))

        suitability = wait.until(EC.presence_of_element_located((By.ID, "eignung"))).text.strip()
        pv_full = wait.until(EC.presence_of_element_located((By.ID, "pv100"))).text.strip()
        pitch = wait.until(EC.presence_of_element_located((By.ID, "pitchOutput"))).text.strip()
        heading = wait.until(EC.presence_of_element_located((By.ID, "headingOutput"))).text.strip()
        area = wait.until(EC.presence_of_element_located((By.ID, "areaOutput"))).text.strip()

        # Always return complete structure
        return {
            "address": address,
            "suitability": suitability or None,
            "pv_full_kwh": to_float(pv_full),
            "roof_pitch_deg": to_float(pitch),
            "roof_heading_deg": to_float(heading),
            "surface_area_m2": to_float(area),
        }

    except Exception as e:
        return {
            "address": address,
            "error": f"Sonnendach scraping failed: {e}",
            "suitability": None,
            "pv_full_kwh": None,
            "roof_pitch_deg": None,
            "roof_heading_deg": None,
            "surface_area_m2": None,
        }

    finally:
        driver.quit()


# -------------------------------
# Cached wrapper
# -------------------------------
@st.cache_data(show_spinner=True, ttl=86400)
def fetch_address_data(address: str) -> dict:
    """
    Combines:
    - Sonnendach scraping
    - Canton detection
    - Electricity price lookup
    Always returns ALL keys — downstream pages never break.
    """

    base = get_sonnendach_info(address)

    canton = extract_canton(address)
    price = ELECTRICITY_PRICES.get(canton)

    base.update({
        "canton": canton,
        "avg_electricity_price_chf_kwh": price,
    })

    return base
