import pytest
from unittest.mock import MagicMock
from spark_jobs.aggregation_job import AggregationJob
from spark_jobs.mapreduce_job import MapReduceJob
from spark_jobs.statistical_analysis import StatisticalAnalysis


def test_aggregation_job_instance():
    job = AggregationJob()
    assert job is not None


def test_mapreduce_word_count():
    job = MapReduceJob()
    df = MagicMock()
    result = job.word_count(df, "text")
    # For now we just check a Spark DataFrame-like object is returned
    assert result is not None


def test_statistical_analysis_run():
    job = StatisticalAnalysis()
    df = MagicMock()
    summary = job.describe(df)
    assert summary is not None
