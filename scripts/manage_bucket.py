#!/usr/bin/env python3
"""
Google Cloud Storage Bucket Management Script for Plant Database API

This script helps you view, organize, and maintain the contents of your
plant-database-photos bucket.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urlparse

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import STORAGE_BUCKET_NAME, init_storage_client
from google.cloud import storage
from google.cloud.exceptions import NotFound

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BucketManager:
    """Manage Google Cloud Storage bucket for plant photos"""
    
    def __init__(self):
        """Initialize the bucket manager with storage client"""
        try:
            self.client = init_storage_client()
            self.bucket = self.client.bucket(STORAGE_BUCKET_NAME)
            logger.info(f"✅ Connected to bucket: {STORAGE_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize bucket manager: {e}")
            raise

    def list_all_photos(self) -> List[Dict]:
        """
        List all photos in the bucket with metadata.
        
        Returns:
            List of dictionaries containing photo information
        """
        logger.info("📋 Listing all photos in bucket...")
        
        photos = []
        try:
            # List all blobs in the bucket
            blobs = self.bucket.list_blobs()
            
            for blob in blobs:
                # Skip if it's not an image file
                if not self._is_image_file(blob.name):
                    continue
                
                photo_info = {
                    'name': blob.name,
                    'size_mb': round(blob.size / 1024 / 1024, 2),
                    'created': blob.time_created.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated': blob.updated.strftime('%Y-%m-%d %H:%M:%S'),
                    'public_url': blob.public_url,
                    'content_type': blob.content_type,
                    'plant_name': self._extract_plant_name(blob.name)
                }
                photos.append(photo_info)
                
            logger.info(f"📸 Found {len(photos)} photos in bucket")
            return sorted(photos, key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to list photos: {e}")
            return []

    def list_photos_by_plant(self, plant_name: str) -> List[Dict]:
        """
        List all photos for a specific plant.
        
        Args:
            plant_name: Name of the plant to search for
            
        Returns:
            List of photo dictionaries for the specified plant
        """
        logger.info(f"🔍 Searching for photos of '{plant_name}'...")
        
        all_photos = self.list_all_photos()
        plant_photos = [
            photo for photo in all_photos 
            if plant_name.lower() in photo['plant_name'].lower()
        ]
        
        logger.info(f"📸 Found {len(plant_photos)} photos for '{plant_name}'")
        return plant_photos

    def get_bucket_stats(self) -> Dict:
        """
        Get statistics about the bucket contents.
        
        Returns:
            Dictionary with bucket statistics
        """
        logger.info("📊 Calculating bucket statistics...")
        
        try:
            photos = self.list_all_photos()
            
            if not photos:
                return {
                    'total_photos': 0,
                    'total_size_mb': 0,
                    'plants_with_photos': 0,
                    'oldest_photo': None,
                    'newest_photo': None
                }
            
            total_size = sum(photo['size_mb'] for photo in photos)
            unique_plants = set(photo['plant_name'] for photo in photos)
            
            stats = {
                'total_photos': len(photos),
                'total_size_mb': round(total_size, 2),
                'plants_with_photos': len(unique_plants),
                'oldest_photo': photos[-1]['created'] if photos else None,
                'newest_photo': photos[0]['created'] if photos else None,
                'average_size_mb': round(total_size / len(photos), 2),
                'unique_plants': sorted(list(unique_plants))
            }
            
            logger.info("✅ Statistics calculated successfully")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate statistics: {e}")
            return {}

    def cleanup_old_photos(self, days_old: int = 30, dry_run: bool = True) -> List[str]:
        """
        Clean up photos older than specified days.
        
        Args:
            days_old: Number of days to consider for cleanup
            dry_run: If True, only show what would be deleted
            
        Returns:
            List of photo names that were (or would be) deleted
        """
        logger.info(f"🧹 {'Simulating' if dry_run else 'Performing'} cleanup of photos older than {days_old} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        photos_to_delete = []
        
        try:
            photos = self.list_all_photos()
            
            for photo in photos:
                photo_date = datetime.strptime(photo['created'], '%Y-%m-%d %H:%M:%S')
                if photo_date < cutoff_date:
                    photos_to_delete.append(photo['name'])
                    
                    if not dry_run:
                        blob = self.bucket.blob(photo['name'])
                        blob.delete()
                        logger.info(f"🗑️  Deleted: {photo['name']}")
                    else:
                        logger.info(f"🔍 Would delete: {photo['name']} (created {photo['created']})")
            
            if dry_run and photos_to_delete:
                logger.info(f"📋 Dry run complete. {len(photos_to_delete)} photos would be deleted")
            elif not dry_run and photos_to_delete:
                logger.info(f"✅ Cleanup complete. Deleted {len(photos_to_delete)} photos")
            else:
                logger.info("✅ No photos found that match cleanup criteria")
                
            return photos_to_delete
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return []

    def delete_photo(self, photo_name: str) -> bool:
        """
        Delete a specific photo from the bucket.
        
        Args:
            photo_name: Name of the photo to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        logger.info(f"🗑️  Deleting photo: {photo_name}")
        
        try:
            blob = self.bucket.blob(photo_name)
            blob.delete()
            logger.info(f"✅ Successfully deleted: {photo_name}")
            return True
            
        except NotFound:
            logger.warning(f"⚠️  Photo not found: {photo_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete {photo_name}: {e}")
            return False

    def download_photo(self, photo_name: str, local_path: str) -> bool:
        """
        Download a photo from the bucket to local storage.
        
        Args:
            photo_name: Name of the photo in the bucket
            local_path: Local path where to save the photo
            
        Returns:
            True if download was successful, False otherwise
        """
        logger.info(f"⬇️  Downloading {photo_name} to {local_path}")
        
        try:
            blob = self.bucket.blob(photo_name)
            blob.download_to_filename(local_path)
            logger.info(f"✅ Successfully downloaded: {photo_name}")
            return True
            
        except NotFound:
            logger.error(f"❌ Photo not found: {photo_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False

    def _is_image_file(self, filename: str) -> bool:
        """Check if a file is an image based on its extension"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def _extract_plant_name(self, filename: str) -> str:
        """Extract plant name from filename"""
        # Assuming format: plant-log/Plant_Name_timestamp_id.ext
        if filename.startswith('plant-log/'):
            basename = filename[10:]  # Remove 'plant-log/' prefix
            parts = basename.split('_')
            if len(parts) >= 2:
                # Reconstruct plant name (everything before the last two parts which are timestamp and id)
                plant_parts = parts[:-2]
                return ' '.join(plant_parts).replace('-', ' ')
        return 'Unknown'

def main():
    """Main function with interactive menu"""
    try:
        manager = BucketManager()
        
        while True:
            print("\n" + "="*60)
            print("🪣 PLANT DATABASE BUCKET MANAGER")
            print("="*60)
            print("1. List all photos")
            print("2. List photos by plant")
            print("3. Show bucket statistics")
            print("4. Search photos")
            print("5. Delete specific photo")
            print("6. Download photo")
            print("7. Cleanup old photos (dry run)")
            print("8. Cleanup old photos (actual deletion)")
            print("9. Exit")
            print("="*60)
            
            choice = input("Select an option (1-9): ").strip()
            
            if choice == '1':
                photos = manager.list_all_photos()
                print(f"\n📸 Found {len(photos)} photos:")
                for i, photo in enumerate(photos[:20], 1):  # Show first 20
                    print(f"{i:2d}. {photo['name']} | {photo['size_mb']}MB | {photo['created']} | Plant: {photo['plant_name']}")
                if len(photos) > 20:
                    print(f"... and {len(photos) - 20} more photos")
                    
            elif choice == '2':
                plant_name = input("Enter plant name: ").strip()
                if plant_name:
                    photos = manager.list_photos_by_plant(plant_name)
                    print(f"\n📸 Found {len(photos)} photos for '{plant_name}':")
                    for i, photo in enumerate(photos, 1):
                        print(f"{i:2d}. {photo['name']} | {photo['size_mb']}MB | {photo['created']}")
                        print(f"    🔗 {photo['public_url']}")
                        
            elif choice == '3':
                stats = manager.get_bucket_stats()
                print(f"\n📊 BUCKET STATISTICS")
                print("-" * 40)
                print(f"Total Photos: {stats.get('total_photos', 0)}")
                print(f"Total Size: {stats.get('total_size_mb', 0)} MB")
                print(f"Plants with Photos: {stats.get('plants_with_photos', 0)}")
                print(f"Average Photo Size: {stats.get('average_size_mb', 0)} MB")
                print(f"Oldest Photo: {stats.get('oldest_photo', 'N/A')}")
                print(f"Newest Photo: {stats.get('newest_photo', 'N/A')}")
                
                if stats.get('unique_plants'):
                    print(f"\n🌱 Plants with photos:")
                    for plant in stats['unique_plants']:
                        print(f"   - {plant}")
                        
            elif choice == '4':
                search_term = input("Enter search term: ").strip()
                if search_term:
                    photos = manager.list_all_photos()
                    matching = [p for p in photos if search_term.lower() in p['name'].lower() or 
                              search_term.lower() in p['plant_name'].lower()]
                    print(f"\n🔍 Found {len(matching)} photos matching '{search_term}':")
                    for photo in matching:
                        print(f"   {photo['name']} | Plant: {photo['plant_name']}")
                        
            elif choice == '5':
                photo_name = input("Enter photo name to delete: ").strip()
                if photo_name:
                    confirm = input(f"Are you sure you want to delete '{photo_name}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        manager.delete_photo(photo_name)
                    else:
                        print("❌ Deletion cancelled")
                        
            elif choice == '6':
                photo_name = input("Enter photo name to download: ").strip()
                local_path = input("Enter local path (with filename): ").strip()
                if photo_name and local_path:
                    manager.download_photo(photo_name, local_path)
                    
            elif choice == '7':
                days = input("Enter number of days (default 30): ").strip()
                days = int(days) if days.isdigit() else 30
                deleted = manager.cleanup_old_photos(days, dry_run=True)
                print(f"\n📋 Dry run: {len(deleted)} photos would be deleted")
                
            elif choice == '8':
                days = input("Enter number of days (default 30): ").strip()
                days = int(days) if days.isdigit() else 30
                confirm = input(f"Are you sure you want to delete photos older than {days} days? (yes/no): ")
                if confirm.lower() == 'yes':
                    deleted = manager.cleanup_old_photos(days, dry_run=False)
                    print(f"✅ Deleted {len(deleted)} photos")
                else:
                    print("❌ Cleanup cancelled")
                    
            elif choice == '9':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")

if __name__ == "__main__":
    main() 