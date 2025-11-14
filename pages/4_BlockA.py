import streamlit as st

st.markdown("""
    <style>
    .stPageLink {display: none !important;}
    </style>
    """, unsafe_allow_html=True)


st.title("Block A — Owner ROI & Impact (40%)")

# ----------------------------
# PROTECT AGAINST DIRECT NAVIGATION
# ----------------------------
passed_addresses = st.session_state.get("passed_addresses")
if not passed_addresses:
    st.error("No valid properties found. Please restart from the beginning.")
    st.stop()

st.write("We now evaluate the financial attractiveness and ESG potential of the remaining properties.")

# =====================================================
# A1 — Scale Economies (Roof Size) — SEGMENT LEVEL
# =====================================================
st.subheader("A1. Scale Economies (Roof Size Category) — 33%")

st.write("""
This score is based on the **average roof size** across all properties 
that passed the previous screening — not per-address.

Average roof size categories:
- **Large segment**: ≥ 3000 m² → Score **3**
- **Medium segment**: 1000–2999 m² → Score **2**
- **Small segment**: < 1000 m² → Score **1**
""")

# Calculate average roof area from passed addresses
roof_areas = [float(item.get("surface_area_m2") or 0) for item in passed_addresses]
avg_roof_area = sum(roof_areas) / len(roof_areas)

if avg_roof_area >= 3000:
    A1_score = 3
    segment_label = "Large"
elif avg_roof_area >= 1000:
    A1_score = 2
    segment_label = "Medium"
else:
    A1_score = 1
    segment_label = "Small"

st.info(
    f"Average roof size across passed properties: **{round(avg_roof_area,1)} m²** → "
    f"**{segment_label} segment** → Score **{A1_score}**"
)

# Save as a single scalar
st.session_state["A1_score_segment"] = A1_score


# ===============================
# A2 — Owner Cost of Capital
# ===============================
st.subheader("A2. Owner Cost of Capital (WACC proxy) — 33%")

st.write("""
Choose the type of owner per address:
- **3 = Low-WACC** (municipalities, hospitals, co-ops, listed funds)
- **2 = Medium-WACC** (institutional private owners)
- **1 = High-WACC** (SMEs or private individuals)
""")

A2_scores = {}

for item in passed_addresses:
    addr = item["address"]

    value = st.radio(
        f"Owner category for **{addr}**",
        [3, 2, 1],
        index=0,
        key=f"A2_{addr}"
    )
    A2_scores[addr] = int(value)


# ===============================
# A3 — ESG relevance
# ===============================
st.subheader("A3. ESG / Public Visibility — 33%")

st.write("""
Score mapping:
- **Yes → 3**
- **IDK → 2**
- **No → 1**
""")

A3_scores = {}
score_map = {"Yes": 3, "IDK": 2, "No": 1}

for item in passed_addresses:
    addr = item["address"]

    choice = st.radio(
        f"ESG relevance for **{addr}**",
        ["Yes", "IDK", "No"],
        index=1,
        key=f"A3_{addr}"
    )

    A3_scores[addr] = int(score_map[choice])


# ----------------------------
# Save results
# ----------------------------
st.session_state["A2_scores"] = A2_scores
st.session_state["A3_scores"] = A3_scores

st.success("Block A scores saved.")

if st.button("Continue to Block B →", type="primary"):
    st.switch_page("5_BlockB")



