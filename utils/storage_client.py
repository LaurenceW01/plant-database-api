"""
Google Cloud Storage client for plant photo management.
Handles image uploads, URL generation, and storage management for the Plant Database API.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from werkzeug.datastructures import FileStorage
from google.cloud.exceptions import NotFound
import os

logger = logging.getLogger(__name__)

# Import storage client and configuration from config
try:
    from config.config import init_storage_client, STORAGE_BUCKET_NAME, STORAGE_PROJECT_ID
    # Initialize storage client with retry logic
    max_retries = 3
    retry_count = 0
    storage_client = None
    
    while retry_count < max_retries and storage_client is None:
        try:
            storage_client = init_storage_client()
            if storage_client:
                logger.info("Successfully initialized Google Cloud Storage client")
                break
        except Exception as e:
            retry_count += 1
            logger.error(f"Attempt {retry_count} failed to initialize storage client: {e}")
            if retry_count < max_retries:
                import time
                time.sleep(1)
    
    if storage_client is None:
        logger.warning("Could not initialize Google Cloud Storage client - photo uploads will be disabled")
        
except Exception as e:
    logger.error(f"Failed to import storage configuration: {e}")
    storage_client = None

def generate_unique_filename(original_filename: str, plant_name: str = None) -> str:
    """
    Generate a unique filename for uploaded plant photos.
    
    Args:
        original_filename (str): Original filename from upload
        plant_name (str, optional): Name of the plant for organization
        
    Returns:
        str: Unique filename with plant-log prefix and timestamp
    """
    # Extract file extension from original filename
    file_extension = os.path.splitext(original_filename)[1].lower()
    if not file_extension:
        file_extension = '.jpg'  # Default to .jpg if no extension
    
    # Generate timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate unique ID for additional uniqueness
    unique_id = str(uuid.uuid4())[:8]
    
    # Create plant-specific prefix if plant name provided
    plant_prefix = ""
    if plant_name:
        # Sanitize plant name for filename (remove special characters)
        sanitized_name = "".join(c for c in plant_name if c.isalnum() or c in (' ', '-', '_')).strip()
        sanitized_name = sanitized_name.replace(' ', '_')[:20]  # Limit length
        plant_prefix = f"{sanitized_name}_"
    
    # Construct filename: plant-log/{plant_prefix}YYYYMMDD_HHMMSS_{unique_id}.ext
    filename = f"plant-log/{plant_prefix}{timestamp}_{unique_id}{file_extension}"
    
    return filename

def validate_image_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate uploaded image file for size, type, and safety.
    
    Args:
        file (FileStorage): Uploaded file object
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check file exists
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file size (limit to 10MB for plant photos)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if hasattr(file, 'content_length') and file.content_length > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    # Check MIME type if available
    if hasattr(file, 'mimetype') and file.mimetype:
        allowed_mimetypes = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        if file.mimetype not in allowed_mimetypes:
            return False, "Invalid file type detected"
    
    return True, ""

def upload_plant_photo(file: FileStorage, plant_name: str = None) -> Dict[str, str]:
    """
    Upload a plant photo to Google Cloud Storage and return URLs.
    
    Args:
        file (FileStorage): The uploaded image file
        plant_name (str, optional): Name of the plant for organization
        
    Returns:
        Dict[str, str]: Dictionary containing photo_url, raw_photo_url, and metadata
        
    Raises:
        ValueError: If file validation fails or storage client unavailable
        Exception: If upload fails
    """
    # Check if storage client is available
    if storage_client is None:
        raise ValueError("Google Cloud Storage not available - check configuration")
    
    # Validate the uploaded file
    is_valid, error_message = validate_image_file(file)
    if not is_valid:
        raise ValueError(f"File validation failed: {error_message}")
    
    try:
        # Generate unique filename
        filename = generate_unique_filename(file.filename, plant_name)
        
        # Get the bucket
        bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
        
        # Create blob object
        blob = bucket.blob(filename)
        
        # Set appropriate content type
        if hasattr(file, 'mimetype') and file.mimetype:
            blob.content_type = file.mimetype
        else:
            # Guess content type from extension
            extension_to_mimetype = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            file_extension = os.path.splitext(filename)[1].lower()
            blob.content_type = extension_to_mimetype.get(file_extension, 'image/jpeg')
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Upload the file
        blob.upload_from_file(file.stream, content_type=blob.content_type)
        
        # Make the blob publicly readable
        blob.make_public()
        
        # Generate URLs
        public_url = blob.public_url
        raw_photo_url = public_url
        
        # For photo_url, we can use the same public URL or format it for sheets
        photo_url = f'=IMAGE("{public_url}")'
        
        logger.info(f"Successfully uploaded plant photo: {filename}")
        
        return {
            'photo_url': photo_url,
            'raw_photo_url': raw_photo_url,
            'filename': filename,
            'upload_time': datetime.now().isoformat(),
            'file_size': blob.size if hasattr(blob, 'size') else 'unknown',
            'content_type': blob.content_type
        }
        
    except NotFound:
        error_msg = f"Storage bucket '{STORAGE_BUCKET_NAME}' not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Failed to upload image: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def delete_plant_photo(filename: str) -> bool:
    """
    Delete a plant photo from Google Cloud Storage.
    
    Args:
        filename (str): The filename/path of the photo to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    if storage_client is None:
        logger.warning("Storage client not available - cannot delete photo")
        return False
    
    try:
        bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
        blob = bucket.blob(filename)
        
        if blob.exists():
            blob.delete()
            logger.info(f"Successfully deleted plant photo: {filename}")
            return True
        else:
            logger.warning(f"Photo not found for deletion: {filename}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to delete photo {filename}: {str(e)}")
        return False

def get_photo_metadata(filename: str) -> Optional[Dict]:
    """
    Get metadata for a plant photo.
    
    Args:
        filename (str): The filename/path of the photo
        
    Returns:
        Optional[Dict]: Photo metadata or None if not found
    """
    if storage_client is None:
        return None
    
    try:
        bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
        blob = bucket.blob(filename)
        
        if blob.exists():
            blob.reload()  # Refresh metadata
            return {
                'filename': filename,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created.isoformat() if blob.time_created else None,
                'updated': blob.updated.isoformat() if blob.updated else None,
                'public_url': blob.public_url
            }
        else:
            return None
            
    except Exception as e:
        logger.error(f"Failed to get photo metadata for {filename}: {str(e)}")
        return None

def is_storage_available() -> bool:
    """
    Check if Google Cloud Storage is available and configured.
    
    Returns:
        bool: True if storage is available, False otherwise
    """
    return storage_client is not None

def create_bucket_if_not_exists() -> bool:
    """
    Create the storage bucket if it doesn't exist.
    
    Returns:
        bool: True if bucket exists or was created successfully
    """
    if storage_client is None:
        return False
    
    try:
        bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
        if not bucket.exists():
            # Create bucket with appropriate settings
            bucket = storage_client.create_bucket(
                STORAGE_BUCKET_NAME,
                location='US'  # You can change this to your preferred region
            )
            logger.info(f"Created storage bucket: {STORAGE_BUCKET_NAME}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create/check bucket: {str(e)}")
        return False 