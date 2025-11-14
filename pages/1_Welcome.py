import streamlit as st

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

st.title(TEXT[lang]["title"])
st.write(TEXT[lang]["text"])

if st.button(TEXT[lang]["next"], type="primary"):
    st.page_link("pages/2_Addresses.py")

if st.button(TEXT[lang]["back"]):
    st.session_state.language = None
    st.page_link("app.py")
