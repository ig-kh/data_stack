1. В качестве данных использован сплит из датасета https://www.kaggle.com/datasets/ucimachinelearning/photoplethysmography-ppg-dataset (300 MB); дополнительно на их основе при помощи обычной дупликации создал увеличенную версию (3 GB, замеры обозначаются XXL суффиксом).
Скрипт совершает кодирование лейблов и iir-фильтрацию показаний прибора.
2. src/run.py - приложение на pyspark с обработкой csv-файла; запуски экспериментов осуществляются в скриптах {run_experements_multi_node, run_experements_multi_node_XXL, run_experements_single_node, run_experements_single_node_XXL}.sh; сконфигурированы в файлах dockerfile/compose_.yml и hadoop.cfg .
3. Само spark приложение дополнительно конфигурируется флагами (--opt - применеие оптимизаций, --pth - путь к файлу, --dbg - дебаг) и запускается через spark submit (с указанием дополнительных исходных кодов через --jars).
4. В приложении применены две оптимизаци - репартицирование и вызов skala-udf (исходные коды и результаты сборки sbt в src/skala/iirf/*) вместо python-udf.
5. Результаты работы (построены в plots.ipynb - ноутбуке, боксплоты на основе 100 запусков каждого сетапа):
   
   Оригинальный сплит - 3 ноды
   ![image](https://github.com/user-attachments/assets/405467f1-3e95-4d1b-b61a-524190f66466)

   Оригинальный сплит - 1 нода
   ![image](https://github.com/user-attachments/assets/4e6a04c8-7305-4740-a757-7eeb2e634699)

   Увеличенный сплит - 3 ноды
![image](https://github.com/user-attachments/assets/6e1403c0-d7f8-40d0-b299-cf84af0b272b)


   Увеличенный сплит - 1 нода
![image](https://github.com/user-attachments/assets/a74026f8-8efd-4626-be3c-1d7c689ecf01)

