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
# NAVIGATION BUTTONS
# ----------------------------------------------------
def nav_buttons(back_step=None, next_step=None, next_label="Continue →"):
    col1, col2 = st.columns([1,1])
    if back_step:
        if col1.button("← Back"):
            st.session_state.step = back_step
            st.rerun()

    if next_step:
        if col2.button(next_label, type="primary"):
            st.session_state.step = next_step
            st.rerun()


# ----------------------------------------------------
# STEP 1: LANGUAGE SELECTION
# ----------------------------------------------------
def render_language_step():

    st.title("Solar21 Pre-Check")

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


# ----------------------------------------------------
# STEP 2: WELCOME PAGE
# ----------------------------------------------------
def render_welcome_step():
    lang = st.session_state.get("language", "en")

    TEXT = {
        "en": {
            "title": "Welcome to the Solar21 Partner Pre-Check",
            "text": "Evaluate in **under two minutes** whether your client’s building fits Solar21’s profile.",
            "next": "Next →",
            "back": "← Back",
        },
        "fr": {
            "title": "Bienvenue sur le pré-check partenaire Solar21",
            "text": "Évaluez en **moins de deux minutes** si le bâtiment de votre client correspond aux critères Solar21.",
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
    st.write("")

    nav_buttons(back_step="language", next_step="addresses", next_label=TEXT[lang]["next"])


# ----------------------------------------------------
# STEP 3: ADDRESS INPUT + USER CHOOSES CANTON
# ----------------------------------------------------
def render_addresses_step():
    st.title("Client Addresses")

    if "addresses" not in st.session_state:
        st.session_state["addresses"] = []
    if "cantons" not in st.session_state:
        st.session_state["cantons"] = {}

    num_addresses = st.number_input(
        "How many addresses do you want to enter?",
        min_value=1,
        max_value=20,
        value=max(1, len(st.session_state["addresses"])),
        step=1,
    )

    addresses = st.session_state["addresses"]
    if len(addresses) < num_addresses:
        addresses += [""] * (num_addresses - len(addresses))
    else:
        addresses = addresses[:num_addresses]
    st.session_state["addresses"] = addresses

    CANTON_LIST = [
        "Zurich", "Bern", "Lucerne", "Uri", "Schwyz", "Obwalden", "Nidwalden", "Glarus", "Zug",
        "Fribourg", "Solothurn", "Basel-Stadt", "Basel-Landschaft", "Schaffhausen", "Appenzell Ausserrhoden",
        "Appenzell Innerrhoden", "St. Gallen", "Graubünden", "Aargau", "Thurgau", "Ticino",
        "Vaud", "Valais", "Neuchâtel", "Geneva", "Jura"
    ]

    with st.form("address_form"):
        for i in range(num_addresses):
            addr = st.text_input(f"Address {i+1}", addresses[i], key=f"addr_{i}")
            st.session_state["addresses"][i] = addr

            st.session_state["cantons"][addr] = st.selectbox(
                f"Canton for {addr or 'Address'}",
                CANTON_LIST,
                key=f"canton_{i}",
            )

        submitted = st.form_submit_button("Save and continue →")

    if submitted:
        valid_addresses = [a for a in st.session_state["addresses"] if a.strip()]
        st.session_state["passed_addresses"] = [
            {"address": a, "canton": st.session_state["cantons"][a]}
            for a in valid_addresses
        ]
        st.session_state.step = "block_a"
        st.rerun()

    nav_buttons(back_step="welcome")


# ----------------------------------------------------
# STEP 4: BLOCK A — ROI / OWNER QUESTIONS
# ----------------------------------------------------
def render_block_a_step():
    st.title("Block A — Owner ROI & Impact (40%)")

    passed = st.session_state.get("passed_addresses", [])

    st.subheader("A1 — Roof scale (automatic)")
    st.write("The optimal roof size for Solar21 is > 1000 m².")

    # For demo, random placeholder (in real app you use Sonnendach scraping)
    roof_areas = [3000] * len(passed)
    avg_area = sum(roof_areas) / len(roof_areas)
    A1_score = 3 if avg_area >= 3000 else (2 if avg_area >= 1000 else 1)
    st.info(f"Avg roof area: {avg_area:.1f} m² → Score {A1_score}")

    st.session_state["A1_scores"] = {p["address"]: A1_score for p in passed}

    st.write("")

    st.subheader("A2 — Owner category (WACC proxy)")
    st.write("Choose **the type of owner**. This affects required returns and deal feasibility.")

    A2_scores = {}
    for p in passed:
        addr = p["address"]
        choice = st.radio(
            f"Owner type for {addr}",
            [
                "3 — Public, institutional, very low cost of capital",
                "2 — Standard commercial owner",
                "1 — Private individual / SME with high capital constraints"
            ],
            key=f"A2_{addr}"
        )
        A2_scores[addr] = int(choice[0])
    st.session_state["A2_scores"] = A2_scores

    st.write("")

    st.subheader("A3 — ESG visibility")
    st.write("Is the owner **actively interested** in sustainability benefits?")

    map_esg = {"Yes": 3, "IDK": 2, "No": 1}
    A3_scores = {}
    for p in passed:
        addr = p["address"]
        ch = st.radio(f"ESG relevance for {addr}", ["Yes", "IDK", "No"], key=f"A3_{addr}")
        A3_scores[addr] = map_esg[ch]
    st.session_state["A3_scores"] = A3_scores

    nav_buttons(back_step="addresses", next_step="block_b")


# ----------------------------------------------------
# STEP 5: BLOCK B — CONSUMPTION / FINANCIAL
# ----------------------------------------------------
def render_block_b_step():
    st.title("Block B — Consumption Profile & Financial Attractiveness")

    passed = st.session_state.get("passed_addresses", [])
    if "block_b_results" not in st.session_state:
        st.session_state["block_b_results"] = {}

    def midpoint(bucket):
        return {
            "< 100k": 50_000,
            "100–300k": 200_000,
            "300–800k": 550_000,
            "> 800k": 900_000,
        }.get(bucket, 0)

    ELECTRICITY_PRICES = {
        "Vaud": 0.3226, "Geneva": 0.2422, "St. Gallen": 0.2772,
        "Zurich": 0.2239, "Bern": 0.2550, "Ticino": 0.2852
    }

    for i, site in enumerate(passed):
        addr = site["address"]
        canton = site["canton"]

        st.subheader(f"🏢 {addr}")

        # Q1 daytime %
        daytime = st.slider(
            f"Typical share of consumption during weekdays 08:00–18:00 at {addr}",
            0, 100, 60, 5, key=f"daytime_{i}"
        )
        daytime_frac = daytime / 100

        # Q2 annual spend
        spend = st.radio(
            f"Annual electricity bill for {addr}",
            ["< 100k", "100–300k", "300–800k", "> 800k"],
            key=f"spend_{i}"
        )
        annual_chf = midpoint(spend)

        # Q3 seasonality
        season = st.radio(
            f"Seasonality of electricity usage at {addr}",
            ["Low (±10%)", "Moderate (±10–25%)", "High (±25%)"],
            key=f"season_{i}"
        )

        # Q4 24/7 loads
        loads247 = st.radio(
            f"Does {addr} have stable 24/7 loads?",
            ["Yes", "No"],
            key=f"load247_{i}"
        )

        # Compute
        price = ELECTRICITY_PRICES.get(canton, None)
        annual_kwh = annual_chf / price if price else None
        pv100 = 550_000  # placeholder
        sc = min(1, annual_kwh / pv100) if annual_kwh and pv100 else None
        imports = daytime_frac * annual_chf * (1 - sc) + (1 - daytime_frac) * annual_chf if sc is not None else None

        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        col1.metric("Annual spend (CHF)", f"{annual_chf:,.0f}")
        col2.metric("Self-consumption", "n/a" if sc is None else f"{sc:.2f}")
        col3.metric("Imports (CHF)", "n/a" if imports is None else f"{imports:,.0f}")

        st.session_state["block_b_results"][addr] = {
            "annual_spend_chf": annual_chf,
            "self_consumption_share": sc,
            "annual_import_chf": imports,
        }

    nav_buttons(back_step="block_a", next_step="results")


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

    for site in passed:
        addr = site["address"]
        st.subheader(addr)
        st.write(f"**A1 (Roof):** {A1.get(addr)}")
        st.write(f"**A2 (WACC):** {A2.get(addr)}")
        st.write(f"**A3 (ESG):** {A3.get(addr)}")

        imports = B.get(addr, {}).get("annual_import_chf")
        st.write(f"**Annual imports (CHF):** {imports if imports else 'None'}")

        st.markdown("---")

    if st.button("🔄 Start again"):
        st.session_state.clear()
        st.session_state.step = "language"
        st.rerun()

    nav_buttons(back_step="block_b")


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
