import streamlit as st

st.markdown("""
<style>
/* Hide the sidebar completely */
[data-testid="stSidebar"] {
    display: none !important;
}

/* Also hide the burger menu that toggles the sidebar */
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




st.title("Block B — Strategic & Financial Attractiveness")

# ----------------------------
# PROTECT AGAINST DIRECT NAVIGATION
# ----------------------------
passed_addresses = st.session_state.get("passed_addresses")
if not passed_addresses:
    st.error("No properties available. Please complete previous steps.")
    st.stop()

st.write("We now evaluate the strategic attractiveness of your portfolio.")
st.write("This block takes only 1–2 minutes.")

blockB_scores = {}

for item in passed_addresses:
    addr = item["address"]
    canton_price = item.get("avg_electricity_price_chf_kwh")  # From Sonnendach
    st.subheader(f"🏢 {addr}")

    # ---------------------------------
    # 1) Electricity Price (manual or pre-filled)
    # ---------------------------------
    initial_price = 28
    if canton_price:
        # Convert CHF/kWh → a more realistic Rp/kWh scale if you want
        # For now we keep the user-defined Rp slider and use CHF only for display
        st.caption(f"Average electricity price for {item.get('canton')}: {canton_price} CHF/kWh")

    price = st.slider(
        f"Electricity price at {addr} (Rp. per kWh)",
        min_value=10,
        max_value=60,
        value=initial_price,
        help="Higher local prices → faster solar ROI"
    )

    # Convert → score 1–3
    if price >= 40:
        price_score = 3
    elif price >= 25:
        price_score = 2
    else:
        price_score = 1

    # ---------------------------------
    # 2) Stability of Client
    # ---------------------------------
    stability = st.selectbox(
        f"How stable is the tenant/ownership structure at {addr}?",
        ["Low stability", "Medium stability", "High stability"],
        index=1,
    )
    stability_score = {"Low stability": 1, "Medium stability": 2, "High stability": 3}[stability]

    # ---------------------------------
    # 3) ESG Ambition
    # ---------------------------------
    esg = st.selectbox(
        f"What is the client's ESG ambition level at {addr}?",
        ["Minimal", "Moderate", "Strong"],
        index=1,
    )
    esg_score = {"Minimal": 1, "Moderate": 2, "Strong": 3}[esg]

    # ---------------------------------
    # 4) Replication Potential
    # ---------------------------------
    replication = st.number_input(
        f"How many additional similar buildings could follow?",
        min_value=0,
        max_value=50,
        value=0,
    )

    if replication >= 10:
        replication_score = 3
    elif replication >= 3:
        replication_score = 2
    else:
        replication_score = 1

    # ---------------------------------
    # Pack final numeric results
    # ---------------------------------
    blockB_scores[addr] = {
        "price_score": int(price_score),           # FIXED
        "stability_score": int(stability_score),
        "esg_score": int(esg_score),
        "replication_score": int(replication_score),
    }

# Save scores
st.session_state["blockB_scores"] = blockB_scores

st.write("---")

if st.button("Continue to Final Result →", type="primary"):
    st.switch_page("pages/6_Result.py")





