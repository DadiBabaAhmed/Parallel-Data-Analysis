#!/usr/bin/env python3
"""
Lightweight Flask API to expose cluster host links and serve result files (graphs and JSON)
Run: python3 web_api.py
"""
import os
import json
from flask import Flask, jsonify, send_from_directory, abort, request
from flask_cors import CORS
import uuid
import threading
import time
from datetime import datetime

# New import for Docker SDK
try:
    import docker
    DOCKER_AVAILABLE = True
except Exception:
    docker = None
    DOCKER_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
GENERAL_DIR = os.path.join(OUTPUT_DIR, 'general')
GRAPHS_DIR = os.path.join(GENERAL_DIR, 'graphs')
STATISTICS_DIR = os.path.join(OUTPUT_DIR, 'statistics')

ALLOWED_DIRS = {
    'general': GENERAL_DIR,
    'graphs': GRAPHS_DIR,
    'statistics': STATISTICS_DIR,
}

# Job management
JOBS_DIR = os.path.join(BASE_DIR, 'output', 'jobs')
os.makedirs(JOBS_DIR, exist_ok=True)
JOBS = {}  # in-memory job registry


def persist_job(job_id):
    path = os.path.join(JOBS_DIR, f"{job_id}.json")
    try:
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(JOBS[job_id], fh, indent=2, default=str)
    except Exception:
        pass


def safe_input_filename(name: str) -> bool:
    # Only allow filenames without directory components
    return safe_filename(name) and os.path.basename(name) == name


app = Flask(__name__)
CORS(app)

# Simple list of container web UIs (assumes local development on default ports)
CONTAINERS = [
    {"name": "Spark Master", "url": "http://localhost:8080"},
    {"name": "Spark App UI", "url": "http://localhost:4040"},
    {"name": "Worker 1", "url": "http://localhost:8081"},
    {"name": "Worker 2", "url": "http://localhost:8082"},
    {"name": "Worker 3", "url": "http://localhost:8083"},
]


def safe_filename(name: str) -> bool:
    if not name:
        return False
    if '..' in name or name.startswith('/') or name.startswith('\\'):
        return False
    return True


# Docker client initialization (if available & socket mounted)
DOCKER_CLIENT = None
if DOCKER_AVAILABLE:
    try:
        DOCKER_CLIENT = docker.from_env()
    except Exception:
        DOCKER_CLIENT = None


def stream_exec_and_monitor(job_id, container_name, exec_cmd, log_path):
    """
    Use the Docker API to create an exec instance inside container_name and stream output to log_path.
    Update JOBS[job_id] status (running -> finished/failed) and exit code.
    """
    JOBS[job_id]['status'] = 'running'
    JOBS[job_id]['started_at'] = datetime.utcnow().isoformat() + 'Z'
    persist_job(job_id)

    if DOCKER_CLIENT is None:
        # Fallback: attempt to run command locally (this will generally fail in containerized setups)
        JOBS[job_id]['status'] = 'failed'
        JOBS[job_id]['error'] = 'docker client not available'
        persist_job(job_id)
        return

    try:
        container = None
        try:
            container = DOCKER_CLIENT.containers.get(container_name)
        except Exception as e_get:
            JOBS[job_id]['status'] = 'failed'
            JOBS[job_id]['error'] = f'container not found: {container_name} ({e_get})'
            persist_job(job_id)
            return

        # Create exec
        api_client = DOCKER_CLIENT.api
        exec_obj = api_client.exec_create(container.id, exec_cmd, tty=False)
        exec_id = exec_obj.get('Id')

        # Stream output
        stream = api_client.exec_start(exec_id, stream=True, demux=False)
        with open(log_path, 'wb') as fh:
            try:
                for chunk in stream:
                    if isinstance(chunk, bytes):
                        fh.write(chunk)
                    else:
                        # some SDKs yield str
                        fh.write(str(chunk).encode('utf-8', errors='ignore'))
                    fh.flush()
            except Exception:
                # stream may raise on disconnect; we'll inspect exit code afterwards
                pass

        # Inspect to get exit code
        info = api_client.exec_inspect(exec_id)
        exit_code = info.get('ExitCode', None)
        JOBS[job_id]['finished_at'] = datetime.utcnow().isoformat() + 'Z'
        JOBS[job_id]['exit_code'] = exit_code
        JOBS[job_id]['status'] = 'finished' if exit_code == 0 else 'failed'
        persist_job(job_id)
    except Exception as e:
        JOBS[job_id]['status'] = 'failed'
        JOBS[job_id]['error'] = str(e)
        JOBS[job_id]['finished_at'] = datetime.utcnow().isoformat() + 'Z'
        persist_job(job_id)


@app.route('/api/hosts')
def api_hosts():
    return jsonify(CONTAINERS)


@app.route('/api/results')
def api_results():
    # List available files in output folders
    results = {
        'graphs': [],
        'statistics': [],
        'general': []
    }

    for key, d in ALLOWED_DIRS.items():
        try:
            files = sorted(os.listdir(d))
            # filter hidden
            files = [f for f in files if not f.startswith('.')]
            results[key] = files
        except FileNotFoundError:
            results[key] = []
    return jsonify(results)


@app.route('/api/input-files')
def api_input_files():
    # List files in data/input
    input_dir = os.path.join(BASE_DIR, 'data', 'input')
    try:
        files = sorted(os.listdir(input_dir))
        files = [f for f in files if not f.startswith('.')]
    except FileNotFoundError:
        files = []
    return jsonify({'files': files})


@app.route('/api/trigger', methods=['POST'])
def api_trigger():
    payload = request.get_json() or {}
    filename = payload.get('filename')
    analysis = payload.get('analysis', 'full')
    master = payload.get('master', 'spark://spark-master:7077')
    container_name = payload.get('container', 'spark-master')

    if not filename or not safe_input_filename(filename):
        return jsonify({'error': 'invalid filename'}), 400
    if analysis not in ['full', 'statistical', 'aggregation']:
        return jsonify({'error': 'invalid analysis type'}), 400

    # Check input file exists in the mounted data/input directory (host path)
    host_input_path = os.path.join(BASE_DIR, 'data', 'input', filename)
    if not os.path.exists(host_input_path):
        return jsonify({'error': 'file not found'}), 404

    job_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:8]
    log_path = os.path.join(JOBS_DIR, f"{job_id}.log")
    JOBS[job_id] = {
        'id': job_id,
        'filename': filename,
        'analysis': analysis,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'log': os.path.relpath(log_path, BASE_DIR)
    }
    persist_job(job_id)

    # Build the command we want executed inside the spark-master container
    container_input_path = f"/app/data/input/{filename}"
    exec_cmd = [
        '/opt/conda/envs/pda/bin/python', '-m', 'src.main',
        '--input', container_input_path,
        '--master', master,
        '--analysis', analysis
    ]

    # If DOCKER_CLIENT available, use Docker SDK to exec, stream logs and monitor.
    if DOCKER_CLIENT:
        t = threading.Thread(
            target=stream_exec_and_monitor,
            args=(job_id, container_name, exec_cmd, log_path),
            daemon=True
        )
        t.start()
        return jsonify({'job_id': job_id, 'status': JOBS[job_id]['status']})

    # Fallback: try to run a local subprocess (non-containerized, original approach).
    try:
        # original subprocess approach (only works if docker CLI is available & permitted)
        import subprocess
        cmd = [
            'docker', 'exec', '-i', container_name
        ] + exec_cmd
        log_fh = open(log_path, 'wb')
        proc = subprocess.Popen(cmd, stdout=log_fh, stderr=subprocess.STDOUT)
        # Monitor in background thread using a simple monitor that checks proc
        def monitor_process_local(job_id, proc, log_path):
            try:
                JOBS[job_id]['status'] = 'running'
                JOBS[job_id]['pid'] = proc.pid
                JOBS[job_id]['started_at'] = datetime.utcnow().isoformat() + 'Z'
                persist_job(job_id)
                ret = proc.wait()
                JOBS[job_id]['finished_at'] = datetime.utcnow().isoformat() + 'Z'
                JOBS[job_id]['exit_code'] = ret
                JOBS[job_id]['status'] = 'finished' if ret == 0 else 'failed'
                persist_job(job_id)
            except Exception as e:
                JOBS[job_id]['status'] = 'failed'
                JOBS[job_id]['error'] = str(e)
                persist_job(job_id)
        t = threading.Thread(target=monitor_process_local, args=(job_id, proc, log_path), daemon=True)
        t.start()
        return jsonify({'job_id': job_id, 'status': JOBS[job_id]['status']})
    except Exception as e:
        JOBS[job_id]['status'] = 'failed'
        JOBS[job_id]['error'] = str(e)
        persist_job(job_id)
        return jsonify({'error': 'failed to start job', 'detail': str(e)}), 500


@app.route('/api/jobs')
def api_jobs():
    return jsonify({'jobs': list(JOBS.values())})


@app.route('/api/job/<job_id>')
def api_job(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({'error': 'job not found'}), 404
    return jsonify(job)


@app.route('/api/job/<job_id>/logs')
def api_job_logs(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({'error': 'job not found'}), 404
    log_path = os.path.join(BASE_DIR, job.get('log', ''))
    if not os.path.exists(log_path):
        return jsonify({'error': 'log not found'}), 404
    # Return last N lines
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()[-400:]
        return jsonify({'log': ''.join(lines)})
    except Exception as e:
        return jsonify({'error': 'could not read log', 'detail': str(e)}), 500


@app.route('/api/graphs/<path:filename>')
def api_graph(filename):
    if not safe_filename(filename):
        abort(400)
    directory = GRAPHS_DIR
    if not os.path.exists(os.path.join(directory, filename)):
        abort(404)
    return send_from_directory(directory, filename)


@app.route('/api/results/file')
def api_results_file():
    # Query params: category (general|statistics|graphs), name
    category = request.args.get('category') or 'general'
    name = request.args.get('name')
    if not name or not safe_filename(name):
        return jsonify({'error': 'invalid filename'}), 400
    if category not in ALLOWED_DIRS:
        return jsonify({'error': 'invalid category'}), 400
    directory = ALLOWED_DIRS[category]
    path = os.path.join(directory, name)
    if not os.path.exists(path):
        return jsonify({'error': 'file not found'}), 404

    # If JSON, return parsed JSON
    if name.lower().endswith('.json'):
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': 'failed to parse json', 'detail': str(e)}), 500

    # If image or other, send as static
    return send_from_directory(directory, name)


@app.route('/api/download')
def api_download():
    # downloads a file (category + name) as attachment
    category = request.args.get('category') or 'general'
    name = request.args.get('name')
    if not name or not safe_filename(name):
        return jsonify({'error': 'invalid filename'}), 400
    if category not in ALLOWED_DIRS:
        return jsonify({'error': 'invalid category'}), 400
    directory = ALLOWED_DIRS[category]
    if not os.path.exists(os.path.join(directory, name)):
        return jsonify({'error': 'file not found'}), 404
    return send_from_directory(directory, name, as_attachment=True)


@app.route('/api/health')
def api_health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Create directories if missing to avoid errors
    for d in [GENERAL_DIR, GRAPHS_DIR, STATISTICS_DIR]:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass
    print('Starting web API on http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)