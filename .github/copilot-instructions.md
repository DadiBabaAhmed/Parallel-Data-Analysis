## Quick context for AI coding agents

This repository is a parallel data analysis framework built around Apache Spark (Python). Key implementation files live in the `Script/` folder (e.g. `main_py.py`, `data_loader_py.py`, `data_analyzer_py.py`, `mapreduce_job_py.py`). The project runs either locally (Spark local[*]) or in a local Docker-based Spark cluster (docker-compose in `Script/docker_compose.yml`).

Keep suggestions narrowly scoped to discoverable patterns below. Do not invent services or rewiring not present in `Script/`.

## Big-picture architecture (from code)
- Entry/Orchestration: `Script/main_py.py` defines the `ParallelDataAnalysis` class and is the primary CLI entrypoint.
- Data ingestion: `Script/data_loader_py.py` (DataLoader) supports csv/json/parquet/avro and returns cached Spark DataFrames.
- Analysis: `Script/data_analyzer_py.py` (DataAnalyzer) implements statistical, aggregation, correlation, MapReduce, and window analysis helpers. Many analyses convert to pandas for small/medium datasets.
- MapReduce helpers: `Script/mapreduce_job_py.py` provides reusable operations (word_count, group_sum, top_n_by_group, moving_average).
- Support: `Script/graph_generator_py.py`, `Script/performance_monitor_py.py`, and `Script/error_handler_py.py` provide visualization, timing/metrics, and centralized error logging (outputs written to `output/` with timestamps).

## Developer workflows & concrete commands
- Install dependencies (file name is nonstandard):
  - pip install -r Script/requirements_txt.txt
- Generate sample data (example script):
  - python Script/example_test_py.py generate
- Run locally (no Docker):
  - python Script/main_py.py --input Script/data/input/sample_sales.csv --master local[*] --analysis full
- Run the Docker Spark cluster (docker-compose file is in `Script/`):
  - cd "Script" && docker-compose up -d
  - Or use the makefile-like helper at `Script/makefile.txt` with: make -f Script/makefile.txt start
  - To run analysis inside master: make -f Script/makefile.txt run-analysis

Notes: the repo stores Makefile and requirements with `_txt` suffixes (`makefile.txt`, `requirements_txt.txt`). Either call `make -f` and `pip install -r Script/requirements_txt.txt`, or rename files to standard names for convenience.

## Project-specific conventions and gotchas
- Filenames end with `_py.py` (e.g. `main_py.py`). Refer to the exact filenames when opening files or running scripts.
- Output conventions: analysis artifacts are saved under `output/` with a timestamped prefix (see `ParallelDataAnalysis.save_results`). Use `output/general`, `output/statistics`, `output/failures`.
- Timestamping: most modules expect/emit a timestamp string (`YYYYmmdd_HHMMSS`) to namespace results. Preserve this pattern for new file outputs.
- Error handling: centralized via `ErrorHandler` (see `error_handler_py.py`); log errors through it rather than printing directly to stdout.
- Performance/monitoring: `PerformanceMonitor` marks named stages. When adding long stages, wrap them with start_stage/end_stage to keep reports consistent.
- Data size assumptions: some analysis (correlation) converts Spark DataFrames to pandas. Avoid that for very large datasets or document a fallback using Spark's correlation functions.

## Integration points to reference in edits
- CLI entry: `Script/main_py.py` (class ParallelDataAnalysis and the `main()` function).
- Data contracts: `DataLoader.load_data(file_path)` returns a cached Spark DataFrame; callers may call `.count()` and expect non-empty DataFrames.
- Aggregation return shape: `DataAnalyzer.aggregate_data` returns a dict with keys `data`, `group_by`, `aggregated_columns` — keep this shape or migrate carefully.
- Docker compose services and ports: `spark-master` (8080 UI, 7077 master), `spark-worker-*` (8081..). Use these names when executing docker exec in automation (makefile uses `spark-master`).

## Example edits and patterns to follow (concrete)
- When adding a new analysis stage, add calls to `performance_monitor.start_stage("name")` and `end_stage("name")` around the work (see `main_py.py`).
- Persist results to `output/general/results_{timestamp}.csv` and `output/general/analysis_{timestamp}.json` using the same naming style.
- When new configuration is required, prefer adding keys to `Script/app_config.yaml` (if present) or to a new file under `Script/config/` and document the path in README.

## What not to change without explicit confirmation
- Do not rename `data_loader_py.py` or `data_analyzer_py.py` to change import paths without updating all imports. Current code imports modules as top-level names (e.g. `from data_loader import DataLoader`) so changing package layout will require a repo-wide refactor.
- Do not assume an existing `src/` package layout; `setup_py.py` expects `README.md` and `requirements.txt` but this repo uses `makefile.txt` and `requirements_txt.txt` in `Script/`. If you modify packaging, align `setup_py.py` accordingly.

## Quick checklist for PRs
- Include a short note: which scripts were updated and how they are executed (local vs Docker).
- Add or update a test or a small example run in `Script/example_test_py.py` that demonstrates the new/changed behavior.
- Ensure new I/O follows timestamp + output/ directory pattern and uses `ErrorHandler` and `PerformanceMonitor` if appropriate.

If any of the above items are unclear or you want me to expand any section with exact file snippets, tell me which section to iterate on.
