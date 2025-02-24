import argparse
import json
import time
import pandas as pd
import random
from confluent_kafka import Producer

TOPIC = "raw_data"


class DataLoaderProducerWrapper:
    def __init__(self, path, producer_id, batch_size=8, random_delay=False):
        self.df = pd.read_csv(path)
        if "Label" in self.df.columns:
            self.df = self.df.drop(columns=["Label"])
        self.conf = {
            "bootstrap.servers": "localhost:9095",
            "client.id": f"producer_{producer_id}",
        }
        self.producer = Producer(self.conf)
        self.producer_id = producer_id
        self.random_delay = random_delay
        self.batch_size = batch_size

    def run(self):
        for i in range(0, len(self.df), self.batch_size):
            batch = self.df.iloc[
                i : min(i + self.batch_size, len(self.df))
            ]  # Берем батч данных
            messages = batch.to_dict(
                orient="records"
            )  # Преобразуем в список JSON-объектов
            self.producer.produce(
                TOPIC, key=f"producer_{self.producer_id}", value=json.dumps(messages)
            )
            self.producer.flush()

            delay = random.uniform(0.25, 0.5) if self.random_delay else (0.25 + 0.5) / 2
            time.sleep(delay)

        print((f"Producer {self.producer_id} finished sending data"))


def parse_args():
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument(
        "--data_source",
        type=str,
        default="./data_ppg/tests",
        help="Path to the CSV data file",
    )
    parser.add_argument("--producer_id", type=int, help="Data Loader ID")
    parser.add_argument(
        "--batch_size",
        type=int,
        default=64,
        help="Max number of samples per loading iteration",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    producer = DataLoaderProducerWrapper(
        path=args.data_source,
        producer_id=args.producer_id,
        batch_size=args.batch_size,
        random_delay=True,
    )
    producer.run()
