#!/bin/bash
# scripts/train_models.sh
# Trains all fraud detection models (supervised + unsupervised) sequentially.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate virtual environment
VENV_PATH="${VENV_PATH:-./venv}"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "Activated virtual environment at $VENV_PATH"
fi

# Ensure data exists
if [ ! -f "data/processed/features_train.csv" ]; then
    echo "Error: data/processed/features_train.csv not found. Run feature engineering first."
    exit 1
fi

# Create output directories if missing
mkdir -p models logs

# Log file
LOG_FILE="logs/training_$(date +%Y%m%d_%H%M%S).log"

echo "Starting model training at $(date)" | tee -a "$LOG_FILE"

# Train models
echo "----------------------------------------" | tee -a "$LOG_FILE"
echo "Training Logistic Regression..." | tee -a "$LOG_FILE"
python -m ml_pipeline.training.train_logistic 2>&1 | tee -a "$LOG_FILE"

echo "Training Random Forest..." | tee -a "$LOG_FILE"
python -m ml_pipeline.training.train_random_forest 2>&1 | tee -a "$LOG_FILE"

echo "Training XGBoost..." | tee -a "$LOG_FILE"
python -m ml_pipeline.training.train_xgboost 2>&1 | tee -a "$LOG_FILE"

echo "Training Isolation Forest..." | tee -a "$LOG_FILE"
python -m ml_pipeline.training.train_isolation_forest 2>&1 | tee -a "$LOG_FILE"

echo "----------------------------------------" | tee -a "$LOG_FILE"
echo "All models trained successfully at $(date)" | tee -a "$LOG_FILE"