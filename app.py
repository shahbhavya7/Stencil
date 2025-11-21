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
    erase_foreground
)
from PIL import Image, ImageFilter, ImageEnhance
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

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-color: #0f172a;
        --card-background: #1e293b;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Main content area background */
    .main .block-container {
        background: transparent;
        padding-top: 2rem;
    }
    
    /* Top header area */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Toolbar area */
    .stApp > header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Ensure all backgrounds match */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stHeader"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 41, 59, 0.5);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        background-color: transparent;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Success message */
    .success-box {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Image preview */
    .image-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .image-container:hover {
        transform: scale(1.02);
    }
    
    /* Sidebar styling - Multiple selectors for compatibility */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Sidebar content styling */
    [data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Sidebar text input */
    [data-testid="stSidebar"] input {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar metrics */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #6366f1 !important;
        font-weight: bold;
    }
    
    /* Sidebar expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: white !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        border-color: #6366f1;
    }
    
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border-color: rgba(99, 102, 241, 0.3);
        margin: 1.5rem 0;
    }
    
    /* Sidebar markdown */
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Sidebar info/warning/success boxes */
    [data-testid="stSidebar"] .stAlert {
        background-color: rgba(30, 41, 59, 0.8);
        border-radius: 8px;
    }
    
    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Feature cards */
    .feature-card {
        background: rgba(30, 41, 59, 0.6);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #6366f1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
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

def main():
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Stencil</h1>
        <p>Professional AI-Powered Image Generation & Editing Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # API Key input with validation
        api_key = st.text_input(
            "🔑 API Key:", 
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
        
        # Statistics
        st.markdown("### 📊 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Generated", st.session_state.generation_count)
        with col2:
            st.metric("In History", len(st.session_state.image_history))
        
        st.markdown("---")
        
        # Image History
        if st.session_state.image_history:
            st.markdown("### 📜 Recent History")
            for idx, item in enumerate(reversed(st.session_state.image_history[-5:])):
                with st.expander(f"🖼️ {item['type']} - {item['timestamp'][:16]}"):
                    if item['prompt']:
                        st.caption(f"Prompt: {item['prompt'][:50]}...")
                    if st.button("Load", key=f"load_history_{idx}"):
                        st.session_state.edited_image = item['url']
                        st.rerun()
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Clear History"):
            st.session_state.image_history = []
            st.session_state.generation_count = 0
            st.success("History cleared!")
        
        if st.button("🗑️ Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # Info
        st.markdown("### ℹ️ About")
        st.info(
            "Stencil is a professional AI-powered image editing platform "
            "that helps you create stunning visuals for your products and marketing needs."
        )

    # Main tabs
    tabs = st.tabs([
        "🎨 Generate Image",
        "🖼️ Lifestyle Shot",
        "✨ Generative Fill",
        "🧹 Erase Elements",
        "🎭 Image Filters"
    ])
    
    # Generate Images Tab
    with tabs[0]:
        st.markdown("### 🎨 AI Image Generation")
        st.markdown("Create stunning images from text descriptions using advanced AI models.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            
            # Prompt input
            prompt = st.text_area(
                "📝 Describe your vision", 
                value="",
                height=350,
                key="prompt_input",
                placeholder="e.g., A sleek modern smartphone on a wooden desk with natural lighting..."
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
    
    # Product Photography Tab
    with tabs[1]:
        st.header("Product Photography")
        
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
                elif st.session_state.pending_urls:
                    st.info("🔄 Images are being generated. Click the refresh button above to check if they're ready.")
                else:
                    st.info("👆 Upload an image above and select an editing option to get started!")

    # Generative Fill Tab
    with tabs[2]:
        st.header("🎨 Generative Fill")
        st.markdown("Draw a mask on the image and describe what you want to generate in that area.")
        
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
                elif st.session_state.pending_urls:
                    st.info("Generation in progress. Click the refresh button above to check status.")

    # Erase Elements Tab
    with tabs[3]:
        st.header("🎨 Erase Elements")
        st.markdown("Upload an image and select the area you want to erase.")
        
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
                else:
                    st.info("👆 Draw on the image above and click 'Erase Selected Area' to remove elements.")
    
    # Image Filters Tab
    with tabs[4]:
        st.markdown("### 🎭 Image Filters & Enhancement")
        st.markdown("Apply professional filters and enhancements to your images.")
        
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
                                import base64
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

if __name__ == "__main__":
    main() 
