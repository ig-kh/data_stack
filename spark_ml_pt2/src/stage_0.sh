#!/bin/bash
mkdir data/raw -p
sudo curl -L -o data/raw/credit-score-classification.zip https://www.kaggle.com/api/v1/datasets/download/parisrohan/credit-score-classification
unzip data/raw/credit-score-classification.zip -d data/raw
rm data/raw/credit-score-classification.zip
echo -e "\033[0;32m[(૭ ｡•̀ ᵕ •́｡ )૭]\033[0m Data is available at it's raw source"