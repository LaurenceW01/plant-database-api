"""
Script to migrate photos from Google Photos to Google Cloud Storage.
Downloads photos from Google Photos URLs and uploads them to GCS bucket.
"""

import os
import sys
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime
from urllib.parse import urlparse

# Add parent directory to path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage_client import upload_plant_photo, storage_client, STORAGE_BUCKET_NAME
from utils.plant_operations import get_plant_data, update_plant_field, get_canonical_field_name
from config.config import sheets_client, SPREADSHEET_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('photo_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_google_photos_url(url: str) -> bool:
    """Check if a URL is from Google Photos."""
    if not url:
        return False
    parsed = urlparse(url)
    return any(domain in parsed.netloc.lower() for domain in [
        'photos.google.com',
        'photos.app.goo.gl',
        'lh3.googleusercontent.com',
        'googleusercontent.com'
    ]) or 'googleusercontent' in url.lower()

def download_photo(url: str) -> Optional[bytes]:
    """Download photo from URL."""
    try:
        # Add a User-Agent header to avoid potential blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Failed to download photo from {url}: {str(e)}")
        return None

def migrate_plant_photos() -> Dict[str, int]:
    """
    Migrate photos from Google Photos to Google Cloud Storage.
    
    Returns:
        Dict with counts of successful and failed migrations
    """
    if not storage_client:
        logger.error("Google Cloud Storage client not available")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    if not sheets_client:
        logger.error("Google Sheets client not available")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    # Get all plants with full data
    plants = get_plant_data()
    if not plants:
        logger.error("Failed to fetch plants from database")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    stats = {"success": 0, "failed": 0, "skipped": 0}
    
    # Get canonical field names
    plant_name_field = get_canonical_field_name('Plant Name')
    raw_photo_url_field = get_canonical_field_name('Raw Photo URL')
    
    for plant in plants:
        plant_name = plant.get(plant_name_field, '')
        raw_photo_url = plant.get(raw_photo_url_field, '')
        
        if not raw_photo_url:
            logger.info(f"No photo URL for plant: {plant_name}")
            stats["skipped"] += 1
            continue
            
        if not is_google_photos_url(raw_photo_url):
            logger.info(f"Not a Google Photos URL for plant {plant_name}: {raw_photo_url}")
            stats["skipped"] += 1
            continue
            
        logger.info(f"Processing plant: {plant_name}")
        logger.info(f"Current photo URL: {raw_photo_url}")
        
        # Download photo
        photo_data = download_photo(raw_photo_url)
        if not photo_data:
            logger.error(f"Failed to download photo for {plant_name}")
            stats["failed"] += 1
            continue
        
        # Create temporary file for upload
        temp_filename = f"temp_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        try:
            with open(temp_filename, 'wb') as f:
                f.write(photo_data)
            
            # Upload to GCS
            from werkzeug.datastructures import FileStorage
            with open(temp_filename, 'rb') as f:
                file = FileStorage(
                    stream=f,
                    filename=f"{plant_name.replace(' ', '_')}.jpg",
                    content_type='image/jpeg'
                )
                upload_result = upload_plant_photo(file, plant_name)
            
            # Update plant record
            if upload_result and 'raw_photo_url' in upload_result:
                new_photo_url = upload_result['raw_photo_url']
                # Get the row number from the plant data
                row_number = plants.index(plant) + 2  # Add 2 because sheet is 1-indexed and has header row
                if update_plant_field(row_number, 'Photo URL', new_photo_url):
                    logger.info(f"Successfully migrated photo for {plant_name}")
                    stats["success"] += 1
                else:
                    logger.error(f"Failed to update plant record for {plant_name}")
                    stats["failed"] += 1
            else:
                logger.error(f"Failed to upload photo for {plant_name}")
                stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"Error processing {plant_name}: {str(e)}")
            stats["failed"] += 1
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    return stats

if __name__ == "__main__":
    logger.info("Starting photo migration...")
    stats = migrate_plant_photos()
    logger.info(f"Migration complete. Results:")
    logger.info(f"Successfully migrated: {stats['success']}")
    logger.info(f"Failed migrations: {stats['failed']}")
    logger.info(f"Skipped (no Google Photos URL): {stats['skipped']}") 