import streamlit as st
from modules.sonnendach import get_sonnendach_info

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Solar21 Evaluation Tool",
)

# -------------------------------------------------------
# GLOBAL CSS (white background, hide sidebar)
# -------------------------------------------------------
st.markdown("""
<style>

    /* Hide Streamlit sidebar completely */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }

    /* White background everywhere */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: white !important;
        color: black !important;
    }

    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    h1, h2, h3, h4, h5 {
        color: black !important;
    }

    /* Solar21 green buttons */
    .stButton>button {
        background-color: #00FF40 !important;
        color: black !important;
        font-weight: 600 !important;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOGO (centered)
# -------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:20px; margin-bottom:20px;">
        <img src="solar21_logo.png" width="300">
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------------

def goto(page):
    st.session_state["page"] = page

def init_state():
    defaults = {
        "page": "lang",
        "language": "en",   # default English
        "addresses": [],
        "current_index": 0,
        "answers": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -------------------------------------------------------
# MULTI-LANGUAGE TEXTS
# -------------------------------------------------------

TEXT = {
    "lang_title": {
        "en": "Choose your language",
        "fr": "Choisissez votre langue",
        "de": "Wählen Sie Ihre Sprache"
    },
    "continue": {"en": "Continue →", "fr": "Continuer →", "de": "Weiter →"},
    "add_site": {"en": "+ Add another address", "fr": "+ Ajouter une adresse", "de": "+ Eine Adresse hinzufügen"},
    "address_title": {
        "en": "Project Sites — Addresses",
        "fr": "Sites du projet — Adresses",
        "de": "Projektstandorte — Adressen"
    },
    "full_address": {
        "en": "Full address",
        "fr": "Adresse complète",
        "de": "Vollständige Adresse"
    },
    "fetch_data": {
        "en": "Fetch rooftop info",
        "fr": "Charger les données du toit",
        "de": "Dachdaten abrufen"
    },
    "save_continue": {"en": "Save & continue →", "fr": "Enregistrer & continuer →", "de": "Speichern & weiter →"},
    "questions_title": {
        "en": "Site Evaluation",
        "fr": "Évaluation du site",
        "de": "Standortbewertung"
    },
    "owner_type": {
        "en": "Owner type",
        "fr": "Type de propriétaire",
        "de": "Eigentümertyp"
    },
    "esg": {
        "en": "ESG visibility",
        "fr": "Visibilité ESG",
        "de": "ESG-Sichtbarkeit"
    },
    "daytime": {
        "en": "Share of consumption between 08:00–18:00",
        "fr": "Part de consommation entre 08h00–18h00",
        "de": "Anteil des Verbrauchs zwischen 08:00–18:00"
    },
    "spend": {
        "en": "Annual electricity spend",
        "fr": "Dépenses annuelles d'électricité",
        "de": "Jährliche Stromkosten"
    },
    "season": {
        "en": "Seasonal variation",
        "fr": "Variation saisonnière",
        "de": "Saisonale Schwankung"
    },
    "loads": {
        "en": "24/7 loads?",
        "fr": "Charges 24/7 ?",
        "de": "24/7-Betrieb?"
    },
    "results_title": {
        "en": "Final Results — Solar21 Evaluation",
        "fr": "Résultats finaux — Évaluation Solar21",
        "de": "Endergebnisse — Solar21 Bewertung"
    },
    "restart": {"en": "Start again", "fr": "Recommencer", "de": "Neu starten"},
}

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def compute_roof_score(area):
    if area is None:
        return None
    if area > 1000:
        return 3
    elif area > 500:
        return 2
    return 1

def restart_button():
    st.markdown("---")
    if st.button(TEXT["restart"][st.session_state["language"]]):
        st.session_state.clear()
        init_state()

# -------------------------------------------------------
# PAGE 1 — LANGUAGE
# -------------------------------------------------------

def page_lang():
    st.title(TEXT["lang_title"]["en"])

    lang = st.radio(
        "",
        ["English", "Français", "Deutsch"],
        index=0
    )

    if lang == "English":
        st.session_state["language"] = "en"
    elif lang == "Français":
        st.session_state["language"] = "fr"
    else:
        st.session_state["language"] = "de"

    if st.button(TEXT["continue"][st.session_state["language"]]):
        goto("address_entry")

# -------------------------------------------------------
# PAGE 2 — ENTER ADDRESSES
# -------------------------------------------------------

def page_address_entry():
    L = st.session_state["language"]

    st.title(TEXT["address_title"][L])

    if st.button(TEXT["add_site"][L]):
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None,
        })

    if len(st.session_state["addresses"]) == 0:
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None,
        })

    for idx, entry in enumerate(st.session_state["addresses"]):
        st.markdown(f"### {TEXT['full_address'][L]} {idx+1}")

        entry["address"] = st.text_input(
            TEXT["full_address"][L],
            value=entry["address"],
            key=f"addr_{idx}"
        )

        entry["canton"] = st.selectbox(
            "Canton",
            ["", "ZH", "SG", "VD", "BE", "GE", "TI", "VS", "LU", "FR", "AG", "BL",
             "BS", "TG", "SO", "NE", "SH", "ZG", "OW", "NW", "UR", "GL", "AI", "AR", "JU"],
            index=0 if entry["canton"] == "" else
            ["","ZH","SG","VD","BE","GE","TI","VS","LU","FR","AG","BL","BS","TG","SO",
             "NE","SH","ZG","OW","NW","UR","GL","AI","AR","JU"].index(entry["canton"]),
            key=f"canton_{idx}"
        )

        if st.button(f"{TEXT['fetch_data'][L]} ({idx+1})"):
            with st.spinner("Fetching data..."):
                data = get_sonnendach_info(entry["address"])
                if data:
                    entry["roof_area"] = data.get("roof_area")
                    entry["roof_pitch"] = data.get("pitch")
                    entry["roof_orientation"] = data.get("orientation")
                    st.success("OK")
                else:
                    st.error("Could not fetch rooftop data.")

        if entry["roof_area"]:
            st.write(f"Rooftop area: **{entry['roof_area']} m²**")

        st.markdown("---")

    if st.button(TEXT["save_continue"][L]):
        goto("questions")

# -------------------------------------------------------
# PAGE 3 — QUESTIONS (ONE PAGE PER ADDRESS)
# -------------------------------------------------------

def page_questions():
    L = st.session_state["language"]
    idx = st.session_state["current_index"]
    site = st.session_state["addresses"][idx]

    st.title(f"{TEXT['questions_title'][L]} — {site['address']} ({site['canton']})")

    prefix = f"a{idx}_"

    # OWNER TYPE
    owner_type = st.radio(
        "### " + TEXT["owner_type"][L],
        [
            "3 — Public / institutional",
            "2 — Commercial",
            "1 — Private / SME"
        ],
        key=prefix + "owner"
    )

    # ESG
    esg = st.radio(
        "### " + TEXT["esg"][L],
        ["Yes", "IDK", "No"],
        key=prefix + "esg"
    )

    # DAYTIME
    daytime = st.slider(
        "### " + TEXT["daytime"][L],
        0, 100, 60,
        key=prefix + "daytime"
    )

    # SPEND
    spend = st.radio(
        "### " + TEXT["spend"][L],
        ["<100k", "100–300k", "300–800k", ">800k"],
        key=prefix + "spend"
    )

    # SEASON
    season = st.radio(
        "### " + TEXT["season"][L],
        ["Low (±10%)", "Moderate (±10–25%)", "High (>25%)"],
        key=prefix + "season"
    )

    # 24/7
    loads = st.radio(
        "### " + TEXT["loads"][L],
        ["Yes", "No"],
        key=prefix + "247"
    )

    # Save all
    st.session_state["answers"][idx] = {
        "owner_type": owner_type,
        "esg": esg,
        "daytime": daytime,
        "spend": spend,
        "season": season,
        "loads": loads,
        "roof_score": compute_roof_score(site["roof_area"]),
    }

    st.markdown("---")
    c1, c2 = st.columns(2)

    if idx > 0:
        if c1.button("← Back"):
            st.session_state["current_index"] -= 1

    if c2.button(TEXT["continue"][L]):
        if idx < len(st.session_state["addresses"]) - 1:
            st.session_state["current_index"] += 1
        else:
            goto("results")

# -------------------------------------------------------
# PAGE 4 — RESULTS
# -------------------------------------------------------

def page_results():
    L = st.session_state["language"]
    st.title(TEXT["results_title"][L])

    for idx, site in enumerate(st.session_state["addresses"]):
        ans = st.session_state["answers"][idx]
        st.markdown(f"## {site['address']} ({site['canton']})")
        st.write(f"**A1 – Roof score:** {ans['roof_score']}")
        st.write(f"**A2 – Owner type:** {ans['owner_type']}")
        st.write(f"**A3 – ESG:** {ans['esg']}")
        st.write(f"**Electricity spend:** {ans['spend']}")
        st.markdown("---")

    restart_button()

# -------------------------------------------------------
# ROUTER
# -------------------------------------------------------

page = st.session_state["page"]

if page == "lang":
    page_lang()
elif page == "address_entry":
    page_address_entry()
elif page == "questions":
    page_questions()
elif page == "results":
    page_results()
