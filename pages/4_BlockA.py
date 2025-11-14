import streamlit as st

st.title("Block A — Owner ROI & Impact (40%)")

# ----------------------------
# PROTECT AGAINST DIRECT NAVIGATION
# ----------------------------
passed_addresses = st.session_state.get("passed_addresses")
if not passed_addresses:
    st.error("No valid properties found. Please restart from the beginning.")
    st.stop()

st.write("We now evaluate the financial attractiveness and ESG potential of the remaining properties.")

# ===============================
# A1 — Scale Economies (Roof Size)
# ===============================
st.subheader("A1. Scale Economies (Roof Size Category) — 33%")

st.write("""
Roof size categories (from Sonnendach):
- **Large roofs**: ≥ 3000 m² → Score **3**
- **Medium roofs**: 1000–2999 m² → Score **2**
- **Small roofs**: < 1000 m² → Score **1**
""")

A1_scores = {}

for item in passed_addresses:
    addr = item["address"]
    roof_area = float(item.get("surface_area_m2") or 0)

    if roof_area >= 3000:
        score = 3
        category = "Large"
    elif roof_area >= 1000:
        score = 2
        category = "Medium"
    else:
        score = 1
        category = "Small"

    A1_scores[addr] = int(score)  # numeric guarantee
    st.write(f"**{addr}** → {roof_area} m² → **{category} roof** → Score **{score}**")


# ===============================
# A2 — Owner Cost of Capital
# ===============================
st.subheader("A2. Owner Cost of Capital (WACC proxy) — 33%")

st.write("""
Choose the type of owner:
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
    A2_scores[addr] = int(value)  # numeric guarantee


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

    A3_scores[addr] = int(score_map[choice])  # numeric guarantee


# ----------------------------
# Save results
# ----------------------------
st.session_state["A1_scores"] = A1_scores
st.session_state["A2_scores"] = A2_scores
st.session_state["A3_scores"] = A3_scores

st.success("Block A scores saved.")

if st.button("Continue to Block B →", type="primary"):
    st.page_link("pages/5_BlockB.py")
