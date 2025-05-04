#!/bin/bash

bash init.sh compose_multinode_spark.yml

echo "resource;stage;value" > ./spark_res_three.csv

for i in $(seq 0 100);
do
    docker exec -i spark-master spark-submit --master spark://spark-master:7077 --jars ./scala/iirf/target/scala-2.12/iirf-assembly-0.1.0-SNAPSHOT.jar ./run.py --pth hdfs://namenode:9000/ppg.csv >> ./spark_res_three.csv
done

echo "resource;stage;value" > ./spark_res_three_opt.csv

for i in $(seq 0 100);
do
    docker exec -i spark-master spark-submit --master spark://spark-master:7077 --jars ./scala/iirf/target/scala-2.12/iirf-assembly-0.1.0-SNAPSHOT.jar ./run.py --pth hdfs://namenode:9000/ppg.csv --opt >> ./spark_res_three_opt.csv
done
