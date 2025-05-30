import sys

sys.path.append("/home/igkh/codes/data_stack/kafka_ml/ml")

import argparse
import json
import pickle

import pandas as pd
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

from ml import InfiniteImpulseResponseFilter, partial_vectorize

TOPIC = "filtered_data"


class PrepocessorConsumerWrapper:
    def __init__(self, le_path) -> None:

        self.filter = InfiniteImpulseResponseFilter()

        with open(le_path, "rb") as f:
            le_object = pickle.load(f)

        self.le = le_object
        self.cons_conf = {
            "bootstrap.servers": "localhost:9095",
            "group.id": "data-processing-group",
            "auto.offset.reset": "earliest",
        }

        self.prod_conf = {
            "bootstrap.servers": "localhost:9095",
            "client.id": "processed_data_producer",
        }

        self.consumer = Consumer(self.cons_conf)
        self.consumer.subscribe(["raw_data"])

        self.producer = Producer(self.prod_conf)

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())

                data = json.loads(msg.value().decode("utf-8"))
                raw_data_batch = pd.DataFrame(data)
                if "Unnamed: 0" in raw_data_batch.columns:
                    raw_data_batch = raw_data_batch.drop(columns=["Unnamed: 0"])
                vec_data = partial_vectorize(raw_data_batch, ["Label"])
                X_test = self.filter(vec_data["seq"])
                y_test = self.le.transform(vec_data["stat"].ravel())

                processed_data = {
                    "X_test": X_test.tolist(),
                    "y_test": y_test.tolist(),
                }

                self.producer.produce(
                    TOPIC, key=msg.key(), value=json.dumps(processed_data)
                )
                self.producer.flush()

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Kafka preprocessing worker-consumer")
    parser.add_argument(
        "--le_path",
        type=str,
        help="Path to the saved LabelEncoder ckpt file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    consumer = PrepocessorConsumerWrapper(
        le_path=args.le_path,
    )
    consumer.run()
