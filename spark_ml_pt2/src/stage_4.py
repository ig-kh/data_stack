from pyspark.sql import SparkSession
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import numpy as np
import argparse
from omegaconf import OmegaConf
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src")
    parser.add_argument("--config")
    args = parser.parse_args()

    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://0.0.0.0:5002")

    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    cfg = OmegaConf.load(args.config)

    # Initialize Spark session
    logger.info("Initializing Spark session")
    spark = (
        SparkSession.builder.appName("XGBoostCreditScoreCV")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    # Start MLflow run
    with mlflow.start_run(run_name="XGBoost_CV"):
        # Log configuration parameters
        logger.info("Logging configuration parameters")
        mlflow.log_params(OmegaConf.to_container(cfg.xgboost, resolve=True))
        mlflow.log_param("train_path", args.src)
        mlflow.log_param("n_folds", cfg.train.n_folds)
        mlflow.log_param("batch_size", cfg.train.batch_size)

        # Load gold data
        logger.info(f"Loading gold data from {args.src}")
        train_df = spark.read.format("delta").load(args.src)
        train_pd = train_df.toPandas()

        # Define features and target
        features = [
            "age",
            "annual_income",
            "credit_history_age_months",
            "monthly_inhand_salary",
            "num_of_delayed_payment_imputed",
            "credit_utilization_ratio"
        ]
        target = "credit_score_class"

        # Prepare data
        X = train_pd[features].values
        y = train_pd[target].values.astype(int)  # Ensure integer labels

        # K-fold cross-validation
        kf = KFold(n_splits=cfg.train.n_folds, shuffle=True, random_state=cfg.xgboost.random_state)
        accuracies = []
        f1_scores = []
        all_predictions = np.zeros((len(y), cfg.train.n_folds))
        fold_idx = 0

        for train_idx, val_idx in kf.split(X):
            with mlflow.start_run(nested=True, run_name=f"Fold_{fold_idx+1}"):
                logger.info(f"Training fold {fold_idx+1}/{cfg.train.n_folds}")
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]

                # Train XGBoost model
                model = xgb.XGBClassifier(**OmegaConf.to_container(cfg.xgboost, resolve=True))
                model.fit(X_train, y_train)

                # Evaluate
                y_pred_val = model.predict(X_val)
                accuracy = accuracy_score(y_val, y_pred_val)
                f1 = f1_score(y_val, y_pred_val, average="weighted")
                mlflow.log_metric("fold_accuracy", accuracy)
                mlflow.log_metric("fold_f1_score", f1)
                logger.info(f"Fold {fold_idx+1} - Accuracy: {accuracy:.4f}, F1-Score: {f1:.4f}")
                accuracies.append(accuracy)
                f1_scores.append(f1)

                # Store predictions
                all_predictions[val_idx, fold_idx] = y_pred_val
                mlflow.xgboost.log_model(model, f"xgboost_model_fold_{fold_idx+1}")
            
            fold_idx += 1

        # Log aggregated metrics
        mean_accuracy = np.mean(accuracies)
        std_accuracy = np.std(accuracies)
        mean_f1 = np.mean(f1_scores)
        std_f1 = np.std(f1_scores)
        mlflow.log_metric("mean_cv_accuracy", mean_accuracy)
        mlflow.log_metric("std_cv_accuracy", std_accuracy)
        mlflow.log_metric("mean_cv_f1_score", mean_f1)
        mlflow.log_metric("std_cv_f1_score", std_f1)
        logger.info(f"CV Results - Mean Accuracy: {mean_accuracy:.4f} (+/-{std_accuracy:.4f}), Mean F1-Score: {mean_f1:.4f} (+/-{std_f1:.4f})")

        # Train final model
        logger.info("Training final model on full data")
        final_model = xgb.XGBClassifier(**OmegaConf.to_container(cfg.xgboost, resolve=True))
        final_model.fit(X, y)
        mlflow.xgboost.log_model(final_model, "final_xgboost_model")

        # Save CV results
        output_path = cfg.train.output_path
        logger.info(f"Saving CV results to {output_path}")
        cv_results = pd.DataFrame({
            "fold": range(1, cfg.train.n_folds + 1),
            "accuracy": accuracies,
            "f1_score": f1_scores
        })
        cv_results.to_csv(output_path, index=False)
        mlflow.log_artifact(output_path)

    # Stop Spark session
    print("\033[0;32m[♡〜٩( ˃▿˂ )۶〜♡]\033[0m XGBoost metrics and params are available at \33[0;34mMLFLOW\033[0m!")
    spark.stop()