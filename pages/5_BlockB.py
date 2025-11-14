import streamlit as st

st.title("Block B — Strategic & Financial Attractiveness")

# Ensure previous blocks passed data
passed_addresses = st.session_state.get("passed_addresses", [])

if not passed_addresses:
    st.error("No properties available. Please complete previous steps.")
    st.stop()

st.write("We now evaluate the **strategic attractiveness** of your portfolio.")
st.write("This block takes only 1–2 minutes.")

blockB_scores = {}

for item in passed_addresses:
    addr = item["address"]
    st.subheader(f"🏢 {addr}")

    # 1) Electricity Price
    price = st.slider(
        f"Electricity price at {addr} (Rp. per kWh)",
        min_value=10,
        max_value=60,
        value=28,
        help="Higher prices = stronger ROI for solar"
    )

    # 2) Client Stability
    stability = st.selectbox(
        f"How stable is the tenant/ownership structure at {addr}?",
        ["Low stability", "Medium stability", "High stability"],
        index=1,
    )

    # 3) Commitment to ESG
    esg = st.selectbox(
        f"What is the client's ESG ambition level at {addr}?",
        ["Minimal", "Moderate", "Strong"],
        index=1,
    )

    # 4) Replication Potential
    replication = st.number_input(
        f"How many additional similar buildings could follow?",
        min_value=0,
        max_value=50,
        value=0,
    )

    # Score conversion
    score = {
        "price_rp_per_kWh": price,
        "stability": stability,
        "esg": esg,
        "replication": replication
    }

    blockB_scores[addr] = score

# Save scores
st.session_state["blockB_scores"] = blockB_scores

st.write("---")

# Continue button
if st.button("Continue to Final Result →", type="primary"):
    st.page_link("pages/6_Result.py")
