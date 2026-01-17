"""
Project Management Service for Stencil.
Handles saving, loading, and managing user projects.
"""
import os
import json
from datetime import datetime
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
    print(f"Supabase not available in project_service: {e}")
    Client = None

def get_supabase_client():
    """Get or create Supabase client with authenticated session."""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        return None
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return None
    
    try:
        # Always create client
        if _supabase_client is None:
            _supabase_client = create_client(url, key)
        
        # If user is authenticated, set the session
        if st.session_state.get("supabase_session"):
            session = st.session_state["supabase_session"]
            access_token = session.get("access_token")
            refresh_token = session.get("refresh_token")
            if access_token and refresh_token:
                try:
                    # Set the session on the client so RLS works
                    _supabase_client.auth.set_session(access_token, refresh_token)
                except Exception as e:
                    print(f"Error setting session: {e}")
        
        return _supabase_client
    except Exception:
        return None


def save_project(name: str, data: dict, thumbnail_url: str = None) -> dict:
    """
    Save a project to the database.
    
    Args:
        name: Project name
        data: Project data (settings, history, current state)
        thumbnail_url: Optional thumbnail URL
    
    Returns:
        dict with 'success', 'message', and optionally 'project_id'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to save projects."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured."}
        
        user_id = st.session_state["user"]["id"]
        
        project_data = {
            "user_id": user_id,
            "name": name,
            "data": json.dumps(data),
            "thumbnail_url": thumbnail_url,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("projects").insert(project_data).execute()
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "message": f"Project '{name}' saved!",
                "project_id": response.data[0]["id"]
            }
        return {"success": False, "message": "Failed to save project."}
        
    except Exception as e:
        return {"success": False, "message": f"Error saving project: {str(e)}"}


def update_project(project_id: str, name: str = None, data: dict = None, thumbnail_url: str = None) -> dict:
    """
    Update an existing project.
    
    Args:
        project_id: The project's ID
        name: New project name (optional)
        data: New project data (optional)
        thumbnail_url: New thumbnail URL (optional)
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to update projects."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured."}
        
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        if name:
            update_data["name"] = name
        if data:
            update_data["data"] = json.dumps(data)
        if thumbnail_url:
            update_data["thumbnail_url"] = thumbnail_url
        
        client.table("projects").update(update_data).eq("id", project_id).execute()
        return {"success": True, "message": "Project updated!"}
        
    except Exception as e:
        return {"success": False, "message": f"Error updating project: {str(e)}"}


def load_project(project_id: str) -> dict:
    """
    Load a project from the database.
    
    Args:
        project_id: The project's ID
    
    Returns:
        dict with 'success', 'message', and optionally 'project' data
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to load projects."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured."}
        
        response = client.table("projects").select("*").eq("id", project_id).execute()
        
        if response.data and len(response.data) > 0:
            project = response.data[0]
            # Parse JSON data
            project["data"] = json.loads(project["data"]) if isinstance(project["data"], str) else project["data"]
            return {
                "success": True,
                "message": "Project loaded!",
                "project": project
            }
        return {"success": False, "message": "Project not found."}
        
    except Exception as e:
        return {"success": False, "message": f"Error loading project: {str(e)}"}


def list_projects() -> dict:
    """
    List all projects for the current user.
    
    Returns:
        dict with 'success', 'message', and 'projects' list
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to view projects.", "projects": []}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured.", "projects": []}
        
        user_id = st.session_state["user"]["id"]
        
        response = client.table("projects").select(
            "id, name, thumbnail_url, created_at, updated_at"
        ).eq("user_id", user_id).order("updated_at", desc=True).execute()
        
        return {
            "success": True,
            "message": f"Found {len(response.data)} projects.",
            "projects": response.data or []
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error listing projects: {str(e)}", "projects": []}


def delete_project(project_id: str) -> dict:
    """
    Delete a project.
    
    Args:
        project_id: The project's ID
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to delete projects."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured."}
        
        client.table("projects").delete().eq("id", project_id).execute()
        return {"success": True, "message": "Project deleted."}
        
    except Exception as e:
        return {"success": False, "message": f"Error deleting project: {str(e)}"}


def get_project_state() -> dict:
    """
    Get current app state that should be saved in a project.
    
    Returns:
        dict with all saveable state
    """
    state = {}
    
    # Save relevant session state
    saveable_keys = [
        "current_image_url",
        "generated_images",
        "image_history",
        "generation_count",
        "current_prompt",
        "enhanced_prompt",
        "selected_style",
        "selected_aspect_ratio",
        "seed",
        "refinement_steps",
        "guidance_scale"
    ]
    
    for key in saveable_keys:
        if key in st.session_state:
            value = st.session_state[key]
            # Skip non-serializable objects
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                state[key] = value
    
    return state


def restore_project_state(project_data: dict) -> None:
    """
    Restore app state from a project.
    
    Args:
        project_data: The project's data dict
    """
    for key, value in project_data.items():
        st.session_state[key] = value


def auto_save_project() -> None:
    """Auto-save current state if auto_save is enabled and user is logged in."""
    if not st.session_state.get("user"):
        return
    
    if not st.session_state.get("auto_save_enabled", True):
        return
    
    # Check if we have an active project
    current_project_id = st.session_state.get("current_project_id")
    
    if current_project_id:
        state = get_project_state()
        update_project(current_project_id, data=state)


def get_all_project_images() -> dict:
    """
    Get all images from all projects for the current user.
    Extracts images from image_history and generated_images fields.
    
    Returns:
        dict with 'success', 'message', and 'images' list
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to view images.", "images": []}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Database not configured.", "images": []}
        
        user_id = st.session_state["user"]["id"]
        
        # Get all projects with their data
        response = client.table("projects").select(
            "id, name, data, created_at"
        ).eq("user_id", user_id).execute()
        
        images = []
        
        for project in response.data or []:
            project_name = project.get("name", "Unknown")
            project_id = project.get("id")
            created_at = project.get("created_at", "")
            
            # Parse the data field
            data = project.get("data")
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    continue
            
            if not isinstance(data, dict):
                continue
            
            # Extract from image_history
            image_history = data.get("image_history", [])
            for item in image_history:
                if isinstance(item, dict):
                    url = item.get("url")
                    if url:
                        images.append({
                            "name": f"{project_name} - {item.get('type', 'image')}",
                            "url": url,
                            "path": f"project/{project_id}",
                            "created_at": item.get("timestamp", created_at),
                            "source": "project",
                            "project_name": project_name
                        })
                elif isinstance(item, str) and item.startswith("http"):
                    images.append({
                        "name": f"{project_name} - image",
                        "url": item,
                        "path": f"project/{project_id}",
                        "created_at": created_at,
                        "source": "project",
                        "project_name": project_name
                    })
            
            # Extract from generated_images
            generated_images = data.get("generated_images", [])
            for idx, url in enumerate(generated_images):
                if isinstance(url, str) and url.startswith("http"):
                    images.append({
                        "name": f"{project_name} - generated_{idx+1}",
                        "url": url,
                        "path": f"project/{project_id}",
                        "created_at": created_at,
                        "source": "project",
                        "project_name": project_name
                    })
            
            # Extract current_image_url if exists
            current_url = data.get("current_image_url")
            if current_url and isinstance(current_url, str) and current_url.startswith("http"):
                images.append({
                    "name": f"{project_name} - current",
                    "url": current_url,
                    "path": f"project/{project_id}",
                    "created_at": created_at,
                    "source": "project",
                    "project_name": project_name
                })
        
        return {
            "success": True,
            "message": f"Found {len(images)} images from projects.",
            "images": images
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error fetching project images: {str(e)}", "images": []}
