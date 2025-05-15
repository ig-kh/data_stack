# ∆-lake 🏞️ feat. 🐍PySpark✨ and 🌴xgboost🌳<br>
### 👉 [💾🌐🗃️ → 🥉 → 🥈 → 🥇 → 🤖📊](run_pipe.sh) 👈

## Stage 0 [📥]: Dump data from internet. <br>
Download credit scoring dataset from kaggle: https://www.kaggle.com/api/v1/datasets/download/parisrohan/credit-score-classification; dump it to raw data storage and unzip. Source can be seen [here](./src/stage_0.sh).<br>
## Stage 1 [💾🌐🗃️ → 🥉]: Load raw data to Bronze layer. <br>
Collects data from raw storage and save it in delta format to bronze layer. Source can be seen [here](./src/stage_1.py).<br>
## Stage 2 [🥉 → 🥈]: <br>
Load data from bronze layer, then perform following: <br>
1. Drop rows with nulls in columns 
2. 
3.
Source can be seen [here](./src/stage_2.py).<br>
## Stage 3 [🥈 → 🥇]: <br>
Source can be seen [here](./src/stage_3.py).<br>
## Stage 4 [🥇 → 🤖📊]: <br>
Source can be seen [here](./src/stage_4.py).<br>