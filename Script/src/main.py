"""
Main entry point for parallel data analysis
"""
import os
import sys
import argparse
from datetime import datetime
from pyspark.sql import SparkSession
from src.data_loader import DataLoader
from src.data_analyzer import DataAnalyzer
from src.graph_generator import GraphGenerator
from src.performance_monitor import PerformanceMonitor
from src.error_handler import ErrorHandler

class ParallelDataAnalysis:
    def __init__(self, app_name="ParallelDataAnalysis", master="local[*]"):
        """Initialize the parallel data analysis framework"""
        self.app_name = app_name
        self.master = master
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        self.create_output_dirs()
        
        # Initialize components
        self.error_handler = ErrorHandler(self.timestamp)
        self.performance_monitor = PerformanceMonitor(self.timestamp)
        
        # Initialize Spark
        self.spark = self.init_spark()
        
        # Initialize modules
        self.data_loader = DataLoader(self.spark, self.error_handler)
        self.analyzer = DataAnalyzer(self.spark, self.error_handler)
        self.graph_gen = GraphGenerator(self.timestamp)
        
    def create_output_dirs(self):
        """Create output directory structure"""
        dirs = [
            'output/general',
            'output/general/graphs',
            'output/statistics',
            'output/failures'
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def init_spark(self):
        """Initialize Spark Session with optimized configuration"""
        try:
            spark = SparkSession.builder \
                .appName(self.app_name) \
                .master(self.master) \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.speculation", "true") \
                .config("spark.task.maxFailures", "4") \
                .getOrCreate()
            
            spark.sparkContext.setLogLevel("WARN")
            return spark
        except Exception as e:
            self.error_handler.log_error("Spark Initialization", str(e))
            raise
    
    def run_analysis(self, input_path, analysis_type="full"):
        """
        Run complete data analysis pipeline
        
        Args:
            input_path: Path to input data file
            analysis_type: Type of analysis (full, statistical, aggregation)
        """
        print(f"\n{'='*60}")
        print(f"Starting Parallel Data Analysis - {self.timestamp}")
        print(f"{'='*60}\n")
        
        self.performance_monitor.start_job()
        
        try:
            # Step 1: Load Data
            print("Step 1: Loading data...")
            self.performance_monitor.start_stage("data_loading")
            df = self.data_loader.load_data(input_path)
            self.performance_monitor.end_stage("data_loading")
            print(f"✓ Loaded {df.count()} records")
            
            # Step 2: Data Analysis
            print("\nStep 2: Performing analysis...")
            results = {}
            
            if analysis_type in ["full", "statistical"]:
                print("  - Statistical analysis...")
                self.performance_monitor.start_stage("statistical_analysis")
                results['statistics'] = self.analyzer.statistical_analysis(df)
                self.performance_monitor.end_stage("statistical_analysis")
            
            if analysis_type in ["full", "aggregation"]:
                print("  - Data aggregation...")
                self.performance_monitor.start_stage("aggregation")
                results['aggregation'] = self.analyzer.aggregate_data(df)
                self.performance_monitor.end_stage("aggregation")
            
            if analysis_type == "full":
                print("  - Correlation analysis...")
                self.performance_monitor.start_stage("correlation")
                results['correlation'] = self.analyzer.correlation_analysis(df)
                self.performance_monitor.end_stage("correlation")
            
            # Step 3: Generate Graphs
            print("\nStep 3: Generating visualizations...")
            self.performance_monitor.start_stage("visualization")
            self.graph_gen.generate_all_graphs(df, results)
            self.performance_monitor.end_stage("visualization")
            
            # Step 4: Save Results
            print("\nStep 4: Saving results...")
            self.save_results(df, results)
            
            # Step 5: Generate Performance Report
            self.performance_monitor.end_job()
            self.performance_monitor.generate_report(self.spark.sparkContext)
            
            print(f"\n{'='*60}")
            print("Analysis completed successfully!")
            print(f"Results saved in output/ directory")
            print(f"{'='*60}\n")
            
        except Exception as e:
            self.error_handler.log_error("Analysis Pipeline", str(e))
            self.performance_monitor.end_job()
            raise
        
        finally:
            self.cleanup()
    
    def save_results(self, df, results):
        """Save analysis results to output directory"""
        # Save processed data using Spark writer to avoid collecting entire dataset
        spark_output_dir = f"output/general/results_{self.timestamp}_spark"
        try:
            # write as CSV files (partitioned); also write a small single-file sample for quick preview
            df.write.mode('overwrite').option('header', 'true').csv(spark_output_dir)
        except Exception:
            # fallback: try coalescing to a single file for small datasets
            try:
                df.coalesce(1).write.mode('overwrite').option('header', 'true').csv(spark_output_dir)
            except Exception as e:
                self.error_handler.log_warning('SaveResults', f'Could not write Spark CSV: {e}')

        # Create a small CSV preview (collect limited rows to driver)
        preview_path = f"output/general/results_{self.timestamp}.csv"
        try:
            df.limit(1000).toPandas().to_csv(preview_path, index=False)
        except Exception as e:
            # If preview fails, log and continue
            self.error_handler.log_warning('SaveResults', f'Preview CSV generation failed: {e}')
        
        # Save analysis summary
        import json
        summary_path = f"output/general/analysis_{self.timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"✓ Results saved to {preview_path}")
        print(f"✓ Analysis summary saved to {summary_path}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.spark:
            self.spark.stop()


def main():
    parser = argparse.ArgumentParser(description='Parallel Data Analysis Framework')
    parser.add_argument('--input', required=True, help='Input data file path')
    parser.add_argument('--master', default='local[*]', help='Spark master URL')
    parser.add_argument('--analysis', default='full', 
                       choices=['full', 'statistical', 'aggregation'],
                       help='Type of analysis to perform')
    
    args = parser.parse_args()
    
    # Initialize and run analysis
    analyzer = ParallelDataAnalysis(master=args.master)
    analyzer.run_analysis(args.input, args.analysis)


if __name__ == "__main__":
    main()
