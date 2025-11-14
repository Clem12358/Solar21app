import streamlit as st

# ---- SESSION STATE SETUP ----
if "language" not in st.session_state:
    st.session_state.language = None

# ---- TRANSLATIONS ----
TEXT = {
    "en": {
        "choose_lang": "Choose your language",
        "welcome_title": "Welcome to the Solar21 Partner Pre-Check",
        "welcome_text": (
            "This short pre-check helps you understand in **under two minutes** "
            "whether your client is a strong fit for Solar21’s model.\n\n"
            "Click below to begin."
        ),
        "start": "Start",
        "back": "Back"
    },
    "fr": {
        "choose_lang": "Choisissez votre langue",
        "welcome_title": "Bienvenue sur le pré-check partenaire Solar21",
        "welcome_text": (
            "Ce pré-check très rapide vous permet de savoir en **moins de deux minutes** "
            "si votre client représente une bonne opportunité pour le modèle Solar21.\n\n"
            "Cliquez ci-dessous pour commencer."
        ),
        "start": "Commencer",
        "back": "Retour"
    },
    "de": {
        "choose_lang": "Wählen Sie Ihre Sprache",
        "welcome_title": "Willkommen zum Solar21 Partner Pre-Check",
        "welcome_text": (
            "Dieser kurze Pre-Check zeigt Ihnen in **unter zwei Minuten**, "
            "ob Ihr Kunde gut zum Geschäftsmodell von Solar21 passt.\n\n"
            "Klicken Sie unten, um zu starten."
        ),
        "start": "Starten",
        "back": "Zurück"
    }
}


# ---- PAGE 1: LANGUAGE SELECTION ----
def page_language_selection():
    st.title(TEXT["en"]["choose_lang"])  # default english title (neutral choice)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = "en"

    with col2:
        if st.button("🇫🇷 Français", use_container_width=True):
            st.session_state.language = "fr"

    with col3:
        if st.button("🇩🇪 Deutsch", use_container_width=True):
            st.session_state.language = "de"


# ---- PAGE 2: WELCOME ----
def page_welcome():
    lang = st.session_state.language
    st.title(TEXT[lang]["welcome_title"])
    st.write(TEXT[lang]["welcome_text"])

    st.write("")
    st.write("")

    if st.button(TEXT[lang]["start"], type="primary", use_container_width=True):
        st.session_state.page = "precheck"   # your future page

    if st.button(TEXT[lang]["back"], use_container_width=True):
        st.session_state.language = None


# ---- ROUTING ----
if "page" not in st.session_state:
    st.session_state.page = "lang"

if st.session_state.language is None:
    page_language_selection()

else:
    if st.session_state.page == "lang":
        page_welcome()

    elif st.session_state.page == "precheck":
        st.title("⚙️ Pre-Check (work in progress)")
        st.write("This is where your questions and scoring logic will go.")
        if st.button("🔙 Back"):
            st.session_state.page = "lang"
