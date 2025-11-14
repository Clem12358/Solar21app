import streamlit as st

# =========================================
# COMPLETE SIDEBAR REMOVAL + FULL-WIDTH PAGE
# =========================================
st.markdown(
    """
    <style>
    /* Hide full sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Expand main content to full width */
    div[data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================
# LANGUAGE HANDLING
# =========================================
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
        "back": "← Back"
    },
    "fr": {
        "title": "Bienvenue sur le pré-check partenaire Solar21",
        "text": (
            "Cet outil vous aide à évaluer en **moins de deux minutes** "
            "si le bâtiment de votre client est un bon candidat pour Solar21."
            "\n\nCliquez sur *Suivant* pour continuer."
        ),
        "next": "Suivant →",
        "back": "← Retour"
    },
    "de": {
        "title": "Willkommen zum Solar21 Partner Pre-Check",
        "text": (
            "Dieses Tool zeigt Ihnen in **unter zwei Minuten**, "
            "ob das Gebäude Ihres Kunden gut zu Solar21 passt."
            "\n\nKlicken Sie auf *Weiter*, um fortzufahren."
        ),
        "next": "Weiter →",
        "back": "← Zurück"
    }
}

# =========================================
# PAGE CONTENT
# =========================================
st.title(TEXT[lang]["title"])
st.write(TEXT[lang]["text"])

col1, col2 = st.columns([1, 1])

with col1:
    if st.button(TEXT[lang]["next"], type="primary", use_container_width=True):
        st.page_link("pages/2_Addresses.py")

with col2:
    if st.button(TEXT[lang]["back"], use_container_width=True):
        st.session_state.language = None
        st.page_link("app.py")
