#!/usr/bin/env python3
"""
Google Cloud Storage Bucket Setup Script for Plant Database API

This script creates and configures the 'plant-database-photos' bucket
with the proper permissions for storing plant log images.
"""

import sys
import os
import logging
from typing import Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import STORAGE_BUCKET_NAME, STORAGE_PROJECT_ID, init_storage_client
from google.cloud import storage
from google.cloud.exceptions import Conflict, NotFound

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_bucket_if_not_exists(client: storage.Client, bucket_name: str, project_id: str) -> storage.Bucket:
    """
    Create a GCS bucket if it doesn't exist, with proper configuration for public image access.
    
    Args:
        client: Authenticated GCS client
        bucket_name: Name of the bucket to create
        project_id: Google Cloud project ID
        
    Returns:
        The bucket object (existing or newly created)
    """
    try:
        # Try to get existing bucket first
        bucket = client.bucket(bucket_name)
        bucket.reload()  # Test if bucket exists and is accessible
        logger.info(f"✅ Bucket '{bucket_name}' already exists and is accessible")
        return bucket
        
    except NotFound:
        logger.info(f"📦 Creating new bucket '{bucket_name}'...")
        
        try:
            # Create bucket with appropriate settings
            bucket = client.create_bucket(
                bucket_name,
                project=project_id,
                location='US'  # Multi-region for better availability
            )
            
            logger.info(f"✅ Successfully created bucket '{bucket_name}'")
            return bucket
            
        except Conflict:
            # Bucket name exists globally but we can't access it
            logger.error(f"❌ Bucket name '{bucket_name}' is already taken globally")
            suggestion = f"{bucket_name}-{project_id}"
            logger.info(f"💡 Try using a unique name like: {suggestion}")
            raise
            
        except Exception as e:
            logger.error(f"❌ Failed to create bucket: {e}")
            raise

def configure_bucket_for_public_access(bucket: storage.Bucket) -> None:
    """
    Configure bucket settings for public read access to uploaded images.
    
    Args:
        bucket: The GCS bucket to configure
    """
    try:
        # Set bucket to allow public read access for images
        policy = bucket.get_iam_policy(requested_policy_version=3)
        
        # Add public read access
        policy.bindings.append({
            "role": "roles/storage.objectViewer",
            "members": {"allUsers"}
        })
        
        bucket.set_iam_policy(policy)
        logger.info("✅ Configured bucket for public read access")
        
    except Exception as e:
        logger.warning(f"⚠️  Could not set public access policy: {e}")
        logger.info("📝 You may need to manually set bucket permissions in the GCP Console")

def set_cors_configuration(bucket: storage.Bucket) -> None:
    """
    Set CORS configuration to allow web access to images.
    
    Args:
        bucket: The GCS bucket to configure
    """
    try:
        # Configure CORS for web access
        cors_configuration = [
            {
                "origin": ["*"],  # Allow all origins for now
                "method": ["GET", "HEAD"],
                "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
                "maxAgeSeconds": 3600
            }
        ]
        
        bucket.cors = cors_configuration
        bucket.patch()
        logger.info("✅ Configured CORS settings for web access")
        
    except Exception as e:
        logger.warning(f"⚠️  Could not set CORS configuration: {e}")
        logger.info("📝 You may need to manually configure CORS in the GCP Console")

def test_bucket_operations(bucket: storage.Bucket) -> None:
    """
    Test basic bucket operations to ensure everything is working.
    
    Args:
        bucket: The GCS bucket to test
    """
    try:
        # Test upload by creating a small test file
        test_blob_name = "test-connection.txt"
        test_content = f"Test connection at {os.getenv('USER', 'unknown')} on {os.getenv('COMPUTERNAME', 'unknown')}"
        
        blob = bucket.blob(test_blob_name)
        blob.upload_from_string(test_content, content_type='text/plain')
        
        # Make the test file public
        blob.make_public()
        
        logger.info(f"✅ Test upload successful")
        logger.info(f"🔗 Test file URL: {blob.public_url}")
        
        # Clean up test file
        blob.delete()
        logger.info("✅ Test cleanup successful")
        
    except Exception as e:
        logger.error(f"❌ Bucket operation test failed: {e}")
        raise

def main():
    """Main setup function"""
    logger.info("🚀 Starting Google Cloud Storage setup for Plant Database API")
    logger.info(f"📂 Project ID: {STORAGE_PROJECT_ID}")
    logger.info(f"🪣 Bucket Name: {STORAGE_BUCKET_NAME}")
    
    try:
        # Initialize storage client
        logger.info("🔑 Initializing Google Cloud Storage client...")
        client = init_storage_client()
        logger.info("✅ Successfully authenticated with Google Cloud Storage")
        
        # Create or verify bucket
        bucket = create_bucket_if_not_exists(client, STORAGE_BUCKET_NAME, STORAGE_PROJECT_ID)
        
        # Configure bucket settings
        logger.info("⚙️  Configuring bucket settings...")
        configure_bucket_for_public_access(bucket)
        set_cors_configuration(bucket)
        
        # Test bucket operations
        logger.info("🧪 Testing bucket operations...")
        test_bucket_operations(bucket)
        
        logger.info("🎉 Google Cloud Storage setup completed successfully!")
        logger.info(f"✅ Bucket '{STORAGE_BUCKET_NAME}' is ready for plant log images")
        
        # Print useful information
        print("\n" + "="*60)
        print("📋 SETUP SUMMARY")
        print("="*60)
        print(f"Bucket Name: {STORAGE_BUCKET_NAME}")
        print(f"Project ID: {STORAGE_PROJECT_ID}")
        print(f"Region: US (Multi-region)")
        print(f"Public Access: Enabled for uploaded images")
        print(f"CORS: Configured for web access")
        print("\n🚀 Your plant database API is now ready to upload images!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        print("\n" + "="*60)
        print("🔧 TROUBLESHOOTING STEPS")
        print("="*60)
        print("1. Verify your service account has Storage Admin permissions")
        print("2. Check that the 'gardenllm' project exists and is accessible")
        print("3. Ensure billing is enabled on your Google Cloud project")
        print("4. Try a different bucket name if this one is taken globally")
        print(f"   Suggestion: {STORAGE_BUCKET_NAME}-{STORAGE_PROJECT_ID}")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main() 