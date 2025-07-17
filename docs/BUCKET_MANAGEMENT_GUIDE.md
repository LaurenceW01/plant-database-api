# Google Cloud Storage Bucket Management Guide

## Overview
This guide shows you multiple ways to view and manage the photos stored in your `plant-database-photos` bucket.

## Method 1: Google Cloud Console (Web Interface) - **EASIEST**

### Accessing the Console
1. **Open your browser** and go to: https://console.cloud.google.com/storage
2. **Sign in** with your Google account that has access to the `gardenllm` project
3. **Select your project**: Make sure `gardenllm` is selected in the project dropdown
4. **Find your bucket**: Look for `plant-database-photos` in the bucket list

### What You Can Do in the Console
- 📋 **View all files**: Browse through your uploaded plant photos
- 📊 **See file details**: File size, upload date, public URLs
- 📁 **Navigate folders**: Files are organized in `plant-log/` folder
- 🗑️ **Delete files**: Select files and click delete
- ⬇️ **Download files**: Click on a file and select "Download"
- 🔧 **Set permissions**: Make files public or private
- 📈 **View usage statistics**: See storage usage and costs

### Viewing Photos
1. Click on the `plant-database-photos` bucket
2. Navigate to the `plant-log/` folder
3. You'll see photos with names like: `plant-log/Tomato_Plant_20240115_001.jpg`
4. Click on any photo to see details and get the public URL

## Method 2: Python Management Script - **MOST POWERFUL**

### Running the Management Script
```bash
# From your project directory
python scripts/manage_bucket.py
```

### Features Available
- **List all photos** with metadata (size, date, plant name)
- **Search by plant name** to find specific plant photos
- **View bucket statistics** (total size, number of photos, etc.)
- **Delete specific photos** with confirmation
- **Download photos** to your local computer
- **Cleanup old photos** with dry-run option
- **Search functionality** across all photos

### Sample Output
```
📸 Found 25 photos:
 1. plant-log/Tomato_Plant_20240115_001.jpg | 2.3MB | 2024-01-15 14:30:22 | Plant: Tomato Plant
 2. plant-log/Rose_Bush_20240114_002.jpg | 1.8MB | 2024-01-14 10:15:33 | Plant: Rose Bush
...

📊 BUCKET STATISTICS
Total Photos: 25
Total Size: 45.6 MB
Plants with Photos: 12
Average Photo Size: 1.8 MB
```

## Method 3: Google Cloud SDK (Command Line) - **FOR DEVELOPERS**

### Install Google Cloud SDK
1. Download from: https://cloud.google.com/sdk/docs/install
2. Follow installation instructions for Windows
3. Run: `gcloud auth login` to authenticate

### Useful Commands
```bash
# List all files in bucket
gsutil ls gs://plant-database-photos/

# List files with details (size, date)
gsutil ls -l gs://plant-database-photos/plant-log/

# Copy a file to your computer
gsutil cp gs://plant-database-photos/plant-log/filename.jpg ./downloads/

# Delete a specific file
gsutil rm gs://plant-database-photos/plant-log/filename.jpg

# Get bucket statistics
gsutil du -s gs://plant-database-photos/

# Sync bucket contents to local folder
gsutil -m rsync -r gs://plant-database-photos/ ./bucket-backup/
```

## Method 4: Programmatic Access (For Developers)

### Quick Python Script
```python
from config.config import init_storage_client, STORAGE_BUCKET_NAME

# Initialize client
client = init_storage_client()
bucket = client.bucket(STORAGE_BUCKET_NAME)

# List all photos
for blob in bucket.list_blobs(prefix='plant-log/'):
    print(f"📸 {blob.name} | {blob.size/1024/1024:.1f}MB | {blob.time_created}")
    print(f"🔗 {blob.public_url}")
```

## Common Management Tasks

### 🔍 Finding Photos for a Specific Plant
**Using Management Script:**
1. Run `python scripts/manage_bucket.py`
2. Choose option 2: "List photos by plant"
3. Enter the plant name

**Using Web Console:**
1. Go to the bucket in Google Cloud Console
2. Use the search box to filter by plant name

### 🗑️ Deleting Old or Unwanted Photos
**Using Management Script (Recommended):**
1. Run `python scripts/manage_bucket.py`
2. Choose option 7 for dry run (shows what would be deleted)
3. Choose option 8 for actual deletion

**Using Web Console:**
1. Browse to the photo in the console
2. Select the checkbox next to the file
3. Click "Delete" button

### 📊 Monitoring Storage Usage and Costs
**View in Google Cloud Console:**
1. Go to: https://console.cloud.google.com/billing
2. Select your project
3. Look for "Cloud Storage" in the usage breakdown

**Current Estimated Costs:**
- Storage: ~$0.020 per GB per month
- Operations: ~$0.005 per 1,000 operations
- Your bucket is likely costing less than $1/month

### ⬇️ Backing Up Photos
**Using the Management Script:**
```bash
# Run the management script and use option 6 to download individual photos
python scripts/manage_bucket.py
```

**Using gsutil (bulk backup):**
```bash
# Download entire bucket to local folder
gsutil -m cp -r gs://plant-database-photos/ ./plant-photos-backup/
```

## File Organization Structure

Your photos are organized like this:
```
plant-database-photos/
└── plant-log/
    ├── Tomato_Plant_20240115_143022_abc123.jpg
    ├── Rose_Bush_20240114_101533_def456.jpg
    └── Basil_20240113_160745_ghi789.png
```

**Filename Format:** `PlantName_YYYYMMDD_HHMMSS_UniqueID.extension`

## Security and Permissions

### Current Setup
- ✅ **Public read access** for uploaded images (so they display in Google Sheets)
- ✅ **Private write access** (only your API can upload new photos)
- ✅ **CORS enabled** for web access

### Changing Permissions
If you need to make photos private:
1. Go to Google Cloud Console
2. Select your bucket
3. Go to "Permissions" tab
4. Remove the "allUsers" role

## Troubleshooting

### "Access Denied" Errors
1. **Check authentication**: Make sure you're signed in to the correct Google account
2. **Verify project**: Ensure you're in the `gardenllm` project
3. **Check permissions**: Your account needs Storage Admin or Storage Object Admin role

### Photos Not Loading in Sheets
1. **Check public access**: Photos need to be publicly readable
2. **Verify URL format**: URLs should start with `https://storage.googleapis.com/`
3. **Test direct access**: Try opening the photo URL in a browser

### High Storage Costs
1. **Review old photos**: Use the cleanup function to remove old photos
2. **Check photo sizes**: Consider compressing large images
3. **Monitor usage**: Set up billing alerts in Google Cloud Console

## Best Practices

### 📅 Regular Maintenance
- **Monthly review**: Check bucket contents and remove unneeded photos
- **Size monitoring**: Keep an eye on total storage usage
- **Cost tracking**: Review Google Cloud billing monthly

### 🔒 Security
- **API key protection**: Keep your Google Cloud service account credentials secure
- **Access logging**: Monitor who's accessing your bucket (if needed)
- **Backup important photos**: Download photos you want to keep permanently

### 📈 Performance
- **Image optimization**: Keep uploaded photos under 5MB for faster loading
- **Regular cleanup**: Remove test photos and old images
- **Monitor quotas**: Be aware of Google Cloud Storage quotas and limits

## Quick Reference

| Task | Best Method | Command/Steps |
|------|-------------|---------------|
| View all photos | Web Console | Go to console.cloud.google.com/storage |
| Find plant photos | Management Script | `python scripts/manage_bucket.py` → option 2 |
| Delete old photos | Management Script | `python scripts/manage_bucket.py` → option 7/8 |
| Download photos | Web Console | Click photo → Download |
| Check storage costs | Billing Console | console.cloud.google.com/billing |
| Backup all photos | Command Line | `gsutil -m cp -r gs://plant-database-photos/ ./backup/` |

---

💡 **Pro Tip**: Start with the web console to get familiar with your bucket contents, then use the management script for regular maintenance tasks! 