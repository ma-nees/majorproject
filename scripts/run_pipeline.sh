#!/bin/bash
# scripts/run_pipeline.sh
# Runs the complete ML pipeline: clean, feature engineering, train, evaluate.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate venv
source ./venv/bin/activate

# Step 1: Preprocessing (if you have a preprocessing script that outputs clean data)
echo "Running data preprocessing..."
python -m ml_pipeline.preprocessing.run_preprocessing  # create this if needed

# Step 2: Feature engineering
echo "Running feature engineering..."
python -m ml_pipeline.feature_engineering.build_features

# Step 3: Train models
echo "Training models..."
./scripts/train_models.sh

# Step 4: Evaluate and compare models
echo "Evaluating models..."
python -m ml_pipeline.evaluation.model_comparison

echo "Pipeline completed."