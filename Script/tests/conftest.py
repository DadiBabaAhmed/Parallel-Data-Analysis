"""
Test configuration and fixtures
"""
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests

from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_session():
    """Create a SparkSession for testing"""
    spark = SparkSession.builder \
        .appName("test") \
        .master("local[1]") \
        .config("spark.ui.enabled", "false") \
        .config("spark.sql.shuffle.partitions", "1") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()


@pytest.fixture(scope="function")
def spark_df(spark_session):
    """Create a test Spark DataFrame"""
    data = [
        ("A", 1, 10.0),
        ("B", 2, 20.0),
        ("A", 3, 30.0),
        ("B", 4, 40.0),
    ]
    columns = ["category", "id", "value"]
    return spark_session.createDataFrame(data, columns)
