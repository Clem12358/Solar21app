# -----------------------------
# GLOBAL DESIGN OVERRIDES
# -----------------------------
st.markdown("""
<style>

    /* Completely hide the Streamlit sidebar */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }

    /* Force full-width layout */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* White background everywhere */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: white !important;
        color: black !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }

</style>
""", unsafe_allow_html=True)
