import streamlit as st
import os
from dotenv import load_dotenv
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground,
    # Auth and project management
    is_authenticated
)
from components.auth_ui import (
    render_auth_page, render_user_sidebar, 
    render_settings_modal, check_authentication
)
from components.project_ui import (
    render_project_sidebar, render_save_dialog, 
    render_load_dialog, render_cloud_storage_section,
    render_cloud_files_modal
)
from services.storage_service import (
    upload_image, list_user_files, download_image_from_url, delete_file
)
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import io
import requests
import json
import time
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Stencil - Professional AI Image Editor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sleek, modern styling with enhanced UX
st.markdown("""
<style>
    /* ===== IMPORTS & VARIABLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-dark: #0a0f1a;
        --bg-card: rgba(15, 23, 42, 0.8);
        --bg-glass: rgba(30, 41, 59, 0.6);
        --border-color: rgba(99, 102, 241, 0.2);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.15);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.25);
        --shadow-glow: 0 0 30px rgba(99, 102, 241, 0.15);
        --transition-fast: 0.15s ease;
        --transition-normal: 0.25s ease;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* ===== GLOBAL STYLES ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0f1a 0%, #1e1b4b 50%, #0a0f1a 100%);
        background-attachment: fixed;
    }
    
    /* Animated background gradient */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }

    /* ===== HEADER ===== */
    .main-header {
        background: transparent;
        padding: 0.75rem 0 1.5rem 0;
        text-align: center;
        margin-bottom: 0.5rem;
        position: relative;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        color: #ffffff;
        text-shadow: 
            0 0 20px rgba(139, 92, 246, 0.8),
            0 0 40px rgba(99, 102, 241, 0.6),
            0 0 60px rgba(139, 92, 246, 0.4);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        animation: headerGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes headerGlow {
        0% { text-shadow: 0 0 20px rgba(139, 92, 246, 0.8), 0 0 40px rgba(99, 102, 241, 0.6), 0 0 60px rgba(139, 92, 246, 0.4); }
        100% { text-shadow: 0 0 30px rgba(167, 139, 250, 1), 0 0 60px rgba(139, 92, 246, 0.8), 0 0 80px rgba(99, 102, 241, 0.5); }
    }
    
    .main-header p {
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        color: #a5b4fc;
        font-weight: 500;
        letter-spacing: 0.05em;
    }
    
    .main-header::after {
        content: '';
        display: block;
        width: 120px;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        margin: 1rem auto 0 auto;
        border-radius: 3px;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
    }

    /* ===== APP CONTAINER ===== */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"],
    header[data-testid="stHeader"],
    .stApp > header {
        background: transparent !important;
    }
    
    .main .block-container {
        background: transparent;
        padding: 1rem 2rem 2rem 2rem;
        max-width: 1400px;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.01em;
        transition: all var(--transition-normal);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45), 0 0 40px rgba(139, 92, 246, 0.2);
        background: linear-gradient(135deg, var(--primary-light) 0%, #9333ea 100%);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(1);
    }
    
    /* Primary button variant */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, #9333ea 100%);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5), 0 0 40px rgba(139, 92, 246, 0.25);
    }
    
    /* Secondary button variant */
    .stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: var(--primary);
        color: var(--primary-light);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }

    /* ===== TABS - Modern Purple to Pink Gradient ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(236, 72, 153, 0.08) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 10px 12px;
        border-radius: 16px;
        border: 1px solid rgba(168, 85, 247, 0.25);
        box-shadow: 
            0 4px 20px rgba(139, 92, 246, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        background: rgba(30, 27, 75, 0.5);
        color: #e0d4fc !important;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        position: relative;
        overflow: hidden;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(236, 72, 153, 0.2) 100%);
        border-color: rgba(236, 72, 153, 0.4) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.25);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f472b6 100%) !important;
        color: #ffffff !important;
        font-weight: 700;
        border: none !important;
        box-shadow: 
            0 6px 25px rgba(168, 85, 247, 0.45),
            0 0 40px rgba(236, 72, 153, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"]:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 30px rgba(168, 85, 247, 0.5),
            0 0 50px rgba(236, 72, 153, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }
    
    /* Tab highlight line - hide it */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    /* Tab panel container */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* Tab border bottom styling */
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 0.9rem;
        transition: all var(--transition-fast);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stTextArea > div > div > textarea {
        min-height: 120px;
    }

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        transition: all var(--transition-normal);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
    }

    /* ===== SLIDERS ===== */
    .stSlider > div > div > div > div {
        background: var(--primary) !important;
    }
    
    .stSlider > div > div > div[data-baseweb="slider"] > div:first-child {
        background: rgba(99, 102, 241, 0.3) !important;
    }

    /* ===== INFO & ALERT BOXES ===== */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        backdrop-filter: blur(10px);
        border-left: 3px solid var(--primary);
        padding: 1rem 1.25rem;
        border-radius: var(--radius-sm);
        margin: 0.75rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        backdrop-filter: blur(10px);
        border-left: 3px solid var(--success);
        padding: 1rem 1.25rem;
        border-radius: var(--radius-sm);
        margin: 0.75rem 0;
    }
    
    .stAlert {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(10px);
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* ===== IMAGES ===== */
    .stImage {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        transition: transform var(--transition-normal), box-shadow var(--transition-normal);
    }
    
    .stImage:hover {
        transform: scale(1.01);
        box-shadow: var(--shadow-glow);
    }
    
    .stImage img {
        border-radius: var(--radius-md);
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(10, 15, 26, 0.98) 100%);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
        padding-top: 1rem;
    }
    
    [data-testid="stSidebar"] .element-container {
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        margin-bottom: 0.75rem;
    }
    
    [data-testid="stSidebar"] input {
        background: var(--bg-glass) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.875rem;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: var(--bg-glass);
        padding: 0.75rem;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.75rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--primary-light) !important;
        font-weight: 700;
        font-size: 1.25rem;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-color);
        color: var(--text-primary) !important;
        font-size: 0.85rem;
        transition: all var(--transition-fast);
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.1) !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: var(--border-color);
        margin: 1rem 0;
        opacity: 0.5;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    [data-testid="stSidebar"] .stAlert {
        background: var(--bg-glass) !important;
        border-radius: var(--radius-sm);
        font-size: 0.85rem;
    }

    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden; height: 0;}
    
    /* ===== FEATURE CARDS ===== */
    .feature-card {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        padding: 1.25rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
        margin: 0.5rem 0;
        transition: all var(--transition-normal);
        text-align: center;
    }
    
    .feature-card:hover {
        border-color: var(--primary);
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow);
    }
    
    .feature-card h4 {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-card p {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.5;
    }

    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .streamlit-expanderContent {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    }

    /* ===== SPINNER/LOADING ===== */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    }

    /* ===== COLOR PICKER ===== */
    .stColorPicker > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }

    /* ===== CANVAS ===== */
    canvas {
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-md);
    }

    /* ===== CHECKBOX ===== */
    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-size: 0.9rem;
    }
    
    .stCheckbox > label > span[data-testid="stCheckbox"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > label {
        color: var(--text-primary) !important;
    }
    
    .stRadio > div {
        background: var(--bg-glass);
        padding: 0.75rem;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-color);
    }

    /* ===== SELECTBOX ===== */
    [data-baseweb="select"] > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== SECTION TITLE - Purple to Pink Gradient ===== */
    .section-title {
        display: inline-block;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        padding: 0;
        letter-spacing: -0.02em;
        text-shadow: none;
        filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.4)) drop-shadow(0 0 40px rgba(236, 72, 153, 0.2));
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #a855f7, #ec4899, #f472b6);
        border-radius: 3px;
        opacity: 0.8;
    }
    
    .section-subtitle {
        color: rgba(196, 181, 253, 0.95) !important;
        font-size: 0.95rem;
        margin-top: 0.75rem;
        margin-bottom: 1.25rem;
        font-weight: 400;
        letter-spacing: 0.01em; 
    }

    /* ===== MARKDOWN & TEXT ===== */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary);
        line-height: 1.7;
    }

    /* ===== COLUMNS & LAYOUT ===== */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }

    /* ===== DIVIDER ===== */
    hr {
        border-color: var(--border-color);
        opacity: 0.3;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-glass);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container {
        animation: fadeIn 0.4s ease-out;
    }

    /* ===== TOAST/NOTIFICATIONS ===== */
    [data-testid="stToast"] {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md) !important;
    }

    /* ===== MODAL/DIALOG ===== */
    [data-testid="stModal"] {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg) !important;
    }

    /* ===== AUTH FORM ENHANCEMENTS ===== */
    /* Better form submit button styling */
    .stForm [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        border: none !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
    }
    
    .stForm [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5), 0 0 40px rgba(139, 92, 246, 0.2);
        background: linear-gradient(135deg, var(--primary-light) 0%, #9333ea 100%) !important;
    }
    
    /* Form inputs with better focus states */
    .stForm .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        color: var(--text-primary) !important;
        transition: all 0.2s ease;
    }
    
    .stForm .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        background: rgba(15, 23, 42, 0.9) !important;
    }
    
    .stForm .stTextInput > div > div > input::placeholder {
        color: rgba(148, 163, 184, 0.6) !important;
    }
    
    /* Enhanced checkbox styling */
    .stForm .stCheckbox {
        padding: 0.25rem 0;
    }
    
    .stForm .stCheckbox > label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
    }
    
    .stForm .stCheckbox > label:hover {
        color: var(--text-primary) !important;
    }
    
    /* Auth tabs specific styling */
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        justify-content: center;
    }
    
    /* Input labels */
    .stForm .stTextInput > label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.375rem;
    }
    
    /* Form spacing */
    .stForm > div {
        gap: 0.75rem !important;
    }
    
    /* Password visibility toggle */
    .stForm .stTextInput button {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
    }
    
    .stForm .stTextInput button:hover {
        color: var(--primary-light) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv(verbose=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('BRIA_API_KEY')
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'pending_urls' not in st.session_state:
        st.session_state.pending_urls = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = None
    if 'image_history' not in st.session_state:
        st.session_state.image_history = []
    if 'generation_count' not in st.session_state:
        st.session_state.generation_count = 0
    # Auth state
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'guest_mode' not in st.session_state:
        st.session_state.guest_mode = False
    # Project state
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None
    if 'current_project_name' not in st.session_state:
        st.session_state.current_project_name = None
    if 'show_save_dialog' not in st.session_state:
        st.session_state.show_save_dialog = False
    if 'show_load_dialog' not in st.session_state:
        st.session_state.show_load_dialog = False
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False
    if 'show_cloud_files' not in st.session_state:
        st.session_state.show_cloud_files = False
    # Gallery state - auto-load images on login
    if 'gallery_images' not in st.session_state:
        st.session_state.gallery_images = []
    if 'gallery_loaded' not in st.session_state:
        st.session_state.gallery_loaded = False

def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def apply_image_filter(image, filter_type):
    """Apply various filters to the image."""
    try:
        img = Image.open(io.BytesIO(image)) if isinstance(image, bytes) else image
        
        if filter_type == "None":
            return img
        elif filter_type == "Grayscale":
            return img.convert('L').convert('RGB')
        elif filter_type == "Sepia":
            img = img.convert('RGB')
            sepia_filter = np.array([[0.393, 0.769, 0.189],
                                      [0.349, 0.686, 0.168],
                                      [0.272, 0.534, 0.131]])
            img_array = np.array(img)
            sepia_img = img_array @ sepia_filter.T
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            return Image.fromarray(sepia_img)
        elif filter_type == "High Contrast":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(2.0)
        elif filter_type == "Brightness":
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.3)
        elif filter_type == "Blur":
            return img.filter(ImageFilter.GaussianBlur(radius=2))
        elif filter_type == "Sharpen":
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == "Edge Enhance":
            return img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == "Vintage":
            img = img.convert('RGB')
            img_array = np.array(img)
            # Apply vintage effect
            img_array = img_array * np.array([1.2, 1.0, 0.8])
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            return Image.fromarray(img_array)
        else:
            return img
    except Exception as e:
        st.error(f"Error applying filter: {str(e)}")
        return None

def save_to_history(image_url, operation_type, prompt=""):
    """Save generated image to history."""
    try:
        st.session_state.image_history.append({
            'url': image_url,
            'type': operation_type,
            'prompt': prompt,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state.generation_count += 1
    except Exception as e:
        print(f"Error saving to history: {str(e)}")

def save_image_to_database(image_url_or_bytes, filename=None, show_success=True):
    """
    Save an image to the database/cloud storage.
    
    Args:
        image_url_or_bytes: Either a URL string or bytes of the image
        filename: Optional filename for the saved image
        show_success: Whether to show success message
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to save images."}
        
        # Get image bytes
        if isinstance(image_url_or_bytes, str):
            # It's a URL, download it
            image_bytes = download_image(image_url_or_bytes)
            if not image_bytes:
                return {"success": False, "message": "Could not download image."}
        else:
            image_bytes = image_url_or_bytes
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stencil_{timestamp}.png"
        
        # Upload to storage
        result = upload_image(image_bytes, filename, "images")
        
        if result["success"]:
            # Reload gallery to include new image
            st.session_state.gallery_loaded = False
            if show_success:
                st.success("✅ Image saved to your gallery!")
            return result
        else:
            if show_success:
                st.error(f"❌ {result['message']}")
            return result
            
    except Exception as e:
        error_msg = f"Error saving image: {str(e)}"
        if show_success:
            st.error(error_msg)
        return {"success": False, "message": error_msg}

def load_gallery_images():
    """Load user's saved images from database/cloud storage AND from projects."""
    try:
        if not st.session_state.get("user"):
            st.session_state.gallery_images = []
            st.session_state.gallery_loaded = True
            st.session_state.gallery_error = None
            return
        
        all_images = []
        errors = []
        
        # Try to list files from the storage bucket
        storage_result = list_user_files("images")
        if storage_result["success"]:
            all_images.extend(storage_result["files"])
        else:
            errors.append(f"Storage: {storage_result.get('message', 'Unknown error')}")
        
        # Also get images from projects table
        from services.project_service import get_all_project_images
        project_result = get_all_project_images()
        if project_result["success"]:
            all_images.extend(project_result["images"])
        else:
            errors.append(f"Projects: {project_result.get('message', 'Unknown error')}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_images = []
        for img in all_images:
            url = img.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_images.append(img)
        
        st.session_state.gallery_images = unique_images
        st.session_state.gallery_error = "; ".join(errors) if errors and not unique_images else None
        st.session_state.gallery_loaded = True
        
    except Exception as e:
        print(f"Error loading gallery: {str(e)}")
        st.session_state.gallery_images = []
        st.session_state.gallery_loaded = True
        st.session_state.gallery_error = str(e)

def render_save_to_db_button(image_url_or_bytes, key_suffix="", button_text="💾 Save to Gallery"):
    """Render a save to database button for feature tabs."""
    if not st.session_state.get("user"):
        st.info("🔐 Login to save images to your gallery")
        return False
    
    if st.button(button_text, key=f"save_to_db_{key_suffix}", use_container_width=True):
        with st.spinner("Saving to gallery..."):
            result = save_image_to_database(image_url_or_bytes)
            return result["success"]
    return False


def check_generated_images():
    """Check if pending images are ready and update the display."""
    if st.session_state.pending_urls:
        ready_images = []
        still_pending = []
        
        for url in st.session_state.pending_urls:
            try:
                response = requests.head(url)
                # Consider an image ready if we get a 200 response with any content length
                if response.status_code == 200:
                    ready_images.append(url)
                else:
                    still_pending.append(url)
            except Exception as e:
                still_pending.append(url)
        
        # Update the pending URLs list
        st.session_state.pending_urls = still_pending
        
        # If we found any ready images, update the display
        if ready_images:
            st.session_state.edited_image = ready_images[0]  # Display the first ready image
            if len(ready_images) > 1:
                st.session_state.generated_images = ready_images  # Store all ready images
            return True
            
    return False

def auto_check_images(status_container):
    """Automatically check for image completion a few times."""
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts and st.session_state.pending_urls:
        time.sleep(2)  # Wait 2 seconds between checks
        if check_generated_images():
            status_container.success("✨ Image ready!")
            return True
        attempt += 1
    return False

def add_text_to_image(image, text, font_size=50, color="#000000", position="center", x_offset=0, y_offset=0):
    """
    Add text overlay to an image.
    
    Args:
        image: PIL Image object
        text: Text to add to the image
        font_size: Size of the font (default: 50)
        color: Color of the text in hex format (default: "#000000")
        position: Position preset ("center", "top-left", "top-center", "top-right", 
                  "bottom-left", "bottom-center", "bottom-right", "custom")
        x_offset: X coordinate offset for custom positioning
        y_offset: Y coordinate offset for custom positioning
    
    Returns:
        PIL Image object with text overlay
    """
    # Create a copy of the image to avoid modifying the original
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    # Try to use a nice font, fall back to default if not available
    try:
        # Try to load a TrueType font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            # Try alternative font names
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except:
                # Fall back to default font
                font = ImageFont.load_default()
    
    # Get text bounding box to calculate size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Get image dimensions
    img_width, img_height = img_copy.size
    
    # Calculate position based on preset or custom coordinates
    if position == "center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    elif position == "top-left":
        x = 20
        y = 20
    elif position == "top-center":
        x = (img_width - text_width) // 2
        y = 20
    elif position == "top-right":
        x = img_width - text_width - 20
        y = 20
    elif position == "bottom-left":
        x = 20
        y = img_height - text_height - 20
    elif position == "bottom-center":
        x = (img_width - text_width) // 2
        y = img_height - text_height - 20
    elif position == "bottom-right":
        x = img_width - text_width - 20
        y = img_height - text_height - 20
    elif position == "custom":
        x = x_offset
        y = y_offset
    else:
        # Default to center
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill=color, font=font)
    
    return img_copy

def main():
    initialize_session_state()
    
    # Check if user is authenticated
    if not check_authentication():
        render_auth_page()
        return
    
    # Compact header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Stencil</h1>
        <p>AI Image Generation & Editing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render dialogs if open
    if st.session_state.get('show_save_dialog'):
        render_save_dialog()
    if st.session_state.get('show_load_dialog'):
        render_load_dialog()
    if st.session_state.get('show_cloud_files'):
        render_cloud_files_modal()
    
    # Render settings modal if open
    render_settings_modal()
    
    # Enhanced Sidebar
    with st.sidebar:
        # User info section (login status, settings, logout)
        render_user_sidebar()
        
        st.markdown("### ⚙️ Settings")
        
        # API Key input with validation
        api_key = st.text_input(
            "🔑 Bria API Key:", 
            value=st.session_state.api_key if st.session_state.api_key else "", 
            type="password",
            help="Enter your Bria API key to access all features"
        )
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key connected")
        else:
            st.warning("⚠️ Please enter your API key")
        
        st.markdown("---")
        
        # Image History - simplified
        if st.session_state.image_history:
            with st.expander("📜 Recent History", expanded=False):
                for idx, item in enumerate(reversed(st.session_state.image_history[-5:])):
                    if st.button(f"🖼️ {item['type'][:12]} - {item['timestamp'][11:16]}", key=f"load_history_{idx}", use_container_width=True):
                        st.session_state.edited_image = item['url']
                        st.rerun()
        
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ About")
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 0.75rem; border-radius: 8px; 
                    border: 1px solid rgba(99, 102, 241, 0.2); font-size: 0.85rem; color: #94a3b8;">
            <strong style="color: #e0e7ff;">Stencil</strong> is a professional AI-powered 
            image editing platform for creating stunning visuals.
        </div>
        """, unsafe_allow_html=True)

    # Auto-load gallery images when user is logged in
    if st.session_state.get("user") and not st.session_state.get("gallery_loaded"):
        load_gallery_images()

    # Main tabs
    tabs = st.tabs([
        "🎨 Generate Image",
        "🖼️ Lifestyle Shot",
        "✨ Generative Fill",
        "🧹 Erase Elements",
        "🎭 Image Filters",
        "📝 Text Overlay",
        "🖼️ My Gallery"
    ])
    
    # Generate Images Tab
    with tabs[0]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="
                color: #d946ef;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                padding: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            ">AI Image Generation</h2>
            <p style="
                color: #c4b5fd;
                font-size: 0.95rem;
                margin: 0;
                font-weight: 400;
            ">Create stunning images from text descriptions using advanced AI models.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            
            # Prompt input
            prompt = st.text_area(
                "📝 Describe your vision", 
                value="",
                height=120,
                key="prompt_input",
                placeholder="A sleek modern smartphone on a wooden desk with natural lighting..."
            )
            
            # Store original prompt in session state when it changes
            if "original_prompt" not in st.session_state:
                st.session_state.original_prompt = prompt
            elif prompt != st.session_state.original_prompt:
                st.session_state.original_prompt = prompt
                st.session_state.enhanced_prompt = None
            
            # Enhanced prompt display
            if st.session_state.get('enhanced_prompt'):
                st.markdown("**✨ Enhanced Prompt:**")
                st.info(st.session_state.enhanced_prompt)
            
            # Enhance Prompt button
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("✨ Enhance Prompt", key="enhance_button"):
                    if not prompt:
                        st.warning("⚠️ Please enter a prompt to enhance.")
                    elif not st.session_state.api_key:
                        st.error("⚠️ Please enter your API key in the sidebar.")
                    else:
                        with st.spinner("✨ Enhancing your prompt with AI..."):
                            try:
                                result = enhance_prompt(st.session_state.api_key, prompt)
                                if result and result != prompt:
                                    st.session_state.enhanced_prompt = result
                                    st.success("✅ Prompt enhanced successfully!")
                                    st.rerun()
                                else:
                                    st.info("💡 Your prompt is already well-crafted!")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            
            with col_b:
                if st.button("🔄 Reset Prompt", key="reset_prompt"):
                    st.session_state.enhanced_prompt = None
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            
            st.markdown("**⚙️ Generation Settings**")
            
            num_images = st.slider("📊 Number of images", 1, 4, 1, 
                                   help="Generate multiple variations at once")
            
            aspect_ratio = st.selectbox(
                "📐 Aspect ratio", 
                ["1:1", "16:9", "9:16", "4:3", "3:4"],
                help="Choose the dimensions for your image"
            )
            
            enhance_img = st.checkbox("✨ Enhance image quality", value=True,
                                      help="Apply post-processing for better quality")
            
            # Style options
            st.markdown("**🎨 Style Options**")
            style = st.selectbox("Image Style", [
                "Realistic", "Artistic", "Cartoon", "Sketch", 
                "Watercolor", "Oil Painting", "Digital Art", "3D Render"
            ])
            
            # Advanced settings in expander
            with st.expander("🔧 Advanced Settings"):
                seed = st.number_input("🎲 Seed (for reproducibility)", 0, 999999, 0)
                steps = st.slider("🔄 Refinement steps", 20, 50, 30)
                guidance = st.slider("🎯 Prompt guidance", 1.0, 10.0, 7.5, 0.5)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate button
        st.markdown("---")
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        with col_gen2:
            if st.button("🎨 Generate Images", type="primary"):
                if not st.session_state.api_key:
                    st.error("⚠️ Please enter your API key in the sidebar.")
                    return
                
                if not prompt:
                    st.error("⚠️ Please enter a prompt first.")
                    return
                    
                with st.spinner("🎨 Creating your masterpiece..."):
                    try:
                        # Add style to prompt
                        final_prompt = st.session_state.enhanced_prompt or prompt
                        if style and style != "Realistic":
                            final_prompt = f"{final_prompt}, in {style.lower()} style"
                        
                        result = generate_hd_image(
                            prompt=final_prompt,
                            api_key=st.session_state.api_key,
                            num_results=num_images,
                            aspect_ratio=aspect_ratio,
                            sync=True,
                            enhance_image=enhance_img,
                            medium="art" if style != "Realistic" else "photography",
                            prompt_enhancement=False,
                            content_moderation=True,
                            seed=seed if seed > 0 else None,
                            steps_num=steps,
                            text_guidance_scale=guidance
                        )
                        
                        if result:
                            image_url = None
                            if isinstance(result, dict):
                                if "result_url" in result:
                                    image_url = result["result_url"]
                                elif "result_urls" in result:
                                    image_url = result["result_urls"][0]
                                elif "urls" in result:
                                    image_url = result["urls"][0]
                                elif "result" in result and isinstance(result["result"], list):
                                    for item in result["result"]:
                                        if isinstance(item, dict) and "urls" in item:
                                            image_url = item["urls"][0]
                                            break
                                        elif isinstance(item, list) and len(item) > 0:
                                            image_url = item[0]
                                            break
                            
                            if image_url:
                                st.session_state.edited_image = image_url
                                save_to_history(image_url, "Generate Image", final_prompt)
                                st.success("✅ Image generated successfully!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Could not extract image URL from response")
                                with st.expander("🔍 Debug Info"):
                                    st.json(result)
                                
                    except Exception as e:
                        st.error(f"❌ Error generating images: {str(e)}")
                        if "401" in str(e):
                            st.error("🔑 Invalid API key. Please check your credentials.")
                        elif "422" in str(e):
                            st.error("⚠️ Content moderation blocked this request.")
        
        # Display generated image
        if st.session_state.edited_image:
            st.markdown("---")
            st.markdown("### 🖼️ Generated Result")
            col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
            with col_img2:
                st.image(st.session_state.edited_image, use_column_width=True)
                image_data = download_image(st.session_state.edited_image)
                if image_data:
                    st.download_button(
                        "⬇️ Download Image",
                        image_data,
                        f"Stencil_generated_{int(time.time())}.png",
                        "image/png"
                    )
                    # Save to gallery button
                    render_save_to_db_button(st.session_state.edited_image, "generate")
    
    # Product Photography Tab
    with tabs[1]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="
                color: #d946ef;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                padding: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            ">Product Photography</h2>
            <p style="
                color: #c4b5fd;
                font-size: 0.95rem;
                margin: 0;
                font-weight: 400;
            ">Generate professional product shots and lifestyle images.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"], key="product_upload")
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Product editing options
                edit_option = st.selectbox("Select Edit Option", [
                    "Create Packshot",
                    "Add Shadow",
                    "Lifestyle Shot"
                ])
                
                if edit_option == "Create Packshot":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        bg_color = st.color_picker("🎨 Background Color", "#FFFFFF")
                        sku = st.text_input("📦 SKU (optional)", "")
                    with col_b:
                        force_rmbg = st.checkbox("✂️ Force Background Removal", False)
                        content_moderation = st.checkbox("🛡️ Enable Content Moderation", False)
                    
                    if st.button("✨ Create Packshot"):
                        if not st.session_state.api_key:
                            st.error("⚠️ Please enter your API key in the sidebar.")
                            return
                        
                        with st.spinner("📸 Creating professional packshot..."):
                            try:
                                result = create_packshot(
                                    st.session_state.api_key,
                                    uploaded_file.getvalue(),
                                    background_color=bg_color,
                                    sku=sku if sku else None,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.session_state.edited_image = result["result_url"]
                                    save_to_history(result["result_url"], "Packshot", "")
                                    st.success("✅ Packshot created successfully!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ No result URL in the API response.")
                                    with st.expander("🔍 Debug Info"):
                                        st.json(result)
                            except Exception as e:
                                st.error(f"❌ Error creating packshot: {str(e)}")
                                if "422" in str(e):
                                    st.warning("⚠️ Content moderation blocked this image.")
                                elif "401" in str(e):
                                    st.error("🔑 Invalid API key.")
                
                elif edit_option == "Add Shadow":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop"])
                        bg_color = st.color_picker("Background Color (optional)", "#FFFFFF")
                        use_transparent_bg = st.checkbox("Use Transparent Background", True)
                        shadow_color = st.color_picker("Shadow Color", "#000000")
                        sku = st.text_input("SKU (optional)", "")
                        
                        # Shadow offset
                        st.subheader("Shadow Offset")
                        offset_x = st.slider("X Offset", -50, 50, 0)
                        offset_y = st.slider("Y Offset", -50, 50, 15)
                    
                    with col_b:
                        shadow_intensity = st.slider("Shadow Intensity", 0, 100, 60)
                        shadow_blur = st.slider("Shadow Blur", 0, 50, 15 if shadow_type.lower() == "regular" else 20)
                        
                        # Float shadow specific controls
                        if shadow_type == "Float":
                            st.subheader("Float Shadow Settings")
                            shadow_width = st.slider("Shadow Width", -100, 100, 0)
                            shadow_height = st.slider("Shadow Height", -100, 100, 70)
                        
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                    
                    if st.button("Add Shadow"):
                        with st.spinner("Adding shadow effect..."):
                            try:
                                result = add_shadow(
                                    api_key=st.session_state.api_key,
                                    image_data=uploaded_file.getvalue(),
                                    shadow_type=shadow_type.lower(),
                                    background_color=None if use_transparent_bg else bg_color,
                                    shadow_color=shadow_color,
                                    shadow_offset=[offset_x, offset_y],
                                    shadow_intensity=shadow_intensity,
                                    shadow_blur=shadow_blur,
                                    shadow_width=shadow_width if shadow_type == "Float" else None,
                                    shadow_height=shadow_height if shadow_type == "Float" else 70,
                                    sku=sku if sku else None,
                                    force_rmbg=force_rmbg,
                                    content_moderation=content_moderation
                                )
                                
                                if result and "result_url" in result:
                                    st.success("✨ Shadow added successfully!")
                                    st.session_state.edited_image = result["result_url"]
                                else:
                                    st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error adding shadow: {str(e)}")
                                if "422" in str(e):
                                    st.warning("Content moderation failed. Please ensure the image is appropriate.")
                
                elif edit_option == "Lifestyle Shot":
                    shot_type = st.radio("Shot Type", ["Text Prompt", "Reference Image"])
                    
                    # Common settings for both types
                    col1, col2 = st.columns(2)
                    with col1:
                        placement_type = st.selectbox("Placement Type", [
                            "Original", "Automatic", "Manual Placement",
                            "Manual Padding", "Custom Coordinates"
                        ])
                        num_results = st.slider("Number of Results", 1, 8, 4)
                        sync_mode = st.checkbox("Synchronous Mode", False,
                            help="Wait for results instead of getting URLs immediately")
                        original_quality = st.checkbox("Original Quality", False,
                            help="Maintain original image quality")
                        
                        if placement_type == "Manual Placement":
                            positions = st.multiselect("Select Positions", [
                                "Upper Left", "Upper Right", "Bottom Left", "Bottom Right",
                                "Right Center", "Left Center", "Upper Center",
                                "Bottom Center", "Center Vertical", "Center Horizontal"
                            ], ["Upper Left"])
                        
                        elif placement_type == "Manual Padding":
                            st.subheader("Padding Values (pixels)")
                            pad_left = st.number_input("Left Padding", 0, 1000, 0)
                            pad_right = st.number_input("Right Padding", 0, 1000, 0)
                            pad_top = st.number_input("Top Padding", 0, 1000, 0)
                            pad_bottom = st.number_input("Bottom Padding", 0, 1000, 0)
                        
                        elif placement_type in ["Automatic", "Manual Placement", "Custom Coordinates"]:
                            st.subheader("Shot Size")
                            shot_width = st.number_input("Width", 100, 2000, 1000)
                            shot_height = st.number_input("Height", 100, 2000, 1000)
                    
                    with col2:
                        if placement_type == "Custom Coordinates":
                            st.subheader("Product Position")
                            fg_width = st.number_input("Product Width", 50, 1000, 500)
                            fg_height = st.number_input("Product Height", 50, 1000, 500)
                            fg_x = st.number_input("X Position", -500, 1500, 0)
                            fg_y = st.number_input("Y Position", -500, 1500, 0)
                        
                        sku = st.text_input("SKU (optional)")
                        force_rmbg = st.checkbox("Force Background Removal", False)
                        content_moderation = st.checkbox("Enable Content Moderation", False)
                        
                        if shot_type == "Text Prompt":
                            fast_mode = st.checkbox("Fast Mode", True,
                                help="Balance between speed and quality")
                            optimize_desc = st.checkbox("Optimize Description", True,
                                help="Enhance scene description using AI")
                            if not fast_mode:
                                exclude_elements = st.text_area("Exclude Elements (optional)",
                                    help="Elements to exclude from the generated scene")
                        else:  # Reference Image
                            enhance_ref = st.checkbox("Enhance Reference Image", True,
                                help="Improve lighting, shadows, and texture")
                            ref_influence = st.slider("Reference Influence", 0.0, 1.0, 1.0,
                                help="Control similarity to reference image")
                    
                    if shot_type == "Text Prompt":
                        prompt = st.text_area("Describe the environment")
                        if st.button("Generate Lifestyle Shot") and prompt:
                            with st.spinner("Generating lifestyle shot..."):
                                try:
                                    # Convert placement selections to API format
                                    if placement_type == "Manual Placement":
                                        manual_placements = [p.lower().replace(" ", "_") for p in positions]
                                    else:
                                        manual_placements = ["upper_left"]
                                    
                                    result = lifestyle_shot_by_text(
                                        api_key=st.session_state.api_key,
                                        image_data=uploaded_file.getvalue(),
                                        scene_description=prompt,
                                        placement_type=placement_type.lower().replace(" ", "_"),
                                        num_results=num_results,
                                        sync=sync_mode,
                                        fast=fast_mode,
                                        optimize_description=optimize_desc,
                                        shot_size=[shot_width, shot_height] if placement_type != "Original" else [1000, 1000],
                                        original_quality=original_quality,
                                        exclude_elements=exclude_elements if not fast_mode else None,
                                        manual_placement_selection=manual_placements,
                                        padding_values=[pad_left, pad_right, pad_top, pad_bottom] if placement_type == "Manual Padding" else [0, 0, 0, 0],
                                        foreground_image_size=[fg_width, fg_height] if placement_type == "Custom Coordinates" else None,
                                        foreground_image_location=[fg_x, fg_y] if placement_type == "Custom Coordinates" else None,
                                        force_rmbg=force_rmbg,
                                        content_moderation=content_moderation,
                                        sku=sku if sku else None
                                    )
                                    
                                    if result:
                                        # Debug logging
                                        st.write("Debug - Raw API Response:", result)
                                        
                                        if sync_mode:
                                            if isinstance(result, dict):
                                                if "result_url" in result:
                                                    st.session_state.edited_image = result["result_url"]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result_urls" in result:
                                                    st.session_state.edited_image = result["result_urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result" in result and isinstance(result["result"], list):
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            st.session_state.edited_image = item["urls"][0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                        elif isinstance(item, list) and len(item) > 0:
                                                            st.session_state.edited_image = item[0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                elif "urls" in result:
                                                    st.session_state.edited_image = result["urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                        else:
                                            urls = []
                                            if isinstance(result, dict):
                                                if "urls" in result:
                                                    urls.extend(result["urls"][:num_results])  # Limit to requested number
                                                elif "result" in result and isinstance(result["result"], list):
                                                    # Process each result item
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            urls.extend(item["urls"])
                                                        elif isinstance(item, list):
                                                            urls.extend(item)
                                                        # Break if we have enough URLs
                                                        if len(urls) >= num_results:
                                                            break
                                                    
                                                    # Trim to requested number
                                                    urls = urls[:num_results]
                                            
                                            if urls:
                                                st.session_state.pending_urls = urls
                                                
                                                # Create a container for status messages
                                                status_container = st.empty()
                                                refresh_container = st.empty()
                                                
                                                # Show initial status
                                                status_container.info(f"🎨 Generation started! Waiting for {len(urls)} image{'s' if len(urls) > 1 else ''}...")
                                                
                                                # Try automatic checking first
                                                if auto_check_images(status_container):
                                                    st.experimental_rerun()
                                                
                                                # Add refresh button for manual checking
                                                if refresh_container.button("🔄 Check for Generated Images"):
                                                    with st.spinner("Checking for completed images..."):
                                                        if check_generated_images():
                                                            status_container.success("✨ Image ready!")
                                                            st.experimental_rerun()
                                                        else:
                                                            status_container.warning(f"⏳ Still generating your image{'s' if len(urls) > 1 else ''}... Please check again in a moment.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    if "422" in str(e):
                                        st.warning("Content moderation failed. Please ensure the content is appropriate.")
                    else:
                        ref_image = st.file_uploader("Upload Reference Image", type=["png", "jpg", "jpeg"], key="ref_upload")
                        if st.button("Generate Lifestyle Shot") and ref_image:
                            with st.spinner("Generating lifestyle shot..."):
                                try:
                                    # Convert placement selections to API format
                                    if placement_type == "Manual Placement":
                                        manual_placements = [p.lower().replace(" ", "_") for p in positions]
                                    else:
                                        manual_placements = ["upper_left"]
                                    
                                    result = lifestyle_shot_by_image(
                                        api_key=st.session_state.api_key,
                                        image_data=uploaded_file.getvalue(),
                                        reference_image=ref_image.getvalue(),
                                        placement_type=placement_type.lower().replace(" ", "_"),
                                        num_results=num_results,
                                        sync=sync_mode,
                                        shot_size=[shot_width, shot_height] if placement_type != "Original" else [1000, 1000],
                                        original_quality=original_quality,
                                        manual_placement_selection=manual_placements,
                                        padding_values=[pad_left, pad_right, pad_top, pad_bottom] if placement_type == "Manual Padding" else [0, 0, 0, 0],
                                        foreground_image_size=[fg_width, fg_height] if placement_type == "Custom Coordinates" else None,
                                        foreground_image_location=[fg_x, fg_y] if placement_type == "Custom Coordinates" else None,
                                        force_rmbg=force_rmbg,
                                        content_moderation=content_moderation,
                                        sku=sku if sku else None,
                                        enhance_ref_image=enhance_ref,
                                        ref_image_influence=ref_influence
                                    )
                                    
                                    if result:
                                        # Debug logging
                                        st.write("Debug - Raw API Response:", result)
                                        
                                        if sync_mode:
                                            if isinstance(result, dict):
                                                if "result_url" in result:
                                                    st.session_state.edited_image = result["result_url"]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result_urls" in result:
                                                    st.session_state.edited_image = result["result_urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                                elif "result" in result and isinstance(result["result"], list):
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            st.session_state.edited_image = item["urls"][0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                        elif isinstance(item, list) and len(item) > 0:
                                                            st.session_state.edited_image = item[0]
                                                            st.success("✨ Image generated successfully!")
                                                            break
                                                elif "urls" in result:
                                                    st.session_state.edited_image = result["urls"][0]
                                                    st.success("✨ Image generated successfully!")
                                        else:
                                            urls = []
                                            if isinstance(result, dict):
                                                if "urls" in result:
                                                    urls.extend(result["urls"][:num_results])  # Limit to requested number
                                                elif "result" in result and isinstance(result["result"], list):
                                                    # Process each result item
                                                    for item in result["result"]:
                                                        if isinstance(item, dict) and "urls" in item:
                                                            urls.extend(item["urls"])
                                                        elif isinstance(item, list):
                                                            urls.extend(item)
                                                        # Break if we have enough URLs
                                                        if len(urls) >= num_results:
                                                            break
                                                    
                                                    # Trim to requested number
                                                    urls = urls[:num_results]
                                            
                                            if urls:
                                                st.session_state.pending_urls = urls
                                                
                                                # Create a container for status messages
                                                status_container = st.empty()
                                                refresh_container = st.empty()
                                                
                                                # Show initial status
                                                status_container.info(f"🎨 Generation started! Waiting for {len(urls)} image{'s' if len(urls) > 1 else ''}...")
                                                
                                                # Try automatic checking first
                                                if auto_check_images(status_container):
                                                    st.experimental_rerun()
                                                
                                                # Add refresh button for manual checking
                                                if refresh_container.button("🔄 Check for Generated Images"):
                                                    with st.spinner("Checking for completed images..."):
                                                        if check_generated_images():
                                                            status_container.success("✨ Image ready!")
                                                            st.experimental_rerun()
                                                        else:
                                                            status_container.warning(f"⏳ Still generating your image{'s' if len(urls) > 1 else ''}... Please check again in a moment.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    if "422" in str(e):
                                        st.warning("Content moderation failed. Please ensure the content is appropriate.")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Edited Image", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "edited_product.png",
                            "image/png"
                        )
                        # Save to gallery button
                        render_save_to_db_button(st.session_state.edited_image, "lifestyle")
                elif st.session_state.pending_urls:
                    st.info("🔄 Images are being generated. Click the refresh button above to check if they're ready.")
                else:
                    st.info("👆 Upload an image above and select an editing option to get started!")

    # Generative Fill Tab
    with tabs[2]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="
                color: #d946ef;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                padding: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            ">Generative Fill</h2>
            <p style="
                color: #c4b5fd;
                font-size: 0.95rem;
                margin: 0;
                font-weight: 400;
            ">Draw a mask on the image and describe what you want to generate in that area.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="fill_upload")
        if uploaded_file:
            # Create columns for original image and canvas
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original image
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image dimensions for canvas
                img = Image.open(uploaded_file)
                img_width, img_height = img.size
                
                # Calculate aspect ratio and set canvas height
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 800)  # Max width of 800px
                canvas_height = int(canvas_width * aspect_ratio)
                
                # Resize image to match canvas dimensions
                img = img.resize((canvas_width, canvas_height))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to numpy array with proper shape and type
                img_array = np.array(img).astype(np.uint8)
                
                # Add drawing canvas using Streamlit's drawing canvas component
                stroke_width = st.slider("Brush width", 1, 50, 20)
                stroke_color = st.color_picker("Brush color", "#fff")
                drawing_mode = "freedraw"
                
                # Create canvas with background image
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    drawing_mode=drawing_mode,
                    background_color="",  # Transparent background
                    background_image=img if img_array.shape[-1] == 3 else None,  # Only pass RGB images
                    height=canvas_height,
                    width=canvas_width,
                    key="canvas",
                )
                
                # Options for generation
                st.subheader("Generation Options")
                prompt = st.text_area("Describe what to generate in the masked area")
                negative_prompt = st.text_area("Describe what to avoid (optional)")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    num_results = st.slider("Number of variations", 1, 4, 1)
                    sync_mode = st.checkbox("Synchronous Mode", False,
                        help="Wait for results instead of getting URLs immediately",
                        key="gen_fill_sync_mode")
                
                with col_b:
                    seed = st.number_input("Seed (optional)", min_value=0, value=0,
                        help="Use same seed to reproduce results")
                    content_moderation = st.checkbox("Enable Content Moderation", False,
                        key="gen_fill_content_mod")
                
                if st.button("🎨 Generate", type="primary"):
                    if not prompt:
                        st.error("Please enter a prompt describing what to generate.")
                        return
                    
                    if canvas_result.image_data is None:
                        st.error("Please draw a mask on the image first.")
                        return
                    
                    # Convert canvas result to mask
                    mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                    mask_img = mask_img.convert('L')
                    
                    # Convert mask to bytes
                    mask_bytes = io.BytesIO()
                    mask_img.save(mask_bytes, format='PNG')
                    mask_bytes = mask_bytes.getvalue()
                    
                    # Convert uploaded image to bytes
                    image_bytes = uploaded_file.getvalue()
                    
                    with st.spinner("🎨 Generating..."):
                        try:
                            result = generative_fill(
                                st.session_state.api_key,
                                image_bytes,
                                mask_bytes,
                                prompt,
                                negative_prompt=negative_prompt if negative_prompt else None,
                                num_results=num_results,
                                sync=sync_mode,
                                seed=seed if seed != 0 else None,
                                content_moderation=content_moderation
                            )
                            
                            if result:
                                st.write("Debug - API Response:", result)
                                
                                if sync_mode:
                                    if "urls" in result and result["urls"]:
                                        st.session_state.edited_image = result["urls"][0]
                                        if len(result["urls"]) > 1:
                                            st.session_state.generated_images = result["urls"]
                                        st.success("✨ Generation complete!")
                                    elif "result_url" in result:
                                        st.session_state.edited_image = result["result_url"]
                                        st.success("✨ Generation complete!")
                                else:
                                    if "urls" in result:
                                        st.session_state.pending_urls = result["urls"][:num_results]
                                        
                                        # Create containers for status
                                        status_container = st.empty()
                                        refresh_container = st.empty()
                                        
                                        # Show initial status
                                        status_container.info(f"🎨 Generation started! Waiting for {len(st.session_state.pending_urls)} image{'s' if len(st.session_state.pending_urls) > 1 else ''}...")
                                        
                                        # Try automatic checking
                                        if auto_check_images(status_container):
                                            st.rerun()
                                        
                                        # Add refresh button
                                        if refresh_container.button("🔄 Check for Generated Images"):
                                            if check_generated_images():
                                                status_container.success("✨ Images ready!")
                                                st.rerun()
                                            else:
                                                status_container.warning("⏳ Still generating... Please check again in a moment.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            st.write("Full error details:", str(e))
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="Generated Result", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            "generated_fill.png",
                            "image/png"
                        )
                        # Save to gallery button
                        render_save_to_db_button(st.session_state.edited_image, "genfill")
                elif st.session_state.pending_urls:
                    st.info("Generation in progress. Click the refresh button above to check status.")

    # Erase Elements Tab
    with tabs[3]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="
                color: #d946ef;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                padding: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            ">Erase Elements</h2>
            <p style="
                color: #c4b5fd;
                font-size: 0.95rem;
                margin: 0;
                font-weight: 400;
            ">Upload an image and select the area you want to erase.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="erase_upload")
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                # Display original image
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
                
                # Get image dimensions for canvas
                img = Image.open(uploaded_file)
                img_width, img_height = img.size
                
                # Calculate aspect ratio and set canvas height
                aspect_ratio = img_height / img_width
                canvas_width = min(img_width, 800)  # Max width of 800px
                canvas_height = int(canvas_width * aspect_ratio)
                
                # Resize image to match canvas dimensions
                img = img.resize((canvas_width, canvas_height))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Add drawing canvas using Streamlit's drawing canvas component
                stroke_width = st.slider("Brush width", 1, 50, 20, key="erase_brush_width")
                stroke_color = st.color_picker("Brush color", "#fff", key="erase_brush_color")
                
                # Create canvas with background image
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_color="",  # Transparent background
                    background_image=img,  # Pass PIL Image directly
                    drawing_mode="freedraw",
                    height=canvas_height,
                    width=canvas_width,
                    key="erase_canvas",
                )
                
                # Options for erasing
                st.subheader("Erase Options")
                content_moderation = st.checkbox("Enable Content Moderation", False, key="erase_content_mod")
                
                if st.button("🎨 Erase Selected Area", key="erase_btn"):
                    if not canvas_result.image_data is None:
                        with st.spinner("Erasing selected area..."):
                            try:
                                # Convert canvas result to mask
                                mask_img = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
                                mask_img = mask_img.convert('L')
                                
                                # Convert uploaded image to bytes
                                image_bytes = uploaded_file.getvalue()
                                
                                result = erase_foreground(
                                    st.session_state.api_key,
                                    image_data=image_bytes,
                                    content_moderation=content_moderation
                                )
                                
                                if result:
                                    if "result_url" in result:
                                        st.session_state.edited_image = result["result_url"]
                                        st.success("✨ Area erased successfully!")
                                    else:
                                        st.error("No result URL in the API response. Please try again.")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                                if "422" in str(e):
                                    st.warning("Content moderation failed. Please ensure the image is appropriate.")
                    else:
                        st.warning("⚠️ Please draw on the image to select the area to erase.")
            
            with col2:
                if st.session_state.edited_image:
                    st.image(st.session_state.edited_image, caption="✨ Result", use_column_width=True)
                    image_data = download_image(st.session_state.edited_image)
                    if image_data:
                        st.download_button(
                            "⬇️ Download Result",
                            image_data,
                            f"Stencil_erased_{int(time.time())}.png",
                            "image/png",
                            key="erase_download"
                        )
                        # Save to gallery button
                        render_save_to_db_button(st.session_state.edited_image, "erase")
                else:
                    st.info("👆 Draw on the image above and click 'Erase Selected Area' to remove elements.")
    
    # Image Filters Tab
    with tabs[4]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="
                color: #d946ef;
                font-size: 2.2rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                padding: 0;
                letter-spacing: -0.02em;
                text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            ">Image Filters</h2>
            <p style="
                color: #c4b5fd;
                font-size: 0.95rem;
                margin: 0;
                font-weight: 400;
            ">Apply professional filters and enhancements to your images.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📤 Upload Image", 
            type=["png", "jpg", "jpeg"], 
            key="filter_upload",
            help="Upload an image to apply filters"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🖼️ Original Image**")
                original_img = Image.open(uploaded_file)
                st.image(original_img, use_column_width=True)
                
                st.markdown("---")
                st.markdown("**🎨 Filter Options**")
                
                filter_type = st.selectbox(
                    "Select Filter",
                    ["None", "Grayscale", "Sepia", "High Contrast", "Brightness", 
                     "Blur", "Sharpen", "Edge Enhance", "Vintage"],
                    help="Choose a filter to apply"
                )
                
                # Additional adjustments
                with st.expander("🔧 Fine-tune Adjustments"):
                    brightness = st.slider("💡 Brightness", 0.5, 2.0, 1.0, 0.1)
                    contrast = st.slider("🌓 Contrast", 0.5, 2.0, 1.0, 0.1)
                    saturation = st.slider("🎨 Saturation", 0.0, 2.0, 1.0, 0.1)
                    sharpness = st.slider("🔪 Sharpness", 0.0, 2.0, 1.0, 0.1)
                
                if st.button("✨ Apply Filters", type="primary"):
                    with st.spinner("🎨 Applying filters..."):
                        try:
                            # Apply selected filter
                            filtered_img = apply_image_filter(original_img, filter_type)
                            
                            if filtered_img:
                                # Apply fine-tune adjustments
                                if brightness != 1.0:
                                    enhancer = ImageEnhance.Brightness(filtered_img)
                                    filtered_img = enhancer.enhance(brightness)
                                
                                if contrast != 1.0:
                                    enhancer = ImageEnhance.Contrast(filtered_img)
                                    filtered_img = enhancer.enhance(contrast)
                                
                                if saturation != 1.0:
                                    enhancer = ImageEnhance.Color(filtered_img)
                                    filtered_img = enhancer.enhance(saturation)
                                
                                if sharpness != 1.0:
                                    enhancer = ImageEnhance.Sharpness(filtered_img)
                                    filtered_img = enhancer.enhance(sharpness)
                                
                                # Save filtered image to session state
                                img_byte_arr = io.BytesIO()
                                filtered_img.save(img_byte_arr, format='PNG')
                                img_byte_arr = img_byte_arr.getvalue()
                                
                                # Store as base64 for display
                                b64_img = base64.b64encode(img_byte_arr).decode()
                                st.session_state.filtered_image = f"data:image/png;base64,{b64_img}"
                                st.session_state.filtered_image_bytes = img_byte_arr
                                
                                st.success("✅ Filters applied successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error applying filters: {str(e)}")
            
            with col2:
                if 'filtered_image' in st.session_state and st.session_state.filtered_image:
                    st.markdown("**✨ Filtered Result**")
                    st.image(st.session_state.filtered_image, use_column_width=True)
                    
                    if 'filtered_image_bytes' in st.session_state:
                        st.download_button(
                            "⬇️ Download Filtered Image",
                            st.session_state.filtered_image_bytes,
                            f"Stencil_filtered_{int(time.time())}.png",
                            "image/png"
                        )
                        # Save to gallery button
                        render_save_to_db_button(st.session_state.filtered_image_bytes, "filter")
                    
                    # Comparison slider would go here if available
                    if st.button("🔄 Reset Filters"):
                        del st.session_state.filtered_image
                        del st.session_state.filtered_image_bytes
                        st.rerun()
                else:
                    st.info("👈 Select a filter and click 'Apply Filters' to see the result")
                    
                    # Filter preview cards
                    st.markdown("**📋 Filter Previews**")
                    st.markdown("""
                    <div class="info-box">
                    <b>Available Filters:</b><br>
                    • <b>Grayscale:</b> Convert to black & white<br>
                    • <b>Sepia:</b> Vintage warm tone<br>
                    • <b>High Contrast:</b> Enhance contrast<br>
                    • <b>Brightness:</b> Increase brightness<br>
                    • <b>Blur:</b> Soft gaussian blur<br>
                    • <b>Sharpen:</b> Enhance details<br>
                    • <b>Edge Enhance:</b> Emphasize edges<br>
                    • <b>Vintage:</b> Retro color effect
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📤 Upload an image to start applying filters and enhancements")
            
            # Feature showcase
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                st.markdown("""
                <div class="feature-card">
                <h4>🎨 Creative Filters</h4>
                <p>Apply professional-grade filters instantly</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_f2:
                st.markdown("""
                <div class="feature-card">
                <h4>⚙️ Fine Control</h4>
                <p>Adjust brightness, contrast, and more</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_f3:
                st.markdown("""
                <div class="feature-card">
                <h4>⚡ Instant Results</h4>
                <p>See changes in real-time</p>
                </div>
                """, unsafe_allow_html=True)
        
    # Text Overlay Tab
    with tabs[5]:
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h2 style="
                    color: #d946ef;
                    font-size: 2.2rem;
                    font-weight: 800;
                    margin: 0 0 0.5rem 0;
                    padding: 0;
                    letter-spacing: -0.02em;
                    text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
                ">Text Overlay</h2>
                <p style="
                    color: #c4b5fd;
                    font-size: 0.95rem;
                    margin: 0;
                    font-weight: 400;
                ">Add custom text to your images with full control over appearance and positioning.</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "📤 Upload Image", 
                type=["png", "jpg", "jpeg"], 
                key="text_overlay_upload",
                help="Upload an image to add text overlay"
            )
            
            if uploaded_file:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🖼️ Original Image**")
                    original_img = Image.open(uploaded_file)
                    st.image(original_img, use_column_width=True)
                    
                    st.markdown("---")
                    st.markdown("**✏️ Text Settings**")
                    
                    # Text input
                    text_input = st.text_area(
                        "Enter your text",
                        placeholder="Type your text here...",
                        help="Enter the text you want to add to the image"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        # Font size
                        font_size = st.slider(
                            "📏 Font Size",
                            min_value=10,
                            max_value=200,
                            value=50,
                            step=5,
                            help="Adjust the size of the text"
                        )
                        
                        # Text color
                        text_color = st.color_picker(
                            "🎨 Text Color",
                            "#000000",
                            help="Choose the color of your text"
                        )
                    
                    with col_b:
                        # Position preset
                        position = st.selectbox(
                            "📍 Position",
                            [
                                "Center",
                                "Top Left",
                                "Top Center",
                                "Top Right",
                                "Bottom Left",
                                "Bottom Center",
                                "Bottom Right",
                                "Custom"
                            ],
                            help="Choose where to place the text"
                        )
                        
                        # Custom position controls (only shown if Custom is selected)
                        if position == "Custom":
                            x_offset = st.number_input(
                                "X Position",
                                min_value=0,
                                max_value=original_img.width,
                                value=original_img.width // 2,
                                help="Horizontal position (pixels from left)"
                            )
                            y_offset = st.number_input(
                                "Y Position",
                                min_value=0,
                                max_value=original_img.height,
                                value=original_img.height // 2,
                                help="Vertical position (pixels from top)"
                            )
                        else:
                            x_offset = 0
                            y_offset = 0
                    
                    # Apply button
                    if st.button("✨ Add Text to Image", type="primary"):
                        if not text_input:
                            st.warning("⚠️ Please enter some text first!")
                        else:
                            with st.spinner("Adding text to image..."):
                                try:
                                    # Convert position to lowercase with hyphens
                                    position_key = position.lower().replace(" ", "-")
                                    
                                    # Add text to image
                                    result_img = add_text_to_image(
                                        original_img,
                                        text_input,
                                        font_size=font_size,
                                        color=text_color,
                                        position=position_key,
                                        x_offset=x_offset,
                                        y_offset=y_offset
                                    )
                                    
                                    # Store in session state
                                    img_byte_arr = io.BytesIO()
                                    result_img.save(img_byte_arr, format='PNG')
                                    img_byte_arr = img_byte_arr.getvalue()
                                    
                                    # Store as base64 for display
                                    b64_img = base64.b64encode(img_byte_arr).decode()
                                    st.session_state.text_overlay_result = f"data:image/png;base64,{b64_img}"
                                    st.session_state.text_overlay_bytes = img_byte_arr
                                    
                                    st.success("✅ Text added successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error adding text: {str(e)}")
                
                with col2:
                    if 'text_overlay_result' in st.session_state and st.session_state.text_overlay_result:
                        st.markdown("**✨ Result with Text**")
                        st.image(st.session_state.text_overlay_result, use_column_width=True)
                        
                        if 'text_overlay_bytes' in st.session_state:
                            st.download_button(
                                "⬇️ Download Image with Text",
                                st.session_state.text_overlay_bytes,
                                f"Stencil_text_overlay_{int(time.time())}.png",
                                "image/png"
                            )
                            # Save to gallery button
                            render_save_to_db_button(st.session_state.text_overlay_bytes, "text_overlay")
                        
                        # Reset button
                        if st.button("🔄 Reset"):
                            del st.session_state.text_overlay_result
                            del st.session_state.text_overlay_bytes
                            st.rerun()
                    else:
                        st.info("👈 Configure text settings and click 'Add Text to Image' to see the result")
                        
                        # Feature info
                        st.markdown("**💡 Tips**")
                        st.markdown("""
                        <div class="info-box">
                        • Use larger font sizes for better visibility<br>
                        • Choose contrasting colors for readability<br>
                        • Try different positions to find the best placement<br>
                        • Custom position gives you pixel-perfect control
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("📤 Upload an image to start adding text overlays")
                
                # Feature showcase
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.markdown("""
                    <div class="feature-card">
                    <h4>✏️ Custom Text</h4>
                    <p>Add any text you want to your images</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_f2:
                    st.markdown("""
                    <div class="feature-card">
                    <h4>🎨 Full Control</h4>
                    <p>Customize size, color, and position</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_f3:
                    st.markdown("""
                    <div class="feature-card">
                    <h4>⚡ Instant Preview</h4>
                    <p>See results immediately</p>
                    </div>
                    """, unsafe_allow_html=True)

    # My Gallery Tab
    # My Gallery Tab
    with tabs[6]:
        # Check if user is logged in
        if not st.session_state.get("user"):
            st.warning("🔐 Please login to view your saved images.")
            st.info("Your gallery will automatically load once you sign in.")
        else:
            # Get image count
            image_count = len(st.session_state.get("gallery_images", []))
            
            # 1. Header Section
            # We use columns to separate the Title/Badge (Left) and Refresh Button (Right)
            col_header_left, col_header_right = st.columns([3, 1])
            
            with col_header_left:
                st.markdown(f"""
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                        <h2 style="
                            color: #d946ef;
                            font-size: 2.2rem;
                            font-weight: 800;
                            margin: 0;
                            padding: 0;
                            letter-spacing: -0.02em;
                            text-shadow: 0 0 30px rgba(217, 70, 239, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
                        ">My Gallery</h2>
                        <span style="background: rgba(30, 41, 59, 1); border: 1px solid rgba(168, 85, 247, 0.4); color: #e0d4fc; 
                                    padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; 
                                    font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem;
                                    box-shadow: 0 2px 8px rgba(168, 85, 247, 0.15);">
                            ☁️ {image_count} images
                        </span>
                    </div>
                    <p style="
                        color: #c4b5fd;
                        font-size: 0.95rem;
                        margin: 0.5rem 0 0 0;
                        font-weight: 400;
                    ">Your cloud-saved creations</p>
                </div>
                """, unsafe_allow_html=True)

            with col_header_right:
                # Align the button to the right/top visually
                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                if st.button("↻ Refresh", use_container_width=True):
                    st.session_state.gallery_loaded = False
                    load_gallery_images()
                    st.success("Refreshed")
                    st.rerun()

            # Load images if not loaded
            gallery_images = st.session_state.get("gallery_images", [])
            if not gallery_images and st.session_state.get("gallery_loaded"):
                load_gallery_images()
                gallery_images = st.session_state.get("gallery_images", [])

            # 2. Main Content Area
            if not gallery_images:
                # Empty State
                st.info("📭 Your gallery is empty. Start by generating or editing images and saving them to your gallery!")
                
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.markdown("""<div class="feature-card"><h4>🎨 Generate</h4><p>Create AI images</p></div>""", unsafe_allow_html=True)
                with col_f2:
                    st.markdown("""<div class="feature-card"><h4>✨ Edit</h4><p>Apply filters & save</p></div>""", unsafe_allow_html=True)
                with col_f3:
                    st.markdown("""<div class="feature-card"><h4>☁️ Cloud</h4><p>Accessible anywhere</p></div>""", unsafe_allow_html=True)
            
            else:
                # Image Grid
                cols_per_row = 4
                rows = [gallery_images[i:i + cols_per_row] for i in range(0, len(gallery_images), cols_per_row)]
                
                for row_idx, row in enumerate(rows):
                    cols = st.columns(cols_per_row)
                    for col_idx, file in enumerate(row):
                        with cols[col_idx]:
                            # Card Container Start
                            # We can't put buttons inside HTML div in Streamlit easily without component hacks.
                            # So we simulate the card visually.
                            
                            # 1. Image
                            st.image(file["url"], use_column_width=True)
                            
                            # 2. Filename (Caption)
                            filename = file.get("name", "image")
                            display_name = filename[:20] + "..." if len(filename) > 20 else filename
                            
                            st.markdown(f"""
                            <div style="margin-top: -0.5rem; margin-bottom: 0.5rem;">
                                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">{display_name}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 3. Action Button
                            is_project = file.get("source") == "project"
                            
                            if is_project:
                                if st.button("📌 Use", key=f"use_{row_idx}_{col_idx}", use_container_width=True):
                                    st.session_state.edited_image = file["url"]
                                    st.success("Loaded!")
                                    st.rerun()
                            else:
                                if st.button("🗑 Delete", key=f"del_{row_idx}_{col_idx}", use_container_width=True):
                                    result = delete_file(file["path"])
                                    if result["success"]:
                                        st.session_state.gallery_loaded = False
                                        st.rerun()
                                    else:
                                        st.error(result.get("message", "Error deleting"))

            # 3. Footer Banner
            st.markdown("""
            <div style="margin-top: 3rem; background: rgba(30, 41, 59, 0.5); border-radius: 8px; 
                        padding: 1rem; display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.2rem;">💡</span>
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
                    Images saved here are stored securely in the cloud and accessible from any device.
                </p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
