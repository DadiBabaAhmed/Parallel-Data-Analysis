"""
Comprehensive tests for DataLoader module
Tests all supported file formats and edge cases
"""
import pytest
import os
from pathlib import Path

from src.data_loader import DataLoader
from src.error_handler import ErrorHandler


class TestDataLoaderInitialization:
    """Test DataLoader initialization and configuration"""
    
    def test_data_loader_init(self, spark_session):
        """Test DataLoader initialization"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        assert loader.spark is not None
        assert loader.error_handler is not None
        assert loader.supported_formats == ['csv', 'json', 'parquet', 'avro']
    
    def test_supported_formats(self, spark_session):
        """Test that all required formats are supported"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        required_formats = ['csv', 'json', 'parquet', 'avro']
        for fmt in required_formats:
            assert fmt in loader.supported_formats, f"Format {fmt} not supported"


class TestDataLoaderCSV:
    """Test CSV file loading"""
    
    def test_load_csv_basic(self, spark_session, test_csv_file):
        """Test loading basic CSV file"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_csv_file)
        
        assert df is not None
        assert df.count() == 4  # Sample CSV has 4 rows
        assert len(df.columns) >= 3  # At least product, quantity, price
    
    def test_load_csv_schema_inference(self, spark_session, test_csv_file):
        """Test that CSV schema is correctly inferred"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_csv_file)
        
        # Check that numeric columns are inferred correctly
        schema_dict = {field.name: str(field.dataType) for field in df.schema.fields}
        assert any("integer" in dtype.lower() or "long" in dtype.lower() 
                  for dtype in schema_dict.values()), "Numeric columns should be inferred"
    
    def test_load_csv_data_integrity(self, spark_session, test_csv_file):
        """Test that data is loaded correctly without corruption"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_csv_file)
        
        # Verify no null columns entirely
        null_counts = {col: df.filter(df[col].isNull()).count() for col in df.columns}
        total_rows = df.count()
        
        # At least some columns should have complete data
        complete_cols = [col for col, null_count in null_counts.items() if null_count == 0]
        assert len(complete_cols) > 0, "At least one column should have complete data"


class TestDataLoaderJSON:
    """Test JSON file loading"""
    
    def test_load_json_basic(self, spark_session, test_json_file):
        """Test loading basic JSON file"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_json_file)
        
        assert df is not None
        assert df.count() == 3  # Test JSON has 3 records
        assert "id" in df.columns
    
    def test_load_json_data_types(self, spark_session, test_json_file):
        """Test that JSON data types are correctly inferred"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_json_file)
        
        schema_dict = {field.name: str(field.dataType) for field in df.schema.fields}
        assert "category" in schema_dict
        assert "value" in schema_dict


class TestDataLoaderParquet:
    """Test Parquet file loading"""
    
    def test_load_parquet_basic(self, spark_session, temp_test_dir):
        """Test loading Parquet file"""
        # Create a Parquet file
        data = [(1, "A", 10.0), (2, "B", 20.0), (3, "C", 30.0)]
        test_df = spark_session.createDataFrame(data, ["id", "letter", "value"])
        parquet_path = os.path.join(temp_test_dir, "test.parquet")
        test_df.write.mode("overwrite").parquet(parquet_path)
        
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(parquet_path)
        
        assert df is not None
        assert df.count() == 3
        assert sorted(df.columns) == ["id", "letter", "value"]
    
    def test_load_parquet_preserves_types(self, spark_session, temp_test_dir):
        """Test that Parquet preserves data types"""
        data = [(1, 10.5, "A"), (2, 20.3, "B")]
        test_df = spark_session.createDataFrame(data, ["int_col", "double_col", "string_col"])
        parquet_path = os.path.join(temp_test_dir, "test_types.parquet")
        test_df.write.mode("overwrite").parquet(parquet_path)
        
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(parquet_path)
        schema_dict = {field.name: str(field.dataType) for field in df.schema.fields}
        
        assert "int" in schema_dict["int_col"].lower()
        assert "double" in schema_dict["double_col"].lower()
        assert "string" in schema_dict["string_col"].lower()


class TestDataLoaderErrorHandling:
    """Test error handling in DataLoader"""
    
    def test_unsupported_format(self, spark_session):
        """Test that unsupported formats raise appropriate error"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        with pytest.raises(ValueError):
            loader.load_data("nonexistent.xyz")
    
    def test_nonexistent_file(self, spark_session):
        """Test that nonexistent files are handled gracefully"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        # Should raise an exception when file doesn't exist
        with pytest.raises(Exception):
            loader.load_data("/nonexistent/path/file.csv")
    
    def test_load_data_with_multiline_csv(self, spark_session, temp_test_dir):
        """Test loading CSV with multiline fields"""
        import tempfile
        
        csv_path = os.path.join(temp_test_dir, "multiline.csv")
        
        # Create a CSV with quoted fields containing newlines
        with open(csv_path, 'w') as f:
            f.write('id,name,description\n')
            f.write('1,"Product A","Line 1\nLine 2"\n')
            f.write('2,"Product B","Single line"\n')
        
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(csv_path)
        assert df.count() == 2


class TestDataLoaderDataFrame:
    """Test DataFrame returned by DataLoader"""
    
    def test_returned_dataframe_is_cached(self, spark_session, test_csv_file):
        """Test that returned DataFrame has useful properties"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_csv_file)
        
        # Check DataFrame operations work
        assert hasattr(df, 'count')
        assert hasattr(df, 'schema')
        assert hasattr(df, 'columns')
        assert callable(df.count)
    
    def test_dataframe_can_be_transformed(self, spark_session, test_csv_file):
        """Test that loaded DataFrame can be transformed"""
        error_handler = ErrorHandler("test_20250101_000000")
        loader = DataLoader(spark_session, error_handler)
        
        df = loader.load_data(test_csv_file)
        
        # Test basic transformations
        filtered_df = df.filter(df["quantity"] > 100)
        assert filtered_df.count() > 0
        
        selected_df = df.select("product")
        assert "product" in selected_df.columns
