import logging
from typing import List, Dict, Optional, Tuple, Union, Any
from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
from utils.sheets_client import check_rate_limit, get_next_id
from models.field_config import get_canonical_field_name, get_all_field_names, is_valid_field
import time

logger = logging.getLogger(__name__)

def upload_and_link_plant_photo(file, plant_id: str, plant_name: str) -> Dict[str, Any]:
    """
    Upload a photo to storage and link it to the plant record in the database.
    
    Args:
        file: The uploaded file object
        plant_id (str): ID of the plant to update
        plant_name (str): Name of the plant for storage organization
        
    Returns:
        Dict containing success status, photo URLs, and update results
    """
    try:
        from .storage_client import upload_plant_photo
        from .plant_database_operations import update_plant
        
        # Upload photo to Google Cloud Storage
        upload_result = upload_plant_photo(file, plant_name)
        
        # Update plant record with photo URLs
        photo_url = upload_result.get('photo_url', '')
        raw_photo_url = upload_result.get('raw_photo_url', '')
        
        update_data = {
            'Photo URL': f'=IMAGE("{photo_url}")' if photo_url and not photo_url.startswith('=IMAGE("') else photo_url,
            'Raw Photo URL': raw_photo_url
        }
        
        db_update_result = update_plant(plant_id, update_data)
        
        return {
            'success': True,
            'message': 'Photo uploaded and linked to plant record',
            'upload_result': upload_result,
            'database_update': db_update_result,
            'photo_url': photo_url,
            'raw_photo_url': raw_photo_url
        }
        
    except Exception as e:
        logger.error(f"Error in upload_and_link_plant_photo: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def migrate_photo_urls():
    """
    Migrates photo URLs from the Photo URL column (which may contain IMAGE formulas)
    to the Raw Photo URL column.
    
    Returns a status message indicating the number of URLs migrated and any errors.
    
    This is a utility function for data migration and maintenance.
    """
    try:
        from .plant_database_operations import get_houston_timestamp
        from .plant_cache_operations import invalidate_plant_list_cache
        
        check_rate_limit()
        
        # Get all plants
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        header = values[0] if values else []
        
        # Find Photo URL and Raw Photo URL columns
        photo_url_field = get_canonical_field_name('Photo URL')
        raw_photo_url_field = get_canonical_field_name('Raw Photo URL')
        
        try:
            photo_col_idx = header.index(photo_url_field)
            raw_photo_col_idx = header.index(raw_photo_url_field)
        except ValueError as e:
            return f"Column not found: {e}"
        
        migrated_count = 0
        errors = []
        
        for i, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
            if len(row) > photo_col_idx:
                photo_url = row[photo_col_idx] if photo_col_idx < len(row) else ''
                raw_photo_url = row[raw_photo_col_idx] if raw_photo_col_idx < len(row) else ''
                
                # Skip if Raw Photo URL already has content
                if raw_photo_url:
                    continue
                
                # Extract URL from IMAGE formula if present
                extracted_url = ''
                if photo_url.startswith('=IMAGE("') and photo_url.endswith('")'):
                    extracted_url = photo_url[8:-2]  # Remove =IMAGE(" and ")
                elif photo_url.startswith('http'):
                    extracted_url = photo_url
                
                # Update Raw Photo URL column if we extracted a URL
                if extracted_url:
                    try:
                        range_name = f'Plants!{chr(65 + raw_photo_col_idx)}{i}'
                        sheets_client.values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=range_name,
                            valueInputOption='USER_ENTERED',
                            body={'values': [[extracted_url]]}
                        ).execute()
                        migrated_count += 1
                        logger.info(f"Migrated photo URL for row {i}: {extracted_url[:50]}...")
                    except Exception as e:
                        error_msg = f"Error updating row {i}: {e}"
                        errors.append(error_msg)
                        logger.error(error_msg)
        
        # Invalidate cache after migration
        invalidate_plant_list_cache()
        
        # Update Last Updated field for tracking
        last_updated_field = get_canonical_field_name('Last Updated')
        if last_updated_field in header:
            timestamp = get_houston_timestamp()
            logger.info(f"Photo URL migration completed at {timestamp}")
        
        if errors:
            return f"Migration completed with {migrated_count} URLs migrated. Errors: {'; '.join(errors)}"
        else:
            return f"Migration completed successfully. {migrated_count} photo URLs migrated to Raw Photo URL column."
    
    except Exception as e:
        logger.error(f"Error during photo URL migration: {e}")
        return f"Migration failed: {str(e)}"

def _generate_ai_care_information(plant_name: str, location: str = "") -> Dict[str, str]:
    """
    Generate comprehensive AI care information for a plant.
    
    Args:
        plant_name (str): Name of the plant to generate care for
        location (str): Location where the plant will be grown
        
    Returns:
        Dict[str, str]: Dictionary with care field names as keys and AI-generated content as values
    """
    logger.info(f"Starting AI care generation for {plant_name} at location: '{location}'")
    
    try:
        from config.config import openai_client
        logger.info("OpenAI client imported successfully")
        
        # Check if OpenAI client is available
        if not openai_client:
            logger.error("OpenAI client is None - OpenAI API key may be missing")
            return {
                'Description': f"A {plant_name} plant suitable for Houston gardening.",
                'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
                'Watering Needs': "Water when soil feels dry to touch",
                'Light Requirements': "Provide appropriate light conditions for plant type"
            }
        
        # Create location context
        location_context = f" in {location}" if location else ""
        location_advice = f"Focus on practical advice for the specified location: {location}. " if location else ""
        
        # Create detailed plant care guide prompt for OpenAI
        prompt = (
            f"Create a detailed plant care guide for {plant_name} in Houston, TX{location_context}. "
            "Include care requirements, growing conditions, and maintenance tips. "
            f"{location_advice}"
            "Provide comprehensive information suitable for a home gardener.\n\n"
            "IMPORTANT: Use EXACTLY the section format shown below with double asterisks and colons:\n"
            "**Description:**\n"
            "**Light:**\n"
            "**Soil:**\n"
            "**Soil pH Type:**\n"
            "**Soil pH Range:**\n"
            "**Watering:**\n"
            "**Temperature:**\n"
            "**Pruning:**\n"
            "**Mulching:**\n"
            "**Fertilizing:**\n"
            "**Winter Care:**\n"
            "**Spacing:**\n"
            "**Care Notes:**"
        )
        
        logger.info(f"Calling OpenAI API for {plant_name}")
        start_time = time.time()
        
        # Get plant care information from OpenAI using GPT-4
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert gardener and plant database manager specializing in Houston, Texas climate. "
                               "Answer as a knowledgeable, friendly assistant. Important: Do not use markdown headers (###). "
                               "For soil pH information: Soil pH Type must be one of: high alkalinity, medium alkalinity, "
                               "slightly alkaline, neutral, slightly acidic, medium acidity, high acidity. "
                               "Soil pH Range must be in format like '5.5 - 6.5' with numerical ranges only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        
        ai_time = time.time() - start_time
        logger.info(f"OpenAI API call completed in {ai_time:.2f} seconds for {plant_name}")
        
        ai_response = response.choices[0].message.content or ""
        logger.info(f"Generated AI care response for {plant_name} (length: {len(ai_response)} chars): {ai_response[:150]}...")
        
        # Parse the care guide response to extract structured data for database storage
        care_details = _parse_care_guide(ai_response)
        
        logger.info(f"Successfully generated AI care information for {plant_name}: {len(care_details)} fields parsed")
        return care_details
        
    except ImportError as e:
        logger.error(f"Import error for OpenAI client: {e}")
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
            'Watering Needs': "Water when soil feels dry to touch",
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }
    except AttributeError as e:
        logger.error(f"OpenAI client attribute error - API key may be invalid: {e}")
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: AI care generation failed due to configuration error. Please research specific care requirements.",
            'Watering Needs': "Water when soil feels dry to touch", 
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }
    except Exception as e:
        logger.error(f"Unexpected error generating AI care information for {plant_name}: {type(e).__name__}: {e}")
        # Return fallback care information if AI generation fails
        return {
            'Description': f"A {plant_name} plant suitable for Houston gardening.",
            'Care Notes': f"Care guide for {plant_name}: Please research specific care requirements for this plant based on Houston's climate and growing conditions.",
            'Watering Needs': "Water when soil feels dry to touch",
            'Light Requirements': "Provide appropriate light conditions for plant type"
        }

def _parse_care_guide(response: str) -> Dict[str, str]:
    """
    Parse the care guide response from OpenAI into a structured dictionary.
    Handles **Section:** headers and maps short names to full field names.
    
    Args:
        response (str): AI response text with section headers
        
    Returns:
        Dict[str, str]: Dictionary mapping field names to care content
    """
    # Mapping from possible section names to spreadsheet field names
    section_map = {
        'Description': 'Description',
        'Light': 'Light Requirements', 
        'Soil': 'Soil Preferences',
        'Soil pH Type': 'Soil pH Type',
        'Soil pH Range': 'Soil pH Range',
        'Watering': 'Watering Needs',
        'Temperature': 'Frost Tolerance',
        'Pruning': 'Pruning Instructions',
        'Mulching': 'Mulching Needs',
        'Fertilizing': 'Fertilizing Schedule',
        'Winter Care': 'Winterizing Instructions',
        'Spacing': 'Spacing Requirements',
        'Care Notes': 'Care Notes'
    }

    care_details = {}
    lines = response.split('\n')
    current_section = None
    current_content = []

    def save_section(section, content):
        """Save the current section content to care_details"""
        if section and content:
            # Extract section name from **Section:** format
            section_name = section.strip('*').strip().rstrip(':').strip()
            field_name = section_map.get(section_name)
            if field_name:
                content_text = '\n'.join(content).strip()
                if content_text:  # Only add non-empty content
                    care_details[field_name] = content_text

    for line in lines:
        line = line.strip()
        # Check if this is a section header (starts and ends with **)
        if line.startswith('**') and line.endswith('**'):
            # Save previous section
            save_section(current_section, current_content)
            # Start new section
            current_section = line
            current_content = []
        elif current_section and line:
            # Add content to current section
            current_content.append(line)
    
    # Save the last section
    save_section(current_section, current_content)
    
    # If no structured content was found, add the full response as care notes
    if not care_details:
        care_details['Care Notes'] = response.strip()
    
    logger.info(f"Parsed care guide into {len(care_details)} fields: {list(care_details.keys())}")
    return care_details

def add_plant_with_fields(plant_data_dict: Dict[str, str]) -> Dict[str, Union[bool, str]]:
    """
    Add a new plant to the database with comprehensive field support.
    
    Args:
        plant_data_dict (Dict[str, str]): Dictionary containing plant field data
        
    Returns:
        Dict[str, Union[bool, str]]: Result with success status, message, and plant ID
    """
    try:
        from .plant_database_operations import get_houston_timestamp
        from .plant_cache_operations import invalidate_plant_list_cache
        
        # Validate that Plant Name is provided
        plant_name_field = get_canonical_field_name('Plant Name')
        plant_name = plant_data_dict.get(plant_name_field) if plant_name_field else None
        if not plant_name:
            return {"success": False, "error": "'Plant Name' is required"}
        
        # Get next available ID
        next_id = get_next_id()
        if not next_id:
            return {"success": False, "error": "Could not generate plant ID"}
        
        # Prepare plant data using field_config
        plant_data = {
            get_canonical_field_name('ID'): next_id,
            get_canonical_field_name('Last Updated'): get_houston_timestamp()
        }
        
        # Process all provided fields
        for field_name, field_value in plant_data_dict.items():
            canonical_field = get_canonical_field_name(field_name)
            if canonical_field:
                if canonical_field == get_canonical_field_name('Photo URL'):
                    # Handle photo URL specially - store both IMAGE formula and raw URL
                    if field_value and not field_value.startswith('=IMAGE("'):
                        photo_formula = f'=IMAGE("{field_value}")' if field_value else ''
                        plant_data[canonical_field] = photo_formula
                        plant_data[get_canonical_field_name('Raw Photo URL')] = field_value
                    else:
                        # Already wrapped, use as-is
                        plant_data[canonical_field] = field_value
                        # Extract raw URL from existing IMAGE formula if needed
                        if field_value.startswith('=IMAGE("') and field_value.endswith('")'):
                            raw_url = field_value[8:-2]  # Remove =IMAGE(" and ")
                            plant_data[get_canonical_field_name('Raw Photo URL')] = raw_url
                else:
                    plant_data[canonical_field] = field_value
        
        # Check if we need to generate AI care information (minimal data provided)
        care_fields_to_check = [
            'Description', 'Light Requirements', 'Watering Needs', 'Soil Preferences',
            'Pruning Instructions', 'Fertilizing Schedule', 'Care Notes'
        ]
        
        provided_care_fields = sum(1 for field in care_fields_to_check 
                                 if get_canonical_field_name(field) in plant_data and 
                                 plant_data[get_canonical_field_name(field)].strip())
        
        # If minimal care information provided (less than 3 care fields), generate AI care
        if provided_care_fields < 3:
            logger.info(f"Generating AI care information for {plant_name} (only {provided_care_fields} care fields provided)")
            try:
                ai_care_data = _generate_ai_care_information(plant_name, plant_data.get(get_canonical_field_name('Location'), ''))
                
                # Merge AI-generated care data with existing data (don't overwrite user-provided fields)
                fields_added = 0
                for field_name, ai_value in ai_care_data.items():
                    canonical_field = get_canonical_field_name(field_name)
                    if canonical_field and (canonical_field not in plant_data or not plant_data[canonical_field].strip()):
                        plant_data[canonical_field] = ai_value
                        fields_added += 1
                
                logger.info(f"AI care generation successful: added {fields_added} care fields for {plant_name}")
                
            except Exception as e:
                logger.error(f"AI care generation failed for {plant_name}, continuing with minimal data: {e}")
                # Continue with whatever data we have - don't fail the entire operation
        
        # Add empty values for all fields not provided
        all_fields = get_all_field_names()
        for field in all_fields:
            if field not in plant_data:
                plant_data[field] = ""
        
        # Convert to list format for Google Sheets
        headers = get_all_field_names()
        row_data = [plant_data.get(field, "") for field in headers]
        
        # Add to sheet
        check_rate_limit()
        sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body={'values': [row_data]}
        ).execute()
        
        # Invalidate cache
        invalidate_plant_list_cache()
        
        logger.info(f"Successfully added plant with comprehensive fields: {plant_name}")
        return {
            "success": True,
            "message": f"Added {plant_name} to garden",
            "plant_id": next_id
        }
        
    except Exception as e:
        logger.error(f"Error adding plant with fields: {e}")
        return {"success": False, "error": str(e)}

def add_test_photo_url():
    """
    Adds a test photo URL to the first plant to verify the migration process.
    
    This is a development/testing utility function.
    """
    try:
        from .plant_database_operations import update_plant_field
        
        test_photo_url = "https://example.com/test-plant-photo.jpg"
        
        # Update the first plant (row 1) with a test photo URL
        success = update_plant_field(1, 'Photo URL', test_photo_url)
        
        if success:
            logger.info(f"Successfully added test photo URL to first plant: {test_photo_url}")
            return f"Test photo URL added successfully: {test_photo_url}"
        else:
            logger.error("Failed to add test photo URL")
            return "Failed to add test photo URL"
            
    except Exception as e:
        logger.error(f"Error adding test photo URL: {e}")
        return f"Error adding test photo URL: {str(e)}"
