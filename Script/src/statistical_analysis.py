"""
The original `src.statistical_analysis` module has been moved to
`Script/spark_jobs/statistical_analysis.py` and the package-level import
path is now `spark_jobs.statistical_analysis`.

Please update imports to:

    from spark_jobs.statistical_analysis import StatisticalAnalysis

The file remains as a pointer to avoid silent failures but intentionally
raises an ImportError to force updating code paths.
"""

raise ImportError(
    "src.statistical_analysis was moved to spark_jobs.statistical_analysis; "
    "update imports to 'from spark_jobs.statistical_analysis import StatisticalAnalysis'"
)
