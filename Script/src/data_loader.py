"""
Data loader module for handling multiple data formats
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import os

class DataLoader:
    def __init__(self, spark, error_handler):
        self.spark = spark
        self.error_handler = error_handler
        self.supported_formats = ['csv', 'json', 'parquet', 'avro']
    
    def load_data(self, file_path):
        """
        Load data from various file formats
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Spark DataFrame
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower().replace('.', '')
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported format: {file_extension}")
            
            if file_extension == 'csv':
                return self._load_csv(file_path)
            elif file_extension == 'json':
                return self._load_json(file_path)
            elif file_extension == 'parquet':
                return self._load_parquet(file_path)
            elif file_extension == 'avro':
                return self._load_avro(file_path)
                
        except Exception as e:
            self.error_handler.log_error("Data Loading", str(e))
            raise
    
    def _load_csv(self, file_path):
        """Load CSV file with automatic schema inference"""
        df = self.spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .option("multiLine", "true") \
            .csv(file_path)
        
        return self._validate_dataframe(df)
    
    def _load_json(self, file_path):
        """Load JSON file"""
        df = self.spark.read \
            .option("multiLine", "true") \
            .json(file_path)
        
        return self._validate_dataframe(df)
    
    def _load_parquet(self, file_path):
        """Load Parquet file"""
        df = self.spark.read.parquet(file_path)
        return self._validate_dataframe(df)
    
    def _load_avro(self, file_path):
        """Load Avro file"""
        df = self.spark.read.format("avro").load(file_path)
        return self._validate_dataframe(df)
    
    def _validate_dataframe(self, df):
        """
        Validate loaded DataFrame
        
        Args:
            df: Spark DataFrame
            
        Returns:
            Validated DataFrame
        """
        if df is None:
            raise ValueError("DataFrame is None")
        
        if df.count() == 0:
            raise ValueError("DataFrame is empty")
        
        # Cache the dataframe for better performance
        df.cache()
        
        return df
    
    def get_schema_info(self, df):
        """Get detailed schema information"""
        schema_info = {
            'columns': df.columns,
            'num_columns': len(df.columns),
            'num_rows': df.count(),
            'schema': df.schema.json()
        }
        return schema_info
    
    def detect_skewness(self, df, column):
        """
        Detect data skewness in a column
        
        Args:
            df: Spark DataFrame
            column: Column name to check
            
        Returns:
            Skewness statistics
        """
        from pyspark.sql.functions import col, count, avg
        
        distribution = df.groupBy(column) \
            .agg(count("*").alias("count")) \
            .orderBy(col("count").desc())
        
        total_count = df.count()
        top_values = distribution.limit(10).collect()
        
        skewness_info = {
            'total_records': total_count,
            'unique_values': distribution.count(),
            'top_values': [(row[column], row['count'], 
                          row['count']/total_count*100) 
                          for row in top_values]
        }
        
        return skewness_info
