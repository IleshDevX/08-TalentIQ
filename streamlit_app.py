"""
TalentIQ v4.0 — Redesigned Premium Dashboard
NLP-Based Resume Analyzer & Job Role Recommendation Platform

Complete UI/UX Redesign v4:
- Glassmorphism cards with depth layers
- Unified indigo/lavender design system
- Compact metric strips with animated rings
- Split-panel dashboard with clear hierarchy
- Animated section reveals & micro-interactions
- Streamlined 7-tab layout (merged JD+ATS)
- Responsive grid with CSS custom properties
- Performance-optimized: fewer DOM nodes, lazy charts

Run:  streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json
import plotly.graph_objects as go
import time
import math

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TalentIQ — AI Resume Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# Design System v4 — Complete CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ─── Fonts ────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ─── CSS Custom Properties ────────────────────────────────────────── */
:root {
    --primary: #6366F1;
    --primary-light: #818CF8;
    --primary-dark: #4F46E5;
    --primary-bg: #EEF2FF;
    --secondary: #A78BFA;
    --accent: #14B8A6;
    --accent-bg: #F0FDFA;
    --success: #10B981;
    --success-bg: #ECFDF5;
    --warning: #F59E0B;
    --warning-bg: #FFFBEB;
    --danger: #EF4444;
    --danger-bg: #FEF2F2;
    --surface: #FFFFFF;
    --surface-alt: #F8FAFC;
    --surface-raised: #FFFFFF;
    --border: #E2E8F0;
    --border-light: #F1F5F9;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted: #94A3B8;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.08);
    --shadow-glow: 0 4px 20px rgba(99,102,241,0.15);
    --transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}

/* ─── Global Reset ─────────────────────────────────────────────────── */
html, body, .main, .stApp {
    background: var(--surface-alt) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}
/* Sidebar toggle icon font */
[data-testid="collapsedControl"] span,
[data-testid="stSidebar"] button[kind="header"] span,
button[kind="headerNoPadding"] span {
    font-family: 'Material Symbols Rounded' !important;
    font-size: 24px !important; overflow: hidden !important;
    width: 24px !important; height: 24px !important;
    display: inline-block !important;
}
.main { padding: 0 !important; }
.block-container {
    padding: 1rem 2.5rem 3rem 2.5rem !important;
    max-width: 100% !important;
}
* { scrollbar-width: thin; scrollbar-color: #CBD5E1 transparent; }
*::-webkit-scrollbar { width: 5px; height: 5px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

/* ─── Hide Streamlit Chrome ────────────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
button[kind="header"] { visibility: visible !important; }
[data-testid="collapsedControl"] { visibility: visible !important; display: flex !important; }

/* ─── Top Banner ───────────────────────────────────────────────────── */
.top-banner {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 30%, #818CF8 60%, #A78BFA 100%);
    border-radius: var(--radius-xl);
    padding: 1.8rem 2.5rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
    position: relative; overflow: hidden;
    margin: 2.5rem 0 1.8rem 0;
}
.top-banner::before {
    content: ''; position: absolute; top: -60%; right: -10%;
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.top-banner::after {
    content: ''; position: absolute; bottom: -50%; left: 5%;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.banner-left { display: flex; align-items: center; gap: 14px; z-index: 1; }
.banner-logo {
    width: 52px; height: 52px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(12px);
    border: 1.5px solid rgba(255,255,255,0.25);
    border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
}
.banner-title {
    font-size: 1.8rem; font-weight: 800; color: #FFF;
    letter-spacing: -0.4px; margin: 0;
    text-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.banner-sub {
    font-size: 0.9rem; color: rgba(255,255,255,0.8);
    font-weight: 500; margin: 3px 0 0 0;
}
.banner-right { display: flex; align-items: center; gap: 12px; z-index: 1; }
.banner-pill {
    background: rgba(255,255,255,0.14);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    color: #FFF; font-size: 0.85rem; font-weight: 600;
    padding: 7px 16px; border-radius: var(--radius-sm);
    display: flex; align-items: center; gap: 6px;
}
.banner-dot {
    width: 7px; height: 7px; background: #4ADE80;
    border-radius: 50%; display: inline-block;
    box-shadow: 0 0 6px rgba(74,222,128,0.5);
    animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(74,222,128,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(74,222,128,0); }
}

/* ─── Score Ring (CSS only) ────────────────────────────────────────── */
.ring-row {
    display: flex; gap: 16px; flex-wrap: wrap;
    justify-content: center; margin: 0.8rem 0;
}
.ring-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.5rem;
    flex: 1 1 170px; max-width: 220px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    position: relative; overflow: hidden;
}
.ring-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-glow);
    border-color: #C7D2FE;
}
.ring-card::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
}
.ring-card.rc-indigo::after  { background: linear-gradient(90deg,#6366F1,#818CF8); }
.ring-card.rc-teal::after    { background: linear-gradient(90deg,#14B8A6,#5EEAD4); }
.ring-card.rc-blue::after    { background: linear-gradient(90deg,#3B82F6,#60A5FA); }
.ring-card.rc-purple::after  { background: linear-gradient(90deg,#8B5CF6,#A78BFA); }
.ring-card.rc-amber::after   { background: linear-gradient(90deg,#F59E0B,#FBBF24); }
.ring-card.rc-green::after   { background: linear-gradient(90deg,#10B981,#34D399); }
.ring-card.rc-coral::after   { background: linear-gradient(90deg,#F87171,#FCA5A5); }

.ring-svg { width: 90px; height: 90px; margin: 0 auto 10px auto; display: block; }
.ring-track { fill: none; stroke: #F1F5F9; stroke-width: 6; }
.ring-fill {
    fill: none; stroke-width: 6; stroke-linecap: round;
    transition: stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1);
    transform: rotate(-90deg); transform-origin: center;
}
.ring-pct {
    font-size: 1.05rem; font-weight: 800;
    fill: var(--text-primary);
    dominant-baseline: central; text-anchor: middle;
}
.ring-label {
    font-size: 0.82rem; font-weight: 700; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.5px; margin: 0;
}
.ring-sub {
    font-size: 0.75rem; color: var(--text-muted);
    margin-top: 3px;
}

/* ─── Section Headers ──────────────────────────────────────────────── */
.sec-header {
    display: flex; align-items: center; gap: 12px;
    margin: 1.8rem 0 1.2rem 0;
    padding-bottom: 0.8rem;
}
.sec-icon {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
}
.sec-title {
    font-size: 1.2rem; font-weight: 700;
    color: var(--text-primary); margin: 0;
}
.sec-badge {
    margin-left: auto;
    font-size: 0.82rem; font-weight: 700;
    padding: 4px 14px; border-radius: 20px;
}

/* ─── Glass Panel ──────────────────────────────────────────────────── */
.glass-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    margin-bottom: 1.2rem;
}
.glass-panel:hover {
    box-shadow: var(--shadow-md);
}
.glass-panel-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 1.2rem; padding-bottom: 0.8rem;
}
.gp-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.gp-title {
    font-size: 1.08rem; font-weight: 700;
    color: var(--text-primary); margin: 0;
}
.gp-count {
    margin-left: auto;
    font-size: 0.85rem; font-weight: 600;
    color: var(--primary); background: var(--primary-bg);
    padding: 4px 14px; border-radius: 10px;
}

/* ─── Chips ────────────────────────────────────────────────────────── */
.chip-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
    display: inline-flex; align-items: center;
    padding: 7px 14px; border-radius: 8px;
    font-size: 0.88rem; font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    cursor: default;
}
.chip:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.chip-default  { background: #EEF2FF; color: #4338CA; border: 1px solid #DDD6FE; }
.chip-matched  { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.chip-missing  { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.chip-soft     { background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD; }
.chip-trending { background: #FDF4FF; color: #A21CAF; border: 1px solid #F0ABFC; }

/* ─── Badges ───────────────────────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center;
    padding: 5px 14px; border-radius: 7px;
    font-weight: 700; font-size: 0.85rem; letter-spacing: 0.2px;
}
.badge-excellent { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.badge-good      { background: #FFFBEB; color: #A16207; border: 1px solid #FDE68A; }
.badge-fair      { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.badge-low       { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }

.badge-priority-high   { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
.badge-priority-medium { background: #FFFBEB; color: #A16207; border: 1px solid #FDE68A; }
.badge-priority-low    { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.badge-promotion { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.badge-lateral   { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.badge-pivot     { background: #FFFBEB; color: #A16207; border: 1px solid #FDE68A; }

/* ─── Insight Rows ─────────────────────────────────────────────────── */
.insight-row {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 14px 18px; border-radius: var(--radius-sm);
    margin: 6px 0; font-size: 1rem; color: var(--text-secondary);
    line-height: 1.6; border-left: 4px solid transparent;
    transition: background 0.15s ease;
}
.insight-row:hover { background: var(--surface-alt); }
.insight-row.ir-blue   { border-color: #60A5FA; background: #F0F7FF; }
.insight-row.ir-green  { border-color: #34D399; background: #F0FDF8; }
.insight-row.ir-amber  { border-color: #FBBF24; background: #FFFDF0; }
.insight-row.ir-red    { border-color: #F87171; background: #FFF5F5; }

/* ─── Big Score Hero ───────────────────────────────────────────────── */
.score-hero {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
    border-radius: var(--radius-lg);
    padding: 2.5rem; text-align: center;
    border: 1px solid #C7D2FE;
}
.score-hero-val {
    font-size: 3.8rem; font-weight: 900; line-height: 1; margin: 0;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.score-hero-label { font-size: 1.05rem; color: var(--primary); font-weight: 600; margin-top: 6px; }
.score-hero-sub { font-size: 0.9rem; color: var(--text-muted); margin-top: 3px; }

/* ─── Breakdown Bars ───────────────────────────────────────────────── */
.bd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.bd-item {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 18px 20px;
    transition: var(--transition);
}
.bd-item:hover { box-shadow: 0 4px 14px rgba(99,102,241,0.08); }
.bd-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.bd-label { font-size: 0.95rem; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; }
.bd-val { font-size: 1.15rem; font-weight: 800; }
.bd-track { height: 8px; background: #F1F5F9; border-radius: 99px; overflow: hidden; }
.bd-fill { height: 100%; border-radius: 99px; transition: width 1s cubic-bezier(0.4,0,0.2,1); }
.bd-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.bd-tag { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 3px 10px; border-radius: 99px; }

/* ─── Profile Info Items ───────────────────────────────────────────── */
.pi-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; font-size: 0.95rem;
}
.pi-item:last-child { }
.pi-bullet { color: var(--primary); font-weight: 800; margin-top: 2px; }
.pi-label { font-weight: 600; color: var(--text-primary); min-width: 130px; }
.pi-value { color: var(--text-secondary); flex: 1; }

/* ─── Check Items ──────────────────────────────────────────────────── */
.ck-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: var(--radius-sm);
    margin: 4px 0; font-size: 0.98rem; font-weight: 500;
    transition: background 0.15s;
}
.ck-item:hover { background: var(--surface-alt); }
.ck-pass { color: #047857; }
.ck-fail { color: #DC2626; }

/* ─── Timeline ─────────────────────────────────────────────────────── */
.tl-item {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 1rem 0; border-left: 2px solid var(--border);
    margin-left: 10px; padding-left: 20px; position: relative;
}
.tl-item::before {
    content: ''; position: absolute;
    left: -7px; top: 1.2rem;
    width: 12px; height: 12px; border-radius: 50%;
    border: 2.5px solid var(--primary); background: white;
}
.tl-item.tl-promo::before  { border-color: var(--success); background: var(--success-bg); }
.tl-item.tl-lat::before    { border-color: #3B82F6; background: #EFF6FF; }
.tl-item.tl-pivot::before  { border-color: var(--warning); background: var(--warning-bg); }
.tl-body { flex: 1; }
.tl-from { font-size: 0.92rem; color: var(--text-muted); font-weight: 500; }
.tl-to { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 3px 0 6px 0; }

/* ─── Action Cards ─────────────────────────────────────────────────── */
.act-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.3rem 1.5rem;
    margin-bottom: 10px; display: flex; align-items: flex-start; gap: 14px;
    transition: var(--transition);
}
.act-card:hover { border-color: #C7D2FE; box-shadow: 0 2px 10px rgba(99,102,241,0.08); }
.act-icon {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem; flex-shrink: 0;
}
.act-icon-high   { background: #FEF2F2; }
.act-icon-medium { background: #FFFBEB; }
.act-icon-low    { background: #ECFDF5; }
.act-body { flex: 1; }
.act-top { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.act-cat {
    font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.4px; color: var(--primary);
    background: var(--primary-bg); padding: 3px 10px; border-radius: 5px;
}
.act-msg { font-size: 1rem; color: #334155; font-weight: 500; line-height: 1.55; margin: 0; }
.act-impact { font-size: 0.88rem; color: var(--text-muted); margin-top: 4px; }

/* ─── Role Row ─────────────────────────────────────────────────────── */
.role-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 10px;
    transition: background 0.15s;
}
.role-row:hover { background: var(--surface-alt); }
.role-rank { width: 34px; text-align: center; font-size: 1.05rem; }
.role-name { font-weight: 600; color: var(--text-primary); font-size: 1.02rem; }

/* ─── Hero Section (Landing) ───────────────────────────────────────── */
.hero { text-align: center; padding: 4rem 1rem 2.5rem 1rem; }
.hero-title {
    font-size: 2.8rem; font-weight: 800; color: var(--text-primary);
    margin: 0 0 0.8rem 0; letter-spacing: -0.5px; line-height: 1.2;
}
.hero-title em {
    font-style: normal;
    background: linear-gradient(135deg,#6366F1,#8B5CF6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-desc {
    font-size: 1.15rem; color: var(--text-secondary); font-weight: 400;
    max-width: 680px; margin: 0 auto; line-height: 1.65;
}

/* ─── Feature Cards (Landing) ──────────────────────────────────────── */
.feat-card {
    background: var(--surface); border-radius: var(--radius-lg);
    padding: 2rem 1.5rem; border: 1px solid var(--border);
    box-shadow: var(--shadow-sm); text-align: center;
    height: 100%; transition: var(--transition);
}
.feat-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-glow); border-color: #C7D2FE;
}
.feat-icon {
    width: 60px; height: 60px; border-radius: var(--radius-md);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.6rem; margin-bottom: 1.2rem;
}
.feat-title { font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.6rem 0; }
.feat-desc { font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; margin: 0; }

/* ─── Tabs ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: var(--surface);
    border-radius: var(--radius-md); padding: 4px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm); overflow-x: auto;
}
.stTabs [data-baseweb="tab"] {
    height: 46px; border-radius: var(--radius-sm);
    color: var(--text-secondary); font-weight: 600; font-size: 0.95rem;
    padding: 0 20px; white-space: nowrap;
    border-bottom: none !important; transition: var(--transition);
}
.stTabs [data-baseweb="tab"]:hover { background: var(--surface-alt); color: var(--text-primary); }
.stTabs [aria-selected="true"] {
    background: var(--primary) !important; color: white !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ─── Buttons ──────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg,#6366F1,#818CF8) !important;
    color: white !important; border: none !important;
    border-radius: var(--radius-md) !important; font-weight: 700 !important;
    padding: 0.85rem 1.8rem !important; font-size: 1rem !important;
    transition: var(--transition) !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    background: linear-gradient(135deg,#4F46E5,#6366F1) !important;
}
.stButton > button p, .stButton > button span { color: white !important; }

.stDownloadButton > button {
    background: var(--surface) !important; color: var(--primary) !important;
    border: 1.5px solid #C7D2FE !important; border-radius: var(--radius-md) !important;
    font-weight: 600 !important; transition: var(--transition) !important;
}
.stDownloadButton > button:hover {
    background: var(--primary-bg) !important; border-color: var(--primary) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button p, .stDownloadButton > button span { color: var(--primary) !important; }

/* ─── Sidebar ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem !important; }

.sb-header {
    display: flex; align-items: center; gap: 10px;
    padding: 0.5rem 0 1rem 0;
    margin-bottom: 1rem;
}
.sb-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg,#6366F1,#818CF8);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.sb-name { font-size: 1.15rem; font-weight: 800; color: var(--text-primary); }
.sb-tag { font-size: 0.78rem; color: var(--text-muted); font-weight: 500; }

.sb-section {
    background: var(--surface-alt); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 0.9rem;
    margin-bottom: 0.8rem;
}
.sb-sec-title {
    font-size: 1rem; font-weight: 700; color: var(--text-primary);
    margin: 0 0 3px 0; display: flex; align-items: center; gap: 7px;
}
.sb-sec-desc { font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0.5rem; line-height: 1.45; }

/* ─── Sidebar Inputs ───────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    border: 1.5px dashed #C7D2FE !important;
    border-radius: var(--radius-sm) !important; background: #FAFAFF !important;
    padding: 0.7rem !important; transition: var(--transition) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--primary-light) !important; background: #F5F3FF !important;
}
[data-baseweb="select"] > div {
    border: 1.5px solid var(--border) !important; border-radius: var(--radius-sm) !important;
    background: var(--surface) !important; transition: border-color 0.2s !important;
    font-size: 0.88rem !important;
}
[data-baseweb="select"] > div:hover { border-color: var(--primary-light) !important; }
[data-baseweb="popover"], [data-baseweb="select"] [role="listbox"], [data-baseweb="menu"] { z-index: 999999 !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] { z-index: 999999 !important; }
[data-testid="stSidebar"] .stFileUploader label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stSelectbox label { font-size: 0.88rem !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stTextArea textarea {
    border: 1.5px solid var(--border) !important; border-radius: var(--radius-sm) !important;
    background: var(--surface) !important; padding: 0.75rem !important;
    font-size: 0.88rem !important; transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: var(--primary-light) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* ─── Progress Bar ─────────────────────────────────────────────────── */
.stProgress > div > div { background: #E8E0F0 !important; border-radius: 6px !important; height: 6px !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg,#818CF8,#A78BFA) !important;
    border-radius: 6px !important;
}

/* ─── Expander ─────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--surface-alt) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important; font-weight: 600 !important;
    color: var(--text-secondary) !important; font-size: 0.84rem !important;
}

/* ─── Typography ───────────────────────────────────────────────────── */
h1,h2,h3,h4,h5,h6 { color: var(--text-primary) !important; font-family: 'Inter', sans-serif !important; }
p, li, span { font-family: 'Inter', sans-serif !important; }

/* ─── Utilities ────────────────────────────────────────────────────── */
.divider { height: 0; background: none; margin: 1.5rem 0; }
.spacer-xs { height: 0.4rem; }
.spacer-sm { height: 0.7rem; }
.spacer-md { height: 1.4rem; }
.spacer-lg { height: 2.2rem; }

/* ─── Responsive ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .top-banner { padding: 1rem; border-radius: var(--radius-md); flex-wrap: wrap; gap: 10px; }
    .banner-right { flex-wrap: wrap; }
    .block-container { padding: 0.8rem 1rem 2rem 1rem !important; }
    .ring-card { max-width: 100%; }
    .bd-grid { grid-template-columns: 1fr; }
}

/* ─── Animations ───────────────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
.anim-up { animation: fadeUp 0.5s ease forwards; }
.anim-fade { animation: fadeIn 0.6s ease forwards; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_roles():
    try:
        resp = requests.get(f"{API_BASE}/roles", timeout=10)
        resp.raise_for_status()
        return resp.json().get("roles", [])
    except Exception:
        return []


def _clr(score: float) -> str:
    if score >= 80: return "#10B981"
    if score >= 60: return "#F59E0B"
    return "#EF4444"


def _label(score: float) -> str:
    if score >= 90: return "Excellent"
    if score >= 80: return "Strong"
    if score >= 70: return "Good"
    if score >= 60: return "Fair"
    if score >= 50: return "Needs Work"
    return "Low"


def _badge_cls(score: float) -> str:
    if score >= 80: return "badge-excellent"
    if score >= 60: return "badge-good"
    if score >= 40: return "badge-fair"
    return "badge-low"


# ─── SVG Ring Builder ──────────────────────────────────────────────────

def ring_svg(pct: float, color: str, size: int = 90, stroke: int = 6) -> str:
    r = (size - stroke) / 2
    circ = 2 * math.pi * r
    offset = circ * (1 - min(pct, 100) / 100)
    return (
        f'<svg class="ring-svg" viewBox="0 0 {size} {size}">'
        f'<circle class="ring-track" cx="{size/2}" cy="{size/2}" r="{r}"/>'
        f'<circle class="ring-fill" cx="{size/2}" cy="{size/2}" r="{r}" '
        f'stroke="{color}" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"/>'
        f'<text class="ring-pct" x="{size/2}" y="{size/2}">{pct:.0f}%</text>'
        f'</svg>'
    )


def render_ring_card(pct, label, sub, color, accent_cls):
    return (
        f'<div class="ring-card {accent_cls}">'
        f'{ring_svg(pct, color)}'
        f'<div class="ring-label">{label}</div>'
        f'<div class="ring-sub">{sub}</div>'
        f'</div>'
    )


# ─── Chart Builders ───────────────────────────────────────────────────────

def make_radar(categories, values, title=""):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(99,102,241,0.08)",
        line=dict(color="#6366F1", width=2.5),
        marker=dict(size=6, color="#6366F1"), name="Score",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#F1F5F9",
                            linecolor="#E5E7EB", tickfont=dict(size=9, color="#94A3B8")),
            angularaxis=dict(gridcolor="#F1F5F9", linecolor="#E5E7EB",
                             tickfont=dict(size=10, color="#64748B", family="Inter")),
            bgcolor="white",
        ),
        showlegend=False,
        title=dict(text=title, x=0.5, font=dict(size=12, color="#64748B", family="Inter")) if title else None,
        height=320, margin=dict(l=55, r=55, t=45, b=25),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter, sans-serif"},
    )
    return fig


def make_bar(labels, values, title="", color="auto"):
    bar_colors = []
    for v in values:
        if v >= 80:   bar_colors.append("#10B981")
        elif v >= 60: bar_colors.append("#6366F1")
        elif v >= 40: bar_colors.append("#F59E0B")
        else:         bar_colors.append("#F87171")

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=bar_colors if color == "auto" else color, cornerradius=4, line=dict(width=0)),
        text=[f"  {v:.0f}%" for v in values], textposition="outside",
        textfont=dict(color="#475569", size=11, family="Inter"),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=12, color="#64748B", family="Inter")) if title else None,
        xaxis=dict(range=[0, max(values) * 1.2 if values else 105], showgrid=True,
                   gridcolor="#F8FAFC", linecolor="#E5E7EB", zeroline=False, title="",
                   tickfont=dict(size=9, color="#94A3B8")),
        yaxis=dict(linecolor="#E5E7EB", tickfont=dict(size=11, color="#475569", family="Inter"), automargin=True),
        height=max(200, len(labels) * 38 + 60),
        margin=dict(l=10, r=40, t=35 if title else 8, b=15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
        font={"family": "Inter, sans-serif"}, bargap=0.3,
    )
    return fig


def make_gauge(value, title, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13, "color": "#64748B", "family": "Inter"}},
        number={"suffix": "%", "font": {"size": 22, "color": _clr(value), "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": "#E5E7EB",
                     "dtick": 25, "tickfont": {"size": 9, "color": "#94A3B8"}},
            "bar": {"color": _clr(value), "thickness": 0.45},
            "bgcolor": "#F8FAFC", "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "#FEF2F2"},
                {"range": [50, 70], "color": "#FFFBEB"},
                {"range": [70, 100],"color": "#ECFDF5"},
            ],
            "threshold": {"line": {"color": "#6366F1", "width": 2}, "thickness": 0.7, "value": value},
        },
    ))
    fig.update_layout(
        height=185, margin=dict(l=18, r=18, t=40, b=5),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter, sans-serif"},
    )
    return fig


# ─── Render Helpers ───────────────────────────────────────────────────────

def chips_html(skills, cls="chip-default"):
    c = "".join(f'<span class="chip {cls}">{s}</span>' for s in skills)
    return f'<div class="chip-wrap">{c}</div>'


def breakdown_html(breakdown: dict) -> str:
    _icons = {"skill": "🎯", "experience": "💼", "semantic": "🔗", "education": "🎓", "format": "📝"}
    _bg = {"skill": "#EEF2FF", "experience": "#FEF3C7", "semantic": "#F0FDFA", "education": "#FDF2F8", "format": "#F5F3FF"}
    html = '<div class="bd-grid">'
    for k, v in breakdown.items():
        label = k.replace("_", " ").title()
        val = v if isinstance(v, (int, float)) else 0
        key_lower = k.lower().split("_")[0]
        icon = _icons.get(key_lower, "📊")
        bg = _bg.get(key_lower, "#F1F5F9")
        if val >= 70:
            grad, col, tag_bg, tag_txt, tag_label = "linear-gradient(90deg,#34D399,#10B981)", "#10B981", "#ECFDF5", "#065F46", "Strong"
        elif val >= 45:
            grad, col, tag_bg, tag_txt, tag_label = "linear-gradient(90deg,#FBBF24,#F59E0B)", "#F59E0B", "#FFFBEB", "#92400E", "Average"
        else:
            grad, col, tag_bg, tag_txt, tag_label = "linear-gradient(90deg,#F87171,#EF4444)", "#EF4444", "#FEF2F2", "#991B1B", "Low"
        html += f'''
        <div class="bd-item">
            <div class="bd-head">
                <div class="bd-label"><span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:6px;background:{bg};font-size:0.7rem;">{icon}</span> {label}</div>
                <div class="bd-val" style="color:{col};">{val:.0f}%</div>
            </div>
            <div class="bd-track"><div class="bd-fill" style="width:{min(val,100):.0f}%;background:{grad};"></div></div>
            <div class="bd-foot">
                <span class="bd-tag" style="background:{tag_bg};color:{tag_txt};">{tag_label}</span>
                <span style="font-size:0.6rem;color:#94A3B8;">0 — 100</span>
            </div>
        </div>'''
    html += '</div>'
    return html


# ═══════════════════════════════════════════════════════════════════════════
# TOP BANNER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="top-banner anim-up">
  <div class="banner-left">
    <div class="banner-logo">🧠</div>
    <div>
      <div class="banner-title">TalentIQ</div>
      <div class="banner-sub">AI Resume Intelligence Platform</div>
    </div>
  </div>
  <div class="banner-right">
    <span class="banner-pill">⚙️ 19 AI Engines</span>
    <span class="banner-pill">🗂️ 86 Roles</span>
    <span class="banner-pill"><span class="banner-dot"></span> Online</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sb-header">
        <div class="sb-logo">🧠</div>
        <div>
            <div class="sb-name">TalentIQ</div>
            <div class="sb-tag">Career Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown("""
    <div class="sb-section">
        <div class="sb-sec-title">📄 Resume Upload</div>
        <div class="sb-sec-desc">PDF or DOCX — max 10 MB</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload resume", type=["pdf", "docx"],
        help="Maximum file size: 10 MB", label_visibility="collapsed",
    )

    # Target role
    st.markdown("""
    <div class="sb-section">
        <div class="sb-sec-title">🎯 Target Role</div>
        <div class="sb-sec-desc">Select a role or let AI auto-detect</div>
    </div>
    """, unsafe_allow_html=True)
    roles_data = fetch_roles()
    role_names = ["Auto-detect (Best Match)"] + [r["role_name"] for r in roles_data]
    selected_role = st.selectbox("Select target role", role_names, index=0, label_visibility="collapsed")
    if selected_role == "Auto-detect (Best Match)":
        selected_role = "Auto-detect (best match)"

    # JD
    st.markdown("""
    <div class="sb-section">
        <div class="sb-sec-title">📋 Job Description</div>
        <div class="sb-sec-desc">Optional — paste JD for comparison</div>
    </div>
    """, unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste job description", height=100,
        placeholder="Paste the job description here for precise matching...",
        label_visibility="collapsed",
    )

    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
    analyze_btn = st.button("🚀  Analyze Resume", type="primary", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# LANDING STATE
# ═══════════════════════════════════════════════════════════════════════════

if not uploaded_file and not analyze_btn:
    st.markdown("""
    <div class="hero anim-up">
        <div class="hero-title">Welcome to <em>TalentIQ</em></div>
        <div class="hero-desc">
            Upload your resume to unlock AI-powered career insights — skill gap analysis,
            role matching, ATS optimization, and personalized improvement roadmaps.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feat-card anim-up">
            <div class="feat-icon" style="background:#EEF2FF;">📊</div>
            <div class="feat-title">Smart Analysis</div>
            <div class="feat-desc">19 specialized AI engines analyze your resume — from ATS compatibility to skill gaps and career trajectory.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feat-card anim-up" style="animation-delay:0.1s;">
            <div class="feat-icon" style="background:#F0FDFA;">🎯</div>
            <div class="feat-title">Intelligent Matching</div>
            <div class="feat-desc">Semantic matching across 86 engineering & management roles using FAISS vector search technology.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feat-card anim-up" style="animation-delay:0.2s;">
            <div class="feat-icon" style="background:#FFFBEB;">📋</div>
            <div class="feat-title">JD Comparison</div>
            <div class="feat-desc">Compare your resume against job descriptions with keyword analysis and section-by-section scoring.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    st.info("👈 **Get Started** — Upload your resume in the sidebar and click **Analyze Resume**")


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

elif analyze_btn and uploaded_file:
    with st.spinner("Analyzing your resume with 19 AI engines..."):
        progress_bar = st.progress(0)
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        form_data = {}
        if selected_role != "Auto-detect (best match)":
            form_data["target_role"] = selected_role
        if jd_text and jd_text.strip():
            form_data["jd_text"] = jd_text.strip()
        progress_bar.progress(10)
        try:
            resp = requests.post(f"{API_BASE}/analyze", files=files, data=form_data, timeout=120)
            progress_bar.progress(90)
            resp.raise_for_status()
            report = resp.json()
            progress_bar.progress(100)
            time.sleep(0.3)
            progress_bar.empty()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to TalentIQ API. Ensure the server is running on port 8000.")
            st.code("python run.py", language="bash")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()
    if "error" in report and len(report) == 1:
        st.error(f"Analysis failed: {report['error']}")
        st.stop()
    st.session_state["report"] = report
    st.session_state["analyzed"] = True


# ═══════════════════════════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.get("analyzed") and "report" in st.session_state:
    report = st.session_state["report"]

    # ── Extract Data ──────────────────────────────────────────────
    meta          = report.get("meta", {})
    target_role   = meta.get("target_role", "N/A")
    jd_source     = meta.get("jd_source", "N/A")
    pipeline_time = meta.get("pipeline_time_seconds", 0)
    engines_count = meta.get("engines_executed", 19)

    ats            = report.get("ats_score", {})
    skill_gap      = report.get("skill_gap", {})
    soft_skill     = report.get("soft_skill", {})
    improvements   = report.get("improvements", {})
    industry       = report.get("industry_alignment", {})
    certifications = report.get("certifications", {})
    explanation    = report.get("explanation", {})
    career         = report.get("career_paths", {})
    role_matches   = report.get("role_matches", {})
    profile        = report.get("candidate_profile", {})
    jd_comp        = report.get("jd_comparison", {})
    ats_sim        = report.get("ats_simulation", {})

    ats_score_val     = ats.get("final_score", 0)
    coverage_pct      = skill_gap.get("coverage_percent", 0)
    jd_match_pct      = jd_comp.get("overall_match_percent", 0)
    ats_sim_score     = ats_sim.get("ats_compatibility_score", 0)
    soft_score        = soft_skill.get("composite_score", 0) if isinstance(soft_skill.get("composite_score"), (int, float)) else 50
    industry_score    = industry.get("alignment_score", 0) if isinstance(industry.get("alignment_score"), (int, float)) else 50
    improvement_score = improvements.get("improvement_score", 0)

    # ══════════════════════════════════════════════════════════════
    #  SCORE RING STRIP — compact horizontal KPI row
    # ══════════════════════════════════════════════════════════════

    rings = [
        (ats_score_val, "ATS Score",    _label(ats_score_val),    _clr(ats_score_val),    "rc-indigo"),
        (coverage_pct,  "Skill Match",  f"{len(skill_gap.get('matched_skills',[]))} found",  _clr(coverage_pct),  "rc-teal"),
        (jd_match_pct,  "JD Alignment", _label(jd_match_pct),     _clr(jd_match_pct),     "rc-blue"),
        (ats_sim_score, "ATS Sim",      _label(ats_sim_score),    _clr(ats_sim_score),    "rc-purple"),
        (soft_score,    "Soft Skills",  _label(soft_score),       _clr(soft_score),       "rc-green"),
        (industry_score,"Industry",     _label(industry_score),   _clr(industry_score),   "rc-amber"),
    ]
    ring_cards = "".join(render_ring_card(p, l, s, c, a) for p, l, s, c, a in rings)
    st.markdown(f'<div class="ring-row anim-up">{ring_cards}</div>', unsafe_allow_html=True)

    # Pipeline + Target meta row
    mt1, mt2, mt3 = st.columns(3)
    with mt1:
        st.markdown(f'''
        <div class="ring-card rc-green" style="max-width:100%;text-align:center;">
            <div style="font-size:2rem;font-weight:800;color:#10B981;margin-bottom:4px;">{pipeline_time:.1f}s</div>
            <div class="ring-label">Pipeline Time</div>
            <div class="ring-sub">{engines_count} engines executed</div>
        </div>''', unsafe_allow_html=True)
    with mt2:
        display_role = target_role if len(target_role) <= 22 else target_role[:20] + "…"
        st.markdown(f'''
        <div class="ring-card rc-coral" style="max-width:100%;text-align:center;">
            <div style="font-size:1.4rem;font-weight:800;color:#F87171;margin-bottom:4px;">{display_role}</div>
            <div class="ring-label">Target Role</div>
            <div class="ring-sub">{jd_source.replace("_"," ").title()}</div>
        </div>''', unsafe_allow_html=True)
    with mt3:
        st.markdown(f'''
        <div class="ring-card rc-amber" style="max-width:100%;text-align:center;">
            <div style="font-size:2rem;font-weight:800;color:#F59E0B;margin-bottom:4px;">{improvement_score:.0f}<span style="font-size:1.05rem;color:#94A3B8;">/100</span></div>
            <div class="ring-label">Resume Quality</div>
            <div class="ring-sub">{_label(improvement_score)}</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════

    tabs = st.tabs([
        "📊 Overview",
        "🎯 Role Match",
        "📋 JD & ATS",
        "🔧 Skills & Gaps",
        "📈 Career",
        "💡 Improve",
        "📄 Report",
    ])

    # ─────────────────────────────────────────────────────────
    # TAB 1 — Overview
    # ─────────────────────────────────────────────────────────
    with tabs[0]:
        ov_l, ov_r = st.columns([1, 1], gap="medium")

        # Left: Radar + Gauges
        with ov_l:
            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#EEF2FF;">🧬</div>
                    <div class="gp-title">Multi-Dimension Assessment</div>
                </div>
            </div>''', unsafe_allow_html=True)
            radar_cats = ["ATS Score", "Skill Match", "JD Align", "ATS Sim", "Soft Skills", "Industry"]
            radar_vals = [ats_score_val, coverage_pct, jd_match_pct, ats_sim_score, soft_score, industry_score]
            st.plotly_chart(make_radar(radar_cats, radar_vals), use_container_width=True, key="radar_ov")

        # Right: Role Explanation + ATS Breakdown
        with ov_r:
            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#F0FDFA;">🎯</div>
                    <div class="gp-title">Role Match Explanation</div>
                </div>
            </div>''', unsafe_allow_html=True)

            verdict   = explanation.get("verdict", "")
            reasoning = explanation.get("reasoning", [])
            if verdict:
                st.markdown(f"**{verdict}**")
            if reasoning:
                colors = ["ir-blue", "ir-green", "ir-amber", "ir-blue", "ir-green", "ir-amber"]
                for i, r in enumerate(reasoning):
                    cls = colors[i % len(colors)]
                    st.markdown(f'<div class="insight-row {cls}">{r}</div>', unsafe_allow_html=True)

            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

            # ATS Breakdown
            ats_bd = ats.get("breakdown", {})
            if ats_bd:
                st.markdown('''
                <div class="sec-header" style="margin-top:0.8rem;">
                    <div class="sec-icon" style="background:#EEF2FF;">📊</div>
                    <div class="sec-title">ATS Score Breakdown</div>
                </div>''', unsafe_allow_html=True)
                st.markdown(breakdown_html(ats_bd), unsafe_allow_html=True)

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # ── Candidate Profile ──────────────────────────────────
        st.markdown('''
        <div class="sec-header">
            <div class="sec-icon" style="background:#ECFDF5;">👤</div>
            <div class="sec-title">Candidate Profile</div>
        </div>''', unsafe_allow_html=True)

        pr1, pr2 = st.columns([1, 1], gap="medium")

        with pr1:
            # Education
            edu = profile.get("education", {})
            if isinstance(edu, dict):
                degrees = edu.get("degrees", [])
                institutions = edu.get("institutions", [])
                deg_count = len(degrees) if degrees else 0
                edu_html = f'''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#EEF2FF;">🎓</div>
                        <div class="gp-title">Education</div>
                        <div class="gp-count">{deg_count} Degree(s)</div>
                    </div>'''
                if degrees:
                    for d in degrees:
                        edu_html += f'<div class="pi-item"><span class="pi-bullet">●</span> <span>{d}</span></div>'
                else:
                    edu_html += '<div style="color:#94A3B8;font-style:italic;padding:8px 0;">No degrees detected</div>'
                if institutions:
                    edu_html += '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #F1F5F9;">'
                    edu_html += '<div style="font-size:0.72rem;font-weight:700;color:#6366F1;text-transform:uppercase;margin-bottom:6px;">Institutions</div>'
                    for inst in institutions[:4]:
                        edu_html += f'<div class="pi-item"><span class="pi-bullet">■</span> <span>{inst}</span></div>'
                    edu_html += '</div>'
                edu_html += '</div>'
                st.markdown(edu_html, unsafe_allow_html=True)

            # Experience
            exp = profile.get("experience", {})
            if isinstance(exp, dict):
                max_yrs = exp.get("max_years", 0)
                job_titles = exp.get("job_titles", [])
                exp_html = f'''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#FEF3C7;">💼</div>
                        <div class="gp-title">Experience</div>
                        <div class="gp-count">{max_yrs} Year(s)</div>
                    </div>
                    <div class="pi-item">
                        <span class="pi-label">Total Experience:</span>
                        <span class="pi-value" style="font-weight:700;color:#0F172A;">{max_yrs} years</span>
                    </div>'''
                if job_titles:
                    exp_html += '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #F1F5F9;">'
                    exp_html += '<div style="font-size:0.72rem;font-weight:700;color:#6366F1;text-transform:uppercase;margin-bottom:6px;">Roles Held</div>'
                    for jt in job_titles[:5]:
                        exp_html += f'<div class="pi-item"><span class="pi-bullet">▸</span> <span>{jt}</span></div>'
                    if len(job_titles) > 5:
                        exp_html += f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:6px;text-align:center;font-style:italic;">…and {len(job_titles)-5} more</div>'
                    exp_html += '</div>'
                exp_html += '</div>'
                st.markdown(exp_html, unsafe_allow_html=True)

        with pr2:
            # Skills
            raw_skills = profile.get("skills_normalized", profile.get("skills_raw", []))
            skills_count = len(raw_skills)
            sk_html = f'''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#F0FDFA;">🔧</div>
                    <div class="gp-title">Technical Skills</div>
                    <div class="gp-count">{skills_count} Skill(s)</div>
                </div>'''
            if raw_skills:
                sk_html += f'<div style="margin-top:4px;">{chips_html(raw_skills[:40])}</div>'
                if len(raw_skills) > 40:
                    sk_html += f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:8px;text-align:center;font-style:italic;">…and {len(raw_skills)-40} more</div>'
            else:
                sk_html += '<div style="color:#94A3B8;font-style:italic;text-align:center;padding:20px 0;">No skills detected</div>'
            sk_html += '</div>'
            st.markdown(sk_html, unsafe_allow_html=True)

            # Domain Keywords
            kw = profile.get("keywords", [])
            if kw:
                kw_html = f'''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#FDF2F8;">🏷️</div>
                        <div class="gp-title">Domain Keywords</div>
                        <div class="gp-count">{len(kw)} Keyword(s)</div>
                    </div>
                    <div style="margin-top:4px;">{chips_html(kw[:20])}</div>'''
                if len(kw) > 20:
                    kw_html += f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:8px;text-align:center;font-style:italic;">…and {len(kw)-20} more</div>'
                kw_html += '</div>'
                st.markdown(kw_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # TAB 2 — Role Matching
    # ─────────────────────────────────────────────────────────
    with tabs[1]:
        top_roles = role_matches.get("top_roles", [])
        if top_roles:
            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#EEF2FF;">🎯</div>
                    <div class="gp-title">Top Role Matches — Semantic Similarity</div>
                </div>
            </div>''', unsafe_allow_html=True)

            role_labels = [r["role_name"] for r in top_roles[:10]]
            role_scores = [r["score"] * 100 for r in top_roles[:10]]
            st.plotly_chart(
                make_bar(role_labels[::-1], role_scores[::-1], "", "auto"),
                use_container_width=True, key="bar_roles",
            )

            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#F0FDFA;">📋</div>
                    <div class="gp-title">Detailed Match List</div>
                </div>
            </div>''', unsafe_allow_html=True)

            for i, r in enumerate(top_roles[:10]):
                sc = r["score"] * 100
                rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                is_target = " &nbsp;⭐ <b>TARGET</b>" if r["role_name"].lower() == target_role.lower() else ""
                bcls = _badge_cls(sc)
                st.markdown(
                    f'<div class="role-row">'
                    f'<span class="role-rank">{rank}</span>'
                    f'<span class="badge {bcls}">{sc:.1f}%</span>'
                    f'<span class="role-name">{r["role_name"]}</span>'
                    f'{is_target}</div>', unsafe_allow_html=True,
                )
        else:
            st.info("No role matching data available.")

    # ─────────────────────────────────────────────────────────
    # TAB 3 — JD Comparison + ATS Simulation (merged)
    # ─────────────────────────────────────────────────────────
    with tabs[2]:
        # — JD Comparison Section —
        if jd_comp:
            overall = jd_comp.get("overall_match_percent", 0)
            st.markdown(f'''
            <div class="score-hero anim-up">
                <div class="score-hero-val">{overall:.1f}%</div>
                <div class="score-hero-label">Overall JD Match</div>
                <div class="score-hero-sub">{_label(overall)}</div>
            </div>''', unsafe_allow_html=True)
            st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

            jc1, jc2 = st.columns(2, gap="medium")
            with jc1:
                matched_kw = jd_comp.get("matched_keywords", [])
                st.markdown(f'''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#ECFDF5;">✅</div>
                        <div class="gp-title">Matched Keywords</div>
                        <div class="gp-count">{len(matched_kw)}</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                if matched_kw:
                    st.markdown(chips_html(matched_kw, "chip-matched"), unsafe_allow_html=True)
                else:
                    st.info("No matched keywords found.")
            with jc2:
                missing_kw = jd_comp.get("missing_keywords", [])
                st.markdown(f'''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#FFF7ED;">❌</div>
                        <div class="gp-title">Missing Keywords</div>
                        <div class="gp-count">{len(missing_kw)}</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                if missing_kw:
                    st.markdown(chips_html(missing_kw, "chip-missing"), unsafe_allow_html=True)
                else:
                    st.success("No missing keywords! Excellent coverage.")

            section_scores = jd_comp.get("section_scores", {})
            if section_scores:
                st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
                st.markdown('''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#F5F3FF;">📊</div>
                        <div class="gp-title">Section-wise Coverage</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                sec_labels = [k.replace("_", " ").title() for k in section_scores]
                sec_values = [v if isinstance(v, (int, float)) else 0 for v in section_scores.values()]
                st.plotly_chart(make_bar(sec_labels, sec_values, "", "auto"), use_container_width=True, key="bar_sec")
        else:
            st.info("No JD comparison data — paste a job description in the sidebar.")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # — ATS Simulation Section —
        st.markdown('''
        <div class="sec-header">
            <div class="sec-icon" style="background:#EEF2FF;">🤖</div>
            <div class="sec-title">ATS Simulation</div>
        </div>''', unsafe_allow_html=True)

        if ats_sim:
            a1, a2 = st.columns([1, 1], gap="medium")

            with a1:
                st.markdown('''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#EEF2FF;">🤖</div>
                        <div class="gp-title">ATS Compatibility</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                st.plotly_chart(make_gauge(ats_sim.get("ats_compatibility_score", 0), "Compatibility"), use_container_width=True, key="gauge_sim")

                kw_report = ats_sim.get("keyword_report", {})
                if kw_report:
                    found   = kw_report.get("found", [])
                    missing = kw_report.get("missing", [])
                    density = kw_report.get("density", 0)
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("Density", f"{density:.1f}%")
                    mc2.metric("Found", len(found))
                    mc3.metric("Missing", len(missing))
                    with st.expander("🔍 Found Keywords"):
                        st.markdown(chips_html(found, "chip-matched"), unsafe_allow_html=True)
                    with st.expander("⚠️ Missing Keywords"):
                        st.markdown(chips_html(missing, "chip-missing"), unsafe_allow_html=True)

            with a2:
                st.markdown('''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#F0FDFA;">📋</div>
                        <div class="gp-title">Section Completeness</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                sections = ats_sim.get("section_completeness", {})
                if sections:
                    for sec_name, found in sections.items():
                        label = sec_name.replace("_", " ").title()
                        cls = "ck-pass" if found else "ck-fail"
                        icon = "✅" if found else "❌"
                        st.markdown(f'<div class="ck-item {cls}">{icon} {label}</div>', unsafe_allow_html=True)

                readability = ats_sim.get("readability", {})
                if readability:
                    st.markdown('''
                    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #F1F5F9;">
                        <div style="font-size:0.78rem;font-weight:700;color:#475569;margin-bottom:8px;">📖 Readability</div>
                    </div>''', unsafe_allow_html=True)
                    r1, r2 = st.columns(2)
                    r1.metric("Score", f"{readability.get('score', 0):.0f}%")
                    r1.metric("Bullets", readability.get("bullet_count", 0))
                    r2.metric("Action Verbs", readability.get("action_verb_count", 0))
                    r2.metric("Quantified", readability.get("quantified_achievements", 0))

            risks  = ats_sim.get("formatting_risks", [])
            alerts = ats_sim.get("alerts", [])
            if risks or alerts:
                st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
                st.markdown('''
                <div class="glass-panel">
                    <div class="glass-panel-header">
                        <div class="gp-icon" style="background:#FEF2F2;">⚠️</div>
                        <div class="gp-title">Alerts & Risks</div>
                    </div>
                </div>''', unsafe_allow_html=True)
                for risk in risks:
                    st.markdown(f'<div class="insight-row ir-amber">⚠️ {risk}</div>', unsafe_allow_html=True)
                for alert in alerts:
                    st.markdown(f'<div class="insight-row ir-red">🚨 {alert}</div>', unsafe_allow_html=True)
        else:
            st.info("No ATS simulation data available.")

    # ─────────────────────────────────────────────────────────
    # TAB 4 — Skills & Gaps
    # ─────────────────────────────────────────────────────────
    with tabs[3]:
        s1, s2 = st.columns(2, gap="medium")

        with s1:
            matched = skill_gap.get("matched_skills", [])
            st.markdown(f'''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#ECFDF5;">✅</div>
                    <div class="gp-title">Matched Skills</div>
                    <div class="gp-count">{len(matched)}</div>
                </div>
            </div>''', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-bottom:0.5rem;"><span class="badge badge-excellent">Coverage: {coverage_pct:.1f}%</span></div>', unsafe_allow_html=True)
            if matched:
                st.markdown(chips_html(matched, "chip-matched"), unsafe_allow_html=True)

        with s2:
            missing = skill_gap.get("missing_skills", [])
            st.markdown(f'''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#FFF7ED;">❌</div>
                    <div class="gp-title">Missing Skills</div>
                    <div class="gp-count">{len(missing)}</div>
                </div>
            </div>''', unsafe_allow_html=True)
            if missing:
                st.markdown(chips_html(missing, "chip-missing"), unsafe_allow_html=True)
            else:
                st.success("You have all the required skills!")

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

        ss1, ss2 = st.columns(2, gap="medium")

        with ss1:
            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#F0F9FF;">💬</div>
                    <div class="gp-title">Soft Skills</div>
                </div>
            </div>''', unsafe_allow_html=True)
            detected_soft = soft_skill.get("detected", soft_skill.get("soft_skills", []))
            if isinstance(detected_soft, list) and detected_soft:
                st.markdown(chips_html(detected_soft, "chip-soft"), unsafe_allow_html=True)
            elif isinstance(detected_soft, dict):
                for cat, items in detected_soft.items():
                    st.markdown(f"**{cat}:**")
                    if isinstance(items, list):
                        st.markdown(chips_html(items, "chip-soft"), unsafe_allow_html=True)
            else:
                st.info("No soft skills detected.")

        with ss2:
            ia_score = industry.get("alignment_score", 0)
            st.markdown(f'''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#FFFBEB;">📈</div>
                    <div class="gp-title">Industry Alignment</div>
                    <div class="gp-count">{ia_score:.0f}%</div>
                </div>
            </div>''', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-bottom:0.5rem;"><span class="badge {_badge_cls(ia_score)}">Alignment: {ia_score:.1f}%</span></div>', unsafe_allow_html=True)
            aligned = industry.get("aligned_skills", [])
            if aligned:
                st.markdown(f"**High-Demand Skills ({len(aligned)}):**")
                st.markdown(chips_html(aligned, "chip-matched"), unsafe_allow_html=True)
            trending = industry.get("trending_skills", [])
            if trending:
                st.markdown('<div style="margin-top:10px;padding-top:10px;border-top:1px solid #F1F5F9;font-size:0.82rem;font-weight:600;color:#475569;">🔥 Trending Skills</div>', unsafe_allow_html=True)
                st.markdown(chips_html(trending[:15], "chip-trending"), unsafe_allow_html=True)

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

        # Certifications
        st.markdown('''
        <div class="glass-panel">
            <div class="glass-panel-header">
                <div class="gp-icon" style="background:#FDF4FF;">🏆</div>
                <div class="gp-title">Certification Suggestions</div>
            </div>
        </div>''', unsafe_allow_html=True)
        cert_list = certifications.get("suggestions", certifications.get("certifications", []))
        if isinstance(cert_list, list) and cert_list:
            for cert in cert_list[:10]:
                if isinstance(cert, dict):
                    name     = cert.get("name", cert.get("certification", ""))
                    provider = cert.get("provider", "")
                    skill    = cert.get("for_skill", cert.get("skill", ""))
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #F8FAFC;">'
                        f'<span>🏆</span> <b>{name}</b>'
                        f' <span style="color:#94A3B8;">({provider})</span>'
                        f' <span class="badge badge-good">For: {skill}</span>'
                        f'</div>', unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"• {cert}")
        else:
            st.info("No certification suggestions at this time.")

    # ─────────────────────────────────────────────────────────
    # TAB 5 — Career Path
    # ─────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown('''
        <div class="glass-panel">
            <div class="glass-panel-header">
                <div class="gp-icon" style="background:#ECFDF5;">📈</div>
                <div class="gp-title">Career Progression Paths</div>
            </div>
        </div>''', unsafe_allow_html=True)

        paths = career.get("paths", career.get("career_paths", []))
        if isinstance(paths, list) and paths:
            for path in paths:
                if isinstance(path, dict):
                    from_role  = path.get("from_role", path.get("current", ""))
                    to_role    = path.get("to_role", path.get("next", ""))
                    transition = path.get("transition_type", path.get("type", ""))
                    if "promotion" in transition.lower():
                        tl_cls, bdg, ico = "tl-promo", "badge-promotion", "⬆️"
                    elif "lateral" in transition.lower():
                        tl_cls, bdg, ico = "tl-lat", "badge-lateral", "↔️"
                    else:
                        tl_cls, bdg, ico = "tl-pivot", "badge-pivot", "🔄"
                    st.markdown(f'''
                    <div class="tl-item {tl_cls}">
                        <div class="tl-body">
                            <div class="tl-from">{ico} From: {from_role}</div>
                            <div class="tl-to">{to_role}</div>
                            <span class="badge {bdg}">{transition}</span>
                        </div>
                    </div>''', unsafe_allow_html=True)
                else:
                    st.markdown(f"• {path}")
        else:
            st.info("No career path data available for this role.")

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # Role explanation
        st.markdown('''
        <div class="glass-panel">
            <div class="glass-panel-header">
                <div class="gp-icon" style="background:#EEF2FF;">🎯</div>
                <div class="gp-title">Role Match Reasoning</div>
            </div>
        </div>''', unsafe_allow_html=True)
        verdict = explanation.get("verdict", "")
        if verdict:
            st.markdown(f"**{verdict}**")
        detail = explanation.get("detail", explanation.get("reasoning", []))
        if isinstance(detail, list):
            for d in detail:
                st.markdown(f'<div class="insight-row ir-blue">{d}</div>', unsafe_allow_html=True)
        elif isinstance(detail, str):
            st.markdown(detail)

    # ─────────────────────────────────────────────────────────
    # TAB 6 — Improvements
    # ─────────────────────────────────────────────────────────
    with tabs[5]:
        if improvement_score:
            st.markdown(f'''
            <div class="score-hero anim-up">
                <div class="score-hero-val">{improvement_score:.0f}<span style="font-size:1.5rem;color:#94A3B8;">/100</span></div>
                <div class="score-hero-label">Resume Quality Score</div>
                <div class="score-hero-sub">{_label(improvement_score)}</div>
            </div>''', unsafe_allow_html=True)
            st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        st.markdown('''
        <div class="sec-header">
            <div class="sec-icon" style="background:#FFFBEB;">💡</div>
            <div class="sec-title">Improvement Suggestions</div>
        </div>''', unsafe_allow_html=True)

        suggestions = improvements.get("suggestions", improvements.get("improvements", []))
        if isinstance(suggestions, list) and suggestions:
            for s in suggestions:
                if isinstance(s, dict):
                    cat      = s.get("category", "General")
                    msg      = s.get("suggestion", s.get("message", ""))
                    priority = s.get("priority", "medium")
                    impact   = s.get("impact", "")
                    p_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                    icon_cls = f"act-icon-{priority}"
                    badge_cls = f"badge-priority-{priority}"
                    impact_h = f'<div class="act-impact">💡 {impact}</div>' if impact else ""
                    st.markdown(f'''
                    <div class="act-card">
                        <div class="act-icon {icon_cls}">{p_icon}</div>
                        <div class="act-body">
                            <div class="act-top">
                                <span class="act-cat">{cat.replace("_"," ").title()}</span>
                                <span class="badge {badge_cls}">{priority.upper()}</span>
                            </div>
                            <p class="act-msg">{msg}</p>
                            {impact_h}
                        </div>
                    </div>''', unsafe_allow_html=True)
                else:
                    st.markdown(f"• {s}")
        elif suggestions:
            st.markdown(str(suggestions))
        else:
            st.success("Your resume looks excellent! No major improvements needed.")

        # Feedback
        feedback_data = report.get("feedback", {})
        if feedback_data:
            st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
            st.markdown('''
            <div class="glass-panel">
                <div class="glass-panel-header">
                    <div class="gp-icon" style="background:#F0FDFA;">💬</div>
                    <div class="gp-title">Overall Feedback</div>
                </div>
            </div>''', unsafe_allow_html=True)
            summary = feedback_data.get("summary", "")
            if summary:
                st.markdown(summary)

    # ─────────────────────────────────────────────────────────
    # TAB 7 — Full Report
    # ─────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown('''
        <div class="glass-panel">
            <div class="glass-panel-header">
                <div class="gp-icon" style="background:#EEF2FF;">📄</div>
                <div class="gp-title">Complete Analysis Report</div>
            </div>
        </div>''', unsafe_allow_html=True)
        st.download_button(
            label="📥  Download Full Report (JSON)",
            data=json.dumps(report, indent=2, default=str),
            file_name=f"talentiq_report_{target_role.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        with st.expander("🔍 View Raw JSON Data", expanded=False):
            st.json(report)


# ── No File Warning ──────────────────────────────────────────────────────

elif analyze_btn and not uploaded_file:
    st.warning("Please upload a resume file in the sidebar first.")
