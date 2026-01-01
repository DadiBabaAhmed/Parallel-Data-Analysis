# Quick Start Guide

## Project Status
✅ **VERIFIED AND READY FOR DEPLOYMENT**

All 17 verification tests passed. Web API is containerized and functional.

---

## Quick Start (5 Minutes)

### Step 1: Start Services
```bash
cd Script/
docker-compose up -d
```

Wait for services to be healthy (~2 minutes):
```bash
docker-compose ps
# All containers should show "Up"
```

### Step 2: Verify Web API
```bash
# Check health
curl http://localhost:5000/api/health

# List files
curl http://localhost:5000/api/input-files

# List hosts
curl http://localhost:5000/api/hosts
```

### Step 3: Start Web Server
```bash
# In another terminal, go to Web site directory
cd "Web site"
python -m http.server 8000
```

### Step 4: Access Application
- **Landing Page**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard.html
- **Spark Master UI**: http://localhost:8080

---

## Running Analysis

1. Go to http://localhost:8000/dashboard.html
2. Select input file from dropdown
3. Choose analysis type (full/statistical/aggregation)
4. Click "Start"
5. Watch status update in real-time
6. Results appear once complete

---

## Monitoring

```bash
# Watch web API logs
docker-compose logs -f web_api

# Watch Spark Master logs
docker-compose logs -f spark-master

# Watch specific worker
docker-compose logs -f spark-worker-1

# View all services status
docker-compose ps
```

---

## Stopping Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check if API is running |
| `/api/hosts` | GET | List cluster hosts and UIs |
| `/api/input-files` | GET | List available input files |
| `/api/results` | GET | List analysis results |
| `/api/trigger` | POST | Start new analysis |
| `/api/jobs` | GET | List all jobs |
| `/api/job/<id>` | GET | Get job status |
| `/api/job/<id>/logs` | GET | Get job logs |
| `/api/graphs/<file>` | GET | Download graph file |

---

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs

# Ensure ports are free
netstat -ano | grep :5000
netstat -ano | grep :8080

# Rebuild images
docker-compose build --no-cache
```

### Web API not responding
```bash
# Check if container is running
docker ps | grep pda-web-api

# Check logs
docker logs pda-web-api

# Restart service
docker-compose restart web_api
```

### Can't access website
```bash
# Ensure web server is running on port 8000
curl http://localhost:8000

# Start web server if needed
cd "Web site"
python -m http.server 8000
```

### Analysis won't trigger
```bash
# Check if files exist
curl http://localhost:5000/api/input-files

# Check Spark Master health
curl http://localhost:8080/

# Check web_api logs
docker-compose logs web_api

# Manually test trigger
curl -X POST http://localhost:5000/api/trigger \
  -H "Content-Type: application/json" \
  -d '{"filename":"sample_sales.csv","analysis":"full"}'
```

---

## Performance Ports

- **Web API**: http://localhost:5000
- **Spark Master UI**: http://localhost:8080
- **Spark Worker 1**: http://localhost:8081
- **Spark Worker 2**: http://localhost:8082
- **Spark Worker 3**: http://localhost:8083
- **Spark Application**: http://localhost:4040 (during job execution)
- **Website**: http://localhost:8000 (or the configured port)

---

## Testing

Run the automated test suite:
```bash
python test_api.py
```

Expected output:
```
✅ Health Check: OK
✅ Hosts Endpoint: OK
✅ Input Files Endpoint: OK
✅ Results Endpoint: OK
✅ Jobs Endpoint: OK
✅ CORS Headers: OK

TEST SUMMARY
============
Total Tests: 6
Passed: 6
Failed: 0
Success Rate: 100.0%
```

---

## File Structure

```
Project/
├── Script/
│   ├── docker-compose.yml          ← Start here
│   ├── docker/
│   │   ├── Dockerfile              ← Web API image
│   │   ├── Dockerfile.master       ← Spark Master image
│   │   └── Dockerfile.worker       ← Spark Worker image
│   ├── api/
│   │   ├── __init__.py
│   │   └── web_api.py              ← Flask API server
│   ├── src/
│   │   ├── main.py
│   │   ├── data_loader.py
│   │   └── ...
│   ├── data/
│   │   └── input/                  ← Input CSV files
│   ├── output/                     ← Analysis results
│   ├── logs/                       ← Service logs
│   └── config/
│       ├── app_config.yaml
│       └── environment.yml
│
├── Web site/
│   ├── index.html                  ← Landing page
│   ├── dashboard.html              ← Analysis dashboard
│   ├── main.js                     ← Landing page logic
│   ├── dashboard.js                ← Dashboard logic
│   └── ...
│
├── test_api.py                     ← API test suite
├── verify_and_test.ps1             ← Verification script
└── VERIFICATION_REPORT.md          ← Detailed report
```

---

## Key Files

- **`docker-compose.yml`**: Service configuration (Spark cluster + Web API)
- **`api/web_api.py`**: Flask API for analysis triggering and result serving
- **`index.html`**: Main landing page with links
- **`dashboard.html`**: Analysis control panel
- **`test_api.py`**: Automated API tests

---

## Common Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache

# Run specific service
docker-compose up -d web_api

# Stop specific service
docker-compose stop web_api

# Restart specific service
docker-compose restart web_api

# Remove all containers and images
docker-compose down --rmi all
```

---

## Expected Timeline

| Activity | Time |
|----------|------|
| docker-compose up | 2-3 minutes |
| Services ready | 3-4 minutes |
| API responding | 4-5 minutes |
| Full analysis | 5-15 minutes (depends on data) |

---

## Support

For detailed information about fixes and verification:
See: **VERIFICATION_REPORT.md**

For comprehensive documentation:
See: **Script/docs/** directory

---

**Last Updated**: December 4, 2025  
**Status**: ✅ VERIFIED & READY
