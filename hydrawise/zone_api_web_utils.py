#!/usr/bin/env python3
"""
Hydrawise Zone Web API Utilities

Web-optimized versions of zone control functions that avoid
long blocking operations and are suitable for HTTP API usage.

Author: AI Assistant
Date: 2024
"""

import os
import time
from dotenv import load_dotenv
from hydrawise_api_explorer import HydrawiseAPIExplorer


def start_zone_web_optimized(explorer, zone_id, duration_minutes):
    """
    Start a zone with web-optimized behavior - direct API call.
    
    This version sends the start command directly without any polling delays.
    
    Args:
        explorer: API explorer instance
        zone_id: Zone ID to start
        duration_minutes: How long to run the zone
        
    Returns:
        bool: True if command was sent successfully
    """
    try:
        print(f"[WEB] Starting zone {zone_id} for {duration_minutes} minutes...")
        
        # Direct API call without using explorer's rate limiting
        import requests
        url = f"{explorer.base_url}/setzone.php"
        params = {
            'action': 'run',
            'relay_id': zone_id,
            'custom': duration_minutes * 60,  # Convert to seconds
            'api_key': explorer.api_key
        }
        
        print(f"[WEB] Direct start command to: {url}")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        print(f"[WEB] Start command sent successfully - Status: {response.status_code}")
        
        # For web API, we trust the command was received
        # and return success immediately to avoid timeouts
        return True
        
    except Exception as e:
        print(f"[WEB ERROR] Failed to start zone: {e}")
        return False


def stop_all_zones_web_optimized(explorer):
    """
    Stop all zones with web-optimized behavior - direct API call.
    
    Returns:
        bool: True if command was sent successfully
    """
    try:
        print(f"[WEB] Stopping all zones...")
        
        # Direct API call without using explorer's methods
        import requests
        url = f"{explorer.base_url}/setzone.php"
        params = {
            'action': 'stopall',
            'api_key': explorer.api_key
        }
        
        print(f"[WEB] Direct stop command to: {url}")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        print(f"[WEB] Stop command sent successfully - Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"[WEB ERROR] Failed to stop zones: {e}")
        return False


def get_zone_list_web_optimized(explorer):
    """
    Get zone list with web-optimized timeouts and minimal delays.
    Bypasses all polling delays for immediate response.
    
    Returns:
        dict: Zone data or empty dict on error
    """
    try:
        # For web optimization, completely bypass the explorer's methods
        # and make direct API calls to avoid any polling delays
        
        # Direct API call without polling delays
        import requests
        url = f"{explorer.base_url}/statusschedule.php"
        params = {'api_key': explorer.api_key}
        
        print(f"[WEB] Direct API call to: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        status_data = response.json()
        print(f"[WEB] Direct call successful - Status: {response.status_code}")
        
        zones = {}
        
        # Extract from status data
        if 'relays' in status_data:
            for relay in status_data['relays']:
                zone_id = relay.get('relay_id')
                if zone_id:
                    zones[zone_id] = {
                        'id': zone_id,
                        'name': relay.get('name', f'Zone {zone_id}'),
                        'running': relay.get('running'),
                        'time_left': relay.get('timestr'),
                        'raw_relay_data': relay
                    }
        
        return zones
        
    except Exception as e:
        print(f"[WEB ERROR] Error getting zones: {e}")
        return {}
