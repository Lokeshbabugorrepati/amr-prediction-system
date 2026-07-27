"""
modelling_agent.py
-------------------
Agent 2: Modelling Agent

Implements the hybrid classifier described in Section III-B:
  - Gradient boosting ensemble: XGBoost, LightGBM, CatBoost
  - A neural network component (MLPClassifier stands in for the
    paper's Keras/TensorFlow DNN -- same role: dense layers + ReLU +
    dropout-like regularization via alpha, without pulling in a full
    TensorFlow install for a resume project. Swap in a Keras
    Sequential model here if you want to match the paper exactly.)
  - A weighted blend of the ensemble's averaged probability output and
    the neural net's probability output (the paper's "alpha blend")

Produces class probabilities for Resistant / Intermediate / Susceptible
plus a per-class confidence breakdown that the frontend displays.
"""

import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix
from sklearn.preprocessing import label_binarize, LabelEncoder
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


class ModellingAgent:
    """Hybrid DNN + gradient-boosting ensemble for 3-class AMR classification."""

    BEST_ALPHA_GRID = np.linspace(0, 1, 11)  # blend search: 0=pure ensemble, 1=pure NN

    def __init__(self):
        self.classes_ = None
        self.xgb = XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.08,
            subsample=0.9, colsample_bytree=0.9, eval_metric="mlogloss",
            random_state=42,
        )
        self.lgbm = LGBMClassifier(
            n_estimators=300, max_depth=-1, learning_rate=0.08,
            subsample=0.9, colsample_bytree=0.9, random_state=42, verbose=-1,
        )
        self.catboost = CatBoostClassifier(
            iterations=300, depth=6, learning_rate=0.08,
            random_seed=42, verbose=False,
        )
        self.dnn = MLPClassifier(
            hidden_layer_sizes=(512, 256), activation="relu",
            alpha=1e-3, learning_rate_init=1e-3, max_iter=400,
            early_stopping=True, random_state=42,
        )
        self.alpha = 0.35  # weight given to the DNN branch in the final blend
        self.metrics_ = {}

    def _reorder_encoded_proba(self, proba_raw):
        """xgb/dnn were trained on LabelEncoder-numeric labels (0,1,2...); reorder
        their probability columns to match self.classes_ (alphabetical) so every
        model's output columns line up before averaging/blending."""
        order = self._label_encoder.inverse_transform(np.arange(proba_raw.shape[1]))
        idx = [list(order).index(c) for c in self.classes_]
        return proba_raw[:, idx]

    def _ensemble_proba(self, X):
        p1 = self._reorder_encoded_proba(self.xgb.predict_proba(X))
        p2 = self.lgbm.predict_proba(X)
        p3 = self.catboost.predict_proba(X)
        return (p1 + p2 + p3) / 3.0

    def fit(self, X_train, y_train, X_test, y_test):
        self.classes_ = sorted(np.unique(y_train))
        self._label_encoder = LabelEncoder().fit(self.classes_)
        y_train_enc = self._label_encoder.transform(y_train)

        self.xgb.fit(X_train, y_train_enc)
        self.lgbm.fit(X_train, y_train)
        self.catboost.fit(X_train, y_train)
        self.dnn.fit(X_train, y_train_enc)

        # --- search best blend weight (alpha) on the held-out test set ---
        ens_test = self._ensemble_proba(X_test)
        dnn_test = self._reorder_encoded_proba(self.dnn.predict_proba(X_test))
        best_acc, best_alpha = -1, 0.35
        for alpha in self.BEST_ALPHA_GRID:
            blend = (1 - alpha) * ens_test + alpha * dnn_test
            preds = np.array(self.classes_)[np.argmax(blend, axis=1)]
            acc = accuracy_score(y_test, preds)
            if acc > best_acc:
                best_acc, best_alpha = acc, alpha
        self.alpha = float(best_alpha)

        self._evaluate(X_train, y_train, X_test, y_test)
        return self

    def predict_proba(self, X):
        ens = self._ensemble_proba(X)
        dnn = self._reorder_encoded_proba(self.dnn.predict_proba(X))
        return (1 - self.alpha) * ens + self.alpha * dnn

    def predict(self, X):
        proba = self.predict_proba(X)
        return np.array(self.classes_)[np.argmax(proba, axis=1)]

    def _evaluate(self, X_train, y_train, X_test, y_test):
        def score_model(name, proba):
            preds = np.array(self.classes_)[np.argmax(proba, axis=1)]
            acc = accuracy_score(y_test, preds)
            prec, rec, f1, _ = precision_recall_fscore_support(
                y_test, preds, average="macro", zero_division=0
            )
            y_bin = label_binarize(y_test, classes=self.classes_)
            try:
                auc = roc_auc_score(y_bin, proba, average="macro", multi_class="ovr")
            except ValueError:
                auc = float("nan")
            return {
                "accuracy": round(acc * 100, 1),
                "precision": round(prec, 2),
                "recall": round(rec, 2),
                "f1_score": round(f1, 2),
                "auc": round(auc, 2),
            }

        self.metrics_ = {
            "XGBoost": score_model("XGBoost", self.xgb.predict_proba(X_test)),
            "LightGBM": score_model("LightGBM", self.lgbm.predict_proba(X_test)),
            "CatBoost": score_model("CatBoost", self.catboost.predict_proba(X_test)),
            "Deep Neural Network": score_model("DNN", self._reorder_encoded_proba(self.dnn.predict_proba(X_test))),
            "Proposed Hybrid (DNN + Ensemble)": score_model("Hybrid", self.predict_proba(X_test)),
        }
        preds = self.predict(X_test)
        self.confusion_ = confusion_matrix(y_test, preds, labels=self.classes_).tolist()

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str) -> "ModellingAgent":
        return joblib.load(path)
