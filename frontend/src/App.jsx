import { useEffect, useState, useRef } from "react";
import PredictionForm from "./components/PredictionForm.jsx";
import AgentPipeline from "./components/AgentPipeline.jsx";
import ResultPanel from "./components/ResultPanel.jsx";
import ExpertChat from "./components/ExpertChat.jsx";
import ModelPerformance from "./components/ModelPerformance.jsx";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [tab, setTab] = useState("predict");
  const [options, setOptions] = useState(null);
  const [result, setResult] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState("idle");
  const [activeIndex, setActiveIndex] = useState(0);
  const [lastRecord, setLastRecord] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const timers = useRef([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/form-options`)
      .then((r) => r.json())
      .then(setOptions)
      .catch(() => setErrorMsg("Could not reach backend at localhost:8000. Start it with: uvicorn main:app --reload"));
  }, []);

  const runPrediction = async (values) => {
    setErrorMsg(null);
    setResult(null);
    setPipelineStatus("running");
    setActiveIndex(0);
    timers.current.forEach(clearTimeout);
    timers.current = [];

    // stage the pipeline visualization while the real request is in flight
    timers.current.push(setTimeout(() => setActiveIndex(1), 350));
    timers.current.push(setTimeout(() => setActiveIndex(2), 750));
    timers.current.push(setTimeout(() => setActiveIndex(3), 1150));

    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();
      const minDelay = new Promise((resolve) => setTimeout(resolve, 1400));
      await minDelay;
      setResult(data);
      setLastRecord({ ...values, prediction: data.prediction, confidence: data.confidence });
      setPipelineStatus("done");
    } catch (err) {
      setErrorMsg("Prediction failed — is the FastAPI backend running on port 8000?");
      setPipelineStatus("idle");
    }
  };

  return (
    <div className="min-h-screen bg-bg text-ink font-body">
      {/* Header */}
      <header className="border-b border-border bg-panel">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
              <span className="text-white font-display text-lg">A</span>
            </div>
            <div>
              <h1 className="font-display text-xl leading-tight text-ink">AMR Insight Platform</h1>
              <p className="text-xs text-inksoft font-mono">Agentic AI · Genomic + Clinical Resistance Prediction</p>
            </div>
          </div>
          <nav className="flex gap-1 bg-bg rounded-lg p-1 border border-border">
            {[
              { key: "predict", label: "Predict" },
              { key: "performance", label: "Model Performance" },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  tab === t.key ? "bg-accent text-white" : "text-inksoft hover:text-ink"
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {errorMsg && (
        <div className="bg-resistantsoft border-b border-resistant/30 text-resistant text-sm px-6 py-2 text-center">
          {errorMsg}
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-6">
        {tab === "predict" && options && (
          <>
            <div className="border border-border rounded-lg bg-panel px-5 py-4 mb-6">
              <AgentPipeline status={pipelineStatus} activeIndex={activeIndex} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr_320px] gap-6 items-start">
              <div>
                <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-2">
                  AMR Prediction — Input
                </p>
                <PredictionForm options={options} onSubmit={runPrediction} isRunning={pipelineStatus === "running"} />
              </div>

              <div>
                <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-2">
                  Prediction Result
                </p>
                <ResultPanel result={result} />
              </div>

              <div className="lg:sticky lg:top-6">
                <p className="text-xs uppercase tracking-widest text-inksoft font-mono mb-2">
                  Follow-up
                </p>
                <ExpertChat context={lastRecord} apiBase={API_BASE} />
              </div>
            </div>
          </>
        )}

        {tab === "predict" && !options && (
          <p className="text-sm text-inksoft">Loading form options…</p>
        )}

        {tab === "performance" && <ModelPerformance apiBase={API_BASE} />}
      </main>

      <footer className="max-w-7xl mx-auto px-6 py-8 text-xs text-inksoft/70 font-mono">
        4-agent architecture · Preprocessing → Modelling → Clinical Interpretation → Orchestrator · Built with LangChain-style agent design, FastAPI, and React
      </footer>
    </div>
  );
}
