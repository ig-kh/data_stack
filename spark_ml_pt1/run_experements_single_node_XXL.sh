#!/bin/bash

bash init.sh compose_singlenode_spark.yml

echo "resource;stage;value" > ./spark_res_single_XXL.csv

for i in $(seq 0 100);
do
    docker exec -i spark-master spark-submit --master spark://spark-master:7077 --jars ./scala/iirf/target/scala-2.12/iirf-assembly-0.1.0-SNAPSHOT.jar ./run.py --pth hdfs://namenode:9000/ppg_XXL.csv >> ./spark_res_single_L.csv
done

echo "resource;stage;value" > ./spark_res_single_XXL_opt.csv

for i in $(seq 0 100);
do
    docker exec -i spark-master spark-submit --master spark://spark-master:7077 --jars ./scala/iirf/target/scala-2.12/iirf-assembly-0.1.0-SNAPSHOT.jar ./run.py --pth hdfs://namenode:9000/ppg_XXL.csv --opt >> ./spark_res_single_L_opt.csv
done
