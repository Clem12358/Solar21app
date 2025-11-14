import streamlit as st
import pandas as pd

st.title("Final Results – Solar21 Property Evaluation")

# -----------------------------
# Retrieve all stored session data
# -----------------------------
passed_addresses = st.session_state.get("passed_addresses", [])
sonnendach_data = st.session_state.get("sonnendach_results", [])
blockA = st.session_state.get("blockA_scores", {})
blockB = st.session_state.get("blockB_scores", {})

if not passed_addresses:
    st.error("No passed addresses found. Please start again.")
    st.stop()

# -----------------------------
# Build consolidated dataframe
# -----------------------------
rows = []

for item in passed_addresses:
    address = item["address"]

    A = blockA.get(address, {})
    B = blockB.get(address, {})

    # Compute a final score (simple model: equal weights)
    final_score = (
        A.get("rooftype_score", 0) +
        A.get("neighbor_score", 0) +
        A.get("partner_score", 0) +
        B.get("consumption_score", 0) +
        B.get("tariff_score", 0) +
        B.get("payback_score", 0)
    )

    row = {
        "Address": address,
        "Roof Area (m²)": item.get("surface_area_m2"),
        "PV Potential (kWh)": item.get("pv_full_kwh"),
        "Pitch (°)": item.get("roof_pitch_deg"),
        "Heading (°)": item.get("roof_heading_deg"),
        "Canton": item.get("canton"),
        "Canton Electricity Price (Rp/kWh)": item.get("canton_price"),
        # ----- Block A -----
        "A_RoofType": A.get("rooftype_score"),
        "A_Neighbors": A.get("neighbor_score"),
        "A_PartnerFit": A.get("partner_score"),
        # ----- Block B -----
        "B_Consumption": B.get("consumption_score"),
        "B_Tariff": B.get("tariff_score"),
        "B_Payback": B.get("payback_score"),
        # Final
        "Final Score": final_score,
    }
    rows.append(row)

df = pd.DataFrame(rows)
df = df.sort_values("Final Score", ascending=False)

# -----------------------------
# Display results
# -----------------------------
st.subheader("Ranking of All Valid Properties")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Best match
# -----------------------------
best = df.iloc[0]

st.success(
    f"🏆 **Top Recommendation:** **{best['Address']}**\n\n"
    f"- Roof: **{best['Roof Area (m²)']} m²**\n"
    f"- PV potential: **{best['PV Potential (kWh)']} kWh/year**\n"
    f"- Electricity price: **{best['Canton Electricity Price (Rp/kWh)']} Rp/kWh**\n"
    f"- Final Score: **{best['Final Score']}**"
)

# -----------------------------
# Download CSV
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
