"""
TalentIQ v3.0 — Premium SaaS Dashboard
NLP-Based Resume Analyzer & Job Role Recommendation Platform

Complete UI/UX Redesign:
- Light pastel theme with soft indigo/lavender palette
- Card-based KPI dashboard
- Professional sticky navigation
- Clean typography hierarchy (Inter font)
- Responsive grid system (8px spacing)
- Timeline career paths, action-card improvements
- Smooth animations & micro-interactions

Run:  streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
import time

# ═══════════════════════════════════════════════════════════════════════════
# Configuration (unchanged)
# ═══════════════════════════════════════════════════════════════════════════

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TalentIQ — AI Resume Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# Premium Light Theme — Design System CSS
# ═══════════════════════════════════════════════════════════════════════════
#
# Design Tokens
#   Primary      : #6366F1  Soft Indigo
#   Secondary    : #818CF8  Lavender
#   Accent       : #14B8A6  Teal / Mint
#   Success      : #10B981  Soft Green
#   Warning      : #F59E0B  Soft Amber
#   Error        : #F87171  Soft Coral
#   Background   : #F8FAFC  Very-light gray
#   Card BG      : #FFFFFF  Pure white
#   Border       : #E5E7EB  Subtle gray
#   Text Primary : #1E293B
#   Text Sec.    : #475569
#   Text Muted   : #94A3B8
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ─── Font Import ──────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ─── Global ───────────────────────────────────────────────────────── */
html, body, .main, .stApp {
    background: #F8FAFC !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
/* Preserve Material Symbols icon font on Streamlit sidebar toggle */
[data-testid="collapsedControl"] span,
[data-testid="stSidebar"] button[kind="header"] span,
button[kind="headerNoPadding"] span {
    font-family: 'Material Symbols Rounded' !important;
    font-size: 24px !important;
    overflow: hidden !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
.main { padding: 0 !important; }
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 100% !important;
    position: relative; z-index: 0;
    isolation: isolate;
}
* { scrollbar-width: thin; scrollbar-color: #CBD5E1 transparent; }
*::-webkit-scrollbar { width: 6px; height: 6px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

/* ─── Hide Streamlit Chrome ────────────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
/* Keep sidebar toggle (collapse/expand) button visible */
button[kind="header"] { visibility: visible !important; }
[data-testid="stSidebar"][aria-expanded="false"] ~ section [data-testid="collapsedControl"] {
    visibility: visible !important; display: flex !important;
}
[data-testid="collapsedControl"] { visibility: visible !important; display: flex !important; }

/* ─── Top Navbar ───────────────────────────────────────────────────── */
.navbar-wrapper {
    margin: 3rem 0 1.5rem 0;
}
.navbar {
    background: linear-gradient(135deg, #6366F1 0%, #818CF8 40%, #A78BFA 70%, #C084FC 100%);
    border-radius: 18px;
    padding: 2rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25), 0 2px 8px rgba(99,102,241,0.15);
    position: relative; overflow: hidden;
    z-index: 999;
}
.navbar::before {
    content: '';
    position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.navbar::after {
    content: '';
    position: absolute; bottom: -40%; left: 10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.nav-brand { display: flex; align-items: center; gap: 12px; position: relative; z-index: 1; }
.nav-logo {
    width: 42px; height: 42px;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    border: 1.5px solid rgba(255,255,255,0.3);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; color: white;
}
.nav-title { font-size: 1.45rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px; margin: 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.nav-subtitle { font-size: 0.75rem; color: rgba(255,255,255,0.8); font-weight: 500; margin: 0.1rem 0 0 0; }
.nav-right { display: flex; align-items: center; gap: 12px; position: relative; z-index: 1; }
.nav-badge {
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.25);
    color: #FFFFFF;
    font-size: 0.7rem; font-weight: 600;
    padding: 5px 12px; border-radius: 8px;
}
.nav-status {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.76rem; color: rgba(255,255,255,0.9); font-weight: 500;
    background: rgba(255,255,255,0.12);
    padding: 5px 12px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
}
.nav-dot {
    width: 7px; height: 7px; background: #4ADE80;
    border-radius: 50%; display: inline-block;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.3);
}

/* ─── KPI Cards ────────────────────────────────────────────────────── */
.kpi-card {
    background: #FFFFFF; border-radius: 14px;
    padding: 1.2rem 1.3rem; border: 1px solid #E5E7EB;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.1);
    border-color: #C7D2FE;
}
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.kpi-indigo::before { background: linear-gradient(90deg,#6366F1,#818CF8); }
.kpi-card.kpi-teal::before   { background: linear-gradient(90deg,#14B8A6,#5EEAD4); }
.kpi-card.kpi-amber::before  { background: linear-gradient(90deg,#F59E0B,#FBBF24); }
.kpi-card.kpi-green::before  { background: linear-gradient(90deg,#10B981,#34D399); }
.kpi-card.kpi-coral::before  { background: linear-gradient(90deg,#F87171,#FCA5A5); }
.kpi-card.kpi-purple::before { background: linear-gradient(90deg,#8B5CF6,#A78BFA); }
.kpi-card.kpi-blue::before   { background: linear-gradient(90deg,#3B82F6,#60A5FA); }

.kpi-icon-wrap {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; margin-bottom: 0.7rem;
}
.kpi-icon-wrap.bg-indigo { background: #EEF2FF; }
.kpi-icon-wrap.bg-teal   { background: #F0FDFA; }
.kpi-icon-wrap.bg-amber  { background: #FFFBEB; }
.kpi-icon-wrap.bg-green  { background: #ECFDF5; }
.kpi-icon-wrap.bg-coral  { background: #FFF1F2; }
.kpi-icon-wrap.bg-purple { background: #F5F3FF; }
.kpi-icon-wrap.bg-blue   { background: #EFF6FF; }

.kpi-value { font-size: 1.65rem; font-weight: 800; color: #1E293B; line-height: 1; margin: 0 0 3px 0; }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.4px; margin: 0; }
.kpi-sub   { font-size: 0.68rem; color: #CBD5E1; margin-top: 2px; }

.kpi-progress { height: 4px; background: #F1F5F9; border-radius: 2px; overflow: hidden; margin-top: 8px; }
.kpi-progress-fill { height: 100%; border-radius: 2px; transition: width 0.8s ease; }

/* ─── Content Cards ────────────────────────────────────────────────── */
.card {
    background: transparent; border-radius: 14px;
    padding: 1.5rem; border: none;
    margin-bottom: 1rem;
}

.card-title {
    font-size: 0.95rem; font-weight: 700; color: #1E293B;
    margin: 0 0 1rem 0; padding-bottom: 0.7rem;
    border-bottom: 1px solid #F1F5F9;
    display: flex; align-items: center; gap: 8px;
}
.card-title-icon {
    width: 26px; height: 26px; border-radius: 7px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
}
.card-subtitle {
    font-size: 0.85rem; font-weight: 600; color: #475569;
    margin: 1.1rem 0 0.5rem 0;
}

/* ─── Feature Cards (Landing) ──────────────────────────────────────── */
.feature-card {
    background: #FFFFFF; border-radius: 16px;
    padding: 2rem; border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    text-align: center; height: 100%;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(99,102,241,0.12);
    border-color: #C7D2FE;
}
.feature-icon {
    width: 54px; height: 54px; border-radius: 14px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.5rem; margin-bottom: 1rem;
}
.fi-indigo { background: #EEF2FF; }
.fi-teal   { background: #F0FDFA; }
.fi-amber  { background: #FFFBEB; }
.feature-title { font-size: 1.02rem; font-weight: 700; color: #1E293B; margin: 0 0 0.5rem 0; }
.feature-desc  { font-size: 0.83rem; color: #64748B; line-height: 1.55; margin: 0; }

/* ─── Hero Section ─────────────────────────────────────────────────── */
.hero-section { text-align: center; padding: 3rem 1rem 2rem 1rem; }
.hero-title {
    font-size: 2.1rem; font-weight: 800; color: #1E293B;
    margin: 0 0 0.5rem 0; letter-spacing: -0.5px;
}
.hero-title span {
    background: linear-gradient(135deg,#6366F1,#8B5CF6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 1.02rem; color: #64748B; font-weight: 400;
    max-width: 600px; margin: 0 auto; line-height: 1.6;
}

/* ─── Chips ────────────────────────────────────────────────────────── */
.chip-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.4rem 0; }
.chip {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 12px; border-radius: 8px;
    font-size: 0.76rem; font-weight: 600;
    transition: transform 0.15s ease; cursor: default;
}
.chip:hover { transform: translateY(-1px); }
.chip-default  { background: #EEF2FF; color: #4338CA; border: 1px solid #DDD6FE; }
.chip-matched  { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.chip-missing  { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.chip-soft     { background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD; }
.chip-trending { background: #FDF4FF; color: #A21CAF; border: 1px solid #F0ABFC; }

/* ─── Badges ───────────────────────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 6px;
    font-weight: 700; font-size: 0.73rem; letter-spacing: 0.2px;
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

/* ─── Alerts ───────────────────────────────────────────────────────── */
.alert {
    border-radius: 10px; padding: 0.8rem 1.1rem; margin: 0.4rem 0;
    font-size: 0.83rem; border-left: 4px solid;
    display: flex; align-items: flex-start; gap: 8px; line-height: 1.5;
}
.alert-info    { background: #EFF6FF; border-color: #60A5FA; color: #1E3A8A; }
.alert-success { background: #ECFDF5; border-color: #34D399; color: #065F46; }
.alert-warning { background: #FFFBEB; border-color: #FBBF24; color: #92400E; }
.alert-danger  { background: #FEF2F2; border-color: #F87171; color: #991B1B; }

/* ─── Check Items ──────────────────────────────────────────────────── */
.check-item {
    display: flex; align-items: center; gap: 10px;
    padding: 0.55rem 0.75rem; border-radius: 8px;
    margin: 3px 0; font-size: 0.83rem; font-weight: 500;
    transition: background 0.15s;
}
.check-item:hover { background: #F8FAFC; }
.check-pass { color: #047857; }
.check-fail { color: #DC2626; }

/* ─── Timeline (Career Path) ──────────────────────────────────────── */
.timeline-item {
    display: flex; align-items: flex-start; gap: 16px;
    padding: 0.9rem 0; border-left: 2px solid #E5E7EB;
    margin-left: 11px; padding-left: 22px; position: relative;
}
.timeline-item::before {
    content: ''; position: absolute;
    left: -7px; top: 1.1rem;
    width: 12px; height: 12px; border-radius: 50%;
    border: 2px solid #6366F1; background: white;
}
.timeline-item.tl-promotion::before { border-color: #10B981; background: #ECFDF5; }
.timeline-item.tl-lateral::before   { border-color: #3B82F6; background: #EFF6FF; }
.timeline-item.tl-pivot::before     { border-color: #F59E0B; background: #FFFBEB; }
.timeline-content { flex: 1; }
.timeline-from { font-size: 0.8rem; color: #94A3B8; font-weight: 500; }
.timeline-to   { font-size: 0.95rem; font-weight: 700; color: #1E293B; margin: 2px 0 4px 0; }

/* ─── Action Cards (Improvements) ─────────────────────────────────── */
.action-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s ease;
    display: flex; align-items: flex-start; gap: 12px;
}
.action-card:hover { border-color: #C7D2FE; box-shadow: 0 2px 8px rgba(99,102,241,0.08); }
.action-icon {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0;
}
.action-icon-high   { background: #FEF2F2; }
.action-icon-medium { background: #FFFBEB; }
.action-icon-low    { background: #ECFDF5; }
.action-content { flex: 1; }
.action-header { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.action-cat {
    font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.4px; color: #6366F1;
    background: #EEF2FF; padding: 2px 7px; border-radius: 4px;
}
.action-msg { font-size: 0.85rem; color: #334155; font-weight: 500; line-height: 1.45; margin: 0; }
.action-impact { font-size: 0.76rem; color: #94A3B8; margin-top: 3px; }

/* ─── Big Score Card ───────────────────────────────────────────────── */
.big-score {
    background: linear-gradient(135deg,#EEF2FF,#E0E7FF);
    border-radius: 16px; padding: 1.8rem; text-align: center;
    border: 1px solid #C7D2FE;
}
.big-score-val { font-size: 2.8rem; font-weight: 900; color: #4F46E5; line-height: 1; margin: 0; }
.big-score-label { font-size: 0.85rem; color: #6366F1; font-weight: 600; margin-top: 4px; }
.big-score-sub { font-size: 0.75rem; color: #94A3B8; margin-top: 2px; }

/* ─── Role List Row ────────────────────────────────────────────────── */
.role-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 4px; border-bottom: 1px solid #F8FAFC;
}
.role-rank { width: 28px; text-align: center; font-size: 0.9rem; }
.role-name { font-weight: 600; color: #1E293B; font-size: 0.88rem; }

/* ─── Tabs ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: #FFFFFF;
    border-radius: 12px; padding: 5px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    overflow-x: auto;
    position: relative; z-index: 5;
}
.stTabs [data-baseweb="tab"] {
    height: 40px; border-radius: 8px;
    color: #64748B; font-weight: 600; font-size: 0.8rem;
    padding: 0 14px; white-space: nowrap;
    border-bottom: none !important;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover { background: #F1F5F9; color: #475569; }
.stTabs [aria-selected="true"] {
    background: #6366F1 !important; color: white !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] {
    position: relative; z-index: 1;
    padding-top: 1rem;
}

/* ─── Buttons ──────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg,#6366F1,#818CF8) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    padding: 0.7rem 1.5rem !important; font-size: 0.9rem !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    background: linear-gradient(135deg,#4F46E5,#6366F1) !important;
}
.stButton > button p,
.stButton > button span { color: white !important; }

.stDownloadButton > button {
    background: #FFFFFF !important; color: #6366F1 !important;
    border: 1.5px solid #C7D2FE !important; border-radius: 12px !important;
    font-weight: 600 !important; transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: #EEF2FF !important; border-color: #6366F1 !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button p,
.stDownloadButton > button span { color: #6366F1 !important; }

/* ─── Sidebar ──────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.4rem 1.1rem !important; }

.sb-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0.4rem 0 1.1rem 0;
    border-bottom: 1px solid #F1F5F9; margin-bottom: 1.1rem;
}
.sb-brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg,#6366F1,#818CF8);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.sb-brand-text { font-size: 1.2rem; font-weight: 800; color: #1E293B; }
.sb-brand-sub  { font-size: 0.8rem; color: #94A3B8; font-weight: 500; }

.sb-section {
    background: #F8FAFC; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 1rem;
    margin-bottom: 0.9rem;
    position: relative; z-index: 1;
}
.sb-section-header {
    font-size: 0.95rem; font-weight: 700; color: #1E293B;
    margin: 0 0 0.2rem 0;
    display: flex; align-items: center; gap: 6px;
}
.sb-section-desc { font-size: 0.85rem; color: #94A3B8; margin-bottom: 0.7rem; line-height: 1.4; }

/* ─── Sidebar Inputs ───────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    border: 1.5px dashed #C7D2FE !important;
    border-radius: 10px !important; background: #FAFAFF !important;
    padding: 0.7rem !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #818CF8 !important; background: #F5F3FF !important;
}
[data-baseweb="select"] > div {
    border: 1.5px solid #E5E7EB !important; border-radius: 10px !important;
    background: #FFFFFF !important; transition: border-color 0.2s !important;
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] .stFileUploader label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
[data-baseweb="select"] > div:hover { border-color: #818CF8 !important; }
/* Ensure dropdown popover sits above sidebar sections */
[data-baseweb="popover"],
[data-baseweb="select"] [role="listbox"],
[data-baseweb="menu"] {
    z-index: 999999 !important;
}
[data-testid="stSidebar"] [data-baseweb="popover"] {
    z-index: 999999 !important;
}


.stTextArea textarea {
    border: 1.5px solid #E5E7EB !important; border-radius: 10px !important;
    background: #FFFFFF !important; padding: 0.75rem !important;
    font-size: 0.9rem !important; transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #818CF8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* ─── Progress Bar (default Streamlit) ─────────────────────────────── */
.stProgress > div > div { background: #E8E0F0 !important; border-radius: 6px !important; height: 8px !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg,#818CF8,#A78BFA) !important;
    border-radius: 6px !important;
}

/* ─── ATS Breakdown Metric Bars ────────────────────────────────────── */
.ats-breakdown { display: flex; flex-direction: column; gap: 14px; margin-top: 12px; }
.ats-metric {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px;
    padding: 14px 18px; transition: box-shadow 0.2s ease;
}
.ats-metric:hover { box-shadow: 0 4px 14px rgba(99,102,241,0.10); }
.ats-metric-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px;
}
.ats-metric-label {
    font-size: 0.82rem; font-weight: 600; color: #475569;
    display: flex; align-items: center; gap: 6px;
}
.ats-metric-label .metric-icon {
    width: 22px; height: 22px; border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.7rem;
}
.ats-metric-value {
    font-size: 1.05rem; font-weight: 800; line-height: 1;
}
.ats-metric-track {
    height: 8px; background: #F1F5F9; border-radius: 99px;
    overflow: hidden; position: relative;
}
.ats-metric-fill {
    height: 100%; border-radius: 99px;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
.ats-metric-sub {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 6px;
}
.ats-metric-tag {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; padding: 2px 8px; border-radius: 99px;
}
.ats-metric-range {
    font-size: 0.62rem; color: #94A3B8; font-weight: 500;
}

/* ─── Score Metrics Cards ──────────────────────────────────────────── */
.score-metrics-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 16px; margin: 1rem 0;
}
@media (max-width: 1024px) {
    .score-metrics-grid { grid-template-columns: repeat(2, 1fr); }
}
.score-metric-card {
    background: linear-gradient(135deg, #FFFFFF, #FAFBFF);
    border: 1px solid #E5E7EB; border-radius: 14px;
    padding: 20px; text-align: center;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
.score-metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; background: linear-gradient(90deg, #6366F1, #818CF8);
    opacity: 0; transition: opacity 0.3s;
}
.score-metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(99,102,241,0.15);
    border-color: #C7D2FE;
}
.score-metric-card:hover::before { opacity: 1; }

.score-metric-icon {
    width: 48px; height: 48px; border-radius: 12px;
    margin: 0 auto 12px; display: flex;
    align-items: center; justify-content: center;
    font-size: 1.4rem;
}
.score-metric-value {
    font-size: 2.2rem; font-weight: 900; line-height: 1;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 8px 0;
}
.score-metric-label {
    font-size: 0.8rem; font-weight: 600; color: #64748B;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.score-metric-badge {
    display: inline-block; margin-top: 8px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700;
}

/* ─── Profile Info Cards ───────────────────────────────────────────── */
.profile-section {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 18px; margin-bottom: 16px;
    transition: box-shadow 0.2s ease;
}
.profile-section:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.profile-section-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 14px; padding-bottom: 10px;
    border-bottom: 2px solid #F1F5F9;
}
.profile-section-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.profile-section-title {
    font-size: 0.9rem; font-weight: 700; color: #1E293B;
    margin: 0;
}
.profile-section-count {
    margin-left: auto; font-size: 0.75rem; font-weight: 600;
    color: #6366F1; background: #EEF2FF;
    padding: 3px 10px; border-radius: 12px;
}
.profile-info-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 0; font-size: 0.84rem; color: #475569;
    border-bottom: 1px solid #F8FAFC;
}
.profile-info-item:last-child { border-bottom: none; }
.profile-info-bullet {
    color: #6366F1; font-weight: 900; margin-top: 2px;
}
.profile-info-label {
    font-weight: 600; color: #334155; min-width: 120px;
}
.profile-info-value {
    flex: 1; color: #64748B;
}

/* ─── Expander ─────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #F8FAFC !important; border: 1px solid #E5E7EB !important;
    border-radius: 10px !important; font-weight: 600 !important;
    color: #475569 !important; font-size: 0.85rem !important;
}

/* ─── Typography ───────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 { color: #1E293B !important; font-family: 'Inter', sans-serif !important; }
p, li, span { font-family: 'Inter', sans-serif !important; }

/* ─── Utilities ────────────────────────────────────────────────────── */
.divider { height: 1px; background: #E5E7EB; margin: 1.5rem 0; }
.spacer-xs { height: 0.5rem; }
.spacer-sm { height: 0.75rem; }
.spacer-md { height: 1.5rem; }
.spacer-lg { height: 2.5rem; }

/* ─── Responsive ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .navbar { padding: 0.9rem 1rem; border-radius: 12px; }
    .nav-right { gap: 6px; flex-wrap: wrap; }
    .block-container { padding: 1rem 1rem 2rem 1rem !important; }
}

/* ─── Animation ────────────────────────────────────────────────────── */
@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.anim-in { animation: fadeUp 0.4s ease forwards; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions — Logic UNCHANGED
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_roles():
    """Fetch available roles from the API."""
    try:
        resp = requests.get(f"{API_BASE}/roles", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("roles", [])
    except Exception:
        return []


def score_color(score: float) -> str:
    if score >= 80: return "#10B981"
    if score >= 60: return "#F59E0B"
    return "#EF4444"


def score_label(score: float) -> str:
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


# ─── Chart Builders ───────────────────────────────────────────────────────

def make_gauge(value: float, title: str, max_val: float = 100) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13, "color": "#64748B", "family": "Inter"}},
        number={"suffix": "%", "font": {"size": 24, "color": score_color(value), "family": "Inter"}},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": "#E5E7EB",
                     "dtick": 25, "tickfont": {"size": 9, "color": "#94A3B8"}},
            "bar": {"color": score_color(value), "thickness": 0.45},
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
        height=195, margin=dict(l=18, r=18, t=42, b=5),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter, sans-serif"},
    )
    return fig


def make_radar(categories: list, values: list, title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(99,102,241,0.1)",
        line=dict(color="#6366F1", width=2),
        marker=dict(size=5, color="#6366F1"), name="Score",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#F1F5F9",
                            linecolor="#E5E7EB", tickfont=dict(size=9, color="#94A3B8")),
            angularaxis=dict(gridcolor="#F1F5F9", linecolor="#E5E7EB",
                             tickfont=dict(size=10, color="#64748B")),
            bgcolor="white",
        ),
        showlegend=False,
        title=dict(text=title, x=0.5, font=dict(size=12, color="#64748B", family="Inter")),
        height=310, margin=dict(l=55, r=55, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter, sans-serif"},
    )
    return fig


def make_bar(labels: list, values: list, title: str = "", color: str = "#6366F1") -> go.Figure:
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
        margin=dict(l=10, r=40, t=35 if title else 8, b=18),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
        font={"family": "Inter, sans-serif"}, bargap=0.3,
    )
    return fig


# ─── Render Helpers ───────────────────────────────────────────────────────

def render_chips(skills: list, chip_class: str = "chip-default") -> str:
    chips = "".join(f'<span class="chip {chip_class}">{s}</span>' for s in skills)
    return f'<div class="chip-wrap">{chips}</div>'


def render_kpi(icon, value, label, sub="", color="indigo", progress=-1):
    progress_html = ""
    if progress >= 0:
        pct = min(progress, 100)
        bar_c = "#10B981" if pct >= 80 else "#6366F1" if pct >= 60 else "#F59E0B" if pct >= 40 else "#F87171"
        progress_html = (
            f'<div class="kpi-progress">'
            f'<div class="kpi-progress-fill" style="width:{pct}%;background:{bar_c};"></div>'
            f'</div>'
        )
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card kpi-{color}">'
        f'<div class="kpi-icon-wrap bg-{color}">{icon}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<p class="kpi-label">{label}</p>'
        f'{sub_html}{progress_html}'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════
# TOP NAVIGATION BAR
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="navbar-wrapper">
  <div class="navbar">
    <div class="nav-brand">
        <div class="nav-logo">🧠</div>
        <div>
            <div class="nav-title">TalentIQ</div>
            <div class="nav-subtitle">AI Resume Intelligence Platform</div>
        </div>
    </div>
    <div class="nav-right">
        <span class="nav-badge">19 AI Engines</span>
        <span class="nav-badge">86 Roles</span>
        <div class="nav-status"><span class="nav-dot"></span> System Ready</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Resume Input Panel
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-icon">🧠</div>
        <div>
            <div class="sb-brand-text">TalentIQ</div>
            <div class="sb-brand-sub">Career Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown("""
    <div class="sb-section">
        <div class="sb-section-header">📄 Resume Upload</div>
        <div class="sb-section-desc">Upload PDF or DOCX (max 10 MB)</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload resume", type=["pdf", "docx"],
        help="Maximum file size: 10 MB", label_visibility="collapsed",
    )

    # Target role
    st.markdown("""
    <div class="sb-section">
        <div class="sb-section-header">🎯 Target Role</div>
        <div class="sb-section-desc">Select a role or let AI auto-detect</div>
    </div>
    """, unsafe_allow_html=True)

    roles_data = fetch_roles()
    role_names = ["Auto-detect (Best Match)"] + [r["role_name"] for r in roles_data]
    selected_role = st.selectbox("Select target role", role_names, index=0, label_visibility="collapsed")
    if selected_role == "Auto-detect (Best Match)":
        selected_role = "Auto-detect (best match)"

    # Job description
    st.markdown("""
    <div class="sb-section">
        <div class="sb-section-header">📋 Job Description</div>
        <div class="sb-section-desc">Optional — paste JD for comparison</div>
    </div>
    """, unsafe_allow_html=True)

    jd_text = st.text_area(
        "Paste job description", height=110,
        placeholder="Paste the job description here for precise matching...",
        label_visibility="collapsed",
    )

    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

    analyze_btn = st.button("🚀 Analyze Resume", type="primary", width="stretch")

# ═══════════════════════════════════════════════════════════════════════════
# LANDING STATE
# ═══════════════════════════════════════════════════════════════════════════

if not uploaded_file and not analyze_btn:
    st.markdown("""
    <div class="hero-section anim-in">
        <div class="hero-title">Welcome to <span>TalentIQ</span></div>
        <div class="hero-subtitle">
            Upload your resume to unlock AI-powered career insights — skill gap analysis,
            role matching, ATS optimization, and personalized improvement roadmaps.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card anim-in">
            <div class="feature-icon fi-indigo">📊</div>
            <div class="feature-title">Smart Analysis</div>
            <div class="feature-desc">19 specialized AI engines analyze your resume — from ATS compatibility to skill gaps and career trajectory.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card anim-in">
            <div class="feature-icon fi-teal">🎯</div>
            <div class="feature-title">Intelligent Matching</div>
            <div class="feature-desc">Semantic matching across 86 engineering & management roles using FAISS vector search technology.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card anim-in">
            <div class="feature-icon fi-amber">📋</div>
            <div class="feature-title">JD Comparison</div>
            <div class="feature-desc">Compare your resume against job descriptions with keyword analysis and section-by-section scoring.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
    st.info("👈 **Get Started** — Upload your resume in the sidebar and click **Analyze Resume**")


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS EXECUTION — Logic UNCHANGED
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
            st.error("❌ Cannot connect to TalentIQ API. Ensure the server is running on port 8000.")
            st.code("python run.py", language="bash")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API Error: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
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

    # ── Extract Data (no logic change) ────────────────────────────────
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

    # ══════════════════════════════════════════════════════════════════
    # KPI ROW  (2 rows: 4 + 3, center-aligned)
    # ══════════════════════════════════════════════════════════════════

    # Row 1 — 4 KPI cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_kpi("📊", f"{ats_score_val:.0f}%", "ATS Score",
                               score_label(ats_score_val), "indigo", ats_score_val), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi("🔧", f"{coverage_pct:.0f}%", "Skill Coverage",
                               f"{len(skill_gap.get('matched_skills', []))} matched", "teal", coverage_pct), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi("📋", f"{jd_match_pct:.0f}%", "JD Match",
                               score_label(jd_match_pct), "blue", jd_match_pct), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi("🤖", f"{ats_sim_score:.0f}%", "ATS Sim",
                               score_label(ats_sim_score), "purple", ats_sim_score), unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

    # Row 2 — 3 KPI cards, centered with padding columns
    _pad_l, k5, k6, k7, _pad_r = st.columns([0.5, 1, 1, 1, 0.5])
    with k5:
        st.markdown(render_kpi("💡", f"{improvement_score:.0f}", "Quality",
                               "/ 100", "amber", improvement_score), unsafe_allow_html=True)
    with k6:
        st.markdown(render_kpi("⚡", f"{pipeline_time:.1f}s", "Pipeline",
                               f"{engines_count} engines", "green"), unsafe_allow_html=True)
    with k7:
        display_role = target_role[:13] if len(target_role) > 13 else target_role
        st.markdown(render_kpi("🎯", display_role, "Target Role",
                               jd_source.replace("_", " ").title()[:20], "coral"), unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════

    tabs = st.tabs([
        "📊 Dashboard",
        "🎯 Role Matching",
        "📋 JD Comparison",
        "🤖 ATS Simulation",
        "🔧 Skills",
        "📈 Career Path",
        "💡 Improvements",
        "📄 Full Report",
    ])

    # ─────────────────────────────────────────────────────────────────
    # TAB 1 : Dashboard Overview
    # ─────────────────────────────────────────────────────────────────
    with tabs[0]:
        col_l, col_r = st.columns([1, 1], gap="medium")

        with col_l:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#EEF2FF;">🧬</span> Multi-Dimension Assessment</div>', unsafe_allow_html=True)
            radar_cats = ["ATS Score", "Skill Coverage", "JD Match", "ATS Sim", "Soft Skills", "Industry"]
            radar_vals = [ats_score_val, coverage_pct, jd_match_pct, ats_sim_score, soft_score, industry_score]
            st.plotly_chart(make_radar(radar_cats, radar_vals), width="stretch", key="radar_main")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F0FDFA;">🎯</span> Role Match Explanation</div>', unsafe_allow_html=True)
            verdict   = explanation.get("verdict", "")
            reasoning = explanation.get("reasoning", [])
            if verdict:
                st.markdown(f"**{verdict}**")
            if reasoning:
                for r in reasoning:
                    st.markdown(f'<div class="alert alert-info">{r}</div>', unsafe_allow_html=True)

            st.markdown('<div class="card-subtitle">📊 ATS Score Breakdown</div>', unsafe_allow_html=True)
            ats_breakdown = ats.get("breakdown", {})
            if ats_breakdown:
                _icons = {"skill": "🎯", "experience": "💼", "semantic": "🔗", "education": "🎓", "format": "📝"}
                _bg    = {"skill": "#EEF2FF", "experience": "#FEF3C7", "semantic": "#F0FDFA", "education": "#FDF2F8", "format": "#F5F3FF"}
                _grad  = {
                    "green":  ("linear-gradient(90deg,#34D399,#10B981)", "#10B981", "#ECFDF5", "#065F46"),
                    "amber":  ("linear-gradient(90deg,#FBBF24,#F59E0B)", "#F59E0B", "#FFFBEB", "#92400E"),
                    "red":    ("linear-gradient(90deg,#F87171,#EF4444)", "#EF4444", "#FEF2F2", "#991B1B"),
                }
                breakdown_html = '<div class="ats-breakdown">'
                for k, v in ats_breakdown.items():
                    label = k.replace("_", " ").title()
                    val = v if isinstance(v, (int, float)) else 0
                    key_lower = k.lower().split("_")[0]
                    icon = _icons.get(key_lower, "📊")
                    bg   = _bg.get(key_lower, "#F1F5F9")
                    if val >= 70:
                        g = _grad["green"]
                        tag_label = "Strong"
                    elif val >= 45:
                        g = _grad["amber"]
                        tag_label = "Average"
                    else:
                        g = _grad["red"]
                        tag_label = "Low"
                    fill_grad, fill_col, tag_bg, tag_txt = g
                    breakdown_html += f'''
                    <div class="ats-metric">
                        <div class="ats-metric-header">
                            <div class="ats-metric-label">
                                <span class="metric-icon" style="background:{bg};">{icon}</span> {label}
                            </div>
                            <div class="ats-metric-value" style="color:{fill_col};">{val:.0f}%</div>
                        </div>
                        <div class="ats-metric-track">
                            <div class="ats-metric-fill" style="width:{min(val,100):.0f}%; background:{fill_grad};"></div>
                        </div>
                        <div class="ats-metric-sub">
                            <span class="ats-metric-tag" style="background:{tag_bg}; color:{tag_txt};">{tag_label}</span>
                            <span class="ats-metric-range">0 — 100</span>
                        </div>
                    </div>'''
                breakdown_html += '</div>'
                st.markdown(breakdown_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # Score Metrics - Modern Cards
        _metrics = [
            ("📊", ats_score_val, "ATS Score", "#EEF2FF", ats_score_val),
            ("🎯", coverage_pct, "Skill Match", "#ECFDF5", coverage_pct),
            ("📋", jd_match_pct, "JD Alignment", "#FFF7ED", jd_match_pct),
            ("🤖", ats_sim_score, "ATS Simulation", "#F0FDFA", ats_sim_score),
        ]
        metrics_html = '<div class="score-metrics-grid">'
        for icon, val, label, bg, score in _metrics:
            if score >= 80:
                badge = '<span class="score-metric-badge" style="background:#ECFDF5; color:#047857;">■ Excellent</span>'
            elif score >= 65:
                badge = '<span class="score-metric-badge" style="background:#FFFBEB; color:#A16207;">▲ Good</span>'
            elif score >= 50:
                badge = '<span class="score-metric-badge" style="background:#FFF7ED; color:#C2410C;">◆ Fair</span>'
            else:
                badge = '<span class="score-metric-badge" style="background:#FEF2F2; color:#DC2626;">● Low</span>'
            metrics_html += f'''
            <div class="score-metric-card">
                <div class="score-metric-icon" style="background:{bg};">{icon}</div>
                <div class="score-metric-value">{val:.1f}%</div>
                <div class="score-metric-label">{label}</div>
                {badge}
            </div>'''
        metrics_html += '</div>'
        st.markdown(metrics_html, unsafe_allow_html=True)

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # Detailed Gauges (collapsible/expandable)
        with st.expander("📈 Detailed Score Gauges", expanded=False):
            g1, g2, g3, g4 = st.columns(4)
            with g1: st.plotly_chart(make_gauge(ats_score_val, "ATS Score"), width="stretch", key="g_ats")
            with g2: st.plotly_chart(make_gauge(coverage_pct, "Skill Coverage"), width="stretch", key="g_sk")
            with g3: st.plotly_chart(make_gauge(jd_match_pct, "JD Match"), width="stretch", key="g_jd")
            with g4: st.plotly_chart(make_gauge(ats_sim_score, "ATS Sim"), width="stretch", key="g_sim")

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # Candidate Profile - Redesigned
        st.markdown('''
        <div style="margin-top: 2rem; margin-bottom: 1rem;">
            <div class="card-title" style="border-bottom: 2px solid #F1F5F9; padding-bottom: 0.8rem;">
                <span class="card-title-icon" style="background:#ECFDF5;">👤</span> 
                Candidate Profile Overview
            </div>
        </div>
        ''', unsafe_allow_html=True)
        prof1, prof2 = st.columns([1, 1], gap="medium")

        with prof1:
            # Education Card
            edu = profile.get("education", {})
            if isinstance(edu, dict):
                degrees = edu.get("degrees", [])
                institutions = edu.get("institutions", [])
                fields = edu.get("fields", [])
                deg_count = len(degrees) if degrees else 0
                
                edu_html = f'''
                <div class="profile-section">
                    <div class="profile-section-header">
                        <div class="profile-section-icon" style="background:#EEF2FF;">🎓</div>
                        <div class="profile-section-title">Education</div>
                        <div class="profile-section-count">{deg_count} Degree(s)</div>
                    </div>'''
                
                if degrees:
                    for d in degrees:
                        edu_html += f'<div class="profile-info-item"><span class="profile-info-bullet">●</span> <span>{d}</span></div>'
                else:
                    edu_html += '<div class="profile-info-item" style="color:#94A3B8; font-style:italic;"><span class="profile-info-bullet">○</span> No degrees detected</div>'
                
                if institutions:
                    edu_html += '<div style="margin-top:12px; padding-top:12px; border-top:1px solid #F1F5F9;">'
                    edu_html += '<div style="font-size:0.75rem; font-weight:700; color:#6366F1; text-transform:uppercase; margin-bottom:8px;">Institutions</div>'
                    for inst in institutions[:3]:
                        edu_html += f'<div class="profile-info-item"><span class="profile-info-bullet">■</span> <span>{inst}</span></div>'
                    edu_html += '</div>'
                
                edu_html += '</div>'
                st.markdown(edu_html, unsafe_allow_html=True)

            # Experience Card
            exp = profile.get("experience", {})
            if isinstance(exp, dict):
                max_yrs = exp.get("max_years", 0)
                job_titles = exp.get("job_titles", [])
                title_count = len(job_titles)
                
                exp_html = f'''
                <div class="profile-section">
                    <div class="profile-section-header">
                        <div class="profile-section-icon" style="background:#FEF3C7;">💼</div>
                        <div class="profile-section-title">Experience</div>
                        <div class="profile-section-count">{max_yrs} Year(s)</div>
                    </div>
                    <div class="profile-info-item">
                        <span class="profile-info-label">Total Experience:</span>
                        <span class="profile-info-value" style="font-weight:700; color:#1E293B;">{max_yrs} years</span>
                    </div>'''
                
                if job_titles:
                    exp_html += '<div style="margin-top:12px; padding-top:12px; border-top:1px solid #F1F5F9;">'
                    exp_html += '<div style="font-size:0.75rem; font-weight:700; color:#6366F1; text-transform:uppercase; margin-bottom:8px;">Roles Held</div>'
                    for jt in job_titles[:5]:
                        exp_html += f'<div class="profile-info-item"><span class="profile-info-bullet">▸</span> <span>{jt}</span></div>'
                    if len(job_titles) > 5:
                        exp_html += f'<div style="font-size:0.75rem; color:#94A3B8; margin-top:8px; text-align:center; font-style:italic;">...and {len(job_titles)-5} more</div>'
                    exp_html += '</div>'
                
                exp_html += '</div>'
                st.markdown(exp_html, unsafe_allow_html=True)

        with prof2:
            # Skills Card
            raw_skills = profile.get("skills_normalized", profile.get("skills_raw", []))
            skills_count = len(raw_skills)
            
            skills_html = f'''
            <div class="profile-section">
                <div class="profile-section-header">
                    <div class="profile-section-icon" style="background:#F0FDFA;">🔧</div>
                    <div class="profile-section-title">Technical Skills</div>
                    <div class="profile-section-count">{skills_count} Skill(s)</div>
                </div>'''
            
            if raw_skills:
                skills_html += f'<div style="margin-top:4px;">{render_chips(raw_skills[:40], "chip-default")}</div>'
                if len(raw_skills) > 40:
                    skills_html += f'<div style="font-size:0.75rem; color:#94A3B8; margin-top:10px; text-align:center; font-style:italic;">...and {len(raw_skills)-40} more skills</div>'
            else:
                skills_html += '<div style="color:#94A3B8; font-style:italic; text-align:center; padding:20px 0;">No skills detected</div>'
            
            skills_html += '</div>'
            st.markdown(skills_html, unsafe_allow_html=True)

            # Domain Keywords Card
            kw = profile.get("keywords", [])
            kw_count = len(kw)
            
            if kw:
                kw_html = f'''
                <div class="profile-section">
                    <div class="profile-section-header">
                        <div class="profile-section-icon" style="background:#FDF2F8;">🏷️</div>
                        <div class="profile-section-title">Domain Keywords</div>
                        <div class="profile-section-count">{kw_count} Keyword(s)</div>
                    </div>
                    <div style="margin-top:4px;">{render_chips(kw[:20], "chip-default")}</div>'''
                
                if len(kw) > 20:
                    kw_html += f'<div style="font-size:0.75rem; color:#94A3B8; margin-top:10px; text-align:center; font-style:italic;">...and {len(kw)-20} more keywords</div>'
                
                kw_html += '</div>'
                st.markdown(kw_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 2 : Role Matching
    # ─────────────────────────────────────────────────────────────────
    with tabs[1]:
        top_roles = role_matches.get("top_roles", [])
        if top_roles:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#EEF2FF;">🎯</span> Top Role Matches — Semantic Similarity</div>', unsafe_allow_html=True)
            role_labels = [r["role_name"] for r in top_roles[:10]]
            role_scores = [r["score"] * 100 for r in top_roles[:10]]
            st.plotly_chart(
                make_bar(role_labels[::-1], role_scores[::-1], "", "auto"),
                width="stretch", key="bar_roles",
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F0FDFA;">📋</span> Detailed Match List</div>', unsafe_allow_html=True)
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
                    f'{is_target}'
                    f'</div>', unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No role matching data available.")

    # ─────────────────────────────────────────────────────────────────
    # TAB 3 : JD Comparison
    # ─────────────────────────────────────────────────────────────────
    with tabs[2]:
        if jd_comp:
            overall = jd_comp.get("overall_match_percent", 0)

            st.markdown(f"""
            <div class="big-score anim-in">
                <div class="big-score-val">{overall:.1f}%</div>
                <div class="big-score-label">Overall JD Match</div>
                <div class="big-score-sub">{score_label(overall)}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

            jc1, jc2 = st.columns(2, gap="medium")
            with jc1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                matched_kw = jd_comp.get("matched_keywords", [])
                st.markdown(f'<div class="card-title"><span class="card-title-icon" style="background:#ECFDF5;">✅</span> Matched Keywords ({len(matched_kw)})</div>', unsafe_allow_html=True)
                if matched_kw:
                    st.markdown(render_chips(matched_kw, "chip-matched"), unsafe_allow_html=True)
                else:
                    st.info("No matched keywords found.")
                st.markdown('</div>', unsafe_allow_html=True)
            with jc2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                missing_kw = jd_comp.get("missing_keywords", [])
                st.markdown(f'<div class="card-title"><span class="card-title-icon" style="background:#FFF7ED;">❌</span> Missing Keywords ({len(missing_kw)})</div>', unsafe_allow_html=True)
                if missing_kw:
                    st.markdown(render_chips(missing_kw, "chip-missing"), unsafe_allow_html=True)
                else:
                    st.success("No missing keywords! Excellent coverage.")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
            section_scores = jd_comp.get("section_scores", {})
            if section_scores:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F5F3FF;">📊</span> Section-wise Coverage</div>', unsafe_allow_html=True)
                sec_labels = [k.replace("_", " ").title() for k in section_scores]
                sec_values = [v if isinstance(v, (int, float)) else 0 for v in section_scores.values()]
                st.plotly_chart(make_bar(sec_labels, sec_values, "", "auto"), width="stretch", key="bar_sec")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No JD comparison data available. Paste a job description in the sidebar for comparison.")

    # ─────────────────────────────────────────────────────────────────
    # TAB 4 : ATS Simulation
    # ─────────────────────────────────────────────────────────────────
    with tabs[3]:
        if ats_sim:
            a1, a2 = st.columns([1, 1], gap="medium")

            with a1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#EEF2FF;">🤖</span> ATS Compatibility</div>', unsafe_allow_html=True)
                st.plotly_chart(make_gauge(ats_sim.get("ats_compatibility_score", 0), "Compatibility"), width="stretch", key="gauge_ats_sim")

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
                        st.markdown(render_chips(found, "chip-matched"), unsafe_allow_html=True)
                    with st.expander("⚠️ Missing Keywords"):
                        st.markdown(render_chips(missing, "chip-missing"), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with a2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F0FDFA;">📋</span> Section Completeness</div>', unsafe_allow_html=True)
                sections = ats_sim.get("section_completeness", {})
                if sections:
                    for sec_name, found in sections.items():
                        label = sec_name.replace("_", " ").title()
                        cls = "check-pass" if found else "check-fail"
                        icon = "✅" if found else "❌"
                        st.markdown(f'<div class="check-item {cls}">{icon} {label}</div>', unsafe_allow_html=True)

                readability = ats_sim.get("readability", {})
                if readability:
                    st.markdown('<div class="card-subtitle">📖 Readability</div>', unsafe_allow_html=True)
                    r1, r2 = st.columns(2)
                    r1.metric("Score", f"{readability.get('score', 0):.0f}%")
                    r1.metric("Bullets", readability.get("bullet_count", 0))
                    r2.metric("Action Verbs", readability.get("action_verb_count", 0))
                    r2.metric("Quantified", readability.get("quantified_achievements", 0))
                st.markdown('</div>', unsafe_allow_html=True)

            risks  = ats_sim.get("formatting_risks", [])
            alerts = ats_sim.get("alerts", [])
            if risks or alerts:
                st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#FEF2F2;">⚠️</span> Alerts & Risks</div>', unsafe_allow_html=True)
                for risk in risks:
                    st.markdown(f'<div class="alert alert-warning">⚠️ {risk}</div>', unsafe_allow_html=True)
                for alert in alerts:
                    st.markdown(f'<div class="alert alert-danger">🚨 {alert}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No ATS simulation data available.")

    # ─────────────────────────────────────────────────────────────────
    # TAB 5 : Skills
    # ─────────────────────────────────────────────────────────────────
    with tabs[4]:
        s1, s2 = st.columns(2, gap="medium")

        # Matched Skills card
        with s1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            matched = skill_gap.get("matched_skills", [])
            st.markdown(f'<div class="card-title"><span class="card-title-icon" style="background:#ECFDF5;">✅</span> Matched Skills ({len(matched)})</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-bottom:0.7rem;"><span class="badge badge-excellent">Coverage: {coverage_pct:.1f}%</span></div>', unsafe_allow_html=True)
            if matched:
                st.markdown(render_chips(matched, "chip-matched"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Missing Skills card
        with s2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            missing = skill_gap.get("missing_skills", [])
            st.markdown(f'<div class="card-title"><span class="card-title-icon" style="background:#FFF7ED;">❌</span> Missing Skills ({len(missing)})</div>', unsafe_allow_html=True)
            if missing:
                st.markdown(render_chips(missing, "chip-missing"), unsafe_allow_html=True)
            else:
                st.success("You have all the required skills!")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

        ss1, ss2 = st.columns(2, gap="medium")

        # Soft Skills card
        with ss1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F0F9FF;">💬</span> Soft Skills</div>', unsafe_allow_html=True)
            detected_soft = soft_skill.get("detected", soft_skill.get("soft_skills", []))
            if isinstance(detected_soft, list) and detected_soft:
                st.markdown(render_chips(detected_soft, "chip-soft"), unsafe_allow_html=True)
            elif isinstance(detected_soft, dict):
                for cat, items in detected_soft.items():
                    st.markdown(f"**{cat}:**")
                    if isinstance(items, list):
                        st.markdown(render_chips(items, "chip-soft"), unsafe_allow_html=True)
            else:
                st.info("No soft skills detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Industry Alignment card
        with ss2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#FFFBEB;">📈</span> Industry Alignment</div>', unsafe_allow_html=True)
            ia_score = industry.get("alignment_score", 0)
            st.markdown(f'<div style="margin-bottom:0.7rem;"><span class="badge {_badge_cls(ia_score)}">Alignment: {ia_score:.1f}%</span></div>', unsafe_allow_html=True)
            aligned = industry.get("aligned_skills", [])
            if aligned:
                st.markdown(f"**High-Demand Skills ({len(aligned)}):**")
                st.markdown(render_chips(aligned, "chip-matched"), unsafe_allow_html=True)
            trending = industry.get("trending_skills", [])
            if trending:
                st.markdown('<div class="card-subtitle">🔥 Trending Skills to Learn</div>', unsafe_allow_html=True)
                st.markdown(render_chips(trending[:15], "chip-trending"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

        # Certifications card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#FDF4FF;">🏆</span> Certification Suggestions</div>', unsafe_allow_html=True)
        cert_list = certifications.get("suggestions", certifications.get("certifications", []))
        if isinstance(cert_list, list) and cert_list:
            for cert in cert_list[:10]:
                if isinstance(cert, dict):
                    name     = cert.get("name", cert.get("certification", ""))
                    provider = cert.get("provider", "")
                    skill    = cert.get("for_skill", cert.get("skill", ""))
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid #F8FAFC;">'
                        f'<span>🏆</span> <b>{name}</b>'
                        f' <span style="color:#94A3B8;">({provider})</span>'
                        f' <span class="badge badge-good">For: {skill}</span>'
                        f'</div>', unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"• {cert}")
        else:
            st.info("No certification suggestions at this time.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 6 : Career Path
    # ─────────────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#ECFDF5;">📈</span> Career Progression Paths</div>', unsafe_allow_html=True)

        paths = career.get("paths", career.get("career_paths", []))
        if isinstance(paths, list) and paths:
            for i, path in enumerate(paths):
                if isinstance(path, dict):
                    from_role  = path.get("from_role", path.get("current", ""))
                    to_role    = path.get("to_role", path.get("next", ""))
                    transition = path.get("transition_type", path.get("type", ""))

                    if "promotion" in transition.lower():
                        tl_cls = "tl-promotion"; bdg = "badge-promotion"; ico = "⬆️"
                    elif "lateral" in transition.lower():
                        tl_cls = "tl-lateral"; bdg = "badge-lateral"; ico = "↔️"
                    else:
                        tl_cls = "tl-pivot"; bdg = "badge-pivot"; ico = "🔄"

                    st.markdown(f"""
                    <div class="timeline-item {tl_cls}">
                        <div class="timeline-content">
                            <div class="timeline-from">{ico} From: {from_role}</div>
                            <div class="timeline-to">{to_role}</div>
                            <span class="badge {bdg}">{transition}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"• {path}")
        else:
            st.info("No career path data available for this role.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

        # Role explanation
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#EEF2FF;">🎯</span> Role Match Reasoning</div>', unsafe_allow_html=True)
        verdict = explanation.get("verdict", "")
        if verdict:
            st.markdown(f"**{verdict}**")
        detail = explanation.get("detail", explanation.get("reasoning", []))
        if isinstance(detail, list):
            for d in detail:
                st.markdown(f'<div class="alert alert-info">{d}</div>', unsafe_allow_html=True)
        elif isinstance(detail, str):
            st.markdown(detail)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 7 : Improvements
    # ─────────────────────────────────────────────────────────────────
    with tabs[6]:
        if improvement_score:
            st.markdown(f"""
            <div class="big-score anim-in">
                <div class="big-score-val">{improvement_score:.0f}<span style="font-size:1.4rem;color:#94A3B8;">/100</span></div>
                <div class="big-score-label">Resume Quality Score</div>
                <div class="big-score-sub">{score_label(improvement_score)}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#FFFBEB;">💡</span> Improvement Suggestions</div>', unsafe_allow_html=True)

        suggestions = improvements.get("suggestions", improvements.get("improvements", []))
        if isinstance(suggestions, list) and suggestions:
            for i, s in enumerate(suggestions):
                if isinstance(s, dict):
                    cat      = s.get("category", "General")
                    msg      = s.get("suggestion", s.get("message", ""))
                    priority = s.get("priority", "medium")
                    impact   = s.get("impact", "")
                    p_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                    icon_cls  = f"action-icon-{priority}"
                    badge_cls = f"badge-priority-{priority}"
                    impact_h  = f'<div class="action-impact">💡 {impact}</div>' if impact else ""
                    st.markdown(f"""
                    <div class="action-card">
                        <div class="action-icon {icon_cls}">{p_icon}</div>
                        <div class="action-content">
                            <div class="action-header">
                                <span class="action-cat">{cat.replace("_"," ").title()}</span>
                                <span class="badge {badge_cls}">{priority.upper()}</span>
                            </div>
                            <p class="action-msg">{msg}</p>
                            {impact_h}
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"• {s}")
        elif suggestions:
            st.markdown(str(suggestions))
        else:
            st.success("✅ Your resume looks excellent! No major improvements needed.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Feedback
        feedback_data = report.get("feedback", {})
        if feedback_data:
            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#F0FDFA;">💬</span> Overall Feedback</div>', unsafe_allow_html=True)
            summary = feedback_data.get("summary", "")
            if summary:
                st.markdown(summary)
            st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 8 : Full Report
    # ─────────────────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="card-title-icon" style="background:#EEF2FF;">📄</span> Complete Analysis Report</div>', unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json.dumps(report, indent=2, default=str),
            file_name=f"talentiq_report_{target_role.replace(' ', '_')}.json",
            mime="application/json",
            width="stretch",
        )
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        with st.expander("🔍 View Raw JSON Data", expanded=False):
            st.json(report)
        st.markdown('</div>', unsafe_allow_html=True)


# No file warning
elif analyze_btn and not uploaded_file:
    st.warning("⚠️ Please upload a resume file in the sidebar first!")
