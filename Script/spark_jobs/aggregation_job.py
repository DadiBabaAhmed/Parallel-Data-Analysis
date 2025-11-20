"""
Advanced aggregation operations for parallel data analysis
"""
from pyspark.sql import functions as F
from pyspark.sql.window import Window

class AggregationJob:
    """Advanced aggregation operations"""
    
    @staticmethod
    def multi_level_aggregation(df, group_cols, agg_cols):
        """
        Perform multi-level aggregation
        
        Args:
            df: Spark DataFrame
            group_cols: List of columns to group by
            agg_cols: List of columns to aggregate
            
        Returns:
            Aggregated DataFrame
        """
        agg_exprs = []
        
        for col in agg_cols:
            agg_exprs.extend([
                F.sum(col).alias(f'{col}_sum'),
                F.avg(col).alias(f'{col}_avg'),
                F.min(col).alias(f'{col}_min'),
                F.max(col).alias(f'{col}_max'),
                F.stddev(col).alias(f'{col}_stddev'),
                F.count(col).alias(f'{col}_count')
            ])
        
        result = df.groupBy(group_cols).agg(*agg_exprs)
        return result
    
    @staticmethod
    def cube_aggregation(df, dimensions, measures):
        """
        Perform CUBE aggregation (all combinations of dimensions)
        
        Args:
            df: Spark DataFrame
            dimensions: List of dimension columns
            measures: Dictionary of measure columns and aggregation functions
            
        Returns:
            Cubed aggregation result
        """
        agg_exprs = []
        for measure, agg_func in measures.items():
            if agg_func == 'sum':
                agg_exprs.append(F.sum(measure).alias(f'{measure}_sum'))
            elif agg_func == 'avg':
                agg_exprs.append(F.avg(measure).alias(f'{measure}_avg'))
            elif agg_func == 'count':
                agg_exprs.append(F.count(measure).alias(f'{measure}_count'))
        
        result = df.cube(*dimensions).agg(*agg_exprs)
        return result
    
    @staticmethod
    def rollup_aggregation(df, hierarchy_cols, measure_col):
        """
        Perform ROLLUP aggregation (hierarchical aggregation)
        
        Args:
            df: Spark DataFrame
            hierarchy_cols: List of columns in hierarchical order
            measure_col: Column to aggregate
            
        Returns:
            Rolled-up aggregation result
        """
        result = df.rollup(*hierarchy_cols).agg(
            F.sum(measure_col).alias(f'{measure_col}_sum'),
            F.avg(measure_col).alias(f'{measure_col}_avg'),
            F.count('*').alias('count')
        )
        
        return result
    
    @staticmethod
    def pivot_aggregation(df, index_col, pivot_col, value_col, agg_func='sum'):
        """
        Perform pivot aggregation
        
        Args:
            df: Spark DataFrame
            index_col: Column to use as index
            pivot_col: Column to pivot on
            value_col: Column with values to aggregate
            agg_func: Aggregation function
            
        Returns:
            Pivoted DataFrame
        """
        if agg_func == 'sum':
            result = df.groupBy(index_col).pivot(pivot_col).sum(value_col)
        elif agg_func == 'avg':
            result = df.groupBy(index_col).pivot(pivot_col).avg(value_col)
        elif agg_func == 'count':
            result = df.groupBy(index_col).pivot(pivot_col).count()
        else:
            result = df.groupBy(index_col).pivot(pivot_col).agg({value_col: agg_func})
        
        return result
    
    @staticmethod
    def time_series_aggregation(df, timestamp_col, value_col, 
                                interval='1 hour'):
        """
        Aggregate time series data by time interval
        
        Args:
            df: Spark DataFrame
            timestamp_col: Timestamp column
            value_col: Value column to aggregate
            interval: Time interval (e.g., '1 hour', '1 day')
            
        Returns:
            Time series aggregated DataFrame
        """
        # Ensure timestamp column is of timestamp type
        df = df.withColumn(timestamp_col, F.col(timestamp_col).cast('timestamp'))
        
        # Create time window
        result = df.groupBy(F.window(timestamp_col, interval)).agg(
            F.sum(value_col).alias(f'{value_col}_sum'),
            F.avg(value_col).alias(f'{value_col}_avg'),
            F.min(value_col).alias(f'{value_col}_min'),
            F.max(value_col).alias(f'{value_col}_max'),
            F.count('*').alias('count')
        )
        
        # Extract window start and end
        result = result.select(
            F.col('window.start').alias('period_start'),
            F.col('window.end').alias('period_end'),
            '*'
        ).drop('window')
        
        return result.orderBy('period_start')
    
    @staticmethod
    def percentile_aggregation(df, group_col, value_col, percentiles=None):
        """
        Calculate percentiles by group
        
        Args:
            df: Spark DataFrame
            group_col: Column to group by
            value_col: Column to calculate percentiles
            percentiles: List of percentiles (default: [0.25, 0.5, 0.75, 0.95])
            
        Returns:
            DataFrame with percentiles
        """
        if percentiles is None:
            percentiles = [0.25, 0.5, 0.75, 0.95]
        
        agg_exprs = [
            F.expr(f'percentile_approx({value_col}, {p})').alias(f'p{int(p*100)}')
            for p in percentiles
        ]
        
        result = df.groupBy(group_col).agg(*agg_exprs)
        return result
    
    @staticmethod
    def running_totals(df, partition_col, order_col, value_col):
        """
        Calculate running totals (cumulative sum)
        
        Args:
            df: Spark DataFrame
            partition_col: Column to partition by
            order_col: Column to order by
            value_col: Column to sum
            
        Returns:
            DataFrame with running totals
        """
        window = Window.partitionBy(partition_col) \
                      .orderBy(order_col) \
                      .rowsBetween(Window.unboundedPreceding, Window.currentRow)
        
        result = df.withColumn(
            f'{value_col}_running_total',
            F.sum(value_col).over(window)
        )
        
        return result
    
    @staticmethod
    def weighted_average(df, group_col, value_col, weight_col):
        """
        Calculate weighted average by group
        
        Args:
            df: Spark DataFrame
            group_col: Column to group by
            value_col: Value column
            weight_col: Weight column
            
        Returns:
            DataFrame with weighted averages
        """
        result = df.groupBy(group_col).agg(
            (F.sum(F.col(value_col) * F.col(weight_col)) / 
             F.sum(weight_col)).alias(f'{value_col}_weighted_avg'),
            F.sum(weight_col).alias('total_weight'),
            F.count('*').alias('count')
        )
        
        return result


# Example usage
def example_sales_aggregation(df):
    """Example: Complex sales aggregation"""
    job = AggregationJob()
    
    # Multi-level aggregation
    sales_summary = job.multi_level_aggregation(
        df,
        group_cols=['region', 'product_category'],
        agg_cols=['sales_amount', 'quantity']
    )
    
    # Pivot aggregation
    sales_pivot = job.pivot_aggregation(
        df,
        index_col='region',
        pivot_col='product_category',
        value_col='sales_amount',
        agg_func='sum'
    )
    
    return {
        'summary': sales_summary,
        'pivot': sales_pivot
    }
