"""
Example test script to demonstrate the parallel data analysis framework
"""
import pandas as pd
import numpy as np
import os

def generate_sample_data():
    """Generate sample dataset for testing"""
    np.random.seed(42)
    
    # Generate sample sales data
    n_records = 10000
    
    data = {
        'date': pd.date_range('2023-01-01', periods=n_records, freq='H'),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n_records),
        'product_name': [f'Product_{i%100}' for i in range(n_records)],
        'sales_amount': np.random.uniform(10, 1000, n_records).round(2),
        'quantity': np.random.randint(1, 50, n_records),
        'customer_id': [f'CUST_{i%500}' for i in range(n_records)],
        'discount_percent': np.random.choice([0, 5, 10, 15, 20], n_records),
        'payment_method': np.random.choice(['Credit', 'Debit', 'Cash', 'Mobile'], n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Add some calculated fields
    df['final_amount'] = df['sales_amount'] * (1 - df['discount_percent']/100)
    df['profit_margin'] = np.random.uniform(0.1, 0.4, n_records).round(3)
    df['profit'] = (df['final_amount'] * df['profit_margin']).round(2)
    
    return df


def save_sample_data():
    """Save sample data in multiple formats"""
    print("Generating sample data...")
    df = generate_sample_data()
    
    # Create data directory
    os.makedirs('data/input', exist_ok=True)
    
    # Save in different formats
    print("Saving sample data...")
    
    # CSV
    df.to_csv('data/input/sample_sales.csv', index=False)
    print("✓ Saved: data/input/sample_sales.csv")
    
    # JSON
    df.to_json('data/input/sample_sales.json', orient='records', lines=True)
    print("✓ Saved: data/input/sample_sales.json")
    
    # Parquet
    df.to_parquet('data/input/sample_sales.parquet', index=False)
    print("✓ Saved: data/input/sample_sales.parquet")
    
    print(f"\n✓ Generated {len(df)} sample records")
    print(f"✓ Columns: {', '.join(df.columns)}")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Total sales: ${df['sales_amount'].sum():,.2f}")


def run_local_test():
    """Run a local test of the framework"""
    print("\n" + "="*60)
    print("Running Local Test")
    print("="*60 + "\n")
    
    # Import framework components
    from src.main import ParallelDataAnalysis
    
    # Create sample data
    save_sample_data()
    
    print("\nStarting analysis...")
    print("-"*60)
    
    # Initialize analyzer in local mode
    analyzer = ParallelDataAnalysis(
        app_name="TestAnalysis",
        master="local[*]"  # Local mode with all cores
    )
    
    # Run analysis
    analyzer.run_analysis(
        input_path="data/input/sample_sales.csv",
        analysis_type="full"
    )
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print("\nCheck the following directories for results:")
    print("  - output/general/          : Analysis results and graphs")
    print("  - output/statistics/       : Performance metrics")
    print("  - output/failures/         : Error logs (if any)")


def run_quick_analysis():
    """Run a quick analysis demonstration"""
    from pyspark.sql import SparkSession
    from src.data_loader import DataLoader
    from src.data_analyzer import DataAnalyzer
    from src.error_handler import ErrorHandler
    from datetime import datetime
    
    print("\n" + "="*60)
    print("Quick Analysis Demo")
    print("="*60 + "\n")
    
    # Generate data
    df_pandas = generate_sample_data()
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("QuickDemo") \
        .master("local[*]") \
        .getOrCreate()
    
    # Convert to Spark DataFrame
    df_spark = spark.createDataFrame(df_pandas)
    
    # Initialize components
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_handler = ErrorHandler(timestamp)
    analyzer = DataAnalyzer(spark, error_handler)
    
    print("Performing statistical analysis...")
    stats = analyzer.statistical_analysis(df_spark)
    
    print("\n✓ Statistical Analysis Complete")
    print(f"  - Analyzed {len(stats)-1} numeric columns")
    
    print("\nPerforming aggregation...")
    agg = analyzer.aggregate_data(df_spark)
    
    print("✓ Aggregation Complete")
    print(f"  - Grouped by: {agg['group_by']}")
    print(f"  - Aggregated columns: {agg['aggregated_columns']}")
    
    print("\nPerforming correlation analysis...")
    corr = analyzer.correlation_analysis(df_spark)
    
    print("✓ Correlation Analysis Complete")
    print(f"  - Analyzed correlations between {len(corr['columns'])} columns")
    
    # Show sample results
    print("\n" + "-"*60)
    print("Sample Results:")
    print("-"*60)
    print("\nSales Amount Statistics:")
    if 'sales_amount' in stats:
        sales_stats = stats['sales_amount']
        print(f"  Mean: ${sales_stats['mean']:.2f}")
        print(f"  Median: ${sales_stats['median']:.2f}")
        print(f"  Std Dev: ${sales_stats['stddev']:.2f}")
        print(f"  Min: ${sales_stats['min']:.2f}")
        print(f"  Max: ${sales_stats['max']:.2f}")
    
    spark.stop()
    
    print("\n✓ Demo Complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick demo without full framework
        run_quick_analysis()
    elif len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Just generate data
        save_sample_data()
    else:
        # Full test
        run_local_test()
