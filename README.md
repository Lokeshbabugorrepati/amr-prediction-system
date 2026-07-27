# AMR Insight Platform

**An Agentic AI system that predicts Antimicrobial Resistance (AMR) from combined genomic and clinical patient data — built as a 4-agent pipeline with a hybrid ML model and an LLM-powered clinical interpretation layer.**

🔗 **[Live Demo](https://amr-prediction-system.vercel.app)** — try it yourself (no signup required)
> Note: the backend runs on a free-tier server that sleeps after inactivity. The first prediction after a period of no traffic may take 30–50 seconds to respond while it wakes up — subsequent requests are fast (typically well under 1 second).

> Antimicrobial Resistance is one of the World Health Organization's top global health threats — bacteria evolving to resist the drugs used to treat them. This project automates the classification of a bacterial isolate as **Resistant**, **Intermediate**, or **Susceptible**, by combining genomic markers with patient clinical history — something most existing ML approaches don't do — and explains *why* in plain clinical language instead of returning an unexplained label.

---

## Table of Contents

- [Overview](#overview)
- [Live Demo / Screenshots](#live-demo--screenshots)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Model Performance](#model-performance)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

Traditional AMR detection relies on lab culture testing, which is accurate but slow — often taking days a critically ill patient doesn't have. Existing ML approaches that try to speed this up typically have two weaknesses: they use *either* genomic *or* clinical data (rarely both), and they behave as black boxes, giving clinicians a label with no reasoning behind it.

**AMR Insight Platform** addresses both problems:

- **Fuses genomic + clinical data** — organism genotype, resistance-gene markers, MIC values, and sequencing metadata alongside patient age, hospitalization status, infection type, and treatment history — into a single prediction.
- **Explains every prediction** — a dedicated LLM agent (LLaMA 3.1 via Groq) turns the raw classification into a clinician-readable narrative: case summary, key risk factors, clinical considerations, and a conclusion.
- **Is built as a true multi-agent system**, not a single script — four independent agents (Preprocessing, Modelling, Clinical Interpretation, Orchestrator) each own one responsibility and hand off to the next, coordinated end-to-end.

This project is a full-stack implementation inspired by the architecture proposed in *"An Agentic AI-based Multi-Class Classification Framework for Predicting Antimicrobial Resistance from Genomic and Clinical Data"* (ICICI-2026).

---

## Live Demo / Screenshots

| Prediction Dashboard | Model Performance |
|---|---|
| *Add a screenshot of the Predict tab here* | *Add a screenshot of the Model Performance tab here* |

> Tip: drag screenshots directly into this README on GitHub's web editor, or reference `docs/screenshots/*.png` if you add an images folder.

---

## Architecture

```
                              ┌─────────────────────────────┐
                              │      Orchestrator Agent      │
                              │  (coordinates the pipeline)  │
                              └───────────────┬───────────────┘
                                              │
        ┌─────────────────────┬──────────────┴──────────────┬─────────────────────┐
        ▼                     ▼                              ▼                     
┌───────────────┐   ┌──────────────────┐          ┌───────────────────────┐
│  Preprocessing │   │    Modelling     │          │  Clinical Interpretation│
│      Agent     │──▶│      Agent       │─────────▶│         Agent          │
│                │   │                  │          │                         │
│ Clean → Encode │   │ XGBoost +        │          │ LLaMA 3.1 via Groq      │
│ → Scale →      │   │ LightGBM +       │          │ generates a clinician-  │
│ SMOTE balance  │   │ CatBoost + DNN   │          │ readable narrative      │
│                │   │ blended hybrid   │          │                         │
└────────────────┘   └──────────────────┘          └───────────────────────┘
                                              │
                                              ▼
                              ┌─────────────────────────────┐
                              │   FastAPI REST layer         │
                              │  /api/predict  /api/chat     │
                              │  /api/metrics  /api/form-... │
                              └───────────────┬───────────────┘
                                              │
                                              ▼
                              ┌─────────────────────────────┐
                              │   React Dashboard (Vite)     │
                              │  Prediction form · Results   │
                              │  panel · Expert chat ·       │
                              │  Model performance charts    │
                              └─────────────────────────────┘
```

**Why this shape, and not one monolithic script?** Separating each responsibility into its own agent module mirrors how the underlying research paper frames the system (data preprocessing, modelling, and clinical interpretation are described as independent LangChain-style agents coordinated by an orchestrator), and it means each piece — the ML model, the LLM explanation layer, the API, the UI — can be modified, tested, or swapped independently.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **ML models** | XGBoost, LightGBM, CatBoost | Gradient-boosted ensemble learners on structured genomic + clinical features |
| **Deep learning** | scikit-learn `MLPClassifier` | Dense neural network component (512→256), blended with the ensemble output |
| **Class balancing** | imbalanced-learn (SMOTE) | Synthetic oversampling to correct class imbalance before training |
| **Preprocessing** | scikit-learn (`StandardScaler`, `OneHotEncoder`) | Z-score normalization + one-hot encoding of categorical features |
| **LLM** | LLaMA 3.1-8B-Instant via **Groq API** | Generates clinician-readable explanations and answers follow-up questions |
| **Backend framework** | FastAPI (Python) | REST API serving predictions, chat, and metrics |
| **Server** | Uvicorn | ASGI server for FastAPI |
| **Frontend framework** | React 18 + Vite | Component-based interactive dashboard |
| **Styling** | Tailwind CSS | Custom clinical design system (utility-first CSS) |
| **Charts** | Recharts | Accuracy comparison chart, confusion matrix visualization |
| **Data handling** | pandas, NumPy | Dataset generation, feature engineering |
| **Serialization** | joblib | Persisting trained model + preprocessing artifacts |
| **Deployment** | Render (backend) + Vercel (frontend) | Live hosting — see [Live Demo](#live-demo--screenshots) above |

---

## Model Performance

Evaluated on a held-out 20% stratified test split (SMOTE-balanced training set):

| Model | Accuracy | Precision | Recall | F1-Score | AUC |
|---|---|---|---|---|---|
| XGBoost | 89.7% | 0.89 | 0.89 | 0.89 | 0.97 |
| LightGBM | 90.2% | 0.90 | 0.90 | 0.90 | 0.97 |
| CatBoost | 89.9% | 0.90 | 0.90 | 0.90 | 0.97 |
| Deep Neural Network | 86.7% | 0.87 | 0.87 | 0.87 | 0.97 |
| **Proposed Hybrid (DNN + Ensemble)** | **91.3%** | **0.91** | **0.91** | **0.91** | **0.98** |

The hybrid model — a weighted blend of the gradient-boosting ensemble and the neural network, with the blend weight found via grid search — outperforms every individual model, consistent with the pattern reported in the reference paper.

The confusion matrix shows the model's main confusion is between **Intermediate** and **Resistant** classes, which realistically share overlapping genomic risk markers — the same finding the reference paper reports.

---

## Project Structure

```
amr-prediction-system/
├── backend/
│   ├── data/
│   │   ├── generate_dataset.py     # builds the synthetic training dataset
│   │   └── amr_dataset.csv         # generated dataset (1,840 samples, 25 features)
│   ├── agents/
│   │   ├── preprocessing_agent.py  # Agent 1 — clean, scale, encode, SMOTE
│   │   ├── modelling_agent.py      # Agent 2 — hybrid ensemble + DNN classifier
│   │   ├── explanation_agent.py    # Agent 3 — LLM clinical interpretation
│   │   └── orchestrator.py         # Agent 4 — coordinates the full pipeline
│   ├── models/                     # saved trained model artifacts (.joblib)
│   ├── train_model.py              # trains the model and saves artifacts
│   ├── main.py                     # FastAPI application + REST endpoints
│   ├── requirements.txt
│   └── .env.example                # Groq API key template
└── frontend/
    ├── src/
    │   ├── App.jsx                 # layout, tab navigation, pipeline orchestration
    │   ├── index.css               # design tokens, global styles
    │   └── components/
    │       ├── PredictionForm.jsx  # patient/organism input form
    │       ├── AgentPipeline.jsx   # animated 4-agent processing visualization
    │       ├── ResultPanel.jsx     # prediction result + confidence + explanation
    │       ├── ExpertChat.jsx      # follow-up Q&A chatbot
    │       └── ModelPerformance.jsx # metrics table, charts, confusion matrix
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## Getting Started

### Prerequisites

- **Python 3.11 or 3.12** (⚠️ Python 3.13/3.14 will fail — numpy/xgboost/lightgbm/catboost don't yet ship pre-built wheels for the newest Python releases)
- **Node.js 18+** and npm
- A free [Groq API key](https://console.groq.com/keys) (optional — the app runs fully without one, using a rule-based explanation fallback)

### 1. Backend setup

```bash
cd backend
python -m venv venv

# Activate the virtual environment
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows PowerShell

pip install -r requirements.txt
```

Generate the dataset and train the model (artifacts are saved to `models/`):

```bash
cd data
python generate_dataset.py
cd ..
python train_model.py
```

*(Optional)* enable real LLM-generated explanations:

```bash
cp .env.example .env       # then paste your Groq key inside .env

# then, in the same terminal session, before starting the server:
export GROQ_API_KEY="your_key_here"     # macOS/Linux
$env:GROQ_API_KEY = "your_key_here"     # Windows PowerShell
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation (auto-generated by FastAPI).

### 2. Frontend setup (in a new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (typically `http://localhost:5173`).

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/form-options` | Returns dropdown values for the prediction form (organism types, infection types, etc.) |
| `POST` | `/api/predict` | Runs the full 4-agent pipeline on a patient/organism record and returns a classification, confidence scores, and clinical explanation |
| `POST` | `/api/chat` | Follow-up question answering for the Expert Consultation chatbot, grounded in the current case context |
| `GET` | `/api/metrics` | Returns model performance metrics (accuracy/precision/recall/F1/AUC per model) and the confusion matrix |

Example `/api/predict` request body:

```json
{
  "age": 68,
  "age_group": "61-80",
  "organism_group": "Pseudomonas aeruginosa",
  "infection_type": "Pneumonia",
  "sample_collection_site": "Sputum",
  "hospitalization_status": "ICU",
  "previous_antibiotic_use": "Yes",
  "previous_amr_history": "Yes",
  "treatment_duration_days": 10,
  "resistance_to_previous_treatment": "Yes",
  "genomic_mutation_marker": "NDM-1",
  "num_amr_genes_detected": 6
}
```

---

## Design Decisions

Notes on a few implementation choices, useful context if this comes up in a technical interview:

- **Synthetic dataset**: NCBI's Pathogen Detection Isolates Browser doesn't provide one clean downloadable file matching the paper's exact 25-feature schema, so `generate_dataset.py` builds a dataset with the same schema and realistic epidemiological correlations (e.g. ICU stay + prior antibiotic use + high-risk organism → higher resistance probability). Swapping in a real, licensed dataset only requires changing the data loading step in `train_model.py` — no other file needs to change.
- **DNN component**: the reference paper uses a Keras/TensorFlow feed-forward network. This implementation uses scikit-learn's `MLPClassifier` (512→256 dense layers, ReLU activation, early stopping) to keep the dependency footprint lightweight — architecturally the same role, without requiring a full TensorFlow install.
- **LLM fallback**: if no `GROQ_API_KEY` is set, `explanation_agent.py` automatically falls back to a deterministic rule-based narrative generator, so the entire system — including the frontend demo — still runs end-to-end without any external API dependency.
- **Separate FastAPI + React services** (rather than a single Streamlit app): mirrors the microservice-style separation implied by the paper's architecture — agents/orchestrator as a backend service, dashboard as an independent client — which is both a closer match to the source architecture and a stronger engineering signal than a single-file app.

---

## Roadmap

- [ ] SHAP-based feature importance visualization for deeper per-prediction explainability
- [ ] Persistent case history (MongoDB) so predictions can be reviewed later
- [ ] Swap synthetic data for a licensed real-world AMR dataset
- [ ] Docker Compose setup for one-command local deployment
- [ ] Production deployment (backend → Render/Railway, frontend → Vercel)
- [ ] Authentication for multi-user clinical use

---

## License

This project was built for educational and portfolio purposes. Feel free to fork, adapt, and build on it.