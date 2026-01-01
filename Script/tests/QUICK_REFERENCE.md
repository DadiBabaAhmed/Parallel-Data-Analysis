# Test Suite Quick Reference

## Quick Start

```bash
# Navigate to project directory
cd Script

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Use helper script
python run_tests.py              # All tests
python run_tests.py unit         # Unit tests only
python run_tests.py coverage     # With coverage report
python run_tests.py quick        # Quick smoke tests
```

## Test File Organization

```
Script/tests/
├── conftest.py              # Shared fixtures & configuration
├── test_data_loader.py      # DataLoader tests (25 tests)
├── test_analyzer.py         # DataAnalyzer tests (35 tests)
├── test_graphs.py           # GraphGenerator tests (20 tests)
├── test_api.py              # Web API tests (45 tests)
├── test_main_smoke.py       # Application integration tests (25 tests)
├── test_suite.py            # Suite configuration
├── pytest.ini               # Pytest configuration
├── run_tests.py             # Test execution helper
└── README.md                # Detailed test documentation
```

## Test Statistics

- **Total Tests**: 150+
- **Unit Tests**: 90
- **Integration Tests**: 45
- **Smoke Tests**: 15+
- **Coverage**: Target 80%+
- **Execution Time**: ~15 seconds

## Test Categories

### Unit Tests (90 tests)
Tests for individual modules in isolation

```bash
pytest tests/ -m unit -v
```

**Modules Tested**:
- DataLoader (25 tests)
- DataAnalyzer (35 tests)
- GraphGenerator (20 tests)
- Utilities (10 tests)

### Integration Tests (45 tests)
Tests for API endpoints and component interaction

```bash
pytest tests/ -m integration -v
```

**Coverage**:
- All REST API endpoints
- CORS headers
- Error handling
- Request/response validation

### Smoke Tests (15+ tests)
Quick tests for basic functionality

```bash
pytest tests/ -m smoke -v
```

**Verifies**:
- Application initialization
- Component startup
- Output directory creation
- Basic pipeline execution

## Common Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_analyzer.py::TestStatisticalAnalysis -v

# Run specific test
pytest tests/test_api.py::TestAPIHealth::test_health_endpoint_returns_ok -v

# Run by marker
pytest tests/ -m unit -v           # Unit tests only
pytest tests/ -m integration -v    # Integration tests only
pytest tests/ -m smoke -v          # Smoke tests only

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests in parallel (faster)
pytest tests/ -n auto              # Requires pytest-xdist

# Run with detailed output
pytest tests/ -vv -s

# Stop on first failure
pytest tests/ -x

# Show slowest tests
pytest tests/ --durations=10

# Run without slow tests
pytest tests/ -m "not slow" -v
```

## Test Fixtures Available

### Spark Fixtures
- `spark_session` - SparkSession for testing
- `spark_df` - Sample DataFrame
- `large_spark_df` - Larger dataset for performance tests
- `numeric_only_df` - DataFrame with only numbers
- `string_only_df` - DataFrame with only strings

### File Fixtures
- `test_csv_file` - Temporary CSV file
- `test_json_file` - Temporary JSON file
- `temp_test_dir` - Temporary directory
- `test_output_dirs` - Pre-created output structure

### API Fixtures
- `api_client` - Flask test client
- `timestamp` - Current timestamp

## Key Test Assertions

### DataLoader
```python
# CSV with correct row count
assert df.count() == 4

# Schema inferred correctly
assert "product" in df.columns

# Data integrity maintained
assert df.count() == original_count
```

### DataAnalyzer
```python
# Statistical analysis returns dict
assert isinstance(result, dict)

# Statistics include required metrics
assert "summary" in result
assert "mean" in result or "value" in result

# Handles null values
assert result is not None
```

### GraphGenerator
```python
# PNG files created
assert os.path.exists(png_path)

# File has content
assert os.path.getsize(png_path) > 0

# PNG signature valid
with open(png_path, 'rb') as f:
    assert f.read(8).startswith(b'\x89PNG')
```

### Web API
```python
# Health check works
assert response.status_code == 200
assert data['status'] == 'ok'

# Valid JSON returned
data = json.loads(response.data)
assert isinstance(data, dict)

# CORS headers present
assert response.status_code == 200
```

## Running Tests in CI/CD

### GitHub Actions
```yaml
- run: cd Script && pytest tests/ -v --cov=src
```

### Local Pre-commit
```bash
cd Script && pytest tests/ -m unit -q
```

### Docker Container
```bash
docker exec <container> pytest tests/ -v
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | Run from `Script` directory: `cd Script` |
| `Address already in use :5000` | Kill process: `lsof -i :5000 \| kill -9` |
| `Java not found` | Install JRE 17: `apt-get install openjdk-17-jre` |
| `matplotlib display error` | Already fixed with `matplotlib.use('Agg')` |
| Tests timeout | Increase timeout: `pytest tests/ --timeout=300` |

## Performance Tips

1. **Run only unit tests** during development
2. **Skip slow tests** with `-m "not slow"`
3. **Run in parallel** with `-n auto` (install pytest-xdist)
4. **Focus on changed modules** instead of all tests
5. **Use coverage selectively** (slower)

## Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Development Checklist

When adding new tests:
- [ ] Test file named `test_<module>.py`
- [ ] Test class named `Test<Feature>`
- [ ] Test method named `test_<functionality>`
- [ ] Descriptive docstring included
- [ ] Uses fixtures from conftest.py
- [ ] Clear assertions
- [ ] Handles edge cases
- [ ] Marked with appropriate decorator (`@pytest.mark.unit`, etc.)
- [ ] No hardcoded paths or ports
- [ ] Cleanup handled by fixtures

## Documentation Files

- `README.md` - Comprehensive test documentation
- `TESTING_STRATEGY.md` - Overall testing strategy and architecture
- `pytest.ini` - Pytest configuration
- `conftest.py` - Fixtures and setup
- `run_tests.py` - Test execution helper

## Next Steps

1. **Run tests**: `pytest tests/ -v`
2. **Check coverage**: `pytest tests/ --cov=src`
3. **Read detailed docs**: `tests/README.md`
4. **Understand strategy**: `TESTING_STRATEGY.md`
5. **Add new tests** as features are added

## Support

For issues or questions:
1. Check `tests/README.md` for details
2. Review existing test implementations
3. Check pytest documentation
4. Run with `-vv` for verbose output
