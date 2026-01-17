"""
Cloud Storage Service for Stencil.
Handles file upload/download using Supabase Storage.
"""
import os
import io
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import requests

load_dotenv()

# Storage bucket name
BUCKET_NAME = "user-files"

# Try to import Supabase - it may fail due to dependency conflicts
SUPABASE_AVAILABLE = False
_supabase_client = None

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"Supabase not available in storage_service: {e}")
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


def upload_image(image_bytes: bytes, filename: str = None, folder: str = "images") -> dict:
    """
    Upload an image to Supabase Storage.
    
    Args:
        image_bytes: The image data as bytes
        filename: Optional filename (auto-generated if not provided)
        folder: Folder within the bucket (default: 'images')
    
    Returns:
        dict with 'success', 'message', and optionally 'url' and 'path'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to upload files."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Storage not configured."}
        
        user_id = st.session_state["user"]["id"]
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
        
        # Create path: user_id/folder/filename
        file_path = f"{user_id}/{folder}/{filename}"
        
        # Upload to Supabase Storage
        response = client.storage.from_(BUCKET_NAME).upload(
            file_path,
            image_bytes,
            {"content-type": "image/png"}
        )
        
        # Get public URL
        public_url = client.storage.from_(BUCKET_NAME).get_public_url(file_path)
        
        return {
            "success": True,
            "message": "Image uploaded successfully!",
            "url": public_url,
            "path": file_path
        }
        
    except Exception as e:
        error_msg = str(e)
        if "Bucket not found" in error_msg:
            return {"success": False, "message": f"Storage bucket '{BUCKET_NAME}' not found. Please create it in Supabase dashboard."}
        if "already exists" in error_msg.lower():
            # File exists, return the URL anyway
            client = get_supabase_client()
            user_id = st.session_state["user"]["id"]
            file_path = f"{user_id}/{folder}/{filename}"
            public_url = client.storage.from_(BUCKET_NAME).get_public_url(file_path)
            return {
                "success": True,
                "message": "File already exists.",
                "url": public_url,
                "path": file_path
            }
        return {"success": False, "message": f"Upload error: {error_msg}"}


def download_image(file_path: str) -> dict:
    """
    Download an image from Supabase Storage.
    
    Args:
        file_path: The file path in storage
    
    Returns:
        dict with 'success', 'message', and optionally 'data' (bytes)
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to download files."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Storage not configured."}
        
        response = client.storage.from_(BUCKET_NAME).download(file_path)
        
        return {
            "success": True,
            "message": "Image downloaded!",
            "data": response
        }
        
    except Exception as e:
        return {"success": False, "message": f"Download error: {str(e)}"}


def download_image_from_url(url: str) -> bytes | None:
    """
    Download image from a URL and return as bytes.
    
    Args:
        url: The image URL
    
    Returns:
        Image bytes or None if failed
    """
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except Exception:
        return None


def list_user_files(folder: str = None) -> dict:
    """
    List all files for the current user.
    
    Args:
        folder: Optional folder to filter by
    
    Returns:
        dict with 'success', 'message', and 'files' list
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to view files.", "files": []}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Storage not configured. Please check Supabase credentials.", "files": []}
        
        user_id = st.session_state["user"]["id"]
        path = f"{user_id}/{folder}" if folder else user_id
        
        # Debug: List bucket root to see all folders
        try:
            bucket_root = client.storage.from_(BUCKET_NAME).list("")
            print(f"[DEBUG] Bucket root contents: {[item.get('name') for item in bucket_root]}")
        except Exception as bucket_error:
            print(f"[DEBUG] Error listing bucket root: {bucket_error}")
        
        # Debug: List user's root folder to see all subfolders
        try:
            user_root = client.storage.from_(BUCKET_NAME).list(user_id)
            print(f"[DEBUG] User root '{user_id}' contents: {[item.get('name') for item in user_root]}")
            for item in user_root:
                print(f"[DEBUG] User root item: {item}")
        except Exception as root_error:
            print(f"[DEBUG] Error listing user root: {root_error}")
        
        # Try listing the target path
        try:
            response = client.storage.from_(BUCKET_NAME).list(path)
            print(f"[DEBUG] Target path '{path}' response: {response}")
        except Exception as list_error:
            return {"success": False, "message": f"Error accessing storage: {str(list_error)}", "files": []}
        
        files = []
        print(f"[DEBUG] list_user_files: Checking path '{path}', found {len(response)} items")
        
        for item in response:
            item_name = item.get("name", "")
            
            # Skip if no name
            if not item_name:
                print(f"[DEBUG] Skipping item with no name: {item}")
                continue
            
            # Skip hidden placeholder files (like .emptyFolderPlaceholder)
            if item_name.startswith("."):
                print(f"[DEBUG] Skipping hidden file: {item_name}")
                continue
            
            # Check if it's an image file by extension
            lower_name = item_name.lower()
            if not any(lower_name.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']):
                print(f"[DEBUG] Skipping non-image file: {item_name}")
                continue
            
            print(f"[DEBUG] Found valid image: {item_name} (id={item.get('id')}, metadata={item.get('metadata')})")
            
            file_path = f"{path}/{item_name}"
            try:
                public_url = client.storage.from_(BUCKET_NAME).get_public_url(file_path)
            except:
                public_url = None
            
            if public_url:
                files.append({
                    "name": item_name,
                    "path": file_path,
                    "url": public_url,
                    "created_at": item.get("created_at"),
                    "size": item.get("metadata", {}).get("size", 0) if item.get("metadata") else 0
                })
        
        return {
            "success": True,
            "message": f"Found {len(files)} files.",
            "files": files
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error listing files: {str(e)}", "files": []}


def delete_file(file_path: str) -> dict:
    """
    Delete a file from storage.
    
    Args:
        file_path: The file path to delete
    
    Returns:
        dict with 'success' and 'message'
    """
    try:
        if not st.session_state.get("user"):
            return {"success": False, "message": "Please login to delete files."}
        
        client = get_supabase_client()
        if not client:
            return {"success": False, "message": "Storage not configured."}
        
        client.storage.from_(BUCKET_NAME).remove([file_path])
        return {"success": True, "message": "File deleted."}
        
    except Exception as e:
        return {"success": False, "message": f"Delete error: {str(e)}"}


def get_storage_usage() -> dict:
    """
    Get storage usage for the current user.
    
    Returns:
        dict with 'success', 'total_files', and 'total_size'
    """
    try:
        result = list_user_files()
        if not result["success"]:
            return {"success": False, "total_files": 0, "total_size": 0}
        
        total_size = sum(f.get("size", 0) for f in result["files"])
        
        return {
            "success": True,
            "total_files": len(result["files"]),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception:
        return {"success": False, "total_files": 0, "total_size": 0}
