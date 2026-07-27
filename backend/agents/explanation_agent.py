"""
explanation_agent.py
---------------------
Agent 3: Clinical Interpretation & Explanation Agent

Uses Groq's hosted LLaMA-3.1-8b-instant (matches the paper) to turn a raw
prediction into a clinician-readable narrative: case summary, key risk
factors, clinical considerations, and a conclusion.

Get a free Groq API key at https://console.groq.com/keys and set it as
an environment variable:

    export GROQ_API_KEY="your_key_here"

If no key is set, this agent automatically falls back to a rule-based
template generator so the whole system still runs end-to-end without
any paid/external API -- useful for demos, offline dev, or if your key
runs out of free quota.
"""

import os
import json

GROQ_MODEL = "llama-3.1-8b-instant"
_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
        _groq_client = Groq(api_key=api_key)
        return _groq_client
    except ImportError:
        return None


SYSTEM_PROMPT = """You are a clinical microbiology assistant embedded in an \
Antimicrobial Resistance (AMR) prediction dashboard. Given a model's \
prediction and the patient/organism data behind it, write a SHORT, \
clinically useful interpretation for a treating clinician. Respond ONLY \
with valid JSON in this exact shape, no markdown fences, no extra text:

{
  "case_summary": "one sentence describing the patient and organism",
  "key_risk_factors": ["2-4 short bullet strings"],
  "clinical_considerations": ["2-4 short bullet strings with actionable guidance"],
  "conclusion": "one to two sentence clinical conclusion"
}

Be concise, evidence-grounded in the data given, and never invent a specific \
drug efficacy statistic that wasn't implied by the input."""


class ExplanationAgent:
    """Generates a clinician-readable narrative for a prediction."""

    def explain(self, record: dict, prediction: str, confidence: dict) -> dict:
        client = _get_groq_client()
        if client is not None:
            try:
                return self._explain_with_llm(client, record, prediction, confidence)
            except Exception:
                pass  # fall through to rule-based backup
        return self._explain_rule_based(record, prediction, confidence)

    def _explain_with_llm(self, client, record, prediction, confidence):
        user_prompt = (
            f"Prediction: {prediction}\n"
            f"Confidence breakdown: {json.dumps(confidence)}\n"
            f"Patient & organism data: {json.dumps(record)}\n"
        )
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        text = resp.choices[0].message.content.strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

    def _explain_rule_based(self, record, prediction, confidence) -> dict:
        """Deterministic fallback: no external API required."""
        organism = record.get("organism_group", "the organism")
        infection = record.get("infection_type", "an infection")
        age = record.get("age", "unknown age")
        hosp = record.get("hospitalization_status", "unknown setting")
        gene = record.get("genomic_mutation_marker", "none")
        prev_abx = record.get("previous_antibiotic_use", "No")
        prev_amr = record.get("previous_amr_history", "No")

        risk_factors = []
        if prev_abx == "Yes":
            risk_factors.append("History of previous antibiotic use")
        if prev_amr == "Yes":
            risk_factors.append("Prior AMR history on record")
        if hosp == "ICU":
            risk_factors.append("ICU hospitalization status")
        elif hosp == "Inpatient":
            risk_factors.append("Inpatient hospitalization status")
        if gene and gene != "none":
            risk_factors.append(f"Genomic resistance marker detected: {gene}")
        if not risk_factors:
            risk_factors.append("No major clinical risk factors flagged in the input data")

        considerations = []
        if prediction == "Resistant":
            considerations.append("Standard first-line therapy may fail; consider susceptibility-guided alternatives")
            considerations.append("Consult local antibiogram before finalizing antibiotic choice")
        elif prediction == "Intermediate":
            considerations.append("Monitor closely for treatment failure and adjust plan accordingly")
            considerations.append("Consider higher-dose regimens or combination therapy where clinically appropriate")
        else:
            considerations.append("Standard treatment protocol is likely to be effective")
            considerations.append("Continue routine monitoring; no escalation indicated at this time")

        top_class = max(confidence, key=confidence.get)
        conf_pct = round(confidence[top_class] * 100, 1)

        return {
            "case_summary": (
                f"{age}-year-old patient with a {organism} {infection}, "
                f"{hosp.lower()} status, predicted to be {prediction}."
            ),
            "key_risk_factors": risk_factors,
            "clinical_considerations": considerations,
            "conclusion": (
                f"The model predicts {prediction} with {conf_pct}% confidence based on organism "
                f"profile and clinical history; correlate with local susceptibility data before "
                f"finalizing treatment."
            ),
        }

    def chat(self, question: str, context: dict) -> str:
        """Powers the 'Expert Consultation' follow-up chatbot."""
        client = _get_groq_client()
        if client is not None:
            try:
                resp = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": (
                            "You are an AMR expert-consultation assistant. Answer the "
                            "clinician's follow-up question using ONLY the case context "
                            "provided. Be concise (2-4 sentences), factual, and never invent "
                            "data not present in the context."
                        )},
                        {"role": "user", "content": f"Case context: {json.dumps(context)}\n\nQuestion: {question}"},
                    ],
                    temperature=0.3,
                    max_tokens=300,
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                pass
        return (
            f"Based on the case data, the prediction of "
            f"{context.get('prediction', 'the current class')} reflects the organism's "
            f"typical resistance profile combined with the clinical risk factors on file. "
            f"For a definitive answer to \"{question}\", correlate with laboratory "
            f"susceptibility testing and your local antibiogram."
        )
