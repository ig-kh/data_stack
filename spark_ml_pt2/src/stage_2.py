from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from argparse import ArgumentParser
from pyspark.sql import types as T
from pyspark.sql import functions as F


@F.udf(returnType=T.IntegerType())  # AGE attribute
def normalize_age(age_str: str):
    return int(age_str.replace(" ", "").replace("-", "").replace("_", ""))


@F.udf(returnType=T.LongType())  # ANNUAL_INCOME attribute
def normalize_money(amount_str: str):
    return float(amount_str.replace(" ", "").replace("-", "").replace("_", ""))


def YM2M_parse_transform(df, col):  # CREDIT_HISTORY_AGE attribute
    df = df.withColumn(
        f"{col}_Y",
        F.regexp_extract_all("col", F.lit(r"(\d+) Years\s*and\s*(\d+) Months"), 1),
    )
    df = df.withColumn(
        f"{col}_M",
        F.regexp_extract_all("col", F.lit(r"(\d+) Years\s*and\s*(\d+) Months"), 2),
    )
    df = df.withColumn(
        f"{col}_transformed",
        F.when(F.col(f"{col}_Y") != "").otherwise(0) * 12
        + F.when(F.col(f"{col}_M") != "").otherwise(0),
    )
    return df.drop(col, f"{col}_Y", f"{col}_M")


def reconstruct_by_group_mode(df, damaged_col, reference_col):
    

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
