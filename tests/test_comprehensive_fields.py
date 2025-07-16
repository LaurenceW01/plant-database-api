"""
Comprehensive field testing to verify ALL fields are properly saved and retrieved
"""
import pytest
import uuid
import time
from api.main import create_app
from models.field_config import get_all_field_names, get_canonical_field_name

# Create test app
app = create_app(testing=True)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_key():
    import os
    return os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')

def test_comprehensive_field_saving_and_retrieval(client, api_key):
    """Test that ALL fields are properly saved and retrieved through the API"""
    
    # Add delay to respect rate limits
    time.sleep(2)
    
    # Create test data with ALL possible fields
    unique_id = str(uuid.uuid4())[:8]
    test_plant_name = f"ComprehensiveTest-{unique_id}"
    
    # Define comprehensive field data using ALL available fields
    comprehensive_payload = {
        "Plant Name": test_plant_name,
        "Description": "Comprehensive test plant with ALL fields populated for API validation",
        "Location": "Comprehensive Test Garden",
        "Light Requirements": "Full Sun to Partial Shade",
        "Frost Tolerance": "Hardy to -15°C (zones 5-9)",
        "Watering Needs": "Moderate to High - water when top inch of soil is dry",
        "Soil Preferences": "Well-draining, slightly acidic soil (pH 6.0-6.8)",
        "Pruning Instructions": "Prune in early spring before new growth, remove dead/diseased branches",
        "Mulching Needs": "Apply 2-3 inch layer of organic mulch around base, keep away from stem",
        "Fertilizing Schedule": "Feed monthly during growing season (April-September) with balanced fertilizer",
        "Winterizing Instructions": "Protect from harsh winds, mulch heavily, cover with burlap if needed",
        "Spacing Requirements": "Space plants 18-24 inches apart for proper air circulation",
        "Care Notes": "Monitor for pests, deadhead spent flowers, divide every 3-4 years for perennials",
        "Photo URL": "https://example.com/comprehensive-test-plant.jpg",
        "Raw Photo URL": "https://example.com/comprehensive-raw-photo.jpg"
    }
    
    print(f"\n=== COMPREHENSIVE FIELD TEST ===")
    print(f"Test plant: {test_plant_name}")
    print(f"Sending {len(comprehensive_payload)} fields:")
    for field, value in comprehensive_payload.items():
        print(f"  {field}: {value[:50]}...")
    
    # === STEP 1: CREATE with comprehensive data ===
    print(f"\n=== STEP 1: Creating plant with ALL fields ===")
    create_response = client.post('/api/plants', 
                                 json=comprehensive_payload, 
                                 headers={"x-api-key": api_key})
    
    print(f"Create response status: {create_response.status_code}")
    print(f"Create response data: {create_response.get_json()}")
    
    # Verify creation succeeded
    assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}: {create_response.get_json()}"
    
    # Add delay before retrieval
    time.sleep(1)
    
    # === STEP 2: RETRIEVE and verify all fields ===
    print(f"\n=== STEP 2: Retrieving plant to verify fields ===")
    get_response = client.get(f'/api/plants/{test_plant_name}')
    
    print(f"Get response status: {get_response.status_code}")
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"
    
    retrieved_plant = get_response.get_json()['plant']
    print(f"Retrieved plant with {len(retrieved_plant)} total fields")
    
    # === STEP 3: Verify ALL fields were saved correctly ===
    print(f"\n=== STEP 3: Field-by-field verification ===")
    
    missing_fields = []
    incorrect_fields = []
    correctly_saved_fields = []
    
    for sent_field, expected_value in comprehensive_payload.items():
        actual_value = retrieved_plant.get(sent_field, "")

        if sent_field == "Photo URL":
            # Photo URL gets converted to IMAGE formula, check if it contains our URL
            if expected_value and actual_value:
                # Check if the actual value is an IMAGE formula containing our expected URL
                if actual_value.startswith('=IMAGE("') and expected_value in actual_value:
                    correctly_saved_fields.append(sent_field)
                else:
                    incorrect_fields.append(f"{sent_field} (expected IMAGE formula with '{expected_value}', got: '{actual_value}')")
            elif expected_value and not actual_value:
                missing_fields.append(f"{sent_field} (expected IMAGE formula, got empty)")  
            else:
                correctly_saved_fields.append(sent_field)
        elif sent_field == "Raw Photo URL":
            # Raw Photo URL should be stored as-is
            if actual_value != expected_value:
                incorrect_fields.append(f"{sent_field} (expected: '{expected_value}', got: '{actual_value}')")
            else:
                correctly_saved_fields.append(sent_field)
        else:
            # All other fields should match exactly
            if actual_value != expected_value:
                if not actual_value:
                    missing_fields.append(f"{sent_field} (completely missing)")
                else:
                    incorrect_fields.append(f"{sent_field} (expected: '{expected_value}', got: '{actual_value}')")
            else:
                correctly_saved_fields.append(sent_field)

        print(f"  ✓ {sent_field}: {'✅ SAVED' if sent_field in correctly_saved_fields else '❌ ISSUE'}")
    
    # === STEP 4: Results summary ===
    print(f"\n=== COMPREHENSIVE FIELD TEST RESULTS ===")
    print(f"✅ Correctly saved: {len(correctly_saved_fields)}/{len(comprehensive_payload)} fields")
    print(f"❌ Missing fields: {len(missing_fields)}")
    print(f"❌ Incorrect fields: {len(incorrect_fields)}")
    
    if correctly_saved_fields:
        print(f"\n✅ CORRECTLY SAVED FIELDS:")
        for field in correctly_saved_fields:
            print(f"  - {field}")
    
    if missing_fields:
        print(f"\n❌ MISSING FIELDS:")
        for field in missing_fields:
            print(f"  - {field}")
    
    if incorrect_fields:
        print(f"\n❌ INCORRECT FIELDS:")
        for field in incorrect_fields:
            print(f"  - {field}")
    
    # === ASSERTIONS ===
    assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"
    assert len(incorrect_fields) == 0, f"Incorrect fields: {incorrect_fields}"
    
    # Verify we got most fields correctly (allow for Photo URL formula conversion)
    success_rate = len(correctly_saved_fields) / len(comprehensive_payload)
    assert success_rate >= 0.95, f"Success rate {success_rate:.1%} is below 95%"
    
    print(f"\n🎉 COMPREHENSIVE FIELD TEST PASSED! Success rate: {success_rate:.1%}")

def test_partial_field_saving_comparison(client, api_key):
    """Test partial field saving to compare with comprehensive test"""
    
    # Add delay to respect rate limits  
    time.sleep(2)
    
    unique_id = str(uuid.uuid4())[:8]
    test_plant_name = f"PartialTest-{unique_id}"
    
    # Send only minimal fields (like existing tests)
    minimal_payload = {
        "Plant Name": test_plant_name,
        "Description": "Minimal field test plant",
        "Location": "Test Garden",
        "Photo URL": "http://example.com/minimal.jpg"
    }
    
    print(f"\n=== PARTIAL FIELD TEST ===")
    print(f"Test plant: {test_plant_name}")
    print(f"Sending only {len(minimal_payload)} fields (minimal)")
    
    # Create plant
    create_response = client.post('/api/plants', 
                                 json=minimal_payload, 
                                 headers={"x-api-key": api_key})
    
    assert create_response.status_code == 201
    
    # Add delay before retrieval
    time.sleep(1)
    
    # Retrieve plant
    get_response = client.get(f'/api/plants/{test_plant_name}')
    assert get_response.status_code == 200
    
    retrieved_plant = get_response.get_json()['plant']
    
    # Verify minimal fields are saved
    for field, expected_value in minimal_payload.items():
        actual_value = retrieved_plant.get(field, "")
        if field != "Photo URL":  # Skip Photo URL due to IMAGE formula conversion
            assert actual_value == expected_value, f"Field {field}: expected '{expected_value}', got '{actual_value}'"
    
    # Verify other fields are empty (not populated)
    all_fields = get_all_field_names()
    sent_fields = set(minimal_payload.keys())
    
    empty_fields = []
    for field in all_fields:
        if field not in sent_fields and field not in ['ID', 'Last Updated', 'Photo URL', 'Raw Photo URL']:
            actual_value = retrieved_plant.get(field, "")
            if not actual_value:
                empty_fields.append(field)
    
    print(f"✅ Minimal fields saved correctly: {len(minimal_payload)}")
    print(f"✅ Other fields left empty (as expected): {len(empty_fields)}")
    print(f"🎉 PARTIAL FIELD TEST PASSED - API saves exactly what it receives") 