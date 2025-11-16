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
# GLOBAL CSS (improved styling)
# -------------------------------------------------------
st.markdown("""
<style>
    /* Hide Streamlit sidebar completely */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Clean white background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: #ffffff !important;
    }

    .block-container {
        padding: 3rem 2rem !important;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Text colors - ensure visibility */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #1a1a1a !important;
    }

    /* Radio buttons - make them visible */
    [data-testid="stRadio"] label {
        color: #1a1a1a !important;
    }
    
    [data-testid="stRadio"] > div {
        color: #1a1a1a !important;
    }

    /* Solar21 green buttons */
    .stButton>button {
        background-color: #00FF40 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    .stButton>button:hover {
        background-color: #00DD38 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-1px) !important;
    }

    /* Text inputs */
    input[type="text"] {
        border: 2px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }

    input[type="text"]:focus {
        border-color: #00FF40 !important;
        box-shadow: 0 0 0 2px rgba(0,255,64,0.1) !important;
    }

    /* Select boxes */
    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 6px !important;
    }
    
    /* Dropdown options */
    [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    [role="option"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    [role="option"]:hover {
        background-color: #f0f0f0 !important;
    }

    /* Language selection cards */
    .lang-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .lang-card:hover {
        border-color: #00FF40;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,255,64,0.2);
    }
    
    .lang-card.selected {
        background: #00FF40;
        border-color: #00FF40;
        color: #000;
    }
    
    /* Gray out non-selected language buttons */
    .stButton>button[disabled] {
        background-color: #f0f0f0 !important;
        color: #999999 !important;
        opacity: 0.6;
    }

    /* Sliders */
    .stSlider {
        padding: 1rem 0 !important;
    }

    /* Success/Error messages */
    .stSuccess, .stError {
        padding: 1rem !important;
        border-radius: 6px !important;
    }

    /* Dividers */
    hr {
        margin: 2rem 0 !important;
        border-color: #e0e0e0 !important;
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOGO (centered)
# -------------------------------------------------------
import os
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Try multiple possible paths for the logo
    possible_paths = [
        "Solar21app/solar21_logo.png",
        "solar21_logo.png",
        "./solar21_logo.png",
        "../solar21_logo.png"
    ]
    
    logo_loaded = False
    for path in possible_paths:
        if os.path.exists(path):
            st.image(path, use_container_width=True)
            logo_loaded = True
            break
    
    if not logo_loaded:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:40px;">
                <h1 style="color: #1a1a1a; margin: 0; font-size: 2.5rem;">Solar21</h1>
                <p style="color: #666; font-size: 1.1rem;">Evaluation Tool</p>
            </div>
            """,
            unsafe_allow_html=True
        )
st.markdown("<br>", unsafe_allow_html=True)

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
    st.markdown(f"<h2 style='text-align: center; color: #1a1a1a; font-size: 2rem; margin-bottom: 2rem;'>{TEXT['lang_title']['en']}</h2>", unsafe_allow_html=True)

    # Create language cards
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # English
        selected_class = "selected" if st.session_state.get("language") == "en" else ""
        if st.button("🇬🇧 English", key="lang_en", use_container_width=True):
            st.session_state["language"] = "en"
        
        # French
        selected_class = "selected" if st.session_state.get("language") == "fr" else ""
        if st.button("🇫🇷 Français", key="lang_fr", use_container_width=True):
            st.session_state["language"] = "fr"
        
        # German
        selected_class = "selected" if st.session_state.get("language") == "de" else ""
        if st.button("🇩🇪 Deutsch", key="lang_de", use_container_width=True):
            st.session_state["language"] = "de"

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button(TEXT["continue"][st.session_state["language"]], key="continue_lang", use_container_width=True):
            goto("address_entry")

# -------------------------------------------------------
# PAGE 2 — ENTER ADDRESSES
# -------------------------------------------------------

def page_address_entry():
    L = st.session_state["language"]

    st.title(TEXT["address_title"][L])
    st.markdown("<br>", unsafe_allow_html=True)

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
        st.markdown(f"### 📍 {TEXT['full_address'][L]} {idx+1}")

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

        if entry["roof_area"]:
            st.info(f"🏠 Rooftop area: **{entry['roof_area']} m²**")

        st.markdown("---")

    if st.button(TEXT["save_continue"][L], use_container_width=True):
        # Fetch rooftop data for all addresses before continuing
        with st.spinner("Fetching rooftop data..."):
            for idx, entry in enumerate(st.session_state["addresses"]):
                if entry["address"] and entry["canton"] and not entry["roof_area"]:
                    data = get_sonnendach_info(entry["address"])
                    if data:
                        entry["roof_area"] = data.get("roof_area")
                        entry["roof_pitch"] = data.get("pitch")
                        entry["roof_orientation"] = data.get("orientation")
        goto("questions")

# -------------------------------------------------------
# PAGE 3 — QUESTIONS (ONE PAGE PER ADDRESS)
# -------------------------------------------------------

def page_questions():
    L = st.session_state["language"]
    idx = st.session_state["current_index"]
    site = st.session_state["addresses"][idx]

    st.title(f"{TEXT['questions_title'][L]}")
    st.markdown(f"**📍 {site['address']} ({site['canton']})**")
    st.markdown("---")

    prefix = f"a{idx}_"

    # OWNER TYPE
    st.markdown(f"### {TEXT['owner_type'][L]}")
    owner_type = st.radio(
        "",
        [
            "3 — Public / institutional",
            "2 — Commercial",
            "1 — Private / SME"
        ],
        key=prefix + "owner",
        label_visibility="collapsed"
    )

    # ESG
    st.markdown(f"### {TEXT['esg'][L]}")
    esg = st.radio(
        "",
        ["Yes", "IDK", "No"],
        key=prefix + "esg",
        label_visibility="collapsed"
    )

    # DAYTIME
    st.markdown(f"### {TEXT['daytime'][L]}")
    daytime = st.slider(
        "",
        0, 100, 60,
        key=prefix + "daytime",
        label_visibility="collapsed"
    )
    st.markdown(f"**{daytime}%**")

    # SPEND
    st.markdown(f"### {TEXT['spend'][L]}")
    spend = st.radio(
        "",
        ["<100k", "100–300k", "300–800k", ">800k"],
        key=prefix + "spend",
        label_visibility="collapsed"
    )

    # SEASON
    st.markdown(f"### {TEXT['season'][L]}")
    season = st.radio(
        "",
        ["Low (±10%)", "Moderate (±10–25%)", "High (>25%)"],
        key=prefix + "season",
        label_visibility="collapsed"
    )

    # 24/7
    st.markdown(f"### {TEXT['loads'][L]}")
    loads = st.radio(
        "",
        ["Yes", "No"],
        key=prefix + "247",
        label_visibility="collapsed"
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
        if c1.button("← Back", use_container_width=True):
            st.session_state["current_index"] -= 1

    if c2.button(TEXT["continue"][L], use_container_width=True):
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
    st.markdown("---")

    for idx, site in enumerate(st.session_state["addresses"]):
        ans = st.session_state["answers"][idx]
        
        st.markdown(f"## 📍 {site['address']} ({site['canton']})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Roof Score", ans['roof_score'] or "N/A")
            st.write(f"**Owner type:** {ans['owner_type']}")
            st.write(f"**ESG visibility:** {ans['esg']}")
        
        with col2:
            st.write(f"**Electricity spend:** {ans['spend']}")
            st.write(f"**Daytime consumption:** {ans['daytime']}%")
            st.write(f"**Seasonal variation:** {ans['season']}")
            st.write(f"**24/7 loads:** {ans['loads']}")
        
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
