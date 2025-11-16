import streamlit as st
from modules.sonnendach import get_sonnendach_info
from modules.geocoder import geocode_address

st.set_page_config(layout="wide", page_title="Solar21 Evaluation Tool")

# -----------------------------
# Helpers
# -----------------------------

def goto(page):
    st.session_state["page"] = page

def init_state():
    defaults = {
        "page": "lang",       # first page
        "addresses": [],
        "current_index": 0,
        "answers": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# Compute A1 roof score silently
def compute_roof_score(roof_area):
    if roof_area is None:
        return None
    if roof_area > 1000:
        return 3
    elif roof_area > 500:
        return 2
    else:
        return 1

# -----------------------------
# UI components
# -----------------------------

def back_button(target):
    st.markdown("---")
    if st.button("← Back"):
        goto(target)

def restart_button():
    st.markdown("---")
    if st.button("Start again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()

# -----------------------------
# Page: Language choice
# -----------------------------

def page_lang():
    st.title("Choose your language")
    lang = st.radio("", ["English"], index=0)
    if st.button("Continue"):
        goto("address_entry")

# -----------------------------
# Page: Address entry
# -----------------------------

def page_address_entry():
    st.title("Project sites — enter addresses")

    if st.button("+ Add another address"):
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None
        })

    # If no addresses yet, create the first
    if len(st.session_state["addresses"]) == 0:
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None
        })

    for idx, entry in enumerate(st.session_state["addresses"]):
        st.markdown(f"### Address {idx+1}")

        entry["address"] = st.text_input(
            f"Enter the full address for site {idx+1}",
            value=entry["address"],
            key=f"addr_{idx}"
        )

        entry["canton"] = st.selectbox(
            "Select canton",
            ["", "ZH", "SG", "VD", "BE", "GE", "TI", "VS", "LU", "FR", "AG", "BL", "BS", "TG", "SO", "NE", "SH", "ZG", "OW", "NW", "UR", "GL", "AI", "AR", "JU"],
            index=0 if entry["canton"] == "" else ["","ZH","SG","VD","BE","GE","TI","VS","LU","FR","AG","BL","BS","TG","SO","NE","SH","ZG","OW","NW","UR","GL","AI","AR","JU"].index(entry["canton"]),
            key=f"canton_{idx}"
        )

        if st.button(f"Fetch rooftop data for address {idx+1}"):
            with st.spinner("Fetching rooftop suitability…"):
                result = get_sonnendach_info(entry["address"])
                if result:
                    entry["roof_area"] = result.get("roof_area")
                    entry["roof_pitch"] = result.get("pitch")
                    entry["roof_orientation"] = result.get("orientation")
                else:
                    st.error("Could not fetch data for this address.")

        if entry["roof_area"] is not None:
            st.success(f"Rooftop data loaded: {entry['roof_area']} m²")

        st.markdown("---")

    if st.button("Save & continue →"):
        # Validate
        for e in st.session_state["addresses"]:
            if e["address"].strip() == "" or e["canton"].strip() == "":
                st.error("Each address must have an address and a canton.")
                return
        st.session_state["current_index"] = 0
        goto("questions")

    back_button("lang")

# -----------------------------
# Page: Full question page for each address
# -----------------------------

def page_questions():
    idx = st.session_state["current_index"]
    addr_data = st.session_state["addresses"][idx]

    address = addr_data["address"]
    canton = addr_data["canton"]
    key_prefix = f"addr_{idx}"

    st.title(f"{address} ({canton})")

    st.markdown("## Owner characteristics")

    # A2 — Owner category
    owner_type = st.radio(
        "**What type of owner is this?**  
This affects investment decisions and deal structure.",
        [
            "3 — Public or large institutional owner (very low cost of capital)",
            "2 — Standard commercial owner",
            "1 — Private individual / SME (higher capital constraints)"
        ],
        key=key_prefix + "_owner"
    )

    # A3 — ESG
    esg = st.radio(
        "**Is the owner visibly engaged in sustainability topics?**  
This can strengthen the case for on-site solar adoption.",
        ["Yes", "IDK", "No"],
        key=key_prefix + "_esg"
    )

    st.markdown("## Consumption profile")

    # B1 — Daytime %
    daytime = st.slider(
        "**Share of electricity consumed during daytime (approx.)**  
Higher daytime consumption increases the value of on-site solar.",
        0, 100, 60,
        key=key_prefix + "_daytime"
    )

    # B2 — Spend
    spend = st.radio(
        "**What is the site's annual electricity spend?**  
Estimate the total yearly cost (CHF).",
        ["<100k", "100–300k", "300–800k", ">800k"],
        key=key_prefix + "_spend"
    )

    # B3 — Seasonality
    season = st.radio(
        "**How seasonal is the load profile?**  
High seasonality reduces the share of solar that can be consumed on-site.",
        ["Low (±10%)", "Moderate (±10–25%)", "High (>25%)"],
        key=key_prefix + "_season"
    )

    # B4 — 24/7 loads
    loads = st.radio(
        "**Does the site have important 24/7 loads (servers, cold storage, etc.)?**",
        ["Yes", "No"],
        key=key_prefix + "_247"
    )

    st.markdown("---")

    # Save answers in a dict
    st.session_state["answers"][idx] = {
        "owner_type": owner_type,
        "esg": esg,
        "daytime": daytime,
        "spend": spend,
        "season": season,
        "loads": loads,
        "roof_score": compute_roof_score(addr_data["roof_area"])
    }

    # Navigation
    cols = st.columns(2)
    if idx > 0:
        if cols[0].button("← Back"):
            st.session_state["current_index"] -= 1

    if cols[1].button("Continue →"):
        if idx < len(st.session_state["addresses"]) - 1:
            st.session_state["current_index"] += 1
        else:
            goto("results")

# -----------------------------
# Page: Final results
# -----------------------------

def page_results():
    st.title("Final Results — Solar21 Evaluation")

    for idx, addr in enumerate(st.session_state["addresses"]):
        st.markdown(f"## {addr['address']} ({addr['canton']})")

        ans = st.session_state["answers"].get(idx, {})
        st.write(f"A1 (Roof scale): {ans.get('roof_score')}")
        st.write(f"A2 (Owner category): {ans.get('owner_type')}")
        st.write(f"A3 (ESG visibility): {ans.get('esg')}")
        st.write(f"B2 Annual spend: {ans.get('spend')}")
        st.markdown("---")

    restart_button()

# -----------------------------
# Router
# -----------------------------

if st.session_state["page"] == "lang":
    page_lang()
elif st.session_state["page"] == "address_entry":
    page_address_entry()
elif st.session_state["page"] == "questions":
    page_questions()
elif st.session_state["page"] == "results":
    page_results()
