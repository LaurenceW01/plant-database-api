#!/usr/bin/env python3
"""
Simple environment switcher - reads from .env file and updates YAML files accordingly.
Usage: python scripts/switch_env.py
"""

import os
import re
from dotenv import load_dotenv

def update_yaml_files():
    """Update YAML files with the correct URL based on .env settings."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get environment and API URL
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    api_url = os.getenv('API_BASE_URL')
    
    # Auto-determine URL if not explicitly set
    if not api_url:
        if environment in ['development', 'dev']:
            api_url = 'https://dev-plant-database-api.onrender.com'
        else:
            api_url = 'https://plant-database-api.onrender.com'
    
    print(f"🔧 Environment: {environment}")
    print(f"🌐 API URL: {api_url}")
    print("-" * 50)
    
    # Files to update
    files_to_update = [
        'chatgpt_actions_schema.yaml',
        'minimal_test_schema.yaml',
        'tests/minimal_test_schema.yaml',
        'tests/simple_test_schema.yaml',
        'chatgpt_endpoints.md'
    ]
    
    updated_count = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            print(f"📝 Updating {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace server URL
            old_content = content
            content = re.sub(
                r'(\s+- url: )https://[^/\s]*plant-database-api\.onrender\.com',
                f'\\1{api_url}',
                content
            )
            
            # Replace server description to match environment
            if environment in ['development', 'dev']:
                content = re.sub(
                    r'(\s+description: )Production server',
                    '\\1Development server',
                    content
                )
            else:
                content = re.sub(
                    r'(\s+description: )Development server',
                    '\\1Production server',
                    content
                )
            
            # Replace example URLs
            content = re.sub(
                r'https://[^/\s]*plant-database-api\.onrender\.com',
                api_url,
                content
            )
            
            if content != old_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_count += 1
                print(f"✅ Updated {file_path}")
            else:
                print(f"⚠️  No changes needed for {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("-" * 50)
    print(f"🎉 Updated {updated_count} files for {environment} environment!")
    print(f"🚀 Ready to use: {api_url}")

if __name__ == "__main__":
    update_yaml_files() 