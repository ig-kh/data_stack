from argparse import ArgumentParser
from pyspark.sql import SparkSession
from pyspark import SparkContext

import time
import getpass

from pyspark import StorageLevel
import pyspark.ml as ML
import pyspark.sql.functions as F
import pyspark.sql.types as T


def iir_filter(x):

    alpha = 0.7

    x_ = x[0]
    x_filt = [x_]

    for x_i in x[1:]:
        x_filt.append(alpha * x_i + (1 - alpha) * x_)
        x_ = x_filt[-1]

    return x_filt


def make_session(app_name: str = None):

    if app_name is None:
        app_name = f"{getpass.getuser()}_spark_at_{time.time()}"

    if SparkContext._active_spark_context is not None:
        sc = SparkContext.getOrCreate()
        sc.stop()

    spark = SparkSession.builder.appName(app_name).getOrCreate()

    return spark


def get_executor_memory(sc, scale="MB"):
    executor_memory_status = sc._jsc.sc().getExecutorMemoryStatus()
    executor_memory_status_dict = (
        sc._jvm.scala.collection.JavaConverters.mapAsJavaMapConverter(
            executor_memory_status
        ).asJava()
    )
    total_used_memory = 0

    scales_dict = {"B": 1, "KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}

    for values in executor_memory_status_dict.values():
        used_memory = (values._1() - values._2()) / scales_dict[scale]
        total_used_memory += used_memory

    return total_used_memory


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument("--pth")
    parser.add_argument("--opt", action="store_true")
    parser.add_argument("--dbg", action="store_true")
    args = parser.parse_args()

    spark = make_session()
    sc = spark.sparkContext.getOrCreate()

    start_time = time.time()
    print("RAM", "INIT STAGE", get_executor_memory(sc), sep=";")

    if args.opt:

        spark.udf.registerJavaFunction(
            "iirf", "iirFilter", T.ArrayType(T.DoubleType())
        )  # iir-filter written in Scala @ .src/scala/iirf/src/main/scala/Main.scala, jar compiled @ .src/scala/iirf/target/scala-2.12/iirf-assembly-0.1.0-SNAPSHOT.jar
        # native to Pyspark eco-system, runs on JVM and does not produce additional VM's

    else:

        spark.udf.register(
            "iirf", iir_filter, T.ArrayType(T.DoubleType())
        )  # iir-filter written in Python @ the beginning of script
        # makes spark to create additional Python VM's on each executor wasting resources and enlarging time

    iirf_transform = lambda df, col, key_col: df.selectExpr(f"iirf({col})", key_col)

    ppg_df = spark.read.csv(args.pth, header=True, inferSchema=True)

    if args.dbg:
        print(ppg_df.schema)
        ppg_df.show()

    if args.opt:
        ppg_df = ppg_df.repartition(spark.sparkContext.defaultParallelism)

    ts_cols = [str(i) for i in range(0, 2000)]

    label_col = "Label"

    label_encoder = ML.feature.StringIndexer(
        inputCol=label_col, outputCol="label_encoded"
    ).fit(ppg_df)

    ppg_df = label_encoder.transform(ppg_df).drop(label_col)

    if args.dbg:
        print(ppg_df.schema)
        ppg_df.show()

    ppg_df = ppg_df.withColumn("ppg_ts_array", F.array(*ts_cols)).drop(*ts_cols)

    ppg_df = iirf_transform(ppg_df, "ppg_ts_array", "label_encoded")

    if args.dbg:
        print(ppg_df.schema)
        ppg_df.show()

    print("RAM", "BEFORE ACTION TRIGGER", get_executor_memory(sc), sep=";")

    ppg_df.write.mode("overwrite").parquet("hdfs://namenode:9000/outs/ppg.parquet")

    print("RAM", "FINAL STAGE", get_executor_memory(sc), sep=";")
    print("TIME", "OVERALL TIME", time.time() - start_time, sep=";")
