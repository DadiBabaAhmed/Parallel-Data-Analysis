import pytest
from unittest.mock import MagicMock, Mock
from spark_jobs.aggregation_job import AggregationJob
from spark_jobs.mapreduce_job import MapReduceJob
from spark_jobs.statistical_analysis import StatisticalAnalysis


def test_aggregation_job_instance():
    """Test AggregationJob instantiation"""
    job = AggregationJob()
    assert job is not None


def test_aggregation_multi_level(spark_df):
    """Test multi-level aggregation"""
    job = AggregationJob()
    result = job.multi_level_aggregation(spark_df, ['category'], ['value'])
    assert result is not None
    assert result.count() > 0


def test_aggregation_cube(spark_session):
    """Test cube aggregation"""
    job = AggregationJob()
    data = [("X", "A", 10), ("X", "B", 20), ("Y", "A", 30)]
    df = spark_session.createDataFrame(data, ["dim1", "dim2", "measure"])

    result = job.cube_aggregation(df, ['dim1', 'dim2'], {'measure': 'sum'})
    assert result is not None
    assert result.count() > 0


def test_aggregation_pivot():
    """Test pivot aggregation"""
    job = AggregationJob()
    df = MagicMock()

    mock_result = MagicMock()
    df.groupBy.return_value.pivot.return_value.sum.return_value = mock_result

    result = job.pivot_aggregation(df, 'index_col', 'pivot_col', 'value_col', 'sum')
    assert result is not None


def test_mapreduce_word_count(spark_session):
    """Test MapReduce word count operation"""
    job = MapReduceJob()
    data = [("hello world",), ("hello spark",), ("world spark",)]
    df = spark_session.createDataFrame(data, ["text"])

    result = job.word_count(df, "text")
    assert result is not None
    assert result.count() > 0


def test_mapreduce_group_sum(spark_session):
    """Test MapReduce group sum operation"""
    job = MapReduceJob()
    data = [("A", 10), ("B", 20), ("A", 30), ("B", 40)]
    df = spark_session.createDataFrame(data, ["category", "amount"])

    result = job.group_sum(df, "category", "amount")
    assert result is not None
    assert result.count() > 0


def test_mapreduce_distinct_count():
    """Test distinct count operation"""
    job = MapReduceJob()
    df = MagicMock()

    df.select.return_value.distinct.return_value.count.return_value = 42

    result = job.distinct_count(df, "column")
    assert result == 42


def test_statistical_analysis_descriptive(spark_df):
    """Test descriptive statistics"""
    job = StatisticalAnalysis()
    result = job.descriptive_statistics(spark_df, ['value'])
    assert 'value' in result
    assert 'mean' in result['value']


def test_statistical_analysis_correlation_matrix():
    """Test correlation matrix calculation"""
    job = StatisticalAnalysis()
    df = MagicMock()

    # Mock schema
    field1 = MagicMock()
    field1.name = "col1"
    field1.dataType = MagicMock()
    field2 = MagicMock()
    field2.name = "col2"
    field2.dataType = MagicMock()
    df.schema.fields = [field1, field2]

    # Mock correlation values
    df.stat.corr.return_value = 0.75

    result = job.correlation_matrix(df, ['col1', 'col2'])
    assert 'col1' in result
    assert 'col2' in result


def test_statistical_analysis_detect_anomalies_zscore(spark_df):
    """Test anomaly detection using z-score method"""
    job = StatisticalAnalysis()
    result = job.detect_anomalies(spark_df, 'value', method='zscore', threshold=3)
    assert result is not None
    assert result.count() >= 0


def test_statistical_analysis_frequency_distribution(spark_df):
    """Test frequency distribution calculation"""
    job = StatisticalAnalysis()
    result = job.frequency_distribution(spark_df, 'value', bins=10)
    assert isinstance(result, list)
    assert len(result) > 0
