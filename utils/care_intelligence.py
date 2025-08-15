"""
Care Intelligence Module

This module provides intelligent care recommendations based on location and container context.
It implements the core intelligence functions for location-specific care calculations and 
container-material adjustments as defined in Phase 1 of the integration strategy.

Author: Plant Database API  
Created: Phase 1 Implementation - Locations & Containers Integration
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, time
from utils.locations_operations import get_location_by_id, get_container_by_id

# Set up logging for this module
logger = logging.getLogger(__name__)

def calculate_optimal_watering_times(location: Dict) -> Dict[str, Any]:
    """
    Calculate optimal watering times based on location sun exposure patterns.
    
    This function analyzes a location's sun exposure to recommend the best times
    for watering to minimize heat stress and maximize water absorption.
    
    Args:
        location (Dict): Location data with sun exposure information
        
    Returns:
        Dict[str, Any]: Watering time recommendations with keys:
            - primary_time: str (best watering time)
            - secondary_time: str (alternative watering time)  
            - avoid_times: List[str] (times to avoid watering)
            - reasoning: str (explanation of recommendations)
    """
    try:
        morning_hours = location.get('morning_sun_hours', 0)
        afternoon_hours = location.get('afternoon_sun_hours', 0) 
        evening_hours = location.get('evening_sun_hours', 0)
        location_name = location.get('location_name', 'Unknown')
        
        recommendations = {
            'primary_time': '',
            'secondary_time': '',
            'avoid_times': [],
            'reasoning': ''
        }
        
        # High afternoon sun (>3 hours) - water early morning
        if afternoon_hours > 3:
            recommendations['primary_time'] = 'Early morning (6:00-8:00 AM)'
            recommendations['secondary_time'] = 'Late evening after sunset'
            recommendations['avoid_times'] = ['Midday (11:00 AM - 3:00 PM)', 'Afternoon (3:00-6:00 PM)']
            recommendations['reasoning'] = f'Location receives {afternoon_hours} hours of afternoon sun, requiring morning watering to prevent heat stress'
        
        # High evening sun (>3 hours) - water very early morning  
        elif evening_hours > 3:
            recommendations['primary_time'] = 'Very early morning (5:30-7:00 AM)'
            recommendations['secondary_time'] = 'Early morning (7:00-8:30 AM)'
            recommendations['avoid_times'] = ['Afternoon (2:00-6:00 PM)', 'Evening (6:00-8:00 PM)']
            recommendations['reasoning'] = f'Location receives {evening_hours} hours of evening sun, requiring very early watering to prepare for heat stress'
        
        # High morning sun (>3 hours) - more flexible timing
        elif morning_hours > 3:
            recommendations['primary_time'] = 'Early morning (6:30-8:00 AM)'
            recommendations['secondary_time'] = 'Evening after peak sun (7:00-8:00 PM)'
            recommendations['avoid_times'] = ['Late morning (9:00-11:00 AM)']
            recommendations['reasoning'] = f'Location receives {morning_hours} hours of morning sun, allowing flexible watering with morning preference'
        
        # Low sun exposure - most flexible
        else:
            total_sun = morning_hours + afternoon_hours + evening_hours
            if total_sun <= 3:
                recommendations['primary_time'] = 'Morning (7:00-9:00 AM)'
                recommendations['secondary_time'] = 'Evening (6:00-8:00 PM)'
                recommendations['avoid_times'] = []
                recommendations['reasoning'] = f'Location receives only {total_sun} total hours of sun, allowing flexible watering schedule'
            else:
                recommendations['primary_time'] = 'Early morning (6:30-8:00 AM)'
                recommendations['secondary_time'] = 'Evening (7:00-8:30 PM)'
                recommendations['avoid_times'] = ['Midday (11:00 AM - 2:00 PM)']
                recommendations['reasoning'] = f'Moderate sun exposure ({total_sun} total hours) with standard watering schedule'
        
        logger.info(f"Generated watering recommendations for location {location_name}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error calculating optimal watering times: {e}")
        return {
            'primary_time': 'Early morning (6:00-8:00 AM)',
            'secondary_time': 'Evening (7:00-8:00 PM)',
            'avoid_times': ['Midday (11:00 AM - 3:00 PM)'],
            'reasoning': 'Default recommendation due to calculation error'
        }

def analyze_container_care_adjustments(container: Dict, location: Dict) -> Dict[str, Any]:
    """
    Analyze container-specific care adjustments based on material, size, and location.
    
    This function provides container-material and size-specific care recommendations
    considering the location's environmental conditions.
    
    Args:
        container (Dict): Container data with type, size, material information
        location (Dict): Location data with sun exposure and microclimate
        
    Returns:
        Dict[str, Any]: Container care adjustments with keys:
            - material_considerations: List[str] (material-specific advice)
            - size_adjustments: List[str] (size-based modifications)
            - drainage_recommendations: List[str] (drainage guidance)
            - temperature_management: List[str] (temperature control advice)
    """
    try:
        material = container.get('container_material', '').lower()
        size = container.get('container_size', '').lower()
        container_type = container.get('container_type', '')
        
        afternoon_hours = location.get('afternoon_sun_hours', 0)
        evening_hours = location.get('evening_sun_hours', 0)
        total_sun = location.get('total_sun_hours', 0)
        microclimate = location.get('microclimate_conditions', '').lower()
        
        adjustments = {
            'material_considerations': [],
            'size_adjustments': [],
            'drainage_recommendations': [],
            'temperature_management': []
        }
        
        # Material-specific considerations
        if 'plastic' in material:
            adjustments['material_considerations'].append('Plastic containers heat up quickly in direct sun')
            if afternoon_hours > 2 or evening_hours > 2:
                adjustments['material_considerations'].append('High heat retention risk - monitor soil temperature')
                adjustments['temperature_management'].append('Water early morning to cool container before peak heat')
            if total_sun > 6:
                adjustments['temperature_management'].append('Consider shade cloth during hottest part of day')
        
        elif 'ceramic' in material:
            adjustments['material_considerations'].append('Ceramic provides better temperature stability than plastic')
            adjustments['material_considerations'].append('Heavier material - ensure stable placement')
            if total_sun > 8:
                adjustments['temperature_management'].append('Ceramic can become very hot - check surface temperature')
        
        elif 'terracotta' in material or 'clay' in material:
            adjustments['material_considerations'].append('Porous material allows good air circulation')
            adjustments['material_considerations'].append('Higher water evaporation rate than plastic or ceramic')
            adjustments['drainage_recommendations'].append('Natural drainage properties - less likely to waterlog')
        
        # Size-specific adjustments
        if 'small' in size:
            adjustments['size_adjustments'].append('Small containers dry out faster - check daily in hot weather')
            adjustments['size_adjustments'].append('Limited root space - monitor for root binding')
            if total_sun > 6:
                adjustments['temperature_management'].append('Small containers overheat quickly - prioritize morning watering')
        
        elif 'large' in size:
            adjustments['size_adjustments'].append('Large containers retain moisture longer - avoid overwatering')
            adjustments['size_adjustments'].append('More stable temperature due to soil mass')
            adjustments['drainage_recommendations'].append('Check bottom drainage to prevent water stagnation')
        
        elif 'medium' in size:
            adjustments['size_adjustments'].append('Medium containers offer good balance of moisture retention and drainage')
            if total_sun > 7:
                adjustments['size_adjustments'].append('Monitor moisture levels every 2-3 days in high sun')
        
        # Drainage considerations based on container type
        if 'pot in ground' in container_type.lower():
            adjustments['drainage_recommendations'].append('Ground placement provides temperature stability')
            adjustments['drainage_recommendations'].append('Check that drainage holes are not blocked by soil')
        elif 'hanging' in container_type.lower():
            adjustments['drainage_recommendations'].append('Elevated position increases air circulation and drying')
            adjustments['temperature_management'].append('Higher position may increase wind exposure')
        
        # Microclimate adjustments
        if 'north facing' in microclimate:
            adjustments['temperature_management'].append('North facing location typically cooler - adjust watering frequency')
        if 'wall' in microclimate:
            adjustments['temperature_management'].append('Wall proximity can create heat reflection - monitor for hot spots')
        
        logger.info(f"Generated care adjustments for {container.get('container_id')} at location {location.get('location_name')}")
        return adjustments
        
    except Exception as e:
        logger.error(f"Error analyzing container care adjustments: {e}")
        return {
            'material_considerations': ['Standard container care applies'],
            'size_adjustments': ['Monitor moisture levels regularly'],
            'drainage_recommendations': ['Ensure adequate drainage'],
            'temperature_management': ['Water in early morning or evening']
        }

def generate_care_profile_for_location(location_id: str) -> Dict[str, Any]:
    """
    Generate a comprehensive care profile for a location.
    
    This function creates a complete care profile that can be used for all plants
    and containers at a specific location.
    
    Args:
        location_id (str): The location ID to generate profile for
        
    Returns:
        Dict[str, Any]: Comprehensive care profile with keys:
            - location_info: Dict (location details)
            - watering_strategy: Dict (optimal watering recommendations)
            - environmental_factors: Dict (sun, microclimate analysis)
            - general_recommendations: List[str] (location-specific advice)
    """
    try:
        location = get_location_by_id(location_id)
        if not location:
            logger.warning(f"Location not found for ID: {location_id}")
            return {}
        
        # Get watering strategy for this location
        watering_strategy = calculate_optimal_watering_times(location)
        
        # Analyze environmental factors
        environmental_factors = {
            'sun_exposure': {
                'morning_hours': location.get('morning_sun_hours', 0),
                'afternoon_hours': location.get('afternoon_sun_hours', 0),
                'evening_hours': location.get('evening_sun_hours', 0),
                'total_hours': location.get('total_sun_hours', 0),
                'pattern_description': location.get('shade_pattern', '')
            },
            'microclimate': {
                'conditions': location.get('microclimate_conditions', ''),
                'implications': _analyze_microclimate_implications(location.get('microclimate_conditions', ''))
            }
        }
        
        # Generate general recommendations
        general_recommendations = _generate_location_recommendations(location)
        
        care_profile = {
            'location_info': {
                'location_id': location['location_id'],
                'location_name': location['location_name'],
                'classification': _classify_location(location)
            },
            'watering_strategy': watering_strategy,
            'environmental_factors': environmental_factors,
            'general_recommendations': general_recommendations
        }
        
        logger.info(f"Generated care profile for location {location.get('location_name')}")
        return care_profile
        
    except Exception as e:
        logger.error(f"Error generating care profile for location {location_id}: {e}")
        return {}

def generate_container_care_requirements(container_id: str) -> Dict[str, Any]:
    """
    Generate specific care requirements for a container.
    
    This function combines container specifications with location context to create
    precise care requirements for the specific container.
    
    Args:
        container_id (str): The container ID to generate requirements for
        
    Returns:
        Dict[str, Any]: Container care requirements with keys:
            - container_info: Dict (container details)
            - location_context: Dict (location information)
            - care_adjustments: Dict (container-specific adjustments)
            - integrated_recommendations: List[str] (combined advice)
    """
    try:
        container = get_container_by_id(container_id)
        if not container:
            logger.warning(f"Container not found for ID: {container_id}")
            return {}
        
        location = get_location_by_id(container['location_id'])
        if not location:
            logger.warning(f"Location not found for container {container_id}")
            return {}
        
        # Get container-specific care adjustments
        care_adjustments = analyze_container_care_adjustments(container, location)
        
        # Get location watering strategy
        watering_strategy = calculate_optimal_watering_times(location)
        
        # Generate integrated recommendations
        integrated_recommendations = _generate_integrated_recommendations(container, location, care_adjustments, watering_strategy)
        
        requirements = {
            'container_info': {
                'container_id': container['container_id'],
                'plant_id': container['plant_id'],
                'type': container['container_type'],
                'size': container['container_size'],
                'material': container['container_material']
            },
            'location_context': {
                'location_id': location['location_id'],
                'location_name': location['location_name'],
                'sun_exposure': f"{location['total_sun_hours']} hours ({location['shade_pattern']})",
                'microclimate': location['microclimate_conditions']
            },
            'care_adjustments': care_adjustments,
            'watering_strategy': watering_strategy,
            'integrated_recommendations': integrated_recommendations
        }
        
        logger.info(f"Generated care requirements for container {container_id}")
        return requirements
        
    except Exception as e:
        logger.error(f"Error generating care requirements for container {container_id}: {e}")
        return {}

def _analyze_microclimate_implications(microclimate: str) -> List[str]:
    """
    Analyze microclimate conditions and their care implications.
    
    Args:
        microclimate (str): Microclimate description
        
    Returns:
        List[str]: List of care implications
    """
    implications = []
    microclimate_lower = microclimate.lower()
    
    if 'north facing' in microclimate_lower:
        implications.append('Cooler temperatures, less intense sun')
        implications.append('May need less frequent watering')
    
    if 'south facing' in microclimate_lower:
        implications.append('Warmer temperatures, more intense sun')
        implications.append('May need more frequent watering')
    
    if 'wall' in microclimate_lower:
        implications.append('Heat reflection from wall possible')
        implications.append('Protection from wind')
    
    if 'protected' in microclimate_lower:
        implications.append('Reduced wind exposure')
        implications.append('More stable environmental conditions')
    
    return implications

def _classify_location(location: Dict) -> str:
    """
    Classify a location based on its sun exposure characteristics.
    
    Args:
        location (Dict): Location data
        
    Returns:
        str: Location classification
    """
    total_sun = location.get('total_sun_hours', 0)
    afternoon_hours = location.get('afternoon_sun_hours', 0)
    
    if total_sun >= 8:
        return 'High intensity full sun'
    elif total_sun >= 6:
        if afternoon_hours > 4:
            return 'High heat stress location'
        else:
            return 'Moderate full sun'
    elif total_sun >= 4:
        return 'Partial sun'
    else:
        return 'Shade/low light'

def _generate_location_recommendations(location: Dict) -> List[str]:
    """
    Generate general recommendations for a location.
    
    Args:
        location (Dict): Location data
        
    Returns:
        List[str]: List of general recommendations
    """
    recommendations = []
    total_sun = location.get('total_sun_hours', 0)
    afternoon_hours = location.get('afternoon_sun_hours', 0)
    evening_hours = location.get('evening_sun_hours', 0)
    
    if total_sun > 8:
        recommendations.append('High sun location - monitor plants daily during hot weather')
    
    if afternoon_hours > 3:
        recommendations.append('Afternoon sun can be intense - consider shade protection for sensitive plants')
    
    if evening_hours > 3:
        recommendations.append('Evening sun location - ensure morning watering to prepare for heat')
    
    if total_sun < 4:
        recommendations.append('Lower light location - choose shade-tolerant plants')
    
    return recommendations

def analyze_plant_with_ai(plant_name: str = '', user_notes: str = '', analysis_type: str = 'general_care', location: str = '') -> Dict[str, Any]:
    """
    AI-powered plant analysis using OpenAI.
    
    Args:
        plant_name (str): Name of the plant to analyze
        user_notes (str): User observations and notes
        analysis_type (str): Type of analysis to perform
        location (str): Plant location for enhanced context
        
    Returns:
        Dict[str, Any]: Analysis results with AI recommendations
    """
    try:
        from config.config import openai_client
        import logging
        
        if not any([plant_name, user_notes]):
            return {
                'success': False,
                'error': 'Either plant_name or user_notes describing the plant is required.'
            }
        
        # Check if OpenAI client is available
        if not openai_client:
            return {
                'success': False,
                'error': 'AI analysis not available - OpenAI API key not configured'
            }
        
        # Build enhanced prompt with location context if available
        location_context = ""
        if location:
            # Try to get location/container intelligence for enhanced analysis
            try:
                from utils.locations_operations import get_plant_location_context
                # Find plant ID if we have a plant name
                from utils.plant_operations import find_plant_by_id_or_name
                plant_id_or_row, plant_data = find_plant_by_id_or_name(plant_name)
                if plant_id_or_row is not None:
                    plant_id = str(plant_id_or_row)  # Use ID field value directly (already correct)
                    context_data = get_plant_location_context(plant_id)
                    if context_data:
                        location_context = f"\n\nENVIRONMENTAL CONTEXT:\nThis plant is located in {location}. Container and microclimate details: {context_data[0].get('context', {}) if context_data else 'No specific container data available'}."
            except:
                location_context = f"\n\nLOCATION: {location}"
        
        # Create comprehensive prompt for OpenAI
        prompt = f"""Provide comprehensive plant care analysis for:

Plant: {plant_name if plant_name else 'Plant requiring identification'}
User Observations: {user_notes if user_notes else 'General care advice needed'}
Analysis Type: {analysis_type}{location_context}

Please provide detailed advice covering:
1. Plant identification (if needed) and health assessment
2. Specific treatment for any issues mentioned
3. Watering requirements and schedule
4. Light and location preferences
5. Soil and fertilization needs
6. Common problems and prevention
7. Seasonal care tips

Format your response clearly and practically for plant care in Houston, Texas climate."""
        
        # Call OpenAI API
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': {
                    'plant_name': plant_name,
                    'ai_analysis': analysis_text,
                    'user_notes': user_notes,
                    'location': location,
                    'analysis_type': analysis_type,
                    'enhanced_with_location': bool(location_context)
                }
            }
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': f'AI analysis failed: {str(e)}',
                'fallback_advice': f'For {plant_name}: Monitor plant health, ensure proper watering and light conditions. Consult local garden center for specific advice.'
            }
        
    except Exception as e:
        logging.error(f"Error in analyze_plant_with_ai: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def _generate_integrated_recommendations(container: Dict, location: Dict, care_adjustments: Dict, watering_strategy: Dict) -> List[str]:
    """
    Generate integrated recommendations combining all factors.
    
    Args:
        container (Dict): Container data
        location (Dict): Location data  
        care_adjustments (Dict): Container care adjustments
        watering_strategy (Dict): Watering recommendations
        
    Returns:
        List[str]: List of integrated recommendations
    """
    recommendations = []
    
    # Add primary watering recommendation
    recommendations.append(f"Water {watering_strategy.get('primary_time', 'early morning')}")
    
    # Add key material considerations
    material_considerations = care_adjustments.get('material_considerations', [])
    if material_considerations:
        recommendations.append(material_considerations[0])  # Add most important material consideration
    
    # Add key size adjustment
    size_adjustments = care_adjustments.get('size_adjustments', [])
    if size_adjustments:
        recommendations.append(size_adjustments[0])  # Add most important size consideration
    
    # Add location-specific advice
    total_sun = location.get('total_sun_hours', 0)
    if total_sun > 7:
        recommendations.append('High sun location - check soil moisture daily during summer')

# ========================================
# API ENDPOINT OPERATIONS (moved from main.py)
# ========================================

def analyze_plant_api():
    """Core plant analysis logic for API endpoints - OpenAI powered"""
    try:
        from flask import jsonify
        from .field_normalization_middleware import get_plant_name, get_normalized_field
        
        # Use field normalization to get data
        plant_name = get_plant_name() or ''
        user_notes = get_normalized_field('user_notes', '')
        analysis_type = get_normalized_field('analysis_type', 'general_care')
        location = get_normalized_field('location', '') or get_normalized_field('Location', '')
        
        # Perform AI analysis
        result = analyze_plant_with_ai(plant_name, user_notes, analysis_type, location)
        
        # Convert result to appropriate HTTP response
        if result.get('success'):
            return jsonify(result), 200
        else:
            status_code = 500 if 'AI analysis failed' in result.get('error', '') else 400
            return jsonify(result), status_code
        
    except Exception as e:
        import logging
        logging.error(f"Error in analyze_plant: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def enhance_analysis_api():
    """Enhanced analysis combining AI insights with database knowledge"""
    try:
        from flask import jsonify
        from .field_normalization_middleware import get_plant_name, get_normalized_field
        
        # Use field normalization to get data
        plant_name = get_plant_name()
        gpt_analysis = get_normalized_field('gpt_analysis', '')
        plant_identification = get_normalized_field('plant_identification', '')
        location = get_normalized_field('location', '') or get_normalized_field('Location', '')
        analysis_type = get_normalized_field('analysis_type', 'health_assessment')
        
        # Require either gpt_analysis or plant_identification
        if not gpt_analysis and not plant_identification:
            return jsonify({
                'success': False,
                'error': 'Either gpt_analysis or plant_identification is required'
            }), 400
        
        # Use AI analysis for the core logic, passing either the analysis text or identification
        analysis_input = gpt_analysis or f"Plant identification: {plant_identification}"
        result = analyze_plant_with_ai(plant_name or plant_identification, analysis_input, analysis_type, location)
        
        # Format response as enhanced_analysis structure
        if result.get('success'):
            enhanced_response = {
                'success': True,
                'enhanced_analysis': {
                    'plant_match': {
                        'found_in_database': bool(plant_name),
                        'original_identification': plant_identification or plant_name
                    },
                    'care_enhancement': {
                        'ai_analysis': result.get('ai_analysis', result.get('diagnosis', ''))
                    },
                    'diagnosis_enhancement': {
                        'urgency_level': 'monitor',  # Default, could be enhanced based on AI analysis
                        'treatment_recommendations': result.get('ai_analysis', result.get('diagnosis', ''))
                    }
                }
            }
            return jsonify(enhanced_response), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import logging
        logging.error(f"Error in enhance_analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500