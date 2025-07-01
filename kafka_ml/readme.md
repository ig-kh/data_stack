# Kafka🕸 feat. 🐍Python AEON⏳ for 🩺PPG based MI detection🫀<br>
### 👉 [🩺🫀🗃️ → 🕸 → ⏳🤖👑](run_pipe.sh) 👈

![alt text](image.png)

## Data [🩺🫀]: Myocardial Infarction from PPG. <br>
The task is based on synthetical dataset containing timeserieses describing PPG data from medical device published at https://www.kaggle.com/datasets/ucimachinelearning/photoplethysmography-ppg-dataset. It also contains labeling for normal mediacl condition and MI case. 
## Kafka [🕸]: Producer-Consumer architecture. <br>
The architecture of application is based on producer-consumer scheme implemented in confluent kafka for python PL.

The data is collected and broadcasted by dataloader prodeucer.
Source can be seen 👉[here](./producers/dataloader).<br>

The main workload of app is spred across three consumers:

- preprocessor
- classifier
- plotter

who carry out data transformation, machine learning algorithm and calculation of qualitive metrics as well as display of them respectively. 

Sources can be seen 👉[here](./consumers/).<br>

## AEON-ML [⏳🤖]: Perform classification. <br>

The main framework goes as follows: the model is trained in offline in the setup described  👉[here](./ml/train.py).

The pipeline includes application of 👉[shapelet learning](https://www.aeon-toolkit.org/en/stable/examples/classification/shapelet_based.html) and simple classifier based on extracted features.

For better application of Machine Learning algorithm as a preprocessing an Infinite Impulse Response Filter was used. The labeles are represented as _str_ type and are encoded as _int_ classes with LabelEncoder.

The IIRF is applied in online manner as seen
👉[here](./consumers/preprocessor.py) in special preprocessor-consumer.<br>

Classifier checkpoint is loaded to produce online prediction at init stage of classifier-consumer.
Source can be seen 👉[here](./consumers/classifier.py).<br>

## StreamLit [👑]: Results live demo. <br>
A live demonstrarion of metrics (f1, ConfusionMatrix) as well as their calculation happens inside matplotlib based plotter entity, the plots are brought to live with dedicated StreamLit service.<br>
Source can be seen 👉[here](./consumers/plotter.py).<br>

## Containerization [🐳]: Docker
All entities as well as ad hoc py venv are loaded and running inside 👉[Docker containers](./docker-compose.yaml).

## Customization [⚙️🛠️]:
All entities can be tuned at start via command line arguments which include loading and batching parameters as well as model and encoder checkpoint paths.

### 👉 [⛔Stop running services⛔](stop_pipe.sh) 👈