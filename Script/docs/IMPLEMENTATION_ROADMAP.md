# Implementation Roadmap: CI/CD, Health Checks, Makefiles & Unit Tests

**Date Created:** November 19, 2025  
**Status:** Planning & Development  
**Final Goal:** Full website integration with clickable analysis execution and live result visualization

---

## 📋 Executive Summary

This document outlines the technical implementation strategy for four key improvements to the Parallel Data Analysis Framework:

1. **Health Checks in Docker Compose** - Container liveness & readiness probes
2. **CI/CD Pipeline** - Automated image builds & test execution
3. **Enhanced Makefile Targets** - Improved developer experience
4. **Unit Tests for Key Modules** - Quality assurance & regression prevention

These improvements directly support the **end goal**: integrating the website with the backend to enable users to launch analyses via button clicks and view real-time results.

---

## 🎯 Strategic Goals & Impact

### Immediate Goals (Weeks 1-2)
- ✅ Ensure cluster reliability with health checks
- ✅ Automate CI/CD to catch breaking changes
- ✅ Simplify common operations with Makefile
- ✅ Establish testing baseline with unit tests

### Mid-Term Goals (Weeks 3-4)
- Enable website backend API to trigger Docker commands safely
- Implement result polling and status tracking
- Set up monitoring and alerting for long-running jobs

### End Goal
- Full web UI integration:
  - Launch analyses from website
  - Real-time progress tracking
  - Automatic result visualization (graphs + statistics)
  - Historical execution logs visible in web UI

---

## 1️⃣ Health Checks in Docker Compose

### Purpose
Prevent container failures from going unnoticed. Health checks ensure:
- Spark master is accepting connections
- Workers are connected and ready
- Analysis jobs fail fast if prerequisites aren't met

### Implementation Details

#### Files to Modify
- `docker-compose.yml` - Add health check sections to services

#### What Gets Added

**Spark Master Health Check**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

**Worker Health Checks**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8081"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

#### Benefits
- 🟢 Automatic container restart on failure
- 🟢 Visual status in `docker-compose ps`
- 🟢 Enables graceful degradation if workers fail
- 🟢 Foundation for Kubernetes/Swarm deployments later

#### Dependencies
- `curl` already available in Dockerfile (in `/opt/conda/envs/pda/bin/`)
- No additional packages needed

#### Testing
```bash
# After starting cluster
docker-compose ps  # Shows health status
docker inspect spark-master | grep -A 10 Health  # Detailed info
```

---

## 2️⃣ CI/CD Pipeline

### Purpose
Automate:
- Docker image building on code changes
- Unit test execution before merging
- Image registry uploads (DockerHub/ECR)
- Security scanning and linting

### Technology Stack

**Recommended:** GitHub Actions (already in `.github/` folder)
- Free for public repos
- Integrates natively with git
- Supports Docker, Python, bash
- Can run on schedule or on push

### Implementation Details

#### Files to Create/Modify

1. **`.github/workflows/ci-pipeline.yml`** (NEW)
   - Triggers on: push to main, pull requests
   - Steps:
     - Checkout code
     - Set up Python environment
     - Run pytest
     - Build Docker images
     - Push to registry (optional)

2. **`.github/workflows/schedule-build.yml`** (NEW)
   - Triggers daily/weekly
   - Rebuilds images to pick up security patches
   - Validates base images (continuumio/miniconda3)

3. **`.dockerignore`** (NEW)
   - Reduce build context size
   - Exclude `.git`, `__pycache__`, `.pytest_cache`, etc.

4. **`Script/tests/` directory** (NEW)
   - Unit test files (see Section 4)

#### Pipeline Stages

**Stage 1: Code Quality**
- Lint Python code (flake8)
- Type hints check (mypy)
- Import sorting (isort)

**Stage 2: Unit Tests**
- Run pytest on key modules
- Generate coverage report
- Fail if coverage < 80%

**Stage 3: Docker Build**
- Build both master and worker images
- Tag with commit SHA
- Tag with `latest`

**Stage 4: Security**
- Scan images for vulnerabilities (Trivy)
- Check for exposed secrets

**Stage 5: Registry Upload**
- Push to DockerHub (optional, requires credentials)
- Push to GitHub Container Registry

#### Benefits
- 🚀 Catch bugs before production
- 🚀 Enforce code quality standards
- 🚀 Reproducible builds (same SHA = same image)
- 🚀 Security scanning prevents vulnerable deployments
- 🚀 Automated image updates

#### Dependencies
- GitHub Actions runner (free)
- Docker buildx (for multi-platform builds)
- pytest for testing

---

## 3️⃣ Enhanced Makefile Targets

### Purpose
Simplify common development workflows, especially for:
- Running analyses with different parameters
- Website integration testing
- Health check verification
- Local development setup

### New Targets to Add

#### Development & Testing
```makefile
test-health              # Verify all containers are healthy
test-integration         # Run integration tests
test-local-analysis      # Test without Docker
lint                     # Code quality checks
format                   # Auto-format Python files
```

#### Website Integration
```makefile
run-analysis-api         # Start API server for website
api-logs                 # View API logs
trigger-analysis         # Run analysis from web request
watch-results            # Monitor output folder for new results
```

#### CI/CD Local Testing
```makefile
ci-test                  # Run all CI checks locally
docker-build-local       # Build images locally
docker-push              # Push to registry (requires auth)
```

#### Debugging & Monitoring
```makefile
debug-master             # Connect to master with debugging enabled
debug-worker             # Connect to worker with debugging enabled
profile-analysis         # Run analysis with profiling
benchmark                # Performance benchmark tests
```

#### Enhanced Existing Targets
```makefile
run-analysis             # Add parameter support (file, type)
setup-dev                # Include pre-commit hooks, linting
clean-deep               # Clean Docker images, volumes, caches
```

### Benefits
- 📖 Self-documenting (`make help`)
- 📖 Reduce command complexity
- 📖 Standardize team workflows
- 📖 Enable CI/CD from command line for testing

---

## 4️⃣ Unit Tests for Key Modules

### Purpose
Ensure reliability of critical components:
- Data loading from multiple formats
- Analysis computations
- Error handling recovery
- Performance monitoring accuracy

### Test Structure

#### Directory: `Script/tests/`
```
tests/
├── conftest.py                    # Shared fixtures
├── test_data_loader.py            # DataLoader tests
├── test_data_analyzer.py          # DataAnalyzer tests
├── test_mapreduce_job.py          # MapReduce tests
├── test_error_handler.py          # Error handling tests
├── test_performance_monitor.py    # Performance tracking tests
└── fixtures/
    └── sample_data/               # Test data files
        ├── small.csv
        ├── small.json
        └── small.parquet
```

#### Module Coverage Plan

**1. `src/data_loader.py` - DataLoader Tests**
- ✅ Load CSV files
- ✅ Load JSON files
- ✅ Load Parquet files
- ✅ Handle missing files (error case)
- ✅ Handle corrupt data (error case)
- ✅ Cache behavior verification

**2. `src/data_analyzer.py` - DataAnalyzer Tests**
- ✅ Statistical analysis (mean, std, percentiles)
- ✅ Aggregation operations
- ✅ Correlation calculations
- ✅ Edge cases (empty data, single row, NaN values)

**3. `spark_jobs/mapreduce_job.py` - MapReduce Tests**
- ✅ Word count operation
- ✅ Group sum operation
- ✅ Top-N filtering
- ✅ Moving averages

**4. `src/error_handler.py` - Error Handling Tests**
- ✅ Log error messages correctly
- ✅ Generate failure JSON
- ✅ Recover from transient failures

**5. `src/performance_monitor.py` - Performance Tests**
- ✅ Stage timing accuracy
- ✅ Metrics aggregation
- ✅ JSON serialization

#### Test Framework & Tools
- **pytest** - Test runner (already in requirements)
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking Spark objects
- **pytest-timeout** - Prevent hanging tests

#### Test Execution Modes

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/test_data_loader.py -v

# With coverage report
pytest tests/ --cov=src --cov=spark_jobs --cov-report=html

# Fast mode (skip Spark tests)
pytest tests/ -m "not spark" -v
```

#### Benefits
- ✔️ Catch regressions early
- ✔️ Enable safe refactoring
- ✔️ Document expected behavior
- ✔️ Provide baseline for performance comparisons

---

## 📅 Implementation Timeline & Priorities

### Phase 1: Health Checks (1-2 hours)
**Priority: HIGH** - Improves reliability immediately

1. Add curl to Dockerfile (already there)
2. Add healthcheck blocks to docker-compose.yml
3. Test with `docker-compose ps`
4. Verify restart behavior

### Phase 2: CI/CD Pipeline (4-6 hours)
**Priority: HIGH** - Prevents breaking changes

1. Create `.github/workflows/ci-pipeline.yml`
2. Set up pytest in CI environment
3. Configure Docker build in CI
4. Test with manual trigger
5. Add branch protection rules

### Phase 3: Makefile Enhancements (2-3 hours)
**Priority: MEDIUM** - Improves developer experience

1. Add new targets to existing Makefile
2. Create website integration targets
3. Update help text
4. Document in README

### Phase 4: Unit Tests (8-10 hours)
**Priority: MEDIUM** - Ensures code quality

1. Create `tests/` directory structure
2. Write DataLoader tests
3. Write DataAnalyzer tests
4. Write MapReduce tests
5. Write Error Handler tests
6. Add CI integration

---

## 🔗 Website Integration Implications

### How These Changes Enable Web Integration

#### Health Checks
- Website can query cluster health before attempting analysis
- Automatic failover when workers are unhealthy
- Better error messages for users ("cluster not ready")

#### CI/CD
- Deploy updated images without downtime
- Test website API against real Docker environment
- Consistent image versions across dev/staging/production

#### Enhanced Makefile
- New targets: `run-analysis-api`, `trigger-analysis`, `watch-results`
- Website backend can invoke `make trigger-analysis --input file.csv`
- Results automatically sync to web-viewable output folder

#### Unit Tests
- Catch issues early before website hits them
- Enable mock testing for website backend (no Docker needed)
- Performance baseline for optimization

### API Server for Website (Future)

```bash
# New endpoint for website to hit:
POST /api/v1/analyze
{
  "input_file": "data/input/sales.csv",
  "analysis_type": "full",
  "output_format": "json"
}

# Website polls:
GET /api/v1/analysis/{job_id}/status
GET /api/v1/analysis/{job_id}/results
GET /api/v1/analysis/{job_id}/graphs
```

---

## 🛠️ Quick Reference: Commands to Use

### After Health Checks Added
```bash
make start                    # Start cluster
docker-compose ps            # Check health status (see "healthy")
```

### After CI/CD Added
```bash
make ci-test                 # Run all CI checks locally
git push                     # Triggers automatic CI
```

### After Makefile Enhanced
```bash
make test-health             # Verify cluster is ready
make run-analysis --input data.csv  # Run with parameters
make watch-results           # Monitor new output files
```

### After Unit Tests Added
```bash
make test                    # Run unit tests
pytest tests/ --cov         # With coverage report
```

---

## 📊 Success Criteria

| Component | Success Metric | Verification |
|-----------|---|---|
| **Health Checks** | All containers show "healthy" after 90s | `docker-compose ps` |
| **CI/CD** | Build completes in < 5min, tests pass | GitHub Actions logs |
| **Makefile** | 15+ targets, all documented | `make help` |
| **Unit Tests** | 80%+ code coverage, 0 failed tests | `pytest --cov` |

---

## 🚀 Getting Started

Proceed with the following order:
1. **Start with Health Checks** (quickest win for reliability)
2. **Add CI/CD Pipeline** (prevents future regressions)
3. **Enhance Makefile** (improves day-to-day workflow)
4. **Write Unit Tests** (ensures maintainability)

Each section is independent; you can tackle them in parallel if needed.

---

## 📝 Notes for Next Steps

- All changes maintain **backward compatibility**
- Existing workflows continue to work
- New features are **opt-in** (use `make help` to discover)
- Documentation will be updated for each phase

---

**Next Action:** Proceed with Phase 1 - Health Checks in Docker Compose ➡️

