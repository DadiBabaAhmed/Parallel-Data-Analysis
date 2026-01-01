"""
Test configuration and fixtures for the entire test suite
Provides centralized setup, teardown, and shared test data
"""
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, StringType


@pytest.fixture(scope="session")
def spark_session():
    """
    Create a SparkSession for testing
    Configured for local testing with minimal overhead
    """
    spark = SparkSession.builder \
        .appName("ParallelDataAnalysisTest") \
        .master("local[2]") \
        .config("spark.ui.enabled", "false") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.memory", "1g") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()


@pytest.fixture(scope="function")
def spark_df(spark_session):
    """Create a test Spark DataFrame with multiple data types"""
    data = [
        ("Category_A", 1, 10.0, 100),
        ("Category_B", 2, 20.0, 200),
        ("Category_A", 3, 30.0, 300),
        ("Category_B", 4, 40.0, 400),
        ("Category_A", 5, 50.0, 500),
    ]
    columns = ["category", "id", "value", "amount"]
    return spark_session.createDataFrame(data, columns)


@pytest.fixture(scope="function")
def large_spark_df(spark_session):
    """Create a larger test DataFrame for performance testing"""
    data = [(f"Cat_{i % 5}", i, float(i * 10), i * 100) for i in range(1, 1001)]
    columns = ["category", "id", "value", "amount"]
    return spark_session.createDataFrame(data, columns)


@pytest.fixture(scope="function")
def numeric_only_df(spark_session):
    """Create a DataFrame with only numeric columns"""
    data = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0), (10.0, 11.0, 12.0)]
    columns = ["value1", "value2", "value3"]
    return spark_session.createDataFrame(data, columns)


@pytest.fixture(scope="function")
def string_only_df(spark_session):
    """Create a DataFrame with only string columns (no numeric data)"""
    data = [("A",), ("B",), ("C",), ("A",), ("B",)]
    columns = ["name"]
    return spark_session.createDataFrame(data, columns)


@pytest.fixture(scope="function")
def temp_test_dir():
    """Create a temporary directory for test files, cleanup after test"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_csv_file(temp_test_dir, spark_session):
    """Create a test CSV file"""
    csv_path = os.path.join(temp_test_dir, "test_data.csv")
    
    # Create sample CSV data
    data = [
        ("Product_A", 100, 1000.0),
        ("Product_B", 200, 2000.0),
        ("Product_C", 150, 1500.0),
        ("Product_A", 120, 1200.0),
    ]
    df = spark_session.createDataFrame(data, ["product", "quantity", "price"])
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(csv_path)
    
    # Return the actual CSV file path (coalesce creates part-00000.csv)
    part_files = Path(csv_path).glob("part-*.csv")
    actual_csv = list(part_files)[0]
    
    yield str(actual_csv)


@pytest.fixture(scope="function")
def test_json_file(temp_test_dir, spark_session):
    """Create a test JSON file"""
    json_path = os.path.join(temp_test_dir, "test_data.json")
    
    data = [
        {"id": 1, "value": 10.5, "category": "A"},
        {"id": 2, "value": 20.3, "category": "B"},
        {"id": 3, "value": 15.7, "category": "A"},
    ]
    df = spark_session.createDataFrame(data)
    df.coalesce(1).write.mode("overwrite").json(json_path)
    
    part_files = Path(json_path).glob("part-*.json")
    actual_json = list(part_files)[0]
    
    yield str(actual_json)


@pytest.fixture(scope="function")
def test_output_dirs(temp_test_dir):
    """Create test output directory structure"""
    dirs = [
        os.path.join(temp_test_dir, "output", "general"),
        os.path.join(temp_test_dir, "output", "general", "graphs"),
        os.path.join(temp_test_dir, "output", "statistics"),
        os.path.join(temp_test_dir, "output", "failures"),
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    yield dirs


@pytest.fixture(scope="function")
def timestamp():
    """Generate a timestamp for tests"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
