"""
train_model.py
----------------
Runs Agent 1 (Preprocessing) and Agent 2 (Modelling) end-to-end on
amr_dataset.csv, then saves both fitted agents to models/ so the FastAPI
backend can load them instantly at request time without retraining.

Run:
    python train_model.py
"""

import json
import pandas as pd
from agents.preprocessing_agent import PreprocessingAgent
from agents.modelling_agent import ModellingAgent

DATA_PATH = "data/amr_dataset.csv"
PREPROCESSOR_OUT = "models/preprocessing_agent.joblib"
MODEL_OUT = "models/modelling_agent.joblib"
METRICS_OUT = "models/metrics.json"


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    print("Running Preprocessing Agent (clean -> scale -> encode -> SMOTE -> split)...")
    prep = PreprocessingAgent()
    X_train, X_test, y_train, y_test = prep.fit_transform(df)
    print(f"  Train shape (post-SMOTE): {X_train.shape}, Test shape: {X_test.shape}")

    print("Running Modelling Agent (XGBoost + LightGBM + CatBoost + DNN blend)...")
    model = ModellingAgent()
    model.fit(X_train, y_train, X_test, y_test)

    print("\nPerformance:")
    for name, m in model.metrics_.items():
        print(f"  {name:35s} acc={m['accuracy']}%  f1={m['f1_score']}  auc={m['auc']}")
    print(f"  Best blend alpha: {model.alpha}")

    prep.save(PREPROCESSOR_OUT)
    model.save(MODEL_OUT)
    with open(METRICS_OUT, "w") as f:
        json.dump({
            "table": model.metrics_,
            "confusion_matrix": model.confusion_,
            "classes": model.classes_,
        }, f, indent=2)

    print(f"\nSaved: {PREPROCESSOR_OUT}, {MODEL_OUT}, {METRICS_OUT}")


if __name__ == "__main__":
    main()
