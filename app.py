import streamlit as st

# ---- Session state defaults ----
if "language" not in st.session_state:
    st.session_state.language = None

# ---- Language selection text ----
LANG_TEXT = {
    "en": "Choose your language",
    "fr": "Choisissez votre langue",
    "de": "Wählen Sie Ihre Sprache"
}

# ---- Main landing page ----
st.title("Solar21 Pre-Check")

if st.session_state.language is None:

    st.subheader("Choose your language")
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

else:
    st.success("Language selected!")
    st.page_link("pages/1_Welcome.py", label="➡️ Continue")
