"""
Centralized field configuration for GardenLLM.
Defines all database field names, user-friendly aliases, field categories, and provides mapping/validation functions.
Every line is documented inline.
"""

from typing import Optional

# List of all database field names as they appear in the Google Sheet
FIELD_NAMES = [
    # Unique identifier for each plant
    'ID',
    # The name of the plant (required field)
    'Plant Name',
    # Description of the plant
    'Description',
    # Location(s) of the plant in the garden
    'Location',
    # Light requirements for the plant
    'Light Requirements',
    # Frost tolerance information
    'Frost Tolerance',
    # Watering needs for the plant
    'Watering Needs',
    # Soil preferences for the plant
    'Soil Preferences',
    # Soil pH type (alkaline, slightly alkaline, neutral, slightly acidic, acidic)
    'Soil pH Type',
    # Soil pH range (e.g., "5.5 - 6.5")
    'Soil pH Range',
    # Pruning instructions for the plant
    'Pruning Instructions',
    # Mulching needs for the plant
    'Mulching Needs',
    # Fertilizing schedule for the plant
    'Fertilizing Schedule',
    # Winterizing instructions for the plant
    'Winterizing Instructions',
    # Spacing requirements for the plant
    'Spacing Requirements',
    # Additional care notes
    'Care Notes',
    # Photo URL (as an IMAGE formula in the sheet)
    'Photo URL',
    # Raw Photo URL (direct link to the image)
    'Raw Photo URL',
    # Last updated timestamp
    'Last Updated',
]

# Plant Log field names as they appear in the Google Sheet
LOG_FIELD_NAMES = [
    # Unique identifier for each log entry (LOG-YYYYMMDD-001 format)
    'Log ID',
    # Name of the plant (EXACT match to existing plant database - enforced validation)
    'Plant Name',
    # Backup reference to plant ID from main database
    'Plant ID',
    # Location where the plant issue occurred (garden area, room, greenhouse, etc.)
    'Location',
    # Human-readable log date ("January 15, 2024 at 2:30 PM")
    'Log Date',
    # Title for the log entry (auto-generated or user-provided)
    'Log Title',
    # Photo URL (uploaded image location as IMAGE formula)
    'Photo URL',
    # Raw Photo URL (direct image link)
    'Raw Photo URL',
    # GPT-generated plant health diagnosis in journal format
    'Diagnosis',
    # GPT-generated treatment recommendations in journal format
    'Treatment Recommendation',
    # Combined user and GPT observations of symptoms
    'Symptoms Observed',
    # User observations and follow-up comments
    'User Notes',
    # GPT analysis confidence score (0.0-1.0)
    'Confidence Score',
    # Type of analysis (health_assessment|identification|general_care|follow_up)
    'Analysis Type',
    # Boolean flag indicating if follow-up is required
    'Follow-up Required',
    # Date when follow-up should occur
    'Follow-up Date',
    # Last updated timestamp for the log entry
    'Last Updated',
]

# User-friendly aliases for each field (all lowercased for matching)
FIELD_ALIASES = {
    # ID field aliases
    'id': 'ID',
    'identifier': 'ID',
    # Plant Name field aliases
    'name': 'Plant Name',
    'plant': 'Plant Name',
    'plant name': 'Plant Name',
    # Description field aliases
    'desc': 'Description',
    'description': 'Description',
    # Location field aliases
    'location': 'Location',
    'where': 'Location',
    'place': 'Location',
    # Light Requirements field aliases
    'light': 'Light Requirements',
    'light requirements': 'Light Requirements',
    'sun': 'Light Requirements',
    'sunlight': 'Light Requirements',
    # Frost Tolerance field aliases
    'frost': 'Frost Tolerance',
    'frost tolerance': 'Frost Tolerance',
    'cold': 'Frost Tolerance',
    'temperature': 'Frost Tolerance',
    # Watering Needs field aliases
    'water': 'Watering Needs',
    'watering': 'Watering Needs',
    'watering needs': 'Watering Needs',
    # Soil Preferences field aliases
    'soil': 'Soil Preferences',
    'soil preferences': 'Soil Preferences',
    # Soil pH Type field aliases
    'soil ph type': 'Soil pH Type',
    'ph type': 'Soil pH Type',
    'soil ph': 'Soil pH Type',
    'ph': 'Soil pH Type',
    'acidity': 'Soil pH Type',
    'alkalinity': 'Soil pH Type',
    # Soil pH Range field aliases
    'soil ph range': 'Soil pH Range',
    'ph range': 'Soil pH Range',
    'ph level': 'Soil pH Range',
    'ph levels': 'Soil pH Range',
    # Pruning Instructions field aliases
    'prune': 'Pruning Instructions',
    'pruning': 'Pruning Instructions',
    'pruning instructions': 'Pruning Instructions',
    # Mulching Needs field aliases
    'mulch': 'Mulching Needs',
    'mulching': 'Mulching Needs',
    'mulching needs': 'Mulching Needs',
    # Fertilizing Schedule field aliases
    'fertilize': 'Fertilizing Schedule',
    'fertilizing': 'Fertilizing Schedule',
    'fertilizing schedule': 'Fertilizing Schedule',
    # Winterizing Instructions field aliases
    'winter': 'Winterizing Instructions',
    'winterizing': 'Winterizing Instructions',
    'winterizing instructions': 'Winterizing Instructions',
    'winter care': 'Winterizing Instructions',
    # Spacing Requirements field aliases
    'spacing': 'Spacing Requirements',
    'spacing requirements': 'Spacing Requirements',
    # Care Notes field aliases
    'notes': 'Care Notes',
    'care notes': 'Care Notes',
    'care instructions': 'Care Notes',
    'instructions': 'Care Notes',
    # Photo URL field aliases
    'photo': 'Photo URL',
    'photo url': 'Photo URL',
    'image': 'Photo URL',
    'picture': 'Photo URL',
    'url': 'Photo URL',
    'image url': 'Photo URL',
    'photo link': 'Photo URL',
    # Raw Photo URL field aliases
    'raw photo url': 'Raw Photo URL',
    'direct photo url': 'Raw Photo URL',
    'raw image url': 'Raw Photo URL',
    # Last Updated field aliases
    'last updated': 'Last Updated',
    'updated': 'Last Updated',
}

# User-friendly aliases for plant log fields (all lowercased for matching)
LOG_FIELD_ALIASES = {
    # Log ID field aliases
    'log id': 'Log ID',
    'id': 'Log ID',
    'log_id': 'Log ID',
    # Plant Name field aliases (same as main plant fields)
    'name': 'Plant Name',
    'plant': 'Plant Name',
    'plant name': 'Plant Name',
    'plant_name': 'Plant Name',
    # Plant ID field aliases
    'plant id': 'Plant ID',
    'plant_id': 'Plant ID',
    'plantid': 'Plant ID',
    # Log Date field aliases
    'date': 'Log Date',
    'log date': 'Log Date',
    'log_date': 'Log Date',
    'timestamp': 'Log Date',
    # Log Title field aliases
    'title': 'Log Title',
    'log title': 'Log Title',
    'log_title': 'Log Title',
    # Photo URL field aliases (same as main plant fields)
    'photo': 'Photo URL',
    'photo url': 'Photo URL',
    'image': 'Photo URL',
    'picture': 'Photo URL',
    # Raw Photo URL field aliases
    'raw photo url': 'Raw Photo URL',
    'raw_photo_url': 'Raw Photo URL',
    'direct photo url': 'Raw Photo URL',
    'raw image url': 'Raw Photo URL',
    # Diagnosis field aliases
    'diagnosis': 'Diagnosis',
    'assessment': 'Diagnosis',
    'health assessment': 'Diagnosis',
    # Treatment Recommendation field aliases
    'treatment': 'Treatment Recommendation',
    'treatment recommendation': 'Treatment Recommendation',
    'treatment_recommendation': 'Treatment Recommendation',
    'recommendation': 'Treatment Recommendation',
    'care plan': 'Treatment Recommendation',
    # Symptoms Observed field aliases
    'symptoms': 'Symptoms Observed',
    'symptoms observed': 'Symptoms Observed',
    'symptoms_observed': 'Symptoms Observed',
    'observations': 'Symptoms Observed',
    # User Notes field aliases
    'notes': 'User Notes',
    'user notes': 'User Notes',
    'user_notes': 'User Notes',
    'comments': 'User Notes',
    'my notes': 'User Notes',
    # Confidence Score field aliases
    'confidence': 'Confidence Score',
    'confidence score': 'Confidence Score',
    'confidence_score': 'Confidence Score',
    'score': 'Confidence Score',
    # Analysis Type field aliases
    'type': 'Analysis Type',
    'analysis type': 'Analysis Type',
    'analysis_type': 'Analysis Type',
    'log type': 'Analysis Type',
    # Follow-up Required field aliases
    'followup': 'Follow-up Required',
    'follow-up': 'Follow-up Required',
    'follow-up required': 'Follow-up Required',
    'followup_required': 'Follow-up Required',
    'follow_up_required': 'Follow-up Required',
    'needs followup': 'Follow-up Required',
    # Follow-up Date field aliases
    'followup date': 'Follow-up Date',
    'follow-up date': 'Follow-up Date',
    'followup_date': 'Follow-up Date',
    'follow_up_date': 'Follow-up Date',
    'next check': 'Follow-up Date',
}

# Field categories for organization and validation
FIELD_CATEGORIES = {
    # Basic information fields
    'basic': [
        'ID',
        'Plant Name',
        'Description',
        'Location',
    ],
    # Care requirement fields
    'care': [
        'Light Requirements',
        'Frost Tolerance',
        'Watering Needs',
        'Soil Preferences',
        'Soil pH Type',
        'Soil pH Range',
        'Pruning Instructions',
        'Mulching Needs',
        'Fertilizing Schedule',
        'Winterizing Instructions',
        'Spacing Requirements',
        'Care Notes',
    ],
    # Media fields
    'media': [
        'Photo URL',
        'Raw Photo URL',
    ],
    # Metadata fields
    'metadata': [
        'Last Updated',
    ],
}

# Plant Log field categories for organization and validation
LOG_FIELD_CATEGORIES = {
    # Essential identification fields
    'identification': [
        'Log ID',
        'Plant Name',
        'Plant ID',
        'Log Date',
        'Log Title',
    ],
    # Photo and media fields
    'media': [
        'Photo URL',
        'Raw Photo URL',
    ],
    # Analysis and diagnosis fields
    'analysis': [
        'Diagnosis',
        'Treatment Recommendation',
        'Symptoms Observed',
        'Confidence Score',
        'Analysis Type',
    ],
    # User interaction fields
    'user_data': [
        'User Notes',
    ],
    # Follow-up tracking fields
    'followup': [
        'Follow-up Required',
        'Follow-up Date',
    ],
    # Metadata fields
    'metadata': [
        'Last Updated',
    ],
}

# Function to get the canonical field name from an alias
# Returns the canonical field name if found, else None
def get_canonical_field_name(alias: str) -> Optional[str]:
    """Return the canonical field name for a given alias (case-insensitive), or None if not found."""
    # Lowercase the alias for matching
    alias_lc = alias.strip().lower()
    # Check if alias is a direct field name
    if alias_lc in (name.lower() for name in FIELD_NAMES):
        # Return the properly cased field name
        for name in FIELD_NAMES:
            if name.lower() == alias_lc:
                return name
    # Check if alias is in the alias mapping
    return FIELD_ALIASES.get(alias_lc)

# Function to validate if a field name or alias is valid
def is_valid_field(field: str) -> bool:
    """Return True if the field or alias is valid, False otherwise."""
    # Try to get the canonical field name
    return get_canonical_field_name(field) is not None

# Function to get all canonical field names
def get_all_field_names() -> list:
    """Return a list of all canonical field names."""
    return FIELD_NAMES.copy()

# Function to get all aliases for a canonical field name
def get_aliases_for_field(field_name: str) -> list:
    """
    Get all aliases for a given canonical field name.
    
    Args:
        field_name (str): The canonical field name
        
    Returns:
        list: List of aliases for the field
    """
    aliases = []
    for alias, canonical in FIELD_ALIASES.items():
        if canonical == field_name:
            aliases.append(alias)
    return aliases

def get_field_alias(field_name: str) -> str:
    """
    Get the primary user-friendly alias for a given canonical field name.
    
    Args:
        field_name (str): The canonical field name
        
    Returns:
        str: The primary alias for the field, or the field name itself if no alias exists
    """
    # First check if the field name itself is an alias
    if field_name in FIELD_ALIASES:
        return field_name
    
    # Look for aliases that map to this field name
    for alias, canonical in FIELD_ALIASES.items():
        if canonical == field_name:
            return alias
    
    # If no alias found, return the field name itself
    return field_name

# Function to get the category for a field name
def get_field_category(field_name: str) -> Optional[str]:
    """Return the category for a given canonical field name, or None if not found."""
    for category, fields in FIELD_CATEGORIES.items():
        if field_name in fields:
            return category
    return None

# Plant Log field management functions

def get_canonical_log_field_name(alias: str) -> Optional[str]:
    """Return the canonical log field name for a given alias (case-insensitive), or None if not found."""
    # Lowercase the alias for matching
    alias_lc = alias.strip().lower()
    # Check if alias is a direct field name
    if alias_lc in (name.lower() for name in LOG_FIELD_NAMES):
        # Return the properly cased field name
        for name in LOG_FIELD_NAMES:
            if name.lower() == alias_lc:
                return name
    # Check if alias is in the log alias mapping
    return LOG_FIELD_ALIASES.get(alias_lc)

def is_valid_log_field(field: str) -> bool:
    """Return True if the log field or alias is valid, False otherwise."""
    # Try to get the canonical log field name
    return get_canonical_log_field_name(field) is not None

def get_all_log_field_names() -> list:
    """Return a list of all canonical log field names."""
    return LOG_FIELD_NAMES.copy()

def get_log_field_category(field_name: str) -> Optional[str]:
    """Return the category for a given canonical log field name, or None if not found."""
    for category, fields in LOG_FIELD_CATEGORIES.items():
        if field_name in fields:
            return category
    return None

def get_log_aliases_for_field(field_name: str) -> list:
    """
    Get all aliases for a given canonical log field name.
    
    Args:
        field_name (str): The canonical log field name
        
    Returns:
        list: List of aliases for the log field
    """
    aliases = []
    for alias, canonical in LOG_FIELD_ALIASES.items():
        if canonical == field_name:
            aliases.append(alias)
    return aliases

def validate_log_field_data(field_name: str, value: str) -> tuple[bool, str]:
    """
    Validate log field data based on field type and requirements.
    
    Args:
        field_name (str): The canonical log field name
        value (str): The value to validate
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not value or not value.strip():
        # Check required fields
        required_fields = ['Log ID', 'Plant Name', 'Log Date']
        if field_name in required_fields:
            return False, f"{field_name} is required"
        return True, ""  # Optional fields can be empty
    
    # Validate specific field types
    if field_name == 'Confidence Score':
        try:
            score = float(value)
            if not (0.0 <= score <= 1.0):
                return False, "Confidence Score must be between 0.0 and 1.0"
        except ValueError:
            return False, "Confidence Score must be a valid number"
    
    elif field_name == 'Analysis Type':
        valid_types = ['health_assessment', 'identification', 'general_care', 'follow_up']
        if value.lower() not in valid_types:
            return False, f"Analysis Type must be one of: {', '.join(valid_types)}"
    
    elif field_name == 'Follow-up Required':
        valid_values = ['true', 'false', 'yes', 'no', '1', '0']
        if value.lower() not in valid_values:
            return False, "Follow-up Required must be true/false or yes/no"
    
    elif field_name in ['Photo URL', 'Raw Photo URL']:
        # Basic URL validation - should start with http:// or https://
        if not (value.startswith('http://') or value.startswith('https://') or value.startswith('=IMAGE(')):
            return False, f"{field_name} must be a valid URL or IMAGE formula"
    
    return True, ""

def generate_log_id() -> str:
    """
    Generate a unique log ID in the format LOG-YYYYMMDD-001.
    
    Returns:
        str: Generated log ID
    """
    from datetime import datetime
    
    # Get current date in YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    
    # For now, use a simple incrementing number
    # In a real implementation, you'd check existing log IDs to get the next number
    import time
    # Use timestamp seconds as a simple unique identifier
    sequence = str(int(time.time()) % 1000).zfill(3)
    
    return f"LOG-{date_str}-{sequence}"

def format_log_date(dt=None) -> str:
    """
    Format a datetime as a human-readable log date.
    
    Args:
        dt: datetime object, defaults to current time
        
    Returns:
        str: Formatted date string like "January 15, 2024 at 2:30 PM"
    """
    from datetime import datetime
    
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime("%B %d, %Y at %I:%M %p") 