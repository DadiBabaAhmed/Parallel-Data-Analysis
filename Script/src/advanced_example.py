"""
Advanced usage examples for Parallel Data Analysis Framework
"""
import sys
sys.path.append('..')

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import framework components
from data_loader import DataLoader
from data_analyzer import DataAnalyzer
from error_handler import ErrorHandler
from performance_monitor import PerformanceMonitor
from graph_generator import GraphGenerator
from spark_jobs.mapreduce_job import MapReduceJob
from spark_jobs.aggregation_job import AggregationJob
from spark_jobs.statistical_analysis import StatisticalAnalysis


class AdvancedExamples:
    """Advanced usage examples"""
    
    def __init__(self, master="local[*]"):
        self.spark = SparkSession.builder \
            .appName("AdvancedExamples") \
            .master(master) \
            .getOrCreate()
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.error_handler = ErrorHandler(self.timestamp)
        self.performance_monitor = PerformanceMonitor(self.timestamp)
        
    def example_1_time_series_analysis(self):
        """Example: Comprehensive time series analysis"""
        print("\n" + "="*60)
        print("Example 1: Time Series Analysis")
        print("="*60 + "\n")
        
        # Generate time series data
        dates = pd.date_range('2023-01-01', periods=1000, freq='H')
        data = {
            'timestamp': dates,
            'temperature': 20 + 10 * np.sin(np.arange(1000) * 2 * np.pi / 24) + np.random.normal(0, 2, 1000),
            'humidity': 50 + 20 * np.sin(np.arange(1000) * 2 * np.pi / 24 + np.pi/4) + np.random.normal(0, 5, 1000),
            'sensor_id': np.random.choice(['S1', 'S2', 'S3'], 1000)
        }
        
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        # Perform time series aggregation
        agg_job = AggregationJob()
        hourly_stats = agg_job.time_series_aggregation(
            df, 'timestamp', 'temperature', interval='1 day'
        )
        
        print("✓ Daily temperature aggregation:")
        hourly_stats.show(5)
        
        # Decomposition
        stats_job = StatisticalAnalysis()
        decomposed = stats_job.time_series_decomposition(
            df, 'timestamp', 'temperature', period=24
        )
        
        print("\n✓ Time series decomposition:")
        decomposed.select('timestamp', 'temperature', 'trend', 'seasonal', 'residual').show(5)
        
    def example_2_advanced_aggregations(self):
        """Example: Advanced aggregation techniques"""
        print("\n" + "="*60)
        print("Example 2: Advanced Aggregations")
        print("="*60 + "\n")
        
        # Generate sales data
        data = {
            'region': np.random.choice(['North', 'South', 'East', 'West'], 500),
            'product': np.random.choice(['A', 'B', 'C', 'D'], 500),
            'quarter': np.random.choice(['Q1', 'Q2', 'Q3', 'Q4'], 500),
            'sales': np.random.uniform(1000, 10000, 500),
            'units': np.random.randint(10, 100, 500)
        }
        
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        agg_job = AggregationJob()
        
        # Multi-level aggregation
        print("Multi-level aggregation:")
        multi_level = agg_job.multi_level_aggregation(
            df,
            group_cols=['region', 'product'],
            agg_cols=['sales', 'units']
        )
        multi_level.show(10)
        
        # CUBE aggregation
        print("\nCUBE aggregation (all combinations):")
        cube_result = agg_job.cube_aggregation(
            df,
            dimensions=['region', 'quarter'],
            measures={'sales': 'sum', 'units': 'sum'}
        )
        cube_result.show(10)
        
        # Pivot table
        print("\nPivot table:")
        pivot_result = agg_job.pivot_aggregation(
            df, 'region', 'product', 'sales', 'sum'
        )
        pivot_result.show()
        
        # Running totals
        print("\nRunning totals:")
        running = agg_job.running_totals(
            df.orderBy('quarter'), 'region', 'quarter', 'sales'
        )
        running.select('region', 'quarter', 'sales', 'sales_running_total').show(10)
        
    def example_3_statistical_analysis(self):
        """Example: Advanced statistical analysis"""
        print("\n" + "="*60)
        print("Example 3: Statistical Analysis")
        print("="*60 + "\n")
        
        # Generate data
        data = {
            'value': np.random.normal(100, 15, 1000),
            'category': np.random.choice(['A', 'B', 'C'], 1000),
            'score': np.random.uniform(0, 100, 1000)
        }
        
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        stats_job = StatisticalAnalysis()
        
        # Descriptive statistics
        print("Descriptive statistics:")
        desc_stats = stats_job.descriptive_statistics(df, ['value', 'score'])
        
        for col, stats in desc_stats.items():
            print(f"\n{col}:")
            print(f"  Mean: {stats['mean']:.2f}")
            print(f"  Median: {stats['median']:.2f}")
            print(f"  Std Dev: {stats['stddev']:.2f}")
            print(f"  Skewness: {stats['skewness']:.2f}")
            print(f"  Kurtosis: {stats['kurtosis']:.2f}")
            if 'outlier_count' in stats:
                print(f"  Outliers: {stats['outlier_count']} ({stats['outlier_percent']:.2f}%)")
        
        # Correlation analysis
        print("\nCorrelation matrix:")
        corr_matrix = stats_job.correlation_matrix(df, ['value', 'score'])
        for col1, correlations in corr_matrix.items():
            for col2, corr in correlations.items():
                print(f"  Corr({col1}, {col2}): {corr:.3f}")
        
        # Anomaly detection
        print("\nAnomaly detection (Z-score method):")
        anomalies = stats_job.detect_anomalies(df, 'value', method='zscore', threshold=3)
        anomaly_count = anomalies.filter(F.col('is_anomaly') == True).count()
        print(f"  Found {anomaly_count} anomalies")
        
        # Frequency distribution
        print("\nFrequency distribution:")
        freq_dist = stats_job.frequency_distribution(df, 'value', bins=10)
        for bin_info in freq_dist[:5]:
            print(f"  {bin_info['range']}: {bin_info['frequency']} records")
        
    def example_4_mapreduce_operations(self):
        """Example: MapReduce operations"""
        print("\n" + "="*60)
        print("Example 4: MapReduce Operations")
        print("="*60 + "\n")
        
        # Generate data
        data = {
            'user_id': [f'U{i%100}' for i in range(1000)],
            'product': np.random.choice(['Laptop', 'Phone', 'Tablet'], 1000),
            'amount': np.random.uniform(100, 2000, 1000),
            'quantity': np.random.randint(1, 5, 1000)
        }
        
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        mapreduce_job = MapReduceJob()
        
        # Group and sum
        print("Total sales by product:")
        product_sales = mapreduce_job.group_sum(df, 'product', 'amount')
        product_sales.show()
        
        # Top N customers
        print("\nTop 10 customers by spending:")
        top_customers = mapreduce_job.top_n_by_group(
            df, 'product', 'amount', n=10
        )
        top_customers.show(10)
        
        # Moving average
        print("\nMoving average (window size=3):")
        moving_avg = mapreduce_job.moving_average(
            df.orderBy('user_id'),
            'product', 'user_id', 'amount', window_size=3
        )
        moving_avg.select('user_id', 'product', 'amount', 'moving_avg_amount').show(10)
        
    def example_5_performance_optimization(self):
        """Example: Performance optimization techniques"""
        print("\n" + "="*60)
        print("Example 5: Performance Optimization")
        print("="*60 + "\n")
        
        # Generate large dataset
        n_records = 100000
        data = {
            'id': range(n_records),
            'value': np.random.random(n_records),
            'category': np.random.choice(['A', 'B', 'C', 'D'], n_records)
        }
        
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        print(f"Dataset size: {n_records} records")
        print(f"Number of partitions: {df.rdd.getNumPartitions()}")
        
        # Caching
        self.performance_monitor.start_stage('without_cache')
        df.groupBy('category').count().collect()
        self.performance_monitor.end_stage('without_cache')
        
        df.cache()
        
        self.performance_monitor.start_stage('with_cache')
        df.groupBy('category').count().collect()
        self.performance_monitor.end_stage('with_cache')
        
        print("\n✓ Performance comparison:")
        without_cache = self.performance_monitor.metrics['stages']['without_cache']['duration_seconds']
        with_cache = self.performance_monitor.metrics['stages']['with_cache']['duration_seconds']
        speedup = without_cache / with_cache if with_cache > 0 else 0
        
        print(f"  Without cache: {without_cache:.3f}s")
        print(f"  With cache: {with_cache:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Repartitioning
        print(f"\nOptimizing partitions...")
        optimal_partitions = max(1, n_records // 10000)
        df_repartitioned = df.repartition(optimal_partitions)
        print(f"  New partition count: {df_repartitioned.rdd.getNumPartitions()}")
        
    def example_6_error_handling(self):
        """Example: Error handling and recovery"""
        print("\n" + "="*60)
        print("Example 6: Error Handling")
        print("="*60 + "\n")
        
        # Simulate various error scenarios
        data = {'value': [1, 2, None, 4, 5]}
        df_pandas = pd.DataFrame(data)
        df = self.spark.createDataFrame(df_pandas)
        
        try:
            # This will handle null values gracefully
            result = df.filter(F.col('value').isNotNull()).count()
            print(f"✓ Successfully handled null values: {result} valid records")
        except Exception as e:
            self.error_handler.log_error("Null Handling", str(e))
        
        # Logging recovery attempts
        self.error_handler.log_recovery_attempt(
            "Data Validation",
            "Filtered null values",
            success=True
        )
        
        # Generate error report
        if self.error_handler.has_errors():
            self.error_handler.generate_error_report()
            print("\n✓ Error report generated")
    
    def run_all_examples(self):
        """Run all examples"""
        self.performance_monitor.start_job()
        
        try:
            self.example_1_time_series_analysis()
            self.example_2_advanced_aggregations()
            self.example_3_statistical_analysis()
            self.example_4_mapreduce_operations()
            self.example_5_performance_optimization()
            self.example_6_error_handling()
            
            self.performance_monitor.end_job()
            self.performance_monitor.generate_report(self.spark.sparkContext)
            
            print("\n" + "="*60)
            print("All Examples Completed Successfully!")
            print("="*60)
            print("\nCheck output/ directory for detailed results")
            
        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            self.error_handler.log_error("Examples", str(e))
        
        finally:
            self.spark.stop()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Examples')
    parser.add_argument('--master', default='local[*]', 
                       help='Spark master URL')
    parser.add_argument('--example', type=int, choices=range(1, 7),
                       help='Run specific example (1-6)')
    
    args = parser.parse_args()
    
    examples = AdvancedExamples(master=args.master)
    
    if args.example:
        # Run specific example
        example_methods = [
            examples.example_1_time_series_analysis,
            examples.example_2_advanced_aggregations,
            examples.example_3_statistical_analysis,
            examples.example_4_mapreduce_operations,
            examples.example_5_performance_optimization,
            examples.example_6_error_handling
        ]
        example_methods[args.example - 1]()
    else:
        # Run all examples
        examples.run_all_examples()


if __name__ == "__main__":
    main()
