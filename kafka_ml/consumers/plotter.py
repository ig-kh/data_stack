import argparse
import json
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from confluent_kafka import Consumer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


class PlotterConsumerWrapper:
    def __init__(self, le_path):
        st.title("ML results")

        with open(le_path, "rb") as f:
            le_object = pickle.load(f)

        le = le_object

        self.le_inv_mapping = dict(zip(le.transform(le.classes_), le.classes_))

        if "y_test" not in st.session_state:
            st.session_state["y_test"] = []

        if "y_pred" not in st.session_state:
            st.session_state["y_pred"] = []

        if "num_processed" not in st.session_state:
            st.session_state["num_processed"] = []

        conf = {
            "bootstrap.servers": "localhost:9095",
            "group.id": "ml-result",
            "auto.offset.reset": "earliest",
        }

        self.consumer = Consumer(conf)
        self.consumer.subscribe(["ml_result"])

        self.chart_f1 = st.empty()
        self.chart_accuracy = st.empty()
        self.hist_chart = st.empty()
        self.conf_matrix_placeholder = st.empty()

        self.f1_scores_batches = []
        self.acc_scores_batches = []

    def run(self):

        while True:
            msg = self.consumer.poll(1000)

            try:
                data = json.loads(msg.value().decode("utf-8"))
            except Exception:
                continue

            if data:

                st.session_state["y_test"].extend(data["y_test"])
                st.session_state["y_pred"].extend(data["y_pred"])
                st.session_state["num_processed"].append(
                    len(st.session_state["y_test"])
                )

                class_counts = (
                    pd.Series(st.session_state["y_test"]).value_counts().sort_index()
                )
                fig, ax = plt.subplots(figsize=(4, 3))
                colors = ["red", "blue"]
                ax.bar(class_counts.index, class_counts.values, color=colors)
                ax.set_xlabel("Classes", fontsize=7)
                ax.set_ylabel("Count", fontsize=7)
                ax.set_title("Running true class distribution", fontsize=10)
                ax.set_xticks([i for i in range(len(self.le_inv_mapping))])
                ax.set_xticklabels(
                    list(self.le_inv_mapping.values()), rotation=60, fontsize=7
                )
                self.hist_chart.pyplot(fig)
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(4, 3))
                f1_cur = f1_score(data["y_test"], data["y_pred"], average="micro")
                self.f1_scores_batches.append(f1_cur)
                ax.plot(
                    [i for i in range(len(self.f1_scores_batches))],
                    self.f1_scores_batches,
                )
                ax.set_title("F1 scores/batches", fontsize=10)
                ax.set_ylabel("F1-score (micro)", fontsize=7)
                ax.set_ylim((0.3, 1))
                ax.grid(True, linestyle="--", alpha=0.6)
                ticks = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                ax.set_yticks(ticks)
                ax.set_yticklabels(list(map(str, ticks)), fontsize=8)
                self.chart_f1.pyplot(fig)
                plt.close(fig)

                fig, ax = plt.subplots(figsize=(4, 3))
                acc_cur = accuracy_score(data["y_test"], data["y_pred"])
                self.acc_scores_batches.append(acc_cur)
                ax.plot(
                    [i for i in range(len(self.acc_scores_batches))],
                    self.acc_scores_batches,
                )
                ax.set_title("Accuracy scores/batches", fontsize=10)
                ax.set_ylabel("Accuracy", fontsize=7)
                ax.set_ylim((0.3, 1))
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.set_yticks(ticks)
                ax.set_yticklabels(list(map(str, ticks)), fontsize=8)
                self.chart_accuracy.pyplot(fig)
                plt.close(fig)

                cm = confusion_matrix(
                    st.session_state["y_test"],
                    st.session_state["y_pred"],
                    labels=list(self.le_inv_mapping.keys()),
                )

                fig, ax = plt.subplots(figsize=(6, 4))
                sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
                ax.set_xticklabels(
                    list(self.le_inv_mapping.values()), rotation=60, fontsize=7
                )
                ax.set_yticklabels(
                    list(self.le_inv_mapping.values()), rotation=0, fontsize=7
                )
                ax.set_xlabel("Predicted labels", fontsize=7)
                ax.set_ylabel("True labels", fontsize=7)
                ax.set_title("Confusion Matrix", fontsize=10)

                self.conf_matrix_placeholder.pyplot(fig)
                plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Streamlit life graphx Kafka consumer")
    parser.add_argument(
        "--le_path",
        type=str,
        help="Path to the saved LabelEncoder ckpt file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    consumer = PlotterConsumerWrapper(
        le_path=args.le_path,
    )
    consumer.run()
