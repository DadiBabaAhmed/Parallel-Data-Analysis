"""
Advanced statistical analysis operations for parallel data processing
"""
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
import numpy as np

class StatisticalAnalysis:
    """Advanced statistical operations"""
    
    @staticmethod
    def descriptive_statistics(df, columns=None):
        """
        Compute comprehensive descriptive statistics
        
        Args:
            df: Spark DataFrame
            columns: List of columns to analyze (None for all numeric)
            
        Returns:
            Dictionary with detailed statistics
        """
        if columns is None:
            columns = [field.name for field in df.schema.fields 
                      if isinstance(field.dataType, (DoubleType,))]
        
        results = {}
        
        for col in columns:
            # Compute multiple statistics in one pass
            stats = df.select(
                F.count(col).alias('count'),
                F.sum(F.when(F.col(col).isNull(), 1).otherwise(0)).alias('null_count'),
                F.mean(col).alias('mean'),
                F.stddev(col).alias('stddev'),
                F.variance(col).alias('variance'),
                F.min(col).alias('min'),
                F.max(col).alias('max'),
                F.expr(f'percentile_approx({col}, 0.25)').alias('q1'),
                F.expr(f'percentile_approx({col}, 0.5)').alias('median'),
                F.expr(f'percentile_approx({col}, 0.75)').alias('q3'),
                F.skewness(col).alias('skewness'),
                F.kurtosis(col).alias('kurtosis')
            ).collect()[0].asDict()
            
            # Calculate IQR and outlier bounds
            iqr = stats.get('q3', None) - stats.get('q1', None) if stats.get('q3') is not None and stats.get('q1') is not None else None
            if iqr:
                stats['iqr'] = iqr
                stats['lower_fence'] = stats['q1'] - 1.5 * iqr
                stats['upper_fence'] = stats['q3'] + 1.5 * iqr
                
                # Count outliers
                outlier_count = df.filter(
                    (F.col(col) < stats['lower_fence']) | 
                    (F.col(col) > stats['upper_fence'])
                ).count()
                stats['outlier_count'] = outlier_count
                stats['outlier_percent'] = (outlier_count / stats['count'] * 100) if stats['count'] > 0 else 0
            
            # Calculate coefficient of variation
            if stats.get('mean') and stats.get('stddev'):
                stats['coefficient_of_variation'] = stats['stddev'] / stats['mean']
            
            results[col] = stats
        
        return results
    
    @staticmethod
    def correlation_matrix(df, columns=None, method='pearson'):
        """
        Calculate correlation matrix using parallel processing
        
        Args:
            df: Spark DataFrame
            columns: List of columns (None for all numeric)
            method: Correlation method ('pearson' or 'spearman')
            
        Returns:
            Correlation matrix as dictionary
        """
        if columns is None:
            columns = [field.name for field in df.schema.fields 
                      if isinstance(field.dataType, (DoubleType,))]
        
        # Use Spark's built-in correlation for large datasets
        correlation_matrix = {}
        
        for col1 in columns:
            correlation_matrix[col1] = {}
            for col2 in columns:
                if col1 == col2:
                    correlation_matrix[col1][col2] = 1.0
                else:
                    corr = df.stat.corr(col1, col2)
                    correlation_matrix[col1][col2] = corr
        
        return correlation_matrix
    
    @staticmethod
    def covariance_matrix(df, columns=None):
        """
        Calculate covariance matrix
        
        Args:
            df: Spark DataFrame
            columns: List of columns
            
        Returns:
            Covariance matrix
        """
        if columns is None:
            columns = [field.name for field in df.schema.fields 
                      if isinstance(field.dataType, (DoubleType,))]
        
        covariance_matrix = {}
        
        for col1 in columns:
            covariance_matrix[col1] = {}
            for col2 in columns:
                cov = df.stat.cov(col1, col2)
                covariance_matrix[col1][col2] = cov
        
        return covariance_matrix
    
    @staticmethod
    def hypothesis_testing(df, column, hypothesized_mean=0, confidence=0.95):
        """
        Perform one-sample t-test
        
        Args:
            df: Spark DataFrame
            column: Column to test
            hypothesized_mean: Hypothesized population mean
            confidence: Confidence level
            
        Returns:
            Test results
        """
        from scipy import stats as scipy_stats
        
        # Collect sample data (use for smaller datasets)
        sample_data = df.select(column).toPandas()[column].dropna()
        
        # Perform t-test
        t_statistic, p_value = scipy_stats.ttest_1samp(sample_data, hypothesized_mean)
        
        # Calculate confidence interval
        mean = sample_data.mean()
        std_error = sample_data.std() / np.sqrt(len(sample_data))
        margin_of_error = scipy_stats.t.ppf((1 + confidence) / 2, len(sample_data) - 1) * std_error
        
        return {
            'column': column,
            'sample_mean': mean,
            'hypothesized_mean': hypothesized_mean,
            't_statistic': t_statistic,
            'p_value': p_value,
            'confidence_level': confidence,
            'confidence_interval': (mean - margin_of_error, mean + margin_of_error),
            'significant': p_value < (1 - confidence)
        }
    
    @staticmethod
    def frequency_distribution(df, column, bins=10):
        """
        Calculate frequency distribution
        
        Args:
            df: Spark DataFrame
            column: Column to analyze
            bins: Number of bins
            
        Returns:
            Frequency distribution
        """
        # Get min and max
        min_max = df.select(F.min(column), F.max(column)).collect()[0]
        min_val, max_val = min_max[0], min_max[1]
        
        # Calculate bin width
        bin_width = (max_val - min_val) / bins
        
        # Create bins and count
        bin_expr = F.floor((F.col(column) - min_val) / bin_width).cast('int')
        
        freq_dist = df.withColumn('bin', bin_expr) \
                     .groupBy('bin') \
                     .count() \
                     .orderBy('bin') \
                     .collect()
        
        # Format results
        results = []
        for row in freq_dist:
            bin_num = row['bin']
            bin_start = min_val + (bin_num * bin_width)
            bin_end = bin_start + bin_width
            results.append({
                'bin': bin_num,
                'range': f'[{bin_start:.2f}, {bin_end:.2f})',
                'frequency': row['count']
            })
        
        return results
    
    @staticmethod
    def detect_anomalies(df, column, method='zscore', threshold=3):
        """
        Detect anomalies/outliers
        
        Args:
            df: Spark DataFrame
            column: Column to analyze
            method: Detection method ('zscore', 'iqr', 'isolation')
            threshold: Threshold for detection
            
        Returns:
            DataFrame with anomaly flag
        """
        if method == 'zscore':
            # Z-score method
            stats = df.select(
                F.mean(column).alias('mean'),
                F.stddev(column).alias('stddev')
            ).collect()[0]
            
            mean, stddev = stats['mean'], stats['stddev']
            
            result_df = df.withColumn(
                'z_score',
                F.abs((F.col(column) - mean) / stddev)
            ).withColumn(
                'is_anomaly',
                F.col('z_score') > threshold
            )
            
        elif method == 'iqr':
            # IQR method
            quartiles = df.select(
                F.expr(f'percentile_approx({column}, 0.25)').alias('q1'),
                F.expr(f'percentile_approx({column}, 0.75)').alias('q3')
            ).collect()[0]
            
            q1, q3 = quartiles['q1'], quartiles['q3']
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            result_df = df.withColumn(
                'is_anomaly',
                (F.col(column) < lower_bound) | (F.col(column) > upper_bound)
            )
        
        return result_df
    
    @staticmethod
    def time_series_decomposition(df, time_col, value_col, period=24):
        """
        Simple time series decomposition (trend + seasonality)
        
        Args:
            df: Spark DataFrame
            time_col: Time column
            value_col: Value column
            period: Seasonal period
            
        Returns:
            DataFrame with decomposition components
        """
        from pyspark.sql.window import Window
        
        # Sort by time
        df = df.orderBy(time_col)
        
        # Calculate trend using moving average
        window_spec = Window.orderBy(time_col).rowsBetween(-period//2, period//2)
        
        df = df.withColumn('trend', F.avg(value_col).over(window_spec))
        
        # Calculate detrended values
        df = df.withColumn('detrended', F.col(value_col) - F.col('trend'))
        
        # Calculate seasonal component (average by period position)
        window_seasonal = Window.partitionBy(
            F.expr(f'row_number() OVER (ORDER BY {time_col}) % {period}')
        )
        
        df = df.withColumn('seasonal', F.avg('detrended').over(window_seasonal))
        
        # Calculate residual
        df = df.withColumn('residual', F.col('detrended') - F.col('seasonal'))
        
        return df
    
    @staticmethod
    def sampling_strategies(df, method='random', fraction=0.1, seed=42):
        """
        Apply various sampling strategies
        
        Args:
            df: Spark DataFrame
            method: Sampling method ('random', 'stratified', 'systematic')
            fraction: Sample fraction
            seed: Random seed
            
        Returns:
            Sampled DataFrame
        """
        if method == 'random':
            return df.sample(withReplacement=False, fraction=fraction, seed=seed)
        
        elif method == 'stratified':
            # Stratified sampling (requires a categorical column)
            # Example: sample proportionally from each group
            categorical_col = [field.name for field in df.schema.fields 
                             if isinstance(field.dataType, StringType)][0]
            
            fractions = df.select(categorical_col).distinct() \
                         .rdd.map(lambda x: (x[0], fraction)).collectAsMap()
            
            return df.sampleBy(categorical_col, fractions, seed)
        
        elif method == 'systematic':
            # Systematic sampling: every nth record
            n = int(1 / fraction)
            return df.filter(F.expr(f'monotonically_increasing_id() % {n} = 0'))


# Import required types
from pyspark.sql.types import FloatType, IntegerType, LongType, StringType
