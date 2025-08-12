import logging
from typing import List, Dict, Optional, Tuple, Union, Any
from config.config import sheets_client, SPREADSHEET_ID, RANGE_NAME
from utils.sheets_client import check_rate_limit
from models.field_config import get_canonical_field_name
import time

logger = logging.getLogger(__name__)

# Phase 2: Plant List Caching System
_plant_list_cache = {
    'names': [],
    'last_updated': 0,
    'cache_duration': 300  # 5 minutes cache duration
}

def get_plant_names_from_database() -> List[str]:
    """
    Get a list of all plant names from the database.
    
    This function uses caching to improve performance and reduce API calls.
    The cache is invalidated when plants are added or updated.
    
    Returns:
        List[str]: List of plant names currently in the database
    """
    global _plant_list_cache
    
    current_time = time.time()
    cache_duration = 300  # 5 minutes
    
    # Check if cache is still valid
    if (_plant_list_cache['names'] and 
        _plant_list_cache['last_updated'] and 
        current_time - _plant_list_cache['last_updated'] < cache_duration):
        logger.info(f"Returning cached plant list with {len(_plant_list_cache['names'])} plants")
        return _plant_list_cache['names'].copy()
    
    try:
        logger.info("Cache expired, fetching fresh plant list from database")
        check_rate_limit()
        
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) <= 1:
            logger.warning("No plants found in database or only header row present")
            _plant_list_cache['names'] = []
            _plant_list_cache['last_updated'] = current_time
            return []
        
        headers = values[0]
        # Use field_config to get canonical field name
        plant_name_field = get_canonical_field_name('Plant Name')
        name_idx = headers.index(plant_name_field) if plant_name_field in headers else 1
        
        # Extract plant names from all rows except header
        plant_names = []
        for row in values[1:]:
            if len(row) > name_idx and row[name_idx]:
                plant_name = row[name_idx].strip()
                if plant_name:  # Only add non-empty names
                    plant_names.append(plant_name)
        
        # Update cache
        _plant_list_cache['names'] = plant_names
        _plant_list_cache['last_updated'] = current_time
        
        logger.info(f"Updated plant list cache with {len(plant_names)} plants")
        return plant_names.copy()
        
    except Exception as e:
        logger.error(f"Error fetching plant names from database: {e}")
        # Return cached data if available, otherwise empty list
        if _plant_list_cache['names']:
            logger.info("Returning cached plant list due to database error")
            return _plant_list_cache['names'].copy()
        return []

def invalidate_plant_list_cache():
    """
    Invalidate the plant list cache to force a fresh fetch on next request.
    
    This should be called when plants are added, updated, or removed from the database.
    """
    global _plant_list_cache
    _plant_list_cache['last_updated'] = 0
    logger.info("Plant list cache invalidated")

def get_plant_list_cache_info() -> Dict:
    """
    Get information about the current plant list cache status.
    
    Returns:
        Dict: Cache information including count, last updated, and cache duration
    """
    global _plant_list_cache
    current_time = time.time()
    age = current_time - _plant_list_cache['last_updated']
    is_valid = age < _plant_list_cache['cache_duration']
    
    return {
        'plant_count': len(_plant_list_cache['names']),
        'last_updated': _plant_list_cache['last_updated'],
        'cache_age_seconds': age,
        'is_valid': is_valid,
        'cache_duration_seconds': _plant_list_cache['cache_duration']
    } 

def get_location_names_from_database() -> List[str]:
    """
    Get a list of unique location names from the database.
    
    This function extracts all unique location values from the database
    to support location-based queries like "what plants are in the arboretum".
    
    Returns:
        List[str]: List of unique location names from the database
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        # Use field_config to get canonical field name
        location_field = get_canonical_field_name('Location')
        location_idx = headers.index(location_field) if location_field in headers else 3
        
        # Extract all location values
        locations = set()
        for row in values[1:]:
            if len(row) > location_idx and row[location_idx]:
                # Split by comma and clean up each location
                location_parts = row[location_idx].split(',')
                for part in location_parts:
                    location = part.strip()
                    if location:  # Only add non-empty locations
                        locations.add(location)
        
        location_list = sorted(list(locations))
        logger.info(f"Retrieved {len(location_list)} unique locations from database")
        return location_list
        
    except Exception as e:
        logger.error(f"Error getting location names from database: {e}")
        return []

def get_plants_by_location(location_names: List[str]) -> List[Dict]:
    """
    Get plants that are located in any of the specified locations (exact match only).
    Args:
        location_names (List[str]): List of location names to search for
    Returns:
        List[Dict]: List of plant data dictionaries for plants in the specified locations
    """
    try:
        check_rate_limit()
        result = sheets_client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        if not values:
            return []
        headers = values[0]
        location_idx = headers.index('Location') if 'Location' in headers else 3
        matching_plants = []
        location_names_lower = [loc.lower().strip() for loc in location_names]
        for row in values[1:]:
            if len(row) > location_idx and row[location_idx]:
                plant_locations = [loc.strip().lower() for loc in row[location_idx].split(',') if loc.strip()]
                if any(loc in location_names_lower for loc in plant_locations):
                    row_data = row + [''] * (len(headers) - len(row))
                    plant_dict = dict(zip(headers, row_data))
                    matching_plants.append(plant_dict)
        logger.info(f"Found {len(matching_plants)} plants in locations: {location_names}")
        return matching_plants
    except Exception as e:
        logger.error(f"Error getting plants by location: {e}")
        return []

def get_plant_by_id_or_name(id_or_name: str) -> Optional[Dict]:
    """
    Get a single plant by ID or name.
    
    Args:
        id_or_name (str): Plant ID or name to search for
        
    Returns:
        Optional[Dict]: Plant data dictionary if found, None otherwise
    """
    try:
        from .plant_database_operations import find_plant_by_id_or_name
        
        plant_row, plant_data = find_plant_by_id_or_name(id_or_name)
        
        if plant_row and plant_data:
            # Convert plant data list to dictionary using headers
            result = sheets_client.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            headers = result.get('values', [[]])[0]
            
            # Ensure plant_data has enough elements
            plant_data_padded = plant_data + [''] * (len(headers) - len(plant_data))
            plant_dict = dict(zip(headers, plant_data_padded))
            
            return plant_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting plant by ID or name '{id_or_name}': {e}")
        return None

def enhanced_plant_matching(plant_identification: str) -> Dict:
    """
    Enhanced plant matching with fuzzy logic and confidence scoring.
    Matches ChatGPT's plant identification against the user's plant database.
    
    Args:
        plant_identification (str): Plant name identified by ChatGPT
        
    Returns:
        Dict: Matching result with confidence score and database info
    """
    try:
        from .plant_database_operations import get_plant_data, _normalize_plant_name
        
        logger.info(f"Enhanced plant matching for: {plant_identification}")
        
        # Get all plants from the database
        all_plants = get_plant_data()
        
        if not all_plants:
            return {
                'found_in_database': False,
                'confidence': 'low',
                'matched_plant_name': None,
                'database_info': 'No plants found in database',
                'alternatives': []
            }
        
        # Extract plant names for matching
        plant_name_field = get_canonical_field_name('Plant Name')
        plant_names = [plant.get(plant_name_field, '') for plant in all_plants if plant.get(plant_name_field)]
        
        # Find the best match using enhanced fuzzy matching
        best_match = find_best_plant_match(plant_identification, plant_names)
        
        if best_match['found']:
            # Get the matched plant's full data
            matched_plant_data = next(
                (plant for plant in all_plants if plant.get(plant_name_field) == best_match['plant_name']),
                None
            )
            
            return {
                'found_in_database': True,
                'plant_name': best_match['plant_name'],
                'matched_plant_name': best_match['plant_name'], 
                'confidence': best_match['confidence'],
                'match_score': best_match['score'],
                'database_info': f"Exact match found in your plant database",
                'plant_data': matched_plant_data,
                'alternatives': best_match.get('alternatives', [])
            }
        else:
            # No match found - provide suggestions for similar plants
            return {
                'found_in_database': False,
                'plant_name': plant_identification,
                'matched_plant_name': None,
                'confidence': 'low',
                'match_score': 0.0,
                'database_info': f"'{plant_identification}' not found in your plant database",
                'suggestions': best_match.get('alternatives', []),
                'alternatives': best_match.get('alternatives', [])
            }
    
    except Exception as e:
        logger.error(f"Error in enhanced plant matching: {e}")
        return {
            'found_in_database': False,
            'confidence': 'low',
            'matched_plant_name': None,
            'database_info': f'Error during plant matching: {str(e)}',
            'error': str(e)
        }

def find_best_plant_match(search_name: str, plant_names: List[str]) -> Dict:
    """
    Find the best matching plant using fuzzy string matching algorithms.
    
    Args:
        search_name (str): Plant name to search for
        plant_names (List[str]): List of plant names in the database
        
    Returns:
        Dict: Best match result with confidence scoring
    """
    try:
        import difflib
        from .plant_database_operations import _normalize_plant_name
        
        search_normalized = _normalize_plant_name(search_name)
        
        # Track all potential matches with scores
        matches = []
        
        for plant_name in plant_names:
            if not plant_name:
                continue
                
            plant_normalized = _normalize_plant_name(plant_name)
            
            # Method 1: Exact match (highest confidence)
            if search_normalized == plant_normalized:
                matches.append({
                    'plant_name': plant_name,
                    'score': 1.0,
                    'method': 'exact'
                })
                continue
            
            # Method 2: Substring match
            if search_normalized in plant_normalized or plant_normalized in search_normalized:
                # Calculate substring match score
                overlap = max(len(search_normalized), len(plant_normalized))
                min_len = min(len(search_normalized), len(plant_normalized))
                score = min_len / overlap if overlap > 0 else 0
                matches.append({
                    'plant_name': plant_name,
                    'score': score * 0.9,  # Slightly lower than exact match
                    'method': 'substring'
                })
                continue
            
            # Method 3: Word-by-word matching
            search_words = set(search_normalized.split())
            plant_words = set(plant_normalized.split())
            
            if search_words and plant_words:
                # Intersection over union
                intersection = len(search_words.intersection(plant_words))
                union = len(search_words.union(plant_words))
                word_score = intersection / union if union > 0 else 0
                
                if word_score > 0.4:  # At least 40% word overlap
                    matches.append({
                        'plant_name': plant_name,
                        'score': word_score * 0.8,
                        'method': 'word_overlap'
                    })
            
            # Method 4: Fuzzy string matching using difflib
            ratio = difflib.SequenceMatcher(None, search_normalized, plant_normalized).ratio()
            if ratio > 0.6:  # At least 60% similarity
                matches.append({
                    'plant_name': plant_name,
                    'score': ratio * 0.7,
                    'method': 'fuzzy'
                })
        
        # Sort matches by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Determine confidence level based on best match score
        if matches:
            best_score = matches[0]['score']
            if best_score >= 0.9:
                confidence = 'high'
            elif best_score >= 0.7:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            # Get top alternatives (excluding the best match)
            alternatives = [
                {
                    'plant_name': match['plant_name'],
                    'score': match['score'],
                    'method': match['method']
                }
                for match in matches[1:4]  # Top 3 alternatives
                if match['score'] > 0.5
            ]
            
            return {
                'found': best_score >= 0.6,  # Minimum threshold for a match
                'plant_name': matches[0]['plant_name'],
                'score': best_score,
                'confidence': confidence,
                'method': matches[0]['method'],
                'alternatives': alternatives
            }
        else:
            # No matches found, but provide some suggestions based on partial word matches
            suggestions = []
            search_words = search_normalized.split()
            
            for plant_name in plant_names[:10]:  # Check first 10 plants for suggestions
                plant_normalized = _normalize_plant_name(plant_name)
                plant_words = plant_normalized.split()
                
                # Check if any search words appear in plant name
                if any(word in plant_normalized for word in search_words):
                    suggestions.append({
                        'plant_name': plant_name,
                        'score': 0.3,  # Low score for suggestions
                        'method': 'suggestion'
                    })
            
            return {
                'found': False,
                'plant_name': None,
                'score': 0.0,
                'confidence': 'none',
                'alternatives': suggestions[:3]  # Top 3 suggestions
            }
    
    except Exception as e:
        logger.error(f"Error in find_best_plant_match: {e}")
        return {
            'found': False,
            'plant_name': None,
            'score': 0.0,
            'confidence': 'error',
            'error': str(e)
        }
