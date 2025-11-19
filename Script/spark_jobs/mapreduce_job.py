"""
MapReduce job implementations for parallel data processing
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

class MapReduceJob:
    """MapReduce operations for parallel data analysis"""
    
    @staticmethod
    def word_count(df, text_column):
        """
        Word count MapReduce operation
        
        Args:
            df: Spark DataFrame
            text_column: Column containing text
            
        Returns:
            DataFrame with word counts
        """
        # Map: Split text into words
        words_df = df.select(
            F.explode(F.split(F.col(text_column), r'\s+')).alias('word')
        )
        
        # Clean and filter
        words_df = words_df.filter(F.length('word') > 0)
        words_df = words_df.withColumn('word', F.lower(F.col('word')))
        
        # Reduce: Count occurrences
        word_counts = words_df.groupBy('word').count()
        word_counts = word_counts.orderBy(F.desc('count'))
        
        return word_counts
    
    @staticmethod
    def group_sum(df, group_column, sum_column):
        """
        Group and sum MapReduce operation
        
        Args:
            df: Spark DataFrame
            group_column: Column to group by
            sum_column: Column to sum
            
        Returns:
            DataFrame with grouped sums
        """
        # Map: Extract key-value pairs
        mapped_df = df.select(group_column, sum_column)
        
        # Reduce: Sum by group
        result = mapped_df.groupBy(group_column).agg(
            F.sum(sum_column).alias(f'total_{sum_column}'),
            F.count('*').alias('count')
        )
        
        return result.orderBy(F.desc(f'total_{sum_column}'))
    
    @staticmethod
    def distinct_count(df, column):
        """
        Count distinct values using MapReduce
        
        Args:
            df: Spark DataFrame
            column: Column to count distinct values
            
        Returns:
            Count of distinct values
        """
        # Map: Get distinct values
        distinct_values = df.select(column).distinct()
        
        # Reduce: Count
        count = distinct_values.count()
        
        return count
    
    @staticmethod
    def top_n_by_group(df, group_column, value_column, n=10):
        """
        Get top N records by group
        
        Args:
            df: Spark DataFrame
            group_column: Column to group by
            value_column: Column to rank by
            n: Number of top records to return
            
        Returns:
            DataFrame with top N records per group
        """
        from pyspark.sql.window import Window
        
        # Define window
        window = Window.partitionBy(group_column).orderBy(F.desc(value_column))
        
        # Map: Add rank
        ranked_df = df.withColumn('rank', F.row_number().over(window))
        
        # Reduce: Filter top N
        top_n_df = ranked_df.filter(F.col('rank') <= n)
        
        return top_n_df.drop('rank')
    
    @staticmethod
    def moving_average(df, partition_column, order_column, 
                      value_column, window_size=3):
        """
        Calculate moving average using window functions
        
        Args:
            df: Spark DataFrame
            partition_column: Column to partition by
            order_column: Column to order by
            value_column: Column to calculate average
            window_size: Size of the moving window
            
        Returns:
            DataFrame with moving average
        """
        from pyspark.sql.window import Window
        
        # Define window
        window = Window.partitionBy(partition_column) \
                      .orderBy(order_column) \
                      .rowsBetween(-(window_size-1), 0)
        
        # Calculate moving average
        result_df = df.withColumn(
            f'moving_avg_{value_column}',
            F.avg(value_column).over(window)
        )
        
        return result_df
    
    @staticmethod
    def custom_mapreduce(spark_context, data, map_func, reduce_func):
        """
        Generic custom MapReduce operation
        
        Args:
            spark_context: Spark context
            data: Input data (list or RDD)
            map_func: Custom map function
            reduce_func: Custom reduce function
            
        Returns:
            Result of MapReduce operation
        """
        # Create RDD if input is list
        if isinstance(data, list):
            rdd = spark_context.parallelize(data)
        else:
            rdd = data
        
        # Map phase
        mapped_rdd = rdd.map(map_func)
        
        # Reduce phase
        result = mapped_rdd.reduce(reduce_func)
        
        return result


# Example usage functions
def example_word_count(spark, input_path):
    """Example: Word count on text data"""
    df = spark.read.text(input_path)
    job = MapReduceJob()
    result = job.word_count(df, 'value')
    return result


def example_sales_analysis(spark, sales_df):
    """Example: Sales analysis using MapReduce"""
    job = MapReduceJob()
    
    # Total sales by product
    product_sales = job.group_sum(sales_df, 'product', 'amount')
    
    # Top 10 customers
    top_customers = job.top_n_by_group(
        sales_df, 'region', 'amount', n=10
    )
    
    return {
        'product_sales': product_sales,
        'top_customers': top_customers
    }
