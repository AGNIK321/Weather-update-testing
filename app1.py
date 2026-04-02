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
import plotly.express as px
from datetime import datetime, timezone, timedelta
import time

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kolkata Rain Intelligence",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Theme Toggle ─────────────────────────────────────────────────────────────
# Placed at the top so it registers immediately
theme_choice = st.radio("Theme", ["Dark", "Light"], horizontal=True, label_visibility="collapsed")
is_dark = theme_choice == "Dark"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
COMMON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700;800&display=swap');

/* ── Base Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

font-family: 'Sora', sans-serif;

[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
section[data-testid="stMain"] > div { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* ── Theme Toggle Placement ── */
div[data-testid="stRadio"] {
    position: absolute;
    top: 25px;
    right: 35px;
    z-index: 100;
    padding: 5px 15px;
    border-radius: 20px;
    backdrop-filter: blur(5px);
}
label[data-baseweb="radio"] div { font-family: 'Space Mono', monospace !important; font-size: 0.7rem !important; }

/* ── Hero Banner ── */
.hero {
    padding: 2.5rem 3rem 2rem;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(56, 182, 255, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(120, 220, 255, 0.04) 0%, transparent 50%);
    pointer-events: none;
}

.hero-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    position: relative;
    z-index: 1;
}

.city-block h1 {
    font-family: 'Sora', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 0.2rem;
}

.city-block .subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(56, 182, 255, 0.1);
    border: 1px solid rgba(56, 182, 255, 0.25);
    border-radius: 100px;
    padding: 0.35rem 0.9rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #38b6ff;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #38b6ff;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.3); }
}

/* ── Main Grid ── */
.main-grid {
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 0;
    min-height: calc(100vh - 160px);
}

/* ── Left Panel ── */
.left-panel {
    padding: 2rem 1.8rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* ── Current Now Card ── */
.now-card {
    border-radius: 20px;
    padding: 1.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.now-card::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,182,255,0.06), transparent 70%);
}

.now-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.rain-icon-big {
    font-size: 3.5rem;
    margin-bottom: 0.6rem;
    display: block;
    filter: drop-shadow(0 0 20px rgba(56,182,255,0.4));
}

.prob-number {
    font-family: 'Sora', sans-serif;
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -3px;
}

.prob-unit {
    font-size: 1.8rem;
    font-weight: 300;
}

.prob-label {
    font-size: 0.78rem;
    margin-top: 0.4rem;
    letter-spacing: 1px;
}

/* ── Stat Pills ── */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.7rem;
}

.stat-pill {
    border-radius: 14px;
    padding: 0.9rem 0.8rem;
    text-align: center;
    transition: border-color 0.2s;
}

.stat-pill .s-val {
    font-family: 'Space Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    display: block;
}
.stat-pill .s-lbl {
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 0.15rem;
}

/* ── Right Panel ── */
.right-panel {
    padding: 2rem 2.2rem;
    display: flex;
    flex-direction: column;
    gap: 1.8rem;
}

/* ── Section Header ── */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1rem;
}
.sec-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.sec-line {
    flex: 1;
    height: 1px;
}

/* ── Forecast Timeline Cards ── */
.forecast-scroll {
    display: flex;
    gap: 0.8rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(56,182,255,0.2) transparent;
}

.fc-card {
    flex: 0 0 120px;
    border-radius: 16px;
    padding: 1rem 0.8rem;
    text-align: center;
    transition: all 0.25s ease;
    cursor: default;
}
.fc-card:hover {
    transform: translateY(-2px);
}
.fc-time {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.fc-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.fc-prob {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
}
.fc-mm {
    font-size: 0.62rem;
    margin-top: 0.2rem;
    font-family: 'Space Mono', monospace;
}

/* ── Plotly chart overrides ── */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ── Footer bar ── */
.footer-bar {
    padding: 1rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Streamlit overrides ── */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
.stSpinner { color: #38b6ff !important; }

/* ── Refresh btn ── */
.stButton > button {
    background: rgba(56,182,255,0.1) !important;
    color: #38b6ff !important;
    border: 1px solid rgba(56,182,255,0.3) !important;
    border-radius: 100px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.4rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(56,182,255,0.2) !important;
    border-color: rgba(56,182,255,0.5) !important;
}
"""

DARK_CSS = """
html, body, [data-testid="stAppViewContainer"] { background: #050c1a !important; color: #e8f4ff; }
div[data-testid="stRadio"] { background: rgba(56,182,255,0.05); border: 1px solid rgba(56,182,255,0.2); color: #e8f4ff; }
.hero { background: linear-gradient(135deg, #050c1a 0%, #0a1f3a 40%, #0d2b52 70%, #091d3a 100%); border-bottom: 1px solid rgba(56, 182, 255, 0.15); }
.city-block h1 { color: #ffffff; }
.city-block .subtitle { color: rgba(160, 210, 255, 0.6); }
.left-panel { background: linear-gradient(180deg, #060e1e 0%, #071020 100%); border-right: 1px solid rgba(56, 182, 255, 0.1); }
.now-card { background: linear-gradient(145deg, rgba(56, 182, 255, 0.08), rgba(56, 182, 255, 0.03)); border: 1px solid rgba(56, 182, 255, 0.18); }
.now-label { color: rgba(160, 210, 255, 0.5); }
.prob-number { color: #ffffff; }
.prob-unit { color: rgba(255,255,255,0.4); }
.prob-label { color: rgba(160, 210, 255, 0.55); }
.stat-pill { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); }
.stat-pill:hover { border-color: rgba(56,182,255,0.25); }
.stat-pill .s-val { color: #e8f4ff; }
.stat-pill .s-lbl { color: rgba(160, 210, 255, 0.45); }
.alert-rain { background: linear-gradient(135deg, rgba(56,182,255,0.12), rgba(56,182,255,0.06)); border: 1px solid rgba(56,182,255,0.3); border-left: 3px solid #38b6ff; border-radius: 12px; padding: 1rem 1.1rem; font-size: 0.82rem; color: #b3ddff; line-height: 1.5; }
.alert-no-rain { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07); border-left: 3px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 1rem 1.1rem; font-size: 0.82rem; color: rgba(200, 220, 255, 0.5); line-height: 1.5; }
.right-panel { background: #050c1a; }
.sec-title { color: rgba(160, 210, 255, 0.55); }
.sec-line { background: rgba(56,182,255,0.1); }
.fc-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); }
.fc-card:hover { background: rgba(56,182,255,0.07); border-color: rgba(56,182,255,0.25); }
.fc-card.rain { background: rgba(56,182,255,0.08); border-color: rgba(56,182,255,0.2); }
.fc-time { color: rgba(160,210,255,0.45); }
.fc-prob { color: #e8f4ff; }
.fc-mm { color: rgba(160,210,255,0.4); }
.footer-bar { border-top: 1px solid rgba(56,182,255,0.08); color: rgba(160,210,255,0.3); }
div[data-testid="stMetric"] { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 1rem; }
[data-testid="stMetricLabel"] { color: rgba(160,210,255,0.45) !important; font-size: 0.65rem !important; letter-spacing: 2px; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #e8f4ff !important; font-family: 'Space Mono', monospace !important; }
.stButton > button:hover { color: #fff !important; }
"""

LIGHT_CSS = """
html, body, [data-testid="stAppViewContainer"] { background: #f0f4f8 !important; color: #0f172a; }
div[data-testid="stRadio"] { background: rgba(0,102,204,0.05); border: 1px solid rgba(0,102,204,0.2); color: #0f172a; }
.hero { background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 40%, #7dd3fc 70%, #38bdf8 100%); border-bottom: 1px solid rgba(0, 102, 204, 0.15); }
.city-block h1 { color: #0f172a; }
.city-block .subtitle { color: rgba(15, 23, 42, 0.6); }
.left-panel { background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border-right: 1px solid rgba(0, 102, 204, 0.1); }
.now-card { background: linear-gradient(145deg, rgba(0, 102, 204, 0.08), rgba(0, 102, 204, 0.02)); border: 1px solid rgba(0, 102, 204, 0.18); }
.now-label { color: rgba(15, 23, 42, 0.5); }
.prob-number { color: #0f172a; }
.prob-unit { color: rgba(15, 23, 42, 0.5); }
.prob-label { color: rgba(15, 23, 42, 0.6); }
.stat-pill { background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.06); }
.stat-pill:hover { border-color: rgba(0,102,204,0.3); }
.stat-pill .s-val { color: #0f172a; }
.stat-pill .s-lbl { color: rgba(15, 23, 42, 0.55); }
.alert-rain { background: linear-gradient(135deg, rgba(0,102,204,0.1), rgba(0,102,204,0.03)); border: 1px solid rgba(0,102,204,0.3); border-left: 3px solid #38b6ff; border-radius: 12px; padding: 1rem 1.1rem; font-size: 0.82rem; color: #0f172a; line-height: 1.5; }
.alert-no-rain { background: rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.08); border-left: 3px solid rgba(0,0,0,0.15); border-radius: 12px; padding: 1rem 1.1rem; font-size: 0.82rem; color: rgba(15, 23, 42, 0.6); line-height: 1.5; }
.right-panel { background: #f0f4f8; }
.sec-title { color: rgba(15, 23, 42, 0.55); }
.sec-line { background: rgba(0,102,204,0.15); }
.fc-card { background: rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.07); }
.fc-card:hover { background: rgba(0,102,204,0.07); border-color: rgba(0,102,204,0.25); }
.fc-card.rain { background: rgba(0,102,204,0.08); border-color: rgba(0,102,204,0.2); }
.fc-time { color: rgba(15, 23, 42, 0.5); }
.fc-prob { color: #0f172a; }
.fc-mm { color: rgba(15, 23, 42, 0.5); }
.footer-bar { border-top: 1px solid rgba(0,102,204,0.1); color: rgba(15, 23, 42, 0.4); }
div[data-testid="stMetric"] { background: rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.06); border-radius: 14px; padding: 1rem; }
[data-testid="stMetricLabel"] { color: rgba(15, 23, 42, 0.5) !important; font-size: 0.65rem !important; letter-spacing: 2px; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #0f172a !important; font-family: 'Space Mono', monospace !important; }
.stButton > button:hover { color: #0f172a !important; }
"""

# Inject dynamic CSS
selected_theme_css = DARK_CSS if is_dark else LIGHT_CSS
st.markdown(f"<style>{COMMON_CSS}{selected_theme_css}</style>", unsafe_allow_html=True)

# ─── ML Engine ────────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))

@st.cache_resource
def load_models():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s1 = joblib.load("stage1_classifier.pkl")
        s2 = joblib.load("stage2_regressor.pkl")
        fc = joblib.load("feature_cols.pkl")
        cfg = joblib.load("model_config.pkl")
    return s1, s2, fc, cfg

def now_ist():
    return pd.Timestamp.now(tz=IST).replace(tzinfo=None)

def rh_to_specific_humidity(rh_pct, temp_c, press_hpa):
    e_sat = 6.112 * np.exp((17.67 * temp_c) / (temp_c + 243.5))
    e_act = (rh_pct / 100.0) * e_sat
    q = (0.622 * e_act) / (press_hpa - 0.378 * e_act)
    return q

TRAIN_MEANS = {'Press_hPa': 1007.399, 'Spec_Hum': 0.01578, 'Temp_C': 26.152}

def log1p_safe(x):
    return np.log1p(np.maximum(x, 0))

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
        df[f'persist_{w}'] = sum((rain.shift(i) > 0.1).astype(float) for i in range(1, w+1)) / w
    df['consec_rain3'] = sum((rain.shift(i)>0.1).astype(float) for i in range(1,4))
    df['consec_rain6'] = sum((rain.shift(i)>0.1).astype(float) for i in range(1,7))
    hrs, last = [], 999
    for i in range(len(df)):
        if i == 0: hrs.append(999)
        elif rain.iloc[i-1] > 0.1: last = 0; hrs.append(0)
        else: last = min(last + 3, 999); hrs.append(last)
    df['hours_since_rain'] = hrs
    df['dry_spell_sq'] = np.sqrt(df['hours_since_rain'].clip(0, 200))
    df['last_rain_int'] = rain_s.where(rain_s > 0.1, np.nan).ffill().fillna(0)
    df['rain_momentum'] = (rain_s.rolling(2, min_periods=1).mean() - rain_s.rolling(8, min_periods=1).mean())
    for lag in [1,2,4,8,12]:
        df[f'Press_lag{lag}'] = df['Press_hPa'].shift(lag).fillna(TRAIN_MEANS['Press_hPa'])
    for d in [1,2,4,6,8,12]:
        df[f'Press_diff{d}'] = df['Press_hPa'].diff(d).fillna(0)
    df['press_accel'] = df['Press_hPa'].diff(1).fillna(0) - df['Press_hPa'].diff(2).fillna(0)
    for lag in [1,2,4,8]:
        df[f'Hum_lag{lag}'] = df['Spec_Hum'].shift(lag).fillna(TRAIN_MEANS['Spec_Hum'])
    df['hum_trend'] = df['Spec_Hum'].diff(1).fillna(0)
    df['hum_trend4'] = df['Spec_Hum'] - df['Spec_Hum'].shift(4).fillna(TRAIN_MEANS['Spec_Hum'])
    df['Spec_Hum_raw'] = df['Spec_Hum']
    df['Press_hPa_raw'] = df['Press_hPa']
    df['Temp_lag1'] = df['Temp_C'].shift(1).fillna(TRAIN_MEANS['Temp_C'])
    df['Temp_lag4'] = df['Temp_C'].shift(4).fillna(TRAIN_MEANS['Temp_C'])
    df['Temp_diff1'] = df['Temp_C'].diff(1).fillna(0)
    df['Temp_diff4'] = df['Temp_C'].diff(4).fillna(0)
    df['hum_x_rain1'] = df['Spec_Hum'] * log1p_safe(rain.shift(1).fillna(0))
    df['press_hum'] = df['Press_hPa'].diff(1).fillna(0) * df['Spec_Hum']
    df['temp_hum'] = df['Temp_C'] * df['Spec_Hum']
    df['hum_press_diff'] = df['Spec_Hum'] * df['Press_hPa'].diff(4).fillna(0)
    df['persist_hum'] = df['persist_4'] * df['Spec_Hum']
    df['hour_sin'] = np.sin(2*np.pi*df['time'].dt.hour/24)
    df['hour_cos'] = np.cos(2*np.pi*df['time'].dt.hour/24)
    df['month_sin'] = np.sin(2*np.pi*df['time'].dt.month/12)
    df['month_cos'] = np.cos(2*np.pi*df['time'].dt.month/12)
    df['dayofyear_sin'] = np.sin(2*np.pi*df['time'].dt.dayofyear/365)
    df['dayofyear_cos'] = np.cos(2*np.pi*df['time'].dt.dayofyear/365)
    df['is_monsoon'] = df['time'].dt.month.isin([6,7,8,9]).astype(float)
    df['is_morning'] = df['time'].dt.hour.isin([6,9,12]).astype(float)
    return df[feat_cols].values

def fetch_realtime_owm(api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": 22.5726, "lon": 88.3639, "appid": api_key, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return {
        'Temp_C': data['main']['temp'],
        'RH_pct': data['main']['humidity'],
        'Press_hPa': data['main']['pressure'],
        'Rain_mm': data.get('rain', {}).get('1h', 0.0),
        'description': data['weather'][0]['description'].title(),
        'wind_speed': data['wind'].get('speed', 0),
        'feels_like': data['main'].get('feels_like', data['main']['temp']),
        'visibility': data.get('visibility', 10000) / 1000,
    }

@st.cache_data(ttl=600)
def fetch_history_and_forecast(_api_key):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 22.5726, "longitude": 88.3639,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation",
        "past_days": 8, "forecast_days": 2, "timezone": "Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()['hourly']
    df = pd.DataFrame({
        'time': pd.to_datetime(data['time']),
        'Temp_C': data['temperature_2m'],
        'RH_pct': data['relative_humidity_2m'],
        'Press_hPa': data['surface_pressure'],
        'Rain_mm': data['precipitation'],
    })
    return df

def run_prediction(api_key):
    import warnings
    warnings.filterwarnings("ignore")
    stage1, stage2, feat_cols, config = load_models()
    THRESHOLD = config['threshold']

    df_raw = fetch_history_and_forecast(api_key)
    current_ist = now_ist()

    # Fetch real-time OWM
    rt = None
    try:
        rt = fetch_realtime_owm(api_key)
    except Exception:
        pass

    # Zero future rain
    df_raw.loc[df_raw['time'] > current_ist, 'Rain_mm'] = 0.0
    df_raw['Spec_Hum'] = rh_to_specific_humidity(df_raw['RH_pct'], df_raw['Temp_C'], df_raw['Press_hPa'])

    # Resample 3-hourly
    df_set = df_raw.set_index('time')
    df_3h = df_set.resample('3h').agg({
        'Temp_C': 'mean', 'Spec_Hum': 'mean', 'Press_hPa': 'mean', 'Rain_mm': 'sum'
    })
    df_3h['Rainfall_mm_hr'] = df_3h['Rain_mm'] / 3.0
    df_3h = df_3h.drop(columns=['Rain_mm']).dropna(subset=['Temp_C','Spec_Hum','Press_hPa']).reset_index()
    df_3h['Rainfall_mm_hr'] = df_3h['Rainfall_mm_hr'].fillna(0)

    # Split past / future
    df_past = df_3h[df_3h['time'] <= current_ist].copy()
    df_future = df_3h[df_3h['time'] > current_ist].head(8).copy()
    df_combined = pd.concat([df_past, df_future]).reset_index(drop=True)
    X_all = build_features(df_combined, feat_cols)

    # Current now (last past row)
    X_now = X_all[[len(df_past)-1], :]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        now_prob = stage1.predict_proba(X_now)[0, 1]
    now_flag = now_prob > THRESHOLD
    now_amount = 0.0
    if now_flag:
        now_amount = float(np.clip(np.expm1(stage2.predict(X_now)), 0, None))

    # Forecast
    n_past = len(df_past)
    X_future_arr = X_all[n_past:n_past+len(df_future), :]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        probs = stage1.predict_proba(X_future_arr)[:, 1]
        flags = probs > THRESHOLD
        amounts = np.zeros(len(df_future))
        if flags.sum() > 0:
            amounts[flags] = np.clip(np.expm1(stage2.predict(X_future_arr[flags])), 0, None)

    forecast_df = pd.DataFrame({
        'time_ist': df_future['time'].values,
        'rain_prob': np.round(probs * 100, 1),
        'rain_flag': flags,
        'rain_mm_hr': np.round(amounts, 3),
    })

    # Historical rain (last 48h)
    cutoff = current_ist - timedelta(hours=48)
    hist_df = df_past[df_past['time'] >= cutoff][['time', 'Rainfall_mm_hr', 'Temp_C', 'Press_hPa']].copy()

    return {
        'now_prob': round(float(now_prob) * 100, 1),
        'now_flag': bool(now_flag),
        'now_amount': round(now_amount, 3),
        'current_ist': current_ist,
        'forecast_df': forecast_df,
        'hist_df': hist_df,
        'rt': rt,
        'threshold': THRESHOLD,
        'config': config,
    }

# ─── App ──────────────────────────────────────────────────────────────────────

# Hero
OWM_KEY = "59a2e9f07edc1cab2cdf70f7bd3955b2"

st.markdown("""
<div class="hero">
  <div class="hero-top">
    <div class="city-block">
      <h1>🌧 Kolkata</h1>
      <div class="subtitle">Rain Intelligence Dashboard &nbsp;·&nbsp; 22.57°N 88.36°E</div>
      <div class="live-badge"><span class="live-dot"></span> Live AI Forecast</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner(""):
    try:
        import warnings
        warnings.filterwarnings("ignore")
        data = run_prediction(OWM_KEY)
    except Exception as e:
        import traceback
        st.error(f"⚠️ Error loading data: {e}")
        st.code(traceback.format_exc())
        st.stop()

prob = data['now_prob']
flag = data['now_flag']
amount = data['now_amount']
rt = data['rt']
forecast_df = data['forecast_df']
hist_df = data['hist_df']
current_ist = data['current_ist']

# Chart Colors based on theme
if is_dark:
    c_text = "rgba(160,210,255,0.4)"
    c_grid = "rgba(255,255,255,0.04)"
    c_hover_bg = "#0a1f3a"
    c_hover_txt = "#e8f4ff"
    c_temp = "rgba(255,160,50,0.5)"
    c_press = "rgba(180,140,255,0.4)"
else:
    c_text = "rgba(15,23,42,0.6)"
    c_grid = "rgba(0,0,0,0.06)"
    c_hover_bg = "#ffffff"
    c_hover_txt = "#0f172a"
    c_temp = "rgba(200,100,0,0.6)"
    c_press = "rgba(100,50,200,0.6)"


# Rain icon logic
def rain_icon(p, flag):
    if not flag:
        if p < 20: return "☀️"
        elif p < 40: return "🌤️"
        else: return "⛅"
    else:
        if amount < 1: return "🌦️"
        elif amount < 5: return "🌧️"
        else: return "⛈️"

icon = rain_icon(prob, flag)

# ─── Layout columns ───────────────────────────────────────────────────────────
left_col, right_col = st.columns([1.1, 2.6], gap="small")

with left_col:
    # Current prediction card
    meta_color = "rgba(160,210,255,0.3)" if is_dark else "rgba(15,23,42,0.4)"
    
    st.markdown(f"""
    <div class="left-panel">
      <div class="now-card">
        <div class="now-label">Now · {current_ist.strftime('%H:%M IST')}</div>
        <span class="rain-icon-big">{icon}</span>
        <div class="prob-number">{prob}<span class="prob-unit">%</span></div>
        <div class="prob-label">Probability of Rain</div>
      </div>

      <div class="stat-grid">
        <div class="stat-pill">
          <span class="s-val">{f"{amount:.2f}" if flag else "0.00"}</span>
          <span class="s-lbl">mm / hr</span>
        </div>
        <div class="stat-pill">
          <span class="s-val">{f"{rt['Temp_C']:.1f}°C" if rt else "—"}</span>
          <span class="s-lbl">Temp</span>
        </div>
        <div class="stat-pill">
          <span class="s-val">{f"{rt['RH_pct']:.0f}%" if rt else "—"}</span>
          <span class="s-lbl">Humidity</span>
        </div>
        <div class="stat-pill">
          <span class="s-val">{f"{rt['Press_hPa']:.0f}" if rt else "—"}</span>
          <span class="s-lbl">hPa</span>
        </div>
        <div class="stat-pill">
          <span class="s-val">{f"{rt['wind_speed']:.1f}" if rt else "—"}</span>
          <span class="s-lbl">m/s Wind</span>
        </div>
        <div class="stat-pill">
          <span class="s-val">{f"{rt['visibility']:.1f}" if rt else "—"}</span>
          <span class="s-lbl">km Vis.</span>
        </div>
      </div>

      {"<div class='alert-rain'>🌧 <b>Rain Alert</b> — Model predicts active rainfall. Intensity: <b>" + str(amount) + " mm/hr</b>. Carry an umbrella.</div>" if flag else "<div class='alert-no-rain'>☀️ Conditions look dry right now. No rain predicted for this period.</div>"}

      <div style="font-family:'Space Mono',monospace;font-size:0.58rem;color:{meta_color};line-height:1.8;padding-top:0.5rem;">
        MODEL · XGBoost Two-Stage<br>
        THRESHOLD · {data['threshold']:.4f}<br>
        TRAINED ON · {data['config']['trained_on']}<br>
        FEATURES · {data['config']['n_features']}<br>
        VAL F1 · {data['config']['val_f1']:.4f}<br>
        TIMESTEP · {data['config']['timestep_hours']}h
      </div>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

    # ── 24h Forecast Timeline ──
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">24-Hour Forecast</span>
      <span class="sec-line"></span>
    </div>
    """, unsafe_allow_html=True)

    cards_html = '<div class="forecast-scroll">'
    for _, row in forecast_df.iterrows():
        t = pd.Timestamp(row['time_ist'])
        fc_icon = "🌧️" if row['rain_flag'] else ("🌤️" if row['rain_prob'] < 30 else "⛅")
        rain_cls = "rain" if row['rain_flag'] else ""
        cards_html += f"""
        <div class="fc-card {rain_cls}">
          <div class="fc-time">{t.strftime('%a')}<br>{t.strftime('%H:%M')}</div>
          <div class="fc-icon">{fc_icon}</div>
          <div class="fc-prob">{row['rain_prob']:.0f}%</div>
          <div class="fc-mm">{row['rain_mm_hr']:.2f} mm/hr</div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Forecast Probability Chart ──
    st.markdown("""
    <div class="sec-header" style="margin-top:1.5rem;">
      <span class="sec-title">Rain Probability Curve</span>
      <span class="sec-line"></span>
    </div>
    """, unsafe_allow_html=True)

    times_fc = [pd.Timestamp(t).strftime('%d %b %H:%M') for t in forecast_df['time_ist']]
    fig_fc = go.Figure()

    # Threshold line
    th_line = "rgba(255,200,0,0.3)" if is_dark else "rgba(200,120,0,0.5)"
    th_text = "rgba(255,200,100,0.5)" if is_dark else "rgba(200,120,0,0.7)"
    
    fig_fc.add_hline(y=data['threshold']*100, line_dash="dot", line_color=th_line,
                     annotation_text=f"Threshold {data['threshold']*100:.1f}%",
                     annotation=dict(font=dict(color=th_text, size=10)))

    # Fill area
    fig_fc.add_trace(go.Scatter(
        x=times_fc, y=forecast_df['rain_prob'],
        fill='tozeroy',
        fillcolor='rgba(56,182,255,0.07)',
        line=dict(color='rgba(56,182,255,0)', width=0),
        showlegend=False, hoverinfo='skip'
    ))

    # Line
    fig_fc.add_trace(go.Scatter(
        x=times_fc, y=forecast_df['rain_prob'],
        mode='lines+markers',
        line=dict(color='#38b6ff', width=2.5),
        marker=dict(
            size=[12 if f else 7 for f in forecast_df['rain_flag']],
            color=['#38b6ff' if f else ('#1a4a6e' if is_dark else '#e0f2fe') for f in forecast_df['rain_flag']],
            line=dict(color='#38b6ff', width=1.5)
        ),
        name='Rain Probability',
        hovertemplate='<b>%{x}</b><br>Probability: %{y:.1f}%<extra></extra>'
    ))

    fig_fc.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(range=[0, 105], ticksuffix='%', gridcolor=c_grid,
                   tickfont=dict(color=c_text, size=10, family='Space Mono'),
                   zeroline=False),
        xaxis=dict(gridcolor=c_grid, tickangle=-30,
                   tickfont=dict(color=c_text, size=9, family='Space Mono')),
        showlegend=False,
        hoverlabel=dict(bgcolor=c_hover_bg, font=dict(color=c_hover_txt), bordercolor='#38b6ff')
    )
    st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

    # ── Historical Rain Chart ──
    if not hist_df.empty:
        st.markdown("""
        <div class="sec-header">
          <span class="sec-title">Historical Rainfall · Last 48 Hours</span>
          <span class="sec-line"></span>
        </div>
        """, unsafe_allow_html=True)

        hist_times = [pd.Timestamp(t).strftime('%d %b %H:%M') for t in hist_df['time']]
        fig_hist = go.Figure()

        fig_hist.add_trace(go.Bar(
            x=hist_times, y=hist_df['Rainfall_mm_hr'],
            marker=dict(
                color=['rgba(56,182,255,0.7)' if v > 0.1 else 'rgba(56,182,255,0.12)'
                       for v in hist_df['Rainfall_mm_hr']],
                line=dict(color='rgba(56,182,255,0.2)', width=0.5)
            ),
            name='Rainfall',
            hovertemplate='<b>%{x}</b><br>%{y:.3f} mm/hr<extra></extra>'
        ))

        # Temp overlay
        fig_hist.add_trace(go.Scatter(
            x=hist_times, y=hist_df['Temp_C'],
            mode='lines', yaxis='y2',
            line=dict(color=c_temp, width=1.5, dash='dot'),
            name='Temp °C',
            hovertemplate='Temp: %{y:.1f}°C<extra></extra>'
        ))

        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=220, margin=dict(l=10, r=50, t=10, b=10),
            yaxis=dict(title='mm/hr', gridcolor=c_grid,
                       tickfont=dict(color=c_text, size=10, family='Space Mono'),
                       zeroline=False, title_font=dict(color=c_text, size=10)),
            yaxis2=dict(title='°C', overlaying='y', side='right', showgrid=False,
                        tickfont=dict(color=c_temp, size=10, family='Space Mono'),
                        title_font=dict(color=c_temp, size=10)),
            xaxis=dict(gridcolor=c_grid, tickangle=-30,
                       tickfont=dict(color=c_text, size=9, family='Space Mono')),
            showlegend=False, barmode='overlay',
            hoverlabel=dict(bgcolor=c_hover_bg, font=dict(color=c_hover_txt), bordercolor='#38b6ff')
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

    # ── Pressure Trend ──
    if not hist_df.empty:
        st.markdown("""
        <div class="sec-header">
          <span class="sec-title">Pressure Trend · Last 48 Hours</span>
          <span class="sec-line"></span>
        </div>
        """, unsafe_allow_html=True)

        fig_press = go.Figure()
        fig_press.add_trace(go.Scatter(
            x=hist_times, y=hist_df['Press_hPa'],
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(120,60,255,0.05)',
            line=dict(color=c_press, width=2),
            hovertemplate='<b>%{x}</b><br>Pressure: %{y:.1f} hPa<extra></extra>'
        ))
        fig_press.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=160, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(gridcolor=c_grid,
                       tickfont=dict(color=c_press, size=10, family='Space Mono'),
                       zeroline=False, ticksuffix=' hPa'),
            xaxis=dict(gridcolor=c_grid, tickangle=-30,
                       tickfont=dict(color=c_text, size=9, family='Space Mono')),
            showlegend=False,
            hoverlabel=dict(bgcolor=c_hover_bg, font=dict(color=c_hover_txt), bordercolor='#a06cff')
        )
        st.plotly_chart(fig_press, use_container_width=True, config={'displayModeBar': False})

    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ──
rain_slots = int(forecast_df['rain_flag'].sum())
peak_prob = forecast_df['rain_prob'].max()
st.markdown(f"""
<div class="footer-bar">
  <span>Kolkata Rain Intelligence · ML-Powered</span>
  <span>Next 24h: {rain_slots}/8 slots with rain · Peak prob {peak_prob:.1f}%</span>
  <span>Updated · {current_ist.strftime('%d %b %Y %H:%M')} IST</span>
</div>
""", unsafe_allow_html=True)

# Refresh button
col1, col2, col3 = st.columns([3, 1, 3])
with col2:
    if st.button("↻ Refresh"):
        st.cache_data.clear()
        st.rerun()