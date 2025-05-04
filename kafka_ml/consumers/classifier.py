import sys

sys.path.append("/home/igkh/codes/data_stack/kafka_ml/ml")

import argparse
import json

import numpy as np
import pandas as pd
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

from ml import ShapeletRidgeCLF

TOPIC = "ml_result"


class CLFConsumerWrapper:
    def __init__(self, model_path) -> None:

        self.model = ShapeletRidgeCLF.from_pickle(model_path)

        self.cons_conf = {
            "bootstrap.servers": "localhost:9095",
            "group.id": "ml-group",
            "auto.offset.reset": "earliest",
        }

        self.prod_conf = {
            "bootstrap.servers": "localhost:9095",
            "client.id": "ml_results_producer",
        }

        self.consumer = Consumer(self.cons_conf)
        self.consumer.subscribe(["filtered_data"])

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
                X_test = data["X_test"]
                X_test = np.vstack([np.asarray(s) for s in X_test])

                y_pred = self.model.predict(X_test)
                y_test = data["y_test"]

                processed_data = {
                    "y_pred": y_pred.tolist(),
                    "y_test": y_test,
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
    parser = argparse.ArgumentParser(description="Kafka ML Model worker-consumer")
    parser.add_argument(
        "--model_path",
        type=str,
        help="Path to the saved model ckpt file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    consumer = CLFConsumerWrapper(
        model_path=args.model_path,
    )
    consumer.run()
