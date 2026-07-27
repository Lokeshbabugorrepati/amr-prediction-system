const STATUS_STYLES = {
  Resistant: { text: "text-resistant", bg: "bg-resistantsoft", bar: "bg-resistant" },
  Intermediate: { text: "text-intermediate", bg: "bg-intermediatesoft", bar: "bg-intermediate" },
  Susceptible: { text: "text-susceptible", bg: "bg-susceptiblesoft", bar: "bg-susceptible" },
};

export default function ResultPanel({ result }) {
  if (!result) {
    return (
      <div className="border border-dashed border-border rounded-lg py-16 px-6 text-center">
        <p className="font-display text-lg text-ink mb-1">No case processed yet</p>
        <p className="text-sm text-inksoft max-w-sm mx-auto">
          Fill in the patient and organism details on the left, then run the
          prediction. The four agents will process the case and return a
          classification with a clinician-readable explanation.
        </p>
      </div>
    );
  }

  const { prediction, confidence, explanation, inference_time_seconds } = result;
  const style = STATUS_STYLES[prediction] || STATUS_STYLES.Susceptible;
  const sortedConf = Object.entries(confidence).sort((a, b) => b[1] - a[1]);

  return (
    <div className="flex flex-col gap-4 fade-up">
      {/* Headline result */}
      <div className={`rounded-lg ${style.bg} border border-border px-5 py-4 flex items-center justify-between`}>
        <div>
          <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-1">
            Prediction Result
          </p>
          <p className={`font-display text-3xl font-semibold ${style.text}`}>
            {prediction}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-inksoft font-mono">Inference time</p>
          <p className="text-sm font-mono text-ink">{inference_time_seconds}s</p>
        </div>
      </div>

      {/* Confidence bars */}
      <div className="border border-border rounded-lg bg-panel p-4">
        <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-3">
          Confidence Breakdown
        </p>
        <div className="flex flex-col gap-2.5">
          {sortedConf.map(([cls, val]) => {
            const s = STATUS_STYLES[cls] || STATUS_STYLES.Susceptible;
            return (
              <div key={cls} className="flex items-center gap-3">
                <span className={`w-24 text-xs font-medium ${s.text}`}>{cls}</span>
                <div className="flex-1 h-2.5 rounded-full bg-bg overflow-hidden">
                  <div
                    className={`h-full ${s.bar} rounded-full transition-all duration-700`}
                    style={{ width: `${Math.max(val * 100, 2)}%` }}
                  />
                </div>
                <span className="w-12 text-right text-xs font-mono text-inksoft">
                  {(val * 100).toFixed(1)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Clinical interpretation */}
      <div className="border border-border rounded-lg bg-panel p-4">
        <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-3">
          Clinical Interpretation
        </p>
        <p className="text-sm text-ink mb-4 leading-relaxed">
          {explanation.case_summary}
        </p>

        <p className="text-xs font-semibold text-inksoft mb-1.5">Key Risk Factors</p>
        <ul className="mb-4 space-y-1">
          {explanation.key_risk_factors.map((r, i) => (
            <li key={i} className="text-sm text-ink flex gap-2">
              <span className="text-accent">▸</span>{r}
            </li>
          ))}
        </ul>

        <p className="text-xs font-semibold text-inksoft mb-1.5">Clinical Considerations</p>
        <ul className="mb-4 space-y-1">
          {explanation.clinical_considerations.map((r, i) => (
            <li key={i} className="text-sm text-ink flex gap-2">
              <span className="text-accent">▸</span>{r}
            </li>
          ))}
        </ul>

        <div className="border-t border-border pt-3">
          <p className="text-xs font-semibold text-inksoft mb-1">Conclusion</p>
          <p className="text-sm text-ink leading-relaxed">{explanation.conclusion}</p>
        </div>
      </div>
    </div>
  );
}
