import streamlit as st
from pathlib import Path
import base64

def apply_styles():
    asset = Path(__file__).resolve().parents[1] / "assets" / "dashboard_ai.png"
    image_b64 = base64.b64encode(asset.read_bytes()).decode("ascii") if asset.exists() else ""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --bg:#080b14; --panel:rgba(18,23,39,.84); --line:rgba(148,163,184,.14); --muted:#8c96ad; --text:#edf1fb; --purple:#9b7bff; --cyan:#65d5ef; }
    html, body, [data-testid="stAppViewContainer"] { background: radial-gradient(ellipse at 72% 0%, rgba(80,57,145,.17), transparent 36%), #080b14; color:var(--text); font-family:'DM Sans',sans-serif; }
    [data-testid="stHeader"] { background:rgba(8,11,20,.75); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0e1220,#090c15); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div { padding-top:1.2rem; }
    .brand {display:flex;gap:12px;align-items:center;padding:7px 4px 18px}
    .brand-mark {width:43px;height:43px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#8d6aff,#4b86d9);box-shadow:0 0 24px #8062ff55;font-size:23px;color:white}
    .brand-name {font:800 19px Manrope;color:#f5f4ff;letter-spacing:-.6px}.brand-name span{color:#a88cff}
    .brand-sub,.side-label {font-size:9px;letter-spacing:1.5px;color:#7e89a3;font-weight:700}
    .side-label {margin:8px 0 10px}
    [data-testid="stRadio"] label {color:#aab3c8!important;font-size:13px!important;border-radius:10px;padding:3px 7px}
    [data-testid="stRadio"] label:hover {background:#ffffff0b;color:#fff!important}
    [data-testid="stRadio"] [aria-checked="true"] + div {color:#fff}
    .sidebar-status {margin-top:16px;padding:10px;border:1px solid var(--line);border-radius:11px;color:#aab3c8;font-size:11px;background:#ffffff06}
    .status-dot {display:inline-block;width:7px;height:7px;background:#54d6a1;border-radius:50%;margin-right:7px;box-shadow:0 0 9px #54d6a1}
    .topline {font-size:9px;letter-spacing:1.6px;color:#74809a;margin:2px 0 22px;font-weight:700}.topline-sep{padding:0 8px;color:#414b62}.topline-right{float:right;color:#626e85}
    h1,h2,h3 {font-family:Manrope,sans-serif!important;letter-spacing:-.7px}
    h1 {font-size:34px!important;color:#f6f7ff!important;font-weight:800!important}
    h2 {font-size:23px!important;color:#f2f4ff!important}
    h3 {font-size:16px!important;color:#e8ecfa!important}
    p,li {color:#b1bad0}
    .eyebrow {font-size:10px;letter-spacing:1.8px;color:#a991ff;font-weight:700;text-transform:uppercase}
    .muted {color:#8994ad;font-size:12px}
    .hero {border:1px solid rgba(160,139,255,.2);border-radius:22px;padding:27px 30px;background:linear-gradient(105deg,rgba(24,27,48,.97),rgba(19,24,43,.78)),url('data:image/png;base64,{image_b64}');background-size:cover;background-position:center;box-shadow:0 15px 60px #0005;position:relative;overflow:hidden}
    .hero h1 {margin:7px 0 8px}.hero p {max-width:620px;line-height:1.65}
    .glass-card {background:linear-gradient(145deg,rgba(24,30,49,.88),rgba(14,19,32,.9));border:1px solid var(--line);border-radius:17px;padding:18px 19px;box-shadow:0 12px 35px #0002;transition:transform .2s,border-color .2s}
    .glass-card:hover {transform:translateY(-3px);border-color:#9b7bff66}
    .metric-label {font-size:11px;color:#8e9ab3;letter-spacing:.4px}.metric-value {font:800 29px Manrope;color:#f5f6ff;margin:6px 0}.metric-foot {font-size:10px;color:#7e8aa4}
    .feature-card {height:145px}.feature-icon {font-size:20px;color:#b49cff;margin-bottom:13px}.feature-title {font-weight:700;color:#eef1ff;font-size:14px}.feature-desc{font-size:11px;color:#8e9ab3;line-height:1.5;margin-top:6px}
    .section-head {display:flex;justify-content:space-between;align-items:end;margin:25px 0 12px}
    .stButton>button {border:1px solid #7863cb;background:linear-gradient(120deg,#7458d7,#4d70b7);color:white;border-radius:10px;padding:.55rem 1rem;font-weight:700;transition:all .2s}
    .stButton>button:hover {border-color:#b49cff;box-shadow:0 0 20px #806aff55;transform:translateY(-1px)}
    .stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"],.stNumberInput input {background:#111829!important;border:1px solid #303b54!important;color:#edf1fb!important;border-radius:10px!important}
    [data-testid="stFileUploader"] {background:#111829;border:1px dashed #47516a;border-radius:12px}
    [data-testid="stMetric"] {background:#12182a;border:1px solid var(--line);padding:13px;border-radius:14px}
    [data-testid="stMetricValue"] {color:#f5f5ff}
    [data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:12px}
    .stTabs [data-baseweb="tab-list"] {gap:8px}.stTabs [data-baseweb="tab"] {background:#111829;border-radius:9px;color:#aeb8cc;padding:8px 14px}
    .stAlert {border-radius:12px}
    hr {border-color:var(--line)!important}
    .risk-wrap {background:#171d2d;border:1px solid var(--line);border-radius:15px;padding:17px}
    .risk-track {height:9px;background:#30384b;border-radius:9px;overflow:hidden;margin:12px 0}
    .risk-fill {height:100%;border-radius:9px;background:linear-gradient(90deg,#4bd4a2,#f2c35d,#ef6c83)}
    .activity-row {padding:11px 0;border-bottom:1px solid #ffffff0d}
    .activity-row:last-child{border-bottom:0}
    .stCaption, small {color:#7f8aa2!important}
    </style>
    """, unsafe_allow_html=True)
