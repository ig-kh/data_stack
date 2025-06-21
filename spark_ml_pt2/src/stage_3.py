from pyspark.sql import SparkSession, Window
from delta.tables import DeltaTable
from argparse import ArgumentParser
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

    # Load silver layer data
    silver_df = spark.read.format("delta").load(args.src)

    # Define window to get the latest record per customer
    window_spec = Window.partitionBy("customer_id").orderBy(F.col("month").desc())

    # Add row number to identify the latest record
    silver_df = silver_df.withColumn("rn", F.row_number().over(window_spec))

    # Select the latest record for each customer
    gold_df = silver_df.filter(F.col("rn") == 1).drop("rn")

    # Select ML-ready features
    ml_features = [
        "customer_id",
        "age",
        "annual_income",
        "credit_history_age_months",
        "monthly_inhand_salary",
        "num_of_delayed_payment_imputed",
        "credit_utilization_ratio",
        "credit_score",
    ]
    gold_df = gold_df.select(ml_features)

    # Write to gold layer
    gold_df.write.format("delta").mode("overwrite").save(args.dst)

    try:
        delta_table = DeltaTable.forPath(spark, args.dst)
        # Optimize with Z-order
        delta_table.optimize().executeZOrderBy("customer_id")
        # Compact table
        delta_table.optimize().executeCompaction()
        print("\033[0;32m[◝(ᵔᗜᵔ)◜]\033[0m ML-ready aggregated features are now available at \033[1;33mGOLD\033[0m layer!")
    except Exception as e:
        print(f"Failed to optimize Delta table: {str(e)}")
        spark.stop()
        exit(1)
