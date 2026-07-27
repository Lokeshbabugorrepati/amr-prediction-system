import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const MODEL_COLORS = {
  XGBoost: "#8FA6A1",
  LightGBM: "#8FA6A1",
  CatBoost: "#8FA6A1",
  "Deep Neural Network": "#8FA6A1",
  "Proposed Hybrid (DNN + Ensemble)": "#0F6E5C",
};

export default function ModelPerformance({ apiBase }) {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${apiBase}/api/metrics`)
      .then((r) => r.json())
      .then(setMetrics)
      .catch(() => setError("Could not load metrics. Is the backend running?"));
  }, [apiBase]);

  if (error) return <p className="text-sm text-resistant">{error}</p>;
  if (!metrics) return <p className="text-sm text-inksoft">Loading model performance…</p>;

  const table = metrics.table;
  const chartData = Object.entries(table).map(([name, m]) => ({
    name: name.replace("Proposed Hybrid (DNN + Ensemble)", "Hybrid (Proposed)"),
    accuracy: m.accuracy,
    auc: m.auc * 100,
  }));

  const classes = metrics.classes;
  const confusion = metrics.confusion_matrix;

  return (
    <div className="flex flex-col gap-6 fade-up">
      <div>
        <h2 className="font-display text-2xl text-ink mb-1">Model Performance</h2>
        <p className="text-sm text-inksoft">
          Evaluated on a held-out 20% stratified test split. Blend weight (α) found via grid search: {metrics.blend_alpha}
        </p>
      </div>

      {/* Table */}
      <div className="border border-border rounded-lg bg-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-bg">
              <th className="text-left px-4 py-2.5 font-medium text-inksoft">Model</th>
              <th className="text-right px-4 py-2.5 font-medium text-inksoft">Accuracy</th>
              <th className="text-right px-4 py-2.5 font-medium text-inksoft">Precision</th>
              <th className="text-right px-4 py-2.5 font-medium text-inksoft">Recall</th>
              <th className="text-right px-4 py-2.5 font-medium text-inksoft">F1-Score</th>
              <th className="text-right px-4 py-2.5 font-medium text-inksoft">AUC</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(table).map(([name, m]) => (
              <tr key={name} className={`border-b border-border last:border-0 ${name.startsWith("Proposed") ? "bg-accentsoft" : ""}`}>
                <td className="px-4 py-2.5 font-medium text-ink">{name}</td>
                <td className="px-4 py-2.5 text-right font-mono">{m.accuracy}%</td>
                <td className="px-4 py-2.5 text-right font-mono">{m.precision}</td>
                <td className="px-4 py-2.5 text-right font-mono">{m.recall}</td>
                <td className="px-4 py-2.5 text-right font-mono">{m.f1_score}</td>
                <td className="px-4 py-2.5 text-right font-mono">{m.auc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Accuracy chart */}
      <div className="border border-border rounded-lg bg-panel p-4">
        <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-3">
          Accuracy Comparison
        </p>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} margin={{ left: -10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D8E0DF" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#4B5D59" }} interval={0} angle={-15} textAnchor="end" height={70} />
            <YAxis domain={[70, 100]} tick={{ fontSize: 11, fill: "#4B5D59" }} unit="%" />
            <Tooltip />
            <Bar dataKey="accuracy" radius={[4, 4, 0, 0]}>
              {chartData.map((d, i) => (
                <Cell key={i} fill={d.name === "Hybrid (Proposed)" ? "#0F6E5C" : "#B7C7C3"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Confusion matrix */}
      <div className="border border-border rounded-lg bg-panel p-4">
        <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-3">
          Confusion Matrix — Hybrid Model
        </p>
        <div className="overflow-x-auto">
          <table className="text-sm mx-auto">
            <thead>
              <tr>
                <th></th>
                {classes.map((c) => (
                  <th key={c} className="px-3 py-1.5 text-xs font-medium text-inksoft">{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {confusion.map((row, ri) => (
                <tr key={ri}>
                  <td className="px-3 py-1.5 text-xs font-medium text-inksoft text-right">{classes[ri]}</td>
                  {row.map((val, ci) => {
                    const isDiagonal = ri === ci;
                    const max = Math.max(...row);
                    const intensity = val === 0 ? 0 : val / (max || 1);
                    return (
                      <td key={ci} className="px-3 py-1.5 text-center font-mono text-sm">
                        <div
                          className="w-14 h-10 flex items-center justify-center rounded-md mx-auto"
                          style={{
                            backgroundColor: isDiagonal
                              ? `rgba(15,110,92,${0.15 + intensity * 0.5})`
                              : `rgba(196,67,43,${intensity * 0.25})`,
                            color: "#10241F",
                          }}
                        >
                          {val}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-inksoft text-center mt-3">Rows = actual class · Columns = predicted class</p>
        </div>
      </div>
    </div>
  );
}
