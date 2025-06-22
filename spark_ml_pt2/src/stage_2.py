from pyspark.sql import SparkSession, Window
from delta.tables import DeltaTable
from argparse import ArgumentParser
from pyspark.sql import types as T
from pyspark.sql import functions as F


@F.udf(returnType=T.IntegerType())  # AGE, NUM_OF_DELAYED_PAYMENT attributes
def normalize_int(int_str: str, allow_neg=False):
    if not isinstance(int_str, str):
        return 0
    int_str = int_str.replace(" ", "").replace("_", "")
    if not allow_neg:
        int_str = int_str.replace("-", "")
    return int(float(int_str))  # Convert to float first to handle decimals, then to int


@F.udf(returnType=T.DoubleType())  # MONTHLY_INHAND_SALARY, ANNUAL_INCOME attributes
def normalize_float(float_str: str, allow_neg=False):
    if not isinstance(float_str, str):
        return 0.
    float_str = float_str.replace(" ", "").replace("_", "")
    if not allow_neg:
        float_str = float_str.replace("-", "")
    return float(float_str)


def YM2M_parse_transform(
    df, col, regexp=r"(\d+) Years\s*and\s*(\d+) Months", ypos=1, mpos=2
):  # CREDIT_HISTORY_AGE attribute
    df = df.withColumn(
        f"{col}_Y",
        F.regexp_extract(F.col(col), regexp, ypos).cast(T.IntegerType()),
    )
    df = df.withColumn(
        f"{col}_M",
        F.regexp_extract(F.col(col), regexp, mpos).cast(T.IntegerType()),
    )
    df = df.withColumn(
        f"{col}_months",
        (F.when(F.col(f"{col}_Y").isNotNull(), F.col(f"{col}_Y")).otherwise(0) * 12)
        + F.when(F.col(f"{col}_M").isNotNull(), F.col(f"{col}_M")).otherwise(0),
    )
    return df.drop(col, f"{col}_Y", f"{col}_M")


def group_bf_fill(
    df, damaged_col, grouping_col, sort_col
):  # NUM_OF_DELAYED_PAYMENT attribute
    """Backward-forward fill for nulls based on sharing data values inside group"""
    ffill_w = Window.partitionBy(grouping_col).orderBy(sort_col)
    bfill_w = ffill_w.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
    return df.withColumn(
        f"{damaged_col}_imputed",
        F.coalesce(
            F.last(damaged_col, ignorenulls=True).over(ffill_w),
            F.first(damaged_col, ignorenulls=True).over(bfill_w),
        ),
    ).drop(damaged_col)


USE_COLS = [
    "id",
    "customer_id",
    "month",
    "age",
    "annual_income",
    "credit_history_age",
    "monthly_inhand_salary",
    "num_of_delayed_payment",
    "credit_utilization_ratio",
    "credit_score",
]

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--src")
    parser.add_argument("--dst")
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("bronzeToSilver")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    # Load and select columns
    bronze_df = spark.read.format("delta").load(args.src).select(USE_COLS)

    # Parse integer columns
    bronze_df = bronze_df.withColumn("age", normalize_int(F.col("age")))
    bronze_df = bronze_df.withColumn("num_of_delayed_payment", normalize_int(F.col("num_of_delayed_payment")))

    # Parse float columns
    bronze_df = bronze_df.withColumn("annual_income", normalize_float(F.col("annual_income")))
    bronze_df = bronze_df.withColumn("monthly_inhand_salary", normalize_float(F.col("monthly_inhand_salary")))

    # Parse credit history age
    bronze_df = YM2M_parse_transform(bronze_df, "credit_history_age")

    # Impute num_of_delayed_payment
    bronze_df = group_bf_fill(bronze_df, "num_of_delayed_payment", "customer_id", "month")

    # Drop rows with remaining nulls
    silver_cols = [
        "id",
        "customer_id",
        "month",
        "age",
        "annual_income",
        "credit_history_age_months",
        "monthly_inhand_salary",
        "num_of_delayed_payment_imputed",
        "credit_utilization_ratio",
        "credit_score",
    ]
    bronze_df = bronze_df.dropna(subset=silver_cols)

    # Write to silver layer
    bronze_df.write.format("delta").mode("overwrite").save(args.dst)

    try:
        delta_table = DeltaTable.forPath(spark, args.dst)
        # Optimize with Z-order
        delta_table.optimize().executeZOrderBy("id")
        # Compact table
        delta_table.optimize().executeCompaction()
        print("\033[0;32m[三ᕕ( ᐛ )ᕗ]\033[0m Cleared data with proper typing saved as Z-ordered Delta table at \033[1;30mSILVER\033[0m layer")
        spark.stop()
    except Exception as e:
        print(f"Failed to optimize Delta table: {str(e)}")
        spark.stop()
        exit(1)
