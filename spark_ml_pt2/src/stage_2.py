from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from argparse import ArgumentParser
from pyspark.sql import functions as F

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--src")
    parser.add_argument("--dst")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("bronzeToSilver") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    bronze_df = spark.read.format("delta").load(args.src)
    


    delta_table = DeltaTable.forPath(spark, args.dst)
    spark.sql(f"""
    OPTIMIZE delta.`{args.dst}`
    ZORDER BY ()
    """)
    delta_table.optimize().executeCompaction()
    
    print("\033[0;32m[ᕕ( ᐛ )ᕗ]\033[0m Cleared data saved as Z-ordered Delta table at \033[1;30mSILVER\033[0m layer")

    spark.stop()