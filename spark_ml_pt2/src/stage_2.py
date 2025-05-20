from pyspark.sql import SparkSession, Window
from delta.tables import DeltaTable
from argparse import ArgumentParser
from pyspark.sql import types as T
from pyspark.sql import functions as F


@F.udf(returnType=T.IntegerType())  # AGE, NUM_OF_DELAYED_PAYMENT attributes
def normalize_int(int_str: str, allow_neg=False):
    int_str = int_str.replace(" ", "").replace("_", "")
    if not allow_neg:
        int_str = int_str.replace("-", "")
    return float(int_str)


@F.udf(returnType=T.LongType())  # MONTHLY_INHAND_SALARY, ANNUAL_INCOME attributes
def normalize_float(float_str: str, allow_neg=False):
    float_str = float_str.replace(" ", "").replace("_", "")
    if not allow_neg:
        float_str = float_str.replace("-", "")
    return float(float_str)


def YM2M_parse_transform(
    df, col, regexp=r"(\d+) Years\s*and\s*(\d+) Months", ypos=1, mpos=2
):  # CREDIT_HISTORY_AGE attribute
    df = df.withColumn(
        f"{col}_Y",
        F.regexp_extract_all("col", F.lit(regexp), ypos),
    )
    df = df.withColumn(
        f"{col}_M",
        F.regexp_extract_all("col", F.lit(regexp), mpos),
    )
    df = df.withColumn(
        f"{col}_months",
        F.when(F.col(f"{col}_Y") != "").otherwise(0) * 12
        + F.when(F.col(f"{col}_M") != "").otherwise(0),
    )
    return df.drop(col, f"{col}_Y", f"{col}_M")


def group_bf_fill(
    df, damaged_col, grouping_col, sort_col
):  # NUM_OF_DELAYED_PAYMENT attribute
    """backward-forward fill for nulls based on sharing data values inside group"""
    ffill_w = Window.partitionBy(grouping_col).orderBy(sort_col)
    bfill_w = ffill_w.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
    return df.withColumn(
        f"{damaged_col}_imputed",
        F.coalesce(
            F.last(damaged_col, True).over(ffill_w),
            F.first(damaged_col, True).over(bfill_w),
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

    bronze_df = spark.read.format("delta").load(args.src)

    bronze_df = bronze_df.na.drop(subset=[])

    delta_table = DeltaTable.forPath(spark, args.dst)
    spark.sql(
        f"""
    OPTIMIZE delta.`{args.dst}`
    ZORDER BY ()
    """
    )
    delta_table.optimize().executeCompaction()

    print(
        "\033[0;32m[三ᕕ( ᐛ )ᕗ]\033[0m Cleared data with proper typing saved as Z-ordered Delta table at \033[1;30mSILVER\033[0m layer"
    )

    spark.stop()
