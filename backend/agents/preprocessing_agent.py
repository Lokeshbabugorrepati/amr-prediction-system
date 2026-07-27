"""
preprocessing_agent.py
-----------------------
Agent 1: Data Collection & Preprocessing Agent

Responsibilities (mirrors Section III-A of the reference paper):
  1. Load raw genomic + clinical data
  2. Fill missing numeric values with the median
  3. Fill missing categorical values with the placeholder "missing"
  4. Z-score normalize numeric features (StandardScaler)
  5. One-Hot Encode categorical features
  6. Balance classes with SMOTE
  7. Stratified 80:20 train/test split

This agent exposes `fit_transform()` (used once, during training) and
`transform_single()` (used at inference time to preprocess one incoming
patient/organism record using the SAME fitted encoders/scalers).
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

TARGET_COL = "resistance_status"
ID_COL = "sample_id"

NUMERIC_FEATURES = [
    "age", "treatment_duration_days", "mic_value_mg_l", "gc_content_pct",
    "genome_size_mb", "num_amr_genes_detected", "plasmid_count",
    "sequence_coverage_x", "prior_hospitalization_days",
]

CATEGORICAL_FEATURES = [
    "age_group", "organism_group", "infection_type", "sample_collection_site",
    "hospitalization_status", "previous_antibiotic_use", "previous_amr_history",
    "resistance_to_previous_treatment", "genomic_mutation_marker",
    "biofilm_formation", "efflux_pump_activity", "beta_lactamase_production",
    "porin_loss_mutation", "geographic_region", "specimen_source",
]


class PreprocessingAgent:
    """Cleans, encodes, normalizes and balances the AMR dataset."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.numeric_medians = {}
        self.class_labels = None

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in NUMERIC_FEATURES:
            median = df[col].median() if df[col].notna().any() else 0.0
            self.numeric_medians[col] = median
            df[col] = df[col].fillna(median)
        for col in CATEGORICAL_FEATURES:
            df[col] = df[col].fillna("missing").astype(str)
        return df

    def fit_transform(self, df: pd.DataFrame):
        """Used once during training. Returns SMOTE-balanced, stratified train/test splits."""
        df = self._clean(df)

        X_num = self.scaler.fit_transform(df[NUMERIC_FEATURES])
        X_cat = self.encoder.fit_transform(df[CATEGORICAL_FEATURES])
        X = np.hstack([X_num, X_cat])
        y = df[TARGET_COL].values
        self.class_labels = sorted(pd.unique(y))

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        smote = SMOTE(random_state=42)
        X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

        return X_train_bal, X_test, y_train_bal, y_test

    def transform_single(self, record: dict) -> np.ndarray:
        """Used at inference time on ONE incoming record (dict of raw field values)."""
        row = {}
        for col in NUMERIC_FEATURES:
            row[col] = record.get(col, self.numeric_medians.get(col, 0.0))
        for col in CATEGORICAL_FEATURES:
            row[col] = str(record.get(col, "missing"))

        df_row = pd.DataFrame([row])
        X_num = self.scaler.transform(df_row[NUMERIC_FEATURES])
        X_cat = self.encoder.transform(df_row[CATEGORICAL_FEATURES])
        return np.hstack([X_num, X_cat])

    def feature_names(self):
        cat_names = list(self.encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        return NUMERIC_FEATURES + cat_names

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str) -> "PreprocessingAgent":
        return joblib.load(path)
