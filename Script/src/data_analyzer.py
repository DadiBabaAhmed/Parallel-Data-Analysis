"""
Data analyzer with parallel algorithms for statistical analysis and aggregation
"""
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import numpy as np

class DataAnalyzer:
    def __init__(self, spark, error_handler):
        self.spark = spark
        self.error_handler = error_handler
    
    def statistical_analysis(self, df):
        """
        Perform comprehensive statistical analysis
        
        Args:
            df: Spark DataFrame
            
        Returns:
            Dictionary with statistical results
        """
        try:
            numeric_cols = [field.name for field in df.schema.fields 
                          if isinstance(field.dataType, (IntegerType, DoubleType, 
                                                        FloatType, LongType))]
            
            if not numeric_cols:
                return {"message": "No numeric columns found for statistical analysis"}
            
            results = {}
            
            # Basic statistics
            results['summary'] = df.select(numeric_cols).describe().toPandas().to_dict()
            
            # Advanced statistics for each numeric column
            for col in numeric_cols:
                col_stats = self._column_statistics(df, col)
                results[col] = col_stats
            
            return results
            
        except Exception as e:
            self.error_handler.log_error("Statistical Analysis", str(e))
            raise
    
    def _column_statistics(self, df, column):
        """Calculate detailed statistics for a column"""
        stats = df.select(
            F.mean(column).alias('mean'),
            F.stddev(column).alias('stddev'),
            F.min(column).alias('min'),
            F.max(column).alias('max'),
            F.expr(f'percentile_approx({column}, 0.25)').alias('q1'),
            F.expr(f'percentile_approx({column}, 0.5)').alias('median'),
            F.expr(f'percentile_approx({column}, 0.75)').alias('q3'),
            F.count(column).alias('count'),
            F.sum(F.when(F.col(column).isNull(), 1).otherwise(0)).alias('null_count')
        ).collect()[0]
        
        return stats.asDict()
    
    def aggregate_data(self, df, group_cols=None, agg_cols=None):
        """
        Perform parallel data aggregation
        
        Args:
            df: Spark DataFrame
            group_cols: Columns to group by (if None, uses first categorical column)
            agg_cols: Columns to aggregate (if None, uses all numeric columns)
            
        Returns:
            Aggregated results
        """
        try:
            # Auto-detect group and aggregation columns if not specified
            if group_cols is None:
                categorical_cols = [field.name for field in df.schema.fields 
                                  if isinstance(field.dataType, StringType)]
                group_cols = categorical_cols[:1] if categorical_cols else []
            
            if agg_cols is None:
                numeric_cols = [field.name for field in df.schema.fields 
                              if isinstance(field.dataType, (IntegerType, DoubleType, 
                                                            FloatType, LongType))]
                agg_cols = numeric_cols
            
            if not group_cols or not agg_cols:
                return {"message": "No suitable columns for aggregation"}
            
            # Perform multiple aggregations
            agg_expressions = []
            for col in agg_cols:
                agg_expressions.extend([
                    F.sum(col).alias(f'{col}_sum'),
                    F.avg(col).alias(f'{col}_avg'),
                    F.min(col).alias(f'{col}_min'),
                    F.max(col).alias(f'{col}_max'),
                    F.count(col).alias(f'{col}_count')
                ])
            
            aggregated_df = df.groupBy(group_cols).agg(*agg_expressions)

            # Persist aggregated results to output (Spark) to avoid collecting very large results
            timestamp = getattr(self.error_handler, 'timestamp', None) or ''
            output_dir = f"output/general/aggregation_{timestamp}_spark"
            try:
                aggregated_df.write.mode('overwrite').option('header', 'true').csv(output_dir)
            except Exception:
                try:
                    aggregated_df.coalesce(1).write.mode('overwrite').option('header', 'true').csv(output_dir)
                except Exception as e:
                    self.error_handler.log_warning('AggregateData', f'Could not write aggregated Spark CSV: {e}')

            # Convert to a safe-sized dict for return (limit if very large)
            try:
                row_count = aggregated_df.count()
                if row_count <= 5000:
                    pandas_df = aggregated_df.toPandas()
                    truncated = False
                else:
                    pandas_df = aggregated_df.limit(500).toPandas()
                    truncated = True

                data_dict = pandas_df.to_dict()
            except Exception as e:
                self.error_handler.log_warning('AggregateData', f'Could not convert aggregated results to pandas: {e}')
                data_dict = {}
                truncated = True

            return {
                'data': data_dict,
                'group_by': group_cols,
                'aggregated_columns': agg_cols,
                'row_count': int(row_count) if 'row_count' in locals() else None,
                'truncated': bool(truncated)
            }
            
        except Exception as e:
            self.error_handler.log_error("Data Aggregation", str(e))
            raise
    
    def correlation_analysis(self, df):
        """
        Calculate correlation matrix for numeric columns
        
        Args:
            df: Spark DataFrame
            
        Returns:
            Correlation matrix
        """
        try:
            numeric_cols = [field.name for field in df.schema.fields 
                          if isinstance(field.dataType, (IntegerType, DoubleType, 
                                                        FloatType, LongType))]
            
            if len(numeric_cols) < 2:
                return {"message": "Need at least 2 numeric columns for correlation"}
            
            # Prefer pandas correlation for small datasets; for large datasets compute pairwise via Spark
            total_count = df.count()
            if total_count <= 50000 and len(numeric_cols) <= 20:
                pandas_df = df.select(numeric_cols).toPandas()
                correlation_matrix = pandas_df.corr()
                return {
                    'matrix': correlation_matrix.to_dict(),
                    'columns': numeric_cols,
                    'method': 'pandas',
                    'row_count': int(total_count)
                }
            else:
                # Compute pairwise correlations using Spark's stat.corr (may be slower but avoids collecting full dataframe)
                matrix = {c: {} for c in numeric_cols}
                for i, c1 in enumerate(numeric_cols):
                    for j, c2 in enumerate(numeric_cols):
                        if j < i:
                            # mirror
                            matrix[c1][c2] = matrix[c2].get(c1)
                        elif i == j:
                            matrix[c1][c2] = 1.0
                        else:
                            try:
                                corr_val = df.stat.corr(c1, c2)
                            except Exception:
                                corr_val = None
                            matrix[c1][c2] = corr_val

                return {
                    'matrix': matrix,
                    'columns': numeric_cols,
                    'method': 'spark_pairwise',
                    'row_count': int(total_count)
                }
            
        except Exception as e:
            self.error_handler.log_error("Correlation Analysis", str(e))
            raise
    
    def mapreduce_operation(self, df, map_func, reduce_func, column):
        """
        Generic MapReduce operation
        
        Args:
            df: Spark DataFrame
            map_func: Map function to apply
            reduce_func: Reduce function (e.g., sum, count)
            column: Column to operate on
            
        Returns:
            Result of MapReduce
        """
        try:
            # Map phase
            rdd = df.select(column).rdd.map(lambda row: map_func(row[0]))
            
            # Reduce phase
            if reduce_func == 'sum':
                result = rdd.reduce(lambda a, b: a + b)
            elif reduce_func == 'count':
                result = rdd.count()
            elif reduce_func == 'max':
                result = rdd.reduce(lambda a, b: max(a, b))
            elif reduce_func == 'min':
                result = rdd.reduce(lambda a, b: min(a, b))
            else:
                result = rdd.reduce(reduce_func)
            
            return result
            
        except Exception as e:
            self.error_handler.log_error("MapReduce Operation", str(e))
            raise
    
    def window_analysis(self, df, partition_col, order_col, window_func='rank'):
        """
        Perform window function analysis
        
        Args:
            df: Spark DataFrame
            partition_col: Column to partition by
            order_col: Column to order by
            window_func: Window function to apply
            
        Returns:
            DataFrame with window analysis
        """
        try:
            window_spec = Window.partitionBy(partition_col).orderBy(F.desc(order_col))
            
            if window_func == 'rank':
                result_df = df.withColumn('rank', F.rank().over(window_spec))
            elif window_func == 'row_number':
                result_df = df.withColumn('row_num', F.row_number().over(window_spec))
            elif window_func == 'cumsum':
                result_df = df.withColumn('cumsum', 
                                         F.sum(order_col).over(window_spec))
            else:
                raise ValueError(f"Unsupported window function: {window_func}")
            
            # Return a safe-sized preview
            try:
                total = result_df.count()
                if total > 5000:
                    preview = result_df.limit(500).toPandas().to_dict()
                else:
                    preview = result_df.toPandas().to_dict()
            except Exception:
                preview = {}

            return preview
            
        except Exception as e:
            self.error_handler.log_error("Window Analysis", str(e))
            raise


# Import required types
from pyspark.sql.types import IntegerType, DoubleType, FloatType, LongType, StringType
