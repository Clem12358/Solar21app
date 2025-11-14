# pages/2_Addresses.py
import streamlit as st

# ----------------------------
# CONFIG / CONSTANTS
# ----------------------------
NEXT_PAGE = "pages/3_Sonnendach.py"   # <-- ADJUST THIS to your real next page

st.markdown("""
    <style>
    .stPageLink {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

st.title("Client Addresses")

# ----------------------------
# PROTECT AGAINST DIRECT NAVIGATION
# ----------------------------
lang = st.session_state.get("language")
if lang is None:
    # User came here without choosing a language
    st.warning("Please select your language first.")
    st.switch_page("app.py")

# ----------------------------
# INITIALISE STATE
# ----------------------------
if "addresses" not in st.session_state:
    st.session_state["addresses"] = []

# ----------------------------
# HOW MANY ADDRESSES?
# ----------------------------
current_len = max(1, len(st.session_state["addresses"]))
num_addresses = st.number_input(
    "How many addresses do you want to enter?",
    min_value=1,
    max_value=20,
    step=1,
    value=current_len,
)

# Resize the internal list to match the number of addresses
addresses = st.session_state["addresses"]
if len(addresses) < num_addresses:
    addresses += [""] * (num_addresses - len(addresses))
elif len(addresses) > num_addresses:
    addresses = addresses[:num_addresses]
st.session_state["addresses"] = addresses

# ----------------------------
# ADDRESS INPUT FORM
# ----------------------------
with st.form("address_form"):
    for i in range(num_addresses):
        st.session_state["addresses"][i] = st.text_input(
            f"Address {i+1}",
            st.session_state["addresses"][i],
            key=f"address_{i}",
            placeholder="Brunnenggstrasse 9 9000 St. Gallen",
        )

    submitted = st.form_submit_button("Save and continue →")

# ----------------------------
# HANDLE SUBMIT
# ----------------------------
if submitted:
    # Clean and validate
    cleaned = [a.strip() for a in st.session_state["addresses"] if a.strip()]

    if not cleaned:
        st.error("Please enter at least one valid address.")
    else:
        st.session_state["addresses"] = cleaned
        # You may also want to clear later-stage results here if user edits addresses
        # st.session_state.pop("passed_addresses", None)

        # Go to the next step in the flow (technical / Sonnendach step)
        st.switch_page(NEXT_PAGE)
