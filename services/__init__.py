from .lifestyle_shot import lifestyle_shot_by_text, lifestyle_shot_by_image
from .shadow import add_shadow
from .packshot import create_packshot
from .prompt_enhancement import enhance_prompt
from .generative_fill import generative_fill
from .hd_image_generation import generate_hd_image
from .erase_foreground import erase_foreground

# Auth and project management
from .auth_service import (
    sign_up, sign_in, sign_out,
    get_current_user, is_authenticated,
    get_user_preferences, save_user_preferences,
    send_password_reset, get_supabase_client
)
from .project_service import (
    save_project, update_project, load_project,
    list_projects, delete_project,
    get_project_state, restore_project_state, auto_save_project
)
from .storage_service import (
    upload_image, download_image, download_image_from_url,
    list_user_files, delete_file, get_storage_usage
)

__all__ = [
    'lifestyle_shot_by_text',
    'lifestyle_shot_by_image',
    'add_shadow',
    'create_packshot',
    'enhance_prompt',
    'generative_fill',
    'generate_hd_image',
    'erase_foreground',
    # Auth services
    'sign_up', 'sign_in', 'sign_out',
    'get_current_user', 'is_authenticated',
    'get_user_preferences', 'save_user_preferences',
    'send_password_reset', 'get_supabase_client',
    # Project services
    'save_project', 'update_project', 'load_project',
    'list_projects', 'delete_project',
    'get_project_state', 'restore_project_state', 'auto_save_project',
    # Storage services
    'upload_image', 'download_image', 'download_image_from_url',
    'list_user_files', 'delete_file', 'get_storage_usage'
]
 