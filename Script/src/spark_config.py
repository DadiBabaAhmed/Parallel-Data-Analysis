"""
Spark configuration settings
"""

SPARK_CONFIG = {
    # Core settings
    'app_name': 'ParallelDataAnalysis',
    'master': 'spark://spark-master:7077',  # Use for cluster mode
    # 'master': 'local[*]',  # Use for local testing
    
    # Memory settings
    'spark.executor.memory': '2g',
    'spark.driver.memory': '2g',
    'spark.executor.cores': '2',
    'spark.driver.cores': '2',
    
    # Performance tuning
    'spark.sql.adaptive.enabled': 'true',
    'spark.sql.adaptive.coalescePartitions.enabled': 'true',
    'spark.sql.adaptive.skewJoin.enabled': 'true',
    'spark.sql.shuffle.partitions': '200',
    
    # Serialization
    'spark.serializer': 'org.apache.spark.serializer.KryoSerializer',
    'spark.kryoserializer.buffer.max': '512m',
    
    # Fault tolerance
    'spark.task.maxFailures': '4',
    'spark.speculation': 'true',
    'spark.speculation.multiplier': '1.5',
    
    # UI and monitoring
    'spark.ui.enabled': 'true',
    'spark.eventLog.enabled': 'true',
    'spark.eventLog.dir': '/tmp/spark-events',
    
    # Network
    'spark.network.timeout': '600s',
    'spark.executor.heartbeatInterval': '60s',
    
    # Compression
    'spark.rdd.compress': 'true',
    'spark.io.compression.codec': 'snappy',
}

# Local mode configuration (for testing without cluster)
LOCAL_CONFIG = {
    'app_name': 'ParallelDataAnalysis_Local',
    'master': 'local[*]',
    'spark.sql.shuffle.partitions': '8',
    'spark.driver.memory': '4g',
}

# Cluster mode configuration (for production)
CLUSTER_CONFIG = {
    **SPARK_CONFIG,
    'spark.executor.instances': '3',
    'spark.dynamicAllocation.enabled': 'true',
    'spark.dynamicAllocation.minExecutors': '1',
    'spark.dynamicAllocation.maxExecutors': '10',
    'spark.dynamicAllocation.initialExecutors': '3',
}


def get_spark_config(mode='local'):
    """
    Get Spark configuration based on mode
    
    Args:
        mode: 'local' or 'cluster'
        
    Returns:
        Configuration dictionary
    """
    if mode == 'local':
        return LOCAL_CONFIG
    elif mode == 'cluster':
        return CLUSTER_CONFIG
    else:
        return SPARK_CONFIG
