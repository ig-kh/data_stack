from pyspark.sql import SparkSession
from argparse import ArgumentParser

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--src")
    parser.add_argument("--dst")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("rawToBronze") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel('ERROR')

    df_raw = spark.read.csv(args.src, header=True, inferSchema=True)

    df_raw.write.format("delta").mode("overwrite").save(args.dst)

    print("\033[0;32m[ᕕ( ᐛ )ᕗ]\033[0m Data saved as Delta table at \033[1;31mBRONZE\033[0m layer")

    spark.stop()