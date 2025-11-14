import streamlit as st

if "language" not in st.session_state:
    st.session_state.language = None

st.set_page_config(page_title="Solar21 Pre-Check", page_icon="🔆")
st.title("Solar21 Pre-Check")

if st.session_state.language is None:
    st.subheader("Choose your language")
    if st.button("🇬🇧 English"):
        st.session_state.language = "en"
    if st.button("🇫🇷 Français"):
        st.session_state.language = "fr"
    if st.button("🇩🇪 Deutsch"):
        st.session_state.language = "de"
else:
    st.page_link("pages/1_Welcome.py", label="➡️ Continue")
