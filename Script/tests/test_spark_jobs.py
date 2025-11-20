import pytest
from unittest.mock import MagicMock, Mock
from spark_jobs.aggregation_job import AggregationJob
from spark_jobs.mapreduce_job import MapReduceJob
from spark_jobs.statistical_analysis import StatisticalAnalysis


def test_aggregation_job_instance():
    """Test AggregationJob instantiation"""
    job = AggregationJob()
    assert job is not None


def test_aggregation_multi_level():
    """Test multi-level aggregation"""
    job = AggregationJob()
    df = MagicMock()

    # Mock groupBy and agg chain
    mock_result = MagicMock()
    df.groupBy.return_value.agg.return_value = mock_result

    result = job.multi_level_aggregation(df, ['category'], ['value'])
    assert result is not None
    df.groupBy.assert_called_once_with(['category'])


def test_aggregation_cube():
    """Test cube aggregation"""
    job = AggregationJob()
    df = MagicMock()

    mock_result = MagicMock()
    df.cube.return_value.agg.return_value = mock_result

    result = job.cube_aggregation(df, ['dim1', 'dim2'], {'measure': 'sum'})
    assert result is not None
    df.cube.assert_called_once()


def test_aggregation_pivot():
    """Test pivot aggregation"""
    job = AggregationJob()
    df = MagicMock()

    mock_result = MagicMock()
    df.groupBy.return_value.pivot.return_value.sum.return_value = mock_result

    result = job.pivot_aggregation(df, 'index_col', 'pivot_col', 'value_col', 'sum')
    assert result is not None


def test_mapreduce_word_count():
    """Test MapReduce word count operation"""
    job = MapReduceJob()
    df = MagicMock()

    # Mock the chain of operations
    mock_words = MagicMock()
    mock_filtered = MagicMock()
    mock_lower = MagicMock()
    mock_grouped = MagicMock()
    mock_result = MagicMock()

    df.select.return_value = mock_words
    mock_words.filter.return_value = mock_filtered
    mock_filtered.withColumn.return_value = mock_lower
    mock_lower.groupBy.return_value.count.return_value = mock_grouped
    mock_grouped.orderBy.return_value = mock_result

    result = job.word_count(df, "text")
    assert result is not None


def test_mapreduce_group_sum():
    """Test MapReduce group sum operation"""
    job = MapReduceJob()
    df = MagicMock()

    mock_result = MagicMock()
    df.select.return_value.groupBy.return_value.agg.return_value.orderBy.return_value = mock_result

    result = job.group_sum(df, "category", "amount")
    assert result is not None


def test_mapreduce_distinct_count():
    """Test distinct count operation"""
    job = MapReduceJob()
    df = MagicMock()

    df.select.return_value.distinct.return_value.count.return_value = 42

    result = job.distinct_count(df, "column")
    assert result == 42


def test_statistical_analysis_descriptive():
    """Test descriptive statistics"""
    job = StatisticalAnalysis()
    df = MagicMock()

    # Mock schema fields
    field1 = MagicMock()
    field1.name = "value"
    field1.dataType = MagicMock()
    df.schema.fields = [field1]

    # Mock the select and collect chain
    mock_row = MagicMock()
    mock_row.asDict.return_value = {
        'count': 100,
        'null_count': 0,
        'mean': 50.5,
        'stddev': 10.2,
        'min': 10,
        'max': 90,
        'q1': 30,
        'median': 50,
        'q3': 70,
        'skewness': 0.1,
        'kurtosis': -0.5
    }
    df.select.return_value.collect.return_value = [mock_row]
    df.filter.return_value.count.return_value = 5

    result = job.descriptive_statistics(df, ['value'])
    assert 'value' in result
    assert result['value']['mean'] == 50.5


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


def test_statistical_analysis_detect_anomalies_zscore():
    """Test anomaly detection using z-score method"""
    job = StatisticalAnalysis()
    df = MagicMock()

    mock_stats = MagicMock()
    mock_stats.__getitem__ = lambda self, key: {'mean': 50, 'stddev': 10}[key]
    df.select.return_value.collect.return_value = [mock_stats]

    mock_result = MagicMock()
    df.withColumn.return_value.withColumn.return_value = mock_result

    result = job.detect_anomalies(df, 'value', method='zscore', threshold=3)
    assert result is not None


def test_statistical_analysis_frequency_distribution():
    """Test frequency distribution calculation"""
    job = StatisticalAnalysis()
    df = MagicMock()

    # Mock min/max
    df.select.return_value.collect.return_value = [(0, 100)]

    # Mock frequency results
    mock_row1 = {'bin': 0, 'count': 20}
    mock_row2 = {'bin': 1, 'count': 30}
    df.withColumn.return_value.groupBy.return_value.count.return_value.orderBy.return_value.collect.return_value = [
        mock_row1, mock_row2
    ]

    result = job.frequency_distribution(df, 'value', bins=10)
    assert isinstance(result, list)
    assert len(result) > 0
