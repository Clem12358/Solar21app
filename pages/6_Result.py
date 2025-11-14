import streamlit as st
import pandas as pd

st.title("Final Results – Solar21 Property Evaluation")

# -----------------------------
# Retrieve all stored data
# -----------------------------
passed_addresses = st.session_state.get("passed_addresses", [])

A1 = st.session_state.get("A1_scores", {})
A2 = st.session_state.get("A2_scores", {})
A3 = st.session_state.get("A3_scores", {})

B = st.session_state.get("blockB_scores", {})

sonnendach = st.session_state.get("sonnendach_results", [])

if not passed_addresses:
    st.error("No passed addresses found. Please start again.")
    st.stop()

# -------------------------------------------------------
# Weighting Model — transparent & balanced
# -------------------------------------------------------
WEIGHT_A = 0.40   # Block A total
WEIGHT_B = 0.40   # Block B total

W_A = WEIGHT_A / 3     # A1, A2, A3 (each ~0.133)
W_B = WEIGHT_B / 3     # B1, B2, B3 (each ~0.133)

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

    score_price = B_addr.get("price_score", 0)
    score_stability = B_addr.get("stability_score", 0)
    score_legal = B_addr.get("legal_score", 0)

    score_B_total = (
        score_price * W_B +
        score_stability * W_B +
        score_legal * W_B
    )

    # Final weighted score across blocks
    final_score = round(score_A_total + score_B_total, 3)

    # ---------------------
    # Construct output row
    # ---------------------
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
        "B Price": score_price,
        "B Stability": score_stability,
        "B Legal": score_legal,

        # Final weighted score
        "Final Score": final_score,
    })

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
    f"🏆 **Top Recommendation: {best['Address']}**\n\n"
    f"- Roof Area: **{best['Roof Area (m²)']} m²**\n"
    f"- PV Potential: **{best['PV Potential (kWh)']} kWh/year**\n"
    f"- Canton: **{best['Canton']}**\n"
    f"- Electricity Price: **{best['Electricity Price (CHF/kWh)']} CHF/kWh**\n"
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
