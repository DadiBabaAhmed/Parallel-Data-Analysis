"""
The original `src.mapreduce_job` module has been moved to
`Script/spark_jobs/mapreduce_job.py` and the package-level import
path is now `spark_jobs.mapreduce_job`.

Please update imports to:

	from spark_jobs.mapreduce_job import MapReduceJob

The file remains as a pointer to avoid silent failures but intentionally
raises an ImportError to force updating code paths.
"""

raise ImportError(
	"src.mapreduce_job was moved to spark_jobs.mapreduce_job; "
	"update imports to 'from spark_jobs.mapreduce_job import MapReduceJob'"
)
