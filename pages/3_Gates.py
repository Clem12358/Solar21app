import streamlit as st

st.title("Block 3 — Feasibility Gates")

# Temporary page-level progress indicator (we will move global one later)
st.progress(60)  # 60% complete, adjust as needed

addresses = st.session_state.get("addresses", [])
if not addresses:
    st.error("No addresses found. Please go back and enter at least one.")
    st.stop()

passed = []

st.write("We now check two essential feasibility conditions for each building:")
st.markdown("""
- **Minimum roof area: ≥ 250 m²**  
- **Meaningful daytime electricity demand** (the building must consume electricity during 08:00–18:00)
""")

for item in addresses:
    addr = item["address"]
    roof = float(item.get("surface_area_m2") or 0)

    st.subheader(f"🏢 {addr}")
    st.write(f"Detected roof area: **{roof} m²**")

    # ---- Gate 1: Roof area ----
    roof_ok = roof >= 250
    if not roof_ok:
        st.warning("Roof too small (must be ≥ 250 m²)")

    # ---- Gate 2: Daytime demand question ----
    demand = st.slider(
        f"How much electricity does this building typically use during the day (08:00–18:00)?",
        min_value=0,
        max_value=200,
        value=20,
        help="Estimate the typical daytime consumption. Buildings with no significant daytime use may not be a fit."
    )
    demand_ok = demand >= 10

    if demand_ok and roof_ok:
        passed.append({**item, "day_demand_kwh": demand})
        st.success("This property passes the feasibility gates.")
    else:
        st.error("This property does not pass the minimum feasibility criteria.")

st.write("---")

# ---- If nothing passed ----
if len(passed) == 0:
    st.error("Unfortunately, none of the buildings passed the feasibility gates.")
    st.info(
        "To continue, at least one building must:\n"
        "- Have **250 m² or more** of usable roof\n"
        "- Have **meaningful daytime electricity demand**"
    )

    if st.button("↩️ Try Again"):
        st.page_link("pages/2_Addresses.py")
    st.stop()

# ---- Save results ----
st.session_state["passed_addresses"] = passed

if st.button("Continue to Block A →", type="primary"):
    st.switch_page("pages/4_BlockA.py")
