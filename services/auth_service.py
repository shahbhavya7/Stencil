"""
Supabase Authentication Service for Stencil.
Handles user registration, login, logout, and session management.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try to import Supabase - it may fail due to dependency conflicts
SUPABASE_AVAILABLE = False
_supabase_client = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"Supabase not available: {e}")
    print("Running in guest-only mode. Install compatible supabase version to enable auth.")
    Client = None

def get_supabase_client():
    """Get or create Supabase client."""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        return None
    
    if _supabase_client is not None:
        return _supabase_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return None
    
    try:
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"Failed to create Supabase client: {e}")
        return None


def sign_up(email: str, password: str, name: str = "") -> dict:
    """
    Register a new user.
    
    Args:
        email: User's email address
        password: User's password (min 6 characters)
        name: User's display name (optional)
    
    Returns:
        dict with 'success', 'message', and optionally 'user' data
    """
    try:
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Supabase not configured. Check SUPABASE_URL and SUPABASE_KEY in .env"}
        
        # Include user metadata with name
        options = {
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": name if name else email.split("@")[0]
                }
            }
        }
        
        response = client.auth.sign_up(options)
        
        if response.user:
            return {
                "success": True,
                "message": "Account created! Please check your email to confirm.",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": name if name else email.split("@")[0]
                }
            }
        else:
            return {"success": False, "message": "Registration failed. Please try again."}
            
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return {"success": False, "message": "This email is already registered. Please login instead."}
        return {"success": False, "message": f"Registration error: {error_msg}"}


def sign_in(email: str, password: str) -> dict:
    """
    Login an existing user.
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        dict with 'success', 'message', and optionally 'user' and 'session' data
    """
    try:
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Supabase not configured. Check SUPABASE_URL and SUPABASE_KEY in .env"}
        
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            # Extract display name from user metadata
            user_metadata = response.user.user_metadata or {}
            display_name = user_metadata.get("display_name", email.split("@")[0])
            
            # Store session in Streamlit session state
            st.session_state["supabase_session"] = {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": display_name
                }
            }
            st.session_state["user"] = {
                "id": response.user.id,
                "email": response.user.email,
                "name": display_name
            }
            st.session_state["is_authenticated"] = True
            
            return {
                "success": True,
                "message": "Login successful!",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": display_name
                }
            }
        else:
            return {"success": False, "message": "Login failed. Please check your credentials."}
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {"success": False, "message": "Invalid email or password."}
        if "Email not confirmed" in error_msg:
            return {"success": False, "message": "Please confirm your email before logging in."}
        return {"success": False, "message": f"Login error: {error_msg}"}


def sign_out() -> dict:
    """
    Logout the current user.
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        client = get_supabase_client()
        if client:
            client.auth.sign_out()
        
        # Clear session state
        if "supabase_session" in st.session_state:
            del st.session_state["supabase_session"]
        if "user" in st.session_state:
            del st.session_state["user"]
        st.session_state["is_authenticated"] = False
        
        return {"success": True, "message": "Logged out successfully."}
        
    except Exception as e:
        return {"success": False, "message": f"Logout error: {str(e)}"}


def get_current_user() -> dict | None:
    """
    Get the currently logged-in user.
    
    Returns:
        User dict with 'id' and 'email', or None if not logged in
    """
    if st.session_state.get("is_authenticated") and st.session_state.get("user"):
        return st.session_state["user"]
    return None


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.get("is_authenticated", False)


def get_user_preferences(user_id: str) -> dict:
    """
    Get user preferences from database.
    
    Args:
        user_id: The user's ID
    
    Returns:
        dict with user preferences or default values
    """
    try:
        client = get_supabase_client()
        if not client:
            return get_default_preferences()
        
        response = client.table("user_preferences").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return get_default_preferences()
        
    except Exception:
        return get_default_preferences()


def save_user_preferences(user_id: str, preferences: dict) -> dict:
    """
    Save user preferences to database.
    
    Args:
        user_id: The user's ID
        preferences: dict with preference values
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Supabase not configured"}
        
        # Upsert preferences
        data = {
            "user_id": user_id,
            **preferences
        }
        
        client.table("user_preferences").upsert(data).execute()
        return {"success": True, "message": "Preferences saved!"}
        
    except Exception as e:
        return {"success": False, "message": f"Error saving preferences: {str(e)}"}


def get_default_preferences() -> dict:
    """Get default user preferences."""
    return {
        "default_style": "Realistic",
        "default_aspect_ratio": "1:1",
        "theme": "dark",
        "auto_save": True
    }


def send_password_reset(email: str) -> dict:
    """
    Send password reset email.
    
    Args:
        email: User's email address
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Supabase not configured"}
        
        client.auth.reset_password_email(email)
        return {"success": True, "message": "Password reset email sent! Check your inbox."}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def restore_session(access_token: str, refresh_token: str) -> dict:
    """
    Restore a session using stored tokens.
    
    Args:
        access_token: The access token
        refresh_token: The refresh token
        
    Returns:
        dict with success status and user data if successful
    """
    try:
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Supabase not configured"}
            
        # Attempt to set the session with the tokens
        response = client.auth.set_session(access_token, refresh_token)
        
        if response.user and response.session:
            # Extract display name
            user_metadata = response.user.user_metadata or {}
            display_name = user_metadata.get("display_name", response.user.email.split("@")[0])
            
            # Update session state
            st.session_state["supabase_session"] = {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": display_name
                }
            }
            st.session_state["user"] = {
                "id": response.user.id,
                "email": response.user.email,
                "name": display_name
            }
            st.session_state["is_authenticated"] = True
            
            return {
                "success": True, 
                "message": "Session restored",
                "user": st.session_state["user"],
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            }
            
        return {"success": False, "message": "Could not restore session"}
        
    except Exception as e:
        return {"success": False, "message": f"Session restoration error: {str(e)}"}
