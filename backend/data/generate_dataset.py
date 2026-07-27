"""
generate_dataset.py
--------------------
Generates a synthetic (but realistically-structured) Antimicrobial
Resistance dataset that mirrors the feature set described in the
reference paper: genomic + clinical features -> Resistant / Intermediate
/ Susceptible.

Why synthetic data? The NCBI Pathogen Detection Isolates Browser does not
offer a single clean downloadable CSV with all 25 paper-described
features, and scraping it is unreliable for a resume project. This
script builds a dataset with the SAME schema and realistic correlations
(e.g. previous antibiotic use + ICU stay -> higher resistance
probability) so the ML pipeline, agents, and UI all behave exactly like
they would on real data. Swap this file out for a real CSV loader later
if you get access to a licensed AMR dataset -- the rest of the pipeline
does not need to change.

Run:
    python generate_dataset.py
Produces:
    amr_dataset.csv  (1840 rows, 25 feature columns + target)
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_SAMPLES = 1840

ORGANISM_GROUPS = [
    "E.coli", "Klebsiella pneumoniae", "Staphylococcus aureus",
    "Pseudomonas aeruginosa", "Acinetobacter baumannii",
    "Enterococcus faecium", "Salmonella", "Shigella",
    "Campylobacter jejuni", "Streptococcus pneumoniae",
]
INFECTION_TYPES = ["UTI", "Bloodstream Infection (BSI)", "Pneumonia", "Wound Infection", "GI Infection"]
SAMPLE_SITES = ["Blood", "Urine", "Sputum", "Wound Swab", "Stool"]
HOSPITALIZATION = ["Outpatient", "Inpatient", "ICU"]
YES_NO = ["Yes", "No"]
AGE_GROUPS = ["0-18", "19-40", "41-60", "61-80", "80+"]

# Organism-level base resistance propensity (mirrors real epidemiology
# roughly -- ESKAPE-type organisms trend more resistant)
ORGANISM_RISK = {
    "E.coli": 0.35, "Klebsiella pneumoniae": 0.55, "Staphylococcus aureus": 0.45,
    "Pseudomonas aeruginosa": 0.60, "Acinetobacter baumannii": 0.65,
    "Enterococcus faecium": 0.50, "Salmonella": 0.30, "Shigella": 0.30,
    "Campylobacter jejuni": 0.25, "Streptococcus pneumoniae": 0.30,
}
HOSPITALIZATION_RISK = {"Outpatient": 0.0, "Inpatient": 0.12, "ICU": 0.25}

GENE_MARKERS = ["blaCTX-M", "blaKPC", "mecA", "vanA", "gyrA(Ser83Leu)",
                 "parC(Ser80Ile)", "ampC", "NDM-1", "OXA-48", "none"]


def make_row():
    organism = RNG.choice(ORGANISM_GROUPS)
    hosp = RNG.choice(HOSPITALIZATION, p=[0.5, 0.35, 0.15])
    prev_abx = RNG.choice(YES_NO, p=[0.4, 0.6])
    prev_amr = RNG.choice(YES_NO, p=[0.25, 0.75])
    age_group = RNG.choice(AGE_GROUPS)
    treatment_duration = int(RNG.integers(1, 15))

    # --- composite resistance score (deterministic signal + small noise) ---
    risk = ORGANISM_RISK[organism]
    risk += HOSPITALIZATION_RISK[hosp]
    risk += 0.15 if prev_abx == "Yes" else 0.0
    risk += 0.20 if prev_amr == "Yes" else 0.0
    risk += 0.05 if age_group in ("61-80", "80+") else 0.0
    risk += RNG.normal(0, 0.04)  # small noise so the model has real signal to learn
    risk = float(np.clip(risk, 0.0, 1.0))

    # clean thresholds -> a learnable but non-trivial 3-class boundary
    if risk >= 0.62:
        label = "Resistant"
    elif risk >= 0.42:
        label = "Intermediate"
    else:
        label = "Susceptible"

    gene = RNG.choice(GENE_MARKERS, p=[0.13, 0.1, 0.12, 0.08, 0.12, 0.12, 0.1, 0.08, 0.1, 0.05])
    if label == "Susceptible" and RNG.random() < 0.5:
        gene = "none"

    return {
        "sample_id": f"AMR{RNG.integers(100000, 999999)}",
        "age": int(np.clip(RNG.normal(45, 20), 1, 95)),
        "age_group": age_group,
        "organism_group": organism,
        "infection_type": RNG.choice(INFECTION_TYPES),
        "sample_collection_site": RNG.choice(SAMPLE_SITES),
        "hospitalization_status": hosp,
        "previous_antibiotic_use": prev_abx,
        "previous_amr_history": prev_amr,
        "treatment_duration_days": treatment_duration,
        "resistance_to_previous_treatment": RNG.choice(YES_NO, p=[0.3, 0.7]),
        "genomic_mutation_marker": gene,
        "mic_value_mg_l": round(float(np.clip(RNG.gamma(2, 4) * (1 + risk), 0.05, 128)), 2),
        "gc_content_pct": round(float(RNG.normal(50, 4)), 2),
        "genome_size_mb": round(float(RNG.normal(4.6, 0.6)), 2),
        "num_amr_genes_detected": int(np.clip(RNG.poisson(1 + risk * 4), 0, 12)),
        "plasmid_count": int(np.clip(RNG.poisson(1.2), 0, 6)),
        "sequence_coverage_x": int(np.clip(RNG.normal(80, 15), 20, 150)),
        "biofilm_formation": RNG.choice(YES_NO, p=[0.35, 0.65]),
        "efflux_pump_activity": RNG.choice(YES_NO, p=[0.3, 0.7]),
        "beta_lactamase_production": RNG.choice(YES_NO, p=[0.3 + risk * 0.3, 0.7 - risk * 0.3]),
        "porin_loss_mutation": RNG.choice(YES_NO, p=[0.2 + risk * 0.2, 0.8 - risk * 0.2]),
        "geographic_region": RNG.choice(["North", "South", "East", "West", "Central"]),
        "specimen_source": RNG.choice(["Community-acquired", "Hospital-acquired"], p=[0.55, 0.45]),
        "prior_hospitalization_days": int(np.clip(RNG.exponential(4), 0, 60)),
        "resistance_status": label,
    }


def main():
    rows = [make_row() for _ in range(N_SAMPLES)]
    df = pd.DataFrame(rows)
    out_path = "amr_dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    print(df["resistance_status"].value_counts())


if __name__ == "__main__":
    main()
