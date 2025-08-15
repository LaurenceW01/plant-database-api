# Advanced Query System Tests

Comprehensive test suite for the new MongoDB-style advanced query system.

## Test Files

### 1. `test_advanced_query_endpoint.py`
**Full endpoint integration tests**
- Tests the complete `/api/garden/query` endpoint
- Real-world query scenarios from the proposal
- Response format validation
- Error handling verification
- **Requires**: Full Flask app context and database access

### 2. `test_advanced_query_components.py`
**Unit tests for individual components**
- Query parser logic
- Filter operations 
- Response formatting
- Operator validation
- **Requires**: No Flask app context (faster execution)

### 3. `run_advanced_query_tests.py`
**Standalone test runner**
- Runs tests independently from regression suite
- Includes smoke test functionality
- Colored output and detailed reporting

## Running Tests

### Option 1: Using the Test Runner (Recommended)
```bash
python tests/run_advanced_query_tests.py
```

### Option 2: Using pytest directly
```bash
# Run all advanced query tests
pytest tests/test_advanced_query_endpoint.py tests/test_advanced_query_components.py -v

# Run only endpoint tests
pytest tests/test_advanced_query_endpoint.py -v

# Run only component tests
pytest tests/test_advanced_query_components.py -v
```

### Option 3: Run specific test classes
```bash
# Test only real-world scenarios
pytest tests/test_advanced_query_endpoint.py::TestRealWorldQueryScenarios -v

# Test only parser components
pytest tests/test_advanced_query_components.py::TestQueryParser -v
```

## Test Scenarios Covered

### Core Functionality
- ✅ Endpoint existence and basic responses
- ✅ Empty filters (return all data)
- ✅ Single table filtering (plants, locations, containers)
- ✅ Multi-table filtering with joins
- ✅ All response formats (summary, detailed, minimal, ids_only)
- ✅ Sorting and limiting
- ✅ Error handling for invalid queries

### MongoDB-style Operators
- ✅ `$eq` (equals) and `$ne` (not equals)
- ✅ `$in` (in array) and `$nin` (not in array)
- ✅ `$gt`, `$gte`, `$lt`, `$lte` (numeric comparisons)
- ✅ `$regex` (pattern matching with case insensitive options)
- ✅ `$exists` (field has value)
- ✅ `$contains` (substring matching)

### Real-World Query Scenarios
Based on the proposal document:

1. **"Plants on patio in small pots"**
   - Multi-table filtering (locations + containers)
   - Summary response format
   - Demonstrates the 26-calls → 1-call optimization

2. **"Sun-loving plants that need daily watering"**
   - Plant-specific filtering
   - Multiple field conditions
   - Detailed response format

3. **"Plastic containers with plants that have photos"**
   - Container material filtering
   - Photo existence checking
   - Combined conditions

4. **"High-sun locations (8+ hours) in ceramic containers"**
   - Numeric comparisons
   - Multi-table joins
   - Location + container filtering

5. **"Recent additions to the garden"**
   - Date-based filtering
   - Sorting by date
   - Limited results

### Error Handling
- ✅ Missing request body
- ✅ Invalid operators
- ✅ Invalid field names
- ✅ Invalid response formats
- ✅ Invalid regex patterns
- ✅ Limit validation
- ✅ Malformed queries

## Expected Test Results

### Success Criteria
- All basic functionality tests pass
- Real-world scenarios execute without errors
- Error handling catches invalid inputs gracefully
- Response formats match specifications
- Performance is acceptable (single API call instead of multiple)

### Performance Expectations
The main goal is replacing multiple API calls with a single optimized call:

- **Before**: "Plants on patio in small pots" = 1 search + 26 individual context calls = **27 API calls**
- **After**: Same query = 1 advanced query call = **1 API call** (96% reduction)

## Test Environment Setup

### Requirements
```bash
# Install test dependencies
pip install pytest flask

# Ensure project modules are accessible
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Mock Data Considerations
These tests work with your actual database data, so results will vary based on:
- Number of plants in your database
- Locations and containers configured
- Field data completeness

### Integration with Existing Tests
These tests are **intentionally separate** from the regression test suite to allow:
- Independent development and debugging
- Faster iteration during implementation
- Separate CI/CD pipeline integration
- Easy inclusion into regression suite later

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Connection Issues**
- Verify your Google Sheets credentials are configured
- Check that the spreadsheet ID is correct
- Ensure you have internet connectivity

**Flask App Context Errors**
- The endpoint tests require a full Flask app
- Component tests can run without Flask context

### Debug Mode
Run tests with extra verbosity:
```bash
pytest tests/test_advanced_query_endpoint.py -v -s --tb=long
```

## Next Steps

1. **Run the tests** to verify the advanced query system works
2. **Review test results** and fix any failing scenarios
3. **Add more specific tests** for your unique data patterns
4. **Integrate with regression suite** when ready
5. **Add performance benchmarks** to measure the 26→1 call optimization

## Contributing

When adding new query capabilities:
1. Add tests to `test_advanced_query_components.py` for unit testing
2. Add integration tests to `test_advanced_query_endpoint.py` for full scenarios
3. Update this README with new test scenarios
4. Ensure all tests pass before committing changes
