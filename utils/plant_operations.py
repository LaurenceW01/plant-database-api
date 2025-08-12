# Streamlined plant_operations.py - now imports from split modules for backward compatibility
# NO FUNCTIONALITY CHANGES - only reorganization and imports

# Import all functions from the split modules to maintain backward compatibility
from .plant_database_operations import (
    get_houston_timestamp,
    get_all_plants,
    _normalize_plant_name,
    _plant_names_match,
    get_plant_data,
    find_plant_by_id_or_name,
    update_plant,
    update_plant_field,
    add_plant
)

from .plant_legacy_operations import (
    update_plant_legacy
)

from .plant_search_operations import (
    search_plants
)

from .plant_api_operations import (
    add_plant_api,
    update_plant_api,
    list_or_search_plants_api,
    get_plant_details_api,
    upload_photo_to_plant_api,
    get_plants
)

from .plant_photo_operations import (
    upload_and_link_plant_photo,
    migrate_photo_urls,
    _generate_ai_care_information,
    _parse_care_guide,
    add_plant_with_fields,
    add_test_photo_url
)

from .plant_cache_operations import (
    get_plant_names_from_database,
    invalidate_plant_list_cache,
    get_plant_list_cache_info,
    get_location_names_from_database,
    get_plants_by_location,
    enhanced_plant_matching,
    find_best_plant_match,
    get_plant_by_id_or_name
)

# Re-export the cache variable for backward compatibility
from .plant_cache_operations import _plant_list_cache

# All functions are now available through their original imports
# Example: from utils.plant_operations import add_plant_api, get_all_plants, etc.
# This maintains 100% backward compatibility while organizing code into logical modules.
