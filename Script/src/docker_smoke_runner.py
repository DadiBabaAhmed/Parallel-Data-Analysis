"""Minimal PySpark-based smoke runner to execute inside the container.

This script uses only pyspark (bundled with Spark in the image) and the
standard library. It loads a CSV and runs a simple aggregation and a
word-count-like example using Spark SQL/functions.
"""
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main(input_path: str):
    spark = SparkSession.builder.appName('DockerSmokeRunner').getOrCreate()

    print('Reading CSV:', input_path)
    df = spark.read.option('header', 'true').option('inferSchema', 'true').csv(input_path)
    print('Schema:')
    df.printSchema()

    print('Counting rows...')
    print(df.count())

    # Example aggregation: total sales by region (if sales_amount exists)
    if 'sales_amount' in df.columns:
        df = df.withColumn('sales_amount', F.col('sales_amount').cast('double'))
        agg = df.groupBy('region').agg(
            F.sum('sales_amount').alias('total_sales'),
            F.count('*').alias('count')
        ).orderBy(F.desc('total_sales'))

        print('Top regions by sales:')
        agg.show(10, truncate=False)

    # Word count example on `product_name` if present
    if 'product_name' in df.columns:
        words = df.select(F.explode(F.split(F.col('product_name'), '\\s+')).alias('word'))
        words = words.filter(F.length('word') > 0).withColumn('word', F.lower(F.col('word')))
        wc = words.groupBy('word').count().orderBy(F.desc('count'))
        print('Sample word counts (product_name):')
        wc.show(10, truncate=False)

    spark.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python docker_smoke_runner.py <input_csv_path>')
        sys.exit(2)
    main(sys.argv[1])
