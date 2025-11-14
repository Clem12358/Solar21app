import streamlit as st
import pandas as pd

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="Solar21 Pre-Check",
    page_icon="🔆",
    layout="wide"
)

# ----------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    main[data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
        padding-left: 2rem !important;
    }
    header[data-testid="stHeader"] { margin-left: 0 !important; }
    .stPageLink { display: none !important; }
    .progress-wrapper {
        width: 100%; background-color: #e0e0e0;
        height: 6px; border-radius: 4px; margin-bottom: 1.5rem;
    }
    .progress-bar {
        height: 6px; border-radius: 4px;
        background-color: #0072ff; width: 8%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# SESSION STATE DEFAULTS
# ----------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = None
if "step" not in st.session_state:
    st.session_state.step = "language"

# ----------------------------------------------------
# STEP 1: LANGUAGE SELECTION
# ----------------------------------------------------
def render_language_step():
    st.markdown(
        """
        <div class="progress-wrapper"><div class="progress-bar"></div></div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Solar21 Pre-Check")

    if st.session_state.language is None:
        st.subheader("Choose your language")
        col1, col2, col3 = st.columns(3)
        if col1.button("🇬🇧 English", use_container_width=True): st.session_state.language = "en"
        if col2.button("🇫🇷 Français", use_container_width=True): st.session_state.language = "fr"
        if col3.button("🇩🇪 Deutsch", use_container_width=True): st.session_state.language = "de"
    else:
        st.success("Language selected!")
        if st.button("➡️ Continue"): st.session_state.step = "welcome"

# ----------------------------------------------------
# STEP 2: WELCOME PAGE
# ----------------------------------------------------
def render_welcome_step():
    lang = st.session_state.get("language", "en")
    TEXT = {
        "en": {"title": "Welcome to the Solar21 Partner Pre-Check",
               "text": "Evaluate in **under two minutes** whether your client's building fits Solar21’s profile.",
               "next": "Next →", "back": "← Back"},
        "fr": {"title": "Bienvenue sur le pré-check partenaire Solar21",
               "text": "Évaluez en **moins de deux minutes** si le bâtiment correspond aux critères Solar21.",
               "next": "Suivant →", "back": "← Retour"},
        "de": {"title": "Willkommen zum Solar21 Partner Pre-Check",
               "text": "Beurteilen Sie in **unter zwei Minuten**, ob das Gebäude geeignet ist.",
               "next": "Weiter →", "back": "← Zurück"},
    }

    st.title(TEXT[lang]["title"])
    st.write(TEXT[lang]["text"])

    col_back, col_next = st.columns(2)
    if col_back.button(TEXT[lang]["back"]):
        st.session_state.language = None
        st.session_state.step = "language"
    if col_next.button(TEXT[lang]["next"], type="primary"):
        st.session_state.step = "addresses"

# ----------------------------------------------------
# STEP 3: ADDRESS INPUT  (NOW WITH SONNENDACH + GEOCODER)
# ----------------------------------------------------
def render_addresses_step():
    st.title("Client Addresses")

    if st.session_state.get("language") is None:
        st.warning("Select language first.")
        st.session_state.step = "language"
        return

    # Load modules
    try:
        from modules.sonnendach import fetch_address_data
        from modules.sonnendach import ELECTRICITY_PRICES
        from modules.geocoder import detect_canton
        modules_ok = True
    except Exception as e:
        modules_ok = False
        st.error(f"⚠️ Debug: Cannot import Sonnendach or geocoder: {e}")

    if "addresses" not in st.session_state:
        st.session_state["addresses"] = []

    current_len = max(1, len(st.session_state["addresses"]))
    num_addresses = st.number_input(
        "How many addresses do you want to enter?",
        1, 20, current_len, 1
    )

    addresses = st.session_state["addresses"]
    if len(addresses) < num_addresses:
        addresses += [""] * (num_addresses - len(addresses))
    elif len(addresses) > num_addresses:
        addresses = addresses[:num_addresses]
    st.session_state["addresses"] = addresses

    # Form
    with st.form("address_form"):
        for i in range(num_addresses):
            st.session_state["addresses"][i] = st.text_input(
                f"Address {i+1}",
                st.session_state["addresses"][i],
                key=f"addr_{i}",
                placeholder="Brunnenggstrasse 9 9000 St. Gallen"
            )
        submitted = st.form_submit_button("Save and continue →")

    if not submitted:
        return

    cleaned = [a.strip() for a in st.session_state["addresses"] if a.strip()]
    if not cleaned:
        st.error("Enter at least one valid address.")
        return

    st.session_state["addresses"] = cleaned
    st.write("Fetching data…")

    enriched = []

    for addr in cleaned:
        if modules_ok:
            data = fetch_address_data(addr)

            # Compute canton via *Swiss government API (best source)*
            canton_geo = detect_canton(addr)  # returns SG, VD, GE, etc.
            if canton_geo:
                # Map abbreviations to full names used in ELECTRICITY_PRICES
                canton_map = {
                    "VD": "Vaud", "GE": "Geneva", "ZH": "Zürich", "SG": "St. Gallen",
                    "BE": "Bern", "FR": "Fribourg", "NE": "Neuchâtel", "JU": "Jura",
                    "TI": "Ticino", "VS": "Valais", "AG": "Aargau", "SO": "Solothurn",
                    "BL": "Basel-Landschaft", "BS": "Basel-Stadt", "GR": "Graubünden",
                    "TG": "Thurgau", "GL": "Glarus", "LU": "Lucerne", "OW": "Obwalden",
                    "NW": "Nidwalden", "SZ": "Schwyz", "ZG": "Zug", "UR": "Uri",
                    "AI": "Appenzell Innerrhoden", "AR": "Appenzell Ausserrhoden"
                }
                data["canton"] = canton_map.get(canton_geo)
            else:
                st.warning(f"⚠️ Debug: Geocoder could not detect canton for: {addr}")
                data["canton"] = None

            # Normalize keys
            data["pv_full_roof_kwh"] = data.get("pv_full_kwh")
            data["avg_price_per_kwh"] = data.get("avg_electricity_price_chf_kwh")

            enriched.append(data)
        else:
            enriched.append({"address": addr})

    st.session_state["passed_addresses"] = enriched
    st.success("Addresses saved — technical data loaded.")

    st.session_state.step = "block_a"

# ----------------------------------------------------
# STEP 4: BLOCK A
# ----------------------------------------------------
def render_block_a_step():
    st.title("Block A — Owner ROI & Impact (40%)")

    passed = st.session_state.get("passed_addresses", [])
    if not passed:
        st.error("No valid data.")
        st.session_state.step = "addresses"
        return

    # A1 — Roof size
    st.subheader("A1 — Scale Economies (Roof size)")
    roof_areas = [float(p.get("surface_area_m2") or 0) for p in passed]
    avg_area = sum(roof_areas) / len(roof_areas) if roof_areas else 0

    if avg_area >= 3000: A1_score = 3
    elif avg_area >= 1000: A1_score = 2
    else: A1_score = 1

    st.info(f"Average roof area {avg_area:.1f} m² → Score {A1_score}")
    st.session_state["A1_scores"] = {p["address"]: A1_score for p in passed}

    # A2 — Owner type
    st.subheader("A2 — Owner Cost of Capital (WACC proxy)")
    A2_scores = {}
    for p in passed:
        addr = p["address"]
        choice = st.radio(f"Owner category for {addr}", [3, 2, 1], key=f"A2_{addr}")
        A2_scores[addr] = choice
    st.session_state["A2_scores"] = A2_scores

    # A3 — ESG relevance
    st.subheader("A3 — ESG Visibility")
    map_esg = {"Yes": 3, "IDK": 2, "No": 1}
    A3_scores = {}
    for p in passed:
        addr = p["address"]
        choice = st.radio(f"ESG relevance for {addr}",
                          ["Yes", "IDK", "No"], index=1, key=f"A3_{addr}")
        A3_scores[addr] = map_esg[choice]
    st.session_state["A3_scores"] = A3_scores

    if st.button("Continue to Block B →", type="primary"):
        st.session_state.step = "block_b"

# ----------------------------------------------------
# STEP 5: BLOCK B (CLEAN, RELIABLE, DEBUGGED)
# ----------------------------------------------------
def render_block_b_step():
    st.title("Block B — Consumption Profile & Financial Attractiveness")

    from modules.sonnendach import ELECTRICITY_PRICES

    passed = st.session_state.get("passed_addresses", [])
    if not passed:
        st.error("No addresses.")
        st.session_state.step = "addresses"
        return

    if "block_b_results" not in st.session_state:
        st.session_state["block_b_results"] = {}

    def midpoint(bucket):
        return {
            "< 100k": 50_000, "100–300k": 200_000,
            "300–800k": 550_000, "> 800k": 900_000
        }.get(bucket, 0)

    for i, site in enumerate(passed):
        addr = site["address"]
        canton = site.get("canton")
        pv100 = site.get("pv_full_roof_kwh")

        st.subheader(f"🏢 {addr}")

        if not canton:
            st.warning(f"⚠️ Debug: Canton missing for {addr}")

        if pv100 is None:
            st.warning(f"⚠️ Debug: pv_full_roof_kwh missing for {addr}")

        # Q1 — daytime share
        daytime = st.slider(
            f"Share of annual kWh on weekdays 08:00–18:00 at {addr}",
            0, 100, 60, 5, key=f"day_{i}"
        )
        s = daytime / 100

        # Q2 — annual spend (bucket)
        spend_choice = st.radio(
            f"Annual electricity spend at {addr}",
            ["< 100k", "100–300k", "300–800k", "> 800k"],
            index=1, key=f"spend_{i}"
        )
        annual_chf = midpoint(spend_choice)

        # Q3 — seasonality
        seasonality = st.radio(
            f"Seasonality at {addr}",
            ["All months similar (±10%) → Low",
             "Some seasonality (±10–25%) → Moderate",
             "Strong seasonality (>±25%) → High"],
            index=1, key=f"season_{i}"
        )

        # Q4 — 24/7 loads
        loads247 = st.radio(
            f"24/7 loads at {addr}?",
            ["Yes (reduces volatility)", "No"], key=f"load_{i}"
        )

        # DERIVATIONS
        price = ELECTRICITY_PRICES.get(canton)
        if price is None:
            st.warning(f"⚠️ Debug: No electricity price found for canton {canton}")

        annual_kwh = (annual_chf / price) if price else None
        sc = max(0, min(1, annual_kwh / pv100)) if (annual_kwh and pv100) else None
        import_chf = (
            s * annual_chf * (1 - sc) + (1 - s) * annual_chf
        ) if sc is not None else None

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Annual Spend (CHF)", f"{annual_chf:,.0f}")
        col2.metric("Self-consumption share", "n/a" if sc is None else f"{sc:.2f}")
        col3.metric("Estimated annual imports (CHF)",
                    "n/a" if import_chf is None else f"{import_chf:,.0f}")

        # SAVE
        st.session_state["block_b_results"][addr] = {
            "address": addr,
            "canton": canton,
            "annual_spend_chf": annual_chf,
            "seasonality": seasonality,
            "loads247": loads247,
            "daytime_frac": s,
            "avg_price_per_kwh": price,
            "annual_kwh": annual_kwh,
            "pv_full_roof_kwh": pv100,
            "self_consumption_share": sc,
            "annual_import_chf": import_chf,
        }

    if st.button("Continue to Results →", type="primary"):
        st.session_state.step = "results"

# ----------------------------------------------------
# STEP 6: RESULTS
# ----------------------------------------------------
def render_results_step():
    st.title("Final Results — Solar21 Evaluation")

    passed = st.session_state.get("passed_addresses", [])
    A1 = st.session_state.get("A1_scores", {})
    A2 = st.session_state.get("A2_scores", {})
    A3 = st.session_state.get("A3_scores", {})
    B = st.session_state.get("block_b_results", {})

    if not passed:
        st.error("No data.")
        st.session_state.step = "addresses"
        return

    st.write("### Results summary")

    for site in passed:
        addr = site["address"]
        st.subheader(addr)
        st.write(f"**A1 (Roof scale):** {A1.get(addr)}")
        st.write(f"**A2 (WACC):** {A2.get(addr)}")
        st.write(f"**A3 (ESG):** {A3.get(addr)}")
        st.write(f"**Annual imports (CHF):** {B.get(addr, {}).get('annual_import_chf')}")

# ----------------------------------------------------
# ROUTER
# ----------------------------------------------------
step = st.session_state.step

if step == "language": render_language_step()
elif step == "welcome": render_welcome_step()
elif step == "addresses": render_addresses_step()
elif step == "block_a": render_block_a_step()
elif step == "block_b": render_block_b_step()
elif step == "results": render_results_step()
else:
    st.session_state.step = "language"
    st.experimental_rerun()
