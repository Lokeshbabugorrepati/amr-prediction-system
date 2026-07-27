const AGENTS = [
  { key: "prep", label: "Data Preprocessing", detail: "Clean · Scale · Encode" },
  { key: "model", label: "Modelling Agent", detail: "XGBoost · LightGBM · CatBoost · DNN" },
  { key: "explain", label: "Clinical Interpretation", detail: "LLaMA 3.1 via Groq" },
  { key: "orchestrator", label: "Orchestrator", detail: "Coordinates the pipeline" },
];

/**
 * status: "idle" | "running" | "done"
 * activeIndex: which agent node is currently lit while running
 */
export default function AgentPipeline({ status, activeIndex }) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs uppercase tracking-widest text-inksoft font-mono">
          Assay Pipeline
        </span>
        <span className="text-xs font-mono text-inksoft">
          {status === "idle" && "Awaiting sample"}
          {status === "running" && "Processing…"}
          {status === "done" && "Complete"}
        </span>
      </div>
      <div className="flex items-center">
        {AGENTS.map((agent, i) => {
          const isActive = status === "running" && i === activeIndex;
          const isDone =
            status === "done" || (status === "running" && i < activeIndex);
          return (
            <div key={agent.key} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1 min-w-0">
                <div
                  className={`w-3.5 h-3.5 rounded-full border-2 transition-colors duration-300 ${
                    isDone
                      ? "bg-accent border-accent"
                      : isActive
                      ? "bg-accent border-accent agent-active"
                      : "bg-panel border-border"
                  }`}
                />
                <span
                  className={`mt-2 text-[11px] font-medium text-center leading-tight px-1 ${
                    isDone || isActive ? "text-ink" : "text-inksoft"
                  }`}
                >
                  {agent.label}
                </span>
                <span className="text-[10px] font-mono text-inksoft/70 text-center leading-tight mt-0.5 hidden sm:block">
                  {agent.detail}
                </span>
              </div>
              {i < AGENTS.length - 1 && (
                <div
                  className={`h-[2px] flex-1 -mt-6 transition-colors duration-500 ${
                    isDone ? "bg-accent" : "bg-border"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
