"""
orchestrator.py
-----------------
Agent 4: Orchestrator Agent

Coordinates the full pipeline exactly as described in Section III-D:
  1. Hand the raw record to the Preprocessing Agent
  2. Pass the transformed features to the Modelling Agent for prediction
  3. Pass the prediction + original record to the Explanation Agent
  4. Return one unified response to the API layer

This is intentionally the ONLY place that knows about all three agents --
main.py (the API) never talks to them directly, it only talks to the
orchestrator. That mirrors the paper's architecture diagram (Fig. 1)
where the Orchestrator Agent is the sole coordinator.
"""

import time
from .preprocessing_agent import PreprocessingAgent
from .modelling_agent import ModellingAgent
from .explanation_agent import ExplanationAgent


class OrchestratorAgent:
    def __init__(self, preprocessing_path: str, modelling_path: str):
        self.preprocessor: PreprocessingAgent = PreprocessingAgent.load(preprocessing_path)
        self.modeller: ModellingAgent = ModellingAgent.load(modelling_path)
        self.explainer = ExplanationAgent()

    def run_prediction(self, record: dict) -> dict:
        t0 = time.time()

        # Step 1: Preprocessing Agent
        X = self.preprocessor.transform_single(record)

        # Step 2: Modelling Agent
        proba = self.modeller.predict_proba(X)[0]
        classes = self.modeller.classes_
        confidence = {cls: float(p) for cls, p in zip(classes, proba)}
        prediction = max(confidence, key=confidence.get)

        # Step 3: Clinical Interpretation & Explanation Agent
        explanation = self.explainer.explain(record, prediction, confidence)

        elapsed = round(time.time() - t0, 2)

        return {
            "prediction": prediction,
            "confidence": confidence,
            "explanation": explanation,
            "inference_time_seconds": elapsed,
            "agent_trace": [
                {"agent": "Data Preprocessing Agent", "status": "complete"},
                {"agent": "Modelling Agent", "status": "complete"},
                {"agent": "Clinical Interpretation Agent", "status": "complete"},
                {"agent": "Orchestrator Agent", "status": "complete"},
            ],
        }

    def run_chat(self, question: str, context: dict) -> str:
        return self.explainer.chat(question, context)

    def model_metrics(self) -> dict:
        return {
            "table": self.modeller.metrics_,
            "confusion_matrix": self.modeller.confusion_,
            "classes": self.modeller.classes_,
            "blend_alpha": self.modeller.alpha,
        }
