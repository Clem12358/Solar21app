import streamlit as st

# --------------------------------
# GLOBAL LAYOUT / CSS
# --------------------------------
st.markdown("""
<style>
/* Hide the sidebar completely */
[data-testid="stSidebar"] {
    display: none !important;
}

/* Hide the burger menu */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Expand main container */
main[data-testid="stAppViewContainer"] {
    margin-left: 0 !important;
    padding-left: 2rem !important;
}

/* Expand header area if needed */
header[data-testid="stHeader"] {
    margin-left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Solar21 Pre-Check", page_icon="🔆")

# --------------------------------
# INITIALISE STATE
# --------------------------------
if "language" not in st.session_state:
    st.session_state.language = None

if "progress" not in st.session_state:
    st.session_state.progress = 0   # landing page = 0%


# --------------------------------
# TOP PROGRESS BAR
# --------------------------------
st.progress(st.session_state.progress)


# --------------------------------
# PAGE CONTENT
# --------------------------------
st.title("Solar21 Pre-Check")

if st.session_state.language is None:

    st.subheader("Choose your language")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = "en"
            st.session_state.progress = 10  # after language selection
            st.page_link("pages/1_Welcome.py")

    with col2:
        if st.button("🇫🇷 Français", use_container_width=True):
            st.session_state.language = "fr"
            st.session_state.progress = 10
            st.page_link("pages/1_Welcome.py")

    with col3:
        if st.button("🇩🇪 Deutsch", use_container_width=True):
            st.session_state.language = "de"
            st.session_state.progress = 10
            st.page_link("pages/1_Welcome.py")

else:
    # Language already chosen in session
    st.page_link("pages/1_Welcome.py", label="➡️ Continue")
