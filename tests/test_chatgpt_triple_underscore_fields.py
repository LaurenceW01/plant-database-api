#!/usr/bin/env python3
"""
Test ChatGPT triple underscore field normalization.

This test ensures that ChatGPT's habit of using triple underscores
in field names (e.g., 'Plant___Name', 'Soil___Preferences') are
properly normalized to their canonical forms.
"""

import pytest
from models.field_config import get_canonical_field_name


class TestChatGPTTripleUnderscoreFields:
    """Test ChatGPT triple underscore field normalization patterns"""
    
    def test_plant_name_triple_underscore(self):
        """Test Plant___Name -> Plant Name normalization"""
        assert get_canonical_field_name('Plant___Name') == 'Plant Name'
        assert get_canonical_field_name('plant___name') == 'Plant Name'
    
    def test_light_requirements_triple_underscore(self):
        """Test Light___Requirements -> Light Requirements normalization"""
        assert get_canonical_field_name('Light___Requirements') == 'Light Requirements'
        assert get_canonical_field_name('light___requirements') == 'Light Requirements'
    
    def test_soil_preferences_triple_underscore(self):
        """Test Soil___Preferences -> Soil Preferences normalization"""
        assert get_canonical_field_name('Soil___Preferences') == 'Soil Preferences'
        assert get_canonical_field_name('soil___preferences') == 'Soil Preferences'
    
    def test_watering_needs_triple_underscore(self):
        """Test Watering___Needs -> Watering Needs normalization"""
        assert get_canonical_field_name('Watering___Needs') == 'Watering Needs'
        assert get_canonical_field_name('watering___needs') == 'Watering Needs'
    
    def test_frost_tolerance_triple_underscore(self):
        """Test Frost___Tolerance -> Frost Tolerance normalization"""
        assert get_canonical_field_name('Frost___Tolerance') == 'Frost Tolerance'
        assert get_canonical_field_name('frost___tolerance') == 'Frost Tolerance'
    
    def test_care_notes_triple_underscore(self):
        """Test Care___Notes -> Care Notes normalization"""
        assert get_canonical_field_name('Care___Notes') == 'Care Notes'
        assert get_canonical_field_name('care___notes') == 'Care Notes'
    
    def test_comprehensive_triple_underscore_fields(self):
        """Test all common ChatGPT triple underscore patterns"""
        test_mappings = {
            'Plant___Name': 'Plant Name',
            'Light___Requirements': 'Light Requirements',
            'Soil___Preferences': 'Soil Preferences',
            'Watering___Needs': 'Watering Needs',
            'Frost___Tolerance': 'Frost Tolerance',
            'Care___Notes': 'Care Notes',
            'Pruning___Instructions': 'Pruning Instructions',
            'Fertilizing___Schedule': 'Fertilizing Schedule',
            'Spacing___Requirements': 'Spacing Requirements'
        }
        
        for triple_underscore_field, expected_canonical in test_mappings.items():
            # Test exact case
            assert get_canonical_field_name(triple_underscore_field) == expected_canonical
            # Test lowercase
            assert get_canonical_field_name(triple_underscore_field.lower()) == expected_canonical
    
    def test_single_underscore_fallback(self):
        """Test that single underscore patterns still work"""
        assert get_canonical_field_name('plant_name') == 'Plant Name'
        assert get_canonical_field_name('light_requirements') == 'Light Requirements'
        assert get_canonical_field_name('soil_preferences') == 'Soil Preferences'
    
    def test_original_field_names_still_work(self):
        """Test that original canonical field names still work"""
        assert get_canonical_field_name('Plant Name') == 'Plant Name'
        assert get_canonical_field_name('Light Requirements') == 'Light Requirements'
        assert get_canonical_field_name('Soil Preferences') == 'Soil Preferences'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
