"""
Project Management UI Components for Stencil.
Provides project save, load, and management UI elements.
"""
import streamlit as st
from datetime import datetime
from services.project_service import (
    save_project, load_project, list_projects, 
    delete_project, get_project_state, restore_project_state
)
from services.storage_service import (
    upload_image, list_user_files, download_image_from_url, get_storage_usage
)
from services.auth_service import is_authenticated


def render_project_sidebar():
    """Render project management section in sidebar."""
    if not is_authenticated():
        return
    
    st.markdown("---")
    st.markdown("### 📁 Projects")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save", use_container_width=True, key="save_project_btn"):
            st.session_state["show_save_dialog"] = True
    
    with col2:
        if st.button("📂 Load", use_container_width=True, key="load_project_btn"):
            st.session_state["show_load_dialog"] = True
    
    # Show current project name if any
    if st.session_state.get("current_project_name"):
        st.markdown(f"""
        <div style="background: rgba(34, 197, 94, 0.1); padding: 0.5rem; border-radius: 8px; 
                    border: 1px solid rgba(34, 197, 94, 0.3); margin-top: 0.5rem; text-align: center;">
            <small style="color: #22c55e;">📄 {st.session_state['current_project_name']}</small>
        </div>
        """, unsafe_allow_html=True)


def render_save_dialog():
    """Render save project dialog."""
    if not st.session_state.get("show_save_dialog"):
        return
    
    st.markdown("### 💾 Save Project")
    
    with st.form("save_project_form"):
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.get("current_project_name", ""),
            placeholder="Enter a name for your project"
        )
        
        save_to_cloud = st.checkbox("Also save images to cloud storage", value=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Project", use_container_width=True, type="primary"):
                if not project_name:
                    st.error("Please enter a project name.")
                else:
                    with st.spinner("Saving project..."):
                        # Get current state
                        state = get_project_state()
                        
                        # Optionally upload current image to cloud
                        thumbnail_url = None
                        if save_to_cloud and st.session_state.get("current_image_url"):
                            image_bytes = download_image_from_url(st.session_state["current_image_url"])
                            if image_bytes:
                                upload_result = upload_image(image_bytes, f"{project_name}_thumb.png", "thumbnails")
                                if upload_result["success"]:
                                    thumbnail_url = upload_result.get("url")
                        
                        # Save project
                        result = save_project(project_name, state, thumbnail_url)
                        
                        if result["success"]:
                            st.success(result["message"])
                            st.session_state["current_project_name"] = project_name
                            st.session_state["current_project_id"] = result.get("project_id")
                            st.session_state["show_save_dialog"] = False
                            st.rerun()
                        else:
                            st.error(result["message"])
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state["show_save_dialog"] = False
                st.rerun()


def render_load_dialog():
    """Render load project dialog."""
    if not st.session_state.get("show_load_dialog"):
        return
    
    st.markdown("### 📂 Load Project")
    
    # Fetch projects
    result = list_projects()
    
    if not result["success"]:
        st.error(result["message"])
        if st.button("Close", key="close_load_error"):
            st.session_state["show_load_dialog"] = False
            st.rerun()
        return
    
    projects = result["projects"]
    
    if not projects:
        st.info("No saved projects yet. Save your first project!")
        if st.button("Close", key="close_load_empty"):
            st.session_state["show_load_dialog"] = False
            st.rerun()
        return
    
    # Display projects as cards
    for project in projects:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**📄 {project['name']}**")
                updated = project.get('updated_at', '')[:10] if project.get('updated_at') else 'Unknown'
                st.caption(f"Updated: {updated}")
            
            with col2:
                if st.button("📂 Load", key=f"load_{project['id']}", use_container_width=True):
                    with st.spinner("Loading..."):
                        load_result = load_project(project['id'])
                        if load_result["success"]:
                            restore_project_state(load_result["project"]["data"])
                            st.session_state["current_project_name"] = project["name"]
                            st.session_state["current_project_id"] = project["id"]
                            st.session_state["show_load_dialog"] = False
                            st.success(f"Loaded: {project['name']}")
                            st.rerun()
                        else:
                            st.error(load_result["message"])
            
            with col3:
                if st.button("🗑️", key=f"delete_{project['id']}", help="Delete project"):
                    delete_result = delete_project(project['id'])
                    if delete_result["success"]:
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error(delete_result["message"])
            
            st.markdown("---")
    
    if st.button("❌ Close", use_container_width=True, key="close_load_dialog"):
        st.session_state["show_load_dialog"] = False
        st.rerun()


def render_cloud_storage_section():
    """Render cloud storage section in sidebar."""
    if not is_authenticated():
        return
    
    with st.expander("☁️ Cloud Storage"):
        # Get usage stats
        usage = get_storage_usage()
        
        if usage["success"]:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Files", usage["total_files"])
            with col2:
                st.metric("Size", f"{usage['total_size_mb']} MB")
        
        # Upload current image
        if st.session_state.get("current_image_url"):
            if st.button("☁️ Save Current Image to Cloud", use_container_width=True):
                with st.spinner("Uploading..."):
                    image_bytes = download_image_from_url(st.session_state["current_image_url"])
                    if image_bytes:
                        result = upload_image(image_bytes)
                        if result["success"]:
                            st.success("Image saved to cloud!")
                        else:
                            st.error(result["message"])
                    else:
                        st.error("Could not download image.")
        
        # View cloud files
        if st.button("📁 View Cloud Files", use_container_width=True):
            st.session_state["show_cloud_files"] = not st.session_state.get("show_cloud_files", False)
            st.rerun()


def render_cloud_files_modal():
    """Render cloud files viewer."""
    if not st.session_state.get("show_cloud_files"):
        return
    
    st.markdown("### ☁️ Cloud Files")
    
    result = list_user_files("images")
    
    if not result["success"]:
        st.error(result["message"])
        return
    
    files = result["files"]
    
    if not files:
        st.info("No files uploaded yet.")
    else:
        # Display in grid
        cols = st.columns(3)
        for i, file in enumerate(files):
            with cols[i % 3]:
                st.image(file["url"], caption=file["name"][:20], use_container_width=True)
                if st.button("Use", key=f"use_cloud_{i}", use_container_width=True):
                    st.session_state["current_image_url"] = file["url"]
                    st.session_state["show_cloud_files"] = False
                    st.rerun()
    
    if st.button("❌ Close", use_container_width=True, key="close_cloud"):
        st.session_state["show_cloud_files"] = False
        st.rerun()
