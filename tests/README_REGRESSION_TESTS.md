# Plant Database API - Comprehensive Regression Test Suite

## Quick Start

### Run All Tests
```bash
# From project root
python tests/test_regression_runner.py --safe
```

### Quick Endpoint Validation  
```bash
python tests/test_regression_runner.py --quick
```

### Individual Test Categories
```bash
# Plant management tests
python -m pytest tests/test_regression_comprehensive.py -m "plant_management" -v

# Location intelligence tests  
python -m pytest tests/test_regression_comprehensive.py -m "location_intelligence" -v

# Test specific endpoint (e.g., the fixed care optimization)
python -m pytest tests/test_regression_comprehensive.py::TestRegressionSuite::test_garden_care_optimization -v

# Test data integrity (NEW - ensures container-location linkage works)
python -m pytest tests/test_care_optimization_data_integrity.py -v
```

## Test Coverage Summary

✅ **23+ Endpoints Tested** across 6 functional categories:

| Category | Endpoints | Status |
|----------|-----------|--------|
| Core Plant Management | 6 endpoints | ✅ Covered |
| AI-Powered Analysis | 2 endpoints | ✅ Covered |
| Health Logging | 3 endpoints | ✅ Covered |
| Photo Upload | 2 endpoints | ✅ Covered |
| Location Intelligence | 8 endpoints | ✅ Covered |
| Weather Integration | 3 endpoints | ✅ Covered |

## Key Features

- **Comprehensive Coverage**: Tests all defined API endpoints
- **Error Scenario Testing**: Validates proper error handling
- **Response Validation**: Ensures correct response structure and data types
- **Rate Limit Safe**: Designed to respect API rate limits
- **CI/CD Ready**: Suitable for automated testing pipelines
- **Performance Monitoring**: Tracks test execution times

## Test Files

- **`test_regression_comprehensive.py`** - Main test suite with all endpoint tests
- **`test_regression_runner.py`** - Enhanced test runner with reporting
- **`conftest_regression.py`** - Test configuration and fixtures
- **`README_REGRESSION_TESTS.md`** - This file

## Documentation

See **`docs/REGRESSION_TEST_SUITE_GUIDE.md`** for complete documentation including:
- Detailed usage instructions
- Test extension guidelines
- Troubleshooting guide
- Integration with development workflow

## Recently Fixed

✅ **Garden Care Optimization Endpoints** - Fixed 400 Bad Request errors:
- `/api/garden/care-optimization` (getCareOptimization)
- `/api/garden/optimize-care` (optimizeGardenCare)

Both endpoints now return proper 200 responses with optimization analysis data.

## Example Test Results

```
📊 Endpoint Validation: 6/6 endpoints responding
✅ GET /api/plants/search - 200
✅ GET /api/garden/get-metadata - 200  
✅ GET /api/garden/care-optimization - 200
✅ GET /api/locations/all - 200
✅ GET /api/logs/search - 200
✅ GET /api/weather/current - 200
```

All major endpoints are responding correctly and ready for production use.
