import streamlit as st

# ----------------------------
# Hide default sidebar & use full width
# ----------------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit’s default sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Expand main content to full width */
    div[data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Language from session state
# ----------------------------
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

# ----------------------------
# UI
# ----------------------------
st.title(TEXT[lang]["title"])
st.write(TEXT[lang]["text"])

col_back, col_next = st.columns([1, 1])

with col_back:
    if st.button(TEXT[lang]["back"]):
        # Reset language and go back to main app page
        st.session_state.language = None
        st.switch_page("app.py")

with col_next:
    if st.button(TEXT[lang]["next"], type="primary"):
        # Go to address input page
        st.switch_page("pages/2_Addresses.py")
