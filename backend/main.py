"""
main.py
--------
FastAPI backend for the AMR Insight Platform.

This file is intentionally thin: it validates incoming requests and
delegates everything else to the Orchestrator Agent, which is the only
component that talks to Preprocessing / Modelling / Explanation agents.

Run (from the backend/ folder):
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from agents.orchestrator import OrchestratorAgent
from agents.preprocessing_agent import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from data.generate_dataset import (
    ORGANISM_GROUPS, INFECTION_TYPES, SAMPLE_SITES, HOSPITALIZATION,
    YES_NO, AGE_GROUPS, GENE_MARKERS,
)

app = FastAPI(title="AMR Insight Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's origin before deploying publicly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent(
    preprocessing_path="models/preprocessing_agent.joblib",
    modelling_path="models/modelling_agent.joblib",
)


class PredictionRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    age_group: str
    organism_group: str
    infection_type: str
    sample_collection_site: str
    hospitalization_status: str
    previous_antibiotic_use: str
    previous_amr_history: str
    treatment_duration_days: int = Field(..., ge=0, le=90)
    resistance_to_previous_treatment: str
    genomic_mutation_marker: str
    mic_value_mg_l: Optional[float] = 4.0
    gc_content_pct: Optional[float] = 50.0
    genome_size_mb: Optional[float] = 4.6
    num_amr_genes_detected: Optional[int] = 1
    plasmid_count: Optional[int] = 1
    sequence_coverage_x: Optional[int] = 80
    biofilm_formation: Optional[str] = "No"
    efflux_pump_activity: Optional[str] = "No"
    beta_lactamase_production: Optional[str] = "No"
    porin_loss_mutation: Optional[str] = "No"
    geographic_region: Optional[str] = "Central"
    specimen_source: Optional[str] = "Community-acquired"
    prior_hospitalization_days: Optional[int] = 0


class ChatRequest(BaseModel):
    question: str
    context: dict


@app.get("/")
def root():
    return {"status": "ok", "service": "AMR Insight Platform API"}


@app.get("/api/form-options")
def form_options():
    """Populates every dropdown in the React form -- single source of truth."""
    return {
        "organism_group": ORGANISM_GROUPS,
        "infection_type": INFECTION_TYPES,
        "sample_collection_site": SAMPLE_SITES,
        "hospitalization_status": HOSPITALIZATION,
        "yes_no": YES_NO,
        "age_group": AGE_GROUPS,
        "genomic_mutation_marker": GENE_MARKERS,
    }


@app.post("/api/predict")
def predict(req: PredictionRequest):
    try:
        result = orchestrator.run_prediction(req.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        answer = orchestrator.run_chat(req.question, req.context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
def metrics():
    try:
        return orchestrator.model_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
