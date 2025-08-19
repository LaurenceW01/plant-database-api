"""
Plant Maintenance Operations Module

Main orchestrator for plant maintenance operations including moving plants between locations,
updating container details, and synchronizing with the main plant spreadsheet.

Author: Plant Database API
Created: v4.0.0 - Plant Maintenance Feature Implementation
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from utils.container_operations import (
    get_containers_for_plant,
    get_container_by_plant_and_location,
    update_container,
    add_container,
    remove_container,
    get_plant_locations_from_containers
)
from utils.plant_database_operations import update_plant, find_plant_by_id_or_name
from utils.locations_database_operations import get_all_locations

# Set up logging for this module
logger = logging.getLogger(__name__)

def process_plant_maintenance(
    plant_name: str,
    destination_location: Optional[str] = None,
    source_location: Optional[str] = None,
    container_size: Optional[str] = None,
    container_type: Optional[str] = None,
    container_material: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for plant maintenance operations.
    Handles plant moves, location additions/removals, and container updates.
    
    Args:
        plant_name (str): Exact plant name from AI
        destination_location (Optional[str]): New location name (null/empty for removal or container only change)
        source_location (Optional[str]): Current location (for ambiguity resolution or container change)
        container_size (Optional[str]): New container size
        container_type (Optional[str]): New container type
        container_material (Optional[str]): New container material
        
    Returns:
        Dict[str, Any]: Result dictionary with success status, data, or error information
    """
    try:
        logger.info(f"Processing plant maintenance for '{plant_name}'")
        logger.info(f"Parameters: destination='{destination_location}', source='{source_location}', "
                   f"size='{container_size}', type='{container_type}', material='{container_material}'")
        
        # Step 1: Validate the maintenance request
        validation_result = validate_maintenance_request(
            plant_name, destination_location, source_location,
            container_size, container_type, container_material
        )
        
        if not validation_result['success']:
            return validation_result
        
        # Step 2: Check for ambiguity in location matching
        ambiguity_result = detect_ambiguity(plant_name, destination_location, source_location)
        
        if not ambiguity_result['success']:
            return ambiguity_result
        
        # Step 3: Execute the maintenance operation
        execution_result = execute_maintenance(
            plant_name, destination_location, source_location,
            container_size, container_type, container_material
        )
        
        if not execution_result['success']:
            return execution_result
        
        # Step 4: Update the main plant spreadsheet location column
        sync_result = sync_plant_locations(plant_name)
        
        if not sync_result['success']:
            logger.warning(f"Failed to sync plant locations for '{plant_name}': {sync_result.get('error', 'Unknown error')}")
            # Don't fail the entire operation for sync issues, but log the warning
        
        logger.info(f"Successfully completed plant maintenance for '{plant_name}'")
        
        return {
            'success': True,
            'message': 'Plant maintenance completed successfully',
            'data': {
                'plant_name': plant_name,
                'old_locations': execution_result.get('old_locations', []),
                'new_locations': execution_result.get('new_locations', []),
                'container_updates': execution_result.get('container_updates', {}),
                'operation_type': execution_result.get('operation_type', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing plant maintenance for '{plant_name}': {e}")
        return {
            'success': False,
            'error': f'Internal error: {str(e)}'
        }

def validate_maintenance_request(
    plant_name: str,
    destination_location: Optional[str],
    source_location: Optional[str],
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """
    Validate the maintenance request parameters.
    
    Args:
        plant_name (str): Name of the plant
        destination_location (Optional[str]): Destination location name
        source_location (Optional[str]): Source location name
        container_size (Optional[str]): Container size
        container_type (Optional[str]): Container type
        container_material (Optional[str]): Container material
        
    Returns:
        Dict[str, Any]: Validation result with success status
    """
    try:
        # Validate plant name is provided and not empty
        if not plant_name or not plant_name.strip():
            return {
                'success': False,
                'error': 'Plant name is required'
            }
        
        # Validate that plant exists in the system
        plant_row, plant_data = find_plant_by_id_or_name(plant_name.strip())
        if not plant_row:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in system'
            }
        
        # Validate that at least one operation is specified
        has_location_change = bool(
            (destination_location and destination_location.strip()) or  # Add/move to destination
            (source_location and source_location.strip() and not destination_location)  # Remove from source
        )
        has_container_update = any([
            container_size and container_size.strip(),
            container_type and container_type.strip(),
            container_material and container_material.strip()
        ])
        
        if not has_location_change and not has_container_update:
            return {
                'success': False,
                'error': 'At least one operation must be specified (location change or container update)'
            }
        
        # Validate locations exist if specified
        if destination_location and destination_location.strip():
            if not _location_exists(destination_location.strip()):
                return {
                    'success': False,
                    'error': f'Destination location "{destination_location}" not found'
                }
        
        if source_location and source_location.strip():
            if not _location_exists(source_location.strip()):
                return {
                    'success': False,
                    'error': f'Source location "{source_location}" not found'
                }
        
        logger.info(f"Validation successful for plant '{plant_name}'")
        
        return {
            'success': True,
            'message': 'Validation passed'
        }
        
    except Exception as e:
        logger.error(f"Error validating maintenance request: {e}")
        return {
            'success': False,
            'error': f'Validation error: {str(e)}'
        }

def detect_ambiguity(
    plant_name: str,
    destination_location: Optional[str],
    source_location: Optional[str]
) -> Dict[str, Any]:
    """
    Check for multiple location matches and ambiguity scenarios.
    
    Args:
        plant_name (str): Name of the plant
        destination_location (Optional[str]): Destination location name
        source_location (Optional[str]): Source location name
        
    Returns:
        Dict[str, Any]: Ambiguity check result with options if ambiguous
    """
    try:
        # Get all containers for the plant to check current locations
        plant_containers = get_containers_for_plant(plant_name)
        
        if not plant_containers:
            # No existing containers - this is valid for adding new locations
            return {
                'success': True,
                'message': 'No existing containers found - ready for new container creation'
            }
        
        # Check for partial string matches in destination location
        # Skip this check if source location is provided, as it resolves ambiguity
        if destination_location and destination_location.strip() and not source_location:
            partial_matches = _find_partial_location_matches(destination_location.strip())
            if len(partial_matches) > 1:
                return {
                    'success': False,
                    'error': 'Multiple locations found',
                    'options': {
                        'locations': partial_matches,
                        'message': f'Please specify which location you mean by "{destination_location}"'
                    }
                }
        
        # Check if plant exists in multiple locations and no source specified
        if len(plant_containers) > 1 and not source_location:
            # Get location names for the plant's containers
            location_ids = [container.get('location_id', '') for container in plant_containers]
            all_locations = get_all_locations()
            location_map = {str(loc.get('location_id', '')): loc.get('location_name', '') 
                           for loc in all_locations}
            
            current_locations = [location_map.get(loc_id, f'Location ID {loc_id}') 
                               for loc_id in location_ids if loc_id]
            
            if destination_location and destination_location.strip():
                # Check if plant already exists in the destination location
                destination_location_id = None
                for location in all_locations:
                    if location.get('location_name', '').strip().lower() == destination_location.strip().lower():
                        destination_location_id = str(location.get('location_id', ''))
                        break
                
                # Check if plant already has a container in the destination
                plant_in_destination = any(str(container.get('location_id', '')) == destination_location_id 
                                         for container in plant_containers)
                
                if plant_in_destination:
                    # Plant already exists in destination - this is an update, need source location
                    return {
                        'success': False,
                        'error': 'Plant exists in multiple locations',
                        'options': {
                            'locations': current_locations,
                            'message': f'Plant "{plant_name}" exists in multiple locations including "{destination_location}". Please specify source location for updates.'
                        }
                    }
                else:
                    # Plant doesn't exist in destination - this is an "add to new location" operation, allow it
                    logger.info(f"Plant '{plant_name}' will be added to new location '{destination_location}'")
                    pass  # Continue with add operation
        
        logger.info(f"No ambiguity detected for plant '{plant_name}'")
        
        return {
            'success': True,
            'message': 'No ambiguity detected'
        }
        
    except Exception as e:
        logger.error(f"Error detecting ambiguity: {e}")
        return {
            'success': False,
            'error': f'Ambiguity detection error: {str(e)}'
        }

def execute_maintenance(
    plant_name: str,
    destination_location: Optional[str],
    source_location: Optional[str],
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """
    Execute the maintenance operation (move, add, remove, or update).
    
    Args:
        plant_name (str): Name of the plant
        destination_location (Optional[str]): Destination location name
        source_location (Optional[str]): Source location name
        container_size (Optional[str]): Container size
        container_type (Optional[str]): Container type
        container_material (Optional[str]): Container material
        
    Returns:
        Dict[str, Any]: Execution result with operation details
    """
    try:
        # Get current plant locations for comparison
        old_locations = get_plant_locations_from_containers(plant_name)
        
        # Determine operation type based on parameters
        if destination_location and destination_location.strip():
            if source_location and source_location.strip():
                # Move operation: move from source to destination
                result = _execute_move_operation(
                    plant_name, source_location.strip(), destination_location.strip(),
                    container_size, container_type, container_material
                )
            else:
                # Add operation: add new location
                result = _execute_add_operation(
                    plant_name, destination_location.strip(),
                    container_size, container_type, container_material
                )
        elif source_location and source_location.strip():
            # Check if container updates are provided
            has_container_updates = any([
                container_size and container_size.strip(),
                container_type and container_type.strip(),
                container_material and container_material.strip()
            ])
            
            if has_container_updates:
                # Update in place operation: update container at source location
                result = _execute_update_in_place_operation(
                    plant_name, source_location.strip(),
                    container_size, container_type, container_material
                )
            else:
                # Remove operation: remove from source location
                result = _execute_remove_operation(plant_name, source_location.strip())
        else:
            # Container update only: update existing containers
            result = _execute_container_update_operation(
                plant_name, container_size, container_type, container_material
            )
        
        if not result['success']:
            return result
        
        # Get new plant locations after operation
        new_locations = get_plant_locations_from_containers(plant_name)
        
        logger.info(f"Maintenance execution successful for '{plant_name}': {old_locations} -> {new_locations}")
        
        return {
            'success': True,
            'old_locations': old_locations,
            'new_locations': new_locations,
            'container_updates': result.get('container_updates', {}),
            'operation_type': result.get('operation_type', 'unknown'),
            'details': result.get('details', {})
        }
        
    except Exception as e:
        logger.error(f"Error executing maintenance operation: {e}")
        return {
            'success': False,
            'error': f'Execution error: {str(e)}'
        }

def sync_plant_locations(plant_name: str) -> Dict[str, Any]:
    """
    Update the main plant spreadsheet location column with comma-separated location names
    derived from container records.
    
    Args:
        plant_name (str): Name of the plant to sync
        
    Returns:
        Dict[str, Any]: Sync result with success status
    """
    try:
        # Get current locations from containers
        location_names = get_plant_locations_from_containers(plant_name)
        
        # Create comma-separated location string
        location_string = ', '.join(location_names) if location_names else ''
        
        # Find the plant in the main spreadsheet
        plant_row, plant_data = find_plant_by_id_or_name(plant_name)
        if not plant_row:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in main spreadsheet'
            }
        
        # Update the location field in the main plant spreadsheet
        update_data = {'location': location_string}
        update_result = update_plant(plant_data[0], update_data)  # plant_data[0] should be the plant ID
        
        if not update_result.get('success', False):
            return {
                'success': False,
                'error': f'Failed to update plant location: {update_result.get("error", "Unknown error")}'
            }
        
        logger.info(f"Successfully synced locations for plant '{plant_name}': '{location_string}'")
        
        return {
            'success': True,
            'message': f'Plant locations synced successfully',
            'location_string': location_string
        }
        
    except Exception as e:
        logger.error(f"Error syncing plant locations for '{plant_name}': {e}")
        return {
            'success': False,
            'error': f'Sync error: {str(e)}'
        }

# Helper functions

def _location_exists(location_name: str) -> bool:
    """Check if a location exists in the locations database."""
    try:
        all_locations = get_all_locations()
        normalized_name = location_name.strip().lower()
        
        for location in all_locations:
            if location.get('location_name', '').strip().lower() == normalized_name:
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if location exists: {e}")
        return False

def _find_partial_location_matches(partial_name: str) -> List[str]:
    """Find locations that partially match the given name."""
    try:
        all_locations = get_all_locations()
        normalized_partial = partial_name.strip().lower()
        
        matches = []
        for location in all_locations:
            location_name = location.get('location_name', '').strip()
            if normalized_partial in location_name.lower():
                matches.append(location_name)
        
        return matches
        
    except Exception as e:
        logger.error(f"Error finding partial location matches: {e}")
        return []

def _execute_move_operation(
    plant_name: str,
    source_location: str,
    destination_location: str,
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """Execute a move operation from source to destination location."""
    try:
        # Find the existing container in the source location
        source_container = get_container_by_plant_and_location(plant_name, source_location)
        if not source_container:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in source location "{source_location}"'
            }
        
        # Get destination location ID
        all_locations = get_all_locations()
        destination_location_id = None
        for location in all_locations:
            if location.get('location_name', '').strip().lower() == destination_location.lower():
                destination_location_id = location.get('location_id', '')
                break
        
        if not destination_location_id:
            return {
                'success': False,
                'error': f'Destination location "{destination_location}" not found'
            }
        
        # Prepare container details for the new location
        container_details = {
            'container_size': container_size or source_container.get('container_size', ''),
            'container_type': container_type or source_container.get('container_type', ''),
            'container_material': container_material or source_container.get('container_material', '')
        }
        
        # Update existing container with new location and details
        update_data = {
            'location_id': destination_location_id,
            'container_size': container_size or source_container.get('container_size', ''),
            'container_type': container_type or source_container.get('container_type', ''),
            'container_material': container_material or source_container.get('container_material', '')
        }
        
        # Remove empty values to avoid updating with blanks
        update_data = {key: value for key, value in update_data.items() if value}
        
        update_result = update_container(source_container.get('container_id', ''), update_data)
        if not update_result.get('success', False):
            return {
                'success': False,
                'error': f'Failed to update container: {update_result.get("error", "Unknown error")}'
            }
        
        logger.info(f"Successfully moved plant '{plant_name}' from '{source_location}' to '{destination_location}'")
        
        return {
            'success': True,
            'operation_type': 'move',
            'container_updates': {field: value for field, value in container_details.items() if value},
            'details': {
                'source_location': source_location,
                'destination_location': destination_location,
                'updated_container_id': source_container.get('container_id', ''),
                'updated_fields': update_result.get('updated_fields', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing move operation: {e}")
        return {
            'success': False,
            'error': f'Move operation error: {str(e)}'
        }

def _execute_add_operation(
    plant_name: str,
    destination_location: str,
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """Execute an add operation to add plant to a new location."""
    try:
        # Get destination location ID
        all_locations = get_all_locations()
        destination_location_id = None
        for location in all_locations:
            if location.get('location_name', '').strip().lower() == destination_location.lower():
                destination_location_id = location.get('location_id', '')
                break
        
        if not destination_location_id:
            return {
                'success': False,
                'error': f'Destination location "{destination_location}" not found'
            }
        
        # Prepare container details
        container_details = {
            'container_size': container_size or '',
            'container_type': container_type or '',
            'container_material': container_material or ''
        }
        
        # Add new container in destination location
        add_result = add_container(plant_name, destination_location_id, container_details)
        if not add_result.get('success', False):
            return {
                'success': False,
                'error': f'Failed to add container: {add_result.get("error", "Unknown error")}'
            }
        
        logger.info(f"Successfully added plant '{plant_name}' to location '{destination_location}'")
        
        return {
            'success': True,
            'operation_type': 'add',
            'container_updates': {field: value for field, value in container_details.items() if value},
            'details': {
                'destination_location': destination_location,
                'new_container_id': add_result.get('container_id', '')
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing add operation: {e}")
        return {
            'success': False,
            'error': f'Add operation error: {str(e)}'
        }

def _execute_update_in_place_operation(
    plant_name: str,
    source_location: str,
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """Execute an update in place operation - update container details without changing location."""
    try:
        # Find the existing container in the source location
        source_container = get_container_by_plant_and_location(plant_name, source_location)
        if not source_container:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in location "{source_location}"'
            }
        
        # Prepare update data with only provided values
        update_data = {}
        if container_size and container_size.strip():
            update_data['container_size'] = container_size.strip()
        if container_type and container_type.strip():
            update_data['container_type'] = container_type.strip()
        if container_material and container_material.strip():
            update_data['container_material'] = container_material.strip()
        
        # Update the container
        update_result = update_container(source_container.get('container_id', ''), update_data)
        if not update_result.get('success', False):
            return {
                'success': False,
                'error': f'Failed to update container: {update_result.get("error", "Unknown error")}'
            }
        
        logger.info(f"Successfully updated container for plant '{plant_name}' in location '{source_location}'")
        
        return {
            'success': True,
            'operation_type': 'update_in_place',
            'container_updates': update_data,
            'details': {
                'location': source_location,
                'container_id': source_container.get('container_id', ''),
                'updated_fields': update_result.get('updated_fields', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing update in place operation: {e}")
        return {
            'success': False,
            'error': f'Update in place operation failed: {str(e)}'
        }

def _execute_remove_operation(plant_name: str, source_location: str) -> Dict[str, Any]:
    """Execute a remove operation to remove plant from a location."""
    try:
        # Find the existing container in the source location
        source_container = get_container_by_plant_and_location(plant_name, source_location)
        if not source_container:
            return {
                'success': False,
                'error': f'Plant "{plant_name}" not found in source location "{source_location}"'
            }
        
        # Remove the container
        remove_result = remove_container(source_container.get('container_id', ''))
        if not remove_result.get('success', False):
            return {
                'success': False,
                'error': f'Failed to remove container: {remove_result.get("error", "Unknown error")}'
            }
        
        logger.info(f"Successfully removed plant '{plant_name}' from location '{source_location}'")
        
        return {
            'success': True,
            'operation_type': 'remove',
            'container_updates': {},
            'details': {
                'source_location': source_location,
                'removed_container_id': source_container.get('container_id', '')
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing remove operation: {e}")
        return {
            'success': False,
            'error': f'Remove operation error: {str(e)}'
        }

def _execute_container_update_operation(
    plant_name: str,
    container_size: Optional[str],
    container_type: Optional[str],
    container_material: Optional[str]
) -> Dict[str, Any]:
    """Execute container update operation for all plant containers."""
    try:
        # Get all containers for the plant
        plant_containers = get_containers_for_plant(plant_name)
        
        if not plant_containers:
            return {
                'success': False,
                'error': f'No containers found for plant "{plant_name}"'
            }
        
        # Prepare updates dictionary (only include non-empty values)
        updates = {}
        if container_size and container_size.strip():
            updates['container_size'] = container_size.strip()
        if container_type and container_type.strip():
            updates['container_type'] = container_type.strip()
        if container_material and container_material.strip():
            updates['container_material'] = container_material.strip()
        
        if not updates:
            return {
                'success': False,
                'error': 'No container updates specified'
            }
        
        # Update all containers for the plant
        updated_containers = []
        for container in plant_containers:
            container_id = container.get('container_id', '')
            if container_id:
                update_result = update_container(container_id, updates)
                if update_result.get('success', False):
                    updated_containers.append(container_id)
                else:
                    logger.warning(f"Failed to update container {container_id}: {update_result.get('error', 'Unknown error')}")
        
        if not updated_containers:
            return {
                'success': False,
                'error': 'Failed to update any containers'
            }
        
        logger.info(f"Successfully updated {len(updated_containers)} containers for plant '{plant_name}'")
        
        return {
            'success': True,
            'operation_type': 'container_update',
            'container_updates': updates,
            'details': {
                'updated_containers': updated_containers,
                'total_containers': len(plant_containers)
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing container update operation: {e}")
        return {
            'success': False,
            'error': f'Container update error: {str(e)}'
        }
