"""
spark_jobs package — container for reusable Spark job modules.

This package exposes MapReduce, Aggregation and Statistical helper classes
used by the higher-level example and analysis scripts.
"""

from .mapreduce_job import MapReduceJob
from .aggregation_job import AggregationJob
from .statistical_analysis import StatisticalAnalysis

__all__ = ["MapReduceJob", "AggregationJob", "StatisticalAnalysis"]
