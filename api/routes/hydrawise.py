"""
Hydrawise Zone Control Routes

Provides a single endpoint for all Hydrawise irrigation zone operations
including listing zones, starting zones, checking status, and stopping zones.
"""

from flask import Blueprint, request, jsonify
from api.core.middleware import require_api_key
import logging

# Import hydrawise utilities from the hydrawise folder
try:
    import sys
    import os
    # Add hydrawise directory to Python path
    hydrawise_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'hydrawise')
    if hydrawise_path not in sys.path:
        sys.path.insert(0, hydrawise_path)
    
    from zone_api_utils import list_zones, start_zone, get_running_zones, stop_all_zones
except ImportError as e:
    logging.error(f"Failed to import hydrawise utilities: {e}")
    # Create fallback functions that return errors
    def list_zones():
        return {'success': False, 'error': 'Hydrawise module not available'}
    def start_zone(zone_selection, duration_minutes):
        return {'success': False, 'error': 'Hydrawise module not available'}
    def get_running_zones():
        return {'success': False, 'error': 'Hydrawise module not available'}
    def stop_all_zones():
        return {'success': False, 'error': 'Hydrawise module not available'}

# Create the hydrawise blueprint
hydrawise_bp = Blueprint('hydrawise', __name__, url_prefix='/api/hydrawise')


@hydrawise_bp.route('/zones', methods=['GET'])
@require_api_key
def hydrawise_zones():
    """
    Single endpoint for all Hydrawise zone operations.
    
    Actions supported via 'action' parameter:
    - list: Get all zones with their current status
    - start: Start a specific zone (requires zone_selection and duration_minutes)
    - status: Get currently running zones only
    - stop: Stop all running zones
    
    Query Parameters:
    - action (required): One of 'list', 'start', 'status', 'stop'
    - zone_selection (for start action): Zone selection number (1-N) or zone ID
    - duration_minutes (for start action): How long to run the zone in minutes
    
    Examples:
    - GET /api/hydrawise/zones?action=list
    - GET /api/hydrawise/zones?action=start&zone_selection=1&duration_minutes=10
    - GET /api/hydrawise/zones?action=status
    - GET /api/hydrawise/zones?action=stop
    """
    try:
        # Get the action parameter
        action = request.args.get('action', '').lower().strip()
        
        if not action:
            return jsonify({
                'success': False,
                'error': 'Action parameter is required',
                'valid_actions': ['list', 'start', 'status', 'stop'],
                'examples': [
                    'GET /api/hydrawise/zones?action=list',
                    'GET /api/hydrawise/zones?action=start&zone_selection=1&duration_minutes=10',
                    'GET /api/hydrawise/zones?action=status',
                    'GET /api/hydrawise/zones?action=stop'
                ]
            }), 400
        
        # Handle different actions
        if action == 'list':
            # List all zones with their status
            result = list_zones()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'action': 'list',
                    'zones': result['zone_list'],
                    'total_zones': result['total_zones'],
                    'running_count': len(result['running_zones']),
                    'message': f'Found {result["total_zones"]} zones, {len(result["running_zones"])} running'
                })
            else:
                return jsonify({
                    'success': False,
                    'action': 'list',
                    'error': result.get('error', 'Unknown error'),
                    'zones': []
                }), 500
        
        elif action == 'start':
            # Start a specific zone
            zone_selection = request.args.get('zone_selection')
            duration_minutes = request.args.get('duration_minutes')
            
            if not zone_selection:
                return jsonify({
                    'success': False,
                    'action': 'start',
                    'error': 'zone_selection parameter is required',
                    'example': 'GET /api/hydrawise/zones?action=start&zone_selection=1&duration_minutes=10'
                }), 400
            
            if not duration_minutes:
                return jsonify({
                    'success': False,
                    'action': 'start',
                    'error': 'duration_minutes parameter is required',
                    'example': 'GET /api/hydrawise/zones?action=start&zone_selection=1&duration_minutes=10'
                }), 400
            
            try:
                duration_minutes = float(duration_minutes)
            except ValueError:
                return jsonify({
                    'success': False,
                    'action': 'start',
                    'error': 'duration_minutes must be a number',
                    'received': duration_minutes
                }), 400
            
            # Convert zone_selection to int if it's a selection number
            try:
                zone_selection = int(zone_selection)
            except ValueError:
                # Keep as string if it's a zone ID
                pass
            
            result = start_zone(zone_selection, duration_minutes)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'action': 'start',
                    'message': result['message'],
                    'zone_id': result['zone_id'],
                    'zone_name': result['zone_name'],
                    'duration_minutes': result['duration_minutes']
                })
            else:
                return jsonify({
                    'success': False,
                    'action': 'start',
                    'error': result.get('error', 'Unknown error'),
                    'zone_selection': zone_selection,
                    'duration_minutes': duration_minutes
                }), 400
        
        elif action == 'status':
            # Get currently running zones
            result = get_running_zones()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'action': 'status',
                    'running_zones': result['running_zones'],
                    'count': result['count'],
                    'message': result['message']
                })
            else:
                return jsonify({
                    'success': False,
                    'action': 'status',
                    'error': result.get('error', 'Unknown error'),
                    'running_zones': []
                }), 500
        
        elif action == 'stop':
            # Stop all running zones
            result = stop_all_zones()
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'action': 'stop',
                    'message': result['message'],
                    'zones_stopped': result.get('zones_stopped', [])
                })
            else:
                return jsonify({
                    'success': False,
                    'action': 'stop',
                    'error': result.get('error', 'Unknown error')
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid action: {action}',
                'valid_actions': ['list', 'start', 'status', 'stop'],
                'received_action': action
            }), 400
    
    except Exception as e:
        logging.error(f"Error in hydrawise_zones endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'action': request.args.get('action', 'unknown')
        }), 500
