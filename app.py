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

    /* Solar21 green buttons - DEFAULT for ALL buttons */
    .stButton > button,
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"] {
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

    .stButton > button:hover,
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #00DD38 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* EXCEPTION: Gray out non-selected language buttons ONLY */
    .stButton > button[kind="secondary"] {
        background-color: #f5f5f5 !important;
        color: #999999 !important;
        opacity: 0.5 !important;
        border: 2px solid #e0e0e0 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #f5f5f5 !important;
        transform: none !important;
        box-shadow: none !important;
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

# Center the logo using columns
logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
with logo_col2:
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
            # Center the image within the column
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.image(path, width=200)
            st.markdown('</div>', unsafe_allow_html=True)
            logo_loaded = True
            break
    
    if not logo_loaded:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:20px;">
                <h1 style="color: #1a1a1a; margin: 0; font-size: 2rem;">Solar21</h1>
                <p style="color: #666; font-size: 0.9rem;">Evaluation Tool</p>
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
    "remove_site": {"en": "🗑️ Remove", "fr": "🗑️ Supprimer", "de": "🗑️ Entfernen"},
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
        "en": "Who owns this site?",
        "fr": "Qui est propriétaire de ce site ?",
        "de": "Wer ist Eigentümer dieses Standorts?"
    },
    "owner_type_help": {
        "en": "This helps us understand how easy it is for the owner to finance a solar project.",
        "fr": "Cela nous aide à comprendre la facilité de financement d'un projet solaire pour le propriétaire.",
        "de": "Dies hilft uns zu verstehen, wie einfach es für den Eigentümer ist, ein Solarprojekt zu finanzieren."
    },
    "esg": {
        "en": "Is the owner visibly engaged in sustainability topics?",
        "fr": "Le propriétaire est-il visiblement engagé dans la durabilité ?",
        "de": "Ist der Eigentümer sichtbar im Nachhaltigkeitsbereich engagiert?"
    },
    "esg_help": {
        "en": "This helps estimate how receptive they are to solar solutions.",
        "fr": "Cela aide à estimer leur réceptivité aux solutions solaires.",
        "de": "Dies hilft einzuschätzen, wie aufgeschlossen sie für Solarlösungen sind."
    },
    "daytime": {
        "en": "What share of the site's electricity is used during daytime (08:00–18:00)?",
        "fr": "Quelle part de l'électricité du site est utilisée en journée (08h00–18h00) ?",
        "de": "Welcher Anteil des Stroms wird tagsüber (08:00–18:00) verbraucht?"
    },
    "daytime_help": {
        "en": "Daytime consumption increases the amount of solar electricity the site can use directly, improving economic attractiveness. Choose your best estimate — it doesn't need to be perfect.",
        "fr": "La consommation diurne augmente la part d'électricité solaire utilisée directement, améliorant l'attractivité économique. Choisissez votre meilleure estimation — elle n'a pas besoin d'être parfaite.",
        "de": "Tagesverbrauch erhöht den Anteil an direkt genutztem Solarstrom und verbessert die Wirtschaftlichkeit. Wählen Sie Ihre beste Schätzung — sie muss nicht perfekt sein."
    },
    "spend": {
        "en": "What is the site's annual electricity cost (CHF)?",
        "fr": "Quel est le coût annuel d'électricité du site (CHF) ?",
        "de": "Was sind die jährlichen Stromkosten des Standorts (CHF)?"
    },
    "spend_help": {
        "en": "This indicates the financial importance of energy decisions and the potential for savings.",
        "fr": "Cela indique l'importance financière des décisions énergétiques et le potentiel d'économies.",
        "de": "Dies zeigt die finanzielle Bedeutung von Energieentscheidungen und das Einsparpotenzial."
    },
    "season": {
        "en": "How stable is the site's electricity consumption throughout the year?",
        "fr": "Quelle est la stabilité de la consommation électrique tout au long de l'année ?",
        "de": "Wie stabil ist der Stromverbrauch des Standorts über das Jahr?"
    },
    "season_help": {
        "en": "High seasonality makes it harder to match solar production with consumption.",
        "fr": "Une forte saisonnalité rend plus difficile l'adéquation entre production solaire et consommation.",
        "de": "Hohe Saisonalität erschwert die Anpassung von Solarproduktion und Verbrauch."
    },
    "loads": {
        "en": "Does the site operate equipment that runs 24/7?",
        "fr": "Le site exploite-t-il des équipements fonctionnant 24h/24 7j/7 ?",
        "de": "Betreibt der Standort Geräte, die 24/7 laufen?"
    },
    "loads_help": {
        "en": "Constant loads (cold rooms, servers, manufacturing lines) increase the share of solar energy that can be consumed directly.",
        "fr": "Les charges constantes (chambres froides, serveurs, lignes de production) augmentent la part d'énergie solaire consommée directement.",
        "de": "Konstante Lasten (Kühlräume, Server, Produktionslinien) erhöhen den Anteil direkt verbrauchter Solarenergie."
    },
    "results_title": {
        "en": "Final Results — Solar21 Evaluation",
        "fr": "Résultats finaux — Évaluation Solar21",
        "de": "Endergebnisse — Solar21 Bewertung"
    },
    "score_label": {
        "en": "Solar21 Score",
        "fr": "Score Solar21",
        "de": "Solar21 Bewertung"
    },
    "recommendation_label": {
        "en": "Recommendation",
        "fr": "Recommandation",
        "de": "Empfehlung"
    },
    "roof_score_label": {
        "en": "Roof Score",
        "fr": "Score du toit",
        "de": "Dachbewertung"
    },
    "roof_area_label": {
        "en": "Roof area",
        "fr": "Surface du toit",
        "de": "Dachfläche"
    },
    "owner_type_label": {
        "en": "Owner type",
        "fr": "Type de propriétaire",
        "de": "Eigentümertyp"
    },
    "esg_label": {
        "en": "ESG visibility",
        "fr": "Visibilité ESG",
        "de": "ESG-Sichtbarkeit"
    },
    "spend_label": {
        "en": "Electricity spend",
        "fr": "Dépenses d'électricité",
        "de": "Stromkosten"
    },
    "daytime_label": {
        "en": "Daytime consumption",
        "fr": "Consommation diurne",
        "de": "Tagesverbrauch"
    },
    "season_label": {
        "en": "Seasonal variation",
        "fr": "Variation saisonnière",
        "de": "Saisonale Schwankung"
    },
    "loads_label": {
        "en": "24/7 loads",
        "fr": "Charges 24/7",
        "de": "24/7-Lasten"
    },
    "interpretation": {
        "exceptional": {
            "en": "Exceptional match",
            "fr": "Correspondance exceptionnelle",
            "de": "Außergewöhnliche Übereinstimmung"
        },
        "strong": {
            "en": "Strong match",
            "fr": "Forte correspondance",
            "de": "Starke Übereinstimmung"
        },
        "moderate": {
            "en": "Moderate suitability",
            "fr": "Adéquation modérée",
            "de": "Mäßige Eignung"
        },
        "weak": {
            "en": "Weak alignment",
            "fr": "Faible alignement",
            "de": "Schwache Ausrichtung"
        },
        "poor": {
            "en": "Poor fit",
            "fr": "Mauvaise adéquation",
            "de": "Schlechte Eignung"
        }
    },
    "recommendation": {
        "exceptional": {
            "en": "Engage immediately. Priority 1.",
            "fr": "Engager immédiatement. Priorité 1.",
            "de": "Sofort engagieren. Priorität 1."
        },
        "strong": {
            "en": "Move forward quickly.",
            "fr": "Avancer rapidement.",
            "de": "Schnell voranschreiten."
        },
        "moderate": {
            "en": "Needs deeper analysis (segment loads, roof segmentation).",
            "fr": "Nécessite une analyse plus approfondie (charges par segment, segmentation du toit).",
            "de": "Benötigt tiefere Analyse (Lastsegmente, Dachsegmentierung)."
        },
        "weak": {
            "en": "Evaluate only if roof is large or strategic location.",
            "fr": "Évaluer uniquement si le toit est grand ou l'emplacement stratégique.",
            "de": "Nur bewerten, wenn Dach groß oder strategischer Standort."
        },
        "poor": {
            "en": "Likely not viable for Solar21's model.",
            "fr": "Probablement pas viable pour le modèle Solar21.",
            "de": "Wahrscheinlich nicht für Solar21-Modell geeignet."
        }
    },
    "restart": {"en": "Start again", "fr": "Recommencer", "de": "Neu starten"},
    "composite_score": {
        "en": "Overall Composite Score",
        "fr": "Score composite global",
        "de": "Gesamtbewertung"
    },
    "composite_desc": {
        "en": "Average across all sites",
        "fr": "Moyenne de tous les sites",
        "de": "Durchschnitt aller Standorte"
    },
}

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def compute_roof_score(area):
    """
    Calculate roof score based on usable area in m²
    > 1000 m² = 3
    500-1000 m² = 2
    < 500 m² = 1
    Missing data = 0
    """
    if area is None or area == 0:
        return 0
    if area > 1000:
        return 3
    elif area >= 500:
        return 2
    else:
        return 1

def compute_final_score(answers, roof_score):
    """Compute the final Solar21 site attractiveness score"""
    
    # Extract owner type score
    owner_str = answers["owner_type"]
    if "Public entity" in owner_str or "Entité publique" in owner_str or "Öffentliche Einrichtung" in owner_str:
        owner_type_score = 3
    elif "Standard commercial" in owner_str or "commercial standard" in owner_str or "Standard-Gewerbe" in owner_str:
        owner_type_score = 2
    else:
        owner_type_score = 1
    
    # Extract ESG score
    esg_str = answers["esg"]
    if esg_str.startswith("Yes") or esg_str.startswith("Oui") or esg_str.startswith("Ja"):
        esg_score = 3
    elif esg_str.startswith("Not sure") or esg_str.startswith("Incertain") or esg_str.startswith("Unsicher"):
        esg_score = 2
    else:
        esg_score = 1
    
    # A_total: roof + owner + esg (max 9)
    A_total = roof_score + owner_type_score + esg_score
    
    # Extract spend score
    spend_str = answers["spend"]
    if "Above 800k" in spend_str or "Plus de 800k" in spend_str or "Über 800k" in spend_str:
        spend_score = 4
    elif "300k" in spend_str and "800k" in spend_str:
        spend_score = 3
    elif "100k" in spend_str and "300k" in spend_str:
        spend_score = 2
    else:
        spend_score = 1
    
    # Daytime score (convert percentage to 0-3)
    daytime_pct = answers["daytime"]
    if daytime_pct >= 75:
        daytime_score = 3
    elif daytime_pct >= 50:
        daytime_score = 2
    elif daytime_pct >= 25:
        daytime_score = 1
    else:
        daytime_score = 0
    
    # Seasonality score (inverted - low variation is better)
    season_str = answers["season"]
    if "Low" in season_str or "Faible" in season_str or "Geringe" in season_str:
        season_score = 3
    elif "Moderate" in season_str or "Modérée" in season_str or "Mäßige" in season_str:
        season_score = 2
    else:
        season_score = 1
    
    # 24/7 loads score
    loads_str = answers["loads"]
    if loads_str.startswith("Yes") or loads_str.startswith("Oui") or loads_str.startswith("Ja"):
        loads_score = 3
    else:
        loads_score = 1
    
    # B_total: spend + daytime + season + loads (max 13: 4+3+3+3)
    B_total = spend_score + daytime_score + season_score + loads_score
    
    # Normalize
    A_norm = A_total / 9
    B_norm = B_total / 13  # max is 13 (4+3+3+3)
    
    # Apply weights: 40% structure (A), 60% consumption (B)
    final_score = 0.40 * A_norm + 0.60 * B_norm
    
    # Convert to 0-100 scale
    final_score_100 = final_score * 100
    
    return round(final_score_100, 1)

def get_score_interpretation(score, lang="en"):
    """Return interpretation and recommendation based on score"""
    if score >= 85:
        return (TEXT["interpretation"]["exceptional"][lang], TEXT["recommendation"]["exceptional"][lang], "🟢")
    elif score >= 70:
        return (TEXT["interpretation"]["strong"][lang], TEXT["recommendation"]["strong"][lang], "🟢")
    elif score >= 55:
        return (TEXT["interpretation"]["moderate"][lang], TEXT["recommendation"]["moderate"][lang], "🟡")
    elif score >= 40:
        return (TEXT["interpretation"]["weak"][lang], TEXT["recommendation"]["weak"][lang], "🟠")
    else:
        return (TEXT["interpretation"]["poor"][lang], TEXT["recommendation"]["poor"][lang], "🔴")

def restart_button():
    st.markdown("---")
    if st.button(TEXT["restart"][st.session_state["language"]]):
        st.session_state.clear()
        init_state()
        st.rerun()

# -------------------------------------------------------
# PAGE 1 — LANGUAGE
# -------------------------------------------------------

def page_lang():
    st.markdown(
        f"<h2 style='text-align: center; color: #1a1a1a; font-size: 2rem; margin-bottom: 2rem;'>{TEXT['lang_title']['en']}</h2>",
        unsafe_allow_html=True,
    )

    # Initialize selected language if not set
    if "selected_lang_temp" not in st.session_state:
        st.session_state["selected_lang_temp"] = None

    # Create language buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # English
        button_type = "primary" if st.session_state["selected_lang_temp"] == "en" else "secondary"
        if st.button("🇬🇧 English", key="lang_en", use_container_width=True, type=button_type):
            st.session_state["language"] = "en"
            st.session_state["selected_lang_temp"] = "en"
            st.rerun()
        
        # French
        button_type = "primary" if st.session_state["selected_lang_temp"] == "fr" else "secondary"
        if st.button("🇫🇷 Français", key="lang_fr", use_container_width=True, type=button_type):
            st.session_state["language"] = "fr"
            st.session_state["selected_lang_temp"] = "fr"
            st.rerun()
        
        # German
        button_type = "primary" if st.session_state["selected_lang_temp"] == "de" else "secondary"
        if st.button("🇩🇪 Deutsch", key="lang_de", use_container_width=True, type=button_type):
            st.session_state["language"] = "de"
            st.session_state["selected_lang_temp"] = "de"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show selected language with checkmark
        if st.session_state["selected_lang_temp"]:
            lang_names = {"en": "English", "fr": "Français", "de": "Deutsch"}
            st.success(f"✓ Selected language: **{lang_names[st.session_state['selected_lang_temp']]}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Only enable continue if a language is selected
        if st.session_state["selected_lang_temp"]:
            if st.button(
                TEXT["continue"][st.session_state["language"]],
                key="continue_lang",
                use_container_width=True,
                type="primary",  # make Continue green like selected language
            ):
                goto("address_entry")
                st.rerun()

# -------------------------------------------------------
# PAGE 2 — ENTER ADDRESSES
# -------------------------------------------------------

def page_address_entry():
    L = st.session_state["language"]

    st.title(TEXT["address_title"][L])
    st.markdown("<br>", unsafe_allow_html=True)

    col_add, col_space = st.columns([1, 3])
    with col_add:
        if st.button(TEXT["add_site"][L]):
            st.session_state["addresses"].append({
                "address": "",
                "canton": "",
                "roof_area": None,
                "roof_pitch": None,
                "roof_orientation": None,
            })
            st.rerun()

    if len(st.session_state["addresses"]) == 0:
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None,
        })

    for idx, entry in enumerate(st.session_state["addresses"]):
        col_title, col_remove = st.columns([4, 1])
        with col_title:
            st.markdown(f"### 📍 {TEXT['full_address'][L]} {idx+1}")
        with col_remove:
            if len(st.session_state["addresses"]) > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(TEXT["remove_site"][L], key=f"remove_{idx}"):
                    st.session_state["addresses"].pop(idx)
                    st.rerun()

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

    # Create a placeholder for the loading message
    status_placeholder = st.empty()
    
    if st.button(TEXT["save_continue"][L], use_container_width=True):
        # Show loading status
        with status_placeholder.container():
            st.info("🔄 Fetching rooftop data, please wait...")
        
        # Fetch rooftop data for all addresses before continuing
        all_success = True
        with st.spinner(""):
            for idx, entry in enumerate(st.session_state["addresses"]):
                if entry["address"] and entry["canton"] and not entry["roof_area"]:
                    data = get_sonnendach_info(entry["address"])
                    if data:
                        entry["roof_area"] = data.get("roof_area")
                        entry["roof_pitch"] = data.get("pitch")
                        entry["roof_orientation"] = data.get("orientation")
                    else:
                        all_success = False
        
        if all_success:
            status_placeholder.success("✅ Data loaded successfully! Proceeding...")
            import time
            time.sleep(1)
            goto("questions")
            st.rerun()
        else:
            status_placeholder.warning("⚠️ Some rooftop data could not be fetched. You can continue anyway.")
            import time
            time.sleep(2)
            goto("questions")
            st.rerun()

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

    # Define answer options for each language
    owner_options = {
        "en": [
            "Public entity or large institutional owner — Hospitals, municipalities, cantonal buildings, universities, major corporates. Typically low cost of capital and stable approval processes.",
            "Standard commercial owner — Regular private companies, logistics firms, retail centers, property companies.",
            "Private individual or small SME — Smaller budgets, higher financing constraints, usually slower decision cycles."
        ],
        "fr": [
            "Entité publique ou grand propriétaire institutionnel — Hôpitaux, municipalités, bâtiments cantonaux, universités, grandes entreprises. Généralement faible coût du capital et processus d'approbation stables.",
            "Propriétaire commercial standard — Entreprises privées régulières, entreprises de logistique, centres commerciaux, sociétés immobilières.",
            "Particulier ou petite PME — Budgets plus petits, contraintes de financement plus élevées, cycles de décision généralement plus lents."
        ],
        "de": [
            "Öffentliche Einrichtung oder großer institutioneller Eigentümer — Krankenhäuser, Gemeinden, Kantonsgebäude, Universitäten, große Unternehmen. Typischerweise niedrige Kapitalkosten und stabile Genehmigungsverfahren.",
            "Standard-Gewerbeinhaber — Reguläre Privatunternehmen, Logistikunternehmen, Einkaufszentren, Immobiliengesellschaften.",
            "Privatperson oder kleines KMU — Kleinere Budgets, höhere Finanzierungsbeschränkungen, in der Regel langsamere Entscheidungszyklen."
        ]
    }

    esg_options = {
        "en": [
            "Yes — sustainability is clearly part of their identity (Website, annual reports, labels, certifications, public commitments)",
            "Not sure — no clear signal (No obvious information available)",
            "No — sustainability is not a visible priority (No ESG communication, purely cost-driven decision-making)"
        ],
        "fr": [
            "Oui — la durabilité fait clairement partie de leur identité (Site web, rapports annuels, labels, certifications, engagements publics)",
            "Incertain — aucun signal clair (Aucune information évidente disponible)",
            "Non — la durabilité n'est pas une priorité visible (Aucune communication ESG, décisions purement basées sur les coûts)"
        ],
        "de": [
            "Ja — Nachhaltigkeit ist eindeutig Teil ihrer Identität (Website, Jahresberichte, Labels, Zertifizierungen, öffentliche Verpflichtungen)",
            "Unsicher — kein klares Signal (Keine offensichtlichen Informationen verfügbar)",
            "Nein — Nachhaltigkeit ist keine sichtbare Priorität (Keine ESG-Kommunikation, rein kostenorientierte Entscheidungsfindung)"
        ]
    }

    spend_options = {
        "en": ["Below 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Above 800k CHF"],
        "fr": ["Moins de 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Plus de 800k CHF"],
        "de": ["Unter 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Über 800k CHF"]
    }

    season_options = {
        "en": [
            "Low seasonal variation (±10%) — Consumption stays stable across the year",
            "Moderate variation (±10–25%) — Some seasonal differences (e.g., cooling or heating loads)",
            "High variation (>25%) — Strong seasonality, big differences between summer and winter"
        ],
        "fr": [
            "Faible variation saisonnière (±10%) — La consommation reste stable tout au long de l'année",
            "Variation modérée (±10–25%) — Quelques différences saisonnières (par ex. charges de refroidissement ou de chauffage)",
            "Forte variation (>25%) — Forte saisonnalité, grandes différences entre été et hiver"
        ],
        "de": [
            "Geringe saisonale Schwankung (±10%) — Verbrauch bleibt über das Jahr stabil",
            "Mäßige Schwankung (±10–25%) — Einige saisonale Unterschiede (z.B. Kühl- oder Heizlasten)",
            "Hohe Schwankung (>25%) — Starke Saisonalität, große Unterschiede zwischen Sommer und Winter"
        ]
    }

    loads_options = {
        "en": [
            "Yes — important 24/7 loads (Cold storage, server rooms, industrial baseload, data centers)",
            "No — mainly daytime or irregular loads"
        ],
        "fr": [
            "Oui — charges importantes 24h/24 7j/7 (Stockage frigorifique, salles de serveurs, charge de base industrielle, centres de données)",
            "Non — principalement charges diurnes ou irrégulières"
        ],
        "de": [
            "Ja — wichtige 24/7-Lasten (Kühlräume, Serverräume, industrielle Grundlast, Rechenzentren)",
            "Nein — hauptsächlich Tages- oder unregelmäßige Lasten"
        ]
    }

    # OWNER TYPE
    st.markdown(f"### {TEXT['owner_type'][L]}")
    st.caption(TEXT["owner_type_help"][L])
    owner_type = st.radio(
        "",
        owner_options[L],
        key=prefix + "owner",
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ESG
    st.markdown(f"### {TEXT['esg'][L]}")
    st.caption(TEXT["esg_help"][L])
    esg = st.radio(
        "",
        esg_options[L],
        key=prefix + "esg",
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # DAYTIME
    st.markdown(f"### {TEXT['daytime'][L]}")
    st.caption(TEXT["daytime_help"][L])
    daytime = st.slider(
        "",
        0, 100, 60,
        key=prefix + "daytime",
        label_visibility="collapsed"
    )
    st.markdown(f"**{daytime}%**")
    st.markdown("<br>", unsafe_allow_html=True)

    # SPEND
    st.markdown(f"### {TEXT['spend'][L]}")
    st.caption(TEXT["spend_help"][L])
    spend = st.radio(
        "",
        spend_options[L],
        key=prefix + "spend",
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # SEASON
    st.markdown(f"### {TEXT['season'][L]}")
    st.caption(TEXT["season_help"][L])
    season = st.radio(
        "",
        season_options[L],
        key=prefix + "season",
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # 24/7
    st.markdown(f"### {TEXT['loads'][L]}")
    st.caption(TEXT["loads_help"][L])
    loads = st.radio(
        "",
        loads_options[L],
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
            st.rerun()

    if c2.button(TEXT["continue"][L], use_container_width=True):
        if idx < len(st.session_state["addresses"]) - 1:
            st.session_state["current_index"] += 1
            st.rerun()
        else:
            goto("results")
            st.rerun()

# -------------------------------------------------------
# PAGE 4 — RESULTS
# -------------------------------------------------------

def page_results():
    L = st.session_state["language"]
    st.title(TEXT["results_title"][L])
    st.markdown("---")

    # Calculate all scores first
    all_scores = []
    
    for idx, site in enumerate(st.session_state["addresses"]):
        ans = st.session_state["answers"][idx]
        
        # Recalculate roof score from the actual roof area
        roof_score = compute_roof_score(site.get("roof_area"))
        
        # Calculate the final score
        final_score = compute_final_score(ans, roof_score)
        all_scores.append(final_score)
        interpretation, recommendation, emoji = get_score_interpretation(final_score, L)
        
        st.markdown(f"## 📍 {site['address']} ({site['canton']})")
        
        # Display the main score prominently
        col_score, col_interp = st.columns([1, 2])
        
        with col_score:
            st.metric(TEXT["score_label"][L], f"{final_score}/100")
        
        with col_interp:
            st.markdown(f"### {emoji} {interpretation}")
            st.write(f"**{TEXT['recommendation_label'][L]}:** {recommendation}")
        
        st.markdown("---")
        
        # Detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{TEXT['roof_score_label'][L]}:** {roof_score}/3")
            if site.get('roof_area'):
                st.write(f"*({TEXT['roof_area_label'][L]}: {site['roof_area']} m²)*")
            st.write(f"**{TEXT['owner_type_label'][L]}:** {ans['owner_type'].split('—')[0].strip()}")
            st.write(f"**{TEXT['esg_label'][L]}:** {ans['esg'].split('—')[0].strip()}")
        
        with col2:
            st.write(f"**{TEXT['spend_label'][L]}:** {ans['spend']}")
            st.write(f"**{TEXT['daytime_label'][L]}:** {ans['daytime']}%")
            st.write(f"**{TEXT['season_label'][L]}:** {ans['season'].split('—')[0].strip()}")
            st.write(f"**{TEXT['loads_label'][L]}:** {ans['loads'].split('—')[0].strip()}")
        
        st.markdown("---")
    
    # If multiple addresses, show composite score
    if len(st.session_state["addresses"]) > 1:
        composite_score = sum(all_scores) / len(all_scores)
        composite_interpretation, composite_recommendation, composite_emoji = get_score_interpretation(composite_score, L)
        
        st.markdown(f"## 🏢 {TEXT['composite_score'][L]}")
        st.caption(TEXT['composite_desc'][L])
        
        col_score, col_interp = st.columns([1, 2])
        
        with col_score:
            st.metric(TEXT["score_label"][L], f"{round(composite_score, 1)}/100")
        
        with col_interp:
            st.markdown(f"### {composite_emoji} {composite_interpretation}")
            st.write(f"**{TEXT['recommendation_label'][L]}:** {composite_recommendation}")
        
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
