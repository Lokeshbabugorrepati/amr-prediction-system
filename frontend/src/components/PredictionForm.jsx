import { useState } from "react";

const FIELD_GROUPS = (options) => [
  {
    title: "Patient",
    fields: [
      { name: "age", label: "Age", type: "number", min: 0, max: 120 },
      { name: "age_group", label: "Age Group", type: "select", opts: options.age_group },
      { name: "hospitalization_status", label: "Hospitalization Status", type: "select", opts: options.hospitalization_status },
      { name: "prior_hospitalization_days", label: "Prior Hospitalization (days)", type: "number", min: 0, max: 60 },
    ],
  },
  {
    title: "Infection",
    fields: [
      { name: "infection_type", label: "Infection Type", type: "select", opts: options.infection_type },
      { name: "sample_collection_site", label: "Sample Collection Site", type: "select", opts: options.sample_collection_site },
      { name: "specimen_source", label: "Specimen Source", type: "select", opts: ["Community-acquired", "Hospital-acquired"] },
      { name: "geographic_region", label: "Geographic Region", type: "select", opts: ["North", "South", "East", "West", "Central"] },
    ],
  },
  {
    title: "Organism & Genomics",
    fields: [
      { name: "organism_group", label: "Organism Group", type: "select", opts: options.organism_group },
      { name: "genomic_mutation_marker", label: "Genomic Mutation Marker", type: "select", opts: options.genomic_mutation_marker },
      { name: "num_amr_genes_detected", label: "AMR Genes Detected (count)", type: "number", min: 0, max: 12 },
      { name: "mic_value_mg_l", label: "MIC Value (mg/L)", type: "number", step: "0.1", min: 0 },
      { name: "gc_content_pct", label: "GC Content (%)", type: "number", step: "0.1" },
      { name: "genome_size_mb", label: "Genome Size (Mb)", type: "number", step: "0.1" },
      { name: "plasmid_count", label: "Plasmid Count", type: "number", min: 0, max: 6 },
      { name: "sequence_coverage_x", label: "Sequence Coverage (x)", type: "number" },
      { name: "biofilm_formation", label: "Biofilm Formation", type: "select", opts: options.yes_no },
      { name: "efflux_pump_activity", label: "Efflux Pump Activity", type: "select", opts: options.yes_no },
      { name: "beta_lactamase_production", label: "Beta-lactamase Production", type: "select", opts: options.yes_no },
      { name: "porin_loss_mutation", label: "Porin Loss Mutation", type: "select", opts: options.yes_no },
    ],
  },
  {
    title: "Treatment History",
    fields: [
      { name: "previous_antibiotic_use", label: "Previous Antibiotic Use", type: "select", opts: options.yes_no },
      { name: "previous_amr_history", label: "Previous AMR History", type: "select", opts: options.yes_no },
      { name: "resistance_to_previous_treatment", label: "Resistance to Previous Treatment", type: "select", opts: options.yes_no },
      { name: "treatment_duration_days", label: "Treatment Duration (days)", type: "number", min: 0, max: 90 },
    ],
  },
];

const DEFAULTS = {
  age: 45,
  age_group: "41-60",
  hospitalization_status: "Inpatient",
  prior_hospitalization_days: 3,
  infection_type: "UTI",
  sample_collection_site: "Urine",
  specimen_source: "Community-acquired",
  geographic_region: "Central",
  organism_group: "E.coli",
  genomic_mutation_marker: "none",
  num_amr_genes_detected: 1,
  mic_value_mg_l: 4,
  gc_content_pct: 50,
  genome_size_mb: 4.6,
  plasmid_count: 1,
  sequence_coverage_x: 80,
  biofilm_formation: "No",
  efflux_pump_activity: "No",
  beta_lactamase_production: "No",
  porin_loss_mutation: "No",
  previous_antibiotic_use: "No",
  previous_amr_history: "No",
  resistance_to_previous_treatment: "No",
  treatment_duration_days: 5,
};

export default function PredictionForm({ options, onSubmit, isRunning }) {
  const [values, setValues] = useState(DEFAULTS);
  const [openGroup, setOpenGroup] = useState(0);

  const update = (name, val) => setValues((v) => ({ ...v, [name]: val }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(values);
  };

  const groups = FIELD_GROUPS(options);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      {groups.map((group, gi) => (
        <div key={group.title} className="border border-border rounded-lg bg-panel overflow-hidden">
          <button
            type="button"
            onClick={() => setOpenGroup(openGroup === gi ? -1 : gi)}
            className="w-full flex items-center justify-between px-4 py-3 text-left"
          >
            <span className="font-display text-[15px] text-ink">{group.title}</span>
            <span className="text-inksoft text-sm font-mono">
              {openGroup === gi ? "−" : "+"}
            </span>
          </button>
          {openGroup === gi && (
            <div className="px-4 pb-4 grid grid-cols-2 gap-3 fade-up">
              {group.fields.map((f) => (
                <label key={f.name} className="flex flex-col gap-1 text-xs">
                  <span className="text-inksoft font-medium">{f.label}</span>
                  {f.type === "select" ? (
                    <select
                      value={values[f.name]}
                      onChange={(e) => update(f.name, e.target.value)}
                      className="border border-border rounded-md px-2 py-1.5 bg-white text-ink text-sm focus:border-accent"
                    >
                      {(f.opts || []).map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="number"
                      value={values[f.name]}
                      min={f.min}
                      max={f.max}
                      step={f.step || 1}
                      onChange={(e) => update(f.name, Number(e.target.value))}
                      className="border border-border rounded-md px-2 py-1.5 bg-white text-ink text-sm focus:border-accent font-mono"
                    />
                  )}
                </label>
              ))}
            </div>
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={isRunning}
        className="mt-1 bg-accent hover:bg-[#0b5947] disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium rounded-lg py-3 transition-colors"
      >
        {isRunning ? "Running assay…" : "Run AMR Prediction"}
      </button>
    </form>
  );
}
