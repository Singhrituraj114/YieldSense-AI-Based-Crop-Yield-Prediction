import streamlit as st
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import shap
import matplotlib.pyplot as plt

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="YieldSense AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== MASTER UI - LUSH 3D GREENERY THEME ====================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&family=Bebas+Neue&display=swap');

    :root {
        --leaf-dark:    #1a3a1f;
        --leaf-mid:     #2d5a27;
        --leaf-bright:  #3d7a35;
        --leaf-light:   #5aa64e;
        --sprout:       #7ec86a;
        --mint:         #a8e6a0;
        --dew:          #d4f5ce;
        --earth-dark:   #2c1a0e;
        --earth-mid:    #5c3317;
        --earth-warm:   #8b5e3c;
        --gold:         #d4a843;
        --gold-light:   #f0c96e;
        --cream:        #fdf8ee;
        --sky-blue:     #7dd3fc;
        --sun:          #fbbf24;

        --shadow-green: 0 0 60px rgba(94, 166, 78, 0.35);
        --shadow-deep:  0 40px 100px rgba(26, 58, 31, 0.5);
        --glow-gold:    0 0 40px rgba(212, 168, 67, 0.4);
    }

    /* ── BASE ── */
    * { box-sizing: border-box; margin: 0; padding: 0; }

    .stApp,
    [data-testid="stAppViewContainer"],
    .main {
        background: 
            radial-gradient(ellipse 120% 80% at 10% 0%,   rgba(45, 90, 39, 0.55) 0%, transparent 55%),
            radial-gradient(ellipse 80%  60% at 90% 100%, rgba(26, 58, 31, 0.6)  0%, transparent 50%),
            radial-gradient(ellipse 60%  40% at 50% 50%,  rgba(61, 122, 53, 0.2) 0%, transparent 70%),
            linear-gradient(160deg, #0d1f0f 0%, #142318 30%, #1a3420 60%, #0f1a10 100%) !important;
        font-family: 'DM Sans', sans-serif;
    }

    /* Animated floating spores / pollen particles */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(circle 2px at 15% 20%, rgba(168, 230, 160, 0.5) 0%, transparent 100%),
            radial-gradient(circle 1px at 80% 15%, rgba(212, 168, 67, 0.6)  0%, transparent 100%),
            radial-gradient(circle 2px at 60% 70%, rgba(168, 230, 160, 0.4) 0%, transparent 100%),
            radial-gradient(circle 1px at 35% 85%, rgba(212, 168, 67, 0.5)  0%, transparent 100%),
            radial-gradient(circle 3px at 90% 50%, rgba(94, 166, 78,  0.3)  0%, transparent 100%),
            radial-gradient(circle 1px at 5%  60%, rgba(168, 230, 160, 0.6) 0%, transparent 100%);
        pointer-events: none;
        z-index: 0;
        animation: drift 20s ease-in-out infinite;
    }

    @keyframes drift {
        0%,100% { transform: translateY(0)   translateX(0); }
        25%      { transform: translateY(-15px) translateX(8px); }
        50%      { transform: translateY(-8px)  translateX(-5px); }
        75%      { transform: translateY(-20px) translateX(12px); }
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: 
            linear-gradient(180deg, #0f1e10 0%, #162a18 50%, #0d1a0e 100%) !important;
        border-right: 1px solid rgba(94, 166, 78, 0.3) !important;
        box-shadow: 4px 0 40px rgba(26, 58, 31, 0.8) !important;
    }

    [data-testid="stSidebar"] * {
        color: #c8e8c4 !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--sprout) !important;
        font-family: 'Playfair Display', serif !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0d1a0e; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--leaf-bright), var(--sprout));
        border-radius: 4px;
    }

    /* ══════════════════════════════════
       HERO HEADER — 3D ORGANIC FOREST
    ══════════════════════════════════ */
    .hero-banner {
        position: relative;
        padding: 5rem 4rem 4rem;
        border-radius: 32px;
        margin-bottom: 3.5rem;
        overflow: hidden;
        isolation: isolate;

        /* 3D card lift */
        transform: perspective(1200px) rotateX(1.5deg);
        transform-style: preserve-3d;
        box-shadow:
            0 60px 120px rgba(13, 26, 14, 0.8),
            0 20px 40px  rgba(94, 166, 78, 0.2),
            inset 0 1px 0 rgba(168, 230, 160, 0.15),
            inset 0 -1px 0 rgba(0,0,0,0.4);

        background:
            radial-gradient(ellipse 90% 60% at 80% 110%, rgba(212, 168, 67, 0.18) 0%, transparent 50%),
            radial-gradient(ellipse 70% 50% at 10%  -10%, rgba(126, 200, 106, 0.25) 0%, transparent 50%),
            linear-gradient(145deg, #122914 0%, #1e4220 40%, #163318 70%, #0f2210 100%);

        border: 1px solid rgba(94, 166, 78, 0.4);
    }

    /* Leaf texture overlay */
    .hero-banner::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
            radial-gradient(ellipse 200px 150px at 5%   20%, rgba(94, 166, 78,  0.12) 0%, transparent 100%),
            radial-gradient(ellipse 150px 200px at 95%  80%, rgba(61, 122, 53,  0.15) 0%, transparent 100%),
            radial-gradient(ellipse 100px 80px  at 50%  5%,  rgba(168, 230, 160, 0.08) 0%, transparent 100%);
        pointer-events: none;
        z-index: 1;
    }

    /* Glowing orb */
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 320px; height: 320px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(212, 168, 67, 0.25) 0%, transparent 70%);
        animation: orb-pulse 6s ease-in-out infinite;
        pointer-events: none;
        z-index: 1;
    }

    @keyframes orb-pulse {
        0%,100% { transform: scale(1); opacity: 0.8; }
        50%      { transform: scale(1.2); opacity: 1; }
    }

    .hero-inner {
        position: relative;
        z-index: 2;
        transform: translateZ(20px);
    }

    .hero-eyebrow {
        display: inline-block;
        background: linear-gradient(90deg, var(--gold), var(--gold-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 0.95rem;
        letter-spacing: 4px;
        margin-bottom: 1rem;
        opacity: 0;
        animation: reveal-up 0.8s 0.1s ease forwards;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(3rem, 6vw, 5.5rem);
        font-weight: 900;
        line-height: 1.05;
        color: var(--dew);
        text-shadow:
            0 4px 30px rgba(0,0,0,0.6),
            0 0  60px rgba(126, 200, 106, 0.15);
        margin-bottom: 1.2rem;
        opacity: 0;
        animation: reveal-up 0.9s 0.25s ease forwards;
    }

    .hero-title span {
        background: linear-gradient(135deg, var(--sprout) 0%, var(--gold-light) 60%, var(--mint) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: rgba(212, 245, 206, 0.8);
        font-weight: 300;
        max-width: 580px;
        line-height: 1.7;
        opacity: 0;
        animation: reveal-up 1s 0.45s ease forwards;
    }

    .hero-badges {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
        margin-top: 2rem;
        opacity: 0;
        animation: reveal-up 1s 0.6s ease forwards;
    }

    .hero-badge {
        background: rgba(94, 166, 78, 0.15);
        border: 1px solid rgba(94, 166, 78, 0.4);
        border-radius: 100px;
        padding: 0.4rem 1.1rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--mint);
        backdrop-filter: blur(8px);
        letter-spacing: 0.5px;
    }

    /* Decorative 3D wheat stalks */
    .hero-deco {
        position: absolute;
        right: 5%;
        top: 50%;
        transform: translateY(-50%) translateZ(30px);
        font-size: 8rem;
        opacity: 0.12;
        filter: blur(1px);
        animation: sway 6s ease-in-out infinite;
        pointer-events: none;
        z-index: 1;
        line-height: 1;
    }

    .hero-deco-2 {
        right: 14%;
        font-size: 5rem;
        opacity: 0.07;
        animation-delay: 2s;
        animation-duration: 8s;
        top: 30%;
    }

    @keyframes sway {
        0%,100% { transform: translateY(-50%) rotate(-3deg); }
        50%      { transform: translateY(-55%) rotate(3deg); }
    }

    @keyframes reveal-up {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ══════════════════════════════════
       INFO CARDS — 3D GLASS LEAVES
    ══════════════════════════════════ */
    .leaf-card {
        position: relative;
        padding: 2.2rem;
        border-radius: 24px;
        overflow: hidden;
        transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1),
                    box-shadow 0.5s ease;
        cursor: default;

        background: linear-gradient(145deg,
            rgba(29, 58, 30, 0.9) 0%,
            rgba(22, 48, 24, 0.95) 100%);

        border: 1px solid rgba(94, 166, 78, 0.35);
        box-shadow:
            0 20px 60px rgba(13, 26, 14, 0.6),
            inset 0 1px 0 rgba(168, 230, 160, 0.1),
            inset 0 0 30px rgba(61, 122, 53, 0.05);

        /* 3D tilt base */
        transform-style: preserve-3d;
    }

    .leaf-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg,
            rgba(168, 230, 160, 0.06) 0%,
            transparent 60%);
        border-radius: inherit;
        pointer-events: none;
    }

    /* Vein accent */
    .leaf-card::after {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg,
            var(--sprout) 0%,
            var(--leaf-bright) 50%,
            var(--gold) 100%);
        border-radius: 24px 0 0 24px;
        box-shadow: 0 0 15px rgba(94, 166, 78, 0.5);
    }

    .leaf-card:hover {
        transform: translateY(-14px) rotateX(4deg) rotateY(-2deg);
        box-shadow:
            0 40px 100px rgba(13, 26, 14, 0.7),
            0 0 40px rgba(94, 166, 78, 0.2),
            inset 0 1px 0 rgba(168, 230, 160, 0.15);
        border-color: rgba(126, 200, 106, 0.6);
    }

    .leaf-card-icon {
        font-size: 2.2rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 4px 12px rgba(94, 166, 78, 0.5));
    }

    .leaf-card h4 {
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        color: var(--mint);
        margin-bottom: 0.8rem;
        font-weight: 700;
    }

    .leaf-card p {
        font-size: 0.9rem;
        color: rgba(212, 245, 206, 0.7);
        line-height: 1.75;
    }

    /* ══════════════════════════════════
       SECTION HEADERS
    ══════════════════════════════════ */
    .section-head {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2.2rem;
    }

    .section-head-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg,
            rgba(94, 166, 78, 0.6) 0%,
            rgba(94, 166, 78, 0.1) 100%);
    }

    .section-head h2 {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        color: var(--mint) !important;
        white-space: nowrap;
        text-shadow: 0 0 30px rgba(94, 166, 78, 0.3);
    }

    /* ══════════════════════════════════
       INPUT PANELS — SOIL TEXTURE CARD
    ══════════════════════════════════ */
    .input-panel {
        background:
            linear-gradient(145deg,
                rgba(22, 42, 24, 0.95) 0%,
                rgba(17, 35, 19, 0.98) 100%);
        border: 1px solid rgba(94, 166, 78, 0.25);
        border-radius: 24px;
        padding: 2.4rem;
        margin-bottom: 2rem;
        box-shadow:
            0 20px 60px rgba(13, 26, 14, 0.5),
            inset 0 1px 0 rgba(168, 230, 160, 0.06);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }

    .input-panel::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg,
            transparent 0%,
            var(--sprout) 30%,
            var(--gold) 70%,
            transparent 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .input-panel:hover::before { opacity: 1; }

    .input-panel:hover {
        border-color: rgba(94, 166, 78, 0.45);
        box-shadow:
            0 30px 80px rgba(13, 26, 14, 0.6),
            0 0 30px rgba(94, 166, 78, 0.1);
        transform: translateY(-4px);
    }

    /* ── Streamlit widget overrides ── */
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: rgba(13, 26, 14, 0.8) !important;
        border: 1.5px solid rgba(94, 166, 78, 0.4) !important;
        border-radius: 12px !important;
        color: #c8e8c4 !important;
        transition: all 0.3s ease !important;
    }

    .stSelectbox > div > div:hover,
    .stNumberInput > div > div:hover {
        border-color: var(--sprout) !important;
        box-shadow: 0 0 20px rgba(94, 166, 78, 0.15) !important;
    }

    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 3px rgba(212, 168, 67, 0.2) !important;
    }

    .stSelectbox label,
    .stNumberInput label,
    .stToggle label,
    .stRadio label {
        color: rgba(200, 232, 196, 0.85) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
    }

    /* Dropdown options */
    [data-baseweb="select"] li {
        background: #122914 !important;
        color: #c8e8c4 !important;
    }

    [data-baseweb="select"] li:hover {
        background: rgba(94, 166, 78, 0.2) !important;
    }

    /* Number input text */
    .stNumberInput input {
        color: #c8e8c4 !important;
        background: transparent !important;
    }

    /* ══════════════════════════════════
       CTA PREDICT BUTTON
    ══════════════════════════════════ */
    .stButton > button {
        width: 100% !important;
        padding: 1.3rem 2rem !important;
        border-radius: 16px !important;
        border: none !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.5rem !important;
        letter-spacing: 3px !important;
        color: #0d1a0e !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        min-height: 64px !important;

        background: linear-gradient(135deg,
            var(--sprout)     0%,
            var(--leaf-light) 30%,
            var(--gold)       70%,
            var(--sprout)     100%) !important;
        background-size: 200% 200% !important;
        animation: harvest-shimmer 4s ease infinite !important;

        box-shadow:
            0 8px 32px rgba(94, 166, 78, 0.4),
            0 2px 8px  rgba(212, 168, 67, 0.3),
            inset 0 1px 0 rgba(255,255,255,0.2) !important;
    }

    @keyframes harvest-shimmer {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 60%; height: 100%;
        background: linear-gradient(90deg,
            transparent,
            rgba(255,255,255,0.35),
            transparent);
        transition: left 0.7s ease;
        transform: skewX(-15deg);
    }

    .stButton > button:hover::before { left: 140%; }

    .stButton > button:hover {
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow:
            0 20px 60px rgba(94, 166, 78, 0.5),
            0 0 40px rgba(212, 168, 67, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.3) !important;
    }

    .stButton > button:active {
        transform: translateY(-2px) scale(1.01) !important;
    }

    /* ══════════════════════════════════
       PREDICTION RESULT — 3D HARVEST
    ══════════════════════════════════ */
    .harvest-result {
        position: relative;
        padding: 4.5rem 3rem;
        border-radius: 32px;
        text-align: center;
        overflow: hidden;
        margin-bottom: 2rem;

        background:
            radial-gradient(ellipse 80% 60% at 50% 0%,   rgba(126, 200, 106, 0.3) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(212, 168, 67, 0.25) 0%, transparent 50%),
            linear-gradient(160deg, #1a4020 0%, #2d6e28 40%, #1e5225 70%, #153018 100%);

        border: 1px solid rgba(126, 200, 106, 0.5);
        box-shadow:
            0 60px 140px rgba(13, 26, 14, 0.7),
            0 0 80px  rgba(94, 166, 78, 0.3),
            inset 0 2px 0 rgba(168, 230, 160, 0.2),
            inset 0 -2px 0 rgba(0,0,0,0.3);

        transform: perspective(1000px) rotateX(-1deg);
        animation: harvest-pop 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }

    @keyframes harvest-pop {
        from { opacity: 0; transform: perspective(1000px) rotateX(-1deg) scale(0.85) translateY(30px); }
        to   { opacity: 1; transform: perspective(1000px) rotateX(-1deg) scale(1)    translateY(0); }
    }

    /* Shimmering grain texture */
    .harvest-result::before {
        content: '';
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            60deg,
            transparent,
            transparent 3px,
            rgba(255,255,255,0.015) 3px,
            rgba(255,255,255,0.015) 6px
        );
        pointer-events: none;
    }

    /* Sun glow */
    .harvest-result::after {
        content: '';
        position: absolute;
        top: -80px; left: 50%;
        transform: translateX(-50%);
        width: 300px; height: 300px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(212, 168, 67, 0.3) 0%, transparent 70%);
        animation: sun-glow 4s ease-in-out infinite;
        pointer-events: none;
    }

    @keyframes sun-glow {
        0%,100% { opacity: 0.7; transform: translateX(-50%) scale(1); }
        50%      { opacity: 1;   transform: translateX(-50%) scale(1.15); }
    }

    .harvest-label {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 0.95rem;
        letter-spacing: 4px;
        color: var(--gold-light);
        opacity: 0.9;
        position: relative; z-index: 2;
    }

    .harvest-number {
        font-family: 'Playfair Display', serif;
        font-size: clamp(4rem, 10vw, 7rem);
        font-weight: 900;
        color: var(--dew);
        text-shadow:
            0 8px 40px rgba(0,0,0,0.5),
            0 0 60px rgba(168, 230, 160, 0.3);
        line-height: 1;
        display: block;
        position: relative; z-index: 2;
        margin: 0.6rem 0;
        animation: count-up 0.6s 0.3s ease both;
    }

    @keyframes count-up {
        from { opacity: 0; transform: scale(0.7) translateY(20px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
    }

    .harvest-unit {
        font-size: 1.1rem;
        color: rgba(212, 245, 206, 0.75);
        position: relative; z-index: 2;
        font-weight: 300;
        letter-spacing: 1px;
    }

    /* ══════════════════════════════════
       METRIC CARDS — SOIL PODS
    ══════════════════════════════════ */
    .soil-pod {
        background:
            linear-gradient(145deg,
                rgba(22, 45, 24, 0.95) 0%,
                rgba(16, 35, 18, 0.98) 100%);
        border: 1px solid rgba(94, 166, 78, 0.3);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow:
            0 16px 48px rgba(13, 26, 14, 0.5),
            inset 0 1px 0 rgba(168, 230, 160, 0.06);
        cursor: default;
        transform-style: preserve-3d;
    }

    .soil-pod::before {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg,
            var(--leaf-bright) 0%,
            var(--gold) 50%,
            var(--sprout) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .soil-pod:hover {
        transform: translateY(-12px) rotateX(5deg);
        border-color: rgba(126, 200, 106, 0.5);
        box-shadow:
            0 30px 80px rgba(13, 26, 14, 0.6),
            0 0 30px rgba(94, 166, 78, 0.2),
            inset 0 1px 0 rgba(168, 230, 160, 0.1);
    }

    .soil-pod:hover::before { opacity: 1; }

    .soil-pod-emoji {
        font-size: 2rem;
        display: block;
        margin-bottom: 0.8rem;
        filter: drop-shadow(0 4px 8px rgba(94, 166, 78, 0.4));
        animation: float-subtle 3s ease-in-out infinite;
    }

    @keyframes float-subtle {
        0%,100% { transform: translateY(0); }
        50%      { transform: translateY(-5px); }
    }

    .soil-pod-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: rgba(200, 232, 196, 0.55);
        margin-bottom: 0.5rem;
    }

    .soil-pod-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--mint);
        text-shadow: 0 0 20px rgba(94, 166, 78, 0.3);
    }

    /* ══════════════════════════════════
       ANALYSIS SUMMARY TABLE
    ══════════════════════════════════ */
    .analysis-table {
        background:
            linear-gradient(145deg,
                rgba(18, 38, 20, 0.97) 0%,
                rgba(14, 30, 16, 0.99) 100%);
        border: 1px solid rgba(94, 166, 78, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        margin-top: 2rem;
        box-shadow:
            0 30px 80px rgba(13, 26, 14, 0.5),
            inset 0 1px 0 rgba(168, 230, 160, 0.05);
        animation: slide-up 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }

    @keyframes slide-up {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .analysis-table h3 {
        font-family: 'Playfair Display', serif !important;
        color: var(--mint) !important;
        font-size: 1.4rem !important;
        margin-bottom: 1.8rem !important;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .analysis-table table { width: 100%; border-collapse: collapse; }

    .analysis-table tr {
        border-bottom: 1px solid rgba(94, 166, 78, 0.12);
        transition: background 0.25s ease;
    }

    .analysis-table tr:last-child { border-bottom: none; }
    .analysis-table tr:hover { background: rgba(94, 166, 78, 0.06); }

    .analysis-table td {
        padding: 1.2rem 1rem;
        color: rgba(212, 245, 206, 0.8);
        font-size: 0.92rem;
    }

    .analysis-table td:first-child {
        color: rgba(200, 232, 196, 0.5);
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        width: 35%;
    }

    .analysis-table td:last-child {
        color: var(--mint);
        font-weight: 600;
    }

    /* ══════════════════════════════════
       SHAP SECTION
    ══════════════════════════════════ */
    .shap-header {
        background:
            linear-gradient(135deg,
                rgba(18, 42, 20, 0.95) 0%,
                rgba(26, 58, 31, 0.95) 100%);
        border: 1px solid rgba(94, 166, 78, 0.35);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(13, 26, 14, 0.4);
        position: relative;
        overflow: hidden;
    }

    .shap-header::before {
        content: '';
        position: absolute;
        right: -40px; top: -40px;
        width: 180px; height: 180px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(94, 166, 78, 0.12) 0%, transparent 70%);
        pointer-events: none;
    }

    .shap-header h2 {
        font-family: 'Playfair Display', serif !important;
        color: var(--mint) !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.6rem !important;
        text-shadow: 0 0 30px rgba(94, 166, 78, 0.2);
    }

    .shap-header p {
        color: rgba(200, 232, 196, 0.6) !important;
        font-size: 0.95rem !important;
    }

    /* ══════════════════════════════════
       DIVIDERS
    ══════════════════════════════════ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(94, 166, 78, 0.4) 30%,
            rgba(212, 168, 67, 0.3) 70%,
            transparent 100%) !important;
        margin: 2.5rem 0 !important;
    }

    /* ══════════════════════════════════
       STREAMLIT INFO / SUCCESS BOXES
    ══════════════════════════════════ */
    .stInfo {
        background: rgba(22, 45, 24, 0.8) !important;
        border: 1px solid rgba(94, 166, 78, 0.4) !important;
        border-radius: 12px !important;
        color: var(--mint) !important;
    }

    .stSuccess {
        background: rgba(18, 40, 20, 0.9) !important;
        border: 1px solid rgba(94, 166, 78, 0.5) !important;
        border-radius: 12px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(13, 26, 14, 0.8) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: rgba(200, 232, 196, 0.6) !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(94, 166, 78, 0.2) !important;
        color: var(--mint) !important;
        box-shadow: inset 0 0 10px rgba(94, 166, 78, 0.1) !important;
    }

    /* Sidebar toggles / radio */
    .stToggle [data-testid="stToggleSwitch"] {
        background: rgba(13, 26, 14, 0.8) !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(22, 45, 24, 0.6) !important;
        border-radius: 10px !important;
        color: var(--mint) !important;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid rgba(94, 166, 78, 0.25) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ══════════════════════════════════
       FOOTER
    ══════════════════════════════════ */
    .forest-footer {
        text-align: center;
        padding: 3.5rem;
        margin-top: 5rem;
        border-radius: 28px;
        position: relative;
        overflow: hidden;

        background:
            radial-gradient(ellipse 80% 50% at 50% 100%, rgba(94, 166, 78, 0.1) 0%, transparent 60%),
            linear-gradient(160deg, #0f1e10 0%, #142318 100%);

        border-top: 1px solid rgba(94, 166, 78, 0.2);
        border: 1px solid rgba(94, 166, 78, 0.15);
    }

    .forest-footer::before {
        content: '🌿 🌾 🌿 🌾 🌿 🌾 🌿';
        position: absolute;
        top: 1rem; left: 50%;
        transform: translateX(-50%);
        font-size: 1.2rem;
        opacity: 0.12;
        letter-spacing: 1.5rem;
        white-space: nowrap;
        filter: blur(1px);
    }

    .footer-title {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 900;
        color: var(--mint);
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(94, 166, 78, 0.3);
    }

    .footer-divider {
        width: 120px;
        height: 2px;
        margin: 1.2rem auto;
        background: linear-gradient(90deg, var(--leaf-bright), var(--gold), var(--leaf-bright));
        border-radius: 100px;
    }

    /* ══════════════════════════════════
       SIDEBAR CARD
    ══════════════════════════════════ */
    .sidebar-brand {
        background:
            linear-gradient(145deg,
                rgba(29, 60, 30, 0.9) 0%,
                rgba(18, 40, 20, 0.95) 100%);
        border: 1px solid rgba(94, 166, 78, 0.4);
        border-radius: 16px;
        padding: 1.4rem;
        text-align: center;
        margin-bottom: 1.4rem;
        box-shadow: 0 10px 30px rgba(13, 26, 14, 0.5);
    }

    .sidebar-stat {
        background: rgba(18, 40, 20, 0.8);
        border: 1px solid rgba(94, 166, 78, 0.25);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .sidebar-feature {
        background: rgba(29, 60, 30, 0.5);
        border-left: 3px solid var(--sprout);
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.5rem;
    }

    /* ══════════════════════════════════
       GLOBAL TEXT VISIBILITY
    ══════════════════════════════════ */
    .stApp p, .stApp span, .stApp div,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {
        color: rgba(212, 245, 206, 0.85);
    }

    .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: var(--mint) !important;
        font-family: 'Playfair Display', serif !important;
    }

    /* ══════════════════════════════════
       RESPONSIVE
    ══════════════════════════════════ */
    @media (max-width: 768px) {
        .hero-banner { padding: 3rem 2rem; transform: none; }
        .hero-title  { font-size: 2.4rem; }
        .harvest-number { font-size: 4rem; }
        .hero-deco   { display: none; }
    }

    @media (max-width: 480px) {
        .hero-title { font-size: 1.9rem; }
        .harvest-number { font-size: 3rem; }
        .harvest-result { padding: 3rem 1.5rem; }
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ==================== LOAD MODEL & ENCODERS ====================
@st.cache_resource
def load_model_and_encoders():
    try:
        model     = joblib.load("yieldsense_model.pkl")
        le_state  = joblib.load("yieldsense_le_state.pkl")
        le_district = joblib.load("yieldsense_le_district.pkl")
        le_crop   = joblib.load("yieldsense_le_crop.pkl")
        le_season = joblib.load("yieldsense_le_season.pkl")
        return model, le_state, le_district, le_crop, le_season
    except FileNotFoundError as e:
        st.error(f"❌ Error loading model files: {e}")
        return None, None, None, None, None

@st.cache_data
def load_crop_production_data():
    try:
        df = pd.read_csv("crop_production.csv")
        df['State_Name']    = df['State_Name'].str.lower().str.strip()
        df['District_Name'] = df['District_Name'].str.lower().str.strip()
        return df
    except FileNotFoundError as e:
        st.error(f"❌ Error loading crop_production.csv: {e}")
        return None

model, le_state, le_district, le_crop, le_season = load_model_and_encoders()
crop_data = load_crop_production_data()

if model is None or crop_data is None:
    st.stop()

# ==================== HELPER FUNCTIONS ====================
def get_districts_for_state(state):
    state_lower = state.lower().strip()
    filtered = crop_data[crop_data['State_Name'] == state_lower]['District_Name'].unique()
    encoder_districts = set(le_district.classes_)
    filtered = [d for d in filtered if d.upper() in encoder_districts]
    return sorted(filtered) if len(filtered) > 0 else []

@st.cache_resource
def create_shap_explainer(_model):
    try:
        return shap.TreeExplainer(_model)
    except Exception as e:
        st.warning(f"⚠️ Could not initialize SHAP: {str(e)}")
        return None

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:2.5rem;margin-bottom:0.4rem;">🌾</div>
        <p style="color:#7ec86a;font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:900;margin:0;">YieldSense AI</p>
        <p style="color:rgba(200,232,196,0.5);font-size:0.72rem;margin:0.3rem 0 0;">Agricultural Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="color:#7ec86a;font-size:0.78rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:0.6rem;">⚙️ Settings</p>', unsafe_allow_html=True)

    show_info  = st.toggle("📊 Show Feature Cards", value=True)
    theme_mode = st.radio("Theme", ["Forest Dark", "Light"], horizontal=True)

    st.divider()

    with st.expander("🌿 Key Features", expanded=True):
        for icon, label, color in [
            ("✨","Accurate Models","#7ec86a"),
            ("🌍","Geographic Precision","#a8e6a0"),
            ("⚡","Real-time Predictions","#d4a843"),
            ("🔍","SHAP Explainability","#7ec86a"),
        ]:
            st.markdown(f"""
            <div class="sidebar-feature">
                <p style="color:{color};font-weight:600;font-size:0.82rem;margin:0;">{icon} {label}</p>
            </div>""", unsafe_allow_html=True)

    with st.expander("📊 Model Performance", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""<div class="sidebar-stat">
                <p style="color:#7ec86a;font-size:1.5rem;font-weight:900;margin:0;">95%</p>
                <p style="color:rgba(200,232,196,0.5);font-size:0.68rem;margin:0;">Accuracy</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="sidebar-stat">
                <p style="color:#d4a843;font-size:1.5rem;font-weight:900;margin:0;">50K+</p>
                <p style="color:rgba(200,232,196,0.5);font-size:0.68rem;margin:0;">Predictions</p>
            </div>""", unsafe_allow_html=True)

    with st.expander("💡 Pro Tips", expanded=False):
        for tip in ["Use historical rainfall data","Verify area measurements in hectares","Select the correct growing season","Account for local climate patterns"]:
            st.markdown(f'<p style="color:rgba(200,232,196,0.65);font-size:0.8rem;margin-bottom:0.5rem;">🌱 {tip}</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:linear-gradient(135deg,rgba(94,166,78,0.15)0%,rgba(212,168,67,0.1)100%);
        border:1px solid rgba(94,166,78,0.3);
        border-radius:12px;padding:1rem;text-align:center;margin-top:1rem;
    ">
        <p style="color:#7ec86a;font-size:0.75rem;margin:0;line-height:1.6;">
            🌿 Sustainable Farming<br>
            <span style="color:rgba(200,232,196,0.5);">v1.0 Premium Edition</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== HERO HEADER ====================
st.markdown("""
<div class="hero-banner">
    <div class="hero-deco">🌾</div>
    <div class="hero-deco hero-deco-2">🌿</div>
    <div class="hero-inner">
        <span class="hero-eyebrow">✦ Agricultural Intelligence Platform ✦</span>
        <h1 class="hero-title">
            <span>YieldSense</span> AI<br>
            <span style="font-size:0.55em;color:rgba(212,245,206,0.7);font-weight:300;">Crop Yield Prediction System</span>
        </h1>
        <p class="hero-subtitle">
            Transform raw agricultural data into precise yield forecasts using
            advanced machine learning and geospatial weather analysis.
        </p>
        <div class="hero-badges">
            <span class="hero-badge">🌿 ML-Powered</span>
            <span class="hero-badge">🌧️ Weather-Aware</span>
            <span class="hero-badge">📊 SHAP Explainability</span>
            <span class="hero-badge">🗺️ Nationwide Coverage</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== INFO CARDS ====================
if show_info:
    c1, c2, c3 = st.columns(3)
    cards = [
        ("🎯","Precision Forecasting","ML models trained on decades of agricultural and meteorological data for maximum yield accuracy."),
        ("🌐","Nationwide Coverage","Every state, district, crop variety, and growing season — all in one intelligent platform."),
        ("⚡","Instant Intelligence","Real-time predictions that empower farmers to make decisive, data-driven choices every season."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(f"""
            <div class="leaf-card">
                <span class="leaf-card-icon">{icon}</span>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ==================== INPUTS ====================
st.markdown("""
<div class="section-head">
    <h2>📋 Prediction Parameters</h2>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="input-panel">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    state_options = [s.title() for s in sorted(le_state.classes_)]
    selected_state_display = st.selectbox("🗺️ Select State", state_options, help="Choose your agricultural state")
    state = selected_state_display.lower().strip()

with col2:
    available_districts = get_districts_for_state(state)
    district_options    = [d.title() for d in available_districts]
    if len(district_options) == 0:
        st.error("❌ No districts available for this state")
        st.stop()
    selected_district_display = st.selectbox("📍 Select District", district_options, help="Choose your district")
    district = selected_district_display.lower().strip()

with col3:
    crop_options = [c.title() for c in sorted(le_crop.classes_)]
    selected_crop_display = st.selectbox("🌱 Select Crop", crop_options, help="Choose the crop type")
    crop = selected_crop_display.lower().strip()

with col4:
    season_options = [s.title() for s in sorted(le_season.classes_)]
    selected_season_display = st.selectbox("🌤️ Select Season", season_options, help="Choose the farming season")
    season = selected_season_display.lower().strip()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div class="section-head">
    <h2>🌧️ Environmental Parameters</h2>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="input-panel">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    area = st.number_input("🏞️ Area (Hectares)", min_value=0.0, value=1.0, step=0.1, help="Agricultural area in hectares")
with col2:
    rainfall = st.number_input("💧 Annual Rainfall (mm)", min_value=0.0, value=500.0, step=10.0, help="Annual rainfall in millimeters")
with col3:
    year = st.number_input("📅 Crop Year", min_value=1997, max_value=2030, value=datetime.now().year, help="Prediction year")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ==================== PREDICT BUTTON ====================
st.markdown("""
<div class="section-head">
    <h2>🚀 Generate Prediction</h2>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    predict_button = st.button("🌾  ANALYSE & PREDICT YIELD", use_container_width=True, key="predict_btn")
with col2:
    st.info("✨ Click to analyse", icon="🌱")

# ==================== PREDICTION LOGIC (UNCHANGED) ====================
if predict_button:
    if area <= 0:
        st.error("❌ Area must be greater than 0 hectares"); st.stop()
    if rainfall <= 0:
        st.error("❌ Rainfall must be greater than 0 mm"); st.stop()

    if state not in le_state.classes_:
        st.error(f"❌ State '{state}' is not supported"); st.stop()
    district_upper = district.upper()
    if district_upper not in le_district.classes_:
        st.error(f"❌ District '{district}' is not supported"); st.stop()
    crop_title = crop.title()
    if crop_title not in le_crop.classes_:
        st.error(f"❌ Crop '{crop}' is not supported"); st.stop()
    season_title = season.title()
    if season_title not in le_season.classes_:
        st.error(f"❌ Season '{season}' is not supported"); st.stop()

    with st.spinner("🌱 Growing your prediction…"):
        try:
            state_enc    = le_state.transform([state])[0]
            district_enc = le_district.transform([district.upper()])[0]
            crop_enc     = le_crop.transform([crop.title()])[0]
            season_enc   = le_season.transform([season.title()])[0]

            input_data = pd.DataFrame([[
                state_enc, district_enc, year, season_enc, crop_enc, area, rainfall
            ]], columns=['State_Name','District_Name','Crop_Year','Season','Crop','Area','Rainfall'])

            prediction = model.predict(input_data)[0]

            # ── PREDICTION CONFIDENCE ──
            preds = np.array([tree.predict(input_data)[0] for tree in model.estimators_])
            confidence = np.std(preds)
            confidence_score = max(0, 100 - (confidence * 10))  # Convert to 0-100 scale

        except Exception as e:
            st.error(f"❌ Prediction error: {str(e)}"); st.stop()

    # ── RESULTS ──
    st.markdown("---")
    st.markdown("""
    <div class="section-head">
        <h2>🌾 Harvest Forecast</h2>
        <div class="section-head-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="harvest-result">
        <div class="harvest-label">✦ PREDICTED CROP YIELD ✦</div>
        <span class="harvest-number">{prediction:.2f}</span>
        <div class="harvest-unit">Quintals per Hectare</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    pods = [
        (col1, "🌱", "Crop",   crop.title()[:12]),
        (col2, "🗺️", "State",  state.title()[:12]),
        (col3, "🌤️", "Season", season.title()[:12]),
        (col4, "📅", "Year",   str(year)),
    ]
    for col, emoji, label, val in pods:
        with col:
            st.markdown(f"""
            <div class="soil-pod">
                <span class="soil-pod-emoji">{emoji}</span>
                <div class="soil-pod-label">{label}</div>
                <div class="soil-pod-value">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── CONFIDENCE SCORE ──
    st.markdown("<br>", unsafe_allow_html=True)
    conf_col1, conf_col2 = st.columns(2)
    with conf_col1:
        st.markdown(f"""
        <div class="soil-pod">
            <span class="soil-pod-emoji">🎯</span>
            <div class="soil-pod-label">Prediction Confidence</div>
            <div class="soil-pod-value">{confidence_score:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with conf_col2:
        st.markdown(f"""
        <div class="soil-pod">
            <span class="soil-pod-emoji">📊</span>
            <div class="soil-pod-label">Model Uncertainty</div>
            <div class="soil-pod-value">{confidence:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="analysis-table">
        <h3>📋 Full Analysis Summary</h3>
        <table>
            <tr><td>State</td><td>{state.title()}</td></tr>
            <tr><td>District</td><td>{district.title()}</td></tr>
            <tr><td>Crop</td><td>{crop.title()}</td></tr>
            <tr><td>Season</td><td>{season.title()}</td></tr>
            <tr><td>Area (Hectares)</td><td>{area:.2f}</td></tr>
            <tr><td>Rainfall (mm)</td><td>{rainfall:.2f}</td></tr>
            <tr><td>Crop Year</td><td>{year}</td></tr>
            <tr><td>🎯 Predicted Yield</td><td><strong style="color:#7ec86a;font-size:1.1rem;">{prediction:.2f} q/ha</strong></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.success("🌾 Prediction complete! Use these insights to optimise your farming strategy.")

    # ── SHAP ──
    st.markdown("---")
    st.markdown("""
    <div class="shap-header">
        <h2>🔍 Model Explainability (SHAP)</h2>
        <p>Understand exactly how each input factor shaped this prediction</p>
    </div>
    """, unsafe_allow_html=True)

    explainer = create_shap_explainer(model)
    if explainer is not None:
        try:
            shap_values = explainer.shap_values(input_data)
            if isinstance(shap_values, list):
                shap_vals = shap_values[0]
            else:
                shap_vals = shap_values
            if isinstance(shap_vals, np.ndarray) and shap_vals.ndim > 1:
                shap_vals = shap_vals[0]

            feature_names  = input_data.columns.tolist()
            feature_values = input_data.values[0]

            tab1, tab2, tab3, tab4 = st.tabs(["📊 Feature Contribution", "🎯 Prediction Breakdown", "📈 Feature Impact", "🌍 Global Importance"])

            with tab1:
                shap_df = pd.DataFrame({
                    'Feature':    feature_names,
                    'Value':      feature_values,
                    'SHAP Impact': np.abs(shap_vals) if shap_vals is not None else np.zeros(len(feature_names)),
                    'Direction':  ['↑ Increases' if sv > 0 else '↓ Decreases'
                                   for sv in (shap_vals if shap_vals is not None else np.zeros(len(feature_names)))]
                }).sort_values('SHAP Impact', ascending=False)

                styled_df = shap_df.style.format({
                    'Value': '{:.2f}', 'SHAP Impact': '{:.4f}'
                }).background_gradient(subset=['SHAP Impact'], cmap='Greens',
                    vmin=shap_df['SHAP Impact'].min(), vmax=shap_df['SHAP Impact'].max())
                st.dataframe(styled_df, use_container_width=True, hide_index=True)

            with tab2:
                col_pred, col_base = st.columns(2)
                base_val = explainer.expected_value
                if isinstance(base_val, np.ndarray):
                    base_val = base_val.item() if base_val.size == 1 else base_val[0]

                with col_pred:
                    st.markdown(f"""
                    <div style="background:rgba(94,166,78,0.15);border:1px solid rgba(94,166,78,0.4);
                                border-radius:16px;padding:2rem;text-align:center;">
                        <p style="color:rgba(200,232,196,0.6);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin:0;">Final Prediction</p>
                        <p style="color:#7ec86a;font-size:2.8rem;font-weight:900;margin:0.5rem 0 0;font-family:'Playfair Display',serif;">{prediction:.2f}</p>
                        <p style="color:rgba(200,232,196,0.5);font-size:0.8rem;margin:0.4rem 0 0;">quintals/hectare</p>
                    </div>""", unsafe_allow_html=True)
                with col_base:
                    st.markdown(f"""
                    <div style="background:rgba(212,168,67,0.12);border:1px solid rgba(212,168,67,0.35);
                                border-radius:16px;padding:2rem;text-align:center;">
                        <p style="color:rgba(200,232,196,0.6);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin:0;">Base Value</p>
                        <p style="color:#d4a843;font-size:2.8rem;font-weight:900;margin:0.5rem 0 0;font-family:'Playfair Display',serif;">{base_val:.2f}</p>
                        <p style="color:rgba(200,232,196,0.5);font-size:0.8rem;margin:0.4rem 0 0;">expected output</p>
                    </div>""", unsafe_allow_html=True)

                cumulative = float(base_val) if not isinstance(base_val, np.ndarray) else float(base_val)
                contributions = []
                for i, (feature, shap_val) in enumerate(zip(feature_names, shap_vals if shap_vals is not None else np.zeros(len(feature_names)))):
                    contributions.append({'Step': f"Step {i+1}", 'Feature': feature,
                                          'Impact': float(shap_val), 'Cumulative': cumulative})
                    cumulative += float(shap_val)

                contrib_df = pd.DataFrame(contributions)
                styled_contrib = contrib_df.style.format({
                    'Impact': '{:.4f}', 'Cumulative': '{:.2f}'
                }).background_gradient(subset=['Impact'], cmap='RdYlGn',
                    vmin=contrib_df['Impact'].min(), vmax=contrib_df['Impact'].max())
                st.dataframe(styled_contrib, use_container_width=True, hide_index=True)

            with tab3:
                impact_data = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': np.abs(shap_vals) if shap_vals is not None else np.zeros(len(feature_names))
                }).sort_values('Importance', ascending=True).tail(7)

                fig, ax = plt.subplots(figsize=(12, 6))
                palette = plt.cm.YlGn(np.linspace(0.35, 0.95, len(impact_data)))
                bars = ax.barh(impact_data['Feature'], impact_data['Importance'],
                               color=palette, edgecolor='#3d7a35', linewidth=1.5)

                ax.set_xlabel('Absolute SHAP Value', color='#a8e6a0', fontsize=11, fontweight='600')
                ax.set_title('Feature Importance — SHAP Analysis',
                             color='#a8e6a0', fontsize=13, fontweight='700', pad=16,
                             fontfamily='serif')
                ax.tick_params(colors='#c8e8c4', labelsize=10)

                fig.patch.set_facecolor('#0f1e10')
                ax.set_facecolor('#162a18')
                ax.spines['bottom'].set_color('#3d7a35')
                ax.spines['left'].set_color('#3d7a35')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='x', alpha=0.15, color='#7ec86a', linestyle='--')

                for bar, val in zip(bars, impact_data['Importance']):
                    ax.text(val, bar.get_y() + bar.get_height()/2,
                            f'  {val:.4f}', va='center', color='#c8e8c4',
                            fontweight='600', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)

                st.markdown("""
                <div style="background:rgba(22,45,24,0.8);border:1px solid rgba(94,166,78,0.25);
                            border-radius:14px;padding:1.4rem;margin-top:1.2rem;">
                    <p style="color:#7ec86a;font-weight:700;margin:0 0 0.7rem;">💡 How to read this chart</p>
                    <ul style="color:rgba(200,232,196,0.65);margin:0;padding-left:1.4rem;line-height:1.9;font-size:0.88rem;">
                        <li>Longer bars indicate features with stronger influence on the prediction</li>
                        <li>Deeper green shades denote higher overall importance</li>
                        <li>Values represent the absolute SHAP contribution magnitude</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with tab4:
                # ── GLOBAL FEATURE IMPORTANCE ──
                global_importance = pd.DataFrame({
                    'Feature': feature_names,
                    'Global Importance': model.feature_importances_
                }).sort_values('Global Importance', ascending=True).tail(7)

                fig, ax = plt.subplots(figsize=(12, 6))
                palette = plt.cm.RdYlGn(np.linspace(0.35, 0.95, len(global_importance)))
                bars = ax.barh(global_importance['Feature'], global_importance['Global Importance'],
                               color=palette, edgecolor='#d4a843', linewidth=1.5)

                ax.set_xlabel('Feature Importance Score', color='#a8e6a0', fontsize=11, fontweight='600')
                ax.set_title('Global Model Feature Importance — Across All Predictions',
                             color='#a8e6a0', fontsize=13, fontweight='700', pad=16,
                             fontfamily='serif')
                ax.tick_params(colors='#c8e8c4', labelsize=10)

                fig.patch.set_facecolor('#0f1e10')
                ax.set_facecolor('#162a18')
                ax.spines['bottom'].set_color('#3d7a35')
                ax.spines['left'].set_color('#3d7a35')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='x', alpha=0.15, color='#7ec86a', linestyle='--')

                for bar, val in zip(bars, global_importance['Global Importance']):
                    ax.text(val, bar.get_y() + bar.get_height()/2,
                            f'  {val:.4f}', va='center', color='#c8e8c4',
                            fontweight='600', fontsize=9)

                plt.tight_layout()
                st.pyplot(fig)

                st.markdown("""
                <div style="background:rgba(22,45,24,0.8);border:1px solid rgba(212,168,67,0.25);
                            border-radius:14px;padding:1.4rem;margin-top:1.2rem;">
                    <p style="color:#d4a843;font-weight:700;margin:0 0 0.7rem;">🌍 What this shows</p>
                    <ul style="color:rgba(200,232,196,0.65);margin:0;padding-left:1.4rem;line-height:1.9;font-size:0.88rem;">
                        <li>Model-wide feature importance across all training data</li>
                        <li>Shows which features the Random Forest uses most for decisions</li>
                        <li>Represents average feature contribution to model predictions</li>
                        <li>Different from SHAP which shows importance for THIS specific prediction</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ SHAP Visualization Error: {str(e)}")
    else:
        st.info("⏳ Initialising SHAP model explanations…")

st.markdown("---")

# ==================== FOOTER ====================
st.markdown("""
<div class="forest-footer">
    <div class="footer-title">🌾 YieldSense AI</div>
    <p style="color:rgba(200,232,196,0.6);font-size:0.95rem;">Intelligent Agricultural Prediction System</p>
    <div class="footer-divider"></div>
    <p style="color:rgba(200,232,196,0.45);font-size:0.85rem;line-height:2;">
        🤖 Advanced ML &nbsp;·&nbsp; 🌧️ Weather Integration &nbsp;·&nbsp; 📊 Real-time Analytics &nbsp;·&nbsp; 💡 Data-Driven Insights
    </p>
    <p style="color:rgba(200,232,196,0.25);font-size:0.78rem;margin-top:1.2rem;">
        ✨ Transforming Agriculture Through Technology ✨
    </p>
</div>
""", unsafe_allow_html=True)