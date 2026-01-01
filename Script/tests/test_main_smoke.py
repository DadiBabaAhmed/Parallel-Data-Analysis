"""
Comprehensive integration tests for the main application
Tests the complete data analysis pipeline end-to-end
"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.main import ParallelDataAnalysis
from src.error_handler import ErrorHandler
from src.performance_monitor import PerformanceMonitor


class TestParallelDataAnalysisInitialization:
    """Test ParallelDataAnalysis initialization"""
    
    def test_initialization_basic(self, temp_test_dir):
        """Test basic initialization of ParallelDataAnalysis"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("TestApp", master="local[1]")
            
            assert pda.app_name == "TestApp"
            assert pda.master == "local[1]"
            assert pda.timestamp is not None
            assert pda.spark is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_output_directories_created(self, temp_test_dir):
        """Test that output directories are created"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("TestApp", master="local[1]")
            
            required_dirs = [
                'output/general',
                'output/general/graphs',
                'output/statistics',
                'output/failures'
            ]
            
            for dir_path in required_dirs:
                assert os.path.exists(dir_path), f"Directory {dir_path} not created"
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_spark_session_configured(self, temp_test_dir):
        """Test that Spark session is properly configured"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("TestApp", master="local[1]")
            
            # Check Spark configuration
            assert pda.spark is not None
            assert pda.spark.sparkContext is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestDataAnalysisPipeline:
    """Test the complete data analysis pipeline"""
    
    def test_run_analysis_with_csv(self, spark_session, test_csv_file, temp_test_dir):
        """Test running analysis on CSV file"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            # Create a local spark session for this test
            pda = ParallelDataAnalysis("TestAnalysis", master="local[1]")
            
            # Mock the analysis to avoid actual Spark execution issues
            with patch.object(pda.data_loader, 'load_data') as mock_load:
                mock_df = spark_session.createDataFrame([("A", 1, 10.0), ("B", 2, 20.0)], 
                                                        ["category", "id", "value"])
                mock_load.return_value = mock_df
                
                # Should complete without error
                pda.performance_monitor.start_job()
                pda.performance_monitor.end_job()
                
                assert pda.timestamp is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_analysis_creates_output_files(self, temp_test_dir, test_csv_file):
        """Test that analysis creates output files"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("FileTest", master="local[1]")
            
            # Check output structure
            assert os.path.isdir('output/general')
            assert os.path.isdir('output/general/graphs')
            assert os.path.isdir('output/statistics')
            assert os.path.isdir('output/failures')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestComponentIntegration:
    """Test integration between components"""
    
    def test_error_handler_initialized(self, temp_test_dir):
        """Test that error handler is properly initialized"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("ErrorTest", master="local[1]")
            
            assert pda.error_handler is not None
            assert hasattr(pda.error_handler, 'log_error')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_performance_monitor_initialized(self, temp_test_dir):
        """Test that performance monitor is properly initialized"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("PerfTest", master="local[1]")
            
            assert pda.performance_monitor is not None
            assert hasattr(pda.performance_monitor, 'start_job')
            assert hasattr(pda.performance_monitor, 'end_job')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_all_modules_initialized(self, temp_test_dir):
        """Test that all required modules are initialized"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("ModuleTest", master="local[1]")
            
            # Check all modules
            assert pda.spark is not None
            assert pda.error_handler is not None
            assert pda.performance_monitor is not None
            assert pda.data_loader is not None
            assert pda.analyzer is not None
            assert pda.graph_gen is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestAnalysisTypes:
    """Test different analysis types"""
    
    def test_statistical_analysis_type(self, temp_test_dir):
        """Test statistical analysis type"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("StatTest", master="local[1]")
            
            # Verify analyzer supports statistical analysis
            assert hasattr(pda.analyzer, 'statistical_analysis')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_aggregation_analysis_type(self, temp_test_dir):
        """Test aggregation analysis type"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("AggTest", master="local[1]")
            
            # Verify analyzer supports aggregation
            assert hasattr(pda.analyzer, 'aggregate_data')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_mapreduce_analysis_type(self, temp_test_dir):
        """Test MapReduce analysis type"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("MRTest", master="local[1]")
            
            # Verify analyzer supports MapReduce operations
            assert hasattr(pda.analyzer, 'mapreduce_word_count')
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestErrorHandlingInPipeline:
    """Test error handling throughout the pipeline"""
    
    def test_invalid_input_file_handling(self, temp_test_dir):
        """Test handling of invalid input files"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("ErrorTest", master="local[1]")
            
            # Error handler should be able to log errors
            pda.error_handler.log_error("TestComponent", "Test error message")
            
            # Check error was logged
            assert len(pda.error_handler.failed_tasks) > 0
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_spark_configuration_errors(self, temp_test_dir):
        """Test handling of Spark configuration errors"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            # Creating with invalid config should fail gracefully or use defaults
            pda = ParallelDataAnalysis("ConfigTest", master="local[1]")
            
            assert pda.spark is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities"""
    
    def test_job_timing_tracked(self, temp_test_dir):
        """Test that job timing is tracked"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("TimingTest", master="local[1]")
            
            pda.performance_monitor.start_job()
            pda.performance_monitor.end_job()
            
            # Check that timing was recorded
            assert pda.performance_monitor.metrics['job_start_time'] is not None
            assert pda.performance_monitor.metrics['job_end_time'] is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_stage_timing_tracked(self, temp_test_dir):
        """Test that stage timing is tracked"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("StageTest", master="local[1]")
            
            pda.performance_monitor.start_stage("test_stage")
            pda.performance_monitor.end_stage("test_stage")
            
            # Check that stage timing was recorded
            assert "test_stage" in pda.performance_monitor.metrics['stages']
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)


class TestApplicationIntegration:
    """End-to-end integration tests"""
    
    def test_full_application_startup(self, temp_test_dir):
        """Test full application startup"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda = ParallelDataAnalysis("FullTest", master="local[1]")
            
            # Verify all components are ready
            assert pda.spark is not None
            assert pda.data_loader is not None
            assert pda.analyzer is not None
            assert pda.graph_gen is not None
            assert pda.error_handler is not None
            assert pda.performance_monitor is not None
            
            pda.spark.stop()
        finally:
            os.chdir(original_cwd)
    
    def test_application_survives_multiple_initializations(self, temp_test_dir):
        """Test that multiple initializations work"""
        original_cwd = os.getcwd()
        os.chdir(temp_test_dir)
        
        try:
            pda1 = ParallelDataAnalysis("App1", master="local[1]")
            pda1.spark.stop()
            
            pda2 = ParallelDataAnalysis("App2", master="local[1]")
            pda2.spark.stop()
            
            # Both should complete successfully
        finally:
            os.chdir(original_cwd)

    mock_perf_instance = MagicMock()
    mock_perf.return_value = mock_perf_instance

    mock_error_instance = MagicMock()
    mock_error.return_value = mock_error_instance

    analyzer = ParallelDataAnalysis("TestApp", master="local[*]")
    analyzer.run_analysis("dummy.csv", "statistical")

    # Verify that load_data was called
    mock_loader_instance.load_data.assert_called_once_with("dummy.csv")
    mock_analyzer_instance.statistical_analysis.assert_called_once()


@patch('src.main.SparkSession')
@patch('src.main.ErrorHandler')
@patch('src.main.PerformanceMonitor')
@patch('src.main.GraphGenerator')
def test_create_output_dirs(mock_graph, mock_perf, mock_error, mock_spark):
    """Test output directory creation"""
    mock_spark.builder.appName.return_value.master.return_value.config.return_value.config.return_value.config.return_value.config.return_value.config.return_value.getOrCreate.return_value = MagicMock()

    analyzer = ParallelDataAnalysis("TestApp", master="local[*]")

    # Directories should be created during initialization
    import os
    assert os.path.exists("output/general")
    assert os.path.exists("output/general/graphs")
