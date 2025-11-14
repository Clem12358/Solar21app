import streamlit as st

addresses = st.session_state.get("addresses", [])

st.title("Pass/Fail Gates")

if not addresses:
    st.error("No addresses found. Go back.")
    st.page_link("pages/2_Addresses.py")

# Placeholder gate results — later replaced with real Sonnendach logic
passed = {addr: True for addr in addresses}  # dummy: all pass

st.session_state["passed_addresses"] = [a for a in addresses if passed[a]]

st.write("Addresses that passed:")
st.write(st.session_state["passed_addresses"])

if st.button("Continue to Block A →", type="primary"):
    st.page_link("pages/4_BlockA.py")
