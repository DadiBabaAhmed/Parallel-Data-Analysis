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


def test_statistical_analysis_with_numeric_columns():
    """Test statistical analysis with numeric columns"""
    spark = MagicMock()
    error_handler = MagicMock()
    analyzer = DataAnalyzer(spark, error_handler)

    df = MagicMock()

    # Mock schema with numeric field
    field = MagicMock()
    field.name = "value"
    field.dataType = IntegerType()
    df.schema.fields = [field]

    # Mock describe result
    describe_df = MagicMock()
    describe_df.toPandas.return_value.to_dict.return_value = {"summary": ["count", "mean"]}
    df.select.return_value.describe.return_value = describe_df

    # Mock column statistics
    mock_row = MagicMock()
    mock_row.asDict.return_value = {
        'mean': 10.5,
        'stddev': 2.5,
        'min': 5,
        'max': 20,
        'count': 100
    }
    df.select.return_value.collect.return_value = [mock_row]

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
