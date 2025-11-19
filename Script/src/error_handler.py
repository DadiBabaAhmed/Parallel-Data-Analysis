"""
Error handler for logging and managing failures
"""
import logging
import json
import traceback
from datetime import datetime
import os

class ErrorHandler:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.output_dir = "output/failures"
        self.error_log_path = f"{self.output_dir}/errors_{timestamp}.log"
        self.failed_tasks_path = f"{self.output_dir}/failed_tasks_{timestamp}.json"
        self.recovery_log_path = f"{self.output_dir}/recovery_actions_{timestamp}.log"
        
        self.failed_tasks = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('ParallelDataAnalysis')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for errors
        file_handler = logging.FileHandler(self.error_log_path)
        file_handler.setLevel(logging.ERROR)
        
        # Console handler for warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(self, component, error_message, additional_info=None):
        """
        Log an error with context
        
        Args:
            component: Component where error occurred
            error_message: Error message
            additional_info: Additional context information
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'error': error_message,
            'traceback': traceback.format_exc(),
            'additional_info': additional_info
        }
        
        self.failed_tasks.append(error_entry)
        
        # Log to file
        self.logger.error(f"[{component}] {error_message}")
        if additional_info:
            self.logger.error(f"Additional Info: {additional_info}")
        
        # Save failed tasks JSON
        self._save_failed_tasks()
    
    def log_warning(self, component, message):
        """Log a warning"""
        self.logger.warning(f"[{component}] {message}")
    
    def log_info(self, component, message):
        """Log informational message"""
        self.logger.info(f"[{component}] {message}")
    
    def log_recovery_attempt(self, component, action, success=False):
        """
        Log recovery attempts
        
        Args:
            component: Component being recovered
            action: Recovery action taken
            success: Whether recovery was successful
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"[{datetime.now().isoformat()}] [{component}] Recovery {status}: {action}\n"
        
        with open(self.recovery_log_path, 'a') as f:
            f.write(message)
        
        if success:
            self.logger.info(f"Recovery successful for {component}: {action}")
        else:
            self.logger.warning(f"Recovery failed for {component}: {action}")
    
    def _save_failed_tasks(self):
        """Save failed tasks to JSON file"""
        with open(self.failed_tasks_path, 'w') as f:
            json.dump(self.failed_tasks, f, indent=4)
    
    def get_error_summary(self):
        """Get summary of errors"""
        return {
            'total_errors': len(self.failed_tasks),
            'errors_by_component': self._group_errors_by_component(),
            'recent_errors': self.failed_tasks[-5:] if self.failed_tasks else []
        }
    
    def _group_errors_by_component(self):
        """Group errors by component"""
        errors_by_component = {}
        for error in self.failed_tasks:
            component = error['component']
            if component not in errors_by_component:
                errors_by_component[component] = 0
            errors_by_component[component] += 1
        return errors_by_component
    
    def has_errors(self):
        """Check if any errors occurred"""
        return len(self.failed_tasks) > 0
    
    def generate_error_report(self):
        """Generate comprehensive error report"""
        if not self.has_errors():
            return
        
        report_path = f"{self.output_dir}/error_report_{self.timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("ERROR REPORT\n")
            f.write("="*60 + "\n\n")
            
            summary = self.get_error_summary()
            f.write(f"Total Errors: {summary['total_errors']}\n\n")
            
            f.write("Errors by Component:\n")
            for component, count in summary['errors_by_component'].items():
                f.write(f"  - {component}: {count} errors\n")
            
            f.write("\n" + "-"*60 + "\n")
            f.write("DETAILED ERROR LOG\n")
            f.write("-"*60 + "\n\n")
            
            for idx, error in enumerate(self.failed_tasks, 1):
                f.write(f"Error #{idx}\n")
                f.write(f"Timestamp: {error['timestamp']}\n")
                f.write(f"Component: {error['component']}\n")
                f.write(f"Message: {error['error']}\n")
                if error.get('additional_info'):
                    f.write(f"Additional Info: {error['additional_info']}\n")
                f.write("\n")
