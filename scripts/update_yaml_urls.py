#!/usr/bin/env python3
"""
Script to automatically update YAML files with environment-appropriate URLs.
This ensures ChatGPT actions schema always points to the correct environment.
"""

import os
import sys
import re
from pathlib import Path

def get_api_url():
    """Get the appropriate API URL based on environment settings."""
    # Check for explicit URL override
    api_url = os.getenv('API_BASE_URL')
    if api_url:
        return api_url
    
    # Auto-determine based on environment
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    if environment in ['development', 'dev']:
        return 'https://dev-plant-database-api.onrender.com'
    else:
        return 'https://plant-database-api.onrender.com'

def update_yaml_file(file_path, target_url):
    """Update a YAML file to use the target URL."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found, skipping...")
        return False
    
    print(f"Updating {file_path} to use: {target_url}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace server URL in servers section
    content = re.sub(
        r'(\s+- url: )https://[^-\s]+plant-database-api\.onrender\.com',
        f'\\1{target_url}',
        content
    )
    
    # Replace example URLs throughout the file
    content = re.sub(
        r'https://[^-\s]+plant-database-api\.onrender\.com',
        target_url,
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function to update YAML files with environment-appropriate URLs."""
    # Get the target URL for this environment
    target_url = get_api_url()
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    print(f"Environment: {environment}")
    print(f"Target URL: {target_url}")
    print("-" * 50)
    
    # Files to update
    yaml_files = [
        'chatgpt_actions_schema.yaml',
        'minimal_test_schema.yaml',
        'tests/minimal_test_schema.yaml', 
        'tests/simple_test_schema.yaml'
    ]
    
    updated_count = 0
    
    # Update each YAML file
    for yaml_file in yaml_files:
        if update_yaml_file(yaml_file, target_url):
            updated_count += 1
    
    print("-" * 50)
    print(f"Updated {updated_count} YAML files with {target_url}")
    
    # Update upload token manager default URL
    upload_manager_file = 'utils/upload_token_manager.py'
    if os.path.exists(upload_manager_file):
        print(f"Updating {upload_manager_file}...")
        with open(upload_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update default base_url parameter
        content = re.sub(
            r'(base_url: str = )"https://[^"]*plant-database-api\.onrender\.com"',
            f'\\1"{target_url}"',
            content
        )
        
        with open(upload_manager_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {upload_manager_file}")
    
    print(f"\n✅ All URLs updated for {environment} environment!")
    print(f"🌐 API Base URL: {target_url}")

if __name__ == "__main__":
    main() 