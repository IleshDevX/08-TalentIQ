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
import streamlit.components.v1 as components
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
    padding: 1.4rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
    position: relative; overflow: hidden;
    margin: 1.8rem 0 1.4rem 0;
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
    justify-content: center; margin: 0.6rem 0;
}
.ring-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.2rem;
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

.ring-svg { width: 90px; height: 90px; margin: 0 auto 8px auto; display: block; }
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
    margin: 1.2rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
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
    padding: 1.2rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    margin-bottom: 0;
}
.glass-panel:hover {
    box-shadow: var(--shadow-md);
}
.glass-panel-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 0; padding-bottom: 0;
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

/* ─── Profile Cards (Candidate Profile) ────────────────────────────── */
.profile-grid {
    display: grid;
    gap: 1.2rem;
}
.profile-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 0;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}
.profile-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
    border-color: #C7D2FE;
}
.profile-card-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(to bottom, var(--surface) 0%, var(--surface-alt) 100%);
}
.pc-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    box-shadow: var(--shadow-sm);
}
.pc-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.pc-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
}
.pc-count {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--primary);
    margin: 0;
}
.profile-card-body {
    padding: 1.2rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.pc-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 6px 0;
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.5;
}
.pc-item-secondary {
    font-size: 0.88rem;
    color: var(--text-muted);
}
.pc-dot {
    width: 6px;
    height: 6px;
    background: var(--primary);
    border-radius: 50%;
    margin-top: 8px;
    flex-shrink: 0;
}
.pc-dot-secondary {
    width: 5px;
    height: 5px;
    background: var(--text-muted);
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}
.pc-divider {
    height: 1px;
    background: var(--border-light);
    margin: 8px 0;
}
.pc-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 4px 0 6px 0;
}
.pc-highlight {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: var(--primary-bg);
    border-radius: var(--radius-sm);
    margin-bottom: 4px;
}
.pc-highlight-label {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-secondary);
}
.pc-highlight-value {
    font-size: 0.9rem;
    font-weight: 800;
    color: var(--primary);
}
.pc-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.pc-empty {
    color: var(--text-muted);
    font-style: italic;
    text-align: center;
    padding: 20px 0;
    font-size: 0.92rem;
}
.pc-more {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: center;
    font-style: italic;
    margin-top: 8px;
}

/* ─── Report Grid (Fixed Layout) ────────────────────────────────────── */
.report-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1rem 0;
}
@media (max-width: 1400px) {
    .report-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 1024px) {
    .report-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
    .report-grid { grid-template-columns: 1fr; }
}

.report-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 0;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    display: flex;
    flex-direction: column;
    height: 280px;
    overflow: hidden;
    position: relative;
}
.report-box:hover {
    box-shadow: var(--shadow-md);
    border-color: #C7D2FE;
}
.report-box-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem 1.1rem;
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(to bottom, var(--surface) 0%, var(--surface-alt) 100%);
    flex-shrink: 0;
}
.rb-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.rb-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
    flex: 1;
}
.rb-badge {
    font-size: 0.8rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    flex-shrink: 0;
}
.report-box-body {
    padding: 1rem 1.1rem;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: #CBD5E1 #F1F5F9;
}
.report-box-body::-webkit-scrollbar {
    width: 6px;
}
.report-box-body::-webkit-scrollbar-track {
    background: #F1F5F9;
    border-radius: 10px;
}
.report-box-body::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 10px;
}
.report-box-body::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}
.rb-metric {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-bottom: 8px;
}
.rb-metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--primary);
    line-height: 1;
}
.rb-metric-unit {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 600;
}
.rb-metric-label {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-bottom: 12px;
}
.rb-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.rb-list-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.5;
    border-bottom: 1px solid var(--border-light);
}
.rb-list-item:last-child {
    border-bottom: none;
}
.rb-list-dot {
    width: 5px;
    height: 5px;
    background: var(--primary);
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}
.rb-list-text {
    flex: 1;
    word-wrap: break-word;
}
.rb-empty {
    color: var(--text-muted);
    font-style: italic;
    text-align: center;
    padding: 40px 10px;
    font-size: 0.88rem;
}
.rb-stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-light);
}
.rb-stat-row:last-child {
    border-bottom: none;
}
.rb-stat-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.rb-stat-value {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
}
.rb-progress {
    width: 100%;
    height: 6px;
    background: #F1F5F9;
    border-radius: 99px;
    overflow: hidden;
    margin: 8px 0;
}
.rb-progress-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s ease;
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
    padding: 10px 14px; border-radius: var(--radius-sm);
    margin: 10px 0; font-size: 1rem; color: var(--text-secondary);
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
    padding: 1.8rem; text-align: center;
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
.bd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.bd-item {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 14px 16px;
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
    padding: 6px 0; font-size: 0.95rem;
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
    padding: 0.7rem 0; border-left: 2px solid var(--border);
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
    border-radius: var(--radius-md); padding: 1rem 1.2rem;
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
    padding: 8px 10px;
    transition: background 0.15s;
}
.role-row:hover { background: var(--surface-alt); }
.role-rank { width: 34px; text-align: center; font-size: 1.05rem; }
.role-name { font-weight: 600; color: var(--text-primary); font-size: 1.02rem; }

/* ─── Hero Section (Landing) ───────────────────────────────────────── */
.hero { text-align: center; padding: 3rem 1rem 2rem 1rem; }
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
    padding: 1.5rem 1.2rem; border: 1px solid var(--border);
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
    font-size: 1.6rem; margin-bottom: 0.8rem;
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
.spacer-xs { height: 0.25rem; }
.spacer-sm { height: 0.5rem; }
.spacer-md { height: 0.8rem; }
.spacer-lg { height: 1.2rem; }

/* ─── Responsive ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .top-banner { padding: 1rem; border-radius: var(--radius-md); flex-wrap: wrap; gap: 10px; }
    .banner-right { flex-wrap: wrap; }
    .block-container { padding: 0.8rem 1rem 2rem 1rem !important; }
    .ring-card { max-width: 100%; }
    .bd-grid { grid-template-columns: 1fr; }
}

/* ─── Role Matches Redesign ───────────────────────────────────────── */
.featured-role-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 2px solid #E2E8F0;
    border-radius: var(--radius-xl);
    padding: 2rem;
    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.12);
    position: relative;
    overflow: hidden;
    transition: var(--transition);
}
.featured-role-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #6366F1, #8B5CF6, #A78BFA);
}
.featured-role-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 50px rgba(99, 102, 241, 0.18);
    border-color: #C7D2FE;
}
.featured-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #FEF3C7, #FDE68A);
    color: #92400E;
    padding: 8px 16px;
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    border: 1px solid #FCD34D;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
}
.featured-role-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    flex-wrap: wrap;
}
.featured-role-info {
    flex: 1;
    min-width: 300px;
}
.featured-role-category {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
}
.featured-role-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0 0 1rem 0;
    line-height: 1.2;
    letter-spacing: -0.5px;
}
.target-badge-featured {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    color: #065F46;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 700;
    border: 1px solid #A7F3D0;
}
.featured-score-ring {
    flex-shrink: 0;
}
.featured-role-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-light);
    flex-wrap: wrap;
    gap: 1rem;
}
.match-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    font-weight: 700;
    border: 1px solid currentColor;
    border-opacity: 0.2;
}
.match-rank {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 600;
}
.section-header-minimal {
    margin: 1.5rem 0 1rem 0;
}
.role-match-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.role-match-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    border-color: #C7D2FE;
}
.role-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.role-card-rank {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-muted);
    min-width: 32px;
}
.role-card-category {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid currentColor;
    border-opacity: 0.15;
}
.role-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.4;
    flex: 1;
}
.target-badge-card {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #ECFDF5;
    color: #065F46;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid #A7F3D0;
}
.role-card-score {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid var(--border-light);
}
.mini-progress-ring {
    display: flex;
    align-items: center;
    justify-content: center;
}
.role-card-strength {
    font-size: 0.85rem;
    font-weight: 700;
    text-align: center;
}
.more-roles-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 1.2rem;
    margin-top: 1rem;
    background: var(--surface-alt);
    border: 1px dashed var(--border);
    border-radius: var(--radius-lg);
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 600;
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


def _color_for_score(score: float) -> str:
    """Return color based on score for progress bars."""
    if score >= 80: return "#10B981"  # Green
    if score >= 60: return "#6366F1"  # Indigo
    if score >= 40: return "#F59E0B"  # Amber
    return "#F87171"  # Red


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
    """Create a modern radar/spider chart matching the UI theme."""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], 
        theta=categories + [categories[0]],
        fill="toself", 
        fillcolor="rgba(99,102,241,0.12)",
        line=dict(color="#6366F1", width=3),
        marker=dict(size=8, color="#6366F1", symbol='circle', line=dict(color='white', width=2)), 
        name="Score",
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                gridcolor="#E2E8F0",
                gridwidth=1,
                linecolor="#CBD5E1", 
                tickfont=dict(size=11, color="#94A3B8", family="Inter"),
                tickmode='linear',
                tick0=0,
                dtick=20
            ),
            angularaxis=dict(
                gridcolor="#E2E8F0", 
                gridwidth=1,
                linecolor="#CBD5E1",
                tickfont=dict(size=12, color="#475569", family="Inter", weight=600)
            ),
            bgcolor="rgba(255, 255, 255, 0.6)",
        ),
        showlegend=False,
        title=dict(
            text=title, 
            x=0, 
            xanchor='left', 
            font=dict(size=15, color="#475569", family="Inter", weight=700)
        ) if title and title.strip() else {},
        height=500, 
        margin=dict(l=80, r=80, t=60, b=60),
        paper_bgcolor="rgba(0,0,0,0)", 
        font={"family": "Inter, sans-serif"},
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#E2E8F0",
            font=dict(family="Inter", size=12, color="#0F172A")
        )
    )
    return fig


def make_bar(labels, values, title="", color="auto"):
    """Create a modern horizontal bar chart matching the UI theme."""
    bar_colors = []
    for v in values:
        if v >= 80:   bar_colors.append("#10B981")
        elif v >= 60: bar_colors.append("#6366F1")
        elif v >= 40: bar_colors.append("#F59E0B")
        else:         bar_colors.append("#F87171")

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(
            color=bar_colors if color == "auto" else color, 
            cornerradius=6,
            line=dict(width=0)
        ),
        text=[f"{v:.0f}%" for v in values], 
        textposition="outside",
        textfont=dict(color="#475569", size=12, family="Inter", weight=600),
        hovertemplate="<b>%{y}</b><br>Match Score: %{x:.1f}%<extra></extra>",
    ))
    
    fig.update_layout(
        title=dict(
            text=title, 
            x=0, 
            xanchor='left',
            font=dict(size=14, color="#475569", family="Inter", weight=600)
        ) if title and title.strip() else {},
        xaxis=dict(
            range=[0, max(values) * 1.15 if values else 105], 
            showgrid=True,
            gridcolor="#F1F5F9", 
            gridwidth=1,
            linecolor="#E2E8F0", 
            linewidth=1,
            zeroline=False, 
            title="",
            tickfont=dict(size=10, color="#94A3B8", family="Inter"),
            ticksuffix="%",
            showticksuffix="all"
        ),
        yaxis=dict(
            linecolor="#E2E8F0",
            linewidth=1,
            tickfont=dict(size=12, color="#475569", family="Inter", weight=500), 
            automargin=True,
            showgrid=False
        ),
        height=max(220, len(labels) * 42 + 80),
        margin=dict(l=10, r=60, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(255, 255, 255, 0.5)",
        font={"family": "Inter, sans-serif"}, 
        bargap=0.25,
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#E2E8F0",
            font=dict(family="Inter", size=12, color="#0F172A")
        )
    )
    
    # Hide Plotly toolbar and make chart non-editable
    config = {
        'displayModeBar': False,
        'staticPlot': False,
        'responsive': True
    }
    fig.update_layout(
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'])
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
            st.plotly_chart(
                make_radar(radar_cats, radar_vals, title="Performance Metrics"), 
                use_container_width=True, 
                key="radar_ov",
                config={'displayModeBar': False, 'staticPlot': False, 'responsive': True}
            )

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
                st.markdown(f'<div style="margin-top: 1.2rem; font-weight: 700; font-size: 1.05rem;">{verdict}</div>', unsafe_allow_html=True)
            if reasoning:
                colors = ["ir-blue", "ir-green", "ir-amber", "ir-blue", "ir-green", "ir-amber"]
                for i, r in enumerate(reasoning):
                    cls = colors[i % len(colors)]
                    st.markdown(f'<div class="insight-row {cls}">{r}</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

        # ATS Breakdown - Full Width
        ats_bd = ats.get("breakdown", {})
        if ats_bd:
            st.markdown('''
            <div class="sec-header">
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

        # Prepare all data first
        edu = profile.get("education", {})
        exp = profile.get("experience", {})
        raw_skills = profile.get("skills_normalized", profile.get("skills_raw", []))
        kw = profile.get("keywords", [])
        
        # Build Education HTML
        if isinstance(edu, dict):
            degrees = edu.get("degrees", [])
            institutions = edu.get("institutions", [])
            deg_count = len(degrees) if degrees else 0
            edu_html = f'''
            <div class="profile-card">
                <div class="profile-card-header">
                    <div class="pc-icon" style="background:#EEF2FF;">🎓</div>
                    <div class="pc-info">
                        <div class="pc-title">Education</div>
                        <div class="pc-count">{deg_count} Degree(s)</div>
                    </div>
                </div>
                <div class="profile-card-body">'''
            if degrees:
                for d in degrees:
                    edu_html += f'<div class="pc-item"><span class="pc-dot"></span><span>{d}</span></div>'
            else:
                edu_html += '<div class="pc-empty">No degrees detected</div>'
            if institutions:
                edu_html += '<div class="pc-divider"></div><div class="pc-section-label">INSTITUTIONS</div>'
                for inst in institutions[:4]:
                    edu_html += f'<div class="pc-item pc-item-secondary"><span class="pc-dot-secondary"></span><span>{inst}</span></div>'
            edu_html += '</div></div>'
        else:
            edu_html = ''

        # Build Experience HTML
        if isinstance(exp, dict):
            max_yrs = exp.get("max_years", 0)
            job_titles = exp.get("job_titles", [])
            exp_html = f'''
            <div class="profile-card">
                <div class="profile-card-header">
                    <div class="pc-icon" style="background:#FEF3C7;">💼</div>
                    <div class="pc-info">
                        <div class="pc-title">Experience</div>
                        <div class="pc-count">{max_yrs} Year(s)</div>
                    </div>
                </div>
                <div class="profile-card-body">
                    <div class="pc-highlight">
                        <span class="pc-highlight-label">Total Experience</span>
                        <span class="pc-highlight-value">{max_yrs} years</span>
                    </div>'''
            if job_titles:
                exp_html += '<div class="pc-divider"></div><div class="pc-section-label">ROLES HELD</div>'
                for jt in job_titles[:5]:
                    exp_html += f'<div class="pc-item"><span class="pc-dot"></span><span>{jt}</span></div>'
                if len(job_titles) > 5:
                    exp_html += f'<div class="pc-more">…and {len(job_titles)-5} more</div>'
            exp_html += '</div></div>'
        else:
            exp_html = ''

        # Build Skills HTML
        skills_count = len(raw_skills)
        sk_html = f'''
        <div class="profile-card">
            <div class="profile-card-header">
                <div class="pc-icon" style="background:#F0FDFA;">🔧</div>
                <div class="pc-info">
                    <div class="pc-title">Technical Skills</div>
                    <div class="pc-count">{skills_count} Skill(s)</div>
                </div>
            </div>
            <div class="profile-card-body">'''
        if raw_skills:
            sk_html += f'<div class="pc-chips">{chips_html(raw_skills[:40])}</div>'
            if len(raw_skills) > 40:
                sk_html += f'<div class="pc-more">…and {len(raw_skills)-40} more</div>'
        else:
            sk_html += '<div class="pc-empty">No skills detected</div>'
        sk_html += '</div></div>'

        # Build Keywords HTML
        if kw:
            kw_html = f'''
            <div class="profile-card">
                <div class="profile-card-header">
                    <div class="pc-icon" style="background:#FDF2F8;">🏷️</div>
                    <div class="pc-info">
                        <div class="pc-title">Domain Keywords</div>
                        <div class="pc-count">{len(kw)} Keyword(s)</div>
                    </div>
                </div>
                <div class="profile-card-body">
                    <div class="pc-chips">{chips_html(kw[:20])}</div>'''
            if len(kw) > 20:
                kw_html += f'<div class="pc-more">…and {len(kw)-20} more</div>'
            kw_html += '</div></div>'
        else:
            kw_html = ''

        # Display in balanced 2x2 grid
        st.markdown('<div class="profile-grid">', unsafe_allow_html=True)
        
        pr_row1_col1, pr_row1_col2 = st.columns(2, gap="medium")
        with pr_row1_col1:
            st.markdown(edu_html, unsafe_allow_html=True)
        with pr_row1_col2:
            st.markdown(sk_html, unsafe_allow_html=True)
        
        st.markdown('<div style="margin: 1.2rem 0;"></div>', unsafe_allow_html=True)
        
        pr_row2_col1, pr_row2_col2 = st.columns(2, gap="medium")
        with pr_row2_col1:
            st.markdown(exp_html, unsafe_allow_html=True)
        with pr_row2_col2:
            if kw_html:
                st.markdown(kw_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # TAB 2 — Role Matching (Complete Redesign)
    # ─────────────────────────────────────────────────────────
    with tabs[1]:
        top_roles = role_matches.get("top_roles", [])
        if top_roles:
            # Helper function to get match strength label
            def get_match_strength(score):
                if score >= 70: return ("Excellent", "#10B981", "#ECFDF5")
                elif score >= 50: return ("Good", "#6366F1", "#EEF2FF")
                elif score >= 30: return ("Moderate", "#F59E0B", "#FFF7ED")
                else: return ("Low", "#EF4444", "#FEF2F2")
            
            # Helper function to categorize role
            def get_role_category(role_name):
                role_lower = role_name.lower()
                if any(x in role_lower for x in ["engineer", "developer", "programmer"]):
                    return ("Engineering", "⚙️", "#3B82F6")
                elif any(x in role_lower for x in ["analyst", "data", "bi", "scientist"]):
                    return ("Analytics", "📊", "#8B5CF6")
                elif any(x in role_lower for x in ["manager", "lead", "director"]):
                    return ("Leadership", "👔", "#EC4899")
                elif any(x in role_lower for x in ["designer", "ux", "ui"]):
                    return ("Design", "🎨", "#F59E0B")
                else:
                    return ("General", "💼", "#6B7280")
            
            # Featured Top Match Card - Using components.html for SVG support
            top_match = top_roles[0]
            top_score = top_match["score"] * 100
            is_target_top = target_role.lower() == top_match["role_name"].lower()
            strength_label, strength_color, strength_bg = get_match_strength(top_score)
            category_name, category_icon, category_color = get_role_category(top_match["role_name"])
            
            target_badge_html = '<div style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,#ECFDF5,#D1FAE5);color:#065F46;padding:8px 16px;border-radius:8px;font-size:0.9rem;font-weight:700;border:1px solid #A7F3D0;">🎯 Your Target Role</div>' if is_target_top else ''
            dash_array_top = top_score * 3.77
            
            featured_full_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: transparent; }}
                    .featured-card {{
                        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                        border: 2px solid #E2E8F0;
                        border-radius: 20px;
                        padding: 2rem;
                        position: relative;
                        overflow: hidden;
                    }}
                    .featured-card::before {{
                        content: '';
                        position: absolute;
                        top: 0; left: 0; right: 0;
                        height: 4px;
                        background: linear-gradient(90deg, #6366F1, #8B5CF6, #A78BFA);
                    }}
                    .best-badge {{
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        background: linear-gradient(135deg, #FEF3C7, #FDE68A);
                        color: #92400E;
                        padding: 8px 16px;
                        border-radius: 99px;
                        font-size: 0.85rem;
                        font-weight: 700;
                        margin-bottom: 1.5rem;
                        border: 1px solid #FCD34D;
                    }}
                    .header-row {{
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        gap: 2rem;
                        flex-wrap: wrap;
                    }}
                    .role-info {{ flex: 1; min-width: 280px; }}
                    .category {{ display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem; font-size: 0.95rem; }}
                    .role-title {{ font-size: 2rem; font-weight: 800; color: #1F2937; margin: 0 0 1rem 0; line-height: 1.2; }}
                    .score-ring {{ flex-shrink: 0; }}
                    .footer-row {{
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-top: 1.5rem;
                        padding-top: 1.5rem;
                        border-top: 1px solid #F1F5F9;
                        flex-wrap: wrap;
                        gap: 1rem;
                    }}
                    .match-badge {{
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        padding: 10px 18px;
                        border-radius: 12px;
                        font-size: 0.95rem;
                        font-weight: 700;
                    }}
                    .match-rank {{ font-size: 0.9rem; color: #6B7280; font-weight: 600; }}
                </style>
            </head>
            <body>
                <div class="featured-card">
                    <div class="best-badge">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#F59E0B" stroke="#F59E0B" stroke-width="2"/>
                        </svg>
                        <span>Best Match</span>
                    </div>
                    
                    <div class="header-row">
                        <div class="role-info">
                            <div class="category">
                                <span style="font-size:1.25rem;">{category_icon}</span>
                                <span style="color:{category_color};font-weight:600;">{category_name}</span>
                            </div>
                            <h2 class="role-title">{top_match["role_name"]}</h2>
                            {target_badge_html}
                        </div>
                        
                        <div class="score-ring">
                            <svg width="140" height="140" viewBox="0 0 140 140">
                                <circle cx="70" cy="70" r="60" fill="none" stroke="#E5E7EB" stroke-width="12"/>
                                <circle cx="70" cy="70" r="60" fill="none" stroke="{strength_color}" stroke-width="12"
                                        stroke-dasharray="{dash_array_top} 377" 
                                        stroke-linecap="round" 
                                        transform="rotate(-90 70 70)"/>
                                <text x="70" y="65" text-anchor="middle" font-size="32" font-weight="700" fill="#1F2937">{top_score:.0f}%</text>
                                <text x="70" y="85" text-anchor="middle" font-size="12" fill="#6B7280">Match Score</text>
                            </svg>
                        </div>
                    </div>
                    
                    <div class="footer-row">
                        <div class="match-badge" style="background:{strength_bg};color:{strength_color};">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
                            </svg>
                            {strength_label} Match
                        </div>
                        <div class="match-rank">#1 of {len(top_roles)} matches</div>
                    </div>
                </div>
            </body>
            </html>
            '''
            components.html(featured_full_html, height=380)
            
            # Section Header for Other Matches
            st.markdown('''
            <div style="margin: 0.5rem 0 0.75rem 0;">
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1F2937;">
                    More Career Opportunities
                </h3>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #6B7280;">
                    Explore other roles that match your profile
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
            
            # Grid of Role Cards (positions 2-9) using components.html
            roles_to_display = top_roles[1:9]  # Show next 8 roles
            
            # Create rows of 4 cards each
            for row_idx in range(0, len(roles_to_display), 4):
                cols = st.columns(4, gap="medium")
                for col_idx, col in enumerate(cols):
                    role_idx = row_idx + col_idx
                    if role_idx < len(roles_to_display):
                        role = roles_to_display[role_idx]
                        score = role["score"] * 100
                        rank = role_idx + 2
                        is_target = target_role.lower() == role["role_name"].lower()
                        strength_label, strength_color, strength_bg = get_match_strength(score)
                        category_name, category_icon, category_color = get_role_category(role["role_name"])
                        
                        rank_display = "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                        target_badge = '<div style="display:inline-flex;align-items:center;gap:4px;background:#ECFDF5;color:#065F46;padding:4px 10px;border-radius:6px;font-size:0.75rem;font-weight:700;border:1px solid #A7F3D0;margin-bottom:8px;">🎯 Target</div>' if is_target else ''
                        dash_array = score * 1.508
                        
                        card_full_html = f'''
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                                body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                                .card {{
                                    background: #FFFFFF;
                                    border: 1px solid #E2E8F0;
                                    border-radius: 16px;
                                    padding: 1.2rem;
                                    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                                    height: 100%;
                                    display: flex;
                                    flex-direction: column;
                                    gap: 0.75rem;
                                }}
                                .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.06); }}
                                .card-header {{
                                    display: flex;
                                    align-items: center;
                                    justify-content: space-between;
                                    gap: 8px;
                                }}
                                .rank {{ font-size: 0.9rem; font-weight: 700; color: #94A3B8; }}
                                .category {{
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 4px;
                                    padding: 4px 10px;
                                    border-radius: 6px;
                                    font-size: 0.75rem;
                                    font-weight: 700;
                                }}
                                .title {{ font-size: 1rem; font-weight: 700; color: #1F2937; line-height: 1.4; }}
                                .score-area {{
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    gap: 0.5rem;
                                    margin-top: auto;
                                    padding-top: 1rem;
                                    border-top: 1px solid #F1F5F9;
                                }}
                                .strength {{ font-size: 0.85rem; font-weight: 700; text-align: center; }}
                            </style>
                        </head>
                        <body>
                            <div class="card">
                                <div class="card-header">
                                    <span class="rank">{rank_display}</span>
                                    <span class="category" style="background:{category_color}15;color:{category_color};">
                                        {category_icon} {category_name}
                                    </span>
                                </div>
                                
                                <div class="title">{role["role_name"]}</div>
                                {target_badge}
                                
                                <div class="score-area">
                                    <svg width="60" height="60" viewBox="0 0 60 60">
                                        <circle cx="30" cy="30" r="24" fill="none" stroke="#E5E7EB" stroke-width="6"/>
                                        <circle cx="30" cy="30" r="24" fill="none" stroke="{strength_color}" stroke-width="6"
                                                stroke-dasharray="{dash_array} 150.8" 
                                                stroke-linecap="round" 
                                                transform="rotate(-90 30 30)"/>
                                        <text x="30" y="34" text-anchor="middle" font-size="14" font-weight="700" fill="#1F2937">{score:.0f}%</text>
                                    </svg>
                                    <div class="strength" style="color:{strength_color};">{strength_label}</div>
                                </div>
                            </div>
                        </body>
                        </html>
                        '''
                        with col:
                            components.html(card_full_html, height=260)
            
            # Show remaining count if more than 9 roles
            if len(top_roles) > 9:
                remaining = len(top_roles) - 9
                plural = 's' if remaining > 1 else ''
                st.markdown(f'''
                <div style="display:flex;align-items:center;justify-content:center;gap:10px;padding:1.2rem;margin-top:1rem;background:#F8FAFC;border:1px dashed #E2E8F0;border-radius:16px;color:#475569;font-size:0.95rem;font-weight:600;">
                    <span>+{remaining} more role{plural} in your profile</span>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No role matching data available.")

    # ─────────────────────────────────────────────────────────
    # TAB 3 — JD & ATS Analysis (Complete Redesign)
    # ─────────────────────────────────────────────────────────
    with tabs[2]:
        if jd_comp or ats_sim:
            # Extract all data
            overall = jd_comp.get("overall_match_percent", 0) if jd_comp else 0
            matched_kw = jd_comp.get("matched_keywords", []) if jd_comp else []
            missing_kw = jd_comp.get("missing_keywords", []) if jd_comp else []
            section_scores = jd_comp.get("section_scores", {}) if jd_comp else {}
            
            ats_compat = ats_sim.get("ats_compatibility_score", 0) if ats_sim else 0
            kw_report = ats_sim.get("keyword_report", {}) if ats_sim else {}
            sections_complete = ats_sim.get("section_completeness", {}) if ats_sim else {}
            readability = ats_sim.get("readability", {}) if ats_sim else {}
            risks = ats_sim.get("formatting_risks", []) if ats_sim else []
            alerts = ats_sim.get("alerts", []) if ats_sim else []
            
            # Calculate combined score
            combined_score = (overall + ats_compat) / 2 if (overall and ats_compat) else (overall or ats_compat)
            
            # Determine grade
            def get_grade(score):
                if score >= 90: return ("A+", "#10B981", "Exceptional")
                elif score >= 80: return ("A", "#10B981", "Excellent")
                elif score >= 70: return ("B+", "#6366F1", "Very Good")
                elif score >= 60: return ("B", "#6366F1", "Good")
                elif score >= 50: return ("C+", "#F59E0B", "Average")
                elif score >= 40: return ("C", "#F59E0B", "Below Average")
                else: return ("D", "#EF4444", "Needs Work")
            
            grade, grade_color, grade_label = get_grade(combined_score)
            
            # ═══════════════════════════════════════════════════════════
            # TOP SECTION: Score Dashboard with 3 Metric Cards
            # ═══════════════════════════════════════════════════════════
            
            score_dashboard_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                    .dashboard {{
                        display: grid;
                        grid-template-columns: 1fr 2fr 1fr;
                        gap: 1.5rem;
                        padding: 1rem 0;
                    }}
                    .metric-card {{
                        background: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 16px;
                        padding: 1.5rem;
                        text-align: center;
                        position: relative;
                        overflow: hidden;
                    }}
                    .metric-card::before {{
                        content: '';
                        position: absolute;
                        top: 0; left: 0; right: 0;
                        height: 3px;
                    }}
                    .card-jd::before {{ background: linear-gradient(90deg, #6366F1, #8B5CF6); }}
                    .card-grade::before {{ background: linear-gradient(90deg, #F59E0B, #FBBF24); }}
                    .card-ats::before {{ background: linear-gradient(90deg, #10B981, #34D399); }}
                    
                    .metric-label {{ font-size: 0.75rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }}
                    .metric-value {{ font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 0.25rem; }}
                    .metric-sub {{ font-size: 0.85rem; color: #6B7280; font-weight: 500; }}
                    
                    .grade-card {{
                        background: linear-gradient(135deg, #FEFCE8 0%, #FEF9C3 100%);
                        border: 2px solid #FDE68A;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    }}
                    .grade-value {{ font-size: 4rem; font-weight: 900; color: {grade_color}; line-height: 1; }}
                    .grade-label {{ font-size: 1rem; font-weight: 700; color: {grade_color}; margin-top: 0.5rem; }}
                    
                    .ring-container {{ position: relative; width: 100px; height: 100px; margin: 0 auto 0.75rem; }}
                </style>
            </head>
            <body>
                <div class="dashboard">
                    <div class="metric-card card-jd">
                        <div class="metric-label">JD Match</div>
                        <div class="ring-container">
                            <svg width="100" height="100" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#E5E7EB" stroke-width="8"/>
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#6366F1" stroke-width="8"
                                        stroke-dasharray="{overall * 2.51} 251" 
                                        stroke-linecap="round" 
                                        transform="rotate(-90 50 50)"/>
                                <text x="50" y="55" text-anchor="middle" font-size="20" font-weight="800" fill="#1F2937">{overall:.0f}%</text>
                            </svg>
                        </div>
                        <div class="metric-sub">Resume vs Job Description</div>
                    </div>
                    
                    <div class="metric-card grade-card">
                        <div class="metric-label">Overall Grade</div>
                        <div class="grade-value">{grade}</div>
                        <div class="grade-label">{grade_label}</div>
                    </div>
                    
                    <div class="metric-card card-ats">
                        <div class="metric-label">ATS Score</div>
                        <div class="ring-container">
                            <svg width="100" height="100" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#E5E7EB" stroke-width="8"/>
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#10B981" stroke-width="8"
                                        stroke-dasharray="{ats_compat * 2.51} 251" 
                                        stroke-linecap="round" 
                                        transform="rotate(-90 50 50)"/>
                                <text x="50" y="55" text-anchor="middle" font-size="20" font-weight="800" fill="#1F2937">{ats_compat:.0f}%</text>
                            </svg>
                        </div>
                        <div class="metric-sub">ATS Compatibility</div>
                    </div>
                </div>
            </body>
            </html>
            '''
            components.html(score_dashboard_html, height=220)
            
            # ═══════════════════════════════════════════════════════════
            # KEYWORD ANALYSIS - Dual Panel with Visual Indicators
            # ═══════════════════════════════════════════════════════════
            
            total_kw = len(matched_kw) + len(missing_kw)
            match_rate = (len(matched_kw) / total_kw * 100) if total_kw > 0 else 0
            
            # Build matched keywords HTML
            matched_chips = ''.join([f'<span class="kw-chip matched">{kw}</span>' for kw in matched_kw[:20]])
            more_matched = f'<span class="kw-more">+{len(matched_kw) - 20} more</span>' if len(matched_kw) > 20 else ''
            
            # Build missing keywords HTML
            missing_chips = ''.join([f'<span class="kw-chip missing">{kw}</span>' for kw in missing_kw[:15]])
            more_missing = f'<span class="kw-more">+{len(missing_kw) - 15} more</span>' if len(missing_kw) > 15 else ''
            
            keyword_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                    .kw-section {{
                        background: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                    }}
                    .kw-header {{
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 1rem;
                        padding-bottom: 1rem;
                        border-bottom: 1px solid #F1F5F9;
                    }}
                    .kw-title-area {{ display: flex; align-items: center; gap: 12px; }}
                    .kw-icon {{
                        width: 40px; height: 40px;
                        border-radius: 10px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 1.2rem;
                    }}
                    .kw-icon-green {{ background: #ECFDF5; }}
                    .kw-icon-red {{ background: #FEF2F2; }}
                    .kw-title {{ font-size: 1.1rem; font-weight: 700; color: #1F2937; }}
                    .kw-stats {{ display: flex; align-items: center; gap: 1rem; }}
                    .kw-stat {{
                        display: flex; align-items: center; gap: 6px;
                        padding: 6px 14px;
                        border-radius: 99px;
                        font-size: 0.85rem;
                        font-weight: 700;
                    }}
                    .kw-stat-green {{ background: #ECFDF5; color: #047857; }}
                    .kw-stat-red {{ background: #FEF2F2; color: #DC2626; }}
                    .kw-stat-blue {{ background: #EFF6FF; color: #1D4ED8; }}
                    
                    .kw-content {{ display: flex; gap: 1.5rem; }}
                    .kw-panel {{ flex: 1; }}
                    .kw-panel-title {{
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: #6B7280;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.75rem;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }}
                    .kw-chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
                    .kw-chip {{
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 0.85rem;
                        font-weight: 600;
                    }}
                    .kw-chip.matched {{ background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }}
                    .kw-chip.missing {{ background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }}
                    .kw-more {{ font-size: 0.8rem; color: #6B7280; font-style: italic; padding: 6px; }}
                    
                    .kw-progress {{
                        margin-top: 1rem;
                        padding-top: 1rem;
                        border-top: 1px solid #F1F5F9;
                    }}
                    .kw-progress-label {{
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #475569;
                        margin-bottom: 0.5rem;
                        display: flex;
                        justify-content: space-between;
                    }}
                    .kw-progress-bar {{
                        height: 8px;
                        background: #FEE2E2;
                        border-radius: 99px;
                        overflow: hidden;
                    }}
                    .kw-progress-fill {{
                        height: 100%;
                        background: linear-gradient(90deg, #10B981, #34D399);
                        border-radius: 99px;
                        width: {match_rate}%;
                    }}
                </style>
            </head>
            <body>
                <div class="kw-section">
                    <div class="kw-header">
                        <div class="kw-title-area">
                            <div class="kw-icon kw-icon-green">🔑</div>
                            <div class="kw-title">Keyword Analysis</div>
                        </div>
                        <div class="kw-stats">
                            <div class="kw-stat kw-stat-green">✓ {len(matched_kw)} Found</div>
                            <div class="kw-stat kw-stat-red">✗ {len(missing_kw)} Missing</div>
                            <div class="kw-stat kw-stat-blue">{match_rate:.0f}% Match Rate</div>
                        </div>
                    </div>
                    
                    <div class="kw-content">
                        <div class="kw-panel">
                            <div class="kw-panel-title">
                                <span style="color:#10B981;">●</span> Keywords Found in Resume
                            </div>
                            <div class="kw-chips">
                                {matched_chips}
                                {more_matched}
                            </div>
                        </div>
                        <div class="kw-panel">
                            <div class="kw-panel-title">
                                <span style="color:#EF4444;">●</span> Keywords to Add
                            </div>
                            <div class="kw-chips">
                                {missing_chips}
                                {more_missing}
                            </div>
                        </div>
                    </div>
                    
                    <div class="kw-progress">
                        <div class="kw-progress-label">
                            <span>Keyword Coverage</span>
                            <span style="font-weight:800;color:#10B981;">{match_rate:.0f}%</span>
                        </div>
                        <div class="kw-progress-bar">
                            <div class="kw-progress-fill"></div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            # Calculate height based on content
            kw_height = 320 if (len(matched_kw) > 10 or len(missing_kw) > 8) else 280
            components.html(keyword_html, height=kw_height)
            
            # ═══════════════════════════════════════════════════════════
            # SECTION COVERAGE - Horizontal Progress Bars with Icons
            # ═══════════════════════════════════════════════════════════
            
            if section_scores:
                section_icons = {
                    "skills": "💻",
                    "experience": "📈",
                    "education": "🎓",
                    "tools": "🔧",
                    "certifications": "📜",
                    "projects": "🚀"
                }
                section_order = ["skills", "experience", "education"]
                
                section_bars_html = ''
                for key in section_order:
                    if key in section_scores:
                        val = section_scores[key]
                        if isinstance(val, dict):
                            val = val.get("relevance_percent", 0)
                        val = max(0, min(100, float(val) if isinstance(val, (int, float)) else 0))
                        
                        # Color based on value
                        if val >= 70:
                            bar_color = "#10B981"
                        elif val >= 50:
                            bar_color = "#6366F1"
                        elif val >= 30:
                            bar_color = "#F59E0B"
                        else:
                            bar_color = "#EF4444"
                        
                        icon = section_icons.get(key, "📊")
                        label = key.title()
                        
                        section_bars_html += f'''
                        <div class="sec-row">
                            <div class="sec-info">
                                <span class="sec-icon">{icon}</span>
                                <span class="sec-name">{label}</span>
                            </div>
                            <div class="sec-bar-container">
                                <div class="sec-bar-track">
                                    <div class="sec-bar-fill" style="width:{val}%;background:{bar_color};"></div>
                                </div>
                            </div>
                            <div class="sec-value" style="color:{bar_color};">{val:.0f}%</div>
                        </div>
                        '''
                
                section_html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                        .section-card {{
                            background: #FFFFFF;
                            border: 1px solid #E2E8F0;
                            border-radius: 16px;
                            padding: 1.5rem;
                        }}
                        .section-title {{
                            font-size: 1.1rem;
                            font-weight: 700;
                            color: #1F2937;
                            margin-bottom: 1.25rem;
                            display: flex;
                            align-items: center;
                            gap: 10px;
                        }}
                        .section-title-icon {{
                            width: 36px; height: 36px;
                            background: #F5F3FF;
                            border-radius: 10px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1.1rem;
                        }}
                        .sec-row {{
                            display: flex;
                            align-items: center;
                            gap: 1rem;
                            padding: 0.75rem 0;
                            border-bottom: 1px solid #F8FAFC;
                        }}
                        .sec-row:last-child {{ border-bottom: none; }}
                        .sec-info {{
                            display: flex;
                            align-items: center;
                            gap: 10px;
                            min-width: 140px;
                        }}
                        .sec-icon {{ font-size: 1.25rem; }}
                        .sec-name {{ font-size: 0.95rem; font-weight: 600; color: #374151; }}
                        .sec-bar-container {{ flex: 1; }}
                        .sec-bar-track {{
                            height: 10px;
                            background: #F1F5F9;
                            border-radius: 99px;
                            overflow: hidden;
                        }}
                        .sec-bar-fill {{
                            height: 100%;
                            border-radius: 99px;
                            transition: width 0.8s ease;
                        }}
                        .sec-value {{
                            font-size: 1rem;
                            font-weight: 800;
                            min-width: 50px;
                            text-align: right;
                        }}
                    </style>
                </head>
                <body>
                    <div class="section-card">
                        <div class="section-title">
                            <div class="section-title-icon">📊</div>
                            Section Coverage
                        </div>
                        {section_bars_html}
                    </div>
                </body>
                </html>
                '''
                # Dynamic height based on number of sections
                section_count = len([k for k in section_order if k in section_scores])
                section_height = 100 + (section_count * 52)
                components.html(section_html, height=section_height)
            
            # ═══════════════════════════════════════════════════════════
            # ATS DEEP DIVE - Expandable Sections
            # ═══════════════════════════════════════════════════════════
            
            st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
            
            # Resume Health Checklist
            if sections_complete or readability:
                checklist_items = ''
                check_count = 0
                total_checks = 0
                
                # Section completeness
                for sec_name, found in sections_complete.items():
                    label = sec_name.replace("_", " ").title()
                    icon = "✓" if found else "✗"
                    color = "#10B981" if found else "#EF4444"
                    bg = "#ECFDF5" if found else "#FEF2F2"
                    if found:
                        check_count += 1
                    total_checks += 1
                    checklist_items += f'<div class="check-item" style="background:{bg};"><span style="color:{color};font-weight:700;">{icon}</span> {label}</div>'
                
                # Readability metrics
                readability_score = readability.get("score", 0)
                bullet_count = readability.get("bullet_count", 0)
                action_verbs = readability.get("action_verb_count", 0)
                quantified = readability.get("quantified_achievements", 0)
                
                health_score = (check_count / total_checks * 100) if total_checks > 0 else 0
                
                health_html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                        .health-container {{
                            display: grid;
                            grid-template-columns: 1fr 1fr;
                            gap: 1rem;
                        }}
                        .health-card {{
                            background: #FFFFFF;
                            border: 1px solid #E2E8F0;
                            border-radius: 16px;
                            padding: 1.25rem;
                        }}
                        .health-title {{
                            font-size: 0.95rem;
                            font-weight: 700;
                            color: #1F2937;
                            margin-bottom: 1rem;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        }}
                        .health-title-icon {{
                            width: 32px; height: 32px;
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1rem;
                        }}
                        .check-grid {{
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 8px;
                        }}
                        .check-item {{
                            padding: 8px 12px;
                            border-radius: 8px;
                            font-size: 0.85rem;
                            font-weight: 500;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        }}
                        .metric-grid {{
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 12px;
                        }}
                        .metric-box {{
                            background: #F8FAFC;
                            border-radius: 12px;
                            padding: 1rem;
                            text-align: center;
                        }}
                        .metric-val {{ font-size: 1.5rem; font-weight: 800; color: #1F2937; }}
                        .metric-label {{ font-size: 0.75rem; color: #6B7280; font-weight: 600; margin-top: 4px; }}
                    </style>
                </head>
                <body>
                    <div class="health-container">
                        <div class="health-card">
                            <div class="health-title">
                                <div class="health-title-icon" style="background:#ECFDF5;">✓</div>
                                Resume Checklist ({check_count}/{total_checks})
                            </div>
                            <div class="check-grid">
                                {checklist_items}
                            </div>
                        </div>
                        <div class="health-card">
                            <div class="health-title">
                                <div class="health-title-icon" style="background:#EEF2FF;">📖</div>
                                Readability Metrics
                            </div>
                            <div class="metric-grid">
                                <div class="metric-box">
                                    <div class="metric-val">{readability_score:.0f}%</div>
                                    <div class="metric-label">Readability Score</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-val">{bullet_count}</div>
                                    <div class="metric-label">Bullet Points</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-val">{action_verbs}</div>
                                    <div class="metric-label">Action Verbs</div>
                                </div>
                                <div class="metric-box">
                                    <div class="metric-val">{quantified}</div>
                                    <div class="metric-label">Quantified Results</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                '''
                # Dynamic height based on number of checklist items
                checklist_count = total_checks
                health_height = max(280, 140 + (checklist_count * 25))
                components.html(health_html, height=health_height)
            
            # Alerts & Risks Section
            if risks or alerts:
                alert_items = ''
                for risk in risks:
                    alert_items += f'<div class="alert-item warning"><span class="alert-icon">⚠️</span><span>{risk}</span></div>'
                for alert in alerts:
                    alert_items += f'<div class="alert-item danger"><span class="alert-icon">🚨</span><span>{alert}</span></div>'
                
                alerts_html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{ font-family: 'Inter', -apple-system, sans-serif; background: transparent; }}
                        .alerts-card {{
                            background: #FFFFFF;
                            border: 1px solid #E2E8F0;
                            border-radius: 16px;
                            padding: 1.25rem;
                            margin-top: 1rem;
                        }}
                        .alerts-title {{
                            font-size: 0.95rem;
                            font-weight: 700;
                            color: #1F2937;
                            margin-bottom: 1rem;
                            display: flex;
                            align-items: center;
                            gap: 8px;
                        }}
                        .alerts-title-icon {{
                            width: 32px; height: 32px;
                            background: #FEF2F2;
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1rem;
                        }}
                        .alert-item {{
                            display: flex;
                            align-items: flex-start;
                            gap: 12px;
                            padding: 12px 16px;
                            border-radius: 10px;
                            margin-bottom: 8px;
                            font-size: 0.9rem;
                            line-height: 1.5;
                        }}
                        .alert-item:last-child {{ margin-bottom: 0; }}
                        .alert-item.warning {{ background: #FFFBEB; color: #92400E; border-left: 3px solid #F59E0B; }}
                        .alert-item.danger {{ background: #FEF2F2; color: #991B1B; border-left: 3px solid #EF4444; }}
                        .alert-icon {{ flex-shrink: 0; }}
                    </style>
                </head>
                <body>
                    <div class="alerts-card">
                        <div class="alerts-title">
                            <div class="alerts-title-icon">⚠️</div>
                            Issues to Address ({len(risks) + len(alerts)})
                        </div>
                        {alert_items}
                    </div>
                </body>
                </html>
                '''
                alert_height = 120 + (len(risks) + len(alerts)) * 50
                components.html(alerts_html, height=min(alert_height, 350))
        
        else:
            st.info("No JD comparison data — paste a job description in the sidebar.")

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
            st.markdown(f'<div style="margin-top: 1.2rem; font-weight: 700; font-size: 1.05rem;">{verdict}</div>', unsafe_allow_html=True)
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
        
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        
        # Download Button
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
        with col_dl2:
            st.download_button(
                label="📥  Download Full Report (JSON)",
                data=json.dumps(report, indent=2, default=str),
                file_name=f"talentiq_report_{target_role.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True,
            )
        
        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        
        # === REPORT GRID - FIXED LAYOUT ===
        st.markdown('<div class="report-grid">', unsafe_allow_html=True)
        
        # Prepare all data for consistent rendering
        ats_score_val = ats.get("overall_score", 0)
        skill_coverage = skill_gap.get("coverage_percent", 0)
        jd_match = jd_comp.get("overall_match_percent", 0) if jd_comp else 0
        soft_score_val = soft_skill.get("overall_score", 0)
        
        matched_skills = skill_gap.get("matched_skills", [])
        missing_skills = skill_gap.get("missing_skills", [])
        top_roles = role_matches.get("top_roles", [])[:5]
        improvements_list = improvements.get("suggestions", [])[:10]
        
        edu_data = profile.get("education", {})
        exp_data = profile.get("experience", {})
        degrees = edu_data.get("degrees", []) if isinstance(edu_data, dict) else []
        max_years = exp_data.get("max_years", 0) if isinstance(exp_data, dict) else 0
        
        career_paths = career.get("paths", [])[:5]
        cert_suggestions = certifications.get("recommended", [])[:8]
        industry_data = industry.get("alignment_score", 0) if industry else 0
        
        # ROW 1: Overview Cards
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        
        with r1c1:
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#EEF2FF;">🎯</div>
                    <div class="rb-title">ATS Score</div>
                    <div class="rb-badge badge-{_badge_cls(ats_score_val).replace("badge-", "")}">{_label(ats_score_val)[:4]}</div>
                </div>
                <div class="report-box-body">
                    <div class="rb-metric">
                        <div class="rb-metric-value">{ats_score_val:.0f}</div>
                        <div class="rb-metric-unit">/ 100</div>
                    </div>
                    <div class="rb-metric-label">Overall ATS Performance</div>
                    <div class="rb-progress">
                        <div class="rb-progress-fill" style="width:{ats_score_val}%;background:{_color_for_score(ats_score_val)};"></div>
                    </div>
                    <div style="margin-top:12px;">
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Keyword Match</span>
                            <span class="rb-stat-value">{ats.get("keyword_match", 0):.0f}%</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Format Score</span>
                            <span class="rb-stat-value">{ats.get("format_score", 0):.0f}%</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Structure Score</span>
                            <span class="rb-stat-value">{ats.get("structure_score", 0):.0f}%</span>
                        </div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r1c2:
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#F0FDFA;">🔧</div>
                    <div class="rb-title">Skills Coverage</div>
                    <div class="rb-badge" style="background:#ECFDF5;color:#047857;">{len(matched_skills)}</div>
                </div>
                <div class="report-box-body">
                    <div class="rb-metric">
                        <div class="rb-metric-value">{skill_coverage:.0f}</div>
                        <div class="rb-metric-unit">%</div>
                    </div>
                    <div class="rb-metric-label">Matched Skills Coverage</div>
                    <div class="rb-progress">
                        <div class="rb-progress-fill" style="width:{skill_coverage}%;background:{_color_for_score(skill_coverage)};"></div>
                    </div>
                    <div style="margin-top:12px;">
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Matched Skills</span>
                            <span class="rb-stat-value">{len(matched_skills)}</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Missing Skills</span>
                            <span class="rb-stat-value" style="color:#DC2626;">{len(missing_skills)}</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Skill Gap</span>
                            <span class="rb-stat-value">{100-skill_coverage:.0f}%</span>
                        </div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r1c3:
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FEF3C7;">📋</div>
                    <div class="rb-title">JD Alignment</div>
                    <div class="rb-badge badge-{_badge_cls(jd_match).replace("badge-", "")}">{_label(jd_match)[:4]}</div>
                </div>
                <div class="report-box-body">
                    <div class="rb-metric">
                        <div class="rb-metric-value">{jd_match:.0f}</div>
                        <div class="rb-metric-unit">%</div>
                    </div>
                    <div class="rb-metric-label">Job Description Match</div>
                    <div class="rb-progress">
                        <div class="rb-progress-fill" style="width:{jd_match}%;background:{_color_for_score(jd_match)};"></div>
                    </div>
                    <div style="margin-top:12px;">
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Matched Keywords</span>
                            <span class="rb-stat-value">{len(jd_comp.get("matched_keywords", [])) if jd_comp else 0}</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Missing Keywords</span>
                            <span class="rb-stat-value" style="color:#DC2626;">{len(jd_comp.get("missing_keywords", [])) if jd_comp else 0}</span>
                        </div>
                        <div class="rb-stat-row">
                            <span class="rb-stat-label">Relevance</span>
                            <span class="rb-stat-value">{jd_comp.get("relevance_score", 0):.0f}%</span>
                        </div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r1c4:
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FDF2F8;">💡</div>
                    <div class="rb-title">Profile Summary</div>
                </div>
                <div class="report-box-body">
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Experience</span>
                        <span class="rb-stat-value">{max_years} years</span>
                    </div>
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Education</span>
                        <span class="rb-stat-value">{len(degrees)} degree(s)</span>
                    </div>
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Total Skills</span>
                        <span class="rb-stat-value">{len(profile.get("skills_normalized", []))}</span>
                    </div>
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Soft Skills</span>
                        <span class="rb-stat-value">{soft_score_val:.0f}%</span>
                    </div>
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Industry Fit</span>
                        <span class="rb-stat-value">{industry_data:.0f}%</span>
                    </div>
                    <div class="rb-stat-row">
                        <span class="rb-stat-label">Target Role</span>
                        <span class="rb-stat-value" style="font-size:0.8rem;color:#6366F1;">{target_role[:20]}{"…" if len(target_role)>20 else ""}</span>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
        
        # ROW 2: Skills & Roles
        st.markdown('<div class="report-grid">', unsafe_allow_html=True)
        
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        
        with r2c1:
            matched_html = '<ul class="rb-list">'
            if matched_skills:
                for skill in matched_skills[:15]:
                    matched_html += f'<li class="rb-list-item"><span class="rb-list-dot"></span><span class="rb-list-text">{skill}</span></li>'
            else:
                matched_html += '<div class="rb-empty">No matched skills</div>'
            matched_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#ECFDF5;">✅</div>
                    <div class="rb-title">Matched Skills</div>
                    <div class="rb-badge" style="background:#ECFDF5;color:#047857;">{len(matched_skills)}</div>
                </div>
                <div class="report-box-body">
                    {matched_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r2c2:
            missing_html = '<ul class="rb-list">'
            if missing_skills:
                for skill in missing_skills[:15]:
                    skill_name = skill if isinstance(skill, str) else skill.get("skill", "")
                    missing_html += f'<li class="rb-list-item"><span class="rb-list-dot" style="background:#DC2626;"></span><span class="rb-list-text">{skill_name}</span></li>'
            else:
                missing_html += '<div class="rb-empty">No skill gaps detected</div>'
            missing_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FEF2F2;">⚠️</div>
                    <div class="rb-title">Missing Skills</div>
                    <div class="rb-badge" style="background:#FEF2F2;color:#DC2626;">{len(missing_skills)}</div>
                </div>
                <div class="report-box-body">
                    {missing_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r2c3:
            roles_html = '<ul class="rb-list">'
            if top_roles:
                for idx, role in enumerate(top_roles):
                    score = role.get("score", 0) * 100
                    role_name = role.get("role_name", "Unknown")
                    roles_html += f'<li class="rb-list-item"><span class="rb-list-dot"></span><span class="rb-list-text"><b>{role_name}</b> <span style="color:#6366F1;font-weight:700;margin-left:4px;">{score:.0f}%</span></span></li>'
            else:
                roles_html += '<div class="rb-empty">No role matches available</div>'
            roles_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#EEF2FF;">🎯</div>
                    <div class="rb-title">Top Role Matches</div>
                </div>
                <div class="report-box-body">
                    {roles_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r2c4:
            improvements_html = '<ul class="rb-list">'
            if improvements_list:
                for imp in improvements_list[:12]:
                    msg = imp.get("message", "") if isinstance(imp, dict) else str(imp)
                    improvements_html += f'<li class="rb-list-item"><span class="rb-list-dot" style="background:#F59E0B;"></span><span class="rb-list-text">{msg[:80]}{"…" if len(msg)>80 else ""}</span></li>'
            else:
                improvements_html += '<div class="rb-empty">No improvements suggested</div>'
            improvements_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FFFBEB;">💡</div>
                    <div class="rb-title">Improvements</div>
                    <div class="rb-badge" style="background:#FFFBEB;color:#A16207;">{len(improvements_list)}</div>
                </div>
                <div class="report-box-body">
                    {improvements_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)
        
        # ROW 3: Career & Certifications
        st.markdown('<div class="report-grid">', unsafe_allow_html=True)
        
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        
        with r3c1:
            career_html = '<ul class="rb-list">'
            if career_paths:
                for path in career_paths:
                    path_type = path.get("type", "Unknown")
                    target = path.get("target_role", "")
                    timeline = path.get("timeline", "")
                    career_html += f'<li class="rb-list-item"><span class="rb-list-dot"></span><span class="rb-list-text"><b>{target}</b> <span style="color:#94A3B8;font-size:0.8rem;">({timeline})</span></span></li>'
            else:
                career_html += '<div class="rb-empty">No career paths available</div>'
            career_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#F0F9FF;">📈</div>
                    <div class="rb-title">Career Paths</div>
                </div>
                <div class="report-box-body">
                    {career_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r3c2:
            cert_html = '<ul class="rb-list">'
            if cert_suggestions:
                for cert in cert_suggestions:
                    cert_name = cert.get("name", "") if isinstance(cert, dict) else str(cert)
                    priority = cert.get("priority", "medium") if isinstance(cert, dict) else "medium"
                    cert_html += f'<li class="rb-list-item"><span class="rb-list-dot" style="background:#8B5CF6;"></span><span class="rb-list-text">{cert_name}</span></li>'
            else:
                cert_html += '<div class="rb-empty">No certifications recommended</div>'
            cert_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FDF4FF;">🏆</div>
                    <div class="rb-title">Certifications</div>
                    <div class="rb-badge" style="background:#FDF4FF;color:#A21CAF;">{len(cert_suggestions)}</div>
                </div>
                <div class="report-box-body">
                    {cert_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r3c3:
            edu_html = '<ul class="rb-list">'
            if degrees:
                for deg in degrees:
                    edu_html += f'<li class="rb-list-item"><span class="rb-list-dot"></span><span class="rb-list-text">{deg}</span></li>'
            else:
                edu_html += '<div class="rb-empty">No education detected</div>'
            
            institutions = edu_data.get("institutions", []) if isinstance(edu_data, dict) else []
            if institutions:
                edu_html += '<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border-light);"><div style="font-size:0.75rem;font-weight:700;color:#6366F1;margin-bottom:6px;">INSTITUTIONS</div>'
                for inst in institutions[:3]:
                    edu_html += f'<li class="rb-list-item" style="font-size:0.82rem;"><span class="rb-list-dot" style="width:4px;height:4px;"></span><span class="rb-list-text">{inst}</span></li>'
                edu_html += '</div>'
            edu_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#EEF2FF;">🎓</div>
                    <div class="rb-title">Education</div>
                    <div class="rb-badge" style="background:#EEF2FF;color:#4338CA;">{len(degrees)}</div>
                </div>
                <div class="report-box-body">
                    {edu_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        with r3c4:
            job_titles = exp_data.get("job_titles", []) if isinstance(exp_data, dict) else []
            exp_html = f'''
            <div style="text-align:center;padding:20px 0;">
                <div style="font-size:2.5rem;font-weight:800;color:#F59E0B;line-height:1;">{max_years}</div>
                <div style="font-size:0.85rem;color:#94A3B8;margin-top:4px;font-weight:600;">YEARS EXPERIENCE</div>
            </div>
            <ul class="rb-list" style="margin-top:12px;">'''
            if job_titles:
                for title in job_titles[:8]:
                    exp_html += f'<li class="rb-list-item"><span class="rb-list-dot"></span><span class="rb-list-text">{title}</span></li>'
            else:
                exp_html += '<div class="rb-empty">No job titles found</div>'
            exp_html += '</ul>'
            
            st.markdown(f'''
            <div class="report-box">
                <div class="report-box-header">
                    <div class="rb-icon" style="background:#FEF3C7;">💼</div>
                    <div class="rb-title">Experience</div>
                </div>
                <div class="report-box-body">
                    {exp_html}
                </div>
            </div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
        
        # Raw JSON Expander
        with st.expander("🔍 View Raw JSON Data", expanded=False):
            st.json(report)


# ── No File Warning ──────────────────────────────────────────────────────

elif analyze_btn and not uploaded_file:
    st.warning("Please upload a resume file in the sidebar first.")
