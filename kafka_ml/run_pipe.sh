#!/bin/bash

pwd

# 1. Поднимаем Kafka
docker-compose up -d

# 2. Ждем, пока Kafka полностью запустится (настройте время ожидания при необходимости)
echo "Waiting for Kafka to start..."
sleep 5
docker exec -it lab1-kafka-1 kafka-topics.sh --create --topic raw_data --bootstrap-server localhost:9095 --partitions 3 --replication-factor 1
docker exec -it lab1-kafka-1 kafka-topics.sh --create --topic processed_data --bootstrap-server localhost:9095 --partitions 3 --replication-factor 1
docker exec -it lab1-kafka-1 kafka-topics.sh --create --topic ml_result --bootstrap-server localhost:9095 --partitions 3 --replication-factor 1

python3 -m pip install confluent_kafka pandas aeon
export PYTHONPATH=$PYTHONPATH:/home/igkh/codes/data_stack/kafka_ml/ml

# 4. Запускаем продюсеров в фоне
echo "Starting Producer 0..."
python3 producers/dataloader.py --data_source /home/igkh/codes/data_stack/kafka_ml/data_ppg/train/ppg_train.csv --producer_id 0 &
echo "Starting Producer 1..."
python3 producers/dataloader.py --data_source /home/igkh/codes/data_stack/kafka_ml/data_ppg/train/ppg_train.csv --producer_id 1 &
sleep 3

# 3. Запускаем консюмеры в фоне (каждый в отдельном терминальном окне или фоне)
echo "Starting processing consumer..."
python3 consumers/preprocessor.py --le_path /home/igkh/codes/data_stack/kafka_ml/ml/checkpoints/le.ckpt &
sleep 3
echo "Starting ML consumer..."
python3 consumers/classifier.py --model_path /home/igkh/codes/data_stack/kafka_ml/ml/checkpoints/model.ckpt &
sleep 3

# echo "Starting visualization consumer..."
# streamlit run consumers/visualization.py &

# Ожидаем завершения фоновых процессов (если требуется)
wait