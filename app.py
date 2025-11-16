import streamlit as st
from pathlib import Path
from modules.sonnendach import get_sonnendach_info

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Solar21 Evaluation Tool",
)

PRIMARY_GREEN = "#00E20C"
PRIMARY_DARK = "#000000"

# -------------------------------------------------------
# GLOBAL CSS OVERRIDES
# -------------------------------------------------------
st.markdown(f"""
<style>

/* --- FORCE WHITE THEME EVEN IF BROWSER IS DARK MODE --- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: white !important;
    color: black !important;
}}

/* Hide sidebar */
[data-testid="stSidebar"], [data-testid="stSidebarNav"] {{
    display: none !important;
}}

/* Container */
.block-container {{
    padding-top: 2.5rem !important;
    max-width: 1350px !important;
}}

/* Headings */
h1, h2, h3, h4, h5 {{
    color: black !important;
    font-weight: 800 !important;
}}

/* Buttons */
.stButton>button {{
    background-color: {PRIMARY_GREEN} !important;
    color: black !important;
    border-radius: 999px !important;
    padding: 0.7rem 2.4rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    border: none !important;
}}
.stButton>button:hover {{
    background-color: #00C60A !important;
}}

/* Language cards */
.lang-card {{
    border: 2px solid #e5e5e5;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    font-size: 1.35rem;
    font-weight: 600;
    cursor: pointer;
    background-color: white;
    transition: all 0.15s ease;
    color: black;
    margin-top: 12px;
}}
.lang-card:hover {{
    border-color: {PRIMARY_GREEN};
    background-color: #f2fff3;
}}
.lang-selected {{
    border-color: {PRIMARY_GREEN} !important;
    background-color: #eaffea !important;
}}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOGO (always visible, centered)
# -------------------------------------------------------
st.markdown(
    """
    <div style="width:100%; display:flex; justify-content:center; margin-top:10px; margin-bottom:15px;">
        <img src="solar21_logo.png" style="width:180px; height:auto;">
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
def goto(page):
    st.session_state["page"] = page

def init_state():
    defaults = {
        "page": "lang",
        "addresses": [],
        "current_index": 0,
        "answers": {},
        "lang_choice": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -------------------------------------------------------
# PAGE 1 — LANGUAGE
# -------------------------------------------------------
def page_lang():

    st.markdown("<h1>Solar21 Pre-Check</h1>", unsafe_allow_html=True)
    st.markdown("### Choose your language")

    selected = st.session_state.get("lang_choice")

    c1, c2, c3 = st.columns(3)

    # English
    with c1:
        clicked = st.button("🇬🇧 English", key="btn_en")
        st.markdown(
            f"<div class='lang-card {'lang-selected' if selected=='en' else ''}'>🇬🇧 English</div>",
            unsafe_allow_html=True,
        )
        if clicked:
            st.session_state["lang_choice"] = "en"
            goto("address_entry")

    # French
    with c2:
        clicked = st.button("🇫🇷 Français", key="btn_fr")
        st.markdown(
            f"<div class='lang-card {'lang-selected' if selected=='fr' else ''}'>🇫🇷 Français</div>",
            unsafe_allow_html=True,
        )
        if clicked:
            st.session_state["lang_choice"] = "fr"
            goto("address_entry")

    # German
    with c3:
        clicked = st.button("🇩🇪 Deutsch", key="btn_de")
        st.markdown(
            f"<div class='lang-card {'lang-selected' if selected=='de' else ''}'>🇩🇪 Deutsch</div>",
            unsafe_allow_html=True,
        )
        if clicked:
            st.session_state["lang_choice"] = "de"
            goto("address_entry")


# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------
def compute_roof_score(area):
    if area is None:
        return None
    if area > 1000:
        return 3
    elif area > 500:
        return 2
    return 1

def back_button(target_page):
    st.markdown("---")
    if st.button("← Back"):
        goto(target_page)

def restart_button():
    st.markdown("---")
    if st.button("Start again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()

# -------------------------------------------------------
# PAGE 2 — ENTER ADDRESSES
# -------------------------------------------------------
def page_address_entry():

    st.title("Project Sites — Addresses")

    if st.button("+ Add another address"):
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None,
        })

    if len(st.session_state["addresses"]) == 0:
        st.session_state["addresses"].append({
            "address": "",
            "canton": "",
            "roof_area": None,
            "roof_pitch": None,
            "roof_orientation": None,
        })

    for idx, entry in enumerate(st.session_state["addresses"]):
        st.markdown(f"### Address {idx+1}")

        entry["address"] = st.text_input(
            f"Full address for site {idx+1}",
            value=entry["address"],
            key=f"addr_{idx}"
        )

        canton_list = ["", "ZH", "SG", "VD", "BE", "GE", "TI", "VS", "LU", "FR", "AG", "BL",
                       "BS", "TG", "SO", "NE", "SH", "ZG", "OW", "NW", "UR", "GL", "AI", "AR", "JU"]

        entry["canton"] = st.selectbox(
            "Canton",
            canton_list,
            index=0 if entry["canton"] == "" else canton_list.index(entry["canton"]),
            key=f"canton_{idx}"
        )

        if st.button(f"Fetch rooftop info (site {idx+1})"):
            with st.spinner("Contacting Sonnendach..."):
                data = get_sonnendach_info(entry["address"])
                if data:
                    entry["roof_area"] = data.get("roof_area")
                    entry["roof_pitch"] = data.get("pitch")
                    entry["roof_orientation"] = data.get("orientation")
                    st.success("Rooftop data loaded.")
                else:
                    st.error("Could not retrieve rooftop data.")

        if entry["roof_area"]:
            st.write(f"Rooftop area detected: **{entry['roof_area']} m²**")

        st.markdown("---")

    if st.button("Save & continue →"):
        for e in st.session_state["addresses"]:
            if e["address"].strip() == "" or e["canton"].strip() == "":
                st.error("Each site must have an address and a canton.")
                return
        st.session_state["current_index"] = 0
        goto("questions")

    back_button("lang")


# -------------------------------------------------------
# PAGE 3 — QUESTIONS
# -------------------------------------------------------
def page_questions():

    idx = st.session_state["current_index"]
    site = st.session_state["addresses"][idx]
    prefix = f"a{idx}_"

    address = site["address"]
    canton = site["canton"]

    st.title(f"Site Evaluation — {address} ({canton})")

    owner_type = st.radio(
        "### Owner type",
        [
            "3 — Public / institutional / large groups",
            "2 — Standard commercial owner",
            "1 — Private individual or SME",
        ],
        key=prefix + "owner"
    )

    esg = st.radio(
        "### ESG visibility",
        ["Yes", "IDK", "No"],
        key=prefix + "esg"
    )

    st.markdown("### Electricity consumption profile")

    daytime = st.slider(
        "Share of yearly electricity consumed between 08:00–18:00",
        0, 100, 60,
        key=prefix + "daytime"
    )

    spend = st.radio(
        "Estimated annual electricity spend (CHF)",
        ["<100k", "100–300k", "300–800k", ">800k"],
        key=prefix + "spend"
    )

    season = st.radio(
        "Seasonal variation of electricity use",
        ["Low (±10%)", "Moderate (±10–25%)", "High (>25%)"],
        key=prefix + "season"
    )

    loads = st.radio(
        "24/7 loads?",
        ["Yes", "No"],
        key=prefix + "247"
    )

    st.session_state["answers"][idx] = {
        "owner_type": owner_type,
        "esg": esg,
        "daytime": daytime,
        "spend": spend,
        "season": season,
        "loads": loads,
        "roof_score": compute_roof_score(site["roof_area"]),
    }

    st.markdown("---")
    c1, c2 = st.columns(2)

    if idx > 0:
        if c1.button("← Back"):
            st.session_state["current_index"] -= 1

    if c2.button("Continue →"):
        if idx < len(st.session_state["addresses"]) - 1:
            st.session_state["current_index"] += 1
        else:
            goto("results")


# -------------------------------------------------------
# PAGE 4 — RESULTS
# -------------------------------------------------------
def page_results():

    st.title("Final Results — Solar21 Evaluation")

    for idx, site in enumerate(st.session_state["addresses"]):
        a = st.session_state["answers"].get(idx, {})
        st.markdown(f"## {site['address']} ({site['canton']})")
        st.write(f"**Roof score:** {a.get('roof_score')}")
        st.write(f"**Owner type:** {a.get('owner_type')}")
        st.write(f"**ESG:** {a.get('esg')}")
        st.write(f"**Spend:** {a.get('spend')}")
        st.markdown("---")

    restart_button()

# -------------------------------------------------------
# ROUTER
# -------------------------------------------------------
if st.session_state["page"] == "lang":
    page_lang()
elif st.session_state["page"] == "address_entry":
    page_address_entry()
elif st.session_state["page"] == "questions":
    page_questions()
elif st.session_state["page"] == "results":
    page_results()
