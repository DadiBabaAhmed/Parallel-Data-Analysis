# Deployment Guide - Parallel Data Analysis Framework

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment Modes](#deployment-modes)
5. [Scaling](#scaling)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free space
- OS: Linux, macOS, or Windows (with WSL2)

**Recommended Requirements:**
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 50+ GB SSD
- OS: Linux (Ubuntu 20.04+)

### Software Requirements

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+ (for local development)
- Git

### Installation Commands

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose python3 python3-pip git

# macOS (with Homebrew)
brew install docker docker-compose python3 git

# Start Docker
sudo systemctl start docker
sudo usermod -aG docker $USER  # Add user to docker group
```

## Installation

### Option 1: Quick Start (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd parallel-data-analysis

# Run quick start script
chmod +x quickstart.sh
./quickstart.sh
```

### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd parallel-data-analysis

# 2. Create directory structure
mkdir -p data/input output/{general,statistics,failures}

# 3. Install Python dependencies (for local testing)
pip3 install -r requirements.txt

# 4. Generate sample data
python3 example_test.py generate

# 5. Build Docker images
docker-compose build

# 6. Start cluster
docker-compose up -d
```

### Option 3: Using Makefile

```bash
make setup    # Complete setup
make start    # Start cluster
make run-analysis  # Run sample analysis
```

## Configuration

### Application Configuration

Edit `config/app_config.yaml`:

```yaml
# Adjust based on your needs
cluster:
  mode: "cluster"  # or "local"
  master_url: "spark://spark-master:7077"
  worker_nodes: 3

resources:
  executor_memory: "2g"
  executor_cores: 2
  driver_memory: "2g"

analysis:
  default_type: "full"
  enable_caching: true
```

### Spark Configuration

Edit `config/spark_config.py`:

```python
SPARK_CONFIG = {
    'spark.executor.memory': '2g',  # Increase for large datasets
    'spark.executor.cores': '2',     # Adjust based on CPU cores
    'spark.sql.shuffle.partitions': '200',  # Tune for performance
}
```

### Docker Resources

Edit `docker-compose.yml`:

```yaml
environment:
  - SPARK_WORKER_CORES=4      # CPU cores per worker
  - SPARK_WORKER_MEMORY=4G    # Memory per worker
```

## Deployment Modes

### Local Mode (Development)

For testing on a single machine:

```bash
# Use local mode in code
python3 -m src.main \
  --input data/input/data.csv \
  --master "local[*]" \
  --analysis full
```

**Advantages:**
- No Docker required
- Easy debugging
- Fast iteration

**Disadvantages:**
- Limited by single machine resources
- No true parallelism

### Cluster Mode (Production)

For production workloads:

```bash
# 1. Start cluster
docker-compose up -d

# 2. Submit job to cluster
docker exec -it spark-master python3 -m src.main \
  --input /app/data/input/data.csv \
  --master spark://spark-master:7077 \
  --analysis full
```

**Advantages:**
- True distributed processing
- Scalable
- Fault tolerant

**Disadvantages:**
- More complex setup
- Requires more resources

### Kubernetes Deployment (Advanced)

For large-scale production:

```yaml
# k8s-deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: spark-master
spec:
  ports:
    - port: 7077
      name: spark
    - port: 8080
      name: ui
  selector:
    app: spark-master
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spark-master
  template:
    metadata:
      labels:
        app: spark-master
    spec:
      containers:
      - name: spark-master
        image: your-registry/parallel-data-analysis:master
        ports:
        - containerPort: 7077
        - containerPort: 8080
```

## Scaling

### Horizontal Scaling (Add More Workers)

```bash
# Method 1: Docker Compose scale
docker-compose up -d --scale spark-worker-1=5

# Method 2: Edit docker-compose.yml and add more worker services
# Then restart
docker-compose down
docker-compose up -d
```

### Vertical Scaling (More Resources per Worker)

Edit `docker-compose.yml`:

```yaml
spark-worker-1:
  environment:
    - SPARK_WORKER_CORES=8      # Increase cores
    - SPARK_WORKER_MEMORY=8G    # Increase memory
```

### Dynamic Allocation

Enable in `config/spark_config.py`:

```python
CLUSTER_CONFIG = {
    'spark.dynamicAllocation.enabled': 'true',
    'spark.dynamicAllocation.minExecutors': '1',
    'spark.dynamicAllocation.maxExecutors': '10',
}
```

### Performance Tuning

**For Small Datasets (<1GB):**
```python
'spark.sql.shuffle.partitions': '8',
'spark.executor.memory': '1g',
```

**For Medium Datasets (1-10GB):**
```python
'spark.sql.shuffle.partitions': '50',
'spark.executor.memory': '2g',
```

**For Large Datasets (>10GB):**
```python
'spark.sql.shuffle.partitions': '200',
'spark.executor.memory': '4g',
'spark.sql.adaptive.enabled': 'true',
```

## Monitoring

### Web Interfaces

1. **Spark Master UI**: http://localhost:8080
   - View cluster status
   - Monitor workers
   - Check running applications

2. **Spark Application UI**: http://localhost:4040
   - View job progress
   - Analyze execution plans
   - Monitor stages and tasks

3. **Worker UIs**:
   - Worker 1: http://localhost:8081
   - Worker 2: http://localhost:8082
   - Worker 3: http://localhost:8083

### Command Line Monitoring

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f spark-master

# Monitor resource usage
docker stats

# Check cluster status
make status
```

### Performance Metrics

Check `output/statistics/` for:
- `performance_[timestamp].json` - Detailed metrics
- `execution_summary_[timestamp].txt` - Human-readable summary
- `node_utilization_[timestamp].csv` - Per-node stats

### Setting Up Prometheus (Optional)

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Troubleshooting

### Common Issues

**1. Out of Memory Errors**

```bash
# Solution: Increase executor memory
# Edit docker-compose.yml
SPARK_WORKER_MEMORY=4G

# Or reduce data size
# Use sampling in your code
df = df.sample(fraction=0.1)
```

**2. Connection Refused**

```bash
# Check if containers are running
docker-compose ps

# Restart cluster
docker-compose restart

# Check firewall
sudo ufw allow 7077/tcp
sudo ufw allow 8080/tcp
```

**3. Slow Performance**

```bash
# Enable adaptive query execution
'spark.sql.adaptive.enabled': 'true',

# Increase partitions for large datasets
'spark.sql.shuffle.partitions': '200',

# Cache frequently used DataFrames
df.cache()
```

**4. Container Crashes**

```bash
# Check logs
docker logs spark-master

# Check resource limits
docker stats

# Increase resources in docker-compose.yml
```

### Debug Mode

```bash
# Run with verbose logging
docker exec -it spark-master bash
export SPARK_LOG_LEVEL=DEBUG
python3 -m src.main --input /app/data/input/data.csv --master spark://spark-master:7077
```

### Health Checks

```bash
# Test Spark connectivity
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --class org.apache.spark.examples.SparkPi \
  /opt/spark/examples/jars/spark-examples*.jar

# Test Python environment
docker exec -it spark-master python3 -c "import pyspark; print(pyspark.__version__)"
```

## Best Practices

### 1. Data Management

- Store input data in `data/input/`
- Use appropriate file formats (Parquet for large datasets)
- Partition large files
- Clean up old output files regularly

```bash
# Clean output
make clean
```

### 2. Resource Management

- Start with small worker configurations
- Scale up as needed
- Monitor resource usage
- Use dynamic allocation for variable workloads

### 3. Code Organization

- Keep analysis logic in separate modules
- Use configuration files for settings
- Implement proper error handling
- Add logging for debugging

### 4. Security

```bash
# Don't commit sensitive data
echo "data/input/*.csv" >> .gitignore

# Use environment variables for credentials
export DB_PASSWORD="secret"

# Restrict network access
# Edit docker-compose.yml
ports:
  - "127.0.0.1:8080:8080"  # Only localhost
```

### 5. Backup and Recovery

```bash
# Backup results
make backup

# Backup configuration
tar -czf config_backup.tar.gz config/

# Version control
git add .
git commit -m "Save configuration"
```

### 6. Testing

```bash
# Run tests before deployment
pytest tests/

# Test with sample data
make run-local

# Load test with large dataset
python3 example_test.py
```

### 7. Maintenance

```bash
# Weekly tasks
- Review logs
- Clean old output files
- Update dependencies
- Check for security updates

# Monthly tasks
- Review and optimize configurations
- Backup important results
- Update documentation

# Commands
docker-compose pull  # Update images
pip install -U -r requirements.txt  # Update Python deps
```

## Production Checklist

Before deploying to production:

- [ ] Test with representative data
- [ ] Configure appropriate resources
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Document configurations
- [ ] Set up alerting
- [ ] Plan for scaling
- [ ] Test failure scenarios
- [ ] Set up log rotation
- [ ] Configure security settings

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review troubleshooting section
3. Check output/failures/ directory
4. Open an issue on GitHub
5. Contact support team
