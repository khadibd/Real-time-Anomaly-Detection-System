from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class SparkStreamProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("AnomaLensStreaming") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .getOrCreate()
        
        self.schema = StructType([
            StructField("sensor_id", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("temperature", DoubleType()),
            StructField("pressure", DoubleType()),
            StructField("humidity", DoubleType()),
            StructField("vibration", DoubleType()),
            StructField("status", StringType())
        ])
    
    def start_streaming(self):
        # Read from Kafka
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "iot_sensors") \
            .load()
        
        # Parse JSON data
        parsed_df = df.select(
            from_json(col("value").cast("string"), self.schema).alias("data")
        ).select("data.*")
        
        # Apply anomaly detection (simple threshold-based)
        processed_df = parsed_df.withColumn(
            "is_anomaly",
            when(col("temperature") > 35, 1).otherwise(0)
        )
        
        # Write to console (or database/file)
        query = processed_df \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", "false") \
            .start()
        
        query.awaitTermination()