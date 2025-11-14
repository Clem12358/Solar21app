import streamlit as st

st.title("Block B — Strategic & Financial Attractiveness")

# ----------------------------
# PROTECT AGAINST DIRECT NAVIGATION
# ----------------------------
passed_addresses = st.session_state.get("passed_addresses")
if not passed_addresses:
    st.error("No properties available. Please complete previous steps.")
    st.stop()

st.write("We now evaluate the **strategic attractiveness** of your portfolio.")
st.write("This block takes only 1–2 minutes.")

blockB_scores = {}

for item in passed_addresses:
    addr = item["address"]
    st.subheader(f"🏢 {addr}")

    # ---------------------------------
    # 1) Electricity Price (normalised)
    # ---------------------------------
    price = st.slider(
        f"Electricity price at {addr} (Rp. per kWh)",
        min_value=10,
        max_value=60,
        value=28,
        help="Higher prices = stronger ROI for solar"
    )
    # Convert Rp/kWh into score 1–3
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
    # Convert into score
    if replication >= 10:
        replication_score = 3
    elif replication >= 3:
        replication_score = 2
    else:
        replication_score = 1

    # Pack final numeric results
    blockB_scores[addr] = {
        "consumption_score": int(price_score),
        "stability_score": int(stability_score),
        "esg_score": int(esg_score),
        "replication_score": int(replication_score),
    }

# Save scores
st.session_state["blockB_scores"] = blockB_scores

st.write("---")

if st.button("Continue to Final Result →", type="primary"):
    st.page_link("pages/6_Result.py")
