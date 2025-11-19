.PHONY: help build start stop restart logs clean test generate-data run-analysis run-local shell

# Variables
MASTER_CONTAINER = spark-master
WORKER_COUNT = 3

help:
	@echo "Parallel Data Analysis Framework - Make Commands"
	@echo ""
	@echo "Setup & Build:"
	@echo "  make build           - Build Docker images"
	@echo "  make start           - Start Spark cluster"
	@echo "  make stop            - Stop Spark cluster"
	@echo "  make restart         - Restart cluster"
	@echo ""
	@echo "Data & Testing:"
	@echo "  make generate-data   - Generate sample data"
	@echo "  make test            - Run unit tests"
	@echo "  make run-local       - Run local test"
	@echo "  make run-analysis    - Run analysis on cluster"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs            - Show cluster logs"
	@echo "  make status          - Show cluster status"
	@echo "  make shell           - Open shell in master"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Clean output files"
	@echo "  make clean-all       - Clean everything"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start the cluster
start:
	@echo "Starting Spark cluster with $(WORKER_COUNT) workers..."
	docker-compose up -d
	@echo "Waiting for cluster to be ready..."
	@sleep 15
	@echo "✓ Cluster started!"
	@echo ""
	@echo "Access Web UIs:"
	@echo "  Spark Master:  http://localhost:8080"
	@echo "  Spark App:     http://localhost:4040"
	@echo "  Worker 1:      http://localhost:8081"
	@echo "  Worker 2:      http://localhost:8082"
	@echo "  Worker 3:      http://localhost:8083"

# Stop the cluster
stop:
	@echo "Stopping Spark cluster..."
	docker-compose down

# Restart the cluster
restart: stop start

# Show logs
logs:
	docker-compose logs -f

# Show cluster status
status:
	@echo "Cluster Status:"
	@docker-compose ps
	@echo ""
	@echo "Docker Stats:"
	@docker stats --no-stream

# Generate sample data
generate-data:
	@echo "Generating sample data..."
	python3 example_test.py generate
	@echo "✓ Sample data generated in data/input/"

# Run unit tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src

# Run local test (without Docker)
run-local:
	@echo "Running local test..."
	python3 example_test.py

# Run quick demo
run-quick:
	@echo "Running quick demo..."
	python3 example_test.py quick

# Run analysis on cluster
run-analysis:
	@echo "Running analysis on Spark cluster..."
	docker exec -it $(MASTER_CONTAINER) \
		python3 -m src.main \
		--input /app/data/input/sample_sales.csv \
		--master spark://spark-master:7077 \
		--analysis full

# Run custom analysis
run-custom:
	@read -p "Enter input file path: " filepath; \
	read -p "Enter analysis type (full/statistical/aggregation): " analysis; \
	docker exec -it $(MASTER_CONTAINER) \
		python3 -m src.main \
		--input $$filepath \
		--master spark://spark-master:7077 \
		--analysis $$analysis

# Open shell in master container
shell:
	docker exec -it $(MASTER_CONTAINER) bash

# Open Python shell with Spark
pyspark:
	docker exec -it $(MASTER_CONTAINER) pyspark --master spark://spark-master:7077

# View output files
show-output:
	@echo "General Output:"
	@ls -lh output/general/ 2>/dev/null || echo "No files yet"
	@echo ""
	@echo "Statistics:"
	@ls -lh output/statistics/ 2>/dev/null || echo "No files yet"
	@echo ""
	@echo "Failures:"
	@ls -lh output/failures/ 2>/dev/null || echo "No files yet"

# Scale workers
scale:
	@read -p "Enter number of workers: " count; \
	docker-compose up -d --scale spark-worker-1=$$count

# Clean output files
clean:
	@echo "Cleaning output files..."
	rm -rf output/general/*
	rm -rf output/statistics/*
	rm -rf output/failures/*
	@echo "✓ Output files cleaned"

# Clean everything
clean-all: clean
	@echo "Cleaning Docker containers and volumes..."
	docker-compose down -v
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Everything cleaned"

# Install Python dependencies (for local development)
install:
	pip install -r requirements.txt

# Setup complete project
setup: install generate-data build
	@echo "✓ Project setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make start' to start the cluster"
	@echo "  2. Run 'make run-analysis' to run analysis"
	@echo "  3. Run 'make show-output' to see results"

# Monitor cluster resources
monitor:
	@echo "Monitoring cluster resources (press Ctrl+C to stop)..."
	@watch -n 2 'docker stats --no-stream'

# Backup results
backup:
	@echo "Creating backup of results..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf backup_$$timestamp.tar.gz output/; \
	echo "✓ Backup created: backup_$$timestamp.tar.gz"
