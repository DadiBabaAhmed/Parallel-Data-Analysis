# Test Suite Documentation

## Overview

This comprehensive test suite ensures the entire Parallel Data Analysis Framework works correctly. The tests cover:

- **Data Loading**: CSV, JSON, Parquet, Avro file format support
- **Data Analysis**: Statistical analysis, aggregation, MapReduce operations
- **Visualization**: Graph generation and file output
- **Web API**: REST endpoints, CORS, error handling
- **Application Pipeline**: End-to-end integration and error handling

## Test Organization

### Test Files

- **`test_data_loader.py`** - Tests for data ingestion module
  - CSV, JSON, Parquet, Avro loading
  - Schema inference and validation
  - Error handling for unsupported formats
  - Data integrity checks

- **`test_analyzer.py`** - Tests for statistical analysis and aggregation
  - Statistical analysis (mean, stddev, percentiles, correlation)
  - Data aggregation and grouping
  - MapReduce operations (word count, etc.)
  - Handling of edge cases (null values, empty data)

- **`test_graphs.py`** - Tests for visualization generation
  - Distribution plots
  - Correlation heatmaps
  - File output and PNG format validation
  - Graph naming conventions

- **`test_api.py`** - Tests for Web API endpoints
  - `/api/health` - Health check
  - `/api/hosts` - Container information
  - `/api/input-files` - Available input files
  - `/api/results` - Analysis results
  - `/api/trigger` - Job triggering
  - `/api/jobs` - Job management
  - `/api/job/<id>` - Job details
  - CORS headers and error handling

- **`test_main_smoke.py`** - Integration tests for the main application
  - Initialization of all components
  - Output directory creation
  - Spark configuration
  - Performance monitoring
  - Full pipeline execution

- **`conftest.py`** - Pytest fixtures and configuration
  - SparkSession fixtures
  - Test data generation (DataFrames, CSV, JSON files)
  - Temporary directory management
  - Output directory setup

## Running Tests

### Run All Tests
```bash
cd Script
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_data_loader.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_analyzer.py::TestStatisticalAnalysis -v
```

### Run Specific Test
```bash
pytest tests/test_data_loader.py::TestDataLoaderCSV::test_load_csv_basic -v
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Run smoke tests (basic functionality)
pytest tests/ -m smoke -v

# Run API tests
pytest tests/ -m api -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests in Parallel (faster)
```bash
pytest tests/ -n auto
```
(Requires `pytest-xdist` package)

## Test Categories

### Unit Tests (Individual Components)
Tests isolated functionality of individual modules:
- DataLoader file reading
- DataAnalyzer calculations
- GraphGenerator visualization
- Error handling

**Run with:** `pytest tests/ -m unit`

### Integration Tests (Component Interaction)
Tests how components work together:
- API endpoint responses
- Database operations with DataLoader
- Analysis pipeline with multiple stages

**Run with:** `pytest tests/ -m integration`

### Smoke Tests (Basic Functionality)
Quick tests verifying the application starts and basic operations work:
- Application initialization
- Component setup
- Basic pipeline execution

**Run with:** `pytest tests/ -m smoke`

## Test Fixtures

### Spark Fixtures (`conftest.py`)

- **`spark_session`** - Local Spark session for testing
- **`spark_df`** - Sample DataFrame with multiple data types
- **`large_spark_df`** - Larger DataFrame for performance tests
- **`numeric_only_df`** - DataFrame with only numeric columns
- **`string_only_df`** - DataFrame with only string columns

### File Fixtures

- **`test_csv_file`** - Temporary CSV file
- **`test_json_file`** - Temporary JSON file
- **`temp_test_dir`** - Temporary directory for test files
- **`test_output_dirs`** - Pre-created output directory structure

### Utility Fixtures

- **`api_client`** - Flask test client for API testing
- **`timestamp`** - Current timestamp in test format

## Key Test Assertions

### DataLoader Tests
✓ Supports CSV, JSON, Parquet, Avro formats
✓ Correctly infers numeric and string data types
✓ Handles multiline CSV fields
✓ Validates data integrity
✓ Handles missing files gracefully
✓ Supports large files

### DataAnalyzer Tests
✓ Calculates descriptive statistics (mean, stddev, min, max, percentiles)
✓ Computes correlation matrices
✓ Performs aggregations with grouping
✓ Implements MapReduce patterns
✓ Handles null values correctly
✓ Works with empty datasets
✓ Produces consistent results
✓ Doesn't modify input data

### GraphGenerator Tests
✓ Creates distribution plots
✓ Generates correlation heatmaps
✓ Produces valid PNG files
✓ Uses timestamp in filenames
✓ Handles missing numeric columns
✓ Works with large datasets
✓ Cleans up matplotlib resources

### API Tests
✓ Health check returns 200 OK
✓ All endpoints return valid JSON
✓ POST endpoints accept JSON payloads
✓ Error endpoints return appropriate status codes
✓ CORS headers present
✓ Handles malformed input
✓ Missing required fields handled gracefully
✓ Invalid endpoints return 404

### Main Application Tests
✓ Initializes all components
✓ Creates output directories
✓ Configures Spark properly
✓ Tracks performance metrics
✓ Handles errors gracefully
✓ Supports multiple analysis types
✓ Multiple instances don't conflict

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd Script
        pytest tests/ -v --cov=src
```

### Local CI/CD Testing
```bash
# Full test pipeline
cd Script
pytest tests/ -v --cov=src --cov-report=html
```

## Troubleshooting

### Tests Fail with "No module named 'src'"
Solution: Run pytest from the `Script` directory:
```bash
cd Script
pytest tests/
```

### Matplotlib Errors
Solution: Already handled in conftest.py with `matplotlib.use('Agg')`

### Spark Java Errors
Solution: Ensure Java is installed and JAVA_HOME is set:
```bash
java -version
```

### Port Already in Use (API Tests)
Solution: Close any existing Flask/API processes:
```bash
lsof -i :5000  # Find process
kill -9 <PID>  # Kill process
```

## Performance

- **Unit tests**: ~1-2 seconds total
- **Integration tests**: ~3-5 seconds total
- **Full test suite**: ~10-15 seconds total
- **With coverage report**: ~20-30 seconds total

## Test Coverage Goals

- **Target**: >80% code coverage
- **Critical modules**: >90% coverage (DataLoader, DataAnalyzer, API)
- **Current**: Run `pytest --cov` to check

## Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_<module>.py`
3. Create test classes: `TestClassName`
4. Create test methods: `test_function_name`
5. Add fixtures as needed in conftest.py
6. Use descriptive assertions
7. Mark with appropriate decorator: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.

Example:
```python
def test_new_feature(spark_session, spark_df):
    """Test that new feature works correctly"""
    # Arrange
    analyzer = DataAnalyzer(spark_session, ErrorHandler("test"))
    
    # Act
    result = analyzer.new_method(spark_df)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive test names
3. **Fixtures**: Reuse fixtures from conftest.py
4. **Mocking**: Mock external dependencies
5. **Error Cases**: Test both success and failure paths
6. **Data**: Use small test datasets for speed
7. **Assertions**: Clear, specific assertions
8. **Cleanup**: Fixtures handle cleanup automatically

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

- ✅ Fast execution (< 30 seconds)
- ✅ No external dependencies required
- ✅ Self-contained test data
- ✅ Proper error reporting
- ✅ Coverage tracking
- ✅ Deterministic results

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [PySpark Testing](https://spark.apache.org/docs/latest/api/python/testing.html)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
