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
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 3rem; margin-bottom: 0.5rem;">🎨 Stencil</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">Professional AI-Powered Image Editor</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the auth form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.8); padding: 2rem; border-radius: 16px; 
                    border: 1px solid rgba(99, 102, 241, 0.3);">
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Continue as guest option
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue as Guest →", use_container_width=True, type="secondary"):
            st.session_state["guest_mode"] = True
            st.rerun()


def render_login_form():
    """Render the login form."""
    with st.form("login_form", clear_on_submit=False):
        st.markdown("### Welcome Back!")
        
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember me", value=True)
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?", type="secondary")
        
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
        
        if forgot_password and email:
            result = send_password_reset(email)
            if result["success"]:
                st.info(result["message"])
            else:
                st.error(result["message"])


def render_register_form():
    """Render the registration form."""
    with st.form("register_form", clear_on_submit=False):
        st.markdown("### Create Account")
        
        email = st.text_input("📧 Email", placeholder="your@email.com", key="reg_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters", key="reg_pass")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
        
        agree_terms = st.checkbox("I agree to the Terms of Service")
        
        submitted = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service.")
            else:
                with st.spinner("Creating account..."):
                    result = sign_up(email, password)
                    if result["success"]:
                        st.success(result["message"])
                        st.info("You can now login with your credentials.")
                    else:
                        st.error(result["message"])


def render_user_sidebar():
    """Render user info and actions in sidebar."""
    user = get_current_user()
    
    if user:
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 1rem; border-radius: 12px; 
                    border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 1rem;">
        """, unsafe_allow_html=True)
        
        st.markdown(f"**👤 {user['email'][:20]}{'...' if len(user['email']) > 20 else ''}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚙️ Settings", use_container_width=True, key="user_settings"):
                st.session_state["show_settings"] = True
        with col2:
            if st.button("🚪 Logout", use_container_width=True, key="user_logout"):
                sign_out()
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Guest mode indicator
        if st.session_state.get("guest_mode"):
            st.markdown("""
            <div style="background: rgba(251, 191, 36, 0.1); padding: 0.75rem; border-radius: 8px; 
                        border: 1px solid rgba(251, 191, 36, 0.3); margin-bottom: 1rem; text-align: center;">
                <span style="color: #fbbf24;">👤 Guest Mode</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔐 Login to Save", use_container_width=True):
                st.session_state["guest_mode"] = False
                st.rerun()


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
