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

# -----------------------------
# GLOBAL DESIGN OVERRIDES
# -----------------------------
PRIMARY_GREEN = "#00E20C"   # from the logo
PRIMARY_DARK = "#000000"

st.markdown(f"""
<style>

/* Force radio text to be fully black and opaque */
.stRadio label {{
    color: #000000 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}}

.stRadio div[role="radiogroup"] label {{
    color: #000000 !important;
    opacity: 1 !important;
}}


/* Hide sidebar */
[data-testid="stSidebar"], [data-testid="stSidebarNav"] {{
    display: none !important;
}}

/* Full-width container */
.block-container {{
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}}

/* White background + base text */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: #ffffff !important;
    color: #111111 !important;
    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    color: {PRIMARY_DARK} !important;
    font-weight: 700 !important;
}}

/* Section dividers */
hr {{
    border-top: 1px solid #EEEEEE !important;
}}

/* Buttons */
.stButton>button {{
    background-color: {PRIMARY_GREEN} !important;
    color: #000000 !important;
    border-radius: 999px !important;
    padding: 0.6rem 1.8rem !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}}
.stButton>button:hover {{
    background-color: #00C60A !important;
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}}

/* Radios + labels */
.stRadio > label {{
    font-weight: 600 !important;
    color: #111111 !important;
}}
.stRadio div[role="radiogroup"] label {{
    color: #111111 !important;
    font-size: 1.02rem !important;
}}

/* Accent color for radio + slider */
input[type="radio"], input[type="range"] {{
    accent-color: {PRIMARY_GREEN};
}}

/* Inputs & select boxes */
.stTextInput>div>div>input,
.stSelectbox>div>div>div {{
    border-radius: 0.6rem !important;
    border: 1px solid #DDDDDD !important;
}}
.stSelectbox>label,
.stTextInput>label {{
    font-weight: 600 !important;
    color: #222222 !important;
    margin-bottom: 0.15rem !important;
}}

/* Sliders */
.stSlider > div > div > div {{
    color: #111111 !important;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOGO (smaller & perfectly centered)
# -------------------------------------------------------
logo_path = Path(__file__).parent / "solar21_logo.png"

st.markdown(
    f"""
    <div style="
        width: 100%;
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 10px;
    ">
        <img src="solar21_logo.png" style="width:180px; height:auto;"/>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------------

def goto(page):
    st.session_state["page"] = page

def init_state():
    defaults = {
        "page": "lang",
        "addresses": [],
        "current_index": 0,
        "answers": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# -------------------------------------------------------
# HELPERS
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
# PAGE 1 — LANGUAGE
# -------------------------------------------------------

def page_lang():
    st.markdown(
        "<h1 style='margin-top:1.5rem;'>Choose your language</h1>",
        unsafe_allow_html=True,
    )

    st.radio(
        "",
        ["English"],
        index=0,
        key="lang_choice"
    )

    st.markdown("")  # small spacing

    if st.button("Continue →"):
        goto("address_entry")

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
                st.error("Each site must have an address and canton.")
                return
        st.session_state["current_index"] = 0
        goto("questions")

    back_button("lang")

# -------------------------------------------------------
# PAGE 3 — QUESTIONS (ONE PAGE PER ADDRESS)
# -------------------------------------------------------

def page_questions():
    idx = st.session_state["current_index"]
    site = st.session_state["addresses"][idx]

    address = site["address"]
    canton = site["canton"]
    prefix = f"a{idx}_"

    st.title(f"Site Evaluation — {address} ({canton})")

    # OWNER TYPE
    owner_type = st.radio(
        """### Owner type  
Choose the profile that best describes the site owner.""",
        [
            "3 — Public / institutional / large groups (very low cost of capital)",
            "2 — Standard commercial owner",
            "1 — Private individual or SME (higher financing constraints)",
        ],
        key=prefix + "owner"
    )

    # ESG
    esg = st.radio(
        """### ESG visibility  
Is the owner known to be engaged in sustainability topics?""",
        ["Yes", "IDK", "No"],
        key=prefix + "esg"
    )

    st.markdown("### Electricity consumption profile")

    # DAYTIME %
    daytime = st.slider(
        """Approximate share of yearly electricity consumed between **08:00–18:00**  
Higher daytime load increases the site's solar attractiveness.""",
        0, 100, 60,
        key=prefix + "daytime"
    )

    # SPEND
    spend = st.radio(
        """Estimated **annual electricity spend (CHF)**  
Choose the bracket that best matches the site's yearly cost.""",
        ["<100k", "100–300k", "300–800k", ">800k"],
        key=prefix + "spend"
    )

    # SEASONALITY
    season = st.radio(
        """How strong is the **seasonal variation** of electricity use?  
High seasonality reduces self-consumption.""",
        ["Low (±10%)", "Moderate (±10–25%)", "High (>25%)"],
        key=prefix + "season"
    )

    # 24/7
    loads = st.radio(
        """Does the site operate **24/7 loads** (cold rooms, servers, critical processes)?""",
        ["Yes", "No"],
        key=prefix + "247"
    )

    # Save results
    st.session_state["answers"][idx] = {
        "owner_type": owner_type,
        "esg": esg,
        "daytime": daytime,
        "spend": spend,
        "season": season,
        "loads": loads,
        "roof_score": compute_roof_score(site["roof_area"]),
    }

    # NAVIGATION
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
        st.write(f"**A1 – Roof score:** {a.get('roof_score')}")
        st.write(f"**A2 – Owner type:** {a.get('owner_type')}")
        st.write(f"**A3 – ESG visibility:** {a.get('esg')}")
        st.write(f"**Annual spend bracket:** {a.get('spend')}")
        st.markdown("---")

    restart_button()

# -------------------------------------------------------
# ROUTER
# -------------------------------------------------------

page = st.session_state["page"]

if page == "lang":
    page_lang()
elif page == "address_entry":
    page_address_entry()
elif page == "questions":
    page_questions()
elif page == "results":
    page_results()
