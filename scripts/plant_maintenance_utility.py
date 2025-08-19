#!/usr/bin/env python3
"""
Plant Maintenance Utility

A command-line utility to efficiently update plant columns in the plant database.
Includes proper rate limiting to avoid overloading the API.

Usage examples:
    python plant_maintenance_utility.py --columns soil_ph_type soil_ph_range
    python plant_maintenance_utility.py --columns soil_ph_type --plant-id 123
    python plant_maintenance_utility.py --columns all --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Set, Any
import requests
from datetime import datetime, timedelta

# Add the parent directory to the path to import project modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import API_BASE_URL, openai_client, sheets_client, SPREADSHEET_ID, RANGE_NAME
from models.field_config import FIELD_NAMES, get_canonical_field_name
from utils.sheets_client import check_rate_limit

# Configure logging with plain text characters to avoid UTF-8 encoding issues on Windows terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_plant_ids(plant_ids_str: str) -> List[str]:
    """
    Parse plant IDs from various formats:
    - Individual: "67"
    - Ranges: "67-69" (expands to 67,68,69)
    - Comma-delimited: "67,68,71-75" (expands to 67,68,71,72,73,74,75)
    
    Args:
        plant_ids_str: String containing plant IDs in various formats
        
    Returns:
        List of individual plant ID strings
    """
    plant_ids = []
    
    # Split by commas first
    parts = [part.strip() for part in plant_ids_str.split(',')]
    
    for part in parts:
        if '-' in part:
            # Handle range like "67-69"
            try:
                start, end = part.split('-', 1)
                start_id = int(start.strip())
                end_id = int(end.strip())
                
                if start_id > end_id:
                    raise ValueError(f"Invalid range: {part} - start must be <= end")
                
                # Add all IDs in the range
                for i in range(start_id, end_id + 1):
                    plant_ids.append(str(i))
                    
            except ValueError as e:
                if "Invalid range" in str(e):
                    raise e
                else:
                    raise ValueError(f"Invalid range format: {part} - must be like '67-69'")
        else:
            # Handle individual ID
            try:
                int(part)  # Validate it's a number
                plant_ids.append(part)
            except ValueError:
                raise ValueError(f"Invalid plant ID: {part} - must be a number")
    
    return plant_ids


class PlantMaintenanceUtility:
    """
    A utility class for maintaining plant data via API calls with proper rate limiting.
    """
    
    def __init__(self, api_key: str, base_url: str = None, rate_limit_delay: float = 6.5):
        """
        Initialize the plant maintenance utility.
        
        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API (defaults to config value)
            rate_limit_delay: Delay between requests in seconds (default 6.5s for ~9 req/min)
        """
        self.api_key = api_key
        self.base_url = base_url or API_BASE_URL
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        # Track request timing for rate limiting
        self.last_request_time = None
        self.request_count = 0
        self.start_time = datetime.now()
        
        logger.info(f"Initialized Plant Maintenance Utility")
        logger.info(f"API Base URL: {self.base_url}")
        logger.info(f"Rate limit delay: {self.rate_limit_delay}s between requests")
    
    def _enforce_rate_limit(self):
        """
        Enforce rate limiting by sleeping if necessary.
        Uses conservative rate limiting to avoid overloading the API.
        """
        if self.last_request_time is not None:
            # Calculate time since last request
            time_since_last = time.time() - self.last_request_time
            
            # If we haven't waited long enough, sleep for the remaining time
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                logger.info(f"Rate limiting: Sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        # Update last request time
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_all_plants(self) -> List[Dict[str, Any]]:
        """
        Retrieve all plants from the API using the search endpoint.
        
        Returns:
            List of plant dictionaries
        """
        logger.info("Fetching all plants from API...")
        self._enforce_rate_limit()
        
        try:
            # Use the search endpoint without a query to get all plants
            response = self.session.get(f"{self.base_url}/api/plants/search")
            response.raise_for_status()
            
            data = response.json()
            plants = data.get('plants', [])
            logger.info(f"SUCCESS: Retrieved {len(plants)} plants from API")
            return plants
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ERROR: Failed to retrieve plants: {e}")
            raise
    
    def update_plants_batch_optimized(self, plant_updates: Dict[str, Dict[str, str]], dry_run: bool = False) -> Dict[str, Any]:
        """
        Optimized batch update of multiple plants using minimal Google Sheets API calls.
        
        Reduces API calls from 5-per-plant to 2-total for any number of plants:
        1. Single sheet read to get all data and find all plant rows
        2. Single batch update for all field changes and timestamps
        
        Args:
            plant_updates: Dictionary mapping plant_id to update_data dict
            dry_run: If True, don't actually update
            
        Returns:
            Dictionary with update results
        """
        if dry_run:
            logger.info(f"DRY RUN: Would batch update {len(plant_updates)} plants")
            for plant_id, data in plant_updates.items():
                logger.info(f"  Plant {plant_id}: {data}")
            return {"message": "Dry run - no actual update performed", "success": True, "updated_count": len(plant_updates)}
        
        logger.info(f"OPTIMIZED BATCH UPDATE: Updating {len(plant_updates)} plants with only 2 API calls...")
        
        try:
            # API CALL 1: Get all sheet data once
            logger.info("Reading complete sheet data (API call 1/2)...")
            check_rate_limit()
            result = sheets_client.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return {"error": "No data found in sheet", "success": False}
            
            headers = values[0]
            
            # Create column mapping for fast lookups
            column_map = {}
            for idx, header in enumerate(headers):
                column_map[header.lower()] = idx
            
            # Find ID column
            id_column = None
            for potential_name in ['id', 'plant id', 'plant_id']:
                if potential_name in column_map:
                    id_column = column_map[potential_name]
                    break
            
            if id_column is None:
                return {"error": "Could not find ID column", "success": False}
            
            # Find last updated column
            last_updated_column = None
            for potential_name in ['last updated', 'last_updated', 'lastupdated']:
                if potential_name in column_map:
                    last_updated_column = column_map[potential_name]
                    break
            
            # Find all requested plants in one pass through the sheet
            plant_rows = {}
            for sheet_row_1_based, row in enumerate(values[1:], start=2):
                if len(row) > id_column:
                    cell_value = str(row[id_column]).strip()
                    if cell_value in plant_updates:
                        plant_rows[cell_value] = sheet_row_1_based
                        logger.info(f"Located plant {cell_value} at sheet row {sheet_row_1_based}")
            
            # Prepare batch update data
            batch_updates = []
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            successful_plants = 0
            
            for plant_id, update_data in plant_updates.items():
                if plant_id not in plant_rows:
                    logger.warning(f"Plant {plant_id} not found in sheet - skipping")
                    continue
                
                row_number = plant_rows[plant_id]
                successful_plants += 1
                
                # Add field updates to batch
                for field_name, field_value in update_data.items():
                    # Get canonical field name and find column
                    canonical_field_name = get_canonical_field_name(field_name)
                    if not canonical_field_name:
                        canonical_field_name = field_name
                    
                    column_index = column_map.get(canonical_field_name.lower())
                    if column_index is not None:
                        column_letter = chr(ord('A') + column_index)
                        cell_range = f"Plants!{column_letter}{row_number}"
                        batch_updates.append({
                            'range': cell_range,
                            'values': [[field_value]]
                        })
                        logger.debug(f"Queued: {field_name} -> {cell_range} = '{field_value}'")
                    else:
                        logger.warning(f"Column '{field_name}' not found for plant {plant_id}")
                
                # Add timestamp update to batch
                if last_updated_column is not None:
                    column_letter = chr(ord('A') + last_updated_column)
                    timestamp_range = f"Plants!{column_letter}{row_number}"
                    batch_updates.append({
                        'range': timestamp_range,
                        'values': [[timestamp]]
                    })
            
            if not batch_updates:
                return {"error": "No valid updates prepared", "success": False}
            
            # API CALL 2: Execute all updates in single batch operation
            logger.info(f"Executing batch update: {len(batch_updates)} cells across {successful_plants} plants (API call 2/2)...")
            check_rate_limit()
            sheets_client.values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': batch_updates
                }
            ).execute()
            
            # Invalidate cache
            from utils.plant_cache_operations import invalidate_plant_list_cache
            invalidate_plant_list_cache()
            
            logger.info(f"SUCCESS: Optimized batch update completed!")
            logger.info(f"  Plants updated: {successful_plants}")
            logger.info(f"  Total cells updated: {len(batch_updates)}")
            logger.info(f"  Total API calls: 2 (vs {successful_plants * 5} with old method)")
            
            return {
                "message": f"Successfully updated {successful_plants} plants", 
                "success": True,
                "updated_count": successful_plants,
                "total_api_calls": 2,
                "cells_updated": len(batch_updates)
            }
            
        except Exception as e:
            logger.error(f"Error in optimized batch update: {e}")
            return {"error": str(e), "success": False}

    def update_plant_directly(self, plant_id: str, plant_row: int, update_data: Dict[str, str], dry_run: bool = False) -> Dict[str, Any]:
        """
        Update a single plant directly in Google Sheets.
        
        Args:
            plant_id: The ID or name of the plant to update
            plant_row: The row number of the plant in the sheet (0-based)
            update_data: Dictionary of field names and values to update
            dry_run: If True, don't actually update the sheet
            
        Returns:
            Update result dictionary
        """
        if dry_run:
            logger.info(f"DRY RUN: Would update plant {plant_id} (row {plant_row}) with data: {update_data}")
            return {"message": "Dry run - no actual update performed", "success": True}
        
        logger.info(f"Updating plant {plant_id} (sheet row {plant_row + 1}, 0-based: {plant_row}) directly in Google Sheets with {len(update_data)} fields...")
        
        try:
            # Get the sheet headers to find column indices
            check_rate_limit()
            result = sheets_client.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            headers = result.get('values', [])[0] if result.get('values') else []
            
            if not headers:
                raise ValueError("Could not retrieve sheet headers")
            
            successful_updates = 0
            failed_updates = 0
            errors = []
            
            # Update each field individually
            for field_name, new_value in update_data.items():
                try:
                    # Get canonical field name
                    canonical_field_name = get_canonical_field_name(field_name)
                    if not canonical_field_name:
                        canonical_field_name = field_name  # Use as-is if not found in config
                    
                    # Find column index
                    try:
                        col_idx = headers.index(canonical_field_name)
                    except ValueError:
                        # Try alternative field name formats
                        alt_names = [field_name, field_name.replace('_', ' ').title()]
                        col_idx = None
                        for alt_name in alt_names:
                            try:
                                col_idx = headers.index(alt_name)
                                break
                            except ValueError:
                                continue
                        
                        if col_idx is None:
                            error_msg = f"Field '{field_name}' not found in sheet headers: {headers}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            failed_updates += 1
                            continue
                    
                    # Calculate cell reference (convert to 1-based)
                    range_name = f'Plants!{chr(65 + col_idx)}{plant_row + 1}'
                    
                    logger.info(f"Updating {canonical_field_name} at {range_name} with value: {new_value}")
                    
                    # Apply rate limiting before each sheet operation
                    check_rate_limit()
                    
                    # Update the cell
                    sheets_client.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body={'values': [[new_value]]}
                    ).execute()
                    
                    successful_updates += 1
                    logger.info(f"SUCCESS: Updated {canonical_field_name} for plant {plant_id}")
                    
                except Exception as field_error:
                    error_msg = f"Failed to update field '{field_name}': {str(field_error)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failed_updates += 1
            
            # Update Last Updated timestamp
            try:
                last_updated_field = get_canonical_field_name('last_updated') or 'Last Updated'
                if last_updated_field in headers:
                    col_idx = headers.index(last_updated_field)
                    range_name = f'Plants!{chr(65 + col_idx)}{plant_row + 1}'
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    check_rate_limit()
                    sheets_client.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body={'values': [[timestamp]]}
                    ).execute()
                    logger.info(f"Updated Last Updated timestamp for plant {plant_id}")
            except Exception as e:
                logger.warning(f"Failed to update Last Updated timestamp: {e}")
            
            # Invalidate cache
            try:
                from utils.plant_cache_operations import invalidate_plant_list_cache
                invalidate_plant_list_cache()
            except ImportError:
                logger.info("Cache invalidation not available (utils not imported)")
            
            result = {
                "success": successful_updates > 0,
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "total_fields": len(update_data),
                "message": f"Updated {successful_updates}/{len(update_data)} fields for plant {plant_id}"
            }
            
            if errors:
                result["errors"] = errors
            
            return result
            
        except Exception as e:
            logger.error(f"ERROR: Failed to update plant {plant_id} in Google Sheets: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update plant {plant_id}"
            }
    
    def _find_plant_row(self, plant_id: str) -> int:
        """
        Find the row number of a plant in the Google Sheet by ID.
        
        Args:
            plant_id: The plant ID to find
            
        Returns:
            Row number (0-based) or -1 if not found
        """
        try:
            check_rate_limit()
            result = sheets_client.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return -1
            
            headers = values[0]
            
            # Find ID column
            id_column = None
            for idx, header in enumerate(headers):
                if header.lower() in ['id', 'plant id', 'plant_id']:
                    id_column = idx
                    break
            
            if id_column is None:
                logger.warning("Could not find ID column in sheet")
                return -1
            
            # Search through all rows to find the plant ID
            logger.info(f"Searching for plant ID {plant_id} in sheet with {len(values)} total rows")
            logger.info(f"ID column is at index {id_column} (header: {headers[id_column]})")
            
            for sheet_row_1_based, row in enumerate(values[1:], start=2):  # Start at row 2 (1-based), skipping header
                if len(row) > id_column:
                    cell_value = str(row[id_column]).strip()
                    logger.debug(f"Checking row {sheet_row_1_based}: ID column value = '{cell_value}'")
                    if cell_value == str(plant_id):
                        sheet_row_0_based = sheet_row_1_based - 1  # Convert to 0-based
                        logger.info(f"FOUND: Plant ID {plant_id} is at sheet row {sheet_row_1_based} (0-based: {sheet_row_0_based})")
                        return sheet_row_0_based
                else:
                    logger.debug(f"Row {sheet_row_1_based} has only {len(row)} columns, skipping")
            
            logger.warning(f"Plant ID {plant_id} not found in sheet")
            return -1
            
        except Exception as e:
            logger.error(f"Error finding plant row for ID {plant_id}: {e}")
            return -1
    
    def get_valid_columns(self) -> Set[str]:
        """
        Get the set of valid column names that can be updated.
        
        Returns:
            Set of valid field names
        """
        # Exclude auto-generated fields that shouldn't be manually updated
        excluded_fields = {'id', 'last_updated', 'plant_name', 'photo_url', 'raw_photo_url'}
        valid_fields = set(FIELD_NAMES) - excluded_fields
        return valid_fields
    
    def get_ai_generated_fields(self) -> Set[str]:
        """
        Get the set of AI-generated field names that can be bulk updated.
        
        These are the fields that AI can determine based on plant name and botanical knowledge.
        Excludes basic identification fields and system-generated fields.
        
        Returns:
            Set of AI-generated field names
        """
        # Fields that AI can intelligently determine for plants
        ai_fields = {
            'description',
            'light_requirements',
            'frost_tolerance',
            'watering_needs',
            'soil_preferences',
            'soil_ph_type',
            'soil_ph_range',
            'pruning_instructions',
            'mulching_needs',
            'fertilizing_schedule',
            'winterizing_instructions',
            'spacing_requirements',
            'care_notes'
        }
        return ai_fields
    
    def validate_columns(self, columns: List[str]) -> List[str]:
        """
        Validate that the provided columns are valid field names.
        
        Args:
            columns: List of column names to validate
            
        Returns:
            List of valid column names
            
        Raises:
            ValueError: If any column names are invalid
        """
        valid_columns = self.get_valid_columns()
        ai_fields = self.get_ai_generated_fields()
        
        # Handle special cases for bulk options
        if len(columns) == 1:
            if columns[0].lower() == 'all':
                return sorted(list(valid_columns))
            elif columns[0].lower() in ['ai-fields', 'ai_fields', 'aifields']:
                logger.info(f"AI-FIELDS: Selected {len(ai_fields)} AI-generated fields for bulk update")
                return sorted(list(ai_fields))
        
        # Validate each column
        invalid_columns = []
        for column in columns:
            if column not in valid_columns:
                invalid_columns.append(column)
        
        if invalid_columns:
            logger.error(f"ERROR: Invalid column names: {invalid_columns}")
            logger.info(f"Valid columns are: {sorted(list(valid_columns))}")
            logger.info(f"AI-generated fields available: {sorted(list(ai_fields))}")
            logger.info(f"Use 'all' for all columns or 'ai-fields' for AI-generated fields only")
            raise ValueError(f"Invalid column names: {invalid_columns}")
        
        return columns
    
    def determine_plant_values(self, plant: Dict[str, Any], columns: List[str]) -> Dict[str, str]:
        """
        Determine appropriate values for the specified columns for a specific plant using AI.
        
        Args:
            plant: Dictionary containing plant information
            columns: List of column names to determine values for
            
        Returns:
            Dictionary mapping column names to appropriate values for this plant
        """
        plant_name = plant.get('plant_name', plant.get('Plant Name', 'Unknown Plant'))
        plant_id = plant.get('id', plant.get('ID', 'Unknown ID'))
        
        logger.info(f"Determining AI values for plant: {plant_name} (ID: {plant_id})")
        
        try:
            # Use AI to determine values for all requested columns
            ai_values = self._get_ai_plant_values(plant_name, columns)
            return ai_values
        except Exception as e:
            logger.error(f"ERROR: AI determination failed for {plant_name}: {e}")
            # Fallback to manual input if AI fails
            values = {}
            for column in columns:
                values[column] = self._prompt_for_plant_value(plant_name, column)
            return values
    
    def _get_ai_plant_values(self, plant_name: str, columns: List[str]) -> Dict[str, str]:
        """
        Use AI to determine appropriate values for the specified columns for a plant.
        
        Args:
            plant_name: Name of the plant
            columns: List of column names to get values for
            
        Returns:
            Dictionary mapping column names to AI-determined values
        """
        # Create a structured prompt for the AI to fill in the requested fields
        field_descriptions = {
            'soil_ph_type': 'Soil pH Type (must be one of: high alkalinity, medium alkalinity, slightly alkaline, neutral, slightly acidic, medium acidity, high acidity)',
            'soil_ph_range': 'Soil pH Range (format like "5.5 - 6.5" with numerical ranges only)',
            'description': 'Plant description',
            'light_requirements': 'Light requirements (e.g., "Full Sun", "Partial Shade")',
            'watering_needs': 'Watering requirements and frequency',
            'soil_preferences': 'Soil type and drainage preferences',
            'frost_tolerance': 'Cold hardiness and frost tolerance information',
            'pruning_instructions': 'When and how to prune this plant',
            'mulching_needs': 'Mulching recommendations',
            'fertilizing_schedule': 'Fertilization timing and type',
            'winterizing_instructions': 'Winter care instructions',
            'spacing_requirements': 'Plant spacing recommendations',
            'care_notes': 'Additional care information and tips',
            'location': 'Preferred garden locations or growing zones'
        }
        
        # Build the prompt with requested fields
        requested_fields = []
        for column in columns:
            if column in field_descriptions:
                # Create proper field name for display (handling special cases)
                if column == 'soil_ph_type':
                    display_name = "Soil Ph Type"
                elif column == 'soil_ph_range':
                    display_name = "Soil Ph Range"
                else:
                    display_name = column.replace('_', ' ').title()
                requested_fields.append(f"**{display_name}:** {field_descriptions[column]}")
        
        prompt = f"""Provide specific plant care information for: {plant_name}
        
Please fill in the following fields with accurate, specific information for this plant.

{chr(10).join(requested_fields)}

IMPORTANT FORMAT REQUIREMENTS:
- Use EXACTLY the field names shown above with double asterisks and colons
- For Soil pH Type: Must be one of: high alkalinity, medium alkalinity, slightly alkaline, neutral, slightly acidic, medium acidity, high acidity
- For Soil pH Range: Use format like "5.5 - 6.5" (numerical ranges only)
- Be specific and accurate for this exact plant variety
- Focus on practical advice for Houston, Texas climate"""

        logger.info(f"Making AI call for {plant_name} with {len(columns)} columns")
        
        try:
            # Rate limiting for AI calls (separate from API rate limiting)
            time.sleep(1)  # Brief delay between AI calls
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert gardener and plant database manager specializing in Houston, Texas climate. "
                                   "Provide accurate, specific plant care information. Use the exact format requested. "
                                   "For soil pH information: Soil pH Type must be one of the seven specified options. "
                                   "Soil pH Range must be in numerical format like '5.5 - 6.5'."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent factual responses
                max_tokens=800
            )
            
            ai_response = response.choices[0].message.content
            if not ai_response:
                raise ValueError("AI response content is empty")
            
            logger.info(f"AI response received for {plant_name}")
            logger.info(f"Raw AI response: {ai_response}")
            
            # Parse the AI response to extract field values
            parsed_values = self._parse_ai_response(ai_response, columns)
            
            logger.info(f"AI determined values for {plant_name}: {parsed_values}")
            return parsed_values
            
        except Exception as e:
            logger.error(f"AI call failed for {plant_name}: {e}")
            raise
    
    def _parse_ai_response(self, ai_response: str, requested_columns: List[str]) -> Dict[str, str]:
        """
        Parse the AI response to extract field values.
        
        Args:
            ai_response: The AI response text
            requested_columns: List of columns that were requested
            
        Returns:
            Dictionary mapping column names to extracted values
        """
        parsed_values = {}
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('**') and ':**' in line:
                # Extract field name and value
                try:
                    field_part = line.split(':**')[0].replace('**', '').strip()
                    value_part = line.split(':**')[1].strip()
                    
                    # Convert field name back to underscore format
                    field_name = field_part.lower().replace(' ', '_')
                    
                    # Handle special cases for pH fields
                    if field_name == 'soil_ph_type':
                        field_name = 'soil_ph_type'
                    elif field_name == 'soil_ph_range':
                        field_name = 'soil_ph_range'
                    
                    # Only include requested columns
                    if field_name in requested_columns and value_part:
                        parsed_values[field_name] = value_part
                        logger.info(f"Parsed {field_name}: {value_part}")
                
                except (IndexError, AttributeError) as e:
                    logger.warning(f"Could not parse line: {line} - {e}")
                    continue
        
        # Check if we got values for all requested columns
        missing_columns = [col for col in requested_columns if col not in parsed_values]
        if missing_columns:
            logger.warning(f"AI response missing values for: {missing_columns}")
        
        return parsed_values
    
    def _prompt_for_plant_value(self, plant_name: str, column: str) -> str:
        """
        Prompt the user for a value for a specific plant and column.
        """
        # Check if we're in auto-only mode (set by the main function)
        if hasattr(self, 'auto_only') and self.auto_only:
            logger.info(f"AUTO-ONLY: Skipping manual fallback for {plant_name} {column}")
            return ''
        
        while True:
            value = input(f"Enter {column} for '{plant_name}' (or 'skip' to leave unchanged): ").strip()
            
            if value.lower() == 'skip':
                return ''
            elif value:
                return value
            else:
                print("Please enter a value or 'skip'")
    
    def update_columns_for_plants(self, columns: List[str], plant_ids: List[str] = None, 
                                 dry_run: bool = False) -> Dict[str, Any]:
        """
        Update specified columns for plants with individual plant-specific values.
        
        Args:
            columns: List of column names to update
            plant_ids: List of specific plant IDs to update (if None, updates all plants)
            dry_run: If True, don't actually make API calls
            
        Returns:
            Summary of update operations
        """
        # Validate columns
        validated_columns = self.validate_columns(columns)
        
        # Get plants to update
        if plant_ids:
            # Fetch actual plant data for the specified IDs
            plants_to_update = []
            for plant_id in plant_ids:
                try:
                    # Get the full plant data from API
                    logger.info(f"Fetching plant data for ID: {plant_id}")
                    self._enforce_rate_limit()
                    # Use the correct endpoint from the schema: /api/plants/get-all-fields/{id}
                    response = self.session.get(f"{self.base_url}/api/plants/get-all-fields/{plant_id}")
                    response.raise_for_status()
                    plant_data = response.json()
                    
                    # Check if we got the plant data successfully
                    if plant_data.get('success') and 'plant' in plant_data:
                        plant_obj = plant_data['plant']
                        # Skip individual row lookup - will be done in batch during optimized update
                        plants_to_update.append(plant_obj)
                        plant_name = plant_obj.get('plant_name', plant_obj.get('Plant Name', 'Unknown'))
                        logger.info(f"Found plant: {plant_name}")
                    else:
                        logger.warning(f"No plant data found for ID: {plant_id}. Response: {plant_data}")
                except Exception as e:
                    logger.error(f"Failed to fetch plant {plant_id}: {e}")
            
            logger.info(f"Successfully fetched {len(plants_to_update)} of {len(plant_ids)} requested plants")
        else:
            all_plants = self.get_all_plants()
            plants_to_update = all_plants
            logger.info(f"Updating all {len(plants_to_update)} plants")
        
        # Perform updates
        results = {
            'successful_updates': 0,
            'failed_updates': 0,
            'skipped_updates': 0,
            'errors': [],
            'updated_plants': [],
            'total_plants': len(plants_to_update)
        }
        
        logger.info(f"Starting OPTIMIZED batch update process for {len(plants_to_update)} plants")
        logger.info(f"Columns to update: {validated_columns}")
        
        # OPTIMIZATION: Collect all plant updates, then batch process them
        plant_updates = {}  # plant_id -> update_data
        
        # Step 1: Determine AI values for all plants (this still requires individual AI calls)
        for i, plant in enumerate(plants_to_update, 1):
            plant_id = plant.get('id') or plant.get('plant_name', f'plant_{i}')
            plant_name = plant.get('plant_name', plant.get('Plant Name', 'Unknown Plant'))
            
            try:
                logger.info(f"Processing plant {i}/{len(plants_to_update)}: {plant_name}")
                
                # Determine individual values for this plant
                plant_values = self.determine_plant_values(plant, validated_columns)
                
                # Filter out empty values (skipped fields)
                update_data = {col: val for col, val in plant_values.items() if val and val.strip()}
                
                if not update_data:
                    logger.info(f"SKIP: No values to update for {plant_name}")
                    results['skipped_updates'] += 1
                    continue
                
                logger.info(f"PREPARED: {plant_name} with {update_data}")
                plant_updates[str(plant_id)] = update_data
                
                # Progress reporting
                if i % 5 == 0 or i == len(plants_to_update):
                    logger.info(f"PROGRESS: {i}/{len(plants_to_update)} plants processed")
                
            except KeyboardInterrupt:
                logger.info("Update process interrupted by user")
                break
            except Exception as e:
                results['failed_updates'] += 1
                error_msg = f"Plant {plant_name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"ERROR: {error_msg}")
        
        # Step 2: Execute optimized batch update for all collected plants
        if plant_updates:
            logger.info(f"Executing OPTIMIZED batch update for {len(plant_updates)} plants...")
            batch_result = self.update_plants_batch_optimized(plant_updates, dry_run)
            
            if batch_result.get('success'):
                # Update results with batch operation success
                updated_count = batch_result.get('updated_count', 0)
                results['successful_updates'] = updated_count
                results['failed_updates'] = len(plant_updates) - updated_count
                
                # Add successfully updated plant names to results
                for plant_id in plant_updates.keys():
                    for plant in plants_to_update:
                        if str(plant.get('id', '')) == plant_id:
                            plant_name = plant.get('plant_name', plant.get('Plant Name', f'Plant {plant_id}'))
                            results['updated_plants'].append(plant_name)
                            break
                
                logger.info(f"BATCH SUCCESS: Updated {updated_count} plants with {batch_result.get('total_api_calls', 2)} API calls")
                logger.info(f"Efficiency gain: {len(plant_updates) * 5} old calls -> {batch_result.get('total_api_calls', 2)} new calls")
            else:
                logger.error(f"BATCH FAILED: {batch_result.get('error', 'Unknown error')}")
                results['failed_updates'] += len(plant_updates)
                results['errors'].append(f"Batch update failed: {batch_result.get('error', 'Unknown error')}")
        else:
            logger.info("No plants to update after AI processing")
        
        # Calculate runtime statistics
        end_time = datetime.now()
        runtime = end_time - self.start_time
        avg_time_per_request = runtime.total_seconds() / self.request_count if self.request_count > 0 else 0
        
        # Summary logging
        logger.info("=" * 60)
        logger.info("UPDATE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total plants processed: {results['total_plants']}")
        logger.info(f"Successful updates: {results['successful_updates']}")
        logger.info(f"Failed updates: {results['failed_updates']}")
        logger.info(f"Skipped updates: {results['skipped_updates']}")
        logger.info(f"Total API requests: {self.request_count}")
        logger.info(f"Total runtime: {runtime}")
        logger.info(f"Average time per request: {avg_time_per_request:.2f}s")
        
        if results['errors']:
            logger.info(f"ERRORS ({len(results['errors'])}):")
            for error in results['errors'][:10]:  # Show first 10 errors
                logger.info(f"  - {error}")
            if len(results['errors']) > 10:
                logger.info(f"  ... and {len(results['errors']) - 10} more errors")
        
        return results
    



def main():
    """
    Main function to handle command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Plant Maintenance Utility - Update plant database columns efficiently",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update all AI-generated fields for all plants (comprehensive update)
  python plant_maintenance_utility.py --columns ai-fields
  
  # Update AI fields for specific plants only
  python plant_maintenance_utility.py --columns ai-fields --plant-ids "67,68,71-75"
  
  # Update soil pH columns for all plants using AI determination
  python plant_maintenance_utility.py --columns soil_ph_type soil_ph_range
  
  # Dry run to see what AI would determine without making changes
  python plant_maintenance_utility.py --columns ai-fields --dry-run
  
  # Auto-only mode: only update with AI, skip manual fallbacks
  python plant_maintenance_utility.py --columns ai-fields --auto-only
  
  # Update specific care columns using AI
  python plant_maintenance_utility.py --columns soil_ph_type soil_ph_range pruning_instructions
        """
    )
    
    parser.add_argument(
        '--columns',
        nargs='+',
        help='Column names to update (use "all" for all columns, "ai-fields" for AI-generated fields only, or specify: soil_ph_type, soil_ph_range, etc.)'
    )
    
    parser.add_argument(
        '--plant-ids',
        type=str,
        help='Plant IDs to update. Supports: individual (67), ranges (67-69), comma-delimited (67,68,71-75)'
    )
    
    parser.add_argument(
        '--auto-only',
        action='store_true',
        help='Only update plants with AI-determined values (skip manual fallback prompts)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making actual changes'
    )
    
    parser.add_argument(
        '--api-key',
        help='API key for authentication (can also use GARDENLLM_API_KEY environment variable)'
    )
    
    parser.add_argument(
        '--rate-limit-delay',
        type=float,
        default=6.5,
        help='Delay between API requests in seconds (default: 6.5s)'
    )
    
    parser.add_argument(
        '--list-columns',
        action='store_true',
        help='List all available column names and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list columns request
    if args.list_columns:
        utility = PlantMaintenanceUtility("dummy_key")  # Just for getting valid columns
        valid_columns = utility.get_valid_columns()
        print("Available columns for updating:")
        for column in sorted(valid_columns):
            print(f"  - {column}")
        print(f"\nTotal: {len(valid_columns)} columns available for updating")
        return
    
    # Check if columns are required when not listing columns
    if not args.columns:
        logger.error("ERROR: --columns argument is required (unless using --list-columns)")
        parser.print_help()
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or os.getenv('GARDENLLM_API_KEY')
    if not api_key:
        logger.error("ERROR: No API key provided. Use --api-key or set GARDENLLM_API_KEY environment variable")
        sys.exit(1)
    
    # Handle auto-only mode
    if args.auto_only:
        logger.info("AUTO-ONLY mode: Will only update plants with AI-determined values (no manual fallbacks)")
    
    try:
        # Initialize utility
        utility = PlantMaintenanceUtility(
            api_key=api_key,
            rate_limit_delay=args.rate_limit_delay
        )
        
        # Set auto-only mode if specified
        if args.auto_only:
            utility.auto_only = True
        
        # Parse plant IDs if provided (supports ranges and comma-delimited)
        parsed_plant_ids = None
        if args.plant_ids:
            try:
                parsed_plant_ids = parse_plant_ids(args.plant_ids)
                logger.info(f"Parsed plant IDs: {parsed_plant_ids}")
            except ValueError as e:
                logger.error(f"Invalid plant ID format: {e}")
                sys.exit(1)
        
        # Perform updates
        results = utility.update_columns_for_plants(
            columns=args.columns,
            plant_ids=parsed_plant_ids,
            dry_run=args.dry_run
        )
        
        # Exit with appropriate code
        if results['failed_updates'] == 0:
            logger.info("SUCCESS: All updates completed successfully")
            sys.exit(0)
        else:
            logger.error(f"ERROR: {results['failed_updates']} updates failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
