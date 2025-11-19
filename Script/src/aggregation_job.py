"""
The original `src.aggregation_job` module has been moved to
`Script/spark_jobs/aggregation_job.py` and the package-level import
path is now `spark_jobs.aggregation_job`.

Please update imports to:

    from spark_jobs.aggregation_job import AggregationJob

The file remains as a pointer to avoid silent failures but intentionally
raises an ImportError to force updating code paths.
"""

raise ImportError(
    "src.aggregation_job was moved to spark_jobs.aggregation_job; "
    "update imports to 'from spark_jobs.aggregation_job import AggregationJob'"
)
