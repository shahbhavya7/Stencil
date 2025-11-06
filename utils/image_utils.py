"""
Utility functions for AdSnap Studio
Common helper functions for image processing and API interactions
"""

import io
import base64
from PIL import Image
import requests
from typing import Optional, Union, Tuple


def image_to_bytes(image: Union[Image.Image, str], format: str = 'PNG') -> bytes:
    """
    Convert PIL Image or file path to bytes
    
    Args:
        image: PIL Image object or file path
        format: Image format (PNG, JPEG, etc.)
    
    Returns:
        Image as bytes
    """
    if isinstance(image, str):
        image = Image.open(image)
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()


def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """
    Convert bytes to PIL Image
    
    Args:
        image_bytes: Image data as bytes
    
    Returns:
        PIL Image object
    """
    return Image.open(io.BytesIO(image_bytes))


def image_to_base64(image: Union[Image.Image, bytes], format: str = 'PNG') -> str:
    """
    Convert image to base64 string for embedding
    
    Args:
        image: PIL Image or bytes
        format: Image format
    
    Returns:
        Base64 encoded string with data URL prefix
    """
    if isinstance(image, Image.Image):
        image_bytes = image_to_bytes(image, format)
    else:
        image_bytes = image
    
    b64_string = base64.b64encode(image_bytes).decode()
    return f"data:image/{format.lower()};base64,{b64_string}"


def download_image_from_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """
    Download image from URL
    
    Args:
        url: Image URL
        timeout: Request timeout in seconds
    
    Returns:
        Image bytes or None if failed
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None


def resize_image(
    image: Image.Image, 
    max_width: int = 1920, 
    max_height: int = 1080,
    maintain_aspect: bool = True
) -> Image.Image:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image: PIL Image to resize
        max_width: Maximum width
        max_height: Maximum height
        maintain_aspect: Whether to maintain aspect ratio
    
    Returns:
        Resized PIL Image
    """
    if maintain_aspect:
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return image
    else:
        return image.resize((max_width, max_height), Image.Resampling.LANCZOS)


def get_image_info(image: Union[Image.Image, bytes]) -> dict:
    """
    Get information about an image
    
    Args:
        image: PIL Image or bytes
    
    Returns:
        Dictionary with image information
    """
    if isinstance(image, bytes):
        image = bytes_to_image(image)
    
    return {
        'format': image.format,
        'mode': image.mode,
        'size': image.size,
        'width': image.width,
        'height': image.height,
        'aspect_ratio': round(image.width / image.height, 2)
    }


def validate_image(
    image_bytes: bytes,
    max_size_mb: float = 10.0,
    allowed_formats: tuple = ('PNG', 'JPEG', 'JPG', 'WEBP')
) -> Tuple[bool, str]:
    """
    Validate image meets requirements
    
    Args:
        image_bytes: Image data as bytes
        max_size_mb: Maximum file size in MB
        allowed_formats: Tuple of allowed formats
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check file size
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"Image size ({size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)"
        
        # Check format
        image = bytes_to_image(image_bytes)
        if image.format.upper() not in allowed_formats:
            return False, f"Format {image.format} not allowed. Use: {', '.join(allowed_formats)}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Invalid image: {str(e)}"


def optimize_image_for_api(
    image: Union[Image.Image, bytes],
    max_dimension: int = 2048,
    quality: int = 90
) -> bytes:
    """
    Optimize image for API upload
    
    Args:
        image: PIL Image or bytes
        max_dimension: Maximum width or height
        quality: JPEG quality (1-100)
    
    Returns:
        Optimized image bytes
    """
    if isinstance(image, bytes):
        image = bytes_to_image(image)
    
    # Resize if too large
    if max(image.size) > max_dimension:
        ratio = max_dimension / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Convert RGBA to RGB if needed
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    
    # Save as JPEG for smaller size
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    return output.getvalue()


def create_thumbnail(
    image: Union[Image.Image, bytes],
    size: Tuple[int, int] = (200, 200)
) -> bytes:
    """
    Create thumbnail of image
    
    Args:
        image: PIL Image or bytes
        size: Thumbnail size (width, height)
    
    Returns:
        Thumbnail image bytes
    """
    if isinstance(image, bytes):
        image = bytes_to_image(image)
    
    image.thumbnail(size, Image.Resampling.LANCZOS)
    return image_to_bytes(image)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple
    
    Args:
        hex_color: Hex color string (e.g., '#FF5733' or 'FF5733')
    
    Returns:
        RGB tuple (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex color
    
    Args:
        rgb: RGB tuple (r, g, b)
    
    Returns:
        Hex color string
    """
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


# Example usage and tests
if __name__ == "__main__":
    print("AdSnap Studio - Image Utilities")
    print("================================")
    print("Available functions:")
    print("- image_to_bytes: Convert PIL Image to bytes")
    print("- bytes_to_image: Convert bytes to PIL Image")
    print("- image_to_base64: Convert image to base64 string")
    print("- download_image_from_url: Download image from URL")
    print("- resize_image: Resize image with aspect ratio")
    print("- get_image_info: Get image information")
    print("- validate_image: Validate image requirements")
    print("- optimize_image_for_api: Optimize for API upload")
    print("- create_thumbnail: Create image thumbnail")
    print("- hex_to_rgb / rgb_to_hex: Color conversion")
