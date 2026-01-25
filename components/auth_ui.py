"""
Authentication UI Components for Stencil.
Provides login, registration, and user profile UI elements.
"""
import streamlit as st
from services.auth_service import (
    sign_up, sign_in, sign_out, 
    get_current_user, is_authenticated,
    get_user_preferences, save_user_preferences,
    send_password_reset
)


def render_auth_page():
    """Render the full authentication page (login/register)."""
    # Logo and branding with solid bright colors for guaranteed visibility
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem 0 1.5rem 0;">
        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="font-size: 3.5rem; filter: drop-shadow(0 4px 25px rgba(167, 139, 250, 0.8));">🎨</span>
            <h1 style="color: #e0e7ff;
                       font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;
                       text-shadow: 0 0 30px rgba(167, 139, 250, 0.8), 0 0 60px rgba(139, 92, 246, 0.5), 0 2px 4px rgba(0,0,0,0.3);">Stencil</h1>
        </div>
        <p style="color: #c7d2fe; font-size: 1.15rem; font-weight: 400; margin: 0; opacity: 0.95;">
            Professional AI-Powered Image Editor
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the auth form with better proportions
    col1, col2, col3 = st.columns([1.2, 2, 1.2])
    
    with col2:
        # Auth card container
        st.markdown("""
        <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); 
                    padding: 0; border-radius: 20px; 
                    border: 1px solid rgba(99, 102, 241, 0.25);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 60px rgba(99, 102, 241, 0.1);
                    overflow: hidden;">
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Continue as guest option with better styling
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Continue as Guest →", use_container_width=True, type="secondary", key="guest_btn"):
            st.session_state["guest_mode"] = True
            st.rerun()


def render_login_form():
    """Render the login form."""
    # Form container with padding
    st.markdown("<div style='padding: 1.5rem 1.5rem 1rem 1.5rem;'>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <h3 style="color: #f1f5f9; font-size: 1.5rem; font-weight: 600; margin: 0 0 1.25rem 0;">
            Welcome Back!
        </h3>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        # Remember me checkbox only - forgot password moved outside
        remember_me = st.checkbox("Remember me", value=True)
        
        # Spacer
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Logging in..."):
                    result = sign_in(email, password)
                    if result["success"]:
                        st.success(result["message"])
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(result["message"])
    
    # Forgot password link OUTSIDE the form, positioned nicely
    st.markdown("""
    <div style="text-align: center; margin-top: 0.75rem;">
        <a href="#" onclick="return false;" style="color: #818cf8; font-size: 0.875rem; 
           text-decoration: none; transition: color 0.2s ease;"
           onmouseover="this.style.color='#a5b4fc'" 
           onmouseout="this.style.color='#818cf8'">
            Forgot Password?
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)


def render_register_form():
    """Render the registration form."""
    # Form container with padding
    st.markdown("<div style='padding: 1.5rem 1.5rem 1rem 1.5rem;'>", unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=False):
        st.markdown("""
        <h3 style="color: #f1f5f9; font-size: 1.5rem; font-weight: 600; margin: 0 0 1.25rem 0;">
            Create Account
        </h3>
        """, unsafe_allow_html=True)
        
        # Add name field for new users
        name = st.text_input("👤 Your Name", placeholder="How should we call you?", key="reg_name")
        email = st.text_input("📧 Email", placeholder="your@email.com", key="reg_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters", key="reg_pass")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
        
        # Spacer
        st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
        
        agree_terms = st.checkbox("I agree to the Terms of Service")
        
        # Spacer
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service.")
            else:
                with st.spinner("Creating account..."):
                    result = sign_up(email, password, name)
                    if result["success"]:
                        st.success(result["message"])
                        st.info("You can now login with your credentials.")
                    else:
                        st.error(result["message"])
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)


def render_user_sidebar():
    """Render user info and actions in sidebar."""
    user = get_current_user()
    
    if user:
        # Get display name - use name if available, otherwise derive from email
        display_name = user.get('name', user['email'].split('@')[0])
        
        # Modern minimal greeting
        st.markdown(f"""
        <p style="color: #64748b; font-size: 0.75rem; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Welcome back</p>
        <p style="color: #f1f5f9; font-size: 1.25rem; font-weight: 600; margin: 0 0 0.75rem 0;">
            👋 Hi, {display_name}!
        </p>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, key="user_logout"):
            sign_out()
            st.rerun()
        
        st.markdown("---")
    else:
        # Guest mode indicator - minimal style
        if st.session_state.get("guest_mode"):
            st.markdown("""
            <p style="color: #fbbf24; font-size: 0.9rem; font-weight: 500; margin: 0 0 0.5rem 0;">
                👤 Guest Mode
            </p>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 Login to Save", use_container_width=True):
                st.session_state["guest_mode"] = False
                st.rerun()
            
            st.markdown("---")


def render_settings_modal():
    """Render user settings modal/dialog."""
    if not st.session_state.get("show_settings"):
        return
    
    user = get_current_user()
    if not user:
        st.session_state["show_settings"] = False
        return
    
    with st.expander("⚙️ User Settings", expanded=True):
        # Load current preferences
        prefs = get_user_preferences(user["id"])
        
        st.markdown("### Preferences")
        
        default_style = st.selectbox(
            "Default Style",
            ["Realistic", "Artistic", "Cartoon", "Sketch", "Watercolor", "Oil Painting", "Digital Art", "3D Render"],
            index=["Realistic", "Artistic", "Cartoon", "Sketch", "Watercolor", "Oil Painting", "Digital Art", "3D Render"].index(prefs.get("default_style", "Realistic"))
        )
        
        default_ratio = st.selectbox(
            "Default Aspect Ratio",
            ["1:1", "16:9", "9:16", "4:3", "3:4"],
            index=["1:1", "16:9", "9:16", "4:3", "3:4"].index(prefs.get("default_aspect_ratio", "1:1"))
        )
        
        auto_save = st.checkbox("Enable Auto-Save", value=prefs.get("auto_save", True))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Settings", use_container_width=True, type="primary"):
                new_prefs = {
                    "default_style": default_style,
                    "default_aspect_ratio": default_ratio,
                    "auto_save": auto_save
                }
                result = save_user_preferences(user["id"], new_prefs)
                if result["success"]:
                    st.success("Settings saved!")
                    st.session_state["show_settings"] = False
                    st.rerun()
                else:
                    st.error(result["message"])
        
        with col2:
            if st.button("❌ Close", use_container_width=True):
                st.session_state["show_settings"] = False
                st.rerun()


def check_authentication() -> bool:
    """
    Check if user is authenticated or in guest mode.
    
    Returns:
        True if user can access the app, False if should show login
    """
    if is_authenticated():
        return True
    if st.session_state.get("guest_mode"):
        return True
    return False
