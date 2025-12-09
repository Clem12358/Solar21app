import json
import os
import base64
from pathlib import Path

import streamlit as st
# sonnendach auto-fetch removed - users will enter data manually via sonnendach.ch link

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Solar21 Evaluation Tool",
)

# -------------------------------------------------------
# INTRO VIDEO (plays once on first visit)
# -------------------------------------------------------
if "intro_video_watched" not in st.session_state:
    st.session_state.intro_video_watched = False

# Check if video ended via query param
query_params = st.query_params.to_dict()
if query_params.get("video_ended") == "true":
    st.session_state.intro_video_watched = True
    st.query_params.clear()
    st.rerun()

if not st.session_state.intro_video_watched:
    # Find the video file
    video_paths = ["My Movie.mp4", "Solar21app/My Movie.mp4", "./My Movie.mp4"]
    video_path = None
    for vp in video_paths:
        if os.path.exists(vp):
            video_path = vp
            break

    if video_path:
        # Read and encode video as base64
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()

        # Create fullscreen video player with autoplay (muted required for autoplay)
        st.markdown("""
        <style>
            /* Hide everything except our video container */
            .block-container { padding: 0 !important; max-width: 100% !important; }
            header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
            [data-testid="stAppViewContainer"] {
                background: #000 !important;
                padding: 0 !important;
            }
            html, body, [data-testid="stApp"] {
                background: #000 !important;
                overflow: hidden !important;
            }

            .video-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: #000;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }

            .video-container video {
                max-width: 100%;
                max-height: 90vh;
                object-fit: contain;
            }

            /* Ensure Streamlit button is visible */
            .stButton {
                position: fixed !important;
                bottom: 30px !important;
                right: 30px !important;
                z-index: 10001 !important;
            }

            .stButton > button {
                background: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
                padding: 10px 25px !important;
                font-size: 14px !important;
                border-radius: 25px !important;
            }

            .stButton > button:hover {
                background: rgba(255, 255, 255, 0.4) !important;
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <meta http-equiv="refresh" content="17;url=?video_ended=true">
        <div class="video-container">
            <video id="introVideo" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        """, unsafe_allow_html=True)

        # Skip button - visible and clickable
        if st.button("Skip ⏭", key="skip_intro"):
            st.session_state.intro_video_watched = True
            st.rerun()

        # Stop execution here - don't show the rest of the app
        st.stop()
    else:
        # Video not found, skip intro
        st.session_state.intro_video_watched = True

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
# LOGO (centered with high quality)
# -------------------------------------------------------

# Try multiple possible paths for the logo
possible_logo_paths = [
    "solar21_logo.png",
    "Solar21app/solar21_logo.png",
    "./solar21_logo.png",
    "../solar21_logo.png"
]

logo_loaded = False
for logo_path in possible_logo_paths:
    if os.path.exists(logo_path):
        # Load logo as base64 for high quality display
        with open(logo_path, "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()

        # Display centered logo using HTML (better centering than st.columns)
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
                <img src="data:image/png;base64,{logo_base64}"
                     style="width: 250px; height: auto; image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges;"
                     alt="Solar21 Logo">
            </div>
            """,
            unsafe_allow_html=True
        )
        logo_loaded = True
        break

if not logo_loaded:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
            <div style="text-align: center;">
                <h1 style="color: #1a1a1a; margin: 0; font-size: 2rem;">Solar21</h1>
                <p style="color: #666; font-size: 0.9rem;">Evaluation Tool</p>
            </div>
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

WEIGHTS_FILE = Path("weights.json")
DEFAULT_WEIGHTS = {
    "structure": 0.40,
    "consumption": 0.60,
    # Sub-weights for structure (must sum to 1.0)
    "sub_roof": 0.40,
    "sub_owner": 0.30,
    "sub_esg": 0.30,
    # Sub-weights for consumption (must sum to 1.0)
    "sub_spend": 0.30,
    "sub_daytime": 0.25,
    "sub_season": 0.25,
    "sub_loads": 0.20,
}
EMPLOYEE_PASSWORD = "28102025"


def _load_weights_from_disk():
    if WEIGHTS_FILE.exists():
        try:
            with WEIGHTS_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)

            structure = float(data.get("structure", DEFAULT_WEIGHTS["structure"]))
            consumption = float(data.get("consumption", DEFAULT_WEIGHTS["consumption"]))
            total = structure + consumption

            if total > 0:
                weights = {
                    "structure": structure / total,
                    "consumption": consumption / total,
                }
            else:
                weights = {
                    "structure": DEFAULT_WEIGHTS["structure"],
                    "consumption": DEFAULT_WEIGHTS["consumption"],
                }

            # Load sub-weights for structure
            sub_roof = float(data.get("sub_roof", DEFAULT_WEIGHTS["sub_roof"]))
            sub_owner = float(data.get("sub_owner", DEFAULT_WEIGHTS["sub_owner"]))
            sub_esg = float(data.get("sub_esg", DEFAULT_WEIGHTS["sub_esg"]))
            struct_total = sub_roof + sub_owner + sub_esg
            if struct_total > 0:
                weights["sub_roof"] = sub_roof / struct_total
                weights["sub_owner"] = sub_owner / struct_total
                weights["sub_esg"] = sub_esg / struct_total
            else:
                weights["sub_roof"] = DEFAULT_WEIGHTS["sub_roof"]
                weights["sub_owner"] = DEFAULT_WEIGHTS["sub_owner"]
                weights["sub_esg"] = DEFAULT_WEIGHTS["sub_esg"]

            # Load sub-weights for consumption
            sub_spend = float(data.get("sub_spend", DEFAULT_WEIGHTS["sub_spend"]))
            sub_daytime = float(data.get("sub_daytime", DEFAULT_WEIGHTS["sub_daytime"]))
            sub_season = float(data.get("sub_season", DEFAULT_WEIGHTS["sub_season"]))
            sub_loads = float(data.get("sub_loads", DEFAULT_WEIGHTS["sub_loads"]))
            cons_total = sub_spend + sub_daytime + sub_season + sub_loads
            if cons_total > 0:
                weights["sub_spend"] = sub_spend / cons_total
                weights["sub_daytime"] = sub_daytime / cons_total
                weights["sub_season"] = sub_season / cons_total
                weights["sub_loads"] = sub_loads / cons_total
            else:
                weights["sub_spend"] = DEFAULT_WEIGHTS["sub_spend"]
                weights["sub_daytime"] = DEFAULT_WEIGHTS["sub_daytime"]
                weights["sub_season"] = DEFAULT_WEIGHTS["sub_season"]
                weights["sub_loads"] = DEFAULT_WEIGHTS["sub_loads"]

            return weights
        except Exception:
            pass

    return DEFAULT_WEIGHTS.copy()


def _persist_weights(weights):
    WEIGHTS_FILE.write_text(json.dumps(weights, indent=2), encoding="utf-8")


# -------------------------------------------------------
# QUESTIONS FILE MANAGEMENT
# -------------------------------------------------------
QUESTIONS_FILE = Path("questions.json")

DEFAULT_QUESTIONS = [
    {
        "id": "owner",
        "category": "structure",
        "type": "select",
        "weight_key": "sub_owner",
        "max_score": 3,
        "topic": {"en": "Owner type", "fr": "Type de propriétaire", "de": "Eigentümertyp"},
        "labels": {"en": "Who owns this site?", "fr": "Qui est propriétaire de ce site ?", "de": "Wer ist Eigentümer dieses Standorts?"},
        "help": {"en": "This helps us understand how easy it is for the owner to finance a solar project.", "fr": "Cela nous aide à comprendre la facilité de financement d'un projet solaire pour le propriétaire.", "de": "Dies hilft uns zu verstehen, wie einfach es für den Eigentümer ist, ein Solarprojekt zu finanzieren."},
        "options": [
            {"score": 3, "labels": {"en": "Public entity or large institutional owner", "fr": "Entité publique ou grand propriétaire institutionnel", "de": "Öffentliche Einrichtung oder großer institutioneller Eigentümer"}},
            {"score": 2, "labels": {"en": "Standard commercial owner", "fr": "Propriétaire commercial standard", "de": "Standard-Gewerbeinhaber"}},
            {"score": 1, "labels": {"en": "Private individual or small SME", "fr": "Particulier ou petite PME", "de": "Privatperson oder kleines KMU"}}
        ]
    },
    {
        "id": "esg",
        "category": "structure",
        "type": "select",
        "weight_key": "sub_esg",
        "max_score": 3,
        "topic": {"en": "ESG engagement", "fr": "Engagement ESG", "de": "ESG-Engagement"},
        "labels": {"en": "Is the owner visibly engaged in sustainability topics?", "fr": "Le propriétaire est-il visiblement engagé dans la durabilité ?", "de": "Ist der Eigentümer sichtbar im Nachhaltigkeitsbereich engagiert?"},
        "help": {"en": "This helps estimate how receptive they are to solar solutions.", "fr": "Cela aide à estimer leur réceptivité aux solutions solaires.", "de": "Dies hilft einzuschätzen, wie aufgeschlossen sie für Solarlösungen sind."},
        "options": [
            {"score": 3, "labels": {"en": "Yes — sustainability is clearly part of their identity", "fr": "Oui — la durabilité fait clairement partie de leur identité", "de": "Ja — Nachhaltigkeit ist eindeutig Teil ihrer Identität"}},
            {"score": 2, "labels": {"en": "Not sure — no clear signal", "fr": "Incertain — aucun signal clair", "de": "Unsicher — kein klares Signal"}},
            {"score": 1, "labels": {"en": "No — sustainability is not a visible priority", "fr": "Non — la durabilité n'est pas une priorité visible", "de": "Nein — Nachhaltigkeit ist keine sichtbare Priorität"}}
        ]
    },
    {
        "id": "daytime",
        "category": "consumption",
        "type": "slider",
        "weight_key": "sub_daytime",
        "max_score": 3,
        "min_value": 0,
        "max_value": 100,
        "default_value": 60,
        "step": 1,
        "unit": "%",
        "topic": {"en": "Daytime consumption", "fr": "Consommation diurne", "de": "Tagesverbrauch"},
        "labels": {"en": "What share of the site's electricity is used during daytime (08:00–18:00)?", "fr": "Quelle part de l'électricité du site est utilisée en journée (08h00–18h00) ?", "de": "Welcher Anteil des Stroms wird tagsüber (08:00–18:00) verbraucht?"},
        "help": {"en": "Daytime consumption increases the amount of solar electricity the site can use directly.", "fr": "La consommation diurne augmente la part d'électricité solaire utilisée directement.", "de": "Tagesverbrauch erhöht den Anteil an direkt genutztem Solarstrom."},
        "scoring_thresholds": [{"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}]
    },
    {
        "id": "spend",
        "category": "consumption",
        "type": "select",
        "weight_key": "sub_spend",
        "max_score": 4,
        "display_horizontal": True,
        "topic": {"en": "Electricity spend", "fr": "Dépenses d'électricité", "de": "Stromkosten"},
        "labels": {"en": "What is the site's annual electricity cost (CHF)?", "fr": "Quel est le coût annuel d'électricité du site (CHF) ?", "de": "Was sind die jährlichen Stromkosten des Standorts (CHF)?"},
        "help": {"en": "This indicates the financial importance of energy decisions and the potential for savings.", "fr": "Cela indique l'importance financière des décisions énergétiques et le potentiel d'économies.", "de": "Dies zeigt die finanzielle Bedeutung von Energieentscheidungen und das Einsparpotenzial."},
        "options": [
            {"score": 1, "labels": {"en": "Below 100k CHF", "fr": "Moins de 100k CHF", "de": "Unter 100k CHF"}},
            {"score": 2, "labels": {"en": "100k — 300k CHF", "fr": "100k — 300k CHF", "de": "100k — 300k CHF"}},
            {"score": 3, "labels": {"en": "300k — 800k CHF", "fr": "300k — 800k CHF", "de": "300k — 800k CHF"}},
            {"score": 4, "labels": {"en": "Above 800k CHF", "fr": "Plus de 800k CHF", "de": "Über 800k CHF"}}
        ]
    },
    {
        "id": "season",
        "category": "consumption",
        "type": "select",
        "weight_key": "sub_season",
        "max_score": 3,
        "topic": {"en": "Seasonal stability", "fr": "Stabilité saisonnière", "de": "Saisonale Stabilität"},
        "labels": {"en": "How stable is the site's electricity consumption throughout the year?", "fr": "Quelle est la stabilité de la consommation électrique tout au long de l'année ?", "de": "Wie stabil ist der Stromverbrauch des Standorts über das Jahr?"},
        "help": {"en": "High seasonality makes it harder to match solar production with consumption.", "fr": "Une forte saisonnalité rend plus difficile l'adéquation entre production solaire et consommation.", "de": "Hohe Saisonalität erschwert die Anpassung von Solarproduktion und Verbrauch."},
        "options": [
            {"score": 3, "labels": {"en": "Low seasonal variation (±10%)", "fr": "Faible variation saisonnière (±10%)", "de": "Geringe saisonale Schwankung (±10%)"}},
            {"score": 2, "labels": {"en": "Moderate variation (±10–25%)", "fr": "Variation modérée (±10–25%)", "de": "Mäßige Schwankung (±10–25%)"}},
            {"score": 1, "labels": {"en": "High variation (>25%)", "fr": "Forte variation (>25%)", "de": "Hohe Schwankung (>25%)"}}
        ]
    },
    {
        "id": "loads",
        "category": "consumption",
        "type": "select",
        "weight_key": "sub_loads",
        "max_score": 3,
        "display_horizontal": True,
        "topic": {"en": "24/7 loads", "fr": "Charges 24/7", "de": "24/7-Lasten"},
        "labels": {"en": "Does the site operate equipment that runs 24/7?", "fr": "Le site exploite-t-il des équipements fonctionnant 24h/24 7j/7 ?", "de": "Betreibt der Standort Geräte, die 24/7 laufen?"},
        "help": {"en": "Constant loads increase the share of solar energy that can be consumed directly.", "fr": "Les charges constantes augmentent la part d'énergie solaire consommée directement.", "de": "Konstante Lasten erhöhen den Anteil direkt verbrauchter Solarenergie."},
        "options": [
            {"score": 3, "labels": {"en": "Yes — important 24/7 loads", "fr": "Oui — charges importantes 24h/24 7j/7", "de": "Ja — wichtige 24/7-Lasten"}},
            {"score": 1, "labels": {"en": "No — mainly daytime or irregular loads", "fr": "Non — principalement charges diurnes ou irrégulières", "de": "Nein — hauptsächlich Tages- oder unregelmäßige Lasten"}}
        ]
    }
]


def _load_questions_from_disk():
    """Load questions from questions.json file"""
    if QUESTIONS_FILE.exists():
        try:
            with QUESTIONS_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data.get("questions", DEFAULT_QUESTIONS)
        except Exception:
            pass
    return DEFAULT_QUESTIONS.copy()


def _persist_questions(questions):
    """Save questions to questions.json file"""
    QUESTIONS_FILE.write_text(json.dumps({"questions": questions}, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_question_by_id(questions, question_id):
    """Get a question by its ID"""
    for q in questions:
        if q["id"] == question_id:
            return q
    return None


def _compute_question_score(question, answer_value):
    """Compute the score for a question based on the answer"""
    if question["type"] == "slider":
        # For slider questions, use scoring_thresholds
        thresholds = question.get("scoring_thresholds", [])
        for threshold in thresholds:
            if answer_value >= threshold["min"]:
                return threshold["score"]
        return 0
    else:
        # For select questions, find the option and return its score
        for option in question.get("options", []):
            if option["labels"].get("en", "") == answer_value or \
               option["labels"].get("fr", "") == answer_value or \
               option["labels"].get("de", "") == answer_value:
                return option["score"]
        # If exact match not found, try partial match (for backward compatibility)
        for option in question.get("options", []):
            for lang in ["en", "fr", "de"]:
                if option["labels"].get(lang, "") in answer_value or answer_value in option["labels"].get(lang, ""):
                    return option["score"]
        return 1  # Default minimum score


def init_state():
    defaults = {
        "page": "lang",
        "language": "en",   # default English
        "addresses": [],
        "current_index": 0,
        "answers": {},
        "weights": _load_weights_from_disk(),
        "questions": _load_questions_from_disk(),
        "employee_authenticated": False,
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
    "role_title": {
        "en": "Who are you?",
        "fr": "Qui êtes-vous ?",
        "de": "Wer sind Sie?",
    },
    "partner_option": {
        "en": "I am a partner of Solar21",
        "fr": "Je suis un partenaire de Solar21",
        "de": "Ich bin Partner von Solar21",
    },
    "employee_option": {
        "en": "I am an employee of Solar21",
        "fr": "Je suis employé(e) de Solar21",
        "de": "Ich bin Mitarbeiter*in von Solar21",
    },
    "employee_password": {
        "en": "Employee password",
        "fr": "Mot de passe employé",
        "de": "Mitarbeiter-Passwort",
    },
    "employee_password_error": {
        "en": "Incorrect password. Please try again.",
        "fr": "Mot de passe incorrect. Veuillez réessayer.",
        "de": "Falsches Passwort. Bitte erneut versuchen.",
    },
    "weights_title": {
        "en": "Adjust calculation weights",
        "fr": "Ajuster les pondérations du calcul",
        "de": "Berechnungsgewichte anpassen",
    },
    "weights_subtext": {
        "en": "These weights apply to everyone using this shared app once saved.",
        "fr": "Ces pondérations s'appliquent à tous ceux qui utilisent cette application partagée une fois sauvegardées.",
        "de": "Diese Gewichte gelten nach dem Speichern für alle, die diese gemeinsame App nutzen.",
    },
    "weights_pull_hint": {
        "en": "If colleagues already downloaded a local copy, they must pull/download the updated app from the same location again to receive these changes.",
        "fr": "Si des collègues ont déjà téléchargé une copie locale, ils doivent récupérer/télécharger à nouveau l'application mise à jour depuis le même emplacement pour recevoir ces changements.",
        "de": "Haben Kolleginnen oder Kollegen bereits eine lokale Kopie heruntergeladen, müssen sie die aktualisierte App erneut vom gleichen Ort beziehen, um diese Änderungen zu erhalten.",
    },
    "structure_weight": {
        "en": "Structure weight (roof + ownership + ESG)",
        "fr": "Poids de la structure (toit + propriétaire + ESG)",
        "de": "Strukturgewicht (Dach + Eigentümer + ESG)",
    },
    "consumption_weight": {
        "en": "Consumption weight (spend + load profile)",
        "fr": "Poids de la consommation (dépenses + profil de charge)",
        "de": "Verbrauchsgewicht (Kosten + Lastprofil)",
    },
    "save_weights": {
        "en": "Save weights for all users",
        "fr": "Enregistrer les pondérations pour tous",
        "de": "Gewichte für alle speichern",
    },
    "weights_saved": {
        "en": "Weights saved for all users.",
        "fr": "Pondérations enregistrées pour tous les utilisateurs.",
        "de": "Gewichte für alle Nutzer gespeichert.",
    },
    "main_weights_section": {
        "en": "Main Category Weights",
        "fr": "Pondérations des catégories principales",
        "de": "Hauptkategoriegewichte",
    },
    "structure_subweights_section": {
        "en": "Structure Sub-weights",
        "fr": "Sous-pondérations de la structure",
        "de": "Struktur-Untergewichte",
    },
    "consumption_subweights_section": {
        "en": "Consumption Sub-weights",
        "fr": "Sous-pondérations de la consommation",
        "de": "Verbrauchs-Untergewichte",
    },
    "sub_roof_weight": {
        "en": "Roof size",
        "fr": "Taille du toit",
        "de": "Dachgröße",
    },
    "sub_owner_weight": {
        "en": "Owner type",
        "fr": "Type de propriétaire",
        "de": "Eigentümertyp",
    },
    "sub_esg_weight": {
        "en": "ESG engagement",
        "fr": "Engagement ESG",
        "de": "ESG-Engagement",
    },
    "sub_spend_weight": {
        "en": "Electricity spend",
        "fr": "Dépenses d'électricité",
        "de": "Stromkosten",
    },
    "sub_daytime_weight": {
        "en": "Daytime consumption",
        "fr": "Consommation diurne",
        "de": "Tagesverbrauch",
    },
    "sub_season_weight": {
        "en": "Seasonal stability",
        "fr": "Stabilité saisonnière",
        "de": "Saisonale Stabilität",
    },
    "sub_loads_weight": {
        "en": "24/7 loads",
        "fr": "Charges 24/7",
        "de": "24/7-Lasten",
    },
    "fine_tune_hint": {
        "en": "Fine-tune individual factors within each category",
        "fr": "Ajustez finement les facteurs individuels de chaque catégorie",
        "de": "Feinabstimmung der einzelnen Faktoren innerhalb jeder Kategorie",
    },
    "proceed": {
        "en": "Proceed →",
        "fr": "Continuer →",
        "de": "Weiter →",
    },
    "add_site": {"en": "+ Add another address", "fr": "+ Ajouter une adresse", "de": "+ Eine Adresse hinzufügen"},
    "remove_site": {"en": "🗑️ Remove", "fr": "🗑️ Supprimer", "de": "🗑️ Entfernen"},
    "address_title": {
        "en": "Project Sites — Addresses",
        "fr": "Sites du projet — Adresses",
        "de": "Projektstandorte — Adressen"
    },
    "roof_data_local_hint": {
        "en": "Automatic roof sizing only works when you run the app locally with Chrome/Chromedriver installed. If you're using the hosted web version, please fill the rooftop values manually below.",
        "fr": "Le dimensionnement automatique du toit fonctionne uniquement si vous exécutez l'application en local avec Chrome/Chromedriver installé. Si vous utilisez la version web hébergée, veuillez saisir manuellement les valeurs du toit ci-dessous.",
        "de": "Die automatische Dachgrößen-Berechnung funktioniert nur, wenn Sie die App lokal mit installiertem Chrome/Chromedriver ausführen. Wenn Sie die gehostete Webversion nutzen, tragen Sie bitte die Dachwerte unten manuell ein.",
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
    "manual_roof_prompt": {
        "en": "If rooftop data cannot be fetched automatically, enter it manually:",
        "fr": "Si les données du toit ne peuvent pas être récupérées automatiquement, saisissez-les manuellement :",
        "de": "Falls die Dachdaten nicht automatisch abgerufen werden können, geben Sie sie bitte manuell ein:",
    },
    "manual_roof_hint": {
        "en": "Enter rooftop values manually. You can find these values on [sonnendach.ch](https://www.sonnendach.ch)",
        "fr": "Saisissez les valeurs du toit manuellement. Vous pouvez trouver ces valeurs sur [sonnendach.ch](https://www.sonnendach.ch)",
        "de": "Geben Sie die Dachwerte manuell ein. Sie finden diese Werte auf [sonnendach.ch](https://www.sonnendach.ch)",
    },
    "roof_area_input": {
        "en": "Rooftop area (m²)",
        "fr": "Surface du toit (m²)",
        "de": "Dachfläche (m²)",
    },
    "roof_pitch_input": {
        "en": "Roof pitch (°)",
        "fr": "Inclinaison du toit (°)",
        "de": "Dachneigung (°)",
    },
    "roof_orientation_input": {
        "en": "Roof orientation (°)",
        "fr": "Orientation du toit (°)",
        "de": "Dachausrichtung (°)",
    },
    "manual_fill_warning": {
        "en": "Automatic lookup failed. Please fill the rooftop values manually, then click Save & continue again.",
        "fr": "La récupération automatique a échoué. Merci de renseigner manuellement les valeurs du toit, puis de cliquer à nouveau sur Enregistrer & continuer.",
        "de": "Der automatische Abruf ist fehlgeschlagen. Bitte füllen Sie die Dachwerte manuell aus und klicken Sie dann erneut auf Speichern & weiter.",
    },
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
    "structure_score_label": {
        "en": "Structure Score",
        "fr": "Score Structure",
        "de": "Strukturbewertung"
    },
    "consumption_score_label": {
        "en": "Consumption Score",
        "fr": "Score Consommation",
        "de": "Verbrauchsbewertung"
    },
    "score_breakdown": {
        "en": "Score Breakdown",
        "fr": "Détail du score",
        "de": "Score-Aufschlüsselung"
    },
    "strengths": {
        "en": "Strengths",
        "fr": "Points forts",
        "de": "Stärken"
    },
    "areas_to_watch": {
        "en": "Areas to Watch",
        "fr": "Points d'attention",
        "de": "Zu beachtende Bereiche"
    },
    "factor_analysis": {
        "en": "Factor Analysis",
        "fr": "Analyse des facteurs",
        "de": "Faktorenanalyse"
    },
    "excellent": {
        "en": "Excellent",
        "fr": "Excellent",
        "de": "Ausgezeichnet"
    },
    "good": {
        "en": "Good",
        "fr": "Bon",
        "de": "Gut"
    },
    "average": {
        "en": "Average",
        "fr": "Moyen",
        "de": "Durchschnittlich"
    },
    "below_average": {
        "en": "Below Average",
        "fr": "Sous la moyenne",
        "de": "Unterdurchschnittlich"
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
            "en": "High priority opportunity.",
            "fr": "Opportunité hautement prioritaire.",
            "de": "Hochprioritäre Gelegenheit."
        },
        "strong": {
            "en": "Promising candidate for next steps.",
            "fr": "Candidat prometteur pour les prochaines étapes.",
            "de": "Vielversprechender Kandidat für nächste Schritte."
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
    # Question management UI texts
    "question_management_title": {
        "en": "Question Management",
        "fr": "Gestion des questions",
        "de": "Fragenverwaltung"
    },
    "question_management_desc": {
        "en": "Add, edit, or remove evaluation questions. Changes apply to all users.",
        "fr": "Ajouter, modifier ou supprimer des questions d'évaluation. Les modifications s'appliquent à tous les utilisateurs.",
        "de": "Bewertungsfragen hinzufügen, bearbeiten oder entfernen. Änderungen gelten für alle Benutzer."
    },
    "current_questions": {
        "en": "Current Questions",
        "fr": "Questions actuelles",
        "de": "Aktuelle Fragen"
    },
    "add_new_question": {
        "en": "Add New Question",
        "fr": "Ajouter une nouvelle question",
        "de": "Neue Frage hinzufügen"
    },
    "question_id": {
        "en": "Question ID (unique, lowercase, no spaces)",
        "fr": "ID de la question (unique, minuscules, sans espaces)",
        "de": "Frage-ID (eindeutig, Kleinbuchstaben, keine Leerzeichen)"
    },
    "question_text_en": {
        "en": "Question text (English)",
        "fr": "Texte de la question (Anglais)",
        "de": "Fragetext (Englisch)"
    },
    "question_text_fr": {
        "en": "Question text (French)",
        "fr": "Texte de la question (Français)",
        "de": "Fragetext (Französisch)"
    },
    "question_text_de": {
        "en": "Question text (German)",
        "fr": "Texte de la question (Allemand)",
        "de": "Fragetext (Deutsch)"
    },
    "help_text_en": {
        "en": "Help text (English)",
        "fr": "Texte d'aide (Anglais)",
        "de": "Hilfetext (Englisch)"
    },
    "help_text_fr": {
        "en": "Help text (French)",
        "fr": "Texte d'aide (Français)",
        "de": "Hilfetext (Französisch)"
    },
    "help_text_de": {
        "en": "Help text (German)",
        "fr": "Texte d'aide (Allemand)",
        "de": "Hilfetext (Deutsch)"
    },
    "question_category": {
        "en": "Category",
        "fr": "Catégorie",
        "de": "Kategorie"
    },
    "category_structure": {
        "en": "Structure (roof, ownership, ESG)",
        "fr": "Structure (toit, propriétaire, ESG)",
        "de": "Struktur (Dach, Eigentümer, ESG)"
    },
    "category_consumption": {
        "en": "Consumption (spend, load profile)",
        "fr": "Consommation (dépenses, profil de charge)",
        "de": "Verbrauch (Kosten, Lastprofil)"
    },
    "question_type": {
        "en": "Answer type",
        "fr": "Type de réponse",
        "de": "Antworttyp"
    },
    "type_select": {
        "en": "Multiple choice",
        "fr": "Choix multiple",
        "de": "Multiple Choice"
    },
    "type_slider": {
        "en": "Percentage slider",
        "fr": "Curseur de pourcentage",
        "de": "Prozentschieberegler"
    },
    "max_score": {
        "en": "Maximum score",
        "fr": "Score maximum",
        "de": "Maximale Punktzahl"
    },
    "initial_weight": {
        "en": "Initial weight (%)",
        "fr": "Pondération initiale (%)",
        "de": "Anfangsgewichtung (%)"
    },
    "options_section": {
        "en": "Answer Options",
        "fr": "Options de réponse",
        "de": "Antwortoptionen"
    },
    "option_text_en": {
        "en": "Option text (English)",
        "fr": "Texte de l'option (Anglais)",
        "de": "Optionstext (Englisch)"
    },
    "option_text_fr": {
        "en": "Option text (French)",
        "fr": "Texte de l'option (Français)",
        "de": "Optionstext (Französisch)"
    },
    "option_text_de": {
        "en": "Option text (German)",
        "fr": "Texte de l'option (Allemand)",
        "de": "Optionstext (Deutsch)"
    },
    "option_score": {
        "en": "Score for this option",
        "fr": "Score pour cette option",
        "de": "Punktzahl für diese Option"
    },
    "add_option": {
        "en": "+ Add option",
        "fr": "+ Ajouter une option",
        "de": "+ Option hinzufügen"
    },
    "remove_option": {
        "en": "Remove",
        "fr": "Supprimer",
        "de": "Entfernen"
    },
    "save_question": {
        "en": "Save Question",
        "fr": "Enregistrer la question",
        "de": "Frage speichern"
    },
    "question_saved": {
        "en": "Question saved successfully!",
        "fr": "Question enregistrée avec succès !",
        "de": "Frage erfolgreich gespeichert!"
    },
    "delete_question": {
        "en": "Delete",
        "fr": "Supprimer",
        "de": "Löschen"
    },
    "edit_question": {
        "en": "Edit",
        "fr": "Modifier",
        "de": "Bearbeiten"
    },
    "question_deleted": {
        "en": "Question deleted.",
        "fr": "Question supprimée.",
        "de": "Frage gelöscht."
    },
    "confirm_delete": {
        "en": "Are you sure you want to delete this question?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette question ?",
        "de": "Sind Sie sicher, dass Sie diese Frage löschen möchten?"
    },
    "cancel": {
        "en": "Cancel",
        "fr": "Annuler",
        "de": "Abbrechen"
    },
    "slider_settings": {
        "en": "Slider Settings",
        "fr": "Paramètres du curseur",
        "de": "Schieberegler-Einstellungen"
    },
    "min_value": {
        "en": "Minimum value",
        "fr": "Valeur minimale",
        "de": "Minimalwert"
    },
    "max_value_slider": {
        "en": "Maximum value",
        "fr": "Valeur maximale",
        "de": "Maximalwert"
    },
    "default_value": {
        "en": "Default value",
        "fr": "Valeur par défaut",
        "de": "Standardwert"
    },
    "scoring_thresholds": {
        "en": "Scoring Thresholds",
        "fr": "Seuils de notation",
        "de": "Bewertungsschwellen"
    },
    "threshold_min": {
        "en": "If value >=",
        "fr": "Si valeur >=",
        "de": "Wenn Wert >="
    },
    "threshold_score": {
        "en": "Score",
        "fr": "Score",
        "de": "Punktzahl"
    },
    "add_threshold": {
        "en": "+ Add threshold",
        "fr": "+ Ajouter un seuil",
        "de": "+ Schwelle hinzufügen"
    },
    "question_id_exists": {
        "en": "A question with this ID already exists.",
        "fr": "Une question avec cet ID existe déjà.",
        "de": "Eine Frage mit dieser ID existiert bereits."
    },
    "question_id_required": {
        "en": "Question ID is required.",
        "fr": "L'ID de la question est requis.",
        "de": "Frage-ID ist erforderlich."
    },
    "question_text_required": {
        "en": "Question text (English) is required.",
        "fr": "Le texte de la question (Anglais) est requis.",
        "de": "Fragetext (Englisch) ist erforderlich."
    },
    "at_least_one_option": {
        "en": "At least one option is required.",
        "fr": "Au moins une option est requise.",
        "de": "Mindestens eine Option ist erforderlich."
    },
    "display_horizontal": {
        "en": "Display options horizontally",
        "fr": "Afficher les options horizontalement",
        "de": "Optionen horizontal anzeigen"
    },
    # New panel structure texts
    "roof_size_note": {
        "en": "📌 Roof size is a fixed input that cannot be edited or removed. Only its weight can be adjusted.",
        "fr": "📌 La taille du toit est une entrée fixe qui ne peut pas être modifiée ou supprimée. Seul son poids peut être ajusté.",
        "de": "📌 Die Dachgröße ist eine feste Eingabe, die nicht bearbeitet oder entfernt werden kann. Nur ihr Gewicht kann angepasst werden."
    },
    "score_formula_title": {
        "en": "Score Calculation Formula",
        "fr": "Formule de calcul du score",
        "de": "Formel zur Punkteberechnung"
    },
    "structure_questions_panel": {
        "en": "Structure Questions Weights",
        "fr": "Poids des questions de structure",
        "de": "Gewichte der Strukturfragen"
    },
    "structure_questions_desc": {
        "en": "Adjust the relative importance of structure-related questions. Weights will be normalized to sum to 100%.",
        "fr": "Ajustez l'importance relative des questions liées à la structure. Les poids seront normalisés pour totaliser 100%.",
        "de": "Passen Sie die relative Bedeutung der strukturbezogenen Fragen an. Die Gewichte werden auf 100% normiert."
    },
    "consumption_questions_panel": {
        "en": "Consumption Questions Weights",
        "fr": "Poids des questions de consommation",
        "de": "Gewichte der Verbrauchsfragen"
    },
    "consumption_questions_desc": {
        "en": "Adjust the relative importance of consumption-related questions. Weights will be normalized to sum to 100%.",
        "fr": "Ajustez l'importance relative des questions liées à la consommation. Les poids seront normalisés pour totaliser 100%.",
        "de": "Passen Sie die relative Bedeutung der verbrauchsbezogenen Fragen an. Die Gewichte werden auf 100% normiert."
    },
    "roof_size_topic": {
        "en": "Roof size",
        "fr": "Taille du toit",
        "de": "Dachgröße"
    },
    "question_topic": {
        "en": "Question topic (short label)",
        "fr": "Sujet de la question (étiquette courte)",
        "de": "Fragenthema (Kurzbezeichnung)"
    },
    "question_topic_en": {
        "en": "Topic (English)",
        "fr": "Sujet (Anglais)",
        "de": "Thema (Englisch)"
    },
    "question_topic_fr": {
        "en": "Topic (French)",
        "fr": "Sujet (Français)",
        "de": "Thema (Französisch)"
    },
    "question_topic_de": {
        "en": "Topic (German)",
        "fr": "Sujet (Allemand)",
        "de": "Thema (Deutsch)"
    },
    "no_questions_in_category": {
        "en": "No questions in this category yet.",
        "fr": "Pas encore de questions dans cette catégorie.",
        "de": "Noch keine Fragen in dieser Kategorie."
    },
    "weights_saved_auto": {
        "en": "Weights updated.",
        "fr": "Poids mis à jour.",
        "de": "Gewichte aktualisiert."
    },
}

# All question options, defined once to avoid recreating per render
QUESTION_OPTIONS = {
    "owner": {
        "en": [
            "Public entity or large institutional owner — Hospitals, municipalities, cantonal buildings, universities, major corporates. Typically low cost of capital and stable approval processes.",
            "Standard commercial owner — Regular private companies, logistics firms, retail centers, property companies.",
            "Private individual or small SME — Smaller budgets, higher financing constraints, usually slower decision cycles.",
        ],
        "fr": [
            "Entité publique ou grand propriétaire institutionnel — Hôpitaux, municipalités, bâtiments cantonaux, universités, grandes entreprises. Généralement faible coût du capital et processus d'approbation stables.",
            "Propriétaire commercial standard — Entreprises privées régulières, entreprises de logistique, centres commerciaux, sociétés immobilières.",
            "Particulier ou petite PME — Budgets plus petits, contraintes de financement plus élevées, cycles de décision généralement plus lents.",
        ],
        "de": [
            "Öffentliche Einrichtung oder großer institutioneller Eigentümer — Krankenhäuser, Gemeinden, Kantonsgebäude, Universitäten, große Unternehmen. Typischerweise niedrige Kapitalkosten und stabile Genehmigungsverfahren.",
            "Standard-Gewerbeinhaber — Reguläre Privatunternehmen, Logistikunternehmen, Einkaufszentren, Immobiliengesellschaften.",
            "Privatperson oder kleines KMU — Kleinere Budgets, höhere Finanzierungsbeschränkungen, in der Regel langsamere Entscheidungszyklen.",
        ],
    },
    "esg": {
        "en": [
            "Yes — sustainability is clearly part of their identity (Website, annual reports, labels, certifications, public commitments)",
            "Not sure — no clear signal (No obvious information available)",
            "No — sustainability is not a visible priority (No ESG communication, purely cost-driven decision-making)",
        ],
        "fr": [
            "Oui — la durabilité fait clairement partie de leur identité (Site web, rapports annuels, labels, certifications, engagements publics)",
            "Incertain — aucun signal clair (Aucune information évidente disponible)",
            "Non — la durabilité n'est pas une priorité visible (Aucune communication ESG, décisions purement basées sur les coûts)",
        ],
        "de": [
            "Ja — Nachhaltigkeit ist eindeutig Teil ihrer Identität (Website, Jahresberichte, Labels, Zertifizierungen, öffentliche Verpflichtungen)",
            "Unsicher — kein klares Signal (Keine offensichtlichen Informationen verfügbar)",
            "Nein — Nachhaltigkeit ist keine sichtbare Priorität (Keine ESG-Kommunikation, rein kostenorientierte Entscheidungsfindung)",
        ],
    },
    "spend": {
        "en": ["Below 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Above 800k CHF"],
        "fr": ["Moins de 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Plus de 800k CHF"],
        "de": ["Unter 100k CHF", "100k — 300k CHF", "300k — 800k CHF", "Über 800k CHF"],
    },
    "season": {
        "en": [
            "Low seasonal variation (±10%) — Consumption stays stable across the year",
            "Moderate variation (±10–25%) — Some seasonal differences (e.g., cooling or heating loads)",
            "High variation (>25%) — Strong seasonality, big differences between summer and winter",
        ],
        "fr": [
            "Faible variation saisonnière (±10%) — La consommation reste stable tout au long de l'année",
            "Variation modérée (±10–25%) — Quelques différences saisonnières (par ex. charges de refroidissement ou de chauffage)",
            "Forte variation (>25%) — Forte saisonnalité, grandes différences entre été et hiver",
        ],
        "de": [
            "Geringe saisonale Schwankung (±10%) — Verbrauch bleibt über das Jahr stabil",
            "Mäßige Schwankung (±10–25%) — Einige saisonale Unterschiede (z.B. Kühl- oder Heizlasten)",
            "Hohe Schwankung (>25%) — Starke Saisonalität, große Unterschiede zwischen Sommer und Winter",
        ],
    },
    "loads": {
        "en": [
            "Yes — important 24/7 loads (Cold storage, server rooms, industrial baseload, data centers)",
            "No — mainly daytime or irregular loads",
        ],
        "fr": [
            "Oui — charges importantes 24h/24 7j/7 (Stockage frigorifique, salles de serveurs, charge de base industrielle, centres de données)",
            "Non — principalement charges diurnes ou irrégulières",
        ],
        "de": [
            "Ja — wichtige 24/7-Lasten (Kühlräume, Serverräume, industrielle Grundlast, Rechenzentren)",
            "Nein — hauptsächlich Tages- oder unregelmäßige Lasten",
        ],
    },
}

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------

def compute_roof_score(area):
    """Calculate roof score based on usable area in m²
    > 1000 m² = 3
    500–1000 m² = 2
    < 500 m² = 1
    Missing or invalid data = 0
    """
    if area is None:
        return 0
    # Be robust if Sonnendach returns a string
    try:
        area_val = float(area)
    except (TypeError, ValueError):
        return 0

    if area_val <= 0:
        return 0
    if area_val > 1000:
        return 3
    elif area_val >= 500:
        return 2
    else:
        return 1

def compute_final_score(answers, roof_score):
    """Compute the final Solar21 site attractiveness score using dynamic questions and weights"""

    # Get questions and weights from session state
    questions = st.session_state.get("questions", _load_questions_from_disk())
    weights = st.session_state.get("weights", DEFAULT_WEIGHTS)

    # Main category weights
    structure_weight = weights.get("structure", DEFAULT_WEIGHTS["structure"])
    consumption_weight = weights.get("consumption", DEFAULT_WEIGHTS["consumption"])

    # Normalize main weights
    total_weight = structure_weight + consumption_weight
    if total_weight > 0:
        structure_weight /= total_weight
        consumption_weight /= total_weight
    else:
        structure_weight = 0.5
        consumption_weight = 0.5

    # Compute scores for each category
    structure_scores = []
    consumption_scores = []

    # Always include roof in structure (it's not a question but a measurement)
    sub_roof = weights.get("sub_roof", DEFAULT_WEIGHTS.get("sub_roof", 0.4))
    roof_norm = roof_score / 3 if roof_score > 0 else 0
    structure_scores.append((roof_norm, sub_roof))

    # Process each question
    for question in questions:
        q_id = question["id"]
        weight_key = question.get("weight_key", f"sub_{q_id}")
        max_score = question.get("max_score", 3)
        category = question.get("category", "consumption")

        # Get the answer
        answer_value = answers.get(q_id)
        if answer_value is None:
            continue

        # Compute score based on question type
        score = _compute_question_score(question, answer_value)
        normalized = score / max_score if max_score > 0 else 0

        # Get the weight for this question
        sub_weight = weights.get(weight_key, 0.2)

        if category == "structure":
            structure_scores.append((normalized, sub_weight))
        else:
            consumption_scores.append((normalized, sub_weight))

    # Normalize sub-weights within each category and compute weighted sum
    def compute_category_score(scores):
        if not scores:
            return 0
        total_sub_weight = sum(w for _, w in scores)
        if total_sub_weight == 0:
            return 0
        return sum(score * (weight / total_sub_weight) for score, weight in scores)

    A_norm = compute_category_score(structure_scores)
    B_norm = compute_category_score(consumption_scores)

    # Final weighted score
    final_score = structure_weight * A_norm + consumption_weight * B_norm

    # Convert to 0-100 scale
    final_score_100 = final_score * 100

    return round(final_score_100, 1)


def compute_detailed_scores(answers, roof_score):
    """Compute detailed breakdown of all scores for results display using dynamic questions"""

    # Get questions and weights from session state
    questions = st.session_state.get("questions", _load_questions_from_disk())
    weights = st.session_state.get("weights", DEFAULT_WEIGHTS)

    structure_weight = weights.get("structure", DEFAULT_WEIGHTS["structure"])
    consumption_weight = weights.get("consumption", DEFAULT_WEIGHTS["consumption"])

    # Build detailed scores dict
    detailed = {}
    structure_scores = []
    consumption_scores = []

    # Roof is always included
    sub_roof = weights.get("sub_roof", DEFAULT_WEIGHTS.get("sub_roof", 0.4))
    roof_norm = roof_score / 3 if roof_score > 0 else 0
    detailed["roof"] = {
        "score": roof_score,
        "max": 3,
        "normalized": roof_norm * 100,
        "weight": sub_roof
    }
    structure_scores.append((roof_norm, sub_roof))

    # Process each question
    for question in questions:
        q_id = question["id"]
        weight_key = question.get("weight_key", f"sub_{q_id}")
        max_score = question.get("max_score", 3)
        category = question.get("category", "consumption")

        # Get the answer
        answer_value = answers.get(q_id)
        if answer_value is None:
            continue

        # Compute score
        score = _compute_question_score(question, answer_value)
        normalized = score / max_score if max_score > 0 else 0
        sub_weight = weights.get(weight_key, 0.2)

        detailed[q_id] = {
            "score": score,
            "max": max_score,
            "normalized": normalized * 100,
            "weight": sub_weight
        }

        if category == "structure":
            structure_scores.append((normalized, sub_weight))
        else:
            consumption_scores.append((normalized, sub_weight))

    # Compute category totals
    def compute_category_score(scores):
        if not scores:
            return 0
        total_sub_weight = sum(w for _, w in scores)
        if total_sub_weight == 0:
            return 0
        return sum(score * (weight / total_sub_weight) for score, weight in scores)

    A_norm = compute_category_score(structure_scores)
    B_norm = compute_category_score(consumption_scores)

    detailed["structure_total"] = A_norm * 100
    detailed["consumption_total"] = B_norm * 100
    detailed["structure_weight"] = structure_weight
    detailed["consumption_weight"] = consumption_weight

    return detailed


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
    if st.button(TEXT["restart"][st.session_state["language"]], type="primary"):
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
                goto("role")
                st.rerun()

# -------------------------------------------------------
# PAGE 2 — ROLE SELECTION
# -------------------------------------------------------

def page_role_selection():
    L = st.session_state["language"]

    # Centered title with subtitle
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='margin-bottom: 0.5rem;'>☀️ {TEXT["role_title"][L]}</h1>
        <p style='color: #666; font-size: 1.1rem;'>{"Select your role to continue" if L == "en" else "Sélectionnez votre rôle pour continuer" if L == "fr" else "Wählen Sie Ihre Rolle, um fortzufahren"}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize role selection state if not exists
    if "selected_role" not in st.session_state:
        st.session_state["selected_role"] = "employee" if st.session_state.get("employee_authenticated") else None

    # Two-column card layout
    col1, col2 = st.columns(2, gap="large")

    with col1:
        # Partner card
        partner_selected = st.session_state.get("selected_role") == "partner"
        border_color = "#22c55e" if partner_selected else "#e0e0e0"
        bg_color = "#f0fdf4" if partner_selected else "#fafafa"

        st.markdown(f"""
        <div style='
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            background: {bg_color};
            min-height: 200px;
            transition: all 0.2s;
        '>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🤝</div>
            <h3 style='margin-bottom: 0.5rem; color: #1f2937;'>{"Partner" if L == "en" else "Partenaire" if L == "fr" else "Partner"}</h3>
            <p style='color: #6b7280; font-size: 0.9rem;'>{"Evaluate sites for Solar21 projects" if L == "en" else "Évaluer des sites pour les projets Solar21" if L == "fr" else "Standorte für Solar21-Projekte bewerten"}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(TEXT["partner_option"][L], key="btn_partner", use_container_width=True,
                     type="primary" if partner_selected else "secondary"):
            st.session_state["selected_role"] = "partner"
            st.session_state["employee_authenticated"] = False
            st.rerun()

    with col2:
        # Employee card
        employee_selected = st.session_state.get("selected_role") == "employee"
        border_color = "#22c55e" if employee_selected else "#e0e0e0"
        bg_color = "#f0fdf4" if employee_selected else "#fafafa"

        st.markdown(f"""
        <div style='
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            background: {bg_color};
            min-height: 200px;
            transition: all 0.2s;
        '>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>⚙️</div>
            <h3 style='margin-bottom: 0.5rem; color: #1f2937;'>{"Employee" if L == "en" else "Employé" if L == "fr" else "Mitarbeiter"}</h3>
            <p style='color: #6b7280; font-size: 0.9rem;'>{"Configure weights and manage questions" if L == "en" else "Configurer les poids et gérer les questions" if L == "fr" else "Gewichte konfigurieren und Fragen verwalten"}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(TEXT["employee_option"][L], key="btn_employee", use_container_width=True,
                     type="primary" if employee_selected else "secondary"):
            st.session_state["selected_role"] = "employee"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Partner flow - show proceed button
    if st.session_state.get("selected_role") == "partner":
        st.markdown("---")
        if st.button(TEXT["proceed"][L], type="primary", use_container_width=True):
            goto("address_entry")
            st.rerun()
        return

    # Employee flow - show password and settings
    if st.session_state.get("selected_role") == "employee":
        st.markdown("---")

        if not st.session_state.get("employee_authenticated"):
            st.markdown(f"🔐 **{TEXT['employee_password'][L]}**")
            pwd = st.text_input(
                TEXT["employee_password"][L],
                type="password",
                key="employee_password_input",
                label_visibility="collapsed",
            )

            if pwd:
                if pwd == EMPLOYEE_PASSWORD:
                    st.session_state["employee_authenticated"] = True
                    st.rerun()
                else:
                    st.error(TEXT["employee_password_error"][L])

    if st.session_state.get("employee_authenticated"):
        st.success(TEXT["weights_subtext"][L])

        st.markdown(f"## {TEXT['weights_title'][L]}")
        st.caption(TEXT["fine_tune_hint"][L])

        # ─────────────────────────────────────────────────────────
        # DYNAMIC SCORE FORMULA
        # ─────────────────────────────────────────────────────────
        questions_for_formula = st.session_state.get("questions", _load_questions_from_disk())
        weights_for_formula = st.session_state.get("weights", DEFAULT_WEIGHTS)

        struct_qs = [q for q in questions_for_formula if q.get("category") == "structure"]
        cons_qs = [q for q in questions_for_formula if q.get("category") == "consumption"]

        # Get main weights
        struct_w = weights_for_formula.get("structure", 0.4)
        cons_w = weights_for_formula.get("consumption", 0.6)

        # Build structure part of formula
        struct_parts = []
        roof_w = weights_for_formula.get("sub_roof", 0.4)
        struct_parts.append(f"{roof_w:.0%} × Roof")
        for q in struct_qs:
            weight_key = q.get("weight_key", f"sub_{q['id']}")
            w = weights_for_formula.get(weight_key, 0.2)
            topic = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q["id"]))
            struct_parts.append(f"{w:.0%} × {topic}")

        # Build consumption part of formula
        cons_parts = []
        for q in cons_qs:
            weight_key = q.get("weight_key", f"sub_{q['id']}")
            w = weights_for_formula.get(weight_key, 0.2)
            topic = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q["id"]))
            cons_parts.append(f"{w:.0%} × {topic}")

        with st.expander(f"📐 {TEXT['score_formula_title'][L]}", expanded=False):
            st.markdown("**Final Score =**")
            st.markdown(f"""
            `{struct_w:.0%}` × **Structure** × ({' + '.join(struct_parts)})

            `+`

            `{cons_w:.0%}` × **Consumption** × ({' + '.join(cons_parts) if cons_parts else 'No questions'})
            """)
            st.caption("Note: Sub-weights within each category are normalized to sum to 100%")

        st.markdown("---")

        # ─────────────────────────────────────────────────────────
        # MAIN CATEGORY WEIGHTS
        # ─────────────────────────────────────────────────────────
        st.markdown(f"### {TEXT['main_weights_section'][L]}")

        col1, col2 = st.columns(2)
        with col1:
            structure_default = int(round(st.session_state["weights"]["structure"] * 100))
            structure_pct = st.slider(
                TEXT["structure_weight"][L],
                0, 100, structure_default,
                step=5, format="%d%%", key="main_structure"
            )
        with col2:
            consumption_pct = 100 - structure_pct
            st.markdown(f"**{TEXT['consumption_weight'][L]}**")
            st.markdown(f"<p style='font-size: 2rem; margin: 0;'>{consumption_pct}%</p>", unsafe_allow_html=True)

        st.markdown("---")

        # Get questions for dynamic weight panels
        questions = st.session_state.get("questions", _load_questions_from_disk())
        structure_questions = [q for q in questions if q.get("category") == "structure"]
        consumption_questions = [q for q in questions if q.get("category") == "consumption"]

        # Dictionary to store all weight slider values
        weight_values = {}

        # ─────────────────────────────────────────────────────────
        # PANEL 1: STRUCTURE QUESTIONS WEIGHTS (includes Roof Size)
        # ─────────────────────────────────────────────────────────
        with st.expander(f"⚙️ {TEXT['structure_questions_panel'][L]}", expanded=False):
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <small>{TEXT['structure_questions_desc'][L]}</small>
            </div>
            """, unsafe_allow_html=True)

            # Roof size (fixed input - always first)
            sub_roof_default = int(round(st.session_state["weights"].get("sub_roof", DEFAULT_WEIGHTS["sub_roof"]) * 100))
            weight_values["sub_roof"] = st.slider(
                TEXT["roof_size_topic"][L],
                0, 100, sub_roof_default,
                step=5, format="%d%%", key="sub_roof"
            )
            st.info(TEXT["roof_size_note"][L])

            st.markdown("---")

            # Other structure questions
            if structure_questions:
                num_cols = min(len(structure_questions), 3)
                cols = st.columns(num_cols)
                for i, q in enumerate(structure_questions):
                    with cols[i % num_cols]:
                        weight_key = q.get("weight_key", f"sub_{q['id']}")
                        topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q["id"]))
                        default_val = int(round(st.session_state["weights"].get(weight_key, 0.2) * 100))
                        weight_values[weight_key] = st.slider(
                            topic_label,
                            0, 100, default_val,
                            step=5, format="%d%%", key=f"weight_{weight_key}"
                        )

            # Total includes roof + all structure questions
            struct_q_total = weight_values.get("sub_roof", 0) + sum(weight_values.get(q.get("weight_key", f"sub_{q['id']}"), 0) for q in structure_questions)
            if struct_q_total > 0:
                st.caption(f"Total: {struct_q_total}% → normalized to 100%")
            else:
                st.warning("At least one sub-weight must be > 0")

        # ─────────────────────────────────────────────────────────
        # PANEL 2: CONSUMPTION QUESTIONS WEIGHTS
        # ─────────────────────────────────────────────────────────
        with st.expander(f"⚙️ {TEXT['consumption_questions_panel'][L]}", expanded=False):
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <small>{TEXT['consumption_questions_desc'][L]}</small>
            </div>
            """, unsafe_allow_html=True)

            if consumption_questions:
                num_cols = min(len(consumption_questions), 2)
                cols = st.columns(num_cols)
                for i, q in enumerate(consumption_questions):
                    with cols[i % num_cols]:
                        weight_key = q.get("weight_key", f"sub_{q['id']}")
                        topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q["id"]))
                        default_val = int(round(st.session_state["weights"].get(weight_key, 0.2) * 100))
                        weight_values[weight_key] = st.slider(
                            topic_label,
                            0, 100, default_val,
                            step=5, format="%d%%", key=f"weight_{weight_key}"
                        )

                cons_q_total = sum(weight_values.get(q.get("weight_key", f"sub_{q['id']}"), 0) for q in consumption_questions)
                if cons_q_total > 0:
                    st.caption(f"Total: {cons_q_total}% → normalized to 100%")
                else:
                    st.warning("At least one sub-weight must be > 0")
            else:
                st.info(TEXT["no_questions_in_category"][L])

        st.markdown("---")

        # ─────────────────────────────────────────────────────────
        # SAVE BUTTON
        # ─────────────────────────────────────────────────────────
        col_save, col_proceed = st.columns(2)
        with col_save:
            if st.button(TEXT["save_weights"][L], type="primary", use_container_width=True):
                # Calculate totals for normalization
                # Fixed inputs (roof) + structure questions
                struct_total = weight_values.get("sub_roof", 0) + sum(
                    weight_values.get(q.get("weight_key", f"sub_{q['id']}"), 0) for q in structure_questions
                )
                if struct_total == 0:
                    struct_total = 1

                # Consumption questions
                cons_total = sum(
                    weight_values.get(q.get("weight_key", f"sub_{q['id']}"), 0) for q in consumption_questions
                )
                if cons_total == 0:
                    cons_total = 1

                # Build new weights dict
                new_weights = {
                    "structure": structure_pct / 100,
                    "consumption": consumption_pct / 100,
                    "sub_roof": weight_values.get("sub_roof", 40) / struct_total,
                }

                # Add structure question weights
                for q in structure_questions:
                    weight_key = q.get("weight_key", f"sub_{q['id']}")
                    new_weights[weight_key] = weight_values.get(weight_key, 0) / struct_total

                # Add consumption question weights
                for q in consumption_questions:
                    weight_key = q.get("weight_key", f"sub_{q['id']}")
                    new_weights[weight_key] = weight_values.get(weight_key, 0) / cons_total

                st.session_state["weights"] = new_weights
                _persist_weights(new_weights)
                st.success(f"✅ {TEXT['weights_saved'][L]}")
                st.rerun()  # Refresh to update formula display

        with col_proceed:
            if st.button(TEXT["proceed"][L], use_container_width=True):
                goto("address_entry")
                st.rerun()

        # ─────────────────────────────────────────────────────────
        # QUESTION MANAGEMENT SECTION
        # ─────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown(f"## {TEXT['question_management_title'][L]}")
        st.caption(TEXT["question_management_desc"][L])

        # Initialize question editor state
        if "editing_question_id" not in st.session_state:
            st.session_state["editing_question_id"] = None
        if "show_add_question" not in st.session_state:
            st.session_state["show_add_question"] = False
        if "new_question_options" not in st.session_state:
            st.session_state["new_question_options"] = [{"en": "", "fr": "", "de": "", "score": 1}]
        if "new_question_thresholds" not in st.session_state:
            st.session_state["new_question_thresholds"] = [{"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}]

        questions = st.session_state.get("questions", _load_questions_from_disk())

        # ── CURRENT QUESTIONS LIST ──
        with st.expander(f"📋 {TEXT['current_questions'][L]} ({len(questions)})", expanded=True):
            for q_idx, question in enumerate(questions):
                q_col1, q_col2, q_col3 = st.columns([4, 1, 1])
                with q_col1:
                    category_label = TEXT["category_structure"][L] if question["category"] == "structure" else TEXT["category_consumption"][L]
                    st.markdown(f"**{q_idx + 1}. {question['labels'].get(L, question['labels'].get('en', 'Unnamed'))}**")
                    st.caption(f"{category_label} | Max score: {question.get('max_score', 3)}")
                with q_col2:
                    if st.button(TEXT["edit_question"][L], key=f"edit_q_{question['id']}", use_container_width=True):
                        st.session_state["editing_question_id"] = question["id"]
                        st.session_state["show_add_question"] = False
                        # Clear initialization flags so new question data loads
                        if "edit_options_initialized" in st.session_state:
                            del st.session_state["edit_options_initialized"]
                        if "edit_thresholds_initialized" in st.session_state:
                            del st.session_state["edit_thresholds_initialized"]
                        st.rerun()
                with q_col3:
                    if st.button(TEXT["delete_question"][L], key=f"del_q_{question['id']}", use_container_width=True):
                        # Remove the question
                        questions = [q for q in questions if q["id"] != question["id"]]
                        st.session_state["questions"] = questions
                        _persist_questions(questions)
                        # Also remove the weight key from weights if it exists
                        weights = st.session_state.get("weights", {})
                        if question.get("weight_key") in weights:
                            del weights[question["weight_key"]]
                            st.session_state["weights"] = weights
                            _persist_weights(weights)
                        st.success(TEXT["question_deleted"][L])
                        st.rerun()
                st.markdown("---")

        # ── ADD NEW QUESTION BUTTON ──
        if not st.session_state.get("show_add_question") and not st.session_state.get("editing_question_id"):
            if st.button(f"➕ {TEXT['add_new_question'][L]}", use_container_width=True):
                st.session_state["show_add_question"] = True
                st.session_state["editing_question_id"] = None
                st.session_state["new_question_options"] = [{"en": "", "fr": "", "de": "", "score": 1}]
                st.session_state["new_question_thresholds"] = [{"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}]
                st.rerun()

        # ── QUESTION EDITOR (for adding or editing) ──
        editing_question = None
        if st.session_state.get("editing_question_id"):
            editing_question = _get_question_by_id(questions, st.session_state["editing_question_id"])

        if st.session_state.get("show_add_question") or editing_question:
            with st.expander(f"✏️ {TEXT['add_new_question'][L] if not editing_question else TEXT['edit_question'][L]}", expanded=True):
                # Question ID
                default_id = editing_question["id"] if editing_question else ""
                q_id = st.text_input(
                    TEXT["question_id"][L],
                    value=default_id,
                    key="new_q_id",
                    disabled=bool(editing_question)  # Can't change ID when editing
                )

                # Question topic (short label for panels and results)
                st.markdown(f"**{TEXT['question_topic'][L]}**")
                topic_en = st.text_input(
                    TEXT["question_topic_en"][L],
                    value=editing_question.get("topic", {}).get("en", "") if editing_question else "",
                    key="new_q_topic_en"
                )
                topic_fr = st.text_input(
                    TEXT["question_topic_fr"][L],
                    value=editing_question.get("topic", {}).get("fr", "") if editing_question else "",
                    key="new_q_topic_fr"
                )
                topic_de = st.text_input(
                    TEXT["question_topic_de"][L],
                    value=editing_question.get("topic", {}).get("de", "") if editing_question else "",
                    key="new_q_topic_de"
                )

                # Question text (multilingual)
                st.markdown(f"**{TEXT['question_text_en'][L]}**")
                q_text_en = st.text_area(
                    TEXT["question_text_en"][L],
                    value=editing_question["labels"].get("en", "") if editing_question else "",
                    key="new_q_text_en",
                    label_visibility="collapsed"
                )
                q_text_fr = st.text_input(
                    TEXT["question_text_fr"][L],
                    value=editing_question["labels"].get("fr", "") if editing_question else "",
                    key="new_q_text_fr"
                )
                q_text_de = st.text_input(
                    TEXT["question_text_de"][L],
                    value=editing_question["labels"].get("de", "") if editing_question else "",
                    key="new_q_text_de"
                )

                # Help text (multilingual)
                st.markdown(f"**{TEXT['help_text_en'][L]}**")
                h_text_en = st.text_area(
                    TEXT["help_text_en"][L],
                    value=editing_question["help"].get("en", "") if editing_question else "",
                    key="new_q_help_en",
                    label_visibility="collapsed"
                )
                h_text_fr = st.text_input(
                    TEXT["help_text_fr"][L],
                    value=editing_question["help"].get("fr", "") if editing_question else "",
                    key="new_q_help_fr"
                )
                h_text_de = st.text_input(
                    TEXT["help_text_de"][L],
                    value=editing_question["help"].get("de", "") if editing_question else "",
                    key="new_q_help_de"
                )

                # Category
                cat_options = [TEXT["category_structure"][L], TEXT["category_consumption"][L]]
                default_cat_idx = 0 if (not editing_question or editing_question["category"] == "structure") else 1
                q_category = st.selectbox(
                    TEXT["question_category"][L],
                    cat_options,
                    index=default_cat_idx,
                    key="new_q_category"
                )
                category_value = "structure" if q_category == TEXT["category_structure"][L] else "consumption"

                # Question type
                type_options = [TEXT["type_select"][L], TEXT["type_slider"][L]]
                default_type_idx = 0 if (not editing_question or editing_question["type"] == "select") else 1
                q_type = st.selectbox(
                    TEXT["question_type"][L],
                    type_options,
                    index=default_type_idx,
                    key="new_q_type"
                )
                type_value = "select" if q_type == TEXT["type_select"][L] else "slider"

                # Max score
                default_max = editing_question.get("max_score", 3) if editing_question else 3
                q_max_score = st.number_input(
                    TEXT["max_score"][L],
                    min_value=1,
                    max_value=10,
                    value=default_max,
                    key="new_q_max_score"
                )

                # Display horizontal option (for select type)
                display_horizontal = False
                if type_value == "select":
                    default_horizontal = editing_question.get("display_horizontal", False) if editing_question else False
                    display_horizontal = st.checkbox(
                        TEXT["display_horizontal"][L],
                        value=default_horizontal,
                        key="new_q_horizontal"
                    )

                # Options for select type
                if type_value == "select":
                    st.markdown(f"### {TEXT['options_section'][L]}")

                    # Initialize options from editing question if available
                    if editing_question and "edit_options_initialized" not in st.session_state:
                        st.session_state["new_question_options"] = [
                            {
                                "en": opt["labels"].get("en", ""),
                                "fr": opt["labels"].get("fr", ""),
                                "de": opt["labels"].get("de", ""),
                                "score": opt.get("score", 1)
                            }
                            for opt in editing_question.get("options", [])
                        ]
                        st.session_state["edit_options_initialized"] = True

                    options_to_render = st.session_state.get("new_question_options", [{"en": "", "fr": "", "de": "", "score": 1}])

                    for opt_idx, opt in enumerate(options_to_render):
                        st.markdown(f"**Option {opt_idx + 1}**")
                        opt_col1, opt_col2 = st.columns([3, 1])
                        with opt_col1:
                            opt["en"] = st.text_input(
                                TEXT["option_text_en"][L],
                                value=opt.get("en", ""),
                                key=f"opt_{opt_idx}_en"
                            )
                            opt["fr"] = st.text_input(
                                TEXT["option_text_fr"][L],
                                value=opt.get("fr", ""),
                                key=f"opt_{opt_idx}_fr"
                            )
                            opt["de"] = st.text_input(
                                TEXT["option_text_de"][L],
                                value=opt.get("de", ""),
                                key=f"opt_{opt_idx}_de"
                            )
                        with opt_col2:
                            opt["score"] = st.number_input(
                                TEXT["option_score"][L],
                                min_value=0,
                                max_value=10,
                                value=opt.get("score", 1),
                                key=f"opt_{opt_idx}_score"
                            )
                            if len(options_to_render) > 1:
                                if st.button(TEXT["remove_option"][L], key=f"remove_opt_{opt_idx}"):
                                    options_to_render.pop(opt_idx)
                                    st.session_state["new_question_options"] = options_to_render
                                    st.rerun()

                    if st.button(TEXT["add_option"][L], key="add_option_btn"):
                        options_to_render.append({"en": "", "fr": "", "de": "", "score": 1})
                        st.session_state["new_question_options"] = options_to_render
                        st.rerun()

                # Slider settings
                if type_value == "slider":
                    st.markdown(f"### {TEXT['slider_settings'][L]}")

                    slider_col1, slider_col2, slider_col3 = st.columns(3)
                    with slider_col1:
                        slider_min = st.number_input(
                            TEXT["min_value"][L],
                            value=editing_question.get("min_value", 0) if editing_question else 0,
                            key="new_q_slider_min"
                        )
                    with slider_col2:
                        slider_max = st.number_input(
                            TEXT["max_value_slider"][L],
                            value=editing_question.get("max_value", 100) if editing_question else 100,
                            key="new_q_slider_max"
                        )
                    with slider_col3:
                        slider_default = st.number_input(
                            TEXT["default_value"][L],
                            value=editing_question.get("default_value", 50) if editing_question else 50,
                            key="new_q_slider_default"
                        )

                    st.markdown(f"### {TEXT['scoring_thresholds'][L]}")

                    # Initialize thresholds from editing question if available
                    if editing_question and "edit_thresholds_initialized" not in st.session_state:
                        st.session_state["new_question_thresholds"] = editing_question.get("scoring_thresholds", [
                            {"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}
                        ])
                        st.session_state["edit_thresholds_initialized"] = True

                    thresholds = st.session_state.get("new_question_thresholds", [])

                    for th_idx, threshold in enumerate(thresholds):
                        th_col1, th_col2, th_col3 = st.columns([2, 2, 1])
                        with th_col1:
                            threshold["min"] = st.number_input(
                                TEXT["threshold_min"][L],
                                value=threshold.get("min", 0),
                                key=f"th_{th_idx}_min"
                            )
                        with th_col2:
                            threshold["score"] = st.number_input(
                                TEXT["threshold_score"][L],
                                value=threshold.get("score", 0),
                                key=f"th_{th_idx}_score"
                            )
                        with th_col3:
                            if len(thresholds) > 1:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button(TEXT["remove_option"][L], key=f"remove_th_{th_idx}"):
                                    thresholds.pop(th_idx)
                                    st.session_state["new_question_thresholds"] = thresholds
                                    st.rerun()

                    if st.button(TEXT["add_threshold"][L], key="add_threshold_btn"):
                        thresholds.append({"min": 0, "score": 0})
                        st.session_state["new_question_thresholds"] = thresholds
                        st.rerun()

                # Save/Cancel buttons
                st.markdown("---")
                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button(TEXT["save_question"][L], type="primary", use_container_width=True):
                        # Validation
                        error = None
                        if not q_id or not q_id.strip():
                            error = TEXT["question_id_required"][L]
                        elif not q_text_en or not q_text_en.strip():
                            error = TEXT["question_text_required"][L]
                        elif not editing_question:
                            # Check if ID already exists (only for new questions)
                            existing_ids = [q["id"] for q in questions]
                            if q_id.strip().lower() in existing_ids:
                                error = TEXT["question_id_exists"][L]
                        elif type_value == "select":
                            # Check at least one option
                            valid_options = [o for o in st.session_state.get("new_question_options", []) if o.get("en", "").strip()]
                            if not valid_options:
                                error = TEXT["at_least_one_option"][L]

                        if error:
                            st.error(error)
                        else:
                            # Build question object
                            weight_key = f"sub_{q_id.strip().lower()}"
                            new_question = {
                                "id": q_id.strip().lower() if not editing_question else editing_question["id"],
                                "category": category_value,
                                "type": type_value,
                                "weight_key": weight_key if not editing_question else editing_question.get("weight_key", weight_key),
                                "max_score": q_max_score,
                                "topic": {
                                    "en": topic_en.strip() if topic_en else q_id.strip(),
                                    "fr": topic_fr.strip() if topic_fr else (topic_en.strip() if topic_en else q_id.strip()),
                                    "de": topic_de.strip() if topic_de else (topic_en.strip() if topic_en else q_id.strip())
                                },
                                "labels": {
                                    "en": q_text_en.strip(),
                                    "fr": q_text_fr.strip() if q_text_fr else q_text_en.strip(),
                                    "de": q_text_de.strip() if q_text_de else q_text_en.strip()
                                },
                                "help": {
                                    "en": h_text_en.strip() if h_text_en else "",
                                    "fr": h_text_fr.strip() if h_text_fr else h_text_en.strip() if h_text_en else "",
                                    "de": h_text_de.strip() if h_text_de else h_text_en.strip() if h_text_en else ""
                                }
                            }

                            if type_value == "select":
                                new_question["display_horizontal"] = display_horizontal
                                new_question["options"] = [
                                    {
                                        "score": opt["score"],
                                        "labels": {
                                            "en": opt["en"].strip(),
                                            "fr": opt["fr"].strip() if opt["fr"] else opt["en"].strip(),
                                            "de": opt["de"].strip() if opt["de"] else opt["en"].strip()
                                        }
                                    }
                                    for opt in st.session_state.get("new_question_options", [])
                                    if opt.get("en", "").strip()
                                ]
                            else:  # slider
                                new_question["min_value"] = int(slider_min)
                                new_question["max_value"] = int(slider_max)
                                new_question["default_value"] = int(slider_default)
                                new_question["step"] = 1
                                new_question["unit"] = "%"
                                new_question["scoring_thresholds"] = sorted(
                                    st.session_state.get("new_question_thresholds", []),
                                    key=lambda x: x["min"],
                                    reverse=True
                                )

                            # Update or add question
                            if editing_question:
                                questions = [new_question if q["id"] == editing_question["id"] else q for q in questions]
                            else:
                                questions.append(new_question)

                            # Save questions
                            st.session_state["questions"] = questions
                            _persist_questions(questions)

                            # Add default weight for new questions (if not editing)
                            if not editing_question:
                                weights = st.session_state.get("weights", _load_weights_from_disk())
                                weight_key_to_use = new_question["weight_key"]
                                if weight_key_to_use not in weights:
                                    weights[weight_key_to_use] = 0.2  # Default 20%
                                    st.session_state["weights"] = weights
                                    _persist_weights(weights)

                            # Reset state
                            st.session_state["show_add_question"] = False
                            st.session_state["editing_question_id"] = None
                            st.session_state["new_question_options"] = [{"en": "", "fr": "", "de": "", "score": 1}]
                            st.session_state["new_question_thresholds"] = [{"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}]
                            if "edit_options_initialized" in st.session_state:
                                del st.session_state["edit_options_initialized"]
                            if "edit_thresholds_initialized" in st.session_state:
                                del st.session_state["edit_thresholds_initialized"]

                            st.success(TEXT["question_saved"][L])
                            st.rerun()

                with cancel_col:
                    if st.button(TEXT["cancel"][L], use_container_width=True):
                        st.session_state["show_add_question"] = False
                        st.session_state["editing_question_id"] = None
                        st.session_state["new_question_options"] = [{"en": "", "fr": "", "de": "", "score": 1}]
                        st.session_state["new_question_thresholds"] = [{"min": 75, "score": 3}, {"min": 50, "score": 2}, {"min": 25, "score": 1}, {"min": 0, "score": 0}]
                        if "edit_options_initialized" in st.session_state:
                            del st.session_state["edit_options_initialized"]
                        if "edit_thresholds_initialized" in st.session_state:
                            del st.session_state["edit_thresholds_initialized"]
                        st.rerun()

# -------------------------------------------------------
# PAGE 3 — ENTER ADDRESSES
# -------------------------------------------------------

def page_address_entry():
    L = st.session_state["language"]

    st.title(TEXT["address_title"][L])
    st.markdown("<br>", unsafe_allow_html=True)

    col_add, col_space = st.columns([1, 3])
    with col_add:
        if st.button(TEXT["add_site"][L], type="primary"):
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
                    answers = st.session_state.get("answers", {})
                    if idx in answers:
                        del answers[idx]
                    st.session_state["answers"] = {
                        (i if i < idx else i - 1): ans
                        for i, ans in answers.items()
                        if i != idx
                    }
                    st.session_state["addresses"].pop(idx)
                    if st.session_state.get("current_index", 0) >= len(st.session_state["addresses"]):
                        st.session_state["current_index"] = max(len(st.session_state["addresses"]) - 1, 0)
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

        st.info(TEXT["manual_roof_hint"][L], icon="🏠")
        col_area, col_pitch, col_orient = st.columns(3)
        area_val = col_area.number_input(
            TEXT["roof_area_input"][L],
            min_value=0.0,
            value=float(entry["roof_area"]) if entry["roof_area"] is not None else 0.0,
            step=1.0,
            key=f"roof_area_{idx}",
        )
        pitch_val = col_pitch.number_input(
            TEXT["roof_pitch_input"][L],
            min_value=0.0,
            max_value=90.0,
            value=float(entry["roof_pitch"]) if entry["roof_pitch"] is not None else 0.0,
            step=1.0,
            key=f"roof_pitch_{idx}",
        )
        orient_val = col_orient.number_input(
            TEXT["roof_orientation_input"][L],
            min_value=0.0,
            max_value=360.0,
            value=float(entry["roof_orientation"]) if entry["roof_orientation"] is not None else 0.0,
            step=5.0,
            key=f"roof_orientation_{idx}",
        )

        entry["roof_area"] = area_val if area_val > 0 else None
        entry["roof_pitch"] = pitch_val if pitch_val > 0 else None
        entry["roof_orientation"] = orient_val if orient_val > 0 else None

        if entry["roof_area"] is not None:
            rs = compute_roof_score(entry["roof_area"])
            st.info(
                f"🏠 Rooftop area used for scoring: **{entry['roof_area']} m²** (roof score: {rs}/3)"
            )

        st.markdown("---")

    if st.button(TEXT["save_continue"][L], use_container_width=True, type="primary"):
        goto("questions")
        st.rerun()

# -------------------------------------------------------
# PAGE 4 — QUESTIONS (ONE PAGE PER ADDRESS)
# -------------------------------------------------------

def page_questions():
    L = st.session_state["language"]
    idx = st.session_state["current_index"]
    site = st.session_state["addresses"][idx]
    total_sites = len(st.session_state["addresses"])

    # ─────────────────────────────────────────────────────────
    # HEADER WITH PROGRESS
    # ─────────────────────────────────────────────────────────
    st.title(f"{TEXT['questions_title'][L]}")

    # Progress indicator
    progress = (idx + 1) / total_sites
    st.progress(progress)
    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <span style='font-size: 1.1rem; font-weight: 600;'>📍 {site['address']}</span>
            <span style='background: #00FF40; color: #000; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>
                Site {idx + 1} / {total_sites}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Roof info card (if available)
    if site.get("roof_area") is not None:
        rs = compute_roof_score(site["roof_area"])
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid #00FF40;'>
                <span style='font-size: 1.1rem;'>🏠 <strong>Roof area:</strong> {site['roof_area']} m² &nbsp;&nbsp;|&nbsp;&nbsp; <strong>Score:</strong> {rs}/3</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    prefix = f"a{idx}_"

    # ─────────────────────────────────────────────────────────
    # QUESTIONS IN STYLED CONTAINERS
    # ─────────────────────────────────────────────────────────

    # Question card style (CSS injection)
    st.markdown("""
    <style>
        .question-card {
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: box-shadow 0.2s ease;
        }
        .question-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .question-number {
            display: inline-block;
            background: #00FF40;
            color: #000;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-weight: 700;
            font-size: 0.9rem;
            margin-right: 0.75rem;
        }
        .question-title {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 0.5rem;
        }
        .question-help {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1rem;
            padding-left: 2.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── DYNAMIC QUESTIONS FROM JSON ──
    questions = st.session_state.get("questions", _load_questions_from_disk())
    answers_dict = {}

    for q_idx, question in enumerate(questions):
        q_id = question["id"]
        q_label = question["labels"].get(L, question["labels"].get("en", "Question"))
        q_help = question["help"].get(L, question["help"].get("en", ""))

        # Render question card
        st.markdown(f"""
        <div class="question-card">
            <div class="question-title"><span class="question-number">{q_idx + 1}</span>{q_label}</div>
            <div class="question-help">{q_help}</div>
        </div>
        """, unsafe_allow_html=True)

        if question["type"] == "slider":
            # Slider question
            min_val = question.get("min_value", 0)
            max_val = question.get("max_value", 100)
            default_val = question.get("default_value", 50)
            unit = question.get("unit", "%")

            col_slider, col_value = st.columns([4, 1])
            with col_slider:
                answer_value = st.slider(
                    f"{q_id}_slider",
                    min_val, max_val, default_val,
                    key=prefix + q_id,
                    label_visibility="collapsed"
                )
            with col_value:
                st.markdown(
                    f"<div style='background: #00FF40; color: #000; padding: 0.5rem 1rem; border-radius: 8px; text-align: center; font-size: 1.3rem; font-weight: 700;'>{answer_value}{unit}</div>",
                    unsafe_allow_html=True
                )
            answers_dict[q_id] = answer_value
        else:
            # Select/radio question
            options = question.get("options", [])
            option_labels = [opt["labels"].get(L, opt["labels"].get("en", "Option")) for opt in options]
            is_horizontal = question.get("display_horizontal", False)

            answer_value = st.radio(
                f"{q_id}_radio",
                option_labels,
                key=prefix + q_id,
                label_visibility="collapsed",
                horizontal=is_horizontal
            )
            answers_dict[q_id] = answer_value

    # ─────────────────────────────────────────────────────────
    # SAVE ANSWERS
    # ─────────────────────────────────────────────────────────
    # Store all answers including roof_score
    answers_dict["roof_score"] = compute_roof_score(site["roof_area"])
    st.session_state["answers"][idx] = answers_dict

    # ─────────────────────────────────────────────────────────
    # NAVIGATION BUTTONS
    # ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        if idx > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state["current_index"] -= 1
                st.rerun()

    with c3:
        button_label = TEXT["continue"][L] if idx < total_sites - 1 else "View Results →"
        if st.button(button_label, use_container_width=True, type="primary"):
            if idx < total_sites - 1:
                st.session_state["current_index"] += 1
                st.rerun()
            else:
                goto("results")
                st.rerun()

# -------------------------------------------------------
# PAGE 5 — RESULTS
# -------------------------------------------------------

def page_results():
    L = st.session_state["language"]

    # ─────────────────────────────────────────────────────────
    # RESULTS PAGE CSS
    # ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
        .score-hero {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .score-hero-value {
            font-size: 4rem !important;
            font-weight: 800 !important;
            color: #00FF40 !important;
            margin: 0 !important;
            line-height: 1 !important;
        }
        .score-hero-label {
            font-size: 1rem !important;
            color: #888 !important;
            margin-top: 0.5rem !important;
        }
        .score-hero-interpretation {
            font-size: 1.5rem !important;
            color: #fff !important;
            margin-top: 1rem !important;
            font-weight: 600 !important;
        }
        .score-hero-recommendation {
            font-size: 1rem !important;
            color: #aaa !important;
            margin-top: 0.5rem !important;
            font-style: italic !important;
        }
        .category-card {
            background: #fafafa;
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        .category-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .category-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a1a;
        }
        .category-score {
            font-size: 1.5rem;
            font-weight: 700;
            color: #00FF40;
        }
        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        .progress-green { background: linear-gradient(90deg, #00FF40, #00DD38); }
        .progress-yellow { background: linear-gradient(90deg, #FFD700, #FFA500); }
        .progress-orange { background: linear-gradient(90deg, #FFA500, #FF6B00); }
        .progress-red { background: linear-gradient(90deg, #FF6B6B, #EE4444); }
        .factor-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .factor-row:last-child {
            border-bottom: none;
        }
        .factor-name {
            font-size: 0.95rem;
            color: #333;
            flex: 1;
        }
        .factor-score {
            font-size: 0.9rem;
            font-weight: 600;
            color: #666;
            min-width: 60px;
            text-align: right;
        }
        .factor-bar {
            flex: 2;
            margin: 0 1rem;
        }
        .insight-card {
            background: #f0fff4;
            border: 1px solid #00FF40;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .insight-card.warning {
            background: #fff8e6;
            border-color: #FFD700;
        }
        .insight-icon {
            font-size: 1.2rem;
            margin-right: 0.5rem;
        }
        .site-divider {
            border: none;
            height: 3px;
            background: linear-gradient(90deg, transparent, #00FF40, transparent);
            margin: 2.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title(TEXT["results_title"][L])

    # Calculate all scores
    all_scores = []
    all_details = []

    for idx, site in enumerate(st.session_state["addresses"]):
        ans = st.session_state["answers"][idx]
        roof_score = compute_roof_score(site.get("roof_area"))
        final_score = compute_final_score(ans, roof_score)
        details = compute_detailed_scores(ans, roof_score)
        all_scores.append(final_score)
        all_details.append(details)

    # ─────────────────────────────────────────────────────────
    # DISPLAY EACH SITE
    # ─────────────────────────────────────────────────────────
    for idx, site in enumerate(st.session_state["addresses"]):
        ans = st.session_state["answers"][idx]
        final_score = all_scores[idx]
        details = all_details[idx]
        interpretation, recommendation, emoji = get_score_interpretation(final_score, L)

        # Site header
        if idx > 0:
            st.markdown('<hr class="site-divider">', unsafe_allow_html=True)

        st.markdown(f"### 📍 {site['address']} ({site['canton']})")

        # ── HERO SCORE CARD ──
        score_color = "#00FF40" if final_score >= 70 else "#FFD700" if final_score >= 55 else "#FFA500" if final_score >= 40 else "#FF6B6B"
        st.markdown(f"""
        <div class="score-hero">
            <p class="score-hero-value" style="color: {score_color} !important;">{final_score}</p>
            <p class="score-hero-label">{TEXT["score_label"][L]} / 100</p>
            <p class="score-hero-interpretation">{emoji} {interpretation}</p>
            <p class="score-hero-recommendation">{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── CATEGORY BREAKDOWN ──
        col_struct, col_cons = st.columns(2)

        with col_struct:
            struct_score = round(details["structure_total"], 1)
            struct_color = "progress-green" if struct_score >= 70 else "progress-yellow" if struct_score >= 50 else "progress-orange" if struct_score >= 30 else "progress-red"
            st.markdown(f"""
            <div class="category-card">
                <div class="category-header">
                    <span class="category-title">🏗️ {TEXT["structure_score_label"][L]}</span>
                    <span class="category-score">{struct_score}%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill {struct_color}" style="width: {struct_score}%;"></div>
                </div>
                <small style="color: #888;">Weight: {round(details["structure_weight"] * 100)}%</small>
            </div>
            """, unsafe_allow_html=True)

        with col_cons:
            cons_score = round(details["consumption_total"], 1)
            cons_color = "progress-green" if cons_score >= 70 else "progress-yellow" if cons_score >= 50 else "progress-orange" if cons_score >= 30 else "progress-red"
            st.markdown(f"""
            <div class="category-card">
                <div class="category-header">
                    <span class="category-title">⚡ {TEXT["consumption_score_label"][L]}</span>
                    <span class="category-score">{cons_score}%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill {cons_color}" style="width: {cons_score}%;"></div>
                </div>
                <small style="color: #888;">Weight: {round(details["consumption_weight"] * 100)}%</small>
            </div>
            """, unsafe_allow_html=True)

        # ── DETAILED FACTOR ANALYSIS ──
        with st.expander(f"📊 {TEXT['factor_analysis'][L]}", expanded=True):
            # Get questions for dynamic labels
            all_questions = st.session_state.get("questions", _load_questions_from_disk())
            structure_qs = [q for q in all_questions if q.get("category") == "structure"]
            consumption_qs = [q for q in all_questions if q.get("category") == "consumption"]

            # Structure factors
            st.markdown(f"**🏗️ {TEXT['structure_score_label'][L]}**")

            # Roof is always first (fixed input)
            factors_structure = [
                (TEXT["roof_size_topic"][L], details["roof"], f"{site.get('roof_area', 'N/A')} m²"),
            ]

            # Add structure questions dynamically
            for q in structure_qs:
                q_id = q["id"]
                if q_id in details:
                    topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q_id))
                    ans_value = ans.get(q_id, "")
                    if isinstance(ans_value, str) and '—' in ans_value:
                        ans_value = ans_value.split('—')[0].strip()
                    factors_structure.append((topic_label, details[q_id], ans_value))

            for name, data, value in factors_structure:
                bar_color = "progress-green" if data["normalized"] >= 66 else "progress-yellow" if data["normalized"] >= 33 else "progress-red"
                st.markdown(f"""
                <div class="factor-row">
                    <span class="factor-name">{name}</span>
                    <div class="factor-bar">
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill {bar_color}" style="width: {data['normalized']}%;"></div>
                        </div>
                    </div>
                    <span class="factor-score">{data['score']}/{data['max']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"↳ {value}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**⚡ {TEXT['consumption_score_label'][L]}**")

            # Add consumption questions dynamically
            factors_consumption = []
            for q in consumption_qs:
                q_id = q["id"]
                if q_id in details:
                    topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q_id))
                    ans_value = ans.get(q_id, "")
                    if q.get("type") == "slider":
                        ans_value = f"{ans_value}%"
                    elif isinstance(ans_value, str) and '—' in ans_value:
                        ans_value = ans_value.split('—')[0].strip()
                    factors_consumption.append((topic_label, details[q_id], ans_value))

            for name, data, value in factors_consumption:
                bar_color = "progress-green" if data["normalized"] >= 66 else "progress-yellow" if data["normalized"] >= 33 else "progress-red"
                st.markdown(f"""
                <div class="factor-row">
                    <span class="factor-name">{name}</span>
                    <div class="factor-bar">
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill {bar_color}" style="width: {data['normalized']}%;"></div>
                        </div>
                    </div>
                    <span class="factor-score">{data['score']}/{data['max']}</span>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"↳ {value}")

        # ── STRENGTHS & AREAS TO WATCH ──
        with st.expander(f"💡 {TEXT['strengths'][L]} & {TEXT['areas_to_watch'][L]}", expanded=False):
            # Build all_factors dynamically
            all_factors = [
                (TEXT["roof_size_topic"][L], details["roof"]["normalized"]),
            ]

            # Add structure questions
            for q in structure_qs:
                q_id = q["id"]
                if q_id in details:
                    topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q_id))
                    all_factors.append((topic_label, details[q_id]["normalized"]))

            # Add consumption questions
            for q in consumption_qs:
                q_id = q["id"]
                if q_id in details:
                    topic_label = q.get("topic", {}).get(L, q.get("topic", {}).get("en", q_id))
                    all_factors.append((topic_label, details[q_id]["normalized"]))

            strengths = [f for f in all_factors if f[1] >= 66]
            weaknesses = [f for f in all_factors if f[1] < 50]

            col_str, col_weak = st.columns(2)

            with col_str:
                st.markdown(f"**✅ {TEXT['strengths'][L]}**")
                if strengths:
                    for name, score in sorted(strengths, key=lambda x: -x[1]):
                        st.markdown(f"""
                        <div class="insight-card">
                            <span class="insight-icon">✓</span>{name} ({round(score)}%)
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No standout strengths")

            with col_weak:
                st.markdown(f"**⚠️ {TEXT['areas_to_watch'][L]}**")
                if weaknesses:
                    for name, score in sorted(weaknesses, key=lambda x: x[1]):
                        st.markdown(f"""
                        <div class="insight-card warning">
                            <span class="insight-icon">!</span>{name} ({round(score)}%)
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No significant weaknesses")

    # ─────────────────────────────────────────────────────────
    # COMPOSITE SCORE (multiple sites)
    # ─────────────────────────────────────────────────────────
    if len(st.session_state["addresses"]) > 1:
        st.markdown('<hr class="site-divider">', unsafe_allow_html=True)
        composite_score = round(sum(all_scores) / len(all_scores), 1)
        composite_interpretation, composite_recommendation, composite_emoji = get_score_interpretation(composite_score, L)

        st.markdown(f"## 🏢 {TEXT['composite_score'][L]}")
        st.caption(TEXT['composite_desc'][L])

        score_color = "#00FF40" if composite_score >= 70 else "#FFD700" if composite_score >= 55 else "#FFA500" if composite_score >= 40 else "#FF6B6B"
        st.markdown(f"""
        <div class="score-hero">
            <p class="score-hero-value" style="color: {score_color} !important;">{composite_score}</p>
            <p class="score-hero-label">{TEXT["score_label"][L]} / 100</p>
            <p class="score-hero-interpretation">{composite_emoji} {composite_interpretation}</p>
            <p class="score-hero-recommendation">{composite_recommendation}</p>
        </div>
        """, unsafe_allow_html=True)

        # Summary table
        st.markdown("### Site Comparison")
        for idx, site in enumerate(st.session_state["addresses"]):
            score = all_scores[idx]
            interp, _, em = get_score_interpretation(score, L)
            st.markdown(f"- **{site['address']}**: {score}/100 {em} *({interp})*")

    restart_button()

# -------------------------------------------------------
# ROUTER
# -------------------------------------------------------

page = st.session_state["page"]

if page == "lang":
    page_lang()
elif page == "role":
    page_role_selection()
elif page == "address_entry":
    page_address_entry()
elif page == "questions":
    page_questions()
elif page == "results":
    page_results()
