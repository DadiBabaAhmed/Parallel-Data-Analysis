```markdown
# Quick Reference Card

## ⚡ Quick Start

```bash
# Navigate to project
cd "C:\Users\ahmed\Desktop\analyses de donnees\Script"

# Start cluster
docker compose up -d

# Run analysis
docker exec spark-master /opt/conda/envs/pda/bin/python /app/src/main.py \
  --input /app/data/input/sample_sales.csv \
  --master spark://spark-master:7077 \
  --analysis statistical

# Stop cluster
docker compose down -v
```

## 🔍 Verify Everything Works

```bash
# Check containers running
docker ps | findstr spark

# Test Python packages
docker exec spark-master /opt/conda/envs/pda/bin/python -c \
  "import pyspark, pandas, numpy; print('✅ All packages work!')"

# Test Spark connectivity
docker exec spark-master /opt/conda/envs/pda/bin/python -c \
  "from pyspark.sql import SparkSession; \
   s = SparkSession.builder.master('spark://spark-master:7077').getOrCreate(); \
   print(s.sparkContext.getConf().getAll())"
```

## 📊 Access UIs

| Service | URL | Purpose |
|---------|-----|---------|
| Spark Master | http://localhost:8080 | Cluster status & workers |
| Spark App | http://localhost:4040 | Job details (when running) |
| Spark Worker 1 | http://localhost:8081 | Worker 1 details |
| Spark Worker 2 | http://localhost:8082 | Worker 2 details |
| Spark Worker 3 | http://localhost:8083 | Worker 3 details |

## 🛠️ Useful Commands

```bash
# View master logs
docker logs -f spark-master

# Execute Python script in container
docker exec spark-master /opt/conda/envs/pda/bin/python /path/to/script.py

# Install additional Python package (temporary)
docker exec spark-master /opt/conda/envs/pda/bin/pip install package_name

# Check conda environment packages
docker exec spark-master conda list -n pda

# Get container shell access
docker exec -it spark-master bash

# View disk usage of images
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

## 📋 Image Specifications

### All 4 Images (master + 3 workers)
- **Size:** 5.7GB each
- **Base:** Debian (via continuumio/miniconda3)
- **Python:** 3.10.19
- **Spark:** 3.5.0 with Hadoop 3
- **Java:** OpenJDK 17 JRE
- **Packages:** 100+ installed via conda-forge

## ✅ Status Check Shortcuts

```bash
# One-liner: Full system check
docker exec spark-master bash -c \
  "echo '=== JAVA ===' && java -version && \
   echo '=== PYTHON ===' && python --version && \
   echo '=== PACKAGES ===' && python -c 'import pyspark, pandas, numpy; print("OK")' && \
   echo '=== SPARK ===' && spark-submit --version | head -2"
```

# ... (shortened; kept full content in docs)

---

**Last Updated:** 2025-11-19  
**Status:** ✅ Production Ready (except minor code bug in output saving)

```