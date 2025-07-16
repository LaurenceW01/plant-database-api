"""
Pytest configuration for test isolation and Google Sheets API rate limiting
"""
import pytest
import time
import os
from api.main import create_app

# Test isolation fixture with Google Sheets API rate limiting
@pytest.fixture(scope="function", autouse=True)
def test_isolation():
    """Ensure proper isolation between tests and respect Google Sheets API limits"""
    # Google Sheets API limit: 60 reads per minute = 1 read per second
    # Each plant operation can involve 2-3 API calls, so we need 3+ second delays
    print(f"\n⏱️  Rate limiting delay...")
    time.sleep(3)  # 3 second delay before each test
    yield
    # Additional delay after test to ensure clean separation
    time.sleep(1)

# API key fixture
@pytest.fixture(scope="session")
def api_key():
    """Provide API key for tests"""
    return os.environ.get('GARDENLLM_API_KEY', 'test-secret-key')

# Rate-limited test client fixture  
@pytest.fixture(scope="function")
def rate_limited_client():
    """Create test client with rate limiting enabled for performance tests"""
    app = create_app(testing=False)  # Enable rate limiting
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Standard test client fixture
@pytest.fixture(scope="function") 
def test_client():
    """Create standard test client without rate limiting"""
    app = create_app(testing=True)  # Disable rate limiting
    with app.test_client() as client:
        yield client

# Session-level cleanup
@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup and cleanup for entire test session"""
    print("\n=== STARTING TEST SESSION ===")
    yield
    print("\n=== TEST SESSION COMPLETE ===")

# Function to add delays for Google Sheets API respect
def sheets_api_delay(delay_seconds=2.0):
    """Add delay to respect Google Sheets API limits (60 requests/minute = 1/second)"""
    print(f"⏱️  Sheets API delay ({delay_seconds}s)...")
    time.sleep(delay_seconds)

# Google Sheets API rate limiting utilities
def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls that includes rate limiting"""
    sheets_api_delay(2)  # 2 second delay before API call
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if "429" in str(e) or "Quota exceeded" in str(e):
            print("⚠️  Rate limit hit, waiting longer...")
            time.sleep(10)  # Wait 10 seconds on rate limit
            return func(*args, **kwargs)
        raise

# Configure pytest to run tests with delays
def pytest_runtest_teardown(item, nextitem):
    """Add delay between tests to prevent Google Sheets API overload"""
    if nextitem:
        print(f"⏱️  Inter-test delay...")
        time.sleep(2)  # 2 second delay between tests to respect API limits 