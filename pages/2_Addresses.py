import streamlit as st

st.markdown("""
    <style>
        /* Hide Streamlit’s default sidebar */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Expand main content to full width */
        div[data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)



lang = st.session_state.get("language", "en")

if "addresses" not in st.session_state:
    st.session_state["addresses"] = []

st.title("Client Addresses")

count = st.number_input("How many addresses do you want to enter?", min_value=1, max_value=10, step=1)

temp_addresses = []

for i in range(count):
    addr = st.text_input(f"Address {i+1}")
    temp_addresses.append(addr)

if st.button("Save and continue →", type="primary"):
    st.session_state["addresses"] = [a for a in temp_addresses if a.strip() != ""]
    st.page_link("pages/3_Gates.py")
