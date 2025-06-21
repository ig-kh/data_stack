FROM bitnami/spark:3.5.0
USER root
RUN apt-get update && apt-get install -y sqlite3 && apt-get clean
RUN pip install --no-cache-dir \
    pyspark==3.5.0 \
    delta-spark==3.2.0 \
    xgboost==2.0.3 \
    mlflow==2.13.2 \
    omegaconf==2.3.0 \
    hydra-core==1.3.2 \
    pandas==2.2.2 \
    scikit-learn==1.5.0 \
    matplotlib==3.8.4 \
    scipy==1.13.0
ENV SPARK_HOME=/opt/bitnami/spark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
USER 1001