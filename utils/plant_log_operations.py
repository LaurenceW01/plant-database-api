"""
Plant Log Operations for the Plant Database API.
Handles CRUD operations for plant log entries with strict plant validation and journal-style formatting.
"""

import logging
from datetime import datetime, timedelta
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

logger = logging.getLogger(__name__)

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
            suggestions = [p.get('Plant Name') for p in similar_plants[:5] if p.get('Plant Name')]
            
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
    log_title: str = ""
) -> Dict[str, Any]:
    """
    Create a new plant log entry with strict plant validation.
    
    Args:
        plant_name (str): Name of the plant (must exist in database)
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
        
    Returns:
        Dict containing success status and log entry data
    """
    try:
        # Initialize log sheet if needed
        if not initialize_log_sheet():
            return {"success": False, "error": "Failed to initialize log sheet"}
        
        # Validate plant exists
        plant_validation = validate_plant_for_log(plant_name)
        if not plant_validation["valid"]:
            return {
                "success": False, 
                "error": "Plant not found in database",
                "suggestions": plant_validation.get("suggestions", []),
                "create_new_option": plant_validation.get("create_new_option", False)
            }
        
        # Use canonical plant name from validation
        canonical_plant_name = plant_validation["canonical_name"]
        plant_id = plant_validation["plant_id"]
        
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
        
        # Prepare log entry data
        log_data = {
            'Log ID': log_id,
            'Plant Name': canonical_plant_name,
            'Plant ID': str(plant_id) if plant_id else "",
            'Log Date': log_date,
            'Log Title': log_title,
            'Photo URL': photo_url,
            'Raw Photo URL': raw_photo_url,
            'Diagnosis': diagnosis,
            'Treatment Recommendation': treatment,
            'Symptoms Observed': symptoms,
            'User Notes': user_notes,
            'Confidence Score': str(confidence_score),
            'Analysis Type': analysis_type,
            'Follow-up Required': 'TRUE' if follow_up_required else 'FALSE',
            'Follow-up Date': follow_up_date,
            'Last Updated': datetime.now().isoformat()
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
        
        logger.info(f"Created log entry {log_id} for plant {canonical_plant_name}")
        
        return {
            "success": True,
            "log_entry": log_data,
            "log_id": log_id,
            "plant_name": canonical_plant_name,
            "sheets_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create log entry: {e}")
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
                    entry[header] = row[i] if i < len(row) else ""
                log_entries.append(entry)
        
        # Sort by log date (newest first)
        log_entries.sort(key=lambda x: x.get('Log Date', ''), reverse=True)
        
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
            if len(row) > 0 and row[0] == log_id:  # Log ID is column 0
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
        date = entry.get('Log Date', 'Unknown date')
        title = entry.get('Log Title', 'Log Entry')
        diagnosis = entry.get('Diagnosis', '')
        treatment = entry.get('Treatment Recommendation', '')
        symptoms = entry.get('Symptoms Observed', '')
        user_notes = entry.get('User Notes', '')
        photo_url = entry.get('Raw Photo URL', '')
        confidence = entry.get('Confidence Score', '')
        follow_up = entry.get('Follow-up Required', 'FALSE')
        follow_up_date = entry.get('Follow-up Date', '')
        
        # Build journal entry text
        journal_text = f"📅 {date}\n🌱 {title}\n\n"
        
        if photo_url:
            journal_text += f"📸 Photo: {photo_url}\n\n"
        
        if symptoms:
            journal_text += f"🔍 What I Observed:\n{symptoms}\n\n"
        
        if user_notes:
            journal_text += f"📝 My Notes:\n{user_notes}\n\n"
        
        if diagnosis:
            confidence_text = ""
            if confidence:
                try:
                    conf_pct = int(float(confidence) * 100)
                    confidence_text = f" (Confidence: {conf_pct}%)"
                except:
                    pass
            journal_text += f"🤖 AI Analysis{confidence_text}:\n{diagnosis}\n\n"
        
        if treatment:
            journal_text += f"💡 Recommended Treatment:\n{treatment}\n\n"
        
        if follow_up.upper() == 'TRUE' and follow_up_date:
            journal_text += f"📅 Follow-up: {follow_up_date}\n"
        
        journal_entry = {
            "log_id": entry.get('Log ID', ''),
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
    plant_name: str = None, 
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
                "total_matches": 0
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
            if plant_name and entry.get('Plant Name', '').lower() != plant_name.lower():
                continue
            
            if query:
                # Search in diagnosis, treatment, symptoms, and notes
                searchable_text = ' '.join([
                    entry.get('Diagnosis', ''),
                    entry.get('Treatment Recommendation', ''),
                    entry.get('Symptoms Observed', ''),
                    entry.get('User Notes', '')
                ]).lower()
                
                if query.lower() not in searchable_text:
                    continue
            
            if symptoms and symptoms.lower() not in entry.get('Symptoms Observed', '').lower():
                continue
            
            # Add to results
            matching_entries.append(entry)
        
        # Sort by date (newest first)
        matching_entries.sort(key=lambda x: x.get('Log Date', ''), reverse=True)
        
        # Apply limit
        limited_results = matching_entries[:limit]
        
        return {
            "success": True,
            "search_results": limited_results,
            "total_matches": len(matching_entries),
            "query": query,
            "plant_name": plant_name
        }
        
    except Exception as e:
        logger.error(f"Failed to search log entries: {e}")
        return {"success": False, "error": str(e)} 