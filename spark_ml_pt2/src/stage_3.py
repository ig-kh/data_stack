from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from argparse import ArgumentParser
from pyspark.sql import types as T
from pyspark.sql import functions as F


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--src")
    parser.add_argument("--dst")
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("silverToGold")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    silver_df = spark.read.format("delta").load(args.src)

    print(
        "\033[0;32m[◝(ᵔᗜᵔ)◜]\033[0m ML-ready aggregated features are now available at \033[1;33mGOLD\033[0m layer!"
    )

    spark.stop()