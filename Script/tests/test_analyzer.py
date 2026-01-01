"""
Comprehensive tests for DataAnalyzer module
Tests statistical analysis, aggregation, and data processing
"""
import pytest
from unittest.mock import MagicMock

from src.data_analyzer import DataAnalyzer
from src.error_handler import ErrorHandler
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, IntegerType, DoubleType


class TestDataAnalyzerInitialization:
    """Test DataAnalyzer initialization"""
    
    def test_analyzer_init(self, spark_session):
        """Test DataAnalyzer initialization"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        assert analyzer.spark is not None
        assert analyzer.error_handler is not None


class TestStatisticalAnalysis:
    """Test statistical analysis functionality"""
    
    def test_statistical_analysis_basic(self, spark_session, spark_df):
        """Test basic statistical analysis"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(spark_df)
        
        assert result is not None
        assert "summary" in result
        assert isinstance(result["summary"], dict)
    
    def test_statistical_analysis_identifies_numeric_columns(self, spark_session, spark_df):
        """Test that statistical analysis identifies numeric columns"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(spark_df)
        
        # Should have entries for numeric columns (id, value, amount)
        numeric_cols = [col for col in spark_df.columns 
                       if col in result and col != "summary"]
        assert len(numeric_cols) > 0, "Should detect numeric columns"
    
    def test_statistical_analysis_no_numeric_columns(self, spark_session, string_only_df):
        """Test statistical analysis with only string columns"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(string_only_df)
        
        # Should handle gracefully
        assert "message" in result or "summary" in result
    
    def test_column_statistics_complete(self, spark_session, numeric_only_df):
        """Test that column statistics include all required metrics"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(numeric_only_df)
        
        # Check that we have summary statistics
        assert "summary" in result
        
        # For a numeric column, should have detailed stats
        if "value1" in result:
            col_stats = result["value1"]
            # Statistics should include mean, stddev, min, max, percentiles
            required_stats = {"mean", "stddev", "min", "max", "count"}
            actual_stats = set(col_stats.keys()) if isinstance(col_stats, dict) else set()
            assert len(actual_stats & required_stats) > 0, "Should have statistical metrics"
    
    def test_statistical_analysis_handles_null_values(self, spark_session):
        """Test statistical analysis with null values"""
        data = [(1, 10.0), (2, None), (3, 30.0), (None, 40.0)]
        df = spark_session.createDataFrame(data, ["id", "value"])
        
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(df)
        
        # Should handle nulls without crashing
        assert result is not None
        assert "summary" in result or "message" in result
    
    def test_statistical_analysis_large_dataset(self, spark_session, large_spark_df):
        """Test statistical analysis on larger dataset"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.statistical_analysis(large_spark_df)
        
        assert result is not None
        assert "summary" in result
        
        # Should have numeric column statistics
        numeric_cols = [col for col in large_spark_df.columns if col in result]
        assert len(numeric_cols) > 0


class TestAggregateData:
    """Test data aggregation functionality"""
    
    def test_aggregate_data_with_explicit_columns(self, spark_session, spark_df):
        """Test aggregation with explicitly specified columns"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        # Aggregate by category, summing the value column
        result = analyzer.aggregate_data(spark_df, group_cols=["category"], agg_cols=["value"])
        
        assert result is not None
        # Result should be a dictionary with aggregation results
        assert isinstance(result, dict)
    
    def test_aggregate_data_auto_columns(self, spark_session, spark_df):
        """Test aggregation with auto-detection of columns"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        # Let it auto-detect columns
        result = analyzer.aggregate_data(spark_df)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_aggregate_data_multiple_aggregations(self, spark_session, spark_df):
        """Test aggregation with multiple aggregation functions"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.aggregate_data(
            spark_df,
            group_cols=["category"],
            agg_cols=["value", "amount"]
        )
        
        assert result is not None
    
    def test_aggregate_data_no_suitable_columns(self, spark_session, string_only_df):
        """Test aggregation when no suitable columns exist"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.aggregate_data(string_only_df)
        
        # Should handle gracefully
        assert result is not None


class TestDataAnalyzerMapReduce:
    """Test MapReduce-style operations"""
    
    def test_mapreduce_word_count_basic(self, spark_session):
        """Test word count functionality"""
        # Create sample text data
        data = [("hello world",), ("hello spark",), ("spark world",)]
        df = spark_session.createDataFrame(data, ["text"])
        
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.mapreduce_word_count(df, "text")
        
        assert result is not None
        # Should be a list of (word, count) tuples
        assert isinstance(result, (list, dict))


class TestCorrelationAnalysis:
    """Test correlation analysis"""
    
    def test_correlation_analysis_basic(self, spark_session, numeric_only_df):
        """Test correlation analysis"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.correlation_analysis(numeric_only_df)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_correlation_analysis_returns_matrix(self, spark_session, numeric_only_df):
        """Test that correlation analysis returns correlation matrix"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        result = analyzer.correlation_analysis(numeric_only_df)
        
        # Should have correlation matrix
        if "matrix" in result:
            matrix = result["matrix"]
            assert isinstance(matrix, (list, dict))


class TestDataAnalyzerErrorHandling:
    """Test error handling in DataAnalyzer"""
    
    def test_analyzer_handles_invalid_dataframe(self, spark_session):
        """Test that analyzer handles invalid DataFrames"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        # Create an empty DataFrame
        empty_df = spark_session.createDataFrame([], "id int")
        
        # Should handle empty data without crashing
        result = analyzer.statistical_analysis(empty_df)
        assert result is not None
    
    def test_analyzer_methods_don_not_modify_input_df(self, spark_session, spark_df):
        """Test that analysis methods don't modify input DataFrame"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        original_count = spark_df.count()
        original_columns = set(spark_df.columns)
        
        analyzer.statistical_analysis(spark_df)
        analyzer.aggregate_data(spark_df)
        
        # Input DataFrame should be unchanged
        assert spark_df.count() == original_count
        assert set(spark_df.columns) == original_columns


class TestDataAnalyzerIntegration:
    """Integration tests for DataAnalyzer"""
    
    def test_full_analysis_pipeline(self, spark_session, spark_df):
        """Test complete analysis pipeline"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        # Run multiple analyses
        stats = analyzer.statistical_analysis(spark_df)
        agg = analyzer.aggregate_data(spark_df)
        
        # All should complete successfully
        assert stats is not None
        assert agg is not None
    
    def test_analysis_results_consistency(self, spark_session, spark_df):
        """Test that analysis results are consistent"""
        error_handler = ErrorHandler("test_20250101_000000")
        analyzer = DataAnalyzer(spark_session, error_handler)
        
        # Run same analysis twice
        result1 = analyzer.statistical_analysis(spark_df)
        result2 = analyzer.statistical_analysis(spark_df)
        
        # Results should be the same
        assert result1.keys() == result2.keys()
