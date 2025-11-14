import streamlit as st
import pandas as pd

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="Solar21 Pre-Check", page_icon="🔆", layout="wide")

# ----------------------------------------------------
# GLOBAL STYLE — hide sidebar, expand content, helpers
# ----------------------------------------------------
st.markdown(
    """
    <style>
    /* Hide the sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Hide the burger menu */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Expand main container */
    main[data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
        padding-left: 2rem !important;
    }

    /* Expand header area */
    header[data-testid="stHeader"] {
        margin-left: 0 !important;
    }

    /* Hide old multipage page links if they exist */
    .stPageLink {
        display: none !important;
    }

    /* --- Progress bar (used on language step) --- */
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
        width: 8%;  /* "page 1" = 8% */
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
    # Start at language selection ("Gates")
    st.session_state.step = "language"


# ----------------------------------------------------
# STEP RENDERERS
# ----------------------------------------------------
def render_language_step():
    """
    Combined from Gates.py
    Initial "Pre-Check" page with language selection.
    """
    # Progress bar
    st.markdown(
        """
        <div class="progress-wrapper">
            <div class="progress-bar"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title("Solar21 Pre-Check")

    if st.session_state.language is None:
        st.subheader("Choose your language")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🇬🇧 English", use_container_width=True):
                st.session_state.language = "en"

        with col2:
            if st.button("🇫🇷 Français", use_container_width=True):
                st.session_state.language = "fr"

        with col3:
            if st.button("🇩🇪 Deutsch", use_container_width=True):
                st.session_state.language = "de"

    else:
        st.success("Language selected!")

        if st.button("➡️ Continue"):
            st.session_state.step = "welcome"


def render_welcome_step():
    """
    Combined from Welcome.py
    """
    lang = st.session_state.get("language", "en")

    TEXT = {
        "en": {
            "title": "Welcome to the Solar21 Partner Pre-Check",
            "text": (
                "This tool helps you evaluate in **under two minutes** "
                "if your client's property is a strong fit for Solar21’s business model."
                "\n\nClick *Next* to continue."
            ),
            "next": "Next →",
            "back": "← Back",
        },
        "fr": {
            "title": "Bienvenue sur le pré-check partenaire Solar21",
            "text": (
                "Cet outil vous aide à évaluer en **moins de deux minutes** "
                "si le bâtiment de votre client est un bon candidat pour Solar21."
                "\n\nCliquez sur *Suivant* pour continuer."
            ),
            "next": "Suivant →",
            "back": "← Retour",
        },
        "de": {
            "title": "Willkommen zum Solar21 Partner Pre-Check",
            "text": (
                "Dieses Tool zeigt Ihnen in **unter zwei Minuten**, "
                "ob das Gebäude Ihres Kunden gut zu Solar21 passt."
                "\n\nKlicken Sie auf *Weiter*, um fortzufahren."
            ),
            "next": "Weiter →",
            "back": "← Zurück",
        },
    }

    st.title(TEXT[lang]["title"])
    st.write(TEXT[lang]["text"])

    col_back, col_next = st.columns(2)

    with col_back:
        if st.button(TEXT[lang]["back"]):
            # Reset language and go back to language selection step
            st.session_state.language = None
            st.session_state.step = "language"

    with col_next:
        if st.button(TEXT[lang]["next"], type="primary"):
            st.session_state.step = "addresses"


def render_addresses_step():
    """
    Combined from Addresses.py
    (without NEXT_PAGE; navigation handled by `step`.)
    """
    st.title("Client Addresses")

    # Protect against direct navigation
    lang = st.session_state.get("language")
    if lang is None:
        st.warning("Please select your language first.")
        st.session_state.step = "language"
        return

    # Init state
    if "addresses" not in st.session_state:
        st.session_state["addresses"] = []

    # How many addresses?
    current_len = max(1, len(st.session_state["addresses"]))
    num_addresses = st.number_input(
        "How many addresses do you want to enter?",
        min_value=1,
        max_value=20,
        step=1,
        value=current_len,
    )

    # Resize internal list
    addresses = st.session_state["addresses"]
    if len(addresses) < num_addresses:
        addresses += [""] * (num_addresses - len(addresses))
    elif len(addresses) > num_addresses:
        addresses = addresses[:num_addresses]
    st.session_state["addresses"] = addresses

    # Address input form
    with st.form("address_form"):
        for i in range(num_addresses):
            st.session_state["addresses"][i] = st.text_input(
                f"Address {i+1}",
                st.session_state["addresses"][i],
                key=f"address_{i}",
                placeholder="Brunnenggstrasse 9 9000 St. Gallen",
            )

        submitted = st.form_submit_button("Save and continue →")

    if submitted:
        cleaned = [a.strip() for a in st.session_state["addresses"] if a.strip()]

        if not cleaned:
            st.error("Please enter at least one valid address.")
        else:
            st.session_state["addresses"] = cleaned

            # For now, treat all cleaned addresses as "passed" properties.
            # (If you have a Sonnendach/technical filter, you can replace this
            # with your real logic that populates passed_addresses.)
            st.session_state["passed_addresses"] = [
                {"address": addr} for addr in cleaned
            ]

            st.session_state.step = "block_a"


def render_block_a_step():
    """
    Combined from BlockA.py
    """
    st.title("Block A — Owner ROI & Impact (40%)")

    # Protect against direct navigation
    passed_addresses = st.session_state.get("passed_addresses")
    if not passed_addresses:
        st.error("No valid properties found. Please restart from the beginning.")
        st.session_state.step = "addresses"
        return

    st.write(
        "We now evaluate the financial attractiveness and ESG potential of the remaining properties."
    )

    # =====================================================
    # A1 — Scale Economies (Roof Size) — SEGMENT LEVEL
    # =====================================================
    st.subheader("A1. Scale Economies (Roof Size Category) — 33%")

    st.write(
        """
This score is based on the **average roof size** across all properties 
that passed the previous screening — not per-address.

Average roof size categories:
- **Large segment**: ≥ 3000 m² → Score **3**
- **Medium segment**: 1000–2999 m² → Score **2**
- **Small segment**: < 1000 m² → Score **1**
"""
    )

    # Calculate average roof area from passed addresses
    roof_areas = [float(item.get("surface_area_m2") or 0) for item in passed_addresses]
    avg_roof_area = sum(roof_areas) / len(roof_areas) if roof_areas else 0

    if avg_roof_area >= 3000:
        A1_score = 3
        segment_label = "Large"
    elif avg_roof_area >= 1000:
        A1_score = 2
        segment_label = "Medium"
    else:
        A1_score = 1
        segment_label = "Small"

    st.info(
        f"Average roof size across passed properties: **{round(avg_roof_area,1)} m²** → "
        f"**{segment_label} segment** → Score **{A1_score}**"
    )

    # Save as a single scalar
    st.session_state["A1_score_segment"] = A1_score

    # Also create per-address A1_scores so the result step can use them.
    A1_scores = {item["address"]: A1_score for item in passed_addresses}
    st.session_state["A1_scores"] = A1_scores

    # ===============================
    # A2 — Owner Cost of Capital
    # ===============================
    st.subheader("A2. Owner Cost of Capital (WACC proxy) — 33%")

    st.write(
        """
Choose the type of owner per address:
- **3 = Low-WACC** (municipalities, hospitals, co-ops, listed funds)
- **2 = Medium-WACC** (institutional private owners)
- **1 = High-WACC** (SMEs or private individuals)
"""
    )

    A2_scores = {}
    for item in passed_addresses:
        addr = item["address"]

        value = st.radio(
            f"Owner category for **{addr}**",
            [3, 2, 1],
            index=0,
            key=f"A2_{addr}",
        )
        A2_scores[addr] = int(value)

    # ===============================
    # A3 — ESG relevance
    # ===============================
    st.subheader("A3. ESG / Public Visibility — 33%")

    st.write(
        """
Score mapping:
- **Yes → 3**
- **IDK → 2**
- **No → 1**
"""
    )

    A3_scores = {}
    score_map = {"Yes": 3, "IDK": 2, "No": 1}

    for item in passed_addresses:
        addr = item["address"]

        choice = st.radio(
            f"ESG relevance for **{addr}**",
            ["Yes", "IDK", "No"],
            index=1,
            key=f"A3_{addr}",
        )

        A3_scores[addr] = int(score_map[choice])

    # ----------------------------
    # Save results
    # ----------------------------
    st.session_state["A2_scores"] = A2_scores
    st.session_state["A3_scores"] = A3_scores

    st.success("Block A scores saved.")

    if st.button("Continue to Block B →", type="primary"):
        st.session_state.step = "block_b"


def render_block_b_step():
    """
    Combined from BlockB.py
    """
    st.title("Block B — Strategic & Financial Attractiveness")

    # Protect against direct navigation
    passed_addresses = st.session_state.get("passed_addresses")
    if not passed_addresses:
        st.error("No properties available. Please complete previous steps.")
        st.session_state.step = "addresses"
        return

    st.write("We now evaluate the strategic attractiveness of your portfolio.")
    st.write("This block takes only 1–2 minutes.")

    blockB_scores = {}

    for item in passed_addresses:
        addr = item["address"]
        canton_price = item.get("avg_electricity_price_chf_kwh")  # From Sonnendach
        st.subheader(f"🏢 {addr}")

        # ---------------------------------
        # 1) Electricity Price
        # ---------------------------------
        initial_price = 28
        if canton_price:
            st.caption(
                f"Average electricity price for {item.get('canton')}: {canton_price} CHF/kWh"
            )

        price = st.slider(
            f"Electricity price at {addr} (Rp. per kWh)",
            min_value=10,
            max_value=60,
            value=initial_price,
            help="Higher local prices → faster solar ROI",
            key=f"price_{addr}",
        )

        if price >= 40:
            price_score = 3
        elif price >= 25:
            price_score = 2
        else:
            price_score = 1

        # ---------------------------------
        # 2) Stability of Client
        # ---------------------------------
        stability = st.selectbox(
            f"How stable is the tenant/ownership structure at {addr}?",
            ["Low stability", "Medium stability", "High stability"],
            index=1,
            key=f"stability_{addr}",
        )
        stability_score = {"Low stability": 1, "Medium stability": 2, "High stability": 3}[
            stability
        ]

        # ---------------------------------
        # 3) ESG Ambition
        # ---------------------------------
        esg = st.selectbox(
            f"What is the client's ESG ambition level at {addr}?",
            ["Minimal", "Moderate", "Strong"],
            index=1,
            key=f"esg_{addr}",
        )
        esg_score = {"Minimal": 1, "Moderate": 2, "Strong": 3}[esg]

        # ---------------------------------
        # 4) Replication Potential
        # ---------------------------------
        replication = st.number_input(
            f"How many additional similar buildings could follow?",
            min_value=0,
            max_value=50,
            value=0,
            key=f"replication_{addr}",
        )

        if replication >= 10:
            replication_score = 3
        elif replication >= 3:
            replication_score = 2
        else:
            replication_score = 1

        # ---------------------------------
        # Pack final numeric results
        # ---------------------------------
        blockB_scores[addr] = {
            "price_score": int(price_score),
            "stability_score": int(stability_score),
            "esg_score": int(esg_score),
            "replication_score": int(replication_score),
        }

    # Save scores
    st.session_state["blockB_scores"] = blockB_scores

    st.write("---")

    if st.button("Continue to Final Result →", type="primary"):
        st.session_state.step = "results"


def render_results_step():
    """
    Combined from results.py
    """
    st.title("Final Results – Solar21 Property Evaluation")

    # Retrieve all stored data
    passed_addresses = st.session_state.get("passed_addresses", [])
    A1 = st.session_state.get("A1_scores", {})
    A2 = st.session_state.get("A2_scores", {})
    A3 = st.session_state.get("A3_scores", {})
    B = st.session_state.get("blockB_scores", {})

    if not passed_addresses:
        st.error("No passed addresses found. Please start again.")
        st.session_state.step = "addresses"
        return

    # Weighting model
    WEIGHT_A = 0.40  # Block A (A1,A2,A3)
    WEIGHT_B = 0.40  # Block B (price, stability, esg, replication)

    W_A = WEIGHT_A / 3  # each A-subscore
    W_B = WEIGHT_B / 4  # four B-sub-scores

    rows = []
    for item in passed_addresses:
        address = item["address"]

        # Block A
        score_A1 = A1.get(address, 0)
        score_A2 = A2.get(address, 0)
        score_A3 = A3.get(address, 0)

        score_A_total = (
            score_A1 * W_A +
            score_A2 * W_A +
            score_A3 * W_A
        )

        # ===================== BLOCK B – LOAD PROFILE & SPEND =====================

import streamlit as st
from sonnendach import CANTON_KWH_PRICES  # adapt if different name

def get_midpoint_spend(choice: str) -> float:
    """
    Map the user bucket to a ballpark annual spend (CHF).
    Adjust these midpoints if you prefer other estimates.
    """
    mapping = {
        "< 100k": 50_000,
        "100–300k": 200_000,
        "300–800k": 550_000,
        "> 800k": 900_000,  # or 1_000_000 if you prefer
    }
    return mapping[choice]

def render_block_b():
    st.header("B. Consumption profile & spend")

    if "sites" not in st.session_state or not st.session_state["sites"]:
        st.info("No addresses found from Block A. Please complete Block A first.")
        return

    # Where we store all answers / derived metrics
    if "block_b_results" not in st.session_state:
        st.session_state["block_b_results"] = {}

    for idx, site in enumerate(st.session_state["sites"]):
        address = site.get("address", f"Site {idx+1}")
        canton = site.get("canton")
        pv_full_roof_kwh = site.get("pv_full_roof_kwh")

        with st.expander(f"Site {idx+1}: {address}", expanded=True):
            st.markdown(f"**Address:** {address}")
            if canton:
                st.caption(f"Canton: {canton}")
            else:
                st.caption("Canton: (not set – please ensure Sonnendach data is available)")

            # --- 1) Share of annual kWh on weekdays 08:00–18:00 ---
            share_daytime = st.slider(
                f"Roughly what share of annual kWh occurs weekdays 08:00–18:00 for: {address}?",
                min_value=0,
                max_value=100,
                value=60,
                step=5,
                key=f"share_daytime_{idx}",
                help="Ballpark % of annual consumption that happens during working hours (Mon–Fri, 08:00–18:00).",
            )
            share_daytime_frac = share_daytime / 100.0

            # --- 2) Ballpark annual electricity spend (CHF) ---
            spend_choice = st.radio(
                f"Ballpark annual electricity spend (CHF) for: {address}",
                options=["< 100k", "100–300k", "300–800k", "> 800k"],
                index=1,
                key=f"spend_bucket_{idx}",
                help="Pick the closest bracket. This is only used as a ballpark for sizing.",
            )
            annual_spend_chf = get_midpoint_spend(spend_choice)

            # --- 3) Seasonality question ---
            seasonality = st.radio(
                "How pronounced is the seasonal pattern in your electricity consumption?",
                options=[
                    "All months similar (±10%) → Low",
                    "Some seasonality (±10–25%) → Moderate",
                    "Strong seasonality (>±25%) → High",
                ],
                index=1,
                key=f"seasonality_{idx}",
            )

            # --- 4) 24/7 loads question ---
            has_247_loads = st.radio(
                "Do you run any 24/7 loads (refrigeration, server rooms, critical processes)?",
                options=["Yes (reduces volatility)", "No"],
                index=1,
                key=f"loads247_{idx}",
            )

            # ============= DERIVED METRICS ======================

            # 4a) Retrieve avg electricity price per kWh for this canton
            avg_price_per_kwh = None
            if canton and canton in CANTON_KWH_PRICES:
                avg_price_per_kwh = CANTON_KWH_PRICES[canton]
            else:
                st.warning(
                    "Average electricity price for this canton not found. "
                    "Please check CANTON_KWH_PRICES in sonnendach.py."
                )

            # 4b) Compute annual kWh consumption (ballpark)
            annual_kwh = None
            if avg_price_per_kwh:
                annual_kwh = annual_spend_chf / avg_price_per_kwh

            # 4c) Compute self-consumption share:
            #     (annual electricity spend / avg price per kWh) / capacity at full roof
            self_consumption_share = None
            if annual_kwh is not None and pv_full_roof_kwh:
                raw_ratio = annual_kwh / pv_full_roof_kwh
                # Cap between 0 and 1 for sanity
                self_consumption_share = max(0.0, min(1.0, raw_ratio))

            # 4d) Compute annual import cost (CHF) using your formula:
            #     import_CHF = (share*annual_CHF*(1-sc)) + ((1-share)*annual_CHF)
            annual_import_chf = None
            if self_consumption_share is not None:
                annual_import_chf = (
                    share_daytime_frac * annual_spend_chf * (1 - self_consumption_share)
                    + (1 - share_daytime_frac) * annual_spend_chf
                )

            # Display derived numbers to the user
            st.markdown("---")
            st.subheader("Derived indicators (internal sizing logic)")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Ballpark annual spend (CHF)",
                    f"{annual_spend_chf:,.0f}",
                )
            with col2:
                if self_consumption_share is not None:
                    st.metric(
                        "Self-consumption share (ratio)",
                        f"{self_consumption_share:.2f}",
                    )
                else:
                    st.metric("Self-consumption share (ratio)", "n/a")
            with col3:
                if annual_import_chf is not None:
                    st.metric(
                        "Estimated annual imports (CHF)",
                        f"{annual_import_chf:,.0f}",
                        help="Higher is better for Solar21, since imports indicate room for on-site PV + RCP optimisation.",
                    )
                else:
                    st.metric("Estimated annual imports (CHF)", "n/a")

            # Save everything for later blocks/scoring
            st.session_state["block_b_results"][address] = {
                "address": address,
                "canton": canton,
                "share_daytime_pct": share_daytime,
                "share_daytime_frac": share_daytime_frac,
                "spend_bucket": spend_choice,
                "annual_spend_chf": annual_spend_chf,
                "seasonality": seasonality,
                "has_247_loads": has_247_loads,
                "avg_price_per_kwh": avg_price_per_kwh,
                "annual_kwh": annual_kwh,
                "pv_full_roof_kwh": pv_full_roof_kwh,
                "self_consumption_share": self_consumption_share,
                "annual_import_chf": annual_import_chf,
            }

    st.success("Block B completed. You can now continue to the next section.")



# ----------------------------------------------------
# ROUTER
# ----------------------------------------------------
step = st.session_state.step

if step == "language":
    render_language_step()
elif step == "welcome":
    render_welcome_step()
elif step == "addresses":
    render_addresses_step()
elif step == "block_a":
    render_block_a_step()
elif step == "block_b":
    render_block_b_step()
elif step == "results":
    render_results_step()
else:
    # Fallback
    st.session_state.step = "language"
    st.experimental_rerun()
