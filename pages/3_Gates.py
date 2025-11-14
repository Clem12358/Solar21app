import streamlit as st

# ----------------------------------------------------
# GLOBAL STYLE — hide sidebar + expand main content
# ----------------------------------------------------
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

/* Expand main content */
main[data-testid="stAppViewContainer"] {
    margin-left: 0 !important;
    padding-left: 2rem !important;
}

/* Expand top header */
header[data-testid="stHeader"] {
    margin-left: 0 !important;
}

/* --- Progress bar wrapper --- */
.progress-wrapper {
    width: 100%;
    background-color: #e0e0e0;
    height: 6px;
    border-radius: 4px;
    margin-bottom: 1.5rem;
}

.progress-bar {
    height: 6px;
    border-radius: 4px;
    background-color: #0072ff;
    width: 8%;  /* Page 1 = 8% */
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="Solar21 Pre-Check", page_icon="🔆")

# ----------------------------------------------------
# PROGRESS BAR (Page 0 of the process → 8%)
# ----------------------------------------------------
st.markdown("""
<div class="progress-wrapper">
    <div class="progress-bar"></div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# LANGUAGE SELECTION LOGIC
# ----------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = None

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
