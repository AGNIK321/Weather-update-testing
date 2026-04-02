# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")
import os
os.environ["PYTHONWARNINGS"] = "ignore"

import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from datetime import timezone, timedelta

st.set_page_config(
    page_title="Kolkata Rain Intelligence",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Theme State ──────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

is_dark = st.session_state.theme == "dark"

# ─── Theme Variables ──────────────────────────────────────────────────────────
if is_dark:
    T = {
        "page_bg":        "#050c1a",
        "hero_bg":        "linear-gradient(135deg,#050c1a 0%,#0a1f3a 40%,#0d2b52 70%,#091d3a 100%)",
        "hero_border":    "rgba(56,182,255,0.15)",
        "left_bg":        "linear-gradient(180deg,#060e1e 0%,#071020 100%)",
        "left_border":    "rgba(56,182,255,0.1)",
        "right_bg":       "#050c1a",
        "text_primary":   "#ffffff",
        "text_secondary": "#e8f4ff",
        "text_muted":     "rgba(160,210,255,0.55)",
        "text_faint":     "rgba(160,210,255,0.4)",
        "text_label":     "rgba(160,210,255,0.45)",
        "accent":         "#38b6ff",
        "accent_glow":    "rgba(56,182,255,0.4)",
        "accent_bg":      "rgba(56,182,255,0.08)",
        "accent_border":  "rgba(56,182,255,0.18)",
        "card_bg":        "rgba(255,255,255,0.03)",
        "card_border":    "rgba(255,255,255,0.07)",
        "card_hover_bg":  "rgba(56,182,255,0.07)",
        "card_hover_bd":  "rgba(56,182,255,0.25)",
        "now_card_bg":    "linear-gradient(145deg,rgba(56,182,255,0.08),rgba(56,182,255,0.03))",
        "now_card_bd":    "rgba(56,182,255,0.18)",
        "alert_rain_bg":  "linear-gradient(135deg,rgba(56,182,255,0.12),rgba(56,182,255,0.06))",
        "alert_rain_bd":  "rgba(56,182,255,0.3)",
        "alert_rain_tx":  "#b3ddff",
        "alert_dry_bg":   "rgba(255,255,255,0.02)",
        "alert_dry_bd":   "rgba(255,255,255,0.07)",
        "alert_dry_tx":   "rgba(200,220,255,0.5)",
        "sec_line":       "rgba(56,182,255,0.1)",
        "footer_bd":      "rgba(56,182,255,0.08)",
        "footer_tx":      "rgba(160,210,255,0.3)",
        "grid_color":     "rgba(255,255,255,0.04)",
        "tick_color":     "rgba(160,210,255,0.4)",
        "bar_dry":        "rgba(56,182,255,0.12)",
        "bar_wet":        "rgba(56,182,255,0.7)",
        "press_fill":     "rgba(120,60,255,0.05)",
        "press_line":     "rgba(160,100,255,0.6)",
        "press_hover":    "#a06cff",
        "temp_line":      "rgba(255,160,50,0.5)",
        "btn_bg":         "rgba(56,182,255,0.1)",
        "btn_tx":         "#38b6ff",
        "btn_bd":         "rgba(56,182,255,0.3)",
        "cmp_dry_bg":     "rgba(255,255,255,0.02)",
        "cmp_dry_bd":     "rgba(255,255,255,0.07)",
        "cmp_g_bg":       "rgba(66,133,244,0.04)",
        "cmp_g_bd":       "rgba(66,133,244,0.25)",
        "cmp_m_bg":       "rgba(56,182,255,0.04)",
        "cmp_m_bd":       "rgba(56,182,255,0.25)",
        "cmp_stats_bd":   "rgba(255,255,255,0.06)",
        "cs_val_tx":      "#e8f4ff",
        "week_bg":        "rgba(255,255,255,0.02)",
        "week_bd":        "rgba(255,255,255,0.06)",
        "week_hi":        "#e8f4ff",
        "week_lo":        "rgba(160,210,255,0.4)",
        "pcr_track":      "rgba(255,255,255,0.05)",
        "pcr_lbl":        "rgba(160,210,255,0.4)",
        "pcr_val":        "#e8f4ff",
        "meta_tx":        "rgba(160,210,255,0.3)",
        "subtitle_tx":    "rgba(160,210,255,0.6)",
        "toggle_icon":    "☀️",
        "toggle_label":   "Light Mode",
        "toggle_bg":      "rgba(255,220,80,0.1)",
        "toggle_bd":      "rgba(255,220,80,0.3)",
        "toggle_tx":      "#ffd850",
        "hoverlabel_bg":  "#0a1f3a",
        "plot_bg":        "rgba(0,0,0,0)",
    }
else:
    T = {
        "page_bg":        "#f0f4f8",
        "hero_bg":        "linear-gradient(135deg,#dbeafe 0%,#bfdbfe 40%,#93c5fd 70%,#bfdbfe 100%)",
        "hero_border":    "rgba(37,99,235,0.2)",
        "left_bg":        "linear-gradient(180deg,#e0ecff 0%,#dce8ff 100%)",
        "left_border":    "rgba(37,99,235,0.15)",
        "right_bg":       "#f0f4f8",
        "text_primary":   "#0f172a",
        "text_secondary": "#1e293b",
        "text_muted":     "rgba(30,58,138,0.65)",
        "text_faint":     "rgba(30,58,138,0.5)",
        "text_label":     "rgba(30,58,138,0.55)",
        "accent":         "#1d4ed8",
        "accent_glow":    "rgba(37,99,235,0.3)",
        "accent_bg":      "rgba(37,99,235,0.08)",
        "accent_border":  "rgba(37,99,235,0.2)",
        "card_bg":        "rgba(255,255,255,0.7)",
        "card_border":    "rgba(37,99,235,0.12)",
        "card_hover_bg":  "rgba(37,99,235,0.08)",
        "card_hover_bd":  "rgba(37,99,235,0.3)",
        "now_card_bg":    "linear-gradient(145deg,rgba(37,99,235,0.1),rgba(37,99,235,0.05))",
        "now_card_bd":    "rgba(37,99,235,0.2)",
        "alert_rain_bg":  "linear-gradient(135deg,rgba(37,99,235,0.1),rgba(37,99,235,0.05))",
        "alert_rain_bd":  "rgba(37,99,235,0.3)",
        "alert_rain_tx":  "#1e3a8a",
        "alert_dry_bg":   "rgba(255,255,255,0.5)",
        "alert_dry_bd":   "rgba(37,99,235,0.1)",
        "alert_dry_tx":   "rgba(30,58,138,0.55)",
        "sec_line":       "rgba(37,99,235,0.15)",
        "footer_bd":      "rgba(37,99,235,0.12)",
        "footer_tx":      "rgba(30,58,138,0.45)",
        "grid_color":     "rgba(37,99,235,0.06)",
        "tick_color":     "rgba(30,58,138,0.45)",
        "bar_dry":        "rgba(37,99,235,0.15)",
        "bar_wet":        "rgba(37,99,235,0.65)",
        "press_fill":     "rgba(109,40,217,0.06)",
        "press_line":     "rgba(109,40,217,0.55)",
        "press_hover":    "#7c3aed",
        "temp_line":      "rgba(234,88,12,0.6)",
        "btn_bg":         "rgba(37,99,235,0.1)",
        "btn_tx":         "#1d4ed8",
        "btn_bd":         "rgba(37,99,235,0.3)",
        "cmp_dry_bg":     "rgba(255,255,255,0.6)",
        "cmp_dry_bd":     "rgba(37,99,235,0.1)",
        "cmp_g_bg":       "rgba(66,133,244,0.07)",
        "cmp_g_bd":       "rgba(66,133,244,0.3)",
        "cmp_m_bg":       "rgba(37,99,235,0.07)",
        "cmp_m_bd":       "rgba(37,99,235,0.3)",
        "cmp_stats_bd":   "rgba(37,99,235,0.1)",
        "cs_val_tx":      "#0f172a",
        "week_bg":        "rgba(255,255,255,0.6)",
        "week_bd":        "rgba(37,99,235,0.1)",
        "week_hi":        "#0f172a",
        "week_lo":        "rgba(30,58,138,0.5)",
        "pcr_track":      "rgba(37,99,235,0.08)",
        "pcr_lbl":        "rgba(30,58,138,0.5)",
        "pcr_val":        "#0f172a",
        "meta_tx":        "rgba(30,58,138,0.4)",
        "subtitle_tx":    "rgba(30,58,138,0.6)",
        "toggle_icon":    "🌙",
        "toggle_label":   "Dark Mode",
        "toggle_bg":      "rgba(30,58,138,0.08)",
        "toggle_bd":      "rgba(30,58,138,0.2)",
        "toggle_tx":      "#1e3a8a",
        "hoverlabel_bg":  "#dbeafe",
        "plot_bg":        "rgba(240,244,248,0)",
    }

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [data-testid="stAppViewContainer"] {{
    background: {T['page_bg']} !important;
    color: {T['text_secondary']};
    font-family: 'Sora', sans-serif;
}}
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stSidebar"] {{ display: none !important; }}
section[data-testid="stMain"] > div {{ padding: 0 !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
footer {{ display: none !important; }}

.hero {{
    background: {T['hero_bg']};
    padding: 2.5rem 3rem 2rem;
    border-bottom: 1px solid {T['hero_border']};
    position: relative; overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 20% 50%, {T['accent_bg']} 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, {T['accent_bg']} 0%, transparent 50%);
    pointer-events: none;
}}
.hero-top {{ display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:1rem; position:relative; z-index:1; }}
.city-block h1 {{ font-family:'Sora',sans-serif; font-size:2.8rem; font-weight:800; letter-spacing:-1px; color:{T['text_primary']}; line-height:1; margin-bottom:0.2rem; }}
.city-block .subtitle {{ font-family:'Space Mono',monospace; font-size:0.72rem; color:{T['subtitle_tx']}; letter-spacing:3px; text-transform:uppercase; }}
.live-badge {{ display:inline-flex; align-items:center; gap:0.45rem; background:{T['accent_bg']}; border:1px solid {T['accent_border']}; border-radius:100px; padding:0.35rem 0.9rem; font-family:'Space Mono',monospace; font-size:0.65rem; color:{T['accent']}; letter-spacing:2px; text-transform:uppercase; margin-top:0.5rem; }}
.live-dot {{ width:6px; height:6px; border-radius:50%; background:{T['accent']}; animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.4;transform:scale(1.3)}} }}

.theme-btn {{ display:inline-flex; align-items:center; gap:0.5rem; background:{T['toggle_bg']}; border:1px solid {T['toggle_bd']}; border-radius:100px; padding:0.4rem 1rem; font-family:'Space Mono',monospace; font-size:0.65rem; color:{T['toggle_tx']}; letter-spacing:2px; text-transform:uppercase; cursor:pointer; margin-top:0.5rem; }}

.left-panel {{ background:{T['left_bg']}; border-right:1px solid {T['left_border']}; padding:2rem 1.8rem; display:flex; flex-direction:column; gap:1.5rem; }}
.right-panel {{ padding:2rem 2.2rem; display:flex; flex-direction:column; gap:1.8rem; background:{T['right_bg']}; }}

.now-card {{ background:{T['now_card_bg']}; border:1px solid {T['now_card_bd']}; border-radius:20px; padding:1.8rem; text-align:center; position:relative; overflow:hidden; }}
.now-card::after {{ content:''; position:absolute; top:-40px; right:-40px; width:120px; height:120px; border-radius:50%; background:radial-gradient(circle,{T['accent_bg']},transparent 70%); }}
.now-label {{ font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase; color:{T['text_muted']}; margin-bottom:1rem; }}
.rain-icon-big {{ font-size:3.5rem; margin-bottom:0.6rem; display:block; filter:drop-shadow(0 0 20px {T['accent_glow']}); }}
.prob-number {{ font-family:'Sora',sans-serif; font-size:4.5rem; font-weight:800; color:{T['text_primary']}; line-height:1; letter-spacing:-3px; }}
.prob-unit {{ font-size:1.8rem; color:{T['text_faint']}; font-weight:300; }}
.prob-label {{ font-size:0.78rem; color:{T['text_muted']}; margin-top:0.4rem; letter-spacing:1px; }}

.stat-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0.7rem; }}
.stat-pill {{ background:{T['card_bg']}; border:1px solid {T['card_border']}; border-radius:14px; padding:0.9rem 0.8rem; text-align:center; transition:border-color .2s; }}
.stat-pill:hover {{ border-color:{T['card_hover_bd']}; }}
.stat-pill .s-val {{ font-family:'Space Mono',monospace; font-size:1.25rem; font-weight:700; color:{T['text_secondary']}; display:block; }}
.stat-pill .s-lbl {{ font-size:0.6rem; color:{T['text_label']}; letter-spacing:1.5px; text-transform:uppercase; margin-top:0.15rem; }}

.alert-rain {{ background:{T['alert_rain_bg']}; border:1px solid {T['alert_rain_bd']}; border-left:3px solid {T['accent']}; border-radius:12px; padding:1rem 1.1rem; font-size:0.82rem; color:{T['alert_rain_tx']}; line-height:1.5; }}
.alert-no-rain {{ background:{T['alert_dry_bg']}; border:1px solid {T['alert_dry_bd']}; border-left:3px solid {T['alert_dry_bd']}; border-radius:12px; padding:1rem 1.1rem; font-size:0.82rem; color:{T['alert_dry_tx']}; line-height:1.5; }}

.sec-header {{ display:flex; align-items:center; gap:0.7rem; margin-bottom:1rem; }}
.sec-title {{ font-family:'Sora',sans-serif; font-size:0.78rem; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:{T['text_muted']}; }}
.sec-line {{ flex:1; height:1px; background:{T['sec_line']}; }}

.forecast-scroll {{ display:flex; gap:0.8rem; overflow-x:auto; padding-bottom:0.5rem; scrollbar-width:thin; scrollbar-color:{T['accent_border']} transparent; }}
.fc-card {{ flex:0 0 120px; background:{T['card_bg']}; border:1px solid {T['card_border']}; border-radius:16px; padding:1rem 0.8rem; text-align:center; transition:all .25s ease; }}
.fc-card:hover {{ background:{T['card_hover_bg']}; border-color:{T['card_hover_bd']}; transform:translateY(-2px); }}
.fc-card.rain {{ background:{T['accent_bg']}; border-color:{T['accent_border']}; }}
.fc-time {{ font-family:'Space Mono',monospace; font-size:0.62rem; color:{T['text_faint']}; letter-spacing:1px; text-transform:uppercase; margin-bottom:0.6rem; }}
.fc-icon {{ font-size:1.6rem; margin-bottom:0.4rem; }}
.fc-prob {{ font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:700; color:{T['text_secondary']}; }}
.fc-mm {{ font-size:0.62rem; color:{T['text_faint']}; margin-top:0.2rem; font-family:'Space Mono',monospace; }}

.footer-bar {{ padding:1rem 3rem; border-top:1px solid {T['footer_bd']}; display:flex; justify-content:space-between; align-items:center; font-family:'Space Mono',monospace; font-size:0.6rem; color:{T['footer_tx']}; letter-spacing:1.5px; text-transform:uppercase; }}

div[data-testid="stHorizontalBlock"] {{ gap:0 !important; }}
.stButton > button {{ background:{T['btn_bg']} !important; color:{T['btn_tx']} !important; border:1px solid {T['btn_bd']} !important; border-radius:100px !important; font-family:'Space Mono',monospace !important; font-size:0.65rem !important; letter-spacing:2px !important; text-transform:uppercase !important; padding:0.4rem 1.2rem !important; transition:all .2s !important; }}
.stButton > button:hover {{ background:{T['card_hover_bg']} !important; border-color:{T['card_hover_bd']} !important; }}

/* Comparison */
.cmp-wrap {{ padding:2rem 3rem; border-top:1px solid {T['footer_bd']}; }}
.cmp-card {{ background:{T['cmp_dry_bg']}; border:1px solid {T['cmp_dry_bd']}; border-radius:20px; padding:1.5rem; }}
.cmp-card.google {{ border-color:{T['cmp_g_bd']}; background:{T['cmp_g_bg']}; }}
.cmp-card.ml {{ border-color:{T['cmp_m_bd']}; background:{T['cmp_m_bg']}; }}
.cmp-badge {{ font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:2px; text-transform:uppercase; padding:0.25rem 0.7rem; border-radius:100px; display:inline-block; margin-bottom:1rem; }}
.badge-google {{ background:rgba(66,133,244,0.15); border:1px solid rgba(66,133,244,0.3); color:#4285f4; }}
.badge-ml {{ background:{T['accent_bg']}; border:1px solid {T['accent_border']}; color:{T['accent']}; }}
.cmp-main {{ display:flex; align-items:center; gap:1rem; margin-bottom:1.2rem; }}
.cmp-icon {{ font-size:2.8rem; }}
.cmp-temp {{ font-family:'Sora',sans-serif; font-size:3rem; font-weight:800; color:{T['text_primary']}; line-height:1; letter-spacing:-2px; }}
.cmp-desc {{ font-size:0.8rem; color:{T['text_muted']}; margin-top:0.2rem; }}
.cmp-stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:0.6rem; border-top:1px solid {T['cmp_stats_bd']}; padding-top:1rem; }}
.cs-item {{ text-align:center; }}
.cs-val {{ font-family:'Space Mono',monospace; font-size:0.95rem; font-weight:700; color:{T['cs_val_tx']}; display:block; }}
.cs-lbl {{ font-size:0.58rem; color:{T['text_faint']}; letter-spacing:1.5px; text-transform:uppercase; margin-top:0.1rem; }}

.pcr-row {{ display:flex; align-items:center; gap:0.8rem; margin-bottom:0.6rem; }}
.pcr-lbl {{ font-family:'Space Mono',monospace; font-size:0.6rem; color:{T['pcr_lbl']}; width:72px; text-align:right; letter-spacing:1px; text-transform:uppercase; flex-shrink:0; }}
.pcr-wrap {{ flex:1; height:8px; background:{T['pcr_track']}; border-radius:100px; overflow:hidden; }}
.pcr-fill {{ height:100%; border-radius:100px; }}
.bar-g {{ background:linear-gradient(90deg,#4285f4,#6aa0f5); }}
.bar-m {{ background:linear-gradient(90deg,{T['accent']},#7dd3fc); }}
.pcr-val {{ font-family:'Space Mono',monospace; font-size:0.65rem; color:{T['pcr_val']}; width:38px; flex-shrink:0; }}

.week-grid {{ display:grid; grid-template-columns:repeat(7,1fr); gap:0.6rem; margin-top:1rem; }}
.week-card {{ background:{T['week_bg']}; border:1px solid {T['week_bd']}; border-radius:14px; padding:0.8rem 0.4rem; text-align:center; }}
.week-day {{ font-family:'Space Mono',monospace; font-size:0.6rem; color:{T['text_faint']}; letter-spacing:1px; text-transform:uppercase; margin-bottom:0.4rem; }}
.week-icon {{ font-size:1.4rem; margin-bottom:0.3rem; }}
.week-hi {{ font-family:'Sora',sans-serif; font-size:0.9rem; font-weight:700; color:{T['week_hi']}; }}
.week-lo {{ font-size:0.75rem; color:{T['week_lo']}; }}
.week-rain {{ font-family:'Space Mono',monospace; font-size:0.6rem; color:{T['accent']}; margin-top:0.3rem; }}

/* ── Live Sensor Pane ─────────────────────────────────────────────────────── */
.sensor-wrap {{ padding:2rem 3rem; border-top:1px solid {T['footer_bd']}; }}
.sensor-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem; }}
.sensor-card {{
    background:{T['now_card_bg']}; border:1px solid {T['now_card_bd']};
    border-radius:20px; padding:1.6rem 1.2rem; text-align:center; position:relative; overflow:hidden;
}}
.sensor-card::after {{ content:''; position:absolute; top:-30px; right:-30px; width:90px; height:90px;
    border-radius:50%; background:radial-gradient(circle,{T['accent_bg']},transparent 70%); }}
.sensor-icon {{ font-size:2.2rem; margin-bottom:0.5rem; display:block;
    filter:drop-shadow(0 0 12px {T['accent_glow']}); }}
.sensor-val {{ font-family:'Sora',sans-serif; font-size:3.2rem; font-weight:800;
    color:{T['text_primary']}; line-height:1; letter-spacing:-2px; }}
.sensor-unit {{ font-size:1.4rem; color:{T['text_faint']}; font-weight:300; }}
.sensor-lbl {{ font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:3px;
    text-transform:uppercase; color:{T['text_muted']}; margin-top:0.5rem; }}
.sensor-status {{ display:inline-flex; align-items:center; gap:0.4rem; margin-top:0.8rem;
    font-family:'Space Mono',monospace; font-size:0.6rem; letter-spacing:2px;
    text-transform:uppercase; color:{T['accent']}; }}
.sensor-dot {{ width:6px; height:6px; border-radius:50%; background:{T['accent']};
    animation:pulse 2s infinite; }}
.sensor-dot.offline {{ background:#ff4444; animation:none; }}
.sensor-age {{ font-family:'Space Mono',monospace; font-size:0.58rem;
    color:{T['meta_tx']}; margin-top:0.3rem; }}

</style>
""", unsafe_allow_html=True)

# ─── Google Sheets Sensor Reader ─────────────────────────────────────────────
SHEET_ID  = "1UpnXi_F-GyX7HCaJkV0RO3vSa4EZEiLvlrnVkXi6GFY"
SHEET_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet1"

@st.cache_data(ttl=10)   # re-fetch every 10 seconds
def fetch_sensor_data():
    """Fetch the Google Sheet as CSV and return the latest row + history."""
    try:
        df = pd.read_csv(SHEET_CSV)
        df.columns = [c.strip() for c in df.columns]
        # Expect columns: Timestamp, Temperature(C), Humidity(%)
        df = df.dropna(subset=[df.columns[1], df.columns[2]])
        df['Timestamp']      = pd.to_datetime(df[df.columns[0]], dayfirst=True, errors='coerce')
        df['Temperature(C)'] = pd.to_numeric(df[df.columns[1]], errors='coerce')
        df['Humidity(%)']    = pd.to_numeric(df[df.columns[2]], errors='coerce')
        df = df.dropna().sort_values('Timestamp').reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()

# ─── Constants ────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))
OWM_KEY = "59a2e9f07edc1cab2cdf70f7bd3955b2"
TRAIN_MEANS = {'Press_hPa': 1007.399, 'Spec_Hum': 0.01578, 'Temp_C': 26.152}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_ist():
    return pd.Timestamp.now(tz=IST).replace(tzinfo=None)

def rh_to_q(rh, t, p):
    e_sat = 6.112 * np.exp((17.67 * t) / (t + 243.5))
    e_act = (rh / 100.0) * e_sat
    return (0.622 * e_act) / (p - 0.378 * e_act)

def log1p_safe(x):
    return np.log1p(np.maximum(x, 0))

def wmo_to_label(code):
    m = {
        0:("Clear Sky","☀️"), 1:("Mainly Clear","🌤️"), 2:("Partly Cloudy","⛅"), 3:("Overcast","☁️"),
        45:("Foggy","🌫️"), 48:("Icy Fog","🌫️"),
        51:("Light Drizzle","🌦️"), 53:("Drizzle","🌦️"), 55:("Heavy Drizzle","🌧️"),
        61:("Slight Rain","🌧️"), 63:("Moderate Rain","🌧️"), 65:("Heavy Rain","🌧️"),
        80:("Showers","🌦️"), 81:("Mod. Showers","🌧️"), 82:("Heavy Showers","⛈️"),
        95:("Thunderstorm","⛈️"), 96:("Thunder+Hail","⛈️"), 99:("Heavy Thunder","⛈️"),
    }
    return m.get(code, ("Unknown","🌡️"))

def rain_icon(prob, flag, amount):
    if not flag:
        return "☀️" if prob < 20 else ("🌤️" if prob < 40 else "⛅")
    return "🌦️" if amount < 1 else ("🌧️" if amount < 5 else "⛈️")

# ─── Feature Builder ──────────────────────────────────────────────────────────
def build_features(df, feat_cols):
    df = df.copy().sort_values('time').reset_index(drop=True)
    rain = df['Rainfall_mm_hr']
    rain_s = rain.shift(1).fillna(0)
    for lag in [1,2,3,4,5,6,7,8,10,12,16,24]:
        df[f'Rain_lag{lag}'] = log1p_safe(rain.shift(lag).fillna(0))
    for w in [2,3,4,6,8,12,16,24,48]:
        df[f'Rain_roll{w}'] = log1p_safe(rain_s.rolling(w, min_periods=1).mean())
    for w in [3,6,8,12,24,48]:
        df[f'Rain_max{w}'] = rain_s.rolling(w, min_periods=1).max()
    for w in [4,8,12]:
        df[f'Rain_std{w}'] = rain_s.rolling(w, min_periods=1).std().fillna(0)
    for w in [2,4,6,8,12,24]:
        df[f'persist_{w}'] = sum((rain.shift(i)>0.1).astype(float) for i in range(1,w+1)) / w
    df['consec_rain3'] = sum((rain.shift(i)>0.1).astype(float) for i in range(1,4))
    df['consec_rain6'] = sum((rain.shift(i)>0.1).astype(float) for i in range(1,7))
    hrs, last = [], 999
    for i in range(len(df)):
        if i == 0: hrs.append(999)
        elif rain.iloc[i-1] > 0.1: last = 0; hrs.append(0)
        else: last = min(last+3, 999); hrs.append(last)
    df['hours_since_rain'] = hrs
    df['dry_spell_sq'] = np.sqrt(df['hours_since_rain'].clip(0,200))
    df['last_rain_int'] = rain_s.where(rain_s>0.1, np.nan).ffill().fillna(0)
    df['rain_momentum'] = rain_s.rolling(2,min_periods=1).mean() - rain_s.rolling(8,min_periods=1).mean()
    for lag in [1,2,4,8,12]:
        df[f'Press_lag{lag}'] = df['Press_hPa'].shift(lag).fillna(TRAIN_MEANS['Press_hPa'])
    for d in [1,2,4,6,8,12]:
        df[f'Press_diff{d}'] = df['Press_hPa'].diff(d).fillna(0)
    df['press_accel'] = df['Press_hPa'].diff(1).fillna(0) - df['Press_hPa'].diff(2).fillna(0)
    for lag in [1,2,4,8]:
        df[f'Hum_lag{lag}'] = df['Spec_Hum'].shift(lag).fillna(TRAIN_MEANS['Spec_Hum'])
    df['hum_trend']  = df['Spec_Hum'].diff(1).fillna(0)
    df['hum_trend4'] = df['Spec_Hum'] - df['Spec_Hum'].shift(4).fillna(TRAIN_MEANS['Spec_Hum'])
    df['Spec_Hum_raw']  = df['Spec_Hum']
    df['Press_hPa_raw'] = df['Press_hPa']
    df['Temp_lag1']  = df['Temp_C'].shift(1).fillna(TRAIN_MEANS['Temp_C'])
    df['Temp_lag4']  = df['Temp_C'].shift(4).fillna(TRAIN_MEANS['Temp_C'])
    df['Temp_diff1'] = df['Temp_C'].diff(1).fillna(0)
    df['Temp_diff4'] = df['Temp_C'].diff(4).fillna(0)
    df['hum_x_rain1']    = df['Spec_Hum'] * log1p_safe(rain.shift(1).fillna(0))
    df['press_hum']      = df['Press_hPa'].diff(1).fillna(0) * df['Spec_Hum']
    df['temp_hum']       = df['Temp_C'] * df['Spec_Hum']
    df['hum_press_diff'] = df['Spec_Hum'] * df['Press_hPa'].diff(4).fillna(0)
    df['persist_hum']    = df['persist_4'] * df['Spec_Hum']
    df['hour_sin']      = np.sin(2*np.pi*df['time'].dt.hour/24)
    df['hour_cos']      = np.cos(2*np.pi*df['time'].dt.hour/24)
    df['month_sin']     = np.sin(2*np.pi*df['time'].dt.month/12)
    df['month_cos']     = np.cos(2*np.pi*df['time'].dt.month/12)
    df['dayofyear_sin'] = np.sin(2*np.pi*df['time'].dt.dayofyear/365)
    df['dayofyear_cos'] = np.cos(2*np.pi*df['time'].dt.dayofyear/365)
    df['is_monsoon']    = df['time'].dt.month.isin([6,7,8,9]).astype(float)
    df['is_morning']    = df['time'].dt.hour.isin([6,9,12]).astype(float)
    return df[feat_cols].values

# ─── Data Fetchers ────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s1  = joblib.load("stage1_classifier.pkl")
        s2  = joblib.load("stage2_regressor.pkl")
        fc  = joblib.load("feature_cols.pkl")
        cfg = joblib.load("model_config.pkl")
    return s1, s2, fc, cfg

@st.cache_data(ttl=600)
def fetch_owm_realtime(_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(url, params={"lat":22.5726,"lon":88.3639,"appid":_key,"units":"metric"}, timeout=10)
    r.raise_for_status()
    d = r.json()
    return {
        'Temp_C':     d['main']['temp'],
        'RH_pct':     d['main']['humidity'],
        'Press_hPa':  d['main']['pressure'],
        'Rain_mm':    d.get('rain',{}).get('1h', 0.0),
        'wind_speed': d['wind'].get('speed', 0),
        'visibility': d.get('visibility', 10000) / 1000,
    }

@st.cache_data(ttl=600)
def fetch_open_meteo_history():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":22.5726, "longitude":88.3639,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation",
        "past_days":8, "forecast_days":2, "timezone":"Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    d = r.json()['hourly']
    return pd.DataFrame({
        'time':      pd.to_datetime(d['time']),
        'Temp_C':    d['temperature_2m'],
        'RH_pct':    d['relative_humidity_2m'],
        'Press_hPa': d['surface_pressure'],
        'Rain_mm':   d['precipitation'],
    })

@st.cache_data(ttl=600)
def fetch_comparison():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":22.5726, "longitude":88.3639,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,surface_pressure,apparent_temperature",
        "daily":   "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "hourly":  "precipitation_probability,precipitation,temperature_2m",
        "forecast_days":7, "timezone":"Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# ─── Prediction Engine ────────────────────────────────────────────────────────
def run_prediction():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stage1, stage2, feat_cols, config = load_models()
    THRESHOLD = config['threshold']
    df_raw = fetch_open_meteo_history()
    current_ist = now_ist()
    rt = None
    try:
        rt = fetch_owm_realtime(OWM_KEY)
    except Exception:
        pass
    df_raw.loc[df_raw['time'] > current_ist, 'Rain_mm'] = 0.0
    df_raw['Spec_Hum'] = rh_to_q(df_raw['RH_pct'], df_raw['Temp_C'], df_raw['Press_hPa'])
    df_3h = df_raw.set_index('time').resample('3h').agg(
        {'Temp_C':'mean','Spec_Hum':'mean','Press_hPa':'mean','Rain_mm':'sum'}
    )
    df_3h['Rainfall_mm_hr'] = df_3h['Rain_mm'] / 3.0
    df_3h = df_3h.drop(columns=['Rain_mm']).dropna(subset=['Temp_C','Spec_Hum','Press_hPa']).reset_index()
    df_3h['Rainfall_mm_hr'] = df_3h['Rainfall_mm_hr'].fillna(0)
    df_past   = df_3h[df_3h['time'] <= current_ist].copy()
    df_future = df_3h[df_3h['time'] >  current_ist].head(8).copy()
    df_comb   = pd.concat([df_past, df_future]).reset_index(drop=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        X_all    = build_features(df_comb, feat_cols)
        X_now    = X_all[[len(df_past)-1], :]
        now_prob = stage1.predict_proba(X_now)[0, 1]
        now_flag = now_prob > THRESHOLD
        now_amt  = 0.0
        if now_flag:
            now_amt = float(np.clip(np.expm1(stage2.predict(X_now)), 0, None))
        n_past  = len(df_past)
        X_fut   = X_all[n_past:n_past+len(df_future), :]
        probs   = stage1.predict_proba(X_fut)[:, 1]
        flags   = probs > THRESHOLD
        amounts = np.zeros(len(df_future))
        if flags.sum() > 0:
            amounts[flags] = np.clip(np.expm1(stage2.predict(X_fut[flags])), 0, None)
    forecast_df = pd.DataFrame({
        'time_ist':   df_future['time'].values,
        'rain_prob':  np.round(probs * 100, 1),
        'rain_flag':  flags,
        'rain_mm_hr': np.round(amounts, 3),
    })
    cutoff  = current_ist - timedelta(hours=48)
    hist_df = df_past[df_past['time'] >= cutoff][['time','Rainfall_mm_hr','Temp_C','Press_hPa']].copy()
    return {
        'now_prob':    round(float(now_prob)*100, 1),
        'now_flag':    bool(now_flag),
        'now_amount':  round(now_amt, 3),
        'current_ist': current_ist,
        'forecast_df': forecast_df,
        'hist_df':     hist_df,
        'rt':          rt,
        'threshold':   THRESHOLD,
        'config':      config,
    }

# ─── Hero ─────────────────────────────────────────────────────────────────────
hero_left, hero_right = st.columns([4, 1])
with hero_left:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-top">
        <div class="city-block">
          <h1>🌧 Kolkata</h1>
          <div class="subtitle">Rain Intelligence Dashboard &nbsp;&middot;&nbsp; 22.57N 88.36E</div>
          <div class="live-badge"><span class="live-dot"></span> Live AI Forecast</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("<div style='padding:2rem 1rem 0 0; text-align:right;'>", unsafe_allow_html=True)
    st.button(
        f"{T['toggle_icon']}  {T['toggle_label']}",
        on_click=toggle_theme,
        key="theme_toggle"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
with st.spinner(""):
    try:
        data = run_prediction()
    except Exception as e:
        import traceback
        st.error(f"Error: {e}")
        st.code(traceback.format_exc())
        st.stop()

prob        = data['now_prob']
flag        = data['now_flag']
amount      = data['now_amount']
rt          = data['rt']
forecast_df = data['forecast_df']
hist_df     = data['hist_df']
current_ist = data['current_ist']
icon        = rain_icon(prob, flag, amount)

# ─── Left + Right Panels ──────────────────────────────────────────────────────
left_col, right_col = st.columns([1.1, 2.6], gap="small")

with left_col:
    amt_str   = f"{amount:.2f}" if flag else "0.00"
    temp_str  = f"{rt['Temp_C']:.1f}°C"   if rt else "—"
    hum_str   = f"{rt['RH_pct']:.0f}%"    if rt else "—"
    press_str = f"{rt['Press_hPa']:.0f}"  if rt else "—"
    wind_str  = f"{rt['wind_speed']:.1f}" if rt else "—"
    vis_str   = f"{rt['visibility']:.1f}" if rt else "—"
    alert_html = (
        f"<div class='alert-rain'>🌧 Rain Alert — Intensity: <b>{amount} mm/hr</b>. Carry an umbrella.</div>"
        if flag else
        "<div class='alert-no-rain'>☀️ Conditions look dry right now.</div>"
    )
    meta = data['config']
    st.markdown(f"""
    <div class="left-panel">
      <div class="now-card">
        <div class="now-label">Now &middot; {current_ist.strftime('%H:%M IST')}</div>
        <span class="rain-icon-big">{icon}</span>
        <div class="prob-number">{prob}<span class="prob-unit">%</span></div>
        <div class="prob-label">Probability of Rain</div>
      </div>
      <div class="stat-grid">
        <div class="stat-pill"><span class="s-val">{amt_str}</span><span class="s-lbl">mm / hr</span></div>
        <div class="stat-pill"><span class="s-val">{temp_str}</span><span class="s-lbl">Temp</span></div>
        <div class="stat-pill"><span class="s-val">{hum_str}</span><span class="s-lbl">Humidity</span></div>
        <div class="stat-pill"><span class="s-val">{press_str}</span><span class="s-lbl">hPa</span></div>
        <div class="stat-pill"><span class="s-val">{wind_str}</span><span class="s-lbl">m/s Wind</span></div>
        <div class="stat-pill"><span class="s-val">{vis_str}</span><span class="s-lbl">km Vis.</span></div>
      </div>
      {alert_html}
      <div style="font-family:'Space Mono',monospace;font-size:0.58rem;color:{T['meta_tx']};line-height:1.8;padding-top:0.5rem;">
        MODEL &middot; XGBoost Two-Stage<br>
        THRESHOLD &middot; {meta['threshold']:.4f}<br>
        TRAINED ON &middot; {meta['trained_on']}<br>
        FEATURES &middot; {meta['n_features']}<br>
        VAL F1 &middot; {meta['val_f1']:.4f}<br>
        TIMESTEP &middot; {meta['timestep_hours']}h
      </div>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown(f"<div class='right-panel'>", unsafe_allow_html=True)

    # 24h Forecast Cards
    st.markdown(f"""<div class="sec-header"><span class="sec-title">24-Hour Forecast</span><span class="sec-line"></span></div>""", unsafe_allow_html=True)
    cards_html = '<div class="forecast-scroll">'
    for _, row in forecast_df.iterrows():
        t = pd.Timestamp(row['time_ist'])
        fc_icon  = "🌧️" if row['rain_flag'] else ("🌤️" if row['rain_prob'] < 30 else "⛅")
        rain_cls = "rain" if row['rain_flag'] else ""
        cards_html += f"""<div class="fc-card {rain_cls}">
          <div class="fc-time">{t.strftime('%a')}<br>{t.strftime('%H:%M')}</div>
          <div class="fc-icon">{fc_icon}</div>
          <div class="fc-prob">{row['rain_prob']:.0f}%</div>
          <div class="fc-mm">{row['rain_mm_hr']:.2f} mm/hr</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # Probability Chart
    st.markdown(f"""<div class="sec-header" style="margin-top:1.5rem;"><span class="sec-title">Rain Probability Curve</span><span class="sec-line"></span></div>""", unsafe_allow_html=True)
    times_fc = [pd.Timestamp(t).strftime('%d %b %H:%M') for t in forecast_df['time_ist']]
    fig_fc = go.Figure()
    fig_fc.add_hline(
        y=data['threshold']*100, line_dash="dot", line_color=T['accent_border'],
        annotation_text=f"Threshold {data['threshold']*100:.1f}%",
        annotation=dict(font=dict(color=T['text_faint'], size=10))
    )
    fig_fc.add_trace(go.Scatter(x=times_fc, y=forecast_df['rain_prob'], fill='tozeroy', fillcolor=T['accent_bg'], line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    fig_fc.add_trace(go.Scatter(
        x=times_fc, y=forecast_df['rain_prob'], mode='lines+markers',
        line=dict(color=T['accent'], width=2.5),
        marker=dict(size=[12 if f else 7 for f in forecast_df['rain_flag']], color=[T['accent'] if f else T['card_bg'] for f in forecast_df['rain_flag']], line=dict(color=T['accent'], width=1.5)),
        hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
    ))
    fig_fc.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220,
        margin=dict(l=10,r=10,t=10,b=10), showlegend=False,
        yaxis=dict(range=[0,105], ticksuffix='%', gridcolor=T['grid_color'], tickfont=dict(color=T['tick_color'], size=10, family='Space Mono'), zeroline=False),
        xaxis=dict(gridcolor=T['grid_color'], tickangle=-30, tickfont=dict(color=T['tick_color'], size=9, family='Space Mono')),
        hoverlabel=dict(bgcolor=T['hoverlabel_bg'], font=dict(color=T['text_secondary']), bordercolor=T['accent'])
    )
    st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

    # Historical Rain
    if not hist_df.empty:
        st.markdown(f"""<div class="sec-header"><span class="sec-title">Historical Rainfall &middot; Last 48 Hours</span><span class="sec-line"></span></div>""", unsafe_allow_html=True)
        hist_times = [pd.Timestamp(t).strftime('%d %b %H:%M') for t in hist_df['time']]
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Bar(
            x=hist_times, y=hist_df['Rainfall_mm_hr'],
            marker=dict(color=[T['bar_wet'] if v > 0.1 else T['bar_dry'] for v in hist_df['Rainfall_mm_hr']]),
            hovertemplate='<b>%{x}</b><br>%{y:.3f} mm/hr<extra></extra>'
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_times, y=hist_df['Temp_C'], mode='lines', yaxis='y2',
            line=dict(color=T['temp_line'], width=1.5, dash='dot'),
            hovertemplate='Temp: %{y:.1f}C<extra></extra>'
        ))
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220,
            margin=dict(l=10,r=50,t=10,b=10), showlegend=False, barmode='overlay',
            yaxis=dict(title='mm/hr', gridcolor=T['grid_color'], tickfont=dict(color=T['tick_color'], size=10, family='Space Mono'), zeroline=False, title_font=dict(color=T['tick_color'], size=10)),
            yaxis2=dict(title='C', overlaying='y', side='right', showgrid=False, tickfont=dict(color=T['tick_color'], size=10, family='Space Mono'), title_font=dict(color=T['tick_color'], size=10)),
            xaxis=dict(gridcolor=T['grid_color'], tickangle=-30, tickfont=dict(color=T['tick_color'], size=9, family='Space Mono')),
            hoverlabel=dict(bgcolor=T['hoverlabel_bg'], font=dict(color=T['text_secondary']), bordercolor=T['accent'])
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

    # Pressure Chart
    if not hist_df.empty:
        st.markdown(f"""<div class="sec-header"><span class="sec-title">Pressure Trend &middot; Last 48 Hours</span><span class="sec-line"></span></div>""", unsafe_allow_html=True)
        fig_press = go.Figure()
        fig_press.add_trace(go.Scatter(
            x=hist_times, y=hist_df['Press_hPa'], mode='lines',
            fill='tozeroy', fillcolor=T['press_fill'],
            line=dict(color=T['press_line'], width=2),
            hovertemplate='<b>%{x}</b><br>%{y:.1f} hPa<extra></extra>'
        ))
        fig_press.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=160,
            margin=dict(l=10,r=10,t=10,b=10), showlegend=False,
            yaxis=dict(gridcolor=T['grid_color'], tickfont=dict(color=T['tick_color'], size=10, family='Space Mono'), zeroline=False, ticksuffix=' hPa'),
            xaxis=dict(gridcolor=T['grid_color'], tickangle=-30, tickfont=dict(color=T['tick_color'], size=9, family='Space Mono')),
            hoverlabel=dict(bgcolor=T['hoverlabel_bg'], font=dict(color=T['text_secondary']), bordercolor=T['press_hover'])
        )
        st.plotly_chart(fig_press, use_container_width=True, config={'displayModeBar': False})

    st.markdown("</div>", unsafe_allow_html=True)

# ─── Comparison Section ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="cmp-wrap">
  <div class="sec-header">
    <span class="sec-title">ML Model vs Open-Meteo (Google Weather Source)</span>
    <span class="sec-line"></span>
  </div>
</div>
""", unsafe_allow_html=True)

comp = None
try:
    comp = fetch_comparison()
except Exception:
    pass

if comp:
    cur   = comp['current']
    daily = comp['daily']
    hrly  = comp['hourly']

    g_temp  = cur.get('temperature_2m', 0)
    g_feels = cur.get('apparent_temperature', 0)
    g_hum   = cur.get('relative_humidity_2m', 0)
    g_wind  = cur.get('wind_speed_10m', 0)
    g_press = cur.get('surface_pressure', 0)
    g_rain  = cur.get('precipitation', 0)
    g_wcode = cur.get('weather_code', 0)
    g_label, g_icon = wmo_to_label(g_wcode)

    h_times_raw = pd.to_datetime(hrly['time'])
    if isinstance(h_times_raw, pd.DatetimeIndex):
        h_times_naive = h_times_raw.tz_convert(None) if h_times_raw.tz is not None else h_times_raw
    else:
        h_times_naive = h_times_raw.dt.tz_convert(None) if h_times_raw.dt.tz is not None else h_times_raw
    # Always work with a tz-naive Series for safe arithmetic
    h_times = pd.Series(pd.to_datetime(h_times_naive).values)
    now_scalar = pd.Timestamp(now_ist())
    ci      = int(np.argmin(np.abs((h_times - now_scalar).values)))
    g_prob  = hrly.get('precipitation_probability', [0]*len(h_times))[ci]
    g_rayn  = "YES" if g_rain > 0.1 else "NO"
    ml_rayn = "YES" if flag else "NO"
    rt_hum  = f"{rt['RH_pct']:.0f}%"  if rt else "N/A"
    rt_temp = f"{rt['Temp_C']:.1f}C"  if rt else "N/A"
    valf1   = f"{data['config']['val_f1']:.3f}"

    g_col, m_col = st.columns(2, gap="medium")

    with g_col:
        st.markdown(f"""
        <div class="cmp-card google" style="margin-left:3rem;">
          <div class="cmp-badge badge-google">Open-Meteo / Google Weather</div>
          <div class="cmp-main">
            <span class="cmp-icon">{g_icon}</span>
            <div>
              <div class="cmp-temp">{g_temp:.0f}&deg;C</div>
              <div class="cmp-desc">{g_label} &middot; Feels {g_feels:.0f}&deg;C</div>
            </div>
          </div>
          <div class="cmp-stats">
            <div class="cs-item"><span class="cs-val">{g_prob}%</span><span class="cs-lbl">Rain Prob</span></div>
            <div class="cs-item"><span class="cs-val">{g_rain:.1f}mm</span><span class="cs-lbl">Intensity</span></div>
            <div class="cs-item"><span class="cs-val">{g_hum}%</span><span class="cs-lbl">Humidity</span></div>
            <div class="cs-item"><span class="cs-val">{g_wind:.1f}</span><span class="cs-lbl">km/h Wind</span></div>
            <div class="cs-item"><span class="cs-val">{g_press:.0f}</span><span class="cs-lbl">hPa</span></div>
            <div class="cs-item"><span class="cs-val">{g_rayn}</span><span class="cs-lbl">Raining?</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col:
        st.markdown(f"""
        <div class="cmp-card ml" style="margin-right:3rem;">
          <div class="cmp-badge badge-ml">Your ML Model</div>
          <div class="cmp-main">
            <span class="cmp-icon">{icon}</span>
            <div>
              <div class="cmp-temp">{prob:.0f}%</div>
              <div class="cmp-desc">Rain Probability &middot; {amount:.3f} mm/hr</div>
            </div>
          </div>
          <div class="cmp-stats">
            <div class="cs-item"><span class="cs-val">{prob}%</span><span class="cs-lbl">Rain Prob</span></div>
            <div class="cs-item"><span class="cs-val">{amount:.2f}mm</span><span class="cs-lbl">Intensity</span></div>
            <div class="cs-item"><span class="cs-val">{rt_hum}</span><span class="cs-lbl">Humidity</span></div>
            <div class="cs-item"><span class="cs-val">{rt_temp}</span><span class="cs-lbl">OWM Temp</span></div>
            <div class="cs-item"><span class="cs-val">{valf1}</span><span class="cs-lbl">Val F1</span></div>
            <div class="cs-item"><span class="cs-val">{ml_rayn}</span><span class="cs-lbl">Raining?</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Probability bars
    st.markdown(f"""
    <div style="padding:1.5rem 3rem 0.5rem;">
      <div class="sec-header">
        <span class="sec-title">Rain Probability Head-to-Head (Next 24h)</span>
        <span class="sec-line"></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    future_ts = [pd.Timestamp(t).replace(tzinfo=None) for t in forecast_df['time_ist']]
    om_probs  = []
    for ft in future_ts:
        idx = int(np.argmin(np.abs((h_times - pd.Timestamp(ft).replace(tzinfo=None)).values)))
        om_probs.append(hrly.get('precipitation_probability', [0]*len(h_times))[idx])

    time_label_color = T['text_faint']
    bars = '<div style="padding:0 3rem 1rem;">'
    for ft, ml_p, om_p in zip(future_ts, forecast_df['rain_prob'].tolist(), om_probs):
        label = ft.strftime('%a %H:%M')
        bars += f"""
        <div style="margin-bottom:1rem;">
          <div style="font-family:'Space Mono',monospace;font-size:0.62rem;color:{time_label_color};letter-spacing:1px;margin-bottom:0.4rem;">{label}</div>
          <div class="pcr-row">
            <span class="pcr-lbl">Open-Meteo</span>
            <div class="pcr-wrap"><div class="pcr-fill bar-g" style="width:{om_p}%"></div></div>
            <span class="pcr-val">{om_p}%</span>
          </div>
          <div class="pcr-row">
            <span class="pcr-lbl">ML Model</span>
            <div class="pcr-wrap"><div class="pcr-fill bar-m" style="width:{ml_p}%"></div></div>
            <span class="pcr-val">{ml_p}%</span>
          </div>
        </div>"""
    bars += '</div>'
    st.markdown(bars, unsafe_allow_html=True)

    # 7-Day Outlook
    st.markdown(f"""
    <div style="padding:0.5rem 3rem 0;">
      <div class="sec-header">
        <span class="sec-title">7-Day Outlook &middot; Open-Meteo</span>
        <span class="sec-line"></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    dates_raw = pd.to_datetime(daily['time'])
    if isinstance(dates_raw, pd.DatetimeIndex):
        dates = dates_raw.tz_convert(None) if dates_raw.tz is not None else dates_raw
    else:
        dates = dates_raw.dt.tz_convert(None) if dates_raw.dt.tz is not None else dates_raw
    week  = '<div style="padding:0 3rem 2rem;"><div class="week-grid">'
    for i in range(min(7, len(dates))):
        d      = dates[i]
        wlabel, wicon = wmo_to_label(daily['weather_code'][i])
        hi     = daily['temperature_2m_max'][i]
        lo     = daily['temperature_2m_min'][i]
        rprob  = daily['precipitation_probability_max'][i]
        dname  = 'Today' if i == 0 else d.strftime('%a')
        rstr   = f"💧 {rprob}%" if rprob else "—"
        week  += f"""
        <div class="week-card">
          <div class="week-day">{dname}<br>{d.strftime('%d %b')}</div>
          <div class="week-icon">{wicon}</div>
          <div class="week-hi">{hi:.0f}&deg;</div>
          <div class="week-lo">{lo:.0f}&deg;</div>
          <div class="week-rain">{rstr}</div>
        </div>"""
    week += '</div></div>'
    st.markdown(week, unsafe_allow_html=True)

else:
    st.markdown(f"""<div style="padding:1rem 3rem;font-family:'Space Mono',monospace;font-size:0.7rem;color:{T['meta_tx']};">Comparison data unavailable.</div>""", unsafe_allow_html=True)

# ─── Live Hardware Sensor Pane ───────────────────────────────────────────────
st.markdown(f"""
<div class="sensor-wrap">
  <div class="sec-header">
    <span class="sec-title">&#x1F4E1; Live Hardware Sensor &middot; SHT30 (NodeMCU)</span>
    <span class="sec-line"></span>
  </div>
</div>
""", unsafe_allow_html=True)

_sensor_df  = fetch_sensor_data()
_now        = now_ist()  # use IST to match sheet timestamps
# Sensor is considered CONNECTED only if a row arrived within the last 2 minutes.
# Beyond that the ESP8266 is powered off / disconnected from WiFi.
_TIMEOUT_S  = 60

if not _sensor_df.empty:
    _latest = _sensor_df.iloc[-1]
    _s_temp = _latest["Temperature(C)"]
    _s_hum  = _latest["Humidity(%)"]
    _s_ts   = _latest["Timestamp"]
    _age_s  = int((_now - _s_ts).total_seconds())
    _connected = _age_s <= _TIMEOUT_S
else:
    _s_temp = _s_hum = None
    _s_ts   = None
    _age_s  = None
    _connected = False

if _connected:
    # ── SENSOR ONLINE ─────────────────────────────────────────────────────────
    _age_str = f"{_age_s}s ago" if _age_s < 60 else f"{_age_s // 60}m {_age_s % 60}s ago"

    st.markdown(f"""
    <div style="padding:0 3rem 1rem;">
      <div class="sensor-grid">
        <div class="sensor-card">
          <span class="sensor-icon">&#x1F321;&#xFE0F;</span>
          <div class="sensor-val">{_s_temp:.1f}<span class="sensor-unit">&deg;C</span></div>
          <div class="sensor-lbl">Temperature</div>
          <div class="sensor-status"><span class="sensor-dot"></span>LIVE</div>
          <div class="sensor-age">Last update: {_age_str}</div>
        </div>
        <div class="sensor-card">
          <span class="sensor-icon">&#x1F4A7;</span>
          <div class="sensor-val">{_s_hum:.1f}<span class="sensor-unit">%</span></div>
          <div class="sensor-lbl">Humidity</div>
          <div class="sensor-status"><span class="sensor-dot"></span>LIVE</div>
          <div class="sensor-age">Last update: {_age_str}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # History chart — last 20 readings
    _hist = _sensor_df.tail(20)
    _fig_s = go.Figure()
    _fig_s.add_trace(go.Scatter(
        x=_hist["Timestamp"], y=_hist["Temperature(C)"],
        name="Temp °C", mode="lines+markers",
        line=dict(color=T["accent"], width=2), marker=dict(size=5),
        hovertemplate="%{x|%H:%M:%S}<br>%{y:.1f}°C<extra></extra>"
    ))
    _fig_s.add_trace(go.Scatter(
        x=_hist["Timestamp"], y=_hist["Humidity(%)"],
        name="Humidity %", mode="lines+markers", yaxis="y2",
        line=dict(color=T["press_line"], width=2, dash="dot"), marker=dict(size=5),
        hovertemplate="%{x|%H:%M:%S}<br>%{y:.1f}%<extra></extra>"
    ))
    _fig_s.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=200,
        margin=dict(l=10,r=50,t=10,b=10), showlegend=True,
        legend=dict(font=dict(color=T["text_faint"], size=9, family="Space Mono"),
                    bgcolor="rgba(0,0,0,0)", orientation="h", y=1.15),
        yaxis=dict(title="°C", gridcolor=T["grid_color"], zeroline=False,
                   tickfont=dict(color=T["tick_color"], size=9, family="Space Mono"),
                   title_font=dict(color=T["tick_color"], size=9)),
        yaxis2=dict(title="%", overlaying="y", side="right", showgrid=False,
                    tickfont=dict(color=T["tick_color"], size=9, family="Space Mono"),
                    title_font=dict(color=T["tick_color"], size=9)),
        xaxis=dict(gridcolor=T["grid_color"], tickangle=-30,
                   tickfont=dict(color=T["tick_color"], size=8, family="Space Mono")),
        hoverlabel=dict(bgcolor=T["hoverlabel_bg"], font=dict(color=T["text_secondary"]))
    )
    st.markdown(f"""<div style="padding:0 3rem 0.5rem;">
      <div class="sec-header">
        <span class="sec-title">Sensor History &middot; Last 20 Readings</span>
        <span class="sec-line"></span>
      </div></div>""", unsafe_allow_html=True)
    st.plotly_chart(_fig_s, use_container_width=True, config={"displayModeBar": False})

else:
    # ── SENSOR OFFLINE ────────────────────────────────────────────────────────
    if _s_ts is not None:
        _last_seen = _s_ts.strftime("%d %b %Y, %H:%M:%S")
        _offline_msg = f"Last seen: {_last_seen}"
    else:
        _offline_msg = "No data has been received yet."

    st.markdown(f"""
    <div style="padding:0 3rem 2rem;">
      <div style="
        background: rgba(255,60,60,0.06);
        border: 1px solid rgba(255,60,60,0.25);
        border-left: 3px solid #ff4444;
        border-radius: 16px;
        padding: 2rem 2rem;
        text-align: center;
      ">
        <div style="font-size:2.8rem; margin-bottom:0.8rem;">🔌</div>
        <div style="font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:700;
             color:#ff6666; margin-bottom:0.4rem;">Sensor Not Connected</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.68rem;
             color:{T['text_muted']}; letter-spacing:1px; margin-bottom:0.6rem;">
          Power on your NodeMCU and ensure it is connected to WiFi
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:0.6rem;
             color:{T['meta_tx']};">{_offline_msg}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style="padding:0 3rem 2rem; text-align:center; font-family:'Space Mono',monospace;
font-size:0.58rem; color:{T['meta_tx']};">
  ESP8266 &#x2192; Google Sheets &#x2192; Streamlit &middot; Auto-refreshes every 30s
</div>""", unsafe_allow_html=True)

# Auto-refresh every 30 seconds
st.markdown("""<meta http-equiv="refresh" content="120">""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
rain_slots = int(forecast_df['rain_flag'].sum())
peak_prob  = forecast_df['rain_prob'].max()
st.markdown(f"""
<div class="footer-bar">
  <span>Kolkata Rain Intelligence &middot; ML-Powered</span>
  <span>Next 24h: {rain_slots}/8 slots with rain &middot; Peak {peak_prob:.1f}%</span>
  <span>Updated &middot; {current_ist.strftime('%d %b %Y %H:%M')} IST</span>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 1, 3])
with c2:
    if st.button("↻ Refresh"):
        st.cache_data.clear()
        st.rerun()
