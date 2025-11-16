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

    header[data-testid="stHeader"] {
        margin-left: 0 !important;
    }

    .stPageLink { display: none !important; }

    .progress-wrapper {
        width: 100%;
        background-color: #e0e0e0;
        height: 6px;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .progress-bar {
        height: 6px;
        border-radius: 4px;
        background-color: #0072ff;
        width: 8%;
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
# STEP 1: LANGUAGE SELECTION (instant jump to welcome)
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

        if col1.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = "en"
            st.session_state.step = "welcome"
            st.rerun()

        if col2.button("🇫🇷 Français", use_container_width=True):
            st.session_state.language = "fr"
            st.session_state.step = "welcome"
            st.rerun()

        if col3.button("🇩🇪 Deutsch", use_container_width=True):
            st.session_state.language = "de"
            st.session_state.step = "welcome"
            st.rerun()
    else:
        # If language is already set, skip this screen entirely.
        st.session_state.step = "welcome"
        st.rerun()


# ----------------------------------------------------
# STEP 2: WELCOME PAGE
# ----------------------------------------------------
def render_welcome_step():
    lang = st.session_state.get("language", "en")

    TEXT = {
        "en": {
            "title": "Welcome to the Solar21 Partner Pre-Check",
            "text": "Evaluate in **under two minutes** whether your client's building fits Solar21’s profile.",
            "next": "Next →",
            "back": "← Back",
        },
        "fr": {
            "title": "Bienvenue sur le pré-check partenaire Solar21",
            "text": "Évaluez en **moins de deux minutes** si le bâtiment du client correspond aux critères Solar21.",
            "next": "Suivant →",
            "back": "← Retour",
        },
        "de": {
            "title": "Willkommen zum Solar21 Partner Pre-Check",
            "text": "Beurteilen Sie in **unter zwei Minuten**, ob das Gebäude Ihres Kunden geeignet ist.",
            "next": "Weiter →",
            "back": "← Zurück",
        },
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
# STEP 3: ADDRESS INPUT (manual canton selection)
# ----------------------------------------------------
def render_addresses_step():
    st.title("Client Addresses")

    if st.session_state.get("language") is None:
        st.warning("Select language first.")
        st.session_state.step = "language"
        return

    # Import Sonnendach fetcher + price list
    try:
        from modules.sonnendach import fetch_address_data, ELECTRICITY_PRICES
        sonnendach_ok = True
    except Exception as e:
        sonnendach_ok = False
        ELECTRICITY_PRICES = {}
        st.error(f"⚠️ Debug: Cannot import sonnendach modules: {e}")

    if "addresses" not in st.session_state:
        st.session_state["addresses"] = []
    if "cantons" not in st.session_state:
        st.session_state["cantons"] = []

    addresses = st.session_state["addresses"]
    cantons = st.session_state["cantons"]

    current_len = max(1, len(addresses))
    num_addresses = st.number_input(
        "How many addresses do you want to enter?",
        min_value=1,
        max_value=20,
        value=current_len,
        step=1,
    )

    # Resize lists to match requested number of addresses
    if len(addresses) < num_addresses:
        addresses += [""] * (num_addresses - len(addresses))
        cantons += [""] * (num_addresses - len(cantons))
    elif len(addresses) > num_addresses:
        addresses = addresses[:num_addresses]
        cantons = cantons[:num_addresses]

    st.session_state["addresses"] = addresses
    st.session_state["cantons"] = cantons

    # Canton options (from Sonnendach price list if available)
    if ELECTRICITY_PRICES:
        canton_options = sorted(set(ELECTRICITY_PRICES.keys()))
    else:
        # Fallback list – should rarely be used
        canton_options = sorted([
            "Aargau", "Appenzell Innerrhoden", "Appenzell Ausserrhoden",
            "Basel-Landschaft", "Basel-Stadt", "Bern", "Fribourg", "Geneva",
            "Glarus", "Graubünden", "Jura", "Lucerne", "Nidwalden", "Obwalden",
            "Neuchâtel", "Schaffhausen", "Schwyz", "Solothurn", "St. Gallen",
            "Thurgau", "Ticino", "Uri", "Vaud", "Valais", "Zug", "Zürich",
        ])

    placeholder = "(select canton)"

    # Address + canton form
    with st.form("address_form"):
        for i in range(num_addresses):
            col_addr, col_canton = st.columns([3, 1])

            with col_addr:
                st.session_state["addresses"][i] = st.text_input(
                    f"Address {i+1}",
                    st.session_state["addresses"][i],
                    key=f"addr_{i}",
                    placeholder="Brunnenggstrasse 9 9000 St. Gallen",
                )

            with col_canton:
                current_canton = st.session_state["cantons"][i]
                options = [placeholder] + canton_options
                if current_canton in canton_options:
                    default_index = options.index(current_canton)
                else:
                    default_index = 0

                selected = st.selectbox(
                    "Canton",
                    options=options,
                    index=default_index,
                    key=f"canton_{i}",
                )
                st.session_state["cantons"][i] = "" if selected == placeholder else selected

        submitted = st.form_submit_button("Save and continue →")

    if not submitted:
        return

    # Clean up: keep only non-empty addresses + their cantons
    raw_addresses = st.session_state["addresses"]
    raw_cantons = st.session_state["cantons"]

    pairs = []
    for addr, canton in zip(raw_addresses, raw_cantons):
        addr_clean = addr.strip()
        if addr_clean:
            pairs.append((addr_clean, canton))

    if not pairs:
        st.error("Enter at least one valid address.")
        return

    # Ensure canton chosen for each entered address
    if any(not c for _, c in pairs):
        st.error("Please select the canton for each address.")
        return

    # Persist cleaned lists
    st.session_state["addresses"] = [a for a, _ in pairs]
    st.session_state["cantons"] = [c for _, c in pairs]

    st.write("Fetching data…")

    enriched = []
    for addr, canton in pairs:
        if sonnendach_ok:
            data = fetch_address_data(addr)  # Sonnendach scraper
            # Normalize keys
            data["pv_full_roof_kwh"] = data.get("pv_full_kwh")
            price = data.get("avg_electricity_price_chf_kwh")

            # If Sonnendach didn't carry a price, fall back to our canton list
            if (price is None or price == 0) and canton in ELECTRICITY_PRICES:
                price = ELECTRICITY_PRICES[canton]

            data["avg_price_per_kwh"] = price
            data["canton"] = canton
            enriched.append(data)
        else:
            enriched.append({"address": addr, "canton": canton})

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
        st.error("No valid address data.")
        st.session_state.step = "addresses"
        return

    # A1 — Roof Segments
    st.subheader("A1 — Scale Economies (Roof size)")

    roof_areas = [float(p.get("surface_area_m2") or 0) for p in passed]
    avg_area = sum(roof_areas) / len(roof_areas) if roof_areas else 0

    if avg_area >= 3000:
        A1_score = 3
    elif avg_area >= 1000:
        A1_score = 2
    else:
        A1_score = 1

    st.info(f"Average roof area {avg_area:.1f} m² → Score {A1_score}")
    st.session_state["A1_scores"] = {p["address"]: A1_score for p in passed}

    # A2 — Owner type
    st.subheader("A2 — Owner Cost of Capital (WACC proxy)")
    A2_scores = {}
    for p in passed:
        addr = p["address"]
        choice = st.radio(
            f"Owner category for {addr}",
            [3, 2, 1],
            key=f"A2_{addr}",
        )
        A2_scores[addr] = choice
    st.session_state["A2_scores"] = A2_scores

    # A3 — ESG
    st.subheader("A3 — ESG Visibility")
    A3_scores = {}
    map_esg = {"Yes": 3, "IDK": 2, "No": 1}
    for p in passed:
        addr = p["address"]
        choice = st.radio(
            f"ESG relevance for {addr}",
            ["Yes", "IDK", "No"],
            index=1,
            key=f"A3_{addr}",
        )
        A3_scores[addr] = map_esg[choice]
    st.session_state["A3_scores"] = A3_scores

    if st.button("Continue to Block B →", type="primary"):
        st.session_state.step = "block_b"


# ----------------------------------------------------
# STEP 5: BLOCK B — CONSUMPTION & FINANCIAL ATTRACTIVENESS
# ----------------------------------------------------
def render_block_b_step():
    st.title("Block B — Consumption Profile & Financial Attractiveness")

    try:
        from modules.sonnendach import ELECTRICITY_PRICES
    except Exception as e:
        st.error(f"⚠️ Debug: Failed to import electricity prices: {e}")
        ELECTRICITY_PRICES = {}

    passed = st.session_state.get("passed_addresses", [])
    if not passed:
        st.error("⚠️ Debug: No addresses available.")
        st.session_state.step = "addresses"
        return

    if "block_b_results" not in st.session_state:
        st.session_state["block_b_results"] = {}

    def midpoint(bucket):
        return {
            "< 100k": 50_000,
            "100–300k": 200_000,
            "300–800k": 550_000,
            "> 800k": 900_000,
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

        # Q1: Share daytime consumption
        daytime = st.slider(
            f"Share of annual kWh on weekdays 08:00–18:00 at {addr}",
            0, 100, 60, 5,
            key=f"daytime_{i}"
        )
        s = daytime / 100

        # Q2: Annual spend
        spend_choice = st.radio(
            f"Annual electricity spend at {addr}",
            ["< 100k", "100–300k", "300–800k", "> 800k"],
            index=1,
            key=f"spend_{i}"
        )
        annual_chf = midpoint(spend_choice)

        # Q3 — seasonality
        seasonality = st.radio(
            f"Seasonality of consumption at {addr}",
            [
                "All months similar (±10%) → Low",
                "Some seasonality (±10–25%) → Moderate",
                "Strong seasonality (>±25%) → High",
            ],
            index=1,
            key=f"season_{i}"
        )

        # Q4 — 24/7 loads
        loads247 = st.radio(
            f"Do you run any 24/7 loads at {addr}?",
            ["Yes (reduces volatility)", "No"],
            key=f"load247_{i}"
        )

        # DERIVATIONS
        price = ELECTRICITY_PRICES.get(canton)
        if price is None:
            st.warning(f"⚠️ Debug: No electricity price for canton '{canton}'")

        annual_kwh = annual_chf / price if price else None

        if annual_kwh is not None and pv100:
            sc = max(0, min(1, annual_kwh / pv100))
        else:
            sc = None

        if sc is not None:
            import_chf = s * annual_chf * (1 - sc) + (1 - s) * annual_chf
        else:
            import_chf = None

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Annual Spend (CHF)", f"{annual_chf:,.0f}")
        col2.metric("Self-consumption share", "n/a" if sc is None else f"{sc:.2f}")

