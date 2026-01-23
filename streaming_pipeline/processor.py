from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class RealTimeProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("AnomaLens") \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .getOrCreate()
        
    def create_schema(self):
        return StructType([
            StructField("sensor_id", StringType()),
            StructField("timestamp", TimestampType()),
            StructField("temperature", DoubleType()),
            StructField("pressure", DoubleType()),
            StructField("humidity", DoubleType()),
            StructField("vibration", DoubleType()),
            StructField("status", StringType())
        ])
    
    def read_from_kafka(self, topic="iot_sensors"):
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", topic) \
            .load()
        
        return df.select(
            from_json(col("value").cast("string"), self.create_schema()).alias("data")
        ).select("data.*")