# Parallel Data Analysis Framework

A distributed data analysis framework using Apache Spark and Docker for parallel processing of large-scale datasets.

## Features

- **Multi-Format Support**: CSV, JSON, Parquet, Avro
- **Parallel Processing**: Distributed computing using Apache Spark
- **Docker Containerization**: Easy deployment with multiple worker nodes
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
parallel-data-analysis/
├── src/                      # Main application code
├── spark_jobs/              # Spark job implementations
├── config/                  # Configuration files
├── docker/                  # Docker configurations
├── output/                  # Analysis results
│   ├── general/            # Main results and graphs
│   ├── statistics/         # Performance metrics
│   └── failures/           # Error logs
├── data/input/             # Input datasets
└── tests/                  # Unit tests
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- 8GB+ RAM recommended

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd parallel-data-analysis
```

### 2. Prepare Your Data

Place your data files in `data/input/`:

```bash
mkdir -p data/input
cp your_data.csv data/input/
```

### 3. Start the Cluster

```bash
# Start Spark cluster with 3 workers
docker-compose up -d

# Check cluster status
docker-compose ps
```

### 4. Run Analysis

```bash
# Enter the master container
docker exec -it spark-master bash

# Run analysis
cd /app
python3 -m src.main --input data/input/your_data.csv --analysis full
```

## Usage Options

### Analysis Types

```bash
# Full analysis (statistical + aggregation + correlation)
python3 -m src.main --input data.csv --analysis full

# Statistical analysis only
python3 -m src.main --input data.csv --analysis statistical

# Aggregation analysis only
python3 -m src.main --input data.csv --analysis aggregation
```

### Cluster Modes

```bash
# Local mode (single machine)
python3 -m src.main --input data.csv --master "local[*]"

# Cluster mode (distributed)
python3 -m src.main --input data.csv --master "spark://spark-master:7077"
```

## Monitoring

### Web UIs

- **Spark Master**: http://localhost:8080
- **Spark Application**: http://localhost:4040
- **Worker 1**: http://localhost:8081
- **Worker 2**: http://localhost:8082
- **Worker 3**: http://localhost:8083

### Output Files

After analysis completion, check:

1. **General Output** (`output/general/`):
   - `results_[timestamp].csv` - Processed data
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

# Initialize analyzer
analyzer = ParallelDataAnalysis(
    master="spark://spark-master:7077"
)

# Run analysis
analyzer.run_analysis(
    input_path="data/input/data.csv",
    analysis_type="full"
)
```

### Custom Analysis

```python
from src.data_loader import DataLoader
from src.data_analyzer import DataAnalyzer
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("CustomAnalysis") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# Load data
loader = DataLoader(spark, error_handler)
df = loader.load_data("data.csv")

# Analyze
analyzer = DataAnalyzer(spark, error_handler)
stats = analyzer.statistical_analysis(df)
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

### Out of Memory

```bash
# Increase executor memory in docker-compose.yml
SPARK_WORKER_MEMORY=4G

# Or reduce partitions in config
spark.sql.shuffle.partitions: 50
```

### Slow Performance

1. Check worker status: http://localhost:8080
2. Review execution metrics in `output/statistics/`
3. Increase number of workers
4. Enable adaptive query execution

### Connection Errors

```bash
# Check cluster connectivity
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --class org.apache.spark.examples.SparkPi \
  /opt/spark/examples/jars/spark-examples*.jar
```

## Testing

```bash
# Run unit tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Examples

### Example 1: Sales Analysis

```python
# Analyze sales data
python3 -m src.main \
  --input data/input/sales.csv \
  --analysis full \
  --master "spark://spark-master:7077"
```

### Example 2: Log Analysis

```python
from spark_jobs.mapreduce_job import MapReduceJob

# Word count on logs
job = MapReduceJob()
word_counts = job.word_count(log_df, 'message')
```

### Example 3: Time Series

```python
from spark_jobs.aggregation_job import AggregationJob

# Aggregate by hour
job = AggregationJob()
hourly_metrics = job.time_series_aggregation(
    df, 'timestamp', 'value', interval='1 hour'
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

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
