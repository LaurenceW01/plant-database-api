import logging
from typing import Dict
from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
from utils.sheets_client import check_rate_limit
from models.field_config import get_canonical_field_name, get_all_field_names

logger = logging.getLogger(__name__)

def update_plant_legacy(plant_data: Dict) -> bool:
    """Update or add a plant in the Google Sheet (legacy function)"""
    try:
        from .plant_database_operations import get_houston_timestamp
        
        check_rate_limit()
        logger.info("Starting plant update process")
        logger.info(f"Plant data received: {plant_data}")
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        header = values[0] if values else []
        
        # Use field_config to get canonical field names
        plant_name_field = get_canonical_field_name('plant_name')
        plant_name = plant_data.get(plant_name_field)
        plant_row = None
        
        if plant_name:
            for i, row in enumerate(values[1:], start=1):
                if len(row) > 1 and row[1].lower() == plant_name.lower():
                    plant_row = i
                    break
        
        # Handle photo URLs - store both the IMAGE formula and raw URL
        photo_url_field = get_canonical_field_name('photo_url')
        photo_url = plant_data.get(photo_url_field, '')
        photo_formula = f'=IMAGE("{photo_url}")' if photo_url else ''
        raw_photo_url = photo_url  # Store the raw URL directly
        
        # Use Houston Central Time for consistent timestamps
        timestamp = get_houston_timestamp()
        
        field_names = get_all_field_names()
        new_row = []
        
        for field_name in field_names:
            if field_name == get_canonical_field_name('id'):
                new_row.append(str(len(values) if plant_row is None else values[plant_row][0]))
            elif field_name == photo_url_field:
                new_row.append(photo_formula)  # Photo URL as image formula
            elif field_name == get_canonical_field_name('raw_photo_url'):
                new_row.append(raw_photo_url)  # Raw Photo URL stored directly
            elif field_name == get_canonical_field_name('last_updated'):
                new_row.append(timestamp)
            else:
                new_row.append(plant_data.get(field_name, ''))
        
        try:
            if plant_row is not None:
                range_name = f'Plants!A{plant_row + 1}:Q{plant_row + 1}'
                result = sheets_client.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body={'values': [new_row]}
                ).execute()
            else:
                result = sheets_client.values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range='Plants!A1:Q',
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [new_row]}
                ).execute()
            
            # Phase 2: Invalidate cache after plant update
            from utils.plant_cache_operations import invalidate_plant_list_cache
            invalidate_plant_list_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Sheet API error: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating plant: {e}")
        return False
