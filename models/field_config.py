"""
Centralized field configuration for GardenLLM.
Defines all database field names, user-friendly aliases, field categories, and provides mapping/validation functions.
Every line is documented inline.
"""

from typing import Optional

# List of all database field names as they appear in the Google Sheet
FIELD_NAMES = [
    # Unique identifier for each plant
    'id',
    # The name of the plant (required field)
    'plant_name',
    # Description of the plant
    'description',
    # Location(s) of the plant in the garden
    'location',
    # Light requirements for the plant
    'light_requirements',
    # Frost tolerance information
    'frost_tolerance',
    # Watering needs for the plant
    'watering_needs',
    # Soil preferences for the plant
    'soil_preferences',
    # Soil pH type (high alkalinity, medium alkalinity, slightly alkaline, neutral, slightly acidic, medium acidity, high acidity)
    'soil_ph_type',
    # Soil pH range (e.g., "5.5 - 6.5")
    'soil_ph_range',
    # Pruning instructions for the plant
    'pruning_instructions',
    # Mulching needs for the plant
    'mulching_needs',
    # Fertilizing schedule for the plant
    'fertilizing_schedule',
    # Winterizing instructions for the plant
    'winterizing_instructions',
    # Spacing requirements for the plant
    'spacing_requirements',
    # Additional care notes
    'care_notes',
    # Photo URL (as an IMAGE formula in the sheet)
    'photo_url',
    # Raw Photo URL (direct link to the image)
    'raw_photo_url',
    # Last updated timestamp
    'last_updated',
]

# Plant Log field names as they appear in the Google Sheet
LOG_FIELD_NAMES = [
    # Unique identifier for each log entry (LOG-YYYYMMDD-001 format)
    'log_id',
    # Name of the plant (EXACT match to existing plant database - enforced validation)
    'plant_name',
    # Backup reference to plant ID from main database
    'plant_id',
    # Location where the plant issue occurred (garden area, room, greenhouse, etc.)
    'location',
    # Human-readable log date ("January 15, 2024 at 2:30 PM")
    'log_date',
    # Title for the log entry (auto-generated or user-provided)
    'log_title',
    # Photo URL (uploaded image location as IMAGE formula)
    'photo_url',
    # Raw Photo URL (direct image link)
    'raw_photo_url',
    # GPT-generated plant health diagnosis in journal format
    'diagnosis',
    # GPT-generated treatment recommendations in journal format
    'treatment_recommendation',
    # Combined user and GPT observations of symptoms
    'symptoms_observed',
    # User observations and follow-up comments
    'user_notes',
    # GPT analysis confidence score (0.0-1.0)
    'confidence_score',
    # Type of analysis (health_assessment|identification|general_care|follow_up)
    'analysis_type',
    # Boolean flag indicating if follow-up is required
    'follow-up_required',
    # Date when follow-up should occur
    'follow-up_date',
    # Last updated timestamp for the log entry
    'last_updated',
]

# User-friendly aliases for each field (all lowercased for matching)
FIELD_ALIASES = {
    # ID field aliases
    'id': 'id',
    'identifier': 'id',
    # Plant Name field aliases
    'name': 'plant_name',
    'plant': 'plant_name',
    'plant name': 'plant_name',
    'plant___name': 'plant_name',  # ChatGPT triple underscore pattern
    'plant_name': 'plant_name',    # Single underscore pattern
    # Description field aliases
    'desc': 'description',
    'description': 'description',
    # Location field aliases
    'location': 'location',
    'where': 'location',
    'place': 'location',
    # Light Requirements field aliases
    'light': 'light_requirements',
    'light requirements': 'light_requirements',
    'light___requirements': 'light_requirements',  # ChatGPT triple underscore pattern
    'light_requirements': 'light_requirements',    # Single underscore pattern
    'sun': 'light_requirements',
    'sunlight': 'light_requirements',
    # Frost Tolerance field aliases
    'frost': 'frost_tolerance',
    'frost tolerance': 'frost_tolerance',
    'frost___tolerance': 'frost_tolerance',  # ChatGPT triple underscore pattern
    'frost_tolerance': 'frost_tolerance',    # Single underscore pattern
    'cold': 'frost_tolerance',
    'temperature': 'frost_tolerance',
    # Watering Needs field aliases
    'water': 'watering_needs',
    'watering': 'watering_needs',
    'watering needs': 'watering_needs',
    'watering___needs': 'watering_needs',  # ChatGPT triple underscore pattern
    'watering_needs': 'watering_needs',    # Single underscore pattern
    # Soil Preferences field aliases
    'soil': 'soil_preferences',
    'soil preferences': 'soil_preferences',
    'soil___preferences': 'soil_preferences',  # ChatGPT triple underscore pattern
    'soil_preferences': 'soil_preferences',    # Single underscore pattern
    # Soil pH Type field aliases
    'soil ph type': 'soil_ph_type',
    'soil_ph_type': 'soil_ph_type',
    'soil___ph___type': 'soil_ph_type',  # ChatGPT triple underscore pattern
    'ph type': 'soil_ph_type',
    'soil ph': 'soil_ph_type',
    'ph': 'soil_ph_type',
    'acidity': 'soil_ph_type',
    'alkalinity': 'soil_ph_type',
    # Soil pH Range field aliases
    'soil ph range': 'soil_ph_range',
    'soil_ph_range': 'soil_ph_range',
    'soil___ph___range': 'soil_ph_range',  # ChatGPT triple underscore pattern
    'ph range': 'soil_ph_range',
    'ph level': 'soil_ph_range',
    'ph levels': 'soil_ph_range',
    # Pruning Instructions field aliases
    'prune': 'pruning_instructions',
    'pruning': 'pruning_instructions',
    'pruning instructions': 'pruning_instructions',
    'pruning___instructions': 'pruning_instructions',  # ChatGPT triple underscore pattern
    'pruning_instructions': 'pruning_instructions',    # Single underscore pattern
    # Mulching Needs field aliases
    'mulch': 'mulching_needs',
    'mulching': 'mulching_needs',
    'mulching needs': 'mulching_needs',
    # Fertilizing Schedule field aliases
    'fertilize': 'fertilizing_schedule',
    'fertilizing': 'fertilizing_schedule',
    'fertilizing schedule': 'fertilizing_schedule',
    'fertilizing___schedule': 'fertilizing_schedule',  # ChatGPT triple underscore pattern
    'fertilizing_schedule': 'fertilizing_schedule',    # Single underscore pattern
    # Winterizing Instructions field aliases
    'winter': 'winterizing_instructions',
    'winterizing': 'winterizing_instructions',
    'winterizing instructions': 'winterizing_instructions',
    'winter care': 'winterizing_instructions',
    # Spacing Requirements field aliases
    'spacing': 'spacing_requirements',
    'spacing requirements': 'spacing_requirements',
    'spacing___requirements': 'spacing_requirements',  # ChatGPT triple underscore pattern
    'spacing_requirements': 'spacing_requirements',    # Single underscore pattern
    # Care Notes field aliases
    'notes': 'care_notes',
    'care notes': 'care_notes',
    'care___notes': 'care_notes',  # ChatGPT triple underscore pattern
    'care_notes': 'care_notes',    # Single underscore pattern
    'care instructions': 'care_notes',
    'instructions': 'care_notes',
    # Photo URL field aliases
    'photo': 'photo_url',
    'photo url': 'photo_url',
    'image': 'photo_url',
    'picture': 'photo_url',
    'url': 'photo_url',
    'image url': 'photo_url',
    'photo link': 'photo_url',
    # Raw Photo URL field aliases
    'raw photo url': 'raw_photo_url',
    'direct photo url': 'raw_photo_url',
    'raw image url': 'raw_photo_url',
    # Last Updated field aliases
    'last updated': 'last_updated',
    'updated': 'last_updated',
}

# User-friendly aliases for plant log fields (all lowercased for matching)
LOG_FIELD_ALIASES = {
    # Log ID field aliases
    'log id': 'log_id',
    'id': 'log_id',
    'log_id': 'log_id',
    # Plant Name field aliases (same as main plant fields)
    'name': 'plant_name',
    'plant': 'plant_name',
    'plant name': 'plant_name',
    'plant_name': 'plant_name',
    # Plant ID field aliases
    'plant id': 'plant_id',
    'plant_id': 'plant_id',
    'plantid': 'plant_id',
    # Log Date field aliases
    'date': 'log_date',
    'log date': 'log_date',
    'log_date': 'log_date',
    'timestamp': 'log_date',
    # Log Title field aliases
    'title': 'log_title',
    'log title': 'log_title',
    'log_title': 'log_title',
    # Photo URL field aliases (same as main plant fields)
    'photo': 'photo_url',
    'photo url': 'photo_url',
    'image': 'photo_url',
    'picture': 'photo_url',
    # Raw Photo URL field aliases
    'raw photo url': 'raw_photo_url',
    'raw_photo_url': 'raw_photo_url',
    'direct photo url': 'raw_photo_url',
    'raw image url': 'raw_photo_url',
    # Diagnosis field aliases
    'diagnosis': 'diagnosis',
    'assessment': 'diagnosis',
    'health assessment': 'diagnosis',
    # Treatment Recommendation field aliases
    'treatment': 'treatment_recommendation',
    'treatment recommendation': 'treatment_recommendation',
    'treatment_recommendation': 'treatment_recommendation',
    'recommendation': 'treatment_recommendation',
    'care plan': 'treatment_recommendation',
    # Symptoms Observed field aliases
    'symptoms': 'symptoms_observed',
    'symptoms observed': 'symptoms_observed',
    'symptoms_observed': 'symptoms_observed',
    'observations': 'symptoms_observed',
    # User Notes field aliases
    'notes': 'user_notes',
    'user notes': 'user_notes',
    'user_notes': 'user_notes',
    'comments': 'user_notes',
    'my notes': 'user_notes',
    # Confidence Score field aliases
    'confidence': 'confidence_score',
    'confidence score': 'confidence_score',
    'confidence_score': 'confidence_score',
    'score': 'confidence_score',
    # Analysis Type field aliases
    'type': 'analysis_type',
    'analysis type': 'analysis_type',
    'analysis_type': 'analysis_type',
    'log type': 'analysis_type',
    # Follow-up Required field aliases
    'followup': 'follow_up_required',
    'follow-up': 'follow_up_required',
    'follow-up required': 'follow_up_required',
    'followup_required': 'follow_up_required',
    'follow_up_required': 'follow_up_required',
    'needs followup': 'follow_up_required',
    # Follow-up Date field aliases
    'followup date': 'follow_up_date',
    'follow-up date': 'follow_up_date',
    'followup_date': 'follow_up_date',
    'follow_up_date': 'follow_up_date',
    'next check': 'follow_up_date',
}

# Field categories for organization and validation
FIELD_CATEGORIES = {
    # Basic information fields
    'basic': [
        'id',
        'plant_name',
        'description',
        'location',
    ],
    # Care requirement fields
    'care': [
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
        'care_notes',
    ],
    # Media fields
    'media': [
        'photo_url',
        'raw_photo_url',
    ],
    # Metadata fields
    'metadata': [
        'last_updated',
    ],
}

# Plant Log field categories for organization and validation
LOG_FIELD_CATEGORIES = {
    # Essential identification fields
    'identification': [
        'log_id',
        'plant_name',
        'plant_id',
        'log_date',
        'log_title',
    ],
    # Photo and media fields
    'media': [
        'photo_url',
        'raw_photo_url',
    ],
    # Analysis and diagnosis fields
    'analysis': [
        'diagnosis',
        'treatment_recommendation',
        'symptoms_observed',
        'confidence_score',
        'analysis_type',
    ],
    # User interaction fields
    'user_data': [
        'user_notes',
    ],
    # Follow-up tracking fields
    'followup': [
        'follow_up_required',
        'follow_up_date',
    ],
    # Metadata fields
    'metadata': [
        'last_updated',
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
        required_fields = ['log_id', 'plant_name', 'log_date']
        if field_name in required_fields:
            return False, f"{field_name} is required"
        return True, ""  # Optional fields can be empty
    
    # Validate specific field types
    if field_name == 'confidence_score':
        try:
            score = float(value)
            if not (0.0 <= score <= 1.0):
                return False, "Confidence Score must be between 0.0 and 1.0"
        except ValueError:
            return False, "Confidence Score must be a valid number"
    
    elif field_name == 'analysis_type':
        valid_types = ['health_assessment', 'identification', 'general_care', 'follow_up']
        if value.lower() not in valid_types:
            return False, f"Analysis Type must be one of: {', '.join(valid_types)}"
    
    elif field_name == 'follow_up_required':
        valid_values = ['true', 'false', 'yes', 'no', '1', '0']
        if value.lower() not in valid_values:
            return False, "Follow-up Required must be true/false or yes/no"
    
    elif field_name in ['photo_url', 'raw_photo_url']:
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