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
# STEP 1 — LANGUAGE (auto-continue)
# ----------------------------------------------------
def render_language_step():
    st.markdown(
        """
        <div class="progress-wrapper"><div class="progress-bar"></div></div>
        """,
        unsafe_allow_html=True,
    )

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
# STEP 2 — WELCOME
# ----------------------------------------------------
def render_welcome_step():
    lang = st.session_state.language

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

    col1, col2 = st.columns(2)

    if col1.button(TEXT[lang]["back"]):
        st.session_state.step = "language"
        st.rerun()

    if col2.button(TEXT[lang]["next"], type="primary"):
        st.session_state.step = "addresses"
        st.rerun()


# ----------------------------------------------------
# STEP 3 — ADDRESS INPUT + canton dropdown
# ----------------------------------------------------
def render_addresses_step():
    st.title("Client Addresses")

    try:
        from modules.sonnendach import fetch_address_data
        sonnendach_ok = True
    except:
        sonnendach_ok = False
        st.error("⚠️ Sonnendach module missing or broken.")

    if "addresses" not in st.session_state:
        st.session_state.addresses = []

    if "cantons_selected" not in st.session_state:
        st.session_state.cantons_selected = {}

    # Number of fields
    count = st.number_input(
        "How many addresses?",
        min_value=1,
        max_value=20,
        step=1,
        value=max(1, len(st.session_state.addresses))
    )

    # Resize internal list
    lst = st.session_state.addresses
    if len(lst) < count:
        lst += [""] * (count - len(lst))
    else:
        lst = lst[:count]
    st.session_state.addresses = lst

    CANTON_OPTIONS = [
        "AG","AI","AR","BE","BL","BS","FR","GE","GL","GR",
        "JU","LU","NE","NW","OW","SG","SH","SO","SZ","TG",
        "TI","UR","VD","VS","ZG","ZH"
    ]

    with st.form("addr_form"):
        for i in range(count):
            colA, colB = st.columns([3,1])
            st.session_state.addresses[i] = colA.text_input(
                f"Address {i+1}",
                st.session_state.addresses[i],
                key=f"addr_{i}"
            )

            st.session_state.cantons_selected[i] = colB.selectbox(
                "Canton",
                CANTON_OPTIONS,
                key=f"ct_{i}"
            )

        submitted = st.form_submit_button("Save and continue →")

    if submitted:
        cleaned = [a.strip() for a in st.session_state.addresses if a.strip()]
        if not cleaned:
            st.error("Enter at least one valid address.")
            return

        enriched = []
        for idx, addr in enumerate(cleaned):
            canton = st.session_state.cantons_selected.get(idx)

            if sonnendach_ok:
                data = fetch_address_data(addr)
            else:
                data = {"address": addr}

            data["canton"] = canton
            enriched.append(data)

        st.session_state.passed_addresses = enriched
        st.session_state.step = "block_a"
        st.rerun()


# ----------------------------------------------------
# STEP 4 — BLOCK A
# ----------------------------------------------------
def render_block_a_step():
    st.title("Block A — Owner ROI & Impact")

    passed = st.session_state.get("passed_addresses", [])
    if not passed:
        st.error("Missing address data.")
        st.session_state.step = "addresses"
        st.rerun()

    # A1 — Roof size
    areas = [float(p.get("surface_area_m2") or 0) for p in passed]
    avg_area = sum(areas) / len(areas) if areas else 0

    if avg_area >= 3000:
        score = 3
    elif avg_area >= 1000:
        score = 2
    else:
        score = 1

    st.info(f"Avg roof area: {avg_area:.1f} m² → Score {score}")

    st.session_state.A1_scores = {p["address"]: score for p in passed}

    # A2 — WACC proxy
    A2 = {}
    for p in passed:
        addr = p["address"]
        A2[addr] = st.radio(
            f"WACC category for {addr}",
            [3, 2, 1],
            key=f"A2_{addr}"
        )
    st.session_state.A2_scores = A2

    # A3 — ESG
    A3 = {}
    for p in passed:
        addr = p["address"]
        val = st.radio(
            f"ESG relevance for {addr}",
            ["Yes","IDK","No"],
            key=f"A3_{addr}"
        )
        A3[addr] = {"Yes":3,"IDK":2,"No":1}[val]
    st.session_state.A3_scores = A3

    if st.button("Continue to Block B →", type="primary"):
        st.session_state.step = "block_b"
        st.rerun()


# ----------------------------------------------------
# STEP 5 — BLOCK B
# ----------------------------------------------------
def render_block_b_step():
    st.title("Block B — Consumption Profile & Financial Attractiveness")

    from modules.sonnendach import ELECTRICITY_PRICES

    passed = st.session_state.get("passed_addresses", [])
    if not passed:
        st.error("Missing address data.")
        st.session_state.step = "addresses"
        st.rerun()

    if "block_b_results" not in st.session_state:
        st.session_state.block_b_results = {}

    def midpoint(bucket):
        return {
            "< 100k": 50_000,
            "100–300k": 200_000,
            "300–800k": 550_000,
            "> 800k": 900_000
        }.get(bucket, 0)

    for i, site in enumerate(passed):
        addr = site["address"]
        canton = site.get("canton")
        pv100 = site.get("pv_full_roof_kwh")

        st.subheader(f"🏢 {addr}")

        # Inputs
        daytime = st.slider(
            f"Daytime % at {addr}",
            0, 100, 60, 5,
            key=f"dt_{i}"
        )
        s = daytime / 100

        spend_bucket = st.radio(
            f"Annual spend at {addr}",
            ["< 100k","100–300k","300–800k","> 800k"],
            index=1,
            key=f"sb_{i}"
        )
        annual_chf = midpoint(spend_bucket)

        seasonality = st.radio(
            f"Seasonality at {addr}",
            [
                "Low (±10%)",
                "Moderate (±10–25%)",
                "High (>±25%)"
            ],
            index=1,
            key=f"ssn_{i}"
        )

        loads247 = st.radio(
            f"24/7 loads at {addr}?",
            ["Yes","No"],
            key=f"l247_{i}"
        )

        # Derivations
        price = ELECTRICITY_PRICES.get(canton)
        annual_kwh = annual_chf / price if price else None
        sc = max(0, min(1, (annual_kwh / pv100))) if (annual_kwh and pv100) else None
        import_chf = (
            s * annual_chf * (1 - sc) + (1 - s) * annual_chf
        ) if sc is not None else None

        # Display
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        col1.metric("Annual spend (CHF)", f"{annual_chf:,.0f}")
        col2.metric("Self-consumption", f"{sc:.2f}" if sc is not None else "n/a")
        col3.metric(
            "Imports (CHF)",
            f"{import_chf:,.0f}" if import_chf is not None else "n/a"
        )

        # Store
        st.session_state.block_b_results[addr] = {
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
            "annual_import_chf": import_chf
        }

    if st.button("Continue to Results →", type="primary"):
        st.session_state.step = "results"
        st.rerun()


# ----------------------------------------------------
# STEP 6 — RESULTS
# ----------------------------------------------------
def render_results_step():
    st.title("Final Results — Solar21 Evaluation")

    passed = st.session_state.get("passed_addresses", [])
    A1 = st.session_state.get("A1_scores", {})
    A2 = st.session_state.get("A2_scores", {})
    A3 = st.session_state.get("A3_scores", {})
    B = st.session_state.get("block_b_results", {})

    for p in passed:
        addr = p["address"]
        st.subheader(addr)
        st.write(f"A1 (Roof): {A1.get(addr)}")
        st.write(f"A2 (WACC): {A2.get(addr)}")
        st.write(f"A3 (ESG): {A3.get(addr)}")
        st.write(f"Annual imports (CHF): {B.get(addr,{}).get('annual_import_chf')}")


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
    st.session_state.step = "language"
    st.rerun()
