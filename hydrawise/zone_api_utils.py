#!/usr/bin/env python3
"""
Hydrawise Zone API Utilities

Provides clean interface functions for zone control operations
to be used by the API endpoints.

Author: AI Assistant
Date: 2024
"""

import os
from dotenv import load_dotenv
from hydrawise_api_explorer import HydrawiseAPIExplorer
from zone_run_simple import get_zone_list, start_zone_and_wait, stop_all_zones_now
from zone_api_web_utils import start_zone_web_optimized, stop_all_zones_web_optimized, get_zone_list_web_optimized

# Global explorer instance - initialized when first needed
_explorer = None

def get_explorer():
    """Get or create the Hydrawise API explorer instance."""
    global _explorer
    
    if _explorer is None:
        # Load API key from environment
        load_dotenv()
        api_key = os.getenv('HUNTER_HYDRAWISE_API_KEY')
        
        if not api_key:
            raise ValueError("HUNTER_HYDRAWISE_API_KEY not found in environment variables")
        
        # Initialize explorer with conservative rate limiting for web API usage
        # Use respect_rate_limits=True but aggressive_rate_limiting=False for web-friendly behavior
        _explorer = HydrawiseAPIExplorer(api_key, respect_rate_limits=True, aggressive_rate_limiting=False)
    
    return _explorer


def list_zones():
    """
    Get list of all available zones with their current status.
    
    Returns:
        dict: Dictionary containing zones data and formatted list
        {
            'zones': {zone_id: zone_info, ...},
            'zone_list': [formatted_zone_info, ...],
            'running_zones': [zone_info, ...],
            'total_zones': int
        }
    """
    try:
        explorer = get_explorer()
        zones = get_zone_list_web_optimized(explorer)
        
        if not zones:
            return {
                'zones': {},
                'zone_list': [],
                'running_zones': [],
                'total_zones': 0,
                'error': 'No zones found'
            }
        
        # Create sorted list for display
        zone_list = list(zones.values())
        zone_list.sort(key=lambda z: z['id'])
        
        # Get running zones
        running_zones = [zone for zone in zones.values() if zone.get('time_left') == 'Now']
        
        # Format zones for API response
        formatted_zones = []
        for i, zone in enumerate(zone_list, 1):
            zone_id = zone['id']
            zone_name = zone['name']
            is_running = zone.get('time_left') == 'Now'
            time_left = zone.get('time_left', 'Unknown') if is_running else None
            
            formatted_zones.append({
                'selection_number': i,
                'zone_id': zone_id,
                'zone_name': zone_name,
                'is_running': is_running,
                'time_left': time_left,
                'status': 'RUNNING' if is_running else 'IDLE'
            })
        
        return {
            'zones': zones,
            'zone_list': formatted_zones,
            'running_zones': running_zones,
            'total_zones': len(zones),
            'success': True
        }
        
    except Exception as e:
        error_msg = str(e)
        if 'rate limited' in error_msg.lower():
            return {
                'zones': {},
                'zone_list': [],
                'running_zones': [],
                'total_zones': 0,
                'error': 'Hydrawise system is rate limited. Please wait a minute before trying again.',
                'rate_limited': True,
                'success': False
            }
        else:
            return {
                'zones': {},
                'zone_list': [],
                'running_zones': [],
                'total_zones': 0,
                'error': f'Error getting zones: {error_msg}',
                'success': False
            }


def start_zone(zone_selection, duration_minutes):
    """
    Start a zone by selection number or zone ID.
    
    Args:
        zone_selection: Either selection number (1-N) or zone ID
        duration_minutes: How long to run the zone
        
    Returns:
        dict: Result of the start operation
    """
    try:
        explorer = get_explorer()
        
        # Get current zones
        zones = get_zone_list_web_optimized(explorer)
        
        if not zones:
            return {
                'success': False,
                'error': 'Failed to get zones'
            }
        
        # Create sorted list for display  
        zone_list = list(zones.values())
        zone_list.sort(key=lambda z: z['id'])
        
        # Format zones for selection
        formatted_zones = []
        for i, zone in enumerate(zone_list, 1):
            formatted_zones.append({
                'selection_number': i,
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'is_running': zone.get('time_left') == 'Now',
                'status': 'RUNNING' if zone.get('time_left') == 'Now' else 'IDLE'
            })
        
        # Determine zone ID from selection
        zone_id = None
        zone_name = None
        
        try:
            # Try as selection number first
            selection_num = int(zone_selection)
            if 1 <= selection_num <= len(formatted_zones):
                selected_zone = formatted_zones[selection_num - 1]
                zone_id = selected_zone['zone_id']
                zone_name = selected_zone['zone_name']
            else:
                return {
                    'success': False,
                    'error': f'Invalid selection number. Please choose 1-{len(formatted_zones)}'
                }
        except ValueError:
            # Not a number, try as zone ID
            if zone_selection in zones:
                zone_id = zone_selection
                zone_name = zones[zone_selection]['name']
            else:
                return {
                    'success': False,
                    'error': f'Zone ID {zone_selection} not found'
                }
        
        # Validate duration
        if not isinstance(duration_minutes, (int, float)) or duration_minutes <= 0:
            return {
                'success': False,
                'error': 'Duration must be a positive number'
            }
        
        # Check if zone is already running
        if zones[zone_id].get('time_left') == 'Now':
            return {
                'success': False,
                'error': f'Zone "{zone_name}" is already running',
                'zone_id': zone_id,
                'zone_name': zone_name,
                'time_left': zones[zone_id].get('time_left')
            }
        
        # Start the zone
        try:
            success = start_zone_web_optimized(explorer, zone_id, duration_minutes)
            
            if success:
                return {
                    'success': True,
                    'message': f'Zone "{zone_name}" started successfully',
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'duration_minutes': duration_minutes
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to start zone "{zone_name}"',
                    'zone_id': zone_id,
                    'zone_name': zone_name
                }
        except Exception as e:
            error_msg = str(e)
            if 'rate limited' in error_msg.lower():
                return {
                    'success': False,
                    'error': f'Hydrawise system is rate limited. Please wait a minute before trying again.',
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'rate_limited': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Error starting zone "{zone_name}": {error_msg}',
                    'zone_id': zone_id,
                    'zone_name': zone_name
                }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error starting zone: {str(e)}'
        }


def get_running_zones():
    """
    Get list of currently running zones.
    
    Returns:
        dict: Information about running zones
    """
    try:
        explorer = get_explorer()
        zones = get_zone_list_web_optimized(explorer)
        
        if not zones:
            return {
                'success': False,
                'error': 'Failed to get zones'
            }
        
        # Get running zones directly
        running_zones = [zone for zone in zones.values() if zone.get('time_left') == 'Now']
        
        # Format running zones for API response
        formatted_running = []
        for zone in running_zones:
            formatted_running.append({
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'time_left': zone.get('time_left', 'Unknown')
            })
        
        return {
            'success': True,
            'running_zones': formatted_running,
            'count': len(running_zones),
            'message': f'{len(running_zones)} zones currently running' if running_zones else 'No zones currently running'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error getting running zones: {str(e)}',
            'running_zones': [],
            'count': 0
        }


def stop_all_zones():
    """
    Stop all currently running zones.
    
    Returns:
        dict: Result of the stop operation
    """
    try:
        explorer = get_explorer()
        
        # Check what zones are running first
        running_data = get_running_zones()
        if not running_data['success']:
            return {
                'success': False,
                'error': running_data.get('error', 'Failed to check running zones')
            }
        
        running_zones = running_data['running_zones']
        
        if not running_zones:
            return {
                'success': True,
                'message': 'No zones were running',
                'zones_stopped': []
            }
        
        # Stop all zones
        try:
            success = stop_all_zones_web_optimized(explorer)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully stopped {len(running_zones)} zones',
                    'zones_stopped': running_zones
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to stop zones',
                    'zones_that_were_running': running_zones
                }
        except Exception as e:
            error_msg = str(e)
            if 'rate limited' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Hydrawise system is rate limited. Please wait a minute before trying again.',
                    'zones_that_were_running': running_zones,
                    'rate_limited': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Error stopping zones: {error_msg}',
                    'zones_that_were_running': running_zones
                }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error stopping zones: {str(e)}',
            'zones_stopped': []
        }
