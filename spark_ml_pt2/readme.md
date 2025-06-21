# ∆-lake 🏞️ feat. 🐍PySpark✨ and 🌴xgboost🌳 for 💵credit score classification🧮<br>
### 👉 [💾🌐🗃️ → 🥉 → 🥈 → 🥇 → 🤖📊](run_pipe.sh) 👈

## Stage 0 [📥]: Dump data from internet. <br>
Download credit scoring dataset from kaggle: https://www.kaggle.com/api/v1/datasets/download/parisrohan/credit-score-classification; dump it to raw data storage and unzip. Source can be seen [here](./src/stage_0.sh).<br>
## Stage 1 [💾🌐🗃️ → 🥉]: Load raw data to Bronze layer. <br>
Collects data from raw storage and save it in delta format to bronze layer. Source can be seen [here](./src/stage_1.py).<br>
## Stage 2 [🥉 → 🥈]: <br>
Load data from bronze layer, then perform following: <br>
1. Narrow down attributes to only necessary
2. Cast to proper numerical types where applicable
3. Parse complex types discribes as strings
4. Fill nulls via heuristics
5. Drop remaining nulls<br>
6. Optimize data via z-ordering and compaction
Source can be seen [here](./src/stage_2.py).<br>
## Stage 3 [🥈 → 🥇]: <br>
Aggregate user info from silver layer based on business logic for completing customer profiling. <br>
Rules for aggregatation and feature-engineering are following: <br>
1. Select Latest Record: Uses a window function to assign row numbers within customer_id partitions, ordered by month descending, and selects the latest record
2. Feature Selection: Retains ML-relevant features
3. No Additional Feature Engineering: Preserves cleaned, numerical data from the silver layer for ML compatibility
4. Encode remainig str-typed attributes
Source can be seen [here](./src/stage_3.py).<br>
## Stage 4 [🥇 → 🤖📊]: <br>

Source can be seen [here](./src/stage_4.py).<br>