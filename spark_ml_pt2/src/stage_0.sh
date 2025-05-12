#!/bin/bash
mkdir data/bronze -p
sudo curl -L -o data/bronze/credit-score-classification.zip https://www.kaggle.com/api/v1/datasets/download/parisrohan/credit-score-classification
unzip data/bronze/credit-score-classification.zip -d data/bronze
rm data/bronze/credit-score-classification.zip