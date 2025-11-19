"""
Performance monitoring module for tracking execution metrics
"""
try:
    import time
    import psutil
    import json
    from datetime import datetime
    import os

    class PerformanceMonitor:
        def __init__(self, timestamp):
            self.timestamp = timestamp
            self.output_dir = "output/statistics"
            self.metrics = {
                'job_start_time': None,
                'job_end_time': None,
                'total_duration': 0,
                'stages': {},
                'system_metrics': {},
                'spark_metrics': {}
            }
            self.stage_times = {}
        
        def start_job(self):
            """Start job timing"""
            self.metrics['job_start_time'] = datetime.now().isoformat()
            self.job_start = time.time()
            self._collect_system_metrics('start')
        
        def end_job(self):
            """End job timing"""
            self.metrics['job_end_time'] = datetime.now().isoformat()
            self.metrics['total_duration'] = time.time() - self.job_start
            self._collect_system_metrics('end')
        
        def start_stage(self, stage_name):
            """Start timing a specific stage"""
            self.stage_times[stage_name] = {
                'start': time.time(),
                'start_time': datetime.now().isoformat()
            }
        
        def end_stage(self, stage_name):
            """End timing a specific stage"""
            if stage_name in self.stage_times:
                end_time = time.time()
                duration = end_time - self.stage_times[stage_name]['start']
                
                self.metrics['stages'][stage_name] = {
                    'start_time': self.stage_times[stage_name]['start_time'],
                    'end_time': datetime.now().isoformat(),
                    'duration_seconds': round(duration, 3),
                    'duration_formatted': self._format_duration(duration)
                }
        
        def _collect_system_metrics(self, phase):
            """Collect system resource metrics"""
            self.metrics['system_metrics'][phase] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        
        def collect_spark_metrics(self, spark_context):
            """Collect Spark-specific metrics"""
            try:
                status_tracker = spark_context.statusTracker()
                
                self.metrics['spark_metrics'] = {
                    'application_id': spark_context.applicationId,
                    'spark_version': spark_context.version,
                    'default_parallelism': spark_context.defaultParallelism,
                    'executor_count': len(spark_context._jsc.sc().getExecutorMemoryStatus()),
                }
                
                # Get job information if available
                active_jobs = status_tracker.getActiveJobIds()
                self.metrics['spark_metrics']['active_jobs'] = len(active_jobs)
                
            except Exception as e:
                self.metrics['spark_metrics']['error'] = str(e)
        
        def generate_report(self, spark_context=None):
            """Generate comprehensive performance report"""
            # Collect Spark metrics if context is provided
            if spark_context:
                self.collect_spark_metrics(spark_context)
            
            # Calculate stage percentages
            total_stage_time = sum(
                stage['duration_seconds'] 
                for stage in self.metrics['stages'].values()
            )
            
            for stage_name, stage_data in self.metrics['stages'].items():
                percentage = (stage_data['duration_seconds'] / total_stage_time * 100) if total_stage_time > 0 else 0
                stage_data['percentage_of_total'] = round(percentage, 2)
            
            # Save JSON report
            json_path = f"{self.output_dir}/performance_{self.timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(self.metrics, f, indent=4)
            
            # Generate text summary
            self._generate_text_summary()
            
            # Generate CSV for stage durations
            self._generate_csv_report()
            
            print(f"✓ Performance report saved to {self.output_dir}/")
        
        def _generate_text_summary(self):
            """Generate human-readable text summary"""
            summary_path = f"{self.output_dir}/execution_summary_{self.timestamp}.txt"
            
            with open(summary_path, 'w') as f:
                f.write("="*60 + "\n")
                f.write("PARALLEL DATA ANALYSIS - PERFORMANCE REPORT\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"Job Start Time: {self.metrics['job_start_time']}\n")
                f.write(f"Job End Time: {self.metrics['job_end_time']}\n")
                f.write(f"Total Duration: {self._format_duration(self.metrics['total_duration'])}\n\n")
                
                f.write("-"*60 + "\n")
                f.write("STAGE EXECUTION TIMES\n")
                f.write("-"*60 + "\n")
                
                for stage_name, stage_data in self.metrics['stages'].items():
                    f.write(f"\n{stage_name.upper()}:\n")
                    f.write(f"  Duration: {stage_data['duration_formatted']}\n")
                    f.write(f"  Percentage: {stage_data['percentage_of_total']}%\n")
                
                f.write("\n" + "-"*60 + "\n")
                f.write("SYSTEM RESOURCES\n")
                f.write("-"*60 + "\n")
                
                for phase, metrics in self.metrics['system_metrics'].items():
                    f.write(f"\n{phase.upper()}:\n")
                    f.write(f"  CPU Usage: {metrics['cpu_percent']}%\n")
                    f.write(f"  Memory Usage: {metrics['memory_percent']}% ")
                    f.write(f"({metrics['memory_used_gb']} GB / {metrics['memory_total_gb']} GB)\n")
                    f.write(f"  Disk Usage: {metrics['disk_usage_percent']}%\n")
                
                if 'spark_metrics' in self.metrics and self.metrics['spark_metrics']:
                    f.write("\n" + "-"*60 + "\n")
                    f.write("SPARK CLUSTER INFORMATION\n")
                    f.write("-"*60 + "\n\n")
                    
                    spark_metrics = self.metrics['spark_metrics']
                    f.write(f"Application ID: {spark_metrics.get('application_id', 'N/A')}\n")
                    f.write(f"Spark Version: {spark_metrics.get('spark_version', 'N/A')}\n")
                    f.write(f"Default Parallelism: {spark_metrics.get('default_parallelism', 'N/A')}\n")
                    f.write(f"Executor Count: {spark_metrics.get('executor_count', 'N/A')}\n")
        
        def _generate_csv_report(self):
            """Generate CSV report for node utilization"""
            csv_path = f"{self.output_dir}/node_utilization_{self.timestamp}.csv"
            
            import csv
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Stage', 'Duration (seconds)', 'Percentage', 'Start Time', 'End Time'])
                
                for stage_name, stage_data in self.metrics['stages'].items():
                    writer.writerow([
                        stage_name,
                        stage_data['duration_seconds'],
                        stage_data['percentage_of_total'],
                        stage_data['start_time'],
                        stage_data['end_time']
                    ])
        
        def _format_duration(self, seconds):
            """Format duration in human-readable format"""
            if seconds < 60:
                return f"{seconds:.2f} seconds"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.2f} minutes"
            else:
                hours = seconds / 3600
                return f"{hours:.2f} hours"
except Exception:
	# Fallback minimal PerformanceMonitor when psutil or other deps are missing
	class PerformanceMonitor:
		def __init__(self, timestamp=None):
			self.timestamp = timestamp

		def start_job(self):
			pass

		def end_job(self):
			pass

		def start_stage(self, name):
			print(f'PerformanceMonitor: start stage {name}')

		def end_stage(self, name):
			print(f'PerformanceMonitor: end stage {name}')

		def generate_report(self, spark_context=None):
			print('PerformanceMonitor: report generation skipped (minimal fallback)')