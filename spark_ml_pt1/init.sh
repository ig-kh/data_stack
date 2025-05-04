#!/bin/bash

docker stop spark-worker-1 spark-master datanode1 datanode2 datanode3 namenode
docker rm spark-worker-1 spark-master datanode1 datanode2 datanode3 namenode

docker-compose -f $1 up -d

docker cp -L src/. spark-master:/opt/bitnami/spark/

sleep 30

docker exec -it namenode hdfs dfsadmin -safemode leave

docker cp data/ppg.csv namenode:/
docker cp data/ppg_XXL.csv namenode:/

docker exec -it namenode hdfs dfs -put ppg.csv /
docker exec -it namenode hdfs dfs -put ppg_XXL.csv /