import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="BigMart Sales Predictor",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================
# THEME TOKENS
# ==========================
NAVY = "#0B1E3D"
ORANGE = "#FF6B35"
TEAL = "#2EC4B6"
YELLOW = "#FFC857"
CREAM = "#F7F4EC"
WHITE = "#FFFFFF"
RED = "#E84855"

OUTLET_COLORS = {
    "Grocery Store": YELLOW,
    "Supermarket Type1": ORANGE,
    "Supermarket Type2": TEAL,
    "Supermarket Type3": NAVY,
}

# ==========================
# GLOBAL CSS
# ==========================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@500;600;700;800&family=Inter:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background-color: {WHITE};
    }}

    h1, h2, h3, .lexend {{
        font-family: 'Lexend', sans-serif;
        letter-spacing: -0.01em;
    }}

    .mono, .receipt, .receipt * {{
        font-family: 'Space Mono', monospace;
    }}

    /* ---------- Header banner ---------- */
    .app-banner {{
        background: linear-gradient(135deg, {NAVY} 0%, #14305c 100%);
        border-radius: 18px;
        padding: 28px 36px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        border: 2px solid {NAVY};
    }}
    .app-banner::before {{
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 180px;
        height: 180px;
        background: {ORANGE};
        border-radius: 50%;
        opacity: 0.15;
    }}
    .app-banner::after {{
        content: "";
        position: absolute;
        bottom: -60px;
        right: 80px;
        width: 120px;
        height: 120px;
        background: {TEAL};
        border-radius: 50%;
        opacity: 0.15;
    }}
    .app-banner h1 {{
        color: {WHITE};
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
    }}
    .app-banner p {{
        color: #C7D2E3;
        margin: 6px 0 0 0;
        font-size: 0.98rem;
    }}
    .tag-pill {{
        display: inline-block;
        background: {ORANGE};
        color: {WHITE};
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 100px;
        letter-spacing: 0.04em;
        margin-bottom: 10px;
        text-transform: uppercase;
    }}

    /* ---------- Price-tag style cards ---------- */
    .price-tag {{
        background: {CREAM};
        border: 2px dashed {NAVY}33;
        border-radius: 14px;
        padding: 16px 18px;
        position: relative;
        height: 100%;
    }}
    .price-tag::before {{
        content: "";
        position: absolute;
        left: -8px;
        top: 50%;
        transform: translateY(-50%);
        width: 14px;
        height: 14px;
        background: {WHITE};
        border-radius: 50%;
        border: 2px solid {NAVY}33;
    }}
    .price-tag .label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {NAVY}99;
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .price-tag .value {{
        font-family: 'Space Mono', monospace;
        font-size: 1.5rem;
        font-weight: 700;
        color: {NAVY};
    }}
    .price-tag .accent {{
        color: {ORANGE};
    }}

    /* ---------- Receipt ---------- */
    .receipt-wrap {{
        display: flex;
        justify-content: center;
        margin: 18px 0 8px 0;
    }}
    .receipt {{
        background: {WHITE};
        width: 100%;
        max-width: 480px;
        padding: 28px 30px 22px 30px;
        box-shadow: 0 14px 40px rgba(11,30,61,0.16);
        border-radius: 4px;
        position: relative;
    }}
    .receipt-zigzag {{
        height: 14px;
        width: 100%;
        max-width: 480px;
        background: linear-gradient(-45deg, {WHITE} 8px, transparent 0), linear-gradient(45deg, {WHITE} 8px, transparent 0);
        background-size: 16px 16px;
        background-position: left bottom;
        background-repeat: repeat-x;
        background-color: transparent;
        margin: 0 auto;
        filter: drop-shadow(0 4px 6px rgba(11,30,61,0.12));
    }}
    .receipt .store-line {{
        text-align: center;
        font-weight: 700;
        font-size: 1.05rem;
        color: {NAVY};
        letter-spacing: 0.08em;
        margin-bottom: 2px;
    }}
    .receipt .sub-line {{
        text-align: center;
        font-size: 0.7rem;
        color: {NAVY}88;
        margin-bottom: 14px;
    }}
    .receipt hr {{
        border: none;
        border-top: 1px dashed {NAVY}55;
        margin: 12px 0;
    }}
    .receipt .row {{
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: {NAVY};
        margin: 5px 0;
    }}
    .receipt .row .k {{
        color: {NAVY}99;
    }}
    .receipt .total-row {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-top: 14px;
    }}
    .receipt .total-label {{
        font-size: 0.95rem;
        font-weight: 700;
        color: {NAVY};
    }}
    .receipt .total-value {{
        font-size: 1.9rem;
        font-weight: 700;
        color: {ORANGE};
    }}
    .receipt .barcode {{
        margin-top: 16px;
        height: 34px;
        background: repeating-linear-gradient(90deg, {NAVY} 0px, {NAVY} 2px, transparent 2px, transparent 5px);
        opacity: 0.85;
    }}
    .receipt .footer-note {{
        text-align: center;
        font-size: 0.68rem;
        color: {NAVY}77;
        margin-top: 10px;
    }}

    /* ---------- Section eyebrow ---------- */
    .eyebrow {{
        font-family: 'Space Mono', monospace;
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {ORANGE};
        font-weight: 700;
        margin-bottom: 2px;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}
    /* ---------- Sidebar Radio styling as vertical menu tabs ---------- */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
        gap: 10px;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        position: relative !important;
        padding: 12px 18px 12px 24px !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        margin-bottom: 0px !important;
        cursor: pointer !important;
        font-family: 'Lexend', sans-serif;
        font-size: 0.95rem;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: {ORANGE}88 !important;
        transform: translateX(2px);
    }}
    /* Active option styling using modern CSS has selector */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: linear-gradient(135deg, {ORANGE} 0%, #ff8a5c 100%) !important;
        border-color: {ORANGE} !important;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.45) !important;
        font-weight: 600 !important;
        transform: translateX(4px) scale(1.02);
    }}
    /* White left bar indicator for the active item */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked)::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 20%;
        height: 60%;
        width: 4px;
        background-color: {WHITE};
        border-radius: 0 4px 4px 0;
    }}
    /* Thoroughly hide the radio selector circle / dots */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[role="presentation"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[data-testid="stVisualGuidance"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label svg,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label input[type="radio"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {{
        display: none !important;
    }}
    /* Remove default margins/padding added by the hidden circle child */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label * {{
        margin-left: 0px !important;
        padding-left: 0px !important;
    }}

    /* ---------- Buttons ---------- */
    .stButton button {{
        background-color: {ORANGE};
        color: {WHITE};
        border: none;
        border-radius: 10px;
        padding: 10px 26px;
        font-weight: 600;
        font-family: 'Lexend', sans-serif;
        transition: transform 0.08s ease, box-shadow 0.15s ease;
    }}
    .stButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(255,107,53,0.35);
        background-color: {ORANGE};
        color: {WHITE};
    }}

    /* compare card */
    .compare-card {{
        border-radius: 14px;
        padding: 18px 20px;
        background: {CREAM};
        border-left: 6px solid {ORANGE};
        height: 100%;
    }}
    .compare-card .scenario-name {{
        font-weight: 700;
        color: {NAVY};
        font-family: 'Lexend', sans-serif;
        margin-bottom: 6px;
    }}
    .compare-card .scenario-pred {{
        font-family: 'Space Mono', monospace;
        font-size: 1.5rem;
        color: {ORANGE};
        font-weight: 700;
    }}
    .compare-card .scenario-meta {{
        font-size: 0.74rem;
        color: {NAVY}99;
        margin-top: 6px;
        line-height: 1.5;
    }}

    /* badge for winner */
    .winner-badge {{
        display: inline-block;
        background: {TEAL};
        color: {WHITE};
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 100px;
        margin-left: 8px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* insight callout card */
    .insight-card {{
        background-color: {CREAM};
        border-left: 4px solid {ORANGE};
        padding: 14px 18px;
        border-radius: 10px;
        margin-top: 14px;
        margin-bottom: 20px;
        font-size: 0.88rem;
        color: {NAVY};
        line-height: 1.45;
        box-shadow: 0 4px 12px rgba(11,30,61,0.03);
    }}
    .insight-card .insight-title {{
        font-weight: 700;
        font-family: 'Lexend', sans-serif;
        margin-bottom: 5px;
        text-transform: uppercase;
        font-size: 0.76rem;
        letter-spacing: 0.06em;
        color: {ORANGE};
    }}

    /* ---------- Contrast fixes for light background ---------- */
    /* Target widget labels */
    div[data-testid="stWidgetLabel"] p, 
    label[data-testid="stWidgetLabel"] p, 
    label[data-testid="stWidgetLabel"] {{
        color: {NAVY} !important;
        font-weight: 600 !important;
    }}
    
    /* Target headings outside banner */
    h1, h2, h3 {{
        color: {NAVY} !important;
    }}
    
    /* Re-enforce white text on the dark banner */
    .app-banner h1 {{
        color: {WHITE} !important;
    }}
    .app-banner p {{
        color: #C7D2E3 !important;
    }}
    
    /* Target tab labels */
    button[data-testid="stTab"] p {{
        color: {NAVY} !important;
        font-weight: 600 !important;
    }}
    button[data-testid="stTab"][aria-selected="true"] p {{
        color: {ORANGE} !important;
    }}
    
    /* Target slider values, ticks and boundaries */
    div[data-testid="stSlider"] div,
    div[data-testid="stSlider"] span,
    div[data-testid="stSlider"] p {{
        color: {NAVY} !important;
    }}

    /* General markdown elements color override for main page area */
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"] td,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"] th {{
        color: {NAVY};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# LOAD MODEL + DATA
# ==========================
@st.cache_resource
def load_model():
    try:
        return pickle.load(open("models/sales_model.pkl", "rb"))
    except FileNotFoundError:
        return None


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/Train.csv")
        # 1. Clean Fat Content
        df['Item_Fat_Content'] = df['Item_Fat_Content'].replace({
            'LF': 'Low Fat',
            'low fat': 'Low Fat',
            'reg': 'Regular'
        })
        # 2. Impute Zero Visibilities with Item Type mean
        mean_vis = df[df['Item_Visibility'] > 0].groupby('Item_Type')['Item_Visibility'].mean()
        df['Item_Visibility'] = df.apply(
            lambda r: mean_vis[r['Item_Type']] if r['Item_Visibility'] == 0 else r['Item_Visibility'],
            axis=1
        )
        # 3. Extract Parent Categories
        df['Item_Category'] = df['Item_Identifier'].apply(lambda x: x[:2]).map({
            'FD': 'Food',
            'DR': 'Drinks',
            'NC': 'Non-Consumable'
        })
        # 4. Calculate operational years
        df['Outlet_Age'] = 2013 - df['Outlet_Establishment_Year']
        # 5. Categorize MRP into bins
        df['MRP_Bin'] = pd.cut(df['Item_MRP'], bins=[0, 70, 140, 210, np.inf], labels=['Low', 'Medium', 'High', 'Very High'])
        return df
    except FileNotFoundError:
        return None


model = load_model()
df = load_data()

ITEM_TYPES = [
    "Dairy", "Soft Drinks", "Meat", "Fruits and Vegetables",
    "Household", "Baking Goods", "Snack Foods",
]
OUTLET_IDS = ["OUT010", "OUT013", "OUT017"]
OUTLET_SIZES = ["Small", "Medium", "High"]
OUTLET_LOCATIONS = ["Tier 1", "Tier 2", "Tier 3"]
OUTLET_TYPES = ["Grocery Store", "Supermarket Type1", "Supermarket Type2", "Supermarket Type3"]


def run_prediction(payload: dict):
    """Run the model on a single scenario dict and return predicted sales (float)."""
    # Create a copy so we do not mutate the input dict
    payload = payload.copy()
    
    # Map Item_Type to broad Item_Category (needed for new model version features)
    item_type_to_category = {
        "Dairy": "Food", "Soft Drinks": "Drinks", "Meat": "Food", 
        "Fruits and Vegetables": "Food", "Household": "Non-Consumable", 
        "Baking Goods": "Food", "Snack Foods": "Food", "Canned": "Food", 
        "Frozen Foods": "Food", "Health and Hygiene": "Non-Consumable", 
        "Hard Drinks": "Drinks", "Others": "Non-Consumable", "Breads": "Food", 
        "Starchy Foods": "Food", "Breakfast": "Food", "Seafood": "Food"
    }
    payload["Item_Category"] = item_type_to_category.get(payload["Item_Type"], "Food")
    
    # Map Item_MRP to MRP_Bin
    mrp = payload["Item_MRP"]
    if mrp <= 70:
        payload["MRP_Bin"] = "Low"
    elif mrp <= 140:
        payload["MRP_Bin"] = "Medium"
    elif mrp <= 210:
        payload["MRP_Bin"] = "High"
    else:
        payload["MRP_Bin"] = "Very High"

    # Try querying the Flask REST API first
    try:
        url = "http://127.0.0.1:5000/predict"
        response = requests.post(url, json=payload, timeout=2)
        if response.status_code == 200:
            result = response.json()
            return float(result["predictions"][0])
    except Exception:
        # Fallback if API is offline
        pass

    if model is None:
        # Demo fallback so the UI is explorable without the real model file
        base = payload["Item_MRP"] * 12 - payload["Item_Visibility"] * 500
        base += {"Small": 0, "Medium": 400, "High": 900}[payload["Outlet_Size"]]
        base += {"Grocery Store": -300, "Supermarket Type1": 200,
                 "Supermarket Type2": 500, "Supermarket Type3": 900}[payload["Outlet_Type"]]
        base += payload["Outlet_Age"] * 5
        return max(base, 50.0)
    
    input_data = pd.DataFrame([payload])
    
    # Dynamically align columns to match model expectations
    if hasattr(model, "feature_names_in_"):
        features = list(model.feature_names_in_)
    else:
        features = [
            'Item_Identifier', 'Item_Weight', 'Item_Fat_Content', 'Item_Visibility',
            'Item_Type', 'Item_MRP', 'Outlet_Identifier', 'Outlet_Establishment_Year',
            'Outlet_Size', 'Outlet_Location_Type', 'Outlet_Type', 'Item_Category',
            'Outlet_Age', 'MRP_Bin'
        ]
        
    for col in features:
        if col not in input_data.columns:
            if col == 'Outlet_Establishment_Year' and 'Outlet_Age' in input_data.columns:
                input_data[col] = 2013 - input_data['Outlet_Age']
            else:
                input_data[col] = np.nan
                
    input_data = input_data[features]
    
    pred = model.predict(input_data)
    return float(np.expm1(pred)[0])


# ==========================
# SIDEBAR INFO & NAV
# ==========================
st.sidebar.markdown("## 🛍️ BigMart")
st.sidebar.caption("Sales Predictor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🔮 Predict", "🆚 Compare", "📈 Analytics", "🧠 About Model"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
if model is None:
    st.sidebar.warning("⚠️ models/sales_model.pkl not found — running on demo formula so you can preview the UI.")
if df is None:
    st.sidebar.warning("⚠️ data/Train.csv not found — Analytics page needs this file.")

st.sidebar.markdown(
    f"<div style='font-size:0.72rem; color:#C7D2E3; margin-top:20px;'>Model: XGBoost Regressor<br>Dataset: BigMart Sales</div>",
    unsafe_allow_html=True,
)

# ==========================
# BANNER HELPER
# ==========================
banner_titles = {
    "predict": ("PREDICTION TERMINAL", "BigMart Sales Predictor", "Enter product & outlet details to forecast sales."),
    "compare": ("SCENARIO COMPARISON", "Compare Up To 3 Scenarios", "See how different products and outlets stack up side by side."),
    "analytics": ("STORE INSIGHTS", "Analytics Dashboard", "Historical patterns across products, outlets, and time."),
    "about": ("MODEL SPEC", "About The Model", "What's under the hood, and what data it was trained on."),
}


def render_banner(key: str):
    eyebrow, title, subtitle = banner_titles[key]
    st.markdown(
        f"""
        <div class="app-banner">
            <span class="tag-pill">{eyebrow}</span>
            <h1>🛍️ {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_form(key_prefix=""):
    """Render the product/outlet input widgets, return dict of values."""
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='eyebrow'>PRODUCT</div>", unsafe_allow_html=True)
        item_weight = st.number_input("Item Weight (kg)", value=10.0, min_value=0.0, key=f"{key_prefix}_w")
        item_visibility = st.number_input("Item Visibility", value=0.05, min_value=0.0, max_value=1.0, step=0.01, key=f"{key_prefix}_v")
        item_mrp = st.number_input("Item MRP (₹)", value=100.0, min_value=0.0, key=f"{key_prefix}_mrp")
        item_fat_content = st.selectbox("Item Fat Content", ["Low Fat", "Regular"], key=f"{key_prefix}_fat")
        item_type = st.selectbox("Item Type", ITEM_TYPES, key=f"{key_prefix}_type")
    with c2:
        st.markdown("<div class='eyebrow'>OUTLET</div>", unsafe_allow_html=True)
        outlet_identifier = st.selectbox("Outlet Identifier", OUTLET_IDS, key=f"{key_prefix}_id")
        outlet_size = st.selectbox("Outlet Size", OUTLET_SIZES, key=f"{key_prefix}_size")
        outlet_location_type = st.selectbox("Outlet Location Type", OUTLET_LOCATIONS, key=f"{key_prefix}_loc")
        outlet_type = st.selectbox("Outlet Type", OUTLET_TYPES, key=f"{key_prefix}_otype")
        outlet_age = st.slider("Outlet Age (years)", 1, 40, 10, key=f"{key_prefix}_age")

    return {
        "Item_Weight": item_weight,
        "Item_Visibility": item_visibility,
        "Item_MRP": item_mrp,
        "Item_Fat_Content": item_fat_content,
        "Item_Type": item_type,
        "Outlet_Identifier": outlet_identifier,
        "Outlet_Size": outlet_size,
        "Outlet_Location_Type": outlet_location_type,
        "Outlet_Type": outlet_type,
        "Outlet_Age": outlet_age,
    }


def render_receipt(payload: dict, prediction: float, scenario_label="BIGMART"):
    ts = datetime.now().strftime("%d %b %Y  %H:%M")
    st.markdown(
        f"""
        <div class="receipt-wrap">
            <div class="receipt">
                <div class="store-line">★ {scenario_label} ★</div>
                <div class="sub-line">SALES FORECAST RECEIPT &nbsp;·&nbsp; {ts}</div>
                <hr>
                <div class="row"><span class="k">Item Type</span><span>{payload['Item_Type']}</span></div>
                <div class="row"><span class="k">Fat Content</span><span>{payload['Item_Fat_Content']}</span></div>
                <div class="row"><span class="k">Item MRP</span><span>₹{payload['Item_MRP']:.2f}</span></div>
                <div class="row"><span class="k">Item Weight</span><span>{payload['Item_Weight']:.2f} kg</span></div>
                <div class="row"><span class="k">Visibility</span><span>{payload['Item_Visibility']:.3f}</span></div>
                <hr>
                <div class="row"><span class="k">Outlet</span><span>{payload['Outlet_Identifier']}</span></div>
                <div class="row"><span class="k">Outlet Type</span><span>{payload['Outlet_Type']}</span></div>
                <div class="row"><span class="k">Outlet Size</span><span>{payload['Outlet_Size']}</span></div>
                <div class="row"><span class="k">Location Tier</span><span>{payload['Outlet_Location_Type']}</span></div>
                <div class="row"><span class="k">Outlet Age</span><span>{payload['Outlet_Age']} yrs</span></div>
                <div class="total-row">
                    <span class="total-label">PREDICTED SALES</span>
                    <span class="total-value">₹{prediction:,.2f}</span>
                </div>
                <div class="barcode"></div>
                <div class="footer-note">THANK YOU FOR SHOPPING WITH THE MODEL · NOT A REAL TRANSACTION</div>
            </div>
        </div>
        <div class="receipt-zigzag"></div>
        """,
        unsafe_allow_html=True,
    )


# ==========================
# MAIN ROUTING
# ==========================
if page == "🔮 Predict":
    render_banner("predict")
    payload = render_input_form(key_prefix="predict")

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='price-tag'><div class='label'>Item Weight</div><div class='value'>{payload['Item_Weight']:.2f} kg</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='price-tag'><div class='label'>Fat Content</div><div class='value'>{payload['Item_Fat_Content']}</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='price-tag'><div class='label'>Visibility</div><div class='value'>{payload['Item_Visibility']:.3f}</div></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='price-tag'><div class='label'>Item MRP</div><div class='value accent'>₹{payload['Item_MRP']:.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        predict_clicked = st.button("🔮 Predict Sales", use_container_width=True)

    if predict_clicked:
        prediction = run_prediction(payload)
        render_receipt(payload, prediction)


elif page == "🆚 Compare":
    render_banner("compare")
    n_scenarios = st.radio("How many scenarios?", [2, 3], horizontal=True)

    scenario_tabs = st.tabs([f"Scenario {i+1}" for i in range(n_scenarios)])
    payloads = []
    for i, tab in enumerate(scenario_tabs):
        with tab:
            st.markdown(f"<div class='eyebrow'>SCENARIO {i+1} INPUTS</div>", unsafe_allow_html=True)
            payloads.append(render_input_form(key_prefix=f"cmp{i}"))

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        compare_clicked = st.button("🆚 Run Comparison", use_container_width=True)

    if compare_clicked:
        results = [run_prediction(p) for p in payloads]
        best_idx = int(np.argmax(results))

        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(n_scenarios)
        for i, col in enumerate(cols):
            with col:
                badge = "<span class='winner-badge'>Best</span>" if i == best_idx else ""
                p = payloads[i]
                col.markdown(
                    f"""
                    <div class="compare-card">
                        <div class="scenario-name">Scenario {i+1}{badge}</div>
                        <div class="scenario-pred">₹{results[i]:,.2f}</div>
                        <div class="scenario-meta">
                            {p['Item_Type']} · {p['Item_Fat_Content']}<br>
                            MRP ₹{p['Item_MRP']:.0f} · Outlet {p['Outlet_Identifier']}<br>
                            {p['Outlet_Type']} · {p['Outlet_Size']} · {p['Outlet_Location_Type']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>SIDE-BY-SIDE</div>", unsafe_allow_html=True)

        bar_colors = [ORANGE, TEAL, YELLOW][:n_scenarios]
        fig = go.Figure(
            data=[
                go.Bar(
                    x=[f"Scenario {i+1}" for i in range(n_scenarios)],
                    y=results,
                    marker_color=bar_colors,
                    text=[f"₹{r:,.0f}" for r in results],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            font_family="Inter",
            font_color=NAVY,
            yaxis_title="Predicted Sales (₹)",
            showlegend=False,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # comparison table
        st.markdown("<div class='eyebrow' style='margin-top:10px;'>FULL DETAIL</div>", unsafe_allow_html=True)
        table_rows = []
        for i, p in enumerate(payloads):
            row = {"Scenario": f"Scenario {i+1}", "Predicted Sales (₹)": round(results[i], 2)}
            row.update(p)
            table_rows.append(row)
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)


elif page == "📈 Analytics":
    render_banner("analytics")
    if df is None:
        st.error("data/Train.csv not found. Place the training dataset in the `data/` folder to see analytics.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='price-tag'><div class='label'>Total Records</div><div class='value'>{len(df):,}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='price-tag'><div class='label'>Average Sales</div><div class='value accent'>₹{df['Item_Outlet_Sales'].mean():,.0f}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='price-tag'><div class='label'>Average MRP</div><div class='value'>₹{df['Item_MRP'].mean():,.0f}</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='price-tag'><div class='label'>Average Weight</div><div class='value'>{df['Item_Weight'].mean():.2f} kg</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("<div class='eyebrow'>DISTRIBUTION</div>", unsafe_allow_html=True)
            st.subheader("Sales Distribution")
            fig = px.histogram(df, x="Item_Outlet_Sales", nbins=30, color_discrete_sequence=[ORANGE])
            fig.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_family="Inter", font_color=NAVY, margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                """
                <div class="insight-card">
                    <div class="insight-title">💡 Conclusion / Key Insight</div>
                    The sales distribution is strongly right-skewed. Most transactions/records have low to moderate sales (below ₹2,000), while a small segment of high-demand items or premium outlets generate very high sales (up to ₹10,000+).
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            st.markdown("<div class='eyebrow'>SHARE</div>", unsafe_allow_html=True)
            st.subheader("Sales Contribution by Outlet Type")
            outlet_share = df.groupby("Outlet_Type")["Item_Outlet_Sales"].sum()
            fig = px.pie(
                values=outlet_share.values,
                names=outlet_share.index,
                color=outlet_share.index,
                color_discrete_map=OUTLET_COLORS,
                hole=0.45,
            )
            fig.update_layout(paper_bgcolor=WHITE, font_family="Inter", font_color=NAVY, margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                """
                <div class="insight-card">
                    <div class="insight-title">💡 Conclusion / Key Insight</div>
                    Supermarket Type1 is the primary revenue engine, contributing the majority of total sales. This suggests standard supermarkets form the core business model for volume and reach.
                </div>
                """,
                unsafe_allow_html=True,
            )

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("<div class='eyebrow'>BY OUTLET</div>", unsafe_allow_html=True)
            st.subheader("Average Sales by Outlet Type")
            sales_by_outlet = df.groupby("Outlet_Type")["Item_Outlet_Sales"].mean().sort_values(ascending=False)
            fig = px.bar(
                x=sales_by_outlet.index,
                y=sales_by_outlet.values,
                color=sales_by_outlet.index,
                color_discrete_map=OUTLET_COLORS,
            )
            fig.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_family="Inter", font_color=NAVY, showlegend=False, xaxis_title="", yaxis_title="Avg Sales (₹)", margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                """
                <div class="insight-card">
                    <div class="insight-title">💡 Conclusion / Key Insight</div>
                    Supermarket Type3 has the highest average sales per store, significantly outperforming other formats (especially Grocery Stores). While Type1 has higher total contribution due to count, Type3 stores are individually the most productive.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            st.markdown("<div class='eyebrow'>BY ITEM</div>", unsafe_allow_html=True)
            st.subheader("Average Sales by Item Type")
            top_items = df.groupby("Item_Type")["Item_Outlet_Sales"].mean().sort_values(ascending=False)
            fig = px.bar(
                x=top_items.index,
                y=top_items.values,
                color_discrete_sequence=[TEAL],
            )
            fig.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_family="Inter", font_color=NAVY, xaxis_title="", yaxis_title="Avg Sales (₹)", margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                """
                <div class="insight-card">
                    <div class="insight-title">💡 Conclusion / Key Insight</div>
                    Average sales are consistently high across all standard categories. However, high-value or fast-moving items like Seafood, Starchy Foods, and Fruits and Vegetables lead slightly, indicating strong pricing power in those segments.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='eyebrow'>OVER TIME</div>", unsafe_allow_html=True)
        st.subheader("Sales Trend by Outlet Establishment Year")
        age_sales = df.groupby("Outlet_Establishment_Year")["Item_Outlet_Sales"].mean()
        fig = px.line(x=age_sales.index, y=age_sales.values, markers=True, color_discrete_sequence=[ORANGE])
        fig.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE, font_family="Inter", font_color=NAVY, xaxis_title="Establishment Year", yaxis_title="Avg Sales (₹)", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">💡 Conclusion / Key Insight</div>
                Outlets established in 1985 show the highest average sales, indicating strong brand loyalty, prime location, and store maturity. Conversely, a sharp dip around 1998 suggests that stores opened in that period (often Grocery Stores) underperformed or had limited capacity. Newer supermarkets maintain stable, consistent performance.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ==========================
        # MODEL DIAGNOSTICS & PERFORMANCES
        # ==========================
        if model is not None:
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.markdown("<div class='eyebrow'>MODEL PERFORMANCE & INTERPRETABILITY</div>", unsafe_allow_html=True)
            st.subheader("Model Diagnostic Dashboard")
            
            c_diag1, c_diag2 = st.columns(2)
            
            with c_diag1:
                st.markdown("<div class='eyebrow'>FEATURE IMPORTANCE</div>", unsafe_allow_html=True)
                st.markdown("<p style='font-size:0.85rem; color:#666;'>Relative feature weights in the trained model prediction splits</p>", unsafe_allow_html=True)
                try:
                    # Get the core model estimator
                    estimator = model.named_steps['model']
                    preprocessor = model.named_steps['preprocessor']
                    
                    if hasattr(estimator, 'feature_importances_'):
                        try:
                            feature_names = preprocessor.get_feature_names_out()
                        except:
                            feature_names = [f"Feature {i}" for i in range(len(estimator.feature_importances_))]
                        
                        importances = estimator.feature_importances_
                        feat_imp_df = pd.DataFrame({
                            "Feature": feature_names,
                            "Importance": importances
                        }).sort_values(by="Importance", ascending=True)
                        
                        # Clean feature names
                        feat_imp_df['Feature'] = feat_imp_df['Feature'].apply(lambda x: x.split('__')[-1])
                        
                        fig_imp = px.bar(
                            feat_imp_df.tail(10), 
                            x="Importance", 
                            y="Feature", 
                            orientation="h", 
                            color_discrete_sequence=[ORANGE]
                        )
                        fig_imp.update_layout(
                            plot_bgcolor=WHITE, 
                            paper_bgcolor=WHITE, 
                            font_family="Inter", 
                            font_color=NAVY,
                            xaxis_title="Relative Importance", 
                            yaxis_title="", 
                            margin=dict(t=10, b=10, l=10, r=10),
                            height=350
                        )
                        st.plotly_chart(fig_imp, use_container_width=True)
                except Exception as e:
                    st.info(f"Could not load feature importances: {str(e)}")
            
            with c_diag2:
                st.markdown("<div class='eyebrow'>ACTUAL VS. PREDICTED SALES</div>", unsafe_allow_html=True)
                st.markdown("<p style='font-size:0.85rem; color:#666;'>Actual sales vs. model predictions on a sample of historical records</p>", unsafe_allow_html=True)
                try:
                    # Take sample and drop target
                    sample_df = df.sample(min(400, len(df)), random_state=42)
                    X_sample = sample_df.drop(columns=['Item_Outlet_Sales'])
                    y_actual = sample_df['Item_Outlet_Sales']
                    
                    # Predict
                    y_pred = np.expm1(model.predict(X_sample))
                    
                    scatter_df = pd.DataFrame({
                        "Actual Sales (₹)": y_actual,
                        "Predicted Sales (₹)": y_pred
                    })
                    
                    fig_scatter = px.scatter(
                        scatter_df, 
                        x="Actual Sales (₹)", 
                        y="Predicted Sales (₹)", 
                        opacity=0.6, 
                        color_discrete_sequence=[TEAL]
                    )
                    
                    # Add perfect match diagonal line
                    max_val = max(y_actual.max(), y_pred.max())
                    fig_scatter.add_shape(
                        type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                        line=dict(color=ORANGE, width=2, dash="dash")
                    )
                    
                    fig_scatter.update_layout(
                        plot_bgcolor=WHITE, 
                        paper_bgcolor=WHITE, 
                        font_family="Inter", 
                        font_color=NAVY,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=350
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                except Exception as e:
                    st.info(f"Could not calculate actual vs predicted: {str(e)}")


elif page == "🧠 About Model":
    render_banner("about")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("<div class='eyebrow'>SPECIFICATION</div>", unsafe_allow_html=True)
        st.markdown(
            """
            ### Model Information

            | Field | Value |
            |---|---|
            | Model | XGBoost Regressor |
            | Framework | Scikit-Learn Pipeline |
            | Dataset | BigMart Sales Dataset |
            | Target | `Item_Outlet_Sales` |
            | Target transform | `log1p` → predicted with `expm1` |
            """
        )
        st.markdown(
            """
            ### Features Used
            - Item Weight
            - Item Visibility
            - Item MRP
            - Item Fat Content
            - Item Type
            - Outlet Identifier
            - Outlet Size
            - Outlet Location Type
            - Outlet Type
            - Outlet Age
            """
        )
    with c2:
        st.markdown(
            f"""
            <div class="price-tag" style="margin-bottom:14px;">
                <div class="label">Algorithm</div>
                <div class="value">XGBoost</div>
            </div>
            <div class="price-tag" style="margin-bottom:14px;">
                <div class="label">Pipeline</div>
                <div class="value">scikit-learn</div>
            </div>
            <div class="price-tag">
                <div class="label">Target Encoding</div>
                <div class="value">log1p / expm1</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
