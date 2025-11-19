"""
Utility functions for the parallel data analysis framework
"""
import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class ConfigLoader:
    """Load and manage configuration settings"""
    
    @staticmethod
    def load_yaml_config(config_path: str = "config/app_config.yaml") -> Dict:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    @staticmethod
    def get_spark_config(mode: str = 'local') -> Dict:
        """Get Spark configuration based on mode"""
        from config.spark_config import get_spark_config as get_config
        return get_config(mode)
    
    @staticmethod
    def merge_configs(*configs: Dict) -> Dict:
        """Merge multiple configuration dictionaries"""
        merged = {}
        for config in configs:
            merged.update(config)
        return merged


class FileUtils:
    """File and directory utilities"""
    
    @staticmethod
    def ensure_dir(directory: str):
        """Ensure directory exists"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(filepath)
    
    @staticmethod
    def get_file_size_human(filepath: str) -> str:
        """Get human-readable file size"""
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
        """List files in directory with optional extension filter"""
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            if extension is None or file.endswith(extension):
                files.append(os.path.join(directory, file))
        return files
    
    @staticmethod
    def save_json(data: Dict, filepath: str):
        """Save data as JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4, default=str)
    
    @staticmethod
    def load_json(filepath: str) -> Dict:
        """Load JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)


class TimeUtils:
    """Time and date utilities"""
    
    @staticmethod
    def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime(format)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.2f} hours"
    
    @staticmethod
    def parse_time_interval(interval_str: str) -> int:
        """
        Parse time interval string to seconds
        Examples: '1h', '30m', '90s'
        """
        unit = interval_str[-1].lower()
        value = int(interval_str[:-1])
        
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        else:
            raise ValueError(f"Unknown time unit: {unit}")


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_dataframe(df) -> bool:
        """Validate that DataFrame is not None and not empty"""
        if df is None:
            raise ValueError("DataFrame is None")
        if df.count() == 0:
            raise ValueError("DataFrame is empty")
        return True
    
    @staticmethod
    def validate_columns(df, required_columns: List[str]) -> bool:
        """Validate that required columns exist"""
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True
    
    @staticmethod
    def check_null_percentage(df, column: str, threshold: float = 0.5) -> Dict:
        """Check null percentage in a column"""
        total = df.count()
        nulls = df.filter(df[column].isNull()).count()
        null_percentage = nulls / total if total > 0 else 0
        
        return {
            'column': column,
            'total_rows': total,
            'null_count': nulls,
            'null_percentage': null_percentage,
            'exceeds_threshold': null_percentage > threshold
        }
    
    @staticmethod
    def infer_data_types(df) -> Dict[str, str]:
        """Infer data types of DataFrame columns"""
        return {field.name: str(field.dataType) for field in df.schema.fields}


class SparkUtils:
    """Spark-specific utilities"""
    
    @staticmethod
    def get_partition_info(df) -> Dict:
        """Get partition information"""
        return {
            'num_partitions': df.rdd.getNumPartitions(),
            'is_cached': df.is_cached
        }
    
    @staticmethod
    def optimize_partitions(df, target_size_mb: int = 128):
        """Optimize number of partitions based on data size"""
        # Estimate data size
        estimated_size = df.rdd.map(lambda x: len(str(x))).sum() / (1024 * 1024)
        optimal_partitions = max(1, int(estimated_size / target_size_mb))
        
        return df.repartition(optimal_partitions)
    
    @staticmethod
    def explain_plan(df, mode: str = "simple"):
        """Print query execution plan"""
        if mode == "simple":
            df.explain()
        elif mode == "extended":
            df.explain(extended=True)
        elif mode == "cost":
            df.explain(mode="cost")


class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def add_metric(self, key: str, value: Any):
        """Add a metric"""
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)
    
    def get_metric(self, key: str) -> List:
        """Get metric values"""
        return self.metrics.get(key, [])
    
    def get_average(self, key: str) -> Optional[float]:
        """Get average of metric"""
        values = self.get_metric(key)
        return sum(values) / len(values) if values else None
    
    def get_summary(self) -> Dict:
        """Get summary of all metrics"""
        summary = {}
        for key, values in self.metrics.items():
            if isinstance(values[0], (int, float)):
                summary[key] = {
                    'count': len(values),
                    'sum': sum(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
            else:
                summary[key] = {
                    'count': len(values),
                    'values': values
                }
        return summary
    
    def export_to_file(self, filepath: str):
        """Export metrics to JSON file"""
        FileUtils.save_json(self.get_summary(), filepath)


class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def info(message: str):
        """Log info message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] [{timestamp}] {message}")
    
    @staticmethod
    def warning(message: str):
        """Log warning message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] [{timestamp}] {message}")
    
    @staticmethod
    def error(message: str):
        """Log error message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] [{timestamp}] {message}")
    
    @staticmethod
    def success(message: str):
        """Log success message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[SUCCESS] [{timestamp}] {message}")


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def calculate_speedup(sequential_time: float, parallel_time: float) -> float:
    """Calculate speedup factor"""
    return sequential_time / parallel_time if parallel_time > 0 else 0


def calculate_efficiency(speedup: float, num_processors: int) -> float:
    """Calculate parallel efficiency"""
    return speedup / num_processors if num_processors > 0 else 0


def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                       suffix: str = '', length: int = 50, fill: str = '█'):
    """Print a progress bar"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()
