#!/bin/bash

#cosmetics
BOLD='\033[1m'
BRONZE_C='\033[1;31m'
SILVER_C='\033[1;30m'
GOLD_C='\033[1;33m'
SPARK_C='\033[1;36m'   
MLFLOW_C='\033[1;34m'
NC='\033[0m'

echo "${BOLD}Running stage 0:${NC} Dump data"
bash src/stage_0.sh

echo "${BOLD}Running stage 1:${NC} Move data to ${BRONZE_C}BRONZE${NC} layer as Delta table"

docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  /app/src/stage_1.py --src ./data/raw/train.csv  --dst ./data/bronze/train

echo "${BOLD}Running stage 2:${NC} Clean ${BRONZE_C}BRONZE${NC} data and transfer it to ${SILVER_C}SILVER${NC} layer"

docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  /app/src/stage_2.py --src ./data/bronze/train  --dst ./data/silver/train

echo "${BOLD}Running stage 3:${NC} Aggregate ${SILVER_C}SILVER${NC} layer data and save to ${GOLD_C}GOLD${NC} layer"

docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  /app/src/stage_3.py --src ./data/silver/train  --dst ./data/gold/train

echo "${BOLD}Running stage 4:${NC} Running train on ${GOLD_C}GOLD${NC} layer"

docker exec -t spark spark-submit --packages io.delta:delta-spark_2.12:3.2.0 \
 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
 --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"  /app/src/stage_4.py --src ./data/gold/train --config ./conf/config.yaml