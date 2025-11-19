# Parallel Data Analysis Framework

A distributed data analysis framework using Apache Spark and Docker for parallel processing of large-scale datasets. Uses **conda-based Docker images** for reproducible, cross-platform environments.

## Features

- **Multi-Format Support**: CSV, JSON, Parquet, Avro
- **Parallel Processing**: Distributed computing using Apache Spark 3.5.0
- **Docker Containerization**: Easy deployment with conda environment for reproducibility
- **Comprehensive Analysis**:
  - Statistical analysis (mean, median, std, percentiles)
  - Data aggregation (sum, avg, min, max, count)
  - Correlation analysis
  - MapReduce operations
- **Visualization**: Automatic graph generation (distributions, correlations, aggregations)
- **Performance Monitoring**: Detailed execution metrics and node utilization
- **Error Handling**: Comprehensive error logging and recovery mechanisms

## Project Structure

```
Script/
├── src/                      # Main application code
│   ├── main.py              # Orchestrator
│   ├── data_loader.py       # Data ingestion
│   ├── data_analyzer.py     # Analysis logic
│   └── ... (9 more files)
│
├── spark_jobs/              # Spark job implementations
│   ├── aggregation_job.py
│   ├── mapreduce_job.py
│   └── statistical_analysis.py
│
├── docs/                    # Documentation (NEW)
│   ├── README.md           # Documentation index
│   ├── QUICK_REFERENCE.md  # Quick start guide
│   └── ... (3 more guides)
│
├── logs/                    # Build logs archive (NEW)
│   ├── README.md
│   └── build_log*.txt
│
├── config/                  # Configuration files
├── docker/                  # Docker configurations
│   ├── Dockerfile.master
│   └── Dockerfile.worker
│
├── output/                  # Analysis results
│   ├── general/
│   ├── statistics/
│   └── failures/
│
├── data/input/             # Input datasets
└── docker-compose.yml      # Container orchestration
```

## Prerequisites

- Docker and Docker Compose (all other dependencies included in container image)
- 22GB disk space (4 images × 5.7GB each, includes Java + Spark + conda packages)
- RAM: 8GB minimum recommended (2GB per worker + 4GB master)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd parallel-data-analysis/Script
```

### 2. Prepare Your Data

Place your data files in `data/input/`:

```bash
mkdir -p data/input
cp your_data.csv data/input/
```

### 3. Start the Cluster

```bash
# Start Spark cluster (4 containers: 1 master + 3 workers)
docker compose up -d

# Verify all containers are running
docker ps | findstr spark
```

### 4. Run Analysis

```bash
# Run analysis with conda-based Python environment
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py \
  --input /app/data/input/your_data.csv \
  --master spark://spark-master:7077 \
  --analysis full

# Results saved to output/general/
```

### 5. Stop Cluster

```bash
docker compose down -v
```

## Usage Options

### Analysis Types

```bash
# Full analysis (statistical + aggregation + correlation)
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py --input /app/data/input/data.csv --analysis full

# Statistical analysis only
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py --input /app/data/input/data.csv --analysis statistical

# Aggregation analysis only
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py --input /app/data/input/data.csv --analysis aggregation
```

### Cluster Modes

```bash
# Cluster mode (distributed) - Recommended
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py --input /app/data/input/data.csv --master spark://spark-master:7077

# Local mode (single machine, for small datasets)
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py --input /app/data/input/data.csv --master "local[*]"
```

## Monitoring

### Web UIs

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| Spark Master | http://localhost:8080 | 8080 | Cluster status & workers |
| Spark Application | http://localhost:4040 | 4040 | Job details (when running) |
| Worker 1 | http://localhost:8081 | 8081 | Worker node 1 status |
| Worker 2 | http://localhost:8082 | 8082 | Worker node 2 status |
| Worker 3 | http://localhost:8083 | 8083 | Worker node 3 status |

### Health Check Status

The cluster includes automatic health checks for reliability:

```bash
# View health status (shows healthy/unhealthy for each container)
docker-compose ps

# Get detailed health info
docker inspect spark-master | grep -A 10 Health

# Verify cluster is ready before running analysis
make test-health
```

**Health checks ensure:**
- ✅ Master Web UI is responding
- ✅ Workers are connected and ready
- ✅ Automatic restart on failure
- ✅ Better error messages for users

See `docs/HEALTH_CHECKS_CI_CD_GUIDE.md` for detailed health check documentation.

### Output Files

After analysis completion, check:

1. **General Output** (`output/general/`):
   - `results_[timestamp].csv` - Processed data (limited preview)
   - `results_[timestamp]_spark/` - Full Spark-written results (partitioned)
   - `analysis_[timestamp].json` - Analysis summary
   - `graphs/` - Generated visualizations

2. **Statistics** (`output/statistics/`):
   - `performance_[timestamp].json` - Performance metrics
   - `execution_summary_[timestamp].txt` - Readable summary
   - `node_utilization_[timestamp].csv` - Node usage data

3. **Failures** (`output/failures/`):
   - `errors_[timestamp].log` - Error logs
   - `failed_tasks_[timestamp].json` - Failed task details
   - `recovery_actions_[timestamp].log` - Recovery attempts

## Scaling

### Add More Workers

```bash
# Scale to 5 workers
docker-compose up -d --scale spark-worker-2=5

# Or edit docker-compose.yml and add more worker services
```

### Adjust Resources

Edit `docker-compose.yml`:

```yaml
environment:
  - SPARK_WORKER_CORES=4      # CPU cores per worker
  - SPARK_WORKER_MEMORY=4G    # Memory per worker
```

## Configuration

### Application Settings

Edit `config/app_config.yaml`:

```yaml
analysis:
  default_type: "full"
  parallelism_level: "auto"
  
monitoring:
  enabled: true
  collect_system_metrics: true
```

### Spark Settings

Edit `config/spark_config.py`:

```python
SPARK_CONFIG = {
    'spark.executor.memory': '2g',
    'spark.executor.cores': '2',
    # ... more settings
}
```

## API Usage

### Python API

```python
from src.main import ParallelDataAnalysis

# Initialize analyzer with Spark cluster
analyzer = ParallelDataAnalysis(
    app_name="MyAnalysis",
    master="spark://spark-master:7077"
)

# Run analysis
analyzer.run_analysis(
    input_path="/app/data/input/data.csv",
    analysis_type="full"
)
```

### Custom Analysis with spark_jobs

```python
from pyspark.sql import SparkSession
from src.data_loader import DataLoader
from spark_jobs.aggregation_job import AggregationJob

# Create Spark session
spark = SparkSession.builder \
    .appName("CustomAnalysis") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Load and analyze data
loader = DataLoader(spark, error_handler)
df = loader.load_data("data.csv")

# Use job classes for specific operations
job = AggregationJob()
result = job.time_series_aggregation(df, 'timestamp', 'value', interval='1 hour')
```

## Performance Tuning

### For Small Datasets (<1GB)

```yaml
spark.sql.shuffle.partitions: 8
spark.executor.memory: 1g
```

### For Large Datasets (>10GB)

```yaml
spark.sql.shuffle.partitions: 200
spark.executor.memory: 4g
spark.dynamicAllocation.enabled: true
```

### For Skewed Data

```yaml
spark.sql.adaptive.enabled: true
spark.sql.adaptive.skewJoin.enabled: true
```

## Troubleshooting

### ModuleNotFoundError: No module named 'numpy'
**Issue:** Using system Python instead of conda environment
**Fix:** Always use the conda environment Python:
```bash
# ✅ Correct
docker exec spark-master /opt/conda/envs/pda/bin/python script.py

# ❌ Wrong
docker exec spark-master python script.py
```

### Java not found / Spark won't start
**Issue:** Java not installed in container
**Fix:** Java 17 is included in the Docker image. If error persists, rebuild:
```bash
docker compose build --no-cache
docker compose up -d
```

### Containers won't start
**Issue:** Port conflicts or Docker daemon issues
**Fix:**
```bash
# Check if ports are free
netstat -ano | findstr ":7077\|:8080"

# Stop any existing containers
docker compose down -v

# Restart
docker compose up -d
```

### Analysis runs but results don't save
**Issue:** Known bug - output_path variable undefined
**Fix:** Already identified and documented. Manually copy results from Spark writer:
```bash
docker exec spark-master ls -la /app/output/general/results_*_spark/
```

### Slow Performance
**Solution:**
1. Check worker status: http://localhost:8080
2. Increase memory: Edit `docker-compose.yml` `SPARK_WORKER_MEMORY`
3. Enable adaptive execution: Already configured in `spark_config.py`

### Container Health Check
```bash
# View master logs
docker logs -f spark-master

# View worker logs
docker logs -f spark-worker-1

# Check cluster connectivity
docker exec spark-master curl -s http://localhost:8080/api/v1/applications
```

## Testing

```bash
# Run smoke tests (verify basic functionality)
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/example_test.py generate

# Quick demo
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/example_test.py quick

# Full integration test
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/example_test.py
```

## Examples

### Example 1: Sales Analysis

```bash
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/main.py \
  --input /app/data/input/sales.csv \
  --analysis full \
  --master spark://spark-master:7077
```

### Example 2: Log Analysis with MapReduce

```python
from spark_jobs.mapreduce_job import MapReduceJob

job = MapReduceJob()
word_counts = job.word_count(log_df, 'message')
word_counts.show(20)
```

### Example 3: Time Series Aggregation

```python
from spark_jobs.aggregation_job import AggregationJob

job = AggregationJob()
hourly_metrics = job.time_series_aggregation(
    df, 'timestamp', 'value', interval='1 hour'
)
```

### Example 4: Advanced Analysis with All Features

```bash
docker exec spark-master /opt/conda/envs/pda/bin/python \
  /app/src/advanced_example.py --master spark://spark-master:7077
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[docs/README.md](docs/README.md)** - Documentation index and guide
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick start and common commands
- **[docs/ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md)** - System design and data flow
- **[docs/HEALTH_CHECKS_CI_CD_GUIDE.md](docs/HEALTH_CHECKS_CI_CD_GUIDE.md)** - Health checks and CI/CD pipeline
- **[docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)** - Development roadmap and improvements
- **[docs/BUILD_VERIFICATION_REPORT.md](docs/BUILD_VERIFICATION_REPORT.md)** - Build specifications
- **[docs/BUILD_STATUS_FINAL.md](docs/BUILD_STATUS_FINAL.md)** - Build verification and next steps
- **[docs/EXECUTION_SUMMARY.md](docs/EXECUTION_SUMMARY.md)** - Pipeline execution results

Historical build logs are in `logs/` directory.

## Development & CI/CD

### Automated Testing & Quality

This project includes automated CI/CD pipeline that runs on every push:

```bash
# GitHub Actions automatically:
✅ Runs code quality checks (linting, formatting)
✅ Executes unit tests with coverage reporting
✅ Builds Docker images
✅ Performs security scans
✅ Reports results
```

**See:** [docs/HEALTH_CHECKS_CI_CD_GUIDE.md](docs/HEALTH_CHECKS_CI_CD_GUIDE.md)

### Local Development

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black isort

# Run code quality checks
make lint

# Run unit tests
make test

# Run all CI checks locally
make ci-test
```

### Making Changes

1. Create a feature branch
2. Make your changes
3. Run `make ci-test` to verify locally
4. Push to GitHub
5. CI/CD pipeline runs automatically
6. Create Pull Request when ready
7. Merge after checks pass

## License

MIT License

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review error logs in `output/failures/`

## Acknowledgments

- Apache Spark
- Docker
- Python Data Science Community
