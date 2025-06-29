# Kafka🕸 feat. 🐍Python AEON⏳ for 🩺PPG based MI detection🫀<br>
### 👉 [🩺🫀🗃️ → 🕸 → ⏳🤖👑](run_pipe.sh) 👈

![alt text](image.png)

## Data [🩺🫀]: Myocardial Infarction from PPG. <br>
The task is based on synthetical dataset containing timeserieses describing PPG data from medical device published at https://www.kaggle.com/datasets/ucimachinelearning/photoplethysmography-ppg-dataset. It also contains labeling for normal mediacl condition and MI case. 
## Kafka [🕸]: Producer-Consumer architecture. <br>
The architecture of application is based on producer-consumer scheme implemented in confluent kafka for python PL.


Source can be seen 👉[here](./producers/dataloader).<br>

Source can be seen 👉[here](./consumers/).<br>

## AEON-ML [⏳🤖]: Perform classification. <br>

For better application of Machine Learning algorithm as a preprocessing an Infinite Impulse Response Filter was used. 

Source can be seen 👉[here](./consumers/preprocessor.py).<br>

Source can be seen 👉[here](./consumers/classifier.py).<br>

## StreamLit [👑]: Results live demo. <br>
A live demonstrarion of 
Source can be seen 👉[here](./consumers/plotter.py).<br>
### 👉 [⛔](stop_pipe.sh) 👈

<!-- Репозиторий реализует инференс модели шейплетной классификации данных с медицинского прибора.

2 продюсера (producers/dataloadr.py) подбирают данные из разных csv файлов, через брокер они попадают в препроцессинг (consumers/preprocessor.py), оттуда фильрованые данные с закодированными лейблами попадают в воркер с моделью (consumers/classifier.py), и наконец метрика считается и отображается графически в плотере (consumers/plotter.py).

Скрипты загрузки парамтеризованы батч сайзом и путями к данным(в лоудере); консюмеры по потребности подгружают гтовые чекпоинты модели и лейбл-энкодера (они предварительно готовятся в ml/train.py; там же и сиходные файлы МЛ-составляющих).

Для запуска скрипта используется run_pipe.sh, для остановки stop_pipe.sh; run_pipe.sh автоматически подгружает в венве, распололоженнос в директории (не создан предварительно) нужные библиотеки, точка запуска - текущая директория (kafka_ml). -->
