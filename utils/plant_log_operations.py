"""
Plant Log Operations for the Plant Database API.
Handles CRUD operations for plant log entries with strict plant validation and journal-style formatting.
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any, Tuple
from models.field_config import (
    get_all_log_field_names, 
    validate_log_field_data, 
    generate_log_id, 
    format_log_date,
    get_canonical_log_field_name
)
from utils.sheets_client import check_rate_limit
from config.config import sheets_client, SPREADSHEET_ID, LOG_SHEET_NAME, LOG_RANGE_NAME
from utils.plant_operations import find_plant_by_id_or_name, search_plants
from utils.upload_token_manager import generate_upload_token, generate_upload_url
import re

logger = logging.getLogger(__name__)

def get_houston_timestamp() -> str:
    """
    Get current timestamp in Houston Central Time format.
    
    Returns:
        str: Formatted timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    # Houston, Texas is in Central Time (US/Central)
    central = ZoneInfo('US/Central')
    return datetime.now(central).strftime('%Y-%m-%d %H:%M:%S')

def get_houston_timestamp_iso() -> str:
    """
    Get current timestamp in Houston Central Time ISO format.
    
    Returns:
        str: ISO formatted timestamp string with timezone
    """
    # Houston, Texas is in Central Time (US/Central)
    central = ZoneInfo('US/Central')
    return datetime.now(central).isoformat()

def initialize_log_sheet():
    """Initialize the Plant Log sheet with headers if it doesn't exist"""
    try:
        # Check if Plant_Log sheet exists
        spreadsheet = sheets_client.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        if LOG_SHEET_NAME not in sheet_names:
            # Create the Plant_Log sheet
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': LOG_SHEET_NAME,
                            'sheetType': 'GRID',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': len(get_all_log_field_names())
                            }
                        }
                    }
                }]
            }
            
            sheets_client.batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            
            logger.info(f"Created Plant_Log sheet")
        
        # Set headers if they don't exist
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{LOG_SHEET_NAME}!1:1'
        ).execute()
        
        if not result.get('values'):
            headers = get_all_log_field_names()
            sheets_client.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'{LOG_SHEET_NAME}!1:1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            logger.info("Set Plant_Log sheet headers")
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Plant_Log sheet: {e}")
        return False

def validate_plant_for_log(plant_name: str) -> Dict[str, Any]:
    """
    Validate that a plant exists in the database before creating log entry.
    Uses existing plant_operations.py functions for consistency.
    
    Args:
        plant_name (str): Name of the plant to validate
        
    Returns:
        Dict containing validation results and plant information
    """
    try:
        # Use existing find_plant_by_id_or_name function
        plant_row, plant_data = find_plant_by_id_or_name(plant_name)
        
        if plant_data:
            return {
                "valid": True,
                "plant_id": plant_data[0] if plant_data else None,  # ID from database
                "canonical_name": plant_data[1] if len(plant_data) > 1 else plant_name,  # Canonical plant name
                "plant_row": plant_row,
                "plant_data": plant_data
            }
        else:
            # Try fuzzy matching using existing search functionality
            similar_plants = search_plants(plant_name)
            suggestions = [p.get('plant_name') for p in similar_plants[:5] if p.get('plant_name')]
            
            return {
                "valid": False,
                "suggestions": suggestions,
                "create_new_option": True,
                "plant_name": plant_name
            }
            
    except Exception as e:
        logger.error(f"Error validating plant for log: {e}")
        return {
            "valid": False,
            "error": str(e),
            "suggestions": [],
            "create_new_option": False
        }

def create_log_entry(
    plant_name: str,
    photo_url: str = "",
    raw_photo_url: str = "",
    diagnosis: str = "",
    treatment: str = "",
    symptoms: str = "",
    user_notes: str = "",
    confidence_score: float = 0.0,
    analysis_type: str = "health_assessment",
    follow_up_required: bool = False,
    follow_up_date: str = "",
    log_title: str = "",
    location: str = ""
) -> Dict[str, Any]:
    """
    Create a new plant log entry with optional plant validation.
    
    If plant_name matches an existing plant in the database, the plant_id will be stored.
    If plant_name doesn't exist, the log entry is still created but without a plant_id.
    This allows for group logs like "Citrus plants" or "The trees".
    
    Args:
        plant_name (str): Name of the plant or plant group (required)
        photo_url (str): Photo URL (IMAGE formula for sheets)
        raw_photo_url (str): Direct photo URL
        diagnosis (str): GPT-generated diagnosis
        treatment (str): Treatment recommendations
        symptoms (str): Observed symptoms
        user_notes (str): User observations
        confidence_score (float): Analysis confidence (0.0-1.0)
        analysis_type (str): Type of analysis
        follow_up_required (bool): Whether follow-up needed
        follow_up_date (str): When to follow up
        log_title (str): Title for the log entry
        location (str): Location where the plant issue occurred
        
    Returns:
        Dict containing success status and log entry data
    """
    try:
        # Initialize log sheet if needed
        if not initialize_log_sheet():
            return {"success": False, "error": "Failed to initialize log sheet"}
        
        # Try to validate plant exists, but allow log creation even if not found
        plant_validation = validate_plant_for_log(plant_name)
        
        if plant_validation["valid"]:
            # Plant exists - use canonical name and plant_id from database
            canonical_plant_name = plant_validation["canonical_name"]
            plant_id = plant_validation["plant_id"]
        else:
            # Plant doesn't exist - use provided name and no plant_id
            # This allows group logs like "Citrus plants" or "The trees"
            canonical_plant_name = plant_name
            plant_id = None
        
        # Generate log entry data
        log_id = generate_log_id()
        log_date = format_log_date()
        
        # Auto-generate title if not provided
        if not log_title:
            if diagnosis:
                log_title = "Health Assessment"
            elif analysis_type == "identification":
                log_title = "Plant Identification"
            else:
                log_title = "General Care Log"
        
        # Prepare log entry data (use lowercase_underscore headers for writing to spreadsheet)
        log_data = {
            'log_id': log_id,
            'plant_name': canonical_plant_name,
            'plant_id': str(plant_id) if plant_id else "",
            'location': location,
            'log_date': log_date,
            'log_title': log_title,
            'photo_url': photo_url,
            'raw_photo_url': raw_photo_url,
            'diagnosis': diagnosis,
            'treatment_recommendation': treatment,
            'symptoms_observed': symptoms,
            'user_notes': user_notes,
            'confidence_score': str(confidence_score),
            'analysis_type': analysis_type,
            'follow_up_required': 'TRUE' if follow_up_required else 'FALSE',
            'follow_up_date': follow_up_date,
            'last_updated': get_houston_timestamp_iso()
        }
        
        # Validate all field data
        headers = get_all_log_field_names()
        for field_name in headers:
            value = log_data.get(field_name, "")
            is_valid, error_msg = validate_log_field_data(field_name, value)
            if not is_valid:
                return {"success": False, "error": f"Validation failed for {field_name}: {error_msg}"}
        
        # Prepare row data in correct order
        row_data = [log_data.get(field, "") for field in headers]
        
        # Rate limiting
        check_rate_limit()
        
        # Insert the log entry
        result = sheets_client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=LOG_RANGE_NAME,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row_data]}
        ).execute()
        
        # Generate upload token for photo upload
        upload_token = generate_upload_token(
            plant_name=canonical_plant_name,
            token_type='log_upload',  # Specify token type for log uploads
            log_id=log_id
        )
        upload_url = generate_upload_url(upload_token)
        
        # Return success with log data and upload URL
        return {
            "success": True,
            "message": "Log entry created successfully",
            "log_id": log_id,
            "plant_name": canonical_plant_name,
            "plant_id": plant_id,
            "log_data": log_data,
            "upload_url": upload_url,
            "upload_token": upload_token
        }
        
    except Exception as e:
        logger.error(f"Error creating log entry: {e}")
        return {"success": False, "error": str(e)}

def update_log_entry_photo(log_id: str, photo_url: str, raw_photo_url: str) -> Dict[str, Any]:
    """
    Update an existing log entry with photo URLs after photo upload.
    
    Args:
        log_id (str): The log entry ID to update
        photo_url (str): Photo URL (will be wrapped in IMAGE formula)
        raw_photo_url (str): Direct photo URL
        
    Returns:
        Dict containing success status and update details
    """
    try:
        # Rate limiting
        check_rate_limit()
        
        # Get all log entries to find the row to update
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOG_RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return {"success": False, "error": "No log entries found"}
        
        # Find headers
        headers = values[0] if values else []
        if 'log_id' not in headers:
            return {"success": False, "error": "log_id column not found in sheet"}
        
        # Find the row with matching log ID
        log_id_col = headers.index('log_id')
        photo_url_col = headers.index('photo_url') if 'photo_url' in headers else -1
        raw_photo_url_col = headers.index('raw_photo_url') if 'raw_photo_url' in headers else -1
        last_updated_col = headers.index('last_updated') if 'last_updated' in headers else -1
        
        target_row = None
        for i, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
            if len(row) > log_id_col and row[log_id_col] == log_id:
                target_row = i
                break
        
        if target_row is None:
            return {"success": False, "error": f"Log entry with ID {log_id} not found"}
        
        # Prepare updates
        updates = []
        
        # Update Photo URL if column exists - handle IMAGE formula
        if photo_url_col >= 0:
            # Check if the value is already an IMAGE formula
            if photo_url.startswith('=IMAGE("'):
                formatted_value = photo_url  # Already formatted, use as is
                raw_url_match = re.search(r'=IMAGE\("([^"]+)"\)', photo_url)
                raw_url = raw_url_match.group(1) if raw_url_match else photo_url
            else:
                # Not a formula, wrap it
                formatted_value = f'=IMAGE("{photo_url}")' if photo_url else ''
                raw_url = photo_url
            
            updates.append({
                'range': f'{LOG_SHEET_NAME}!{chr(65 + photo_url_col)}{target_row}',
                'values': [[formatted_value]]
            })
            
            # Update Raw Photo URL if column exists
            if raw_photo_url_col >= 0:
                updates.append({
                    'range': f'{LOG_SHEET_NAME}!{chr(65 + raw_photo_url_col)}{target_row}',
                    'values': [[raw_url]]
                })
        
        # Update Last Updated timestamp
        if last_updated_col >= 0:
            updates.append({
                'range': f'{LOG_SHEET_NAME}!{chr(65 + last_updated_col)}{target_row}',
                'values': [[get_houston_timestamp_iso()]]
            })
        
        if not updates:
            return {"success": False, "error": "No photo URL columns found to update"}
        
        # Perform batch update
        batch_update_body = {
            'valueInputOption': 'USER_ENTERED',
            'data': updates
        }
        
        update_result = sheets_client.values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=batch_update_body
        ).execute()
        
        logger.info(f"Updated log entry {log_id} with photo URLs")
        
        return {
            "success": True,
            "log_id": log_id,
            "message": f"Photo URLs updated for log entry {log_id}",
            "updates_applied": len(updates),
            "sheets_result": update_result
        }
        
    except Exception as e:
        logger.error(f"Failed to update log entry photo: {e}")
        return {"success": False, "error": str(e)}

def get_plant_log_entries(plant_name: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    Get all log entries for a specific plant in chronological order.
    
    Args:
        plant_name (str): Name of the plant
        limit (int): Maximum number of entries to return
        offset (int): Number of entries to skip
        
    Returns:
        Dict containing plant info and log entries
    """
    try:
        # Validate plant exists
        plant_validation = validate_plant_for_log(plant_name)
        if not plant_validation["valid"]:
            return {
                "success": False,
                "error": "Plant not found",
                "suggestions": plant_validation.get("suggestions", [])
            }
        
        canonical_plant_name = plant_validation["canonical_name"]
        
        # Get all log data
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOG_RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return {
                "success": True,
                "plant_name": canonical_plant_name,
                "log_entries": [],
                "total_entries": 0
            }
        
        headers = values[0]
        log_entries = []
        
        # Filter entries for this plant
        for row in values[1:]:  # Skip header row
            if len(row) > 1 and row[1] == canonical_plant_name:  # Plant Name is column 1
                entry = {}
                for i, header in enumerate(headers):
                    # Normalize field names to lowercase_underscore format
                    normalized_header = header.lower().replace(' ', '_').replace('-', '_')
                    entry[normalized_header] = row[i] if i < len(row) else ""
                log_entries.append(entry)
        
        # Sort by log date (newest first)
        log_entries.sort(key=lambda x: x.get('log_date', ''), reverse=True)
        
        # Apply pagination
        total_entries = len(log_entries)
        paginated_entries = log_entries[offset:offset + limit]
        
        return {
            "success": True,
            "plant_name": canonical_plant_name,
            "plant_id": plant_validation["plant_id"],
            "log_entries": paginated_entries,
            "total_entries": total_entries,
            "has_more": offset + limit < total_entries,
            "next_offset": offset + limit if offset + limit < total_entries else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get log entries for {plant_name}: {e}")
        return {"success": False, "error": str(e)}

def get_log_entry_by_id(log_id: str) -> Dict[str, Any]:
    """
    Get a specific log entry by its ID.
    
    Args:
        log_id (str): The log ID to find
        
    Returns:
        Dict containing the log entry or error
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOG_RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return {"success": False, "error": "No log entries found"}
        
        headers = values[0]
        
        # Find the entry with matching log ID
        for row in values[1:]:  # Skip header row
            if len(row) > 0 and row[0] == log_id:  # log_id is column 0
                entry = {}
                for i, header in enumerate(headers):
                    entry[header] = row[i] if i < len(row) else ""
                
                return {
                    "success": True,
                    "log_entry": entry
                }
        
        return {"success": False, "error": f"Log entry {log_id} not found"}
        
    except Exception as e:
        logger.error(f"Failed to get log entry {log_id}: {e}")
        return {"success": False, "error": str(e)}

def format_log_entries_as_journal(log_entries: List[Dict]) -> List[Dict]:
    """
    Format log entries in a human-readable journal style.
    
    Args:
        log_entries (List[Dict]): List of log entries
        
    Returns:
        List[Dict]: Formatted journal entries
    """
    journal_entries = []
    
    for entry in log_entries:
        # Create journal-style formatting
        date = entry.get('log_date', 'Unknown date')
        title = entry.get('log_title', 'Log Entry')
        diagnosis = entry.get('diagnosis', '')
        treatment = entry.get('treatment_recommendation', '')
        symptoms = entry.get('symptoms_observed', '')
        user_notes = entry.get('user_notes', '')
        photo_url = entry.get('raw_photo_url', '')
        confidence = entry.get('confidence_score', '')
        follow_up = entry.get('follow_up_required', 'FALSE')
        follow_up_date = entry.get('follow_up_date', '')
        
        # Build journal entry text
        journal_text = f"{date}\n{title}\n\n"
        
        if photo_url:
            journal_text += f"Photo: {photo_url}\n\n"
        
        if symptoms:
            journal_text += f"What I Observed:\n{symptoms}\n\n"
        
        if user_notes:
            journal_text += f"My Notes:\n{user_notes}\n\n"
        
        if diagnosis:
            confidence_text = ""
            if confidence:
                try:
                    conf_pct = int(float(confidence) * 100)
                    confidence_text = f" (Confidence: {conf_pct}%)"
                except:
                    pass
            journal_text += f"AI Analysis{confidence_text}:\n{diagnosis}\n\n"
        
        if treatment:
            journal_text += f"Recommended Treatment:\n{treatment}\n\n"
        
        if follow_up.upper() == 'TRUE' and follow_up_date:
            journal_text += f"Follow-up: {follow_up_date}\n"
        
        journal_entry = {
            "log_id": entry.get('log_id', ''),
            "date": date,
            "title": title,
            "journal_entry": journal_text.strip(),
            "photo_url": photo_url,
            "confidence_level": confidence,
            "follow_up_required": follow_up.upper() == 'TRUE',
            "follow_up_date": follow_up_date
        }
        
        journal_entries.append(journal_entry)
    
    return journal_entries

def search_log_entries(
    plant_name: Optional[str] = None, 
    query: str = "", 
    symptoms: str = "", 
    date_from: str = "", 
    date_to: str = "",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search log entries with various filters.
    
    Args:
        plant_name (str, optional): Filter by plant name
        query (str): General text search
        symptoms (str): Search in symptoms field
        date_from (str): Start date filter
        date_to (str): End date filter
        limit (int): Maximum results
        
    Returns:
        Dict containing search results
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=LOG_RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return {
                "success": True,
                "search_results": [],
                "total_results": 0
            }
        
        headers = values[0]
        matching_entries = []
        
        for row in values[1:]:  # Skip header row
            if len(row) < len(headers):
                continue
                
            entry = {}
            for i, header in enumerate(headers):
                entry[header] = row[i] if i < len(row) else ""
            
            # Apply filters
            if plant_name and entry.get('plant_name', '').lower() != plant_name.lower():
                continue
            
            if query:
                # Search in all relevant fields including log_id, log_title, plant_name, diagnosis, treatment, symptoms, and notes
                searchable_text = ' '.join([
                    entry.get('log_id', ''),
                    entry.get('log_title', ''),
                    entry.get('plant_name', ''),
                    entry.get('diagnosis', ''),
                    entry.get('treatment_recommendation', ''),
                    entry.get('symptoms_observed', ''),
                    entry.get('user_notes', ''),
                    entry.get('location', '')
                ]).lower()
                
                if query.lower() not in searchable_text:
                    continue
            
            if symptoms and symptoms.lower() not in entry.get('symptoms_observed', '').lower():
                continue
            
            # Add to results
            matching_entries.append(entry)
        
        # Sort by date (newest first)
        matching_entries.sort(key=lambda x: x.get('log_date', ''), reverse=True)
        
        # Apply limit
        limited_results = matching_entries[:limit]
        
        return {
            "success": True,
            "search_results": limited_results,
            "total_results": len(matching_entries),
            "query": query,
            "plant_name": plant_name
        }
        
    except Exception as e:
        logger.error(f"Failed to search log entries: {e}")
        return {"success": False, "error": str(e)}

# ========================================
# API ENDPOINT OPERATIONS (moved from main.py)
# ========================================

def create_plant_log_api():
    """Core plant log creation with multipart support for API endpoints"""
    try:
        from flask import request, jsonify
        from .storage_client import upload_plant_photo, is_storage_available
        from .upload_token_manager import generate_upload_token
        
        # Get form data
        plant_name = request.form.get('plant_name', '').strip()
        user_notes = request.form.get('user_notes', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name is required'}), 400
        
        # Handle file upload
        photo_url = ""
        raw_photo_url = ""
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            if is_storage_available():
                upload_result = upload_plant_photo(file, plant_name)
                photo_url = upload_result['photo_url']
                raw_photo_url = upload_result['raw_photo_url']
        
        # Create log entry
        result = create_log_entry(
            plant_name=plant_name,
            photo_url=photo_url,
            raw_photo_url=raw_photo_url,
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes
        )
        
        if result.get('success'):
            # Generate upload token
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                token_type='log_upload',
                expiration_hours=24
            )
            
            upload_url = f"https://{request.host}/api/photos/upload-for-log/{upload_token}"
            
            return jsonify({
                **result,
                'upload_url': upload_url
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error creating plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_plant_log_simple_api():
    """Simplified plant log creation for API endpoints"""
    try:
        from flask import request, jsonify
        from .field_normalization_middleware import get_normalized_field, get_plant_name
        from .upload_token_manager import generate_upload_token
        
        # Use field normalization
        plant_name = get_plant_name()
        user_notes = get_normalized_field('user_notes', '')
        diagnosis = get_normalized_field('diagnosis', '')
        treatment = get_normalized_field('treatment', '')
        symptoms = get_normalized_field('symptoms', '')
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'Plant name is required'}), 400
        
        # Create log entry (no photo upload here)
        result = create_log_entry(
            plant_name=plant_name,
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=symptoms,
            user_notes=user_notes
        )
        
        if result.get('success'):
            # Generate upload token for optional photo
            upload_token = generate_upload_token(
                log_id=result['log_id'],
                plant_name=plant_name,
                token_type='log_upload',
                expiration_hours=24
            )
            
            upload_url = f"https://{request.host}/api/photos/upload-for-log/{upload_token}"
            
            return jsonify({
                **result,
                'upload_url': upload_url
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error creating simple plant log: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def search_plant_logs_api():
    """Core plant log search logic for API endpoints"""
    try:
        from flask import request, jsonify
        
        plant_name = request.args.get('plant_name', '').strip()
        
        if not plant_name:
            return jsonify({'success': False, 'error': 'plant_name parameter is required'}), 400
        
        logs = get_logs_for_plant(plant_name)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error searching plant logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def upload_photo_to_log_api(token):
    """Core photo upload logic for logs"""
    try:
        from flask import request, jsonify
        from .upload_token_manager import validate_upload_token, mark_token_used
        from .storage_client import upload_plant_photo
        
        # Validate token
        is_valid, token_data, error_message = validate_upload_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message or 'Invalid or expired token'
            }), 401
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Upload photo (use plant_photo function with appropriate identifier)
        # Handle both log upload tokens and plant upload tokens
        if token_data.get('token_type') == 'log_upload':
            identifier = f"log_{token_data['log_id']}"
        else:
            # For plant upload tokens, use plant info
            identifier = token_data.get('plant_name', 'unknown_plant')
        
        result = upload_plant_photo(file, identifier)
        
        # Mark token as used
        mark_token_used(token, request.remote_addr or '')
        
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            **result
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error uploading photo to log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 