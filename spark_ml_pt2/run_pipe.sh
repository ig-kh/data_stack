#!/bin/bash
BOLD='\033[1m'
BRONZE_C='\033[1;31m'
SILVER_C='\033[1;30m'
GOLD_C='\033[1;33m'
SPARK_C='\033[1;36m'   
MLFLOW_C='\033[1;34m'
NC='\033[0m'

echo -e "${BOLD}Init:${NC} Initializing ${SPARK_C}SPARK${NC}"

echo -e "${BOLD}Init:${NC} Resetting data storage"
rm -rf data/*

echo -e "${BOLD}Running stage 0:${NC} Dump data to ${BRONZE_C}BRONZE${NC} layer"
bash src/stage_0.sh

echo -e "${BOLD}Running stage 1:${NC} Clean ${BRONZE_C}BRONZE${NC} data and transfer it to ${SILVER_C}SILVER${NC} layer as Delta table"

echo "Processing train"

echo "Processing test"

echo -e "${BOLD}Running stage 2:${NC} Aggregate ${SILVER_C}SILVER${NC} layer data and save to ${GOLD_C}GOLD${NC} layer"

echo "Processing train"

echo "Processing test"

echo -e "${BOLD}Running stage 3:${NC} Running train on ${GOLD_C}GOLD${NC} layer"