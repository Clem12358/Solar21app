import json
import os
from pathlib import Path

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

def init_state():
    defaults = {
        "page": "lang",
        "language": "en",   # default English
        "addresses": [],
        "current_index": 0,
        "answers": {},
        "weights": _load_weights_from_disk(),
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
        "en": "You can also approximate these values on <a href=\"https://www.sonnendach.ch\" target=\"_blank\">sonnendach.ch</a>.",
        "fr": "Vous pouvez également estimer ces valeurs sur <a href=\"https://www.sonnendach.ch\" target=\"_blank\">sonnendach.ch</a>.",
        "de": "Sie können diese Werte auch auf <a href=\"https://www.sonnendach.ch\" target=\"_blank\">sonnendach.ch</a> abschätzen.",
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
    """Compute the final Solar21 site attractiveness score using weighted sub-scores"""

    # Extract owner type score (max 3)
    owner_str = answers["owner_type"]
    if "Public entity" in owner_str or "Entité publique" in owner_str or "Öffentliche Einrichtung" in owner_str:
        owner_type_score = 3
    elif "Standard commercial" in owner_str or "commercial standard" in owner_str or "Standard-Gewerbe" in owner_str:
        owner_type_score = 2
    else:
        owner_type_score = 1

    # Extract ESG score (max 3)
    esg_str = answers["esg"]
    if esg_str.startswith("Yes") or esg_str.startswith("Oui") or esg_str.startswith("Ja"):
        esg_score = 3
    elif esg_str.startswith("Not sure") or esg_str.startswith("Incertain") or esg_str.startswith("Unsicher"):
        esg_score = 2
    else:
        esg_score = 1

    # Extract spend score (max 4)
    spend_str = answers["spend"]
    if "Above 800k" in spend_str or "Plus de 800k" in spend_str or "Über 800k" in spend_str:
        spend_score = 4
    elif "300k" in spend_str and "800k" in spend_str:
        spend_score = 3
    elif "100k" in spend_str and "300k" in spend_str:
        spend_score = 2
    else:
        spend_score = 1

    # Daytime score (max 3)
    daytime_pct = answers["daytime"]
    if daytime_pct >= 75:
        daytime_score = 3
    elif daytime_pct >= 50:
        daytime_score = 2
    elif daytime_pct >= 25:
        daytime_score = 1
    else:
        daytime_score = 0

    # Seasonality score (max 3, inverted - low variation is better)
    season_str = answers["season"]
    if "Low" in season_str or "Faible" in season_str or "Geringe" in season_str:
        season_score = 3
    elif "Moderate" in season_str or "modérée" in season_str or "Mäßige" in season_str:
        season_score = 2
    else:
        season_score = 1

    # 24/7 loads score (max 3)
    loads_str = answers["loads"]
    if loads_str.startswith("Yes") or loads_str.startswith("Oui") or loads_str.startswith("Ja"):
        loads_score = 3
    else:
        loads_score = 1

    # Get weights from session state
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
        structure_weight = DEFAULT_WEIGHTS["structure"]
        consumption_weight = DEFAULT_WEIGHTS["consumption"]

    # Structure sub-weights
    sub_roof = weights.get("sub_roof", DEFAULT_WEIGHTS["sub_roof"])
    sub_owner = weights.get("sub_owner", DEFAULT_WEIGHTS["sub_owner"])
    sub_esg = weights.get("sub_esg", DEFAULT_WEIGHTS["sub_esg"])

    # Consumption sub-weights
    sub_spend = weights.get("sub_spend", DEFAULT_WEIGHTS["sub_spend"])
    sub_daytime = weights.get("sub_daytime", DEFAULT_WEIGHTS["sub_daytime"])
    sub_season = weights.get("sub_season", DEFAULT_WEIGHTS["sub_season"])
    sub_loads = weights.get("sub_loads", DEFAULT_WEIGHTS["sub_loads"])

    # Normalize each sub-score to 0-1 range, then apply sub-weights
    # Structure: roof (0-3), owner (1-3), esg (1-3)
    roof_norm = roof_score / 3 if roof_score > 0 else 0
    owner_norm = owner_type_score / 3
    esg_norm = esg_score / 3

    A_norm = sub_roof * roof_norm + sub_owner * owner_norm + sub_esg * esg_norm

    # Consumption: spend (1-4), daytime (0-3), season (1-3), loads (1-3)
    spend_norm = spend_score / 4
    daytime_norm = daytime_score / 3
    season_norm = season_score / 3
    loads_norm = loads_score / 3

    B_norm = sub_spend * spend_norm + sub_daytime * daytime_norm + sub_season * season_norm + sub_loads * loads_norm

    # Final weighted score
    final_score = structure_weight * A_norm + consumption_weight * B_norm

    # Convert to 0-100 scale
    final_score_100 = final_score * 100

    return round(final_score_100, 1)


def compute_detailed_scores(answers, roof_score):
    """Compute detailed breakdown of all scores for results display"""

    # Extract owner type score (max 3)
    owner_str = answers["owner_type"]
    if "Public entity" in owner_str or "Entité publique" in owner_str or "Öffentliche Einrichtung" in owner_str:
        owner_type_score = 3
    elif "Standard commercial" in owner_str or "commercial standard" in owner_str or "Standard-Gewerbe" in owner_str:
        owner_type_score = 2
    else:
        owner_type_score = 1

    # Extract ESG score (max 3)
    esg_str = answers["esg"]
    if esg_str.startswith("Yes") or esg_str.startswith("Oui") or esg_str.startswith("Ja"):
        esg_score = 3
    elif esg_str.startswith("Not sure") or esg_str.startswith("Incertain") or esg_str.startswith("Unsicher"):
        esg_score = 2
    else:
        esg_score = 1

    # Extract spend score (max 4)
    spend_str = answers["spend"]
    if "Above 800k" in spend_str or "Plus de 800k" in spend_str or "Über 800k" in spend_str:
        spend_score = 4
    elif "300k" in spend_str and "800k" in spend_str:
        spend_score = 3
    elif "100k" in spend_str and "300k" in spend_str:
        spend_score = 2
    else:
        spend_score = 1

    # Daytime score (max 3)
    daytime_pct = answers["daytime"]
    if daytime_pct >= 75:
        daytime_score = 3
    elif daytime_pct >= 50:
        daytime_score = 2
    elif daytime_pct >= 25:
        daytime_score = 1
    else:
        daytime_score = 0

    # Seasonality score (max 3)
    season_str = answers["season"]
    if "Low" in season_str or "Faible" in season_str or "Geringe" in season_str:
        season_score = 3
    elif "Moderate" in season_str or "modérée" in season_str or "Mäßige" in season_str:
        season_score = 2
    else:
        season_score = 1

    # 24/7 loads score (max 3)
    loads_str = answers["loads"]
    if loads_str.startswith("Yes") or loads_str.startswith("Oui") or loads_str.startswith("Ja"):
        loads_score = 3
    else:
        loads_score = 1

    # Get weights
    weights = st.session_state.get("weights", DEFAULT_WEIGHTS)
    structure_weight = weights.get("structure", DEFAULT_WEIGHTS["structure"])
    consumption_weight = weights.get("consumption", DEFAULT_WEIGHTS["consumption"])

    # Sub-weights
    sub_roof = weights.get("sub_roof", DEFAULT_WEIGHTS["sub_roof"])
    sub_owner = weights.get("sub_owner", DEFAULT_WEIGHTS["sub_owner"])
    sub_esg = weights.get("sub_esg", DEFAULT_WEIGHTS["sub_esg"])
    sub_spend = weights.get("sub_spend", DEFAULT_WEIGHTS["sub_spend"])
    sub_daytime = weights.get("sub_daytime", DEFAULT_WEIGHTS["sub_daytime"])
    sub_season = weights.get("sub_season", DEFAULT_WEIGHTS["sub_season"])
    sub_loads = weights.get("sub_loads", DEFAULT_WEIGHTS["sub_loads"])

    # Normalized scores (0-1)
    roof_norm = roof_score / 3 if roof_score > 0 else 0
    owner_norm = owner_type_score / 3
    esg_norm = esg_score / 3
    spend_norm = spend_score / 4
    daytime_norm = daytime_score / 3
    season_norm = season_score / 3
    loads_norm = loads_score / 3

    # Category scores (0-100)
    A_norm = sub_roof * roof_norm + sub_owner * owner_norm + sub_esg * esg_norm
    B_norm = sub_spend * spend_norm + sub_daytime * daytime_norm + sub_season * season_norm + sub_loads * loads_norm

    return {
        "roof": {"score": roof_score, "max": 3, "normalized": roof_norm * 100, "weight": sub_roof},
        "owner": {"score": owner_type_score, "max": 3, "normalized": owner_norm * 100, "weight": sub_owner},
        "esg": {"score": esg_score, "max": 3, "normalized": esg_norm * 100, "weight": sub_esg},
        "spend": {"score": spend_score, "max": 4, "normalized": spend_norm * 100, "weight": sub_spend},
        "daytime": {"score": daytime_score, "max": 3, "normalized": daytime_norm * 100, "weight": sub_daytime},
        "season": {"score": season_score, "max": 3, "normalized": season_norm * 100, "weight": sub_season},
        "loads": {"score": loads_score, "max": 3, "normalized": loads_norm * 100, "weight": sub_loads},
        "structure_total": A_norm * 100,
        "consumption_total": B_norm * 100,
        "structure_weight": structure_weight,
        "consumption_weight": consumption_weight,
    }


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
    st.title(TEXT["role_title"][L])
    st.markdown("<br>", unsafe_allow_html=True)

    choice = st.radio(
        "",
        [TEXT["partner_option"][L], TEXT["employee_option"][L]],
        key="role_choice",
        label_visibility="collapsed",
    )

    if choice == TEXT["partner_option"][L]:
        st.session_state["employee_authenticated"] = False
        if st.button(TEXT["proceed"][L], type="primary", use_container_width=True):
            goto("address_entry")
            st.rerun()
        return

    # Employee branch
    pwd = st.text_input(
        TEXT["employee_password"][L],
        type="password",
        key="employee_password_input",
    )

    if pwd:
        if pwd == EMPLOYEE_PASSWORD:
            st.session_state["employee_authenticated"] = True
        else:
            st.session_state["employee_authenticated"] = False
            st.error(TEXT["employee_password_error"][L])

    if st.session_state.get("employee_authenticated"):
        st.success(TEXT["weights_subtext"][L])
        st.info(TEXT["weights_pull_hint"][L])

        st.markdown(f"## {TEXT['weights_title'][L]}")
        st.caption(TEXT["fine_tune_hint"][L])
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

        # ─────────────────────────────────────────────────────────
        # STRUCTURE SUB-WEIGHTS (expandable)
        # ─────────────────────────────────────────────────────────
        with st.expander(f"⚙️ {TEXT['structure_subweights_section'][L]}", expanded=False):
            st.markdown("""
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <small>These weights determine the relative importance of factors within the Structure category. They will be normalized to sum to 100%.</small>
            </div>
            """, unsafe_allow_html=True)

            scol1, scol2, scol3 = st.columns(3)
            with scol1:
                sub_roof_default = int(round(st.session_state["weights"].get("sub_roof", DEFAULT_WEIGHTS["sub_roof"]) * 100))
                sub_roof_pct = st.slider(
                    TEXT["sub_roof_weight"][L],
                    0, 100, sub_roof_default,
                    step=5, format="%d%%", key="sub_roof"
                )
            with scol2:
                sub_owner_default = int(round(st.session_state["weights"].get("sub_owner", DEFAULT_WEIGHTS["sub_owner"]) * 100))
                sub_owner_pct = st.slider(
                    TEXT["sub_owner_weight"][L],
                    0, 100, sub_owner_default,
                    step=5, format="%d%%", key="sub_owner"
                )
            with scol3:
                sub_esg_default = int(round(st.session_state["weights"].get("sub_esg", DEFAULT_WEIGHTS["sub_esg"]) * 100))
                sub_esg_pct = st.slider(
                    TEXT["sub_esg_weight"][L],
                    0, 100, sub_esg_default,
                    step=5, format="%d%%", key="sub_esg"
                )

            struct_sub_total = sub_roof_pct + sub_owner_pct + sub_esg_pct
            if struct_sub_total > 0:
                st.caption(f"Total: {struct_sub_total}% → normalized to 100%")
            else:
                st.warning("At least one sub-weight must be > 0")

        # ─────────────────────────────────────────────────────────
        # CONSUMPTION SUB-WEIGHTS (expandable)
        # ─────────────────────────────────────────────────────────
        with st.expander(f"⚙️ {TEXT['consumption_subweights_section'][L]}", expanded=False):
            st.markdown("""
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <small>These weights determine the relative importance of factors within the Consumption category. They will be normalized to sum to 100%.</small>
            </div>
            """, unsafe_allow_html=True)

            ccol1, ccol2 = st.columns(2)
            with ccol1:
                sub_spend_default = int(round(st.session_state["weights"].get("sub_spend", DEFAULT_WEIGHTS["sub_spend"]) * 100))
                sub_spend_pct = st.slider(
                    TEXT["sub_spend_weight"][L],
                    0, 100, sub_spend_default,
                    step=5, format="%d%%", key="sub_spend"
                )
                sub_daytime_default = int(round(st.session_state["weights"].get("sub_daytime", DEFAULT_WEIGHTS["sub_daytime"]) * 100))
                sub_daytime_pct = st.slider(
                    TEXT["sub_daytime_weight"][L],
                    0, 100, sub_daytime_default,
                    step=5, format="%d%%", key="sub_daytime"
                )
            with ccol2:
                sub_season_default = int(round(st.session_state["weights"].get("sub_season", DEFAULT_WEIGHTS["sub_season"]) * 100))
                sub_season_pct = st.slider(
                    TEXT["sub_season_weight"][L],
                    0, 100, sub_season_default,
                    step=5, format="%d%%", key="sub_season"
                )
                sub_loads_default = int(round(st.session_state["weights"].get("sub_loads", DEFAULT_WEIGHTS["sub_loads"]) * 100))
                sub_loads_pct = st.slider(
                    TEXT["sub_loads_weight"][L],
                    0, 100, sub_loads_default,
                    step=5, format="%d%%", key="sub_loads"
                )

            cons_sub_total = sub_spend_pct + sub_daytime_pct + sub_season_pct + sub_loads_pct
            if cons_sub_total > 0:
                st.caption(f"Total: {cons_sub_total}% → normalized to 100%")
            else:
                st.warning("At least one sub-weight must be > 0")

        st.markdown("---")

        # ─────────────────────────────────────────────────────────
        # SAVE BUTTON
        # ─────────────────────────────────────────────────────────
        col_save, col_proceed = st.columns(2)
        with col_save:
            if st.button(TEXT["save_weights"][L], type="primary", use_container_width=True):
                # Normalize structure sub-weights
                struct_total = sub_roof_pct + sub_owner_pct + sub_esg_pct
                if struct_total == 0:
                    struct_total = 1  # Avoid division by zero
                # Normalize consumption sub-weights
                cons_total = sub_spend_pct + sub_daytime_pct + sub_season_pct + sub_loads_pct
                if cons_total == 0:
                    cons_total = 1

                new_weights = {
                    "structure": structure_pct / 100,
                    "consumption": consumption_pct / 100,
                    "sub_roof": sub_roof_pct / struct_total,
                    "sub_owner": sub_owner_pct / struct_total,
                    "sub_esg": sub_esg_pct / struct_total,
                    "sub_spend": sub_spend_pct / cons_total,
                    "sub_daytime": sub_daytime_pct / cons_total,
                    "sub_season": sub_season_pct / cons_total,
                    "sub_loads": sub_loads_pct / cons_total,
                }
                st.session_state["weights"] = new_weights
                _persist_weights(new_weights)
                st.success(f"✅ {TEXT['weights_saved'][L]}")

        with col_proceed:
            if st.button(TEXT["proceed"][L], use_container_width=True):
                goto("address_entry")
                st.rerun()

# -------------------------------------------------------
# PAGE 3 — ENTER ADDRESSES
# -------------------------------------------------------

def page_address_entry():
    L = st.session_state["language"]

    st.title(TEXT["address_title"][L])
    st.markdown("<br>", unsafe_allow_html=True)

    st.warning(TEXT["roof_data_local_hint"][L])

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

        # Debug: show raw Sonnendach response if available
        if entry.get("sonnendach_raw") is not None:
            with st.expander("Debug Sonnendach data", expanded=False):
                st.json(entry["sonnendach_raw"])

        st.markdown(f"**{TEXT['manual_roof_prompt'][L]}**")
        st.caption(TEXT["roof_data_local_hint"][L])
        st.caption(TEXT["manual_roof_hint"][L], unsafe_allow_html=True)
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

    # Create a placeholder for the loading message
    status_placeholder = st.empty()
    
    if st.button(TEXT["save_continue"][L], use_container_width=True, type="primary"):
        # Show loading status
        with status_placeholder.container():
            st.info("🔄 Fetching rooftop data, please wait...")

        # Fetch rooftop data for all addresses before continuing
        all_success = True
        lookup_errors = []
        with st.spinner(""):
            for idx, entry in enumerate(st.session_state["addresses"]):
                if entry["address"] and entry["canton"] and not entry["roof_area"]:
                    data = get_sonnendach_info(entry["address"])

                    # Store raw data for debugging so we can inspect it on the address page
                    entry["sonnendach_raw"] = data

                    if data:
                        # TODO: adjust these keys once we see the exact Sonnendach structure
                        entry["roof_area"] = data.get("surface_area_m2")
                        entry["roof_pitch"] = data.get("roof_pitch_deg")
                        entry["roof_orientation"] = data.get("roof_heading_deg")
                        if data.get("error"):
                            lookup_errors.append(data.get("error"))
                    if entry.get("roof_area") is None:
                        all_success = False

        if all_success:
            status_placeholder.success("✅ Data loaded successfully! Proceeding...")
            import time
            time.sleep(1)
            goto("questions")
            st.rerun()
        else:
            status_placeholder.warning(TEXT["manual_fill_warning"][L])
            if lookup_errors:
                for err in dict.fromkeys(lookup_errors):
                    status_placeholder.caption(f"• {err}")

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

    if site.get("sonnendach_raw") is not None:
        with st.expander("🔍 Debug roof data", expanded=False):
            st.json(site["sonnendach_raw"])

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

    # ── QUESTION 1: OWNER TYPE ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">1</span>{TEXT['owner_type'][L]}</div>
        <div class="question-help">{TEXT['owner_type_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    owner_type = st.radio(
        "owner_type_radio",
        QUESTION_OPTIONS["owner"][L],
        key=prefix + "owner",
        label_visibility="collapsed"
    )

    # ── QUESTION 2: ESG ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">2</span>{TEXT['esg'][L]}</div>
        <div class="question-help">{TEXT['esg_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    esg = st.radio(
        "esg_radio",
        QUESTION_OPTIONS["esg"][L],
        key=prefix + "esg",
        label_visibility="collapsed"
    )

    # ── QUESTION 3: DAYTIME ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">3</span>{TEXT['daytime'][L]}</div>
        <div class="question-help">{TEXT['daytime_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    col_slider, col_value = st.columns([4, 1])
    with col_slider:
        daytime = st.slider(
            "daytime_slider",
            0, 100, 60,
            key=prefix + "daytime",
            label_visibility="collapsed"
        )
    with col_value:
        st.markdown(
            f"<div style='background: #00FF40; color: #000; padding: 0.5rem 1rem; border-radius: 8px; text-align: center; font-size: 1.3rem; font-weight: 700;'>{daytime}%</div>",
            unsafe_allow_html=True
        )

    # ── QUESTION 4: SPEND ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">4</span>{TEXT['spend'][L]}</div>
        <div class="question-help">{TEXT['spend_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    spend = st.radio(
        "spend_radio",
        QUESTION_OPTIONS["spend"][L],
        key=prefix + "spend",
        label_visibility="collapsed",
        horizontal=True
    )

    # ── QUESTION 5: SEASON ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">5</span>{TEXT['season'][L]}</div>
        <div class="question-help">{TEXT['season_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    season = st.radio(
        "season_radio",
        QUESTION_OPTIONS["season"][L],
        key=prefix + "season",
        label_visibility="collapsed"
    )

    # ── QUESTION 6: 24/7 LOADS ──
    st.markdown(f"""
    <div class="question-card">
        <div class="question-title"><span class="question-number">6</span>{TEXT['loads'][L]}</div>
        <div class="question-help">{TEXT['loads_help'][L]}</div>
    </div>
    """, unsafe_allow_html=True)
    loads = st.radio(
        "loads_radio",
        QUESTION_OPTIONS["loads"][L],
        key=prefix + "247",
        label_visibility="collapsed",
        horizontal=True
    )

    # ─────────────────────────────────────────────────────────
    # SAVE ANSWERS
    # ─────────────────────────────────────────────────────────
    st.session_state["answers"][idx] = {
        "owner_type": owner_type,
        "esg": esg,
        "daytime": daytime,
        "spend": spend,
        "season": season,
        "loads": loads,
        "roof_score": compute_roof_score(site["roof_area"]),
    }

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
            font-size: 4rem;
            font-weight: 800;
            color: #00FF40;
            margin: 0;
            line-height: 1;
        }
        .score-hero-label {
            font-size: 1rem;
            color: #888;
            margin-top: 0.5rem;
        }
        .score-hero-interpretation {
            font-size: 1.5rem;
            color: #fff;
            margin-top: 1rem;
            font-weight: 600;
        }
        .score-hero-recommendation {
            font-size: 1rem;
            color: #aaa;
            margin-top: 0.5rem;
            font-style: italic;
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
            <p class="score-hero-value" style="color: {score_color};">{final_score}</p>
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
            # Structure factors
            st.markdown(f"**🏗️ {TEXT['structure_score_label'][L]}**")

            factors_structure = [
                (TEXT["roof_score_label"][L], details["roof"], f"{site.get('roof_area', 'N/A')} m²"),
                (TEXT["owner_type_label"][L], details["owner"], ans['owner_type'].split('—')[0].strip()),
                (TEXT["esg_label"][L], details["esg"], ans['esg'].split('—')[0].strip()),
            ]

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

            factors_consumption = [
                (TEXT["spend_label"][L], details["spend"], ans['spend']),
                (TEXT["daytime_label"][L], details["daytime"], f"{ans['daytime']}%"),
                (TEXT["season_label"][L], details["season"], ans['season'].split('—')[0].strip()),
                (TEXT["loads_label"][L], details["loads"], ans['loads'].split('—')[0].strip()),
            ]

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
            all_factors = [
                (TEXT["roof_score_label"][L], details["roof"]["normalized"]),
                (TEXT["owner_type_label"][L], details["owner"]["normalized"]),
                (TEXT["esg_label"][L], details["esg"]["normalized"]),
                (TEXT["spend_label"][L], details["spend"]["normalized"]),
                (TEXT["daytime_label"][L], details["daytime"]["normalized"]),
                (TEXT["season_label"][L], details["season"]["normalized"]),
                (TEXT["loads_label"][L], details["loads"]["normalized"]),
            ]

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
            <p class="score-hero-value" style="color: {score_color};">{composite_score}</p>
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
