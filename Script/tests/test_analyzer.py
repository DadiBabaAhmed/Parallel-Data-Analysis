import pytest
from unittest.mock import MagicMock, Mock
from src.data_analyzer import DataAnalyzer
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType


def test_analyzer_initialization():
    """Test DataAnalyzer initialization"""
    spark = MagicMock()
    error_handler = MagicMock()
    analyzer = DataAnalyzer(spark, error_handler)
    assert analyzer.spark == spark
    assert analyzer.error_handler == error_handler


def test_statistical_analysis_no_numeric_columns():
    """Test statistical analysis with no numeric columns"""
    spark = MagicMock()
    error_handler = MagicMock()
    analyzer = DataAnalyzer(spark, error_handler)

    df = MagicMock()
    # Mock schema with only string fields
    field = MagicMock()
    field.name = "name"
    field.dataType = StringType()
    df.schema.fields = [field]

    result = analyzer.statistical_analysis(df)
    assert "message" in result
    assert "No numeric columns found" in result["message"]


def test_statistical_analysis_with_numeric_columns(spark_session):
    """Test statistical analysis with numeric columns"""
    error_handler = MagicMock()
    analyzer = DataAnalyzer(spark_session, error_handler)

    # Create a real DataFrame with numeric columns
    data = [(1, 10), (2, 20), (3, 30), (4, 40)]
    df = spark_session.createDataFrame(data, ["id", "value"])

    result = analyzer.statistical_analysis(df)
    assert "summary" in result
    assert "value" in result


def test_aggregate_data_no_suitable_columns():
    """Test aggregation with no suitable columns"""
    spark = MagicMock()
    error_handler = MagicMock()
    error_handler.timestamp = "20231201_120000"
    analyzer = DataAnalyzer(spark, error_handler)

    df = MagicMock()
    df.schema.fields = []

    result = analyzer.aggregate_data(df)
    assert "message" in result


def test_correlation_analysis_insufficient_columns():
    """Test correlation analysis with less than 2 numeric columns"""
    spark = MagicMock()
    error_handler = MagicMock()
    analyzer = DataAnalyzer(spark, error_handler)

    df = MagicMock()
    field = MagicMock()
    field.name = "value"
    field.dataType = IntegerType()
    df.schema.fields = [field]

    result = analyzer.correlation_analysis(df)
    assert "message" in result
    assert "at least 2 numeric columns" in result["message"]
