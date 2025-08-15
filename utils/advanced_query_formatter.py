"""
Advanced Query Response Formatter Module

Handles formatting of query results into different response formats
(summary, detailed, minimal, ids_only).

Author: Plant Database API
Created: Advanced Filtering System Implementation
"""

from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict

# Import existing operations for context (no modifications)
from utils.locations_operations import get_plant_location_context

logger = logging.getLogger(__name__)

def format_query_response(results: List[Dict], response_format: str, include_fields: List[str]) -> Dict[str, Any]:
    """
    Format query results according to requested format.
    
    Args:
        results: Query results
        response_format: Format type ('summary', 'detailed', 'minimal', 'ids_only')
        include_fields: Fields to include
        
    Returns:
        Dict: Formatted response
    """
    if response_format == 'ids_only':
        return {
            'plant_ids': [str(result.get('plant_id', '')) for result in results],
            'total_matches': len(results)
        }
    
    elif response_format == 'minimal':
        return format_minimal_response(results)
    
    elif response_format == 'summary':
        return format_summary_response(results)
    
    else:  # detailed
        return format_detailed_response(results, include_fields)

def format_minimal_response(results: List[Dict]) -> Dict[str, Any]:
    """
    Create minimal response with basic plant information.
    
    Args:
        results: Query results
        
    Returns:
        Dict: Minimal response
    """
    return {
        'plants': [
            {
                'plant_id': result.get('plant_id'),
                'plant_name': get_plant_name(result.get('plant_data', {})),
                'location': get_location_name(result.get('location_data'))
            }
            for result in results
        ],
        'total_matches': len(results)
    }

def format_summary_response(results: List[Dict]) -> Dict[str, Any]:
    """
    Create summary response with aggregated information.
    
    Args:
        results: Query results
        
    Returns:
        Dict: Summary response
    """
    # Aggregate data
    plant_types = defaultdict(int)
    container_types = defaultdict(int)
    location_groups = defaultdict(int)
    
    sample_plants = []
    
    for i, result in enumerate(results):
        plant_name = get_plant_name(result.get('plant_data', {}))
        plant_types[plant_name] += 1
        
        # Count container types
        containers = result.get('containers', [])
        for container in containers:
            container_info = f"{container.get('container_size', '')} {container.get('container_material', '')}".strip()
            if container_info:
                container_types[container_info] += 1
        
        # Count locations
        location_name = get_location_name(result.get('location_data'))
        if location_name:
            location_groups[location_name] += 1
        
        # Take first 5 as samples
        if i < 5:
            sample_plants.append(create_sample_plant_data(result))
    
    return {
        'total_matches': len(results),
        'summary': {
            'by_plant_type': dict(plant_types),
            'by_container': dict(container_types),
            'by_location': dict(location_groups)
        },
        'sample_plants': sample_plants,
        'response_format': 'summary'
    }

def format_detailed_response(results: List[Dict], include_fields: List[str]) -> Dict[str, Any]:
    """
    Create detailed response with full data.
    
    Args:
        results: Query results
        include_fields: Fields to include
        
    Returns:
        Dict: Detailed response
    """
    detailed_plants = []
    
    for result in results:
        plant_record = {
            'plant_id': result.get('plant_id')
        }
        
        # Include requested data
        if 'plants' in include_fields:
            plant_record['plant_data'] = result.get('plant_data', {})
        
        if 'locations' in include_fields:
            plant_record['location_data'] = result.get('location_data')
        
        if 'containers' in include_fields:
            plant_record['containers'] = result.get('containers', [])
        
        # Add context if requested
        if 'context' in include_fields:
            plant_record['context'] = get_plant_context_safe(result.get('plant_id'))
        
        detailed_plants.append(plant_record)
    
    return {
        'plants': detailed_plants,
        'total_matches': len(results),
        'response_format': 'detailed'
    }

def create_sample_plant_data(result: Dict) -> Dict[str, Any]:
    """
    Create sample plant data for summary responses.
    
    Args:
        result: Query result record
        
    Returns:
        Dict: Sample plant information
    """
    plant_data = result.get('plant_data', {})
    location_data = result.get('location_data', {})
    containers = result.get('containers', [])
    
    return {
        'plant_id': result.get('plant_id'),
        'plant_name': get_plant_name(plant_data),
        'location': get_location_name(location_data),
        'containers': [
            {
                'type': container.get('container_type'),
                'size': container.get('container_size'),
                'material': container.get('container_material')
            }
            for container in containers
        ]
    }

def get_plant_name(plant_data: Dict) -> str:
    """Get plant name from plant data dictionary."""
    return plant_data.get('plant_name') or plant_data.get('Plant Name') or 'Unknown'

def get_location_name(location_data: Optional[Dict]) -> Optional[str]:
    """Get location name from location data dictionary."""
    if not location_data:
        return None
    return location_data.get('location_name')

def get_plant_context_safe(plant_id: str) -> Optional[Dict]:
    """
    Get plant context using existing operations with error handling.
    
    Args:
        plant_id: Plant ID
        
    Returns:
        Optional[Dict]: Plant context data
    """
    try:
        return get_plant_location_context(plant_id)
    except Exception as e:
        logger.warning(f"Could not get context for plant {plant_id}: {e}")
        return None
