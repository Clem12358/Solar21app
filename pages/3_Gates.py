import streamlit as st
from modules.sonnendach import fetch_address_data

st.title("Pass/Fail Gates")

# Retrieve stored addresses
addresses = st.session_state.get("addresses", [])

if not addresses:
    st.error("No addresses found. Please go back and enter them.")
    st.stop()

st.write("We are checking your properties against Solar21’s preliminary criteria.")

results = []
failed_addresses = []
passed_addresses = []

# ---- Gate thresholds ----
MIN_SURFACE_M2 = 250  # equivalent to ~30 kWp usable roof

# ---- Loop through each address ----
for addr in addresses:
    with st.spinner(f"Fetching Sonnendach data for: {addr}"):
        try:
            data = fetch_address_data(addr)
        except Exception as e:
            st.error(f"Couldn't fetch data for {addr}: {e}")
            failed_addresses.append({"address": addr, "reason": "Sonnendach_fetch_error"})
            continue

    # Gate G1: Roof surface must be ≥ 250 m²
    surface = data["surface_area_m2"]
    gate1_pass = surface >= MIN_SURFACE_M2

    # Store gate result
    data["G1_pass"] = gate1_pass

    # Gate G2: Ask user if daytime demand exists
    st.subheader(f"Does this address show meaningful daytime electricity load?")
    daytime = st.radio(
        f"Daytime demand (08:00–18:00) for **{addr}**",
        ["Yes", "No"],
        index=0,
        key=f"daytime_{addr}"
    )

    gate2_pass = (daytime == "Yes")
    data["G2_pass"] = gate2_pass

    # Add to appropriate lists
    results.append(data)

    if gate1_pass and gate2_pass:
        passed_addresses.append(data)
    else:
        failed_addresses.append(data)

# ---- Save results to session ----
st.session_state["sonnendach_results"] = results
st.session_state["passed_addresses"] = passed_addresses
st.session_state["failed_addresses"] = failed_addresses

# ---- Display results ----
st.write("### Gate Results")
st.write("**Passed:**")
for p in passed_addresses:
    st.success(f"✔ {p['address']} — Roof: {p['surface_area_m2']} m²")

st.write("**Failed:**")
for f in failed_addresses:
    st.error(f"✘ {f['address']} — Roof: {f['surface_area_m2']} m² (or failed G2)")

# Summary
if len(addresses) > 0:
    pct = round(len(passed_addresses) / len(addresses) * 100, 1)
    st.write(f"### {pct}% of properties passed the initial gates.")

# Continue button
if len(passed_addresses) > 0:
    if st.button("Continue to Block A →", type="primary"):
        st.page_link("pages/4_BlockA.py")
else:
    st.warning("No properties passed the gates. You cannot continue.")
