import streamlit as st
import pandas as pd

st.markdown("""
    <style>
    .stPageLink {display: none !important;}
    </style>
    """, unsafe_allow_html=True)


st.title("Final Results – Solar21 Property Evaluation")

# -----------------------------
# Retrieve all stored data
# -----------------------------
passed_addresses = st.session_state.get("passed_addresses", [])
A1 = st.session_state.get("A1_scores", {})
A2 = st.session_state.get("A2_scores", {})
A3 = st.session_state.get("A3_scores", {})
B = st.session_state.get("blockB_scores", {})

if not passed_addresses:
    st.error("No passed addresses found. Please start again.")
    st.stop()

# -------------------------------------------------------
# Weighting Model
# -------------------------------------------------------
WEIGHT_A = 0.40          # Block A (A1,A2,A3)
WEIGHT_B = 0.40          # Block B (price, stability, esg, replication)

W_A = WEIGHT_A / 3       # each A-subscore
W_B = WEIGHT_B / 4       # now four B-sub-scores

# -----------------------------
# Build consolidated dataframe
# -----------------------------
rows = []

for item in passed_addresses:
    address = item["address"]

    # ----- Block A -----
    score_A1 = A1.get(address, 0)
    score_A2 = A2.get(address, 0)
    score_A3 = A3.get(address, 0)

    score_A_total = (
        score_A1 * W_A +
        score_A2 * W_A +
        score_A3 * W_A
    )

    # ----- Block B -----
    B_addr = B.get(address, {})

    price_score = B_addr.get("price_score", 0)
    stability_score = B_addr.get("stability_score", 0)
    esg_score = B_addr.get("esg_score", 0)
    replication_score = B_addr.get("replication_score", 0)

    score_B_total = (
        price_score * W_B +
        stability_score * W_B +
        esg_score * W_B +
        replication_score * W_B
    )

    final_score = round(score_A_total + score_B_total, 3)

    rows.append({
        "Address": address,
        "Roof Area (m²)": item.get("surface_area_m2"),
        "PV Potential (kWh)": item.get("pv_full_kwh"),
        "Pitch (°)": item.get("roof_pitch_deg"),
        "Heading (°)": item.get("roof_heading_deg"),
        "Canton": item.get("canton"),
        "Electricity Price (CHF/kWh)": item.get("avg_electricity_price_chf_kwh"),

        # Block A
        "A1 Roof Size": score_A1,
        "A2 Cost of Capital": score_A2,
        "A3 ESG": score_A3,

        # Block B
        "B Price": price_score,
        "B Stability": stability_score,
        "B ESG Ambition": esg_score,
        "B Replication": replication_score,

        # Final score
        "Final Score": final_score,
    })

df = pd.DataFrame(rows).sort_values("Final Score", ascending=False)

# -----------------------------
# Display table
# -----------------------------
st.subheader("Ranking of All Valid Properties")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Best match highlight
# -----------------------------
best = df.iloc[0]

st.success(
    f"🏆 **Top Recommendation: {best['Address']}**\n\n"
    f"- Roof Area: **{best['Roof Area (m²)']} m²**\n"
    f"- PV Potential: **{best['PV Potential (kWh)']} kWh/year**\n"
    f"- Canton: **{best['Canton']}**\n"
    f"- Electricity Price: **{best['Electricity Price (CHF/kWh)']} CHF/kWh**\n"
    f"- Final Score: **{best['Final Score']}**"
)

# -----------------------------
# Download
# -----------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Detailed Results (CSV)",
    data=csv,
    file_name="solar21_results.csv",
    mime="text/csv",
)

# -----------------------------
# Navigation
# -----------------------------
if st.button("Start Again"):
    st.session_state.clear()
    st.page_link("pages/1_Welcome.py")
