import { useState, useRef, useEffect } from "react";

export default function ExpertChat({ context, apiBase }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "I'm ready to address your queries regarding the prediction, AMR, and clinical management.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const disabled = !context;

  const send = async () => {
    if (!input.trim() || loading || disabled) return;
    const question = input.trim();
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, context }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", text: data.answer }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Could not reach the backend. Is the FastAPI server running on port 8000?" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border border-border rounded-lg bg-panel flex flex-col h-full min-h-[360px]">
      <div className="px-4 py-3 border-b border-border">
        <p className="text-xs uppercase tracking-widest text-inksoft font-mono">
          Expert Consultation
        </p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto thin-scroll px-4 py-3 flex flex-col gap-2.5">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm px-3 py-2 rounded-lg max-w-[90%] leading-relaxed ${
              m.role === "user"
                ? "bg-accent text-white self-end rounded-br-sm"
                : "bg-bg text-ink self-start rounded-bl-sm"
            }`}
          >
            {m.text}
          </div>
        ))}
        {loading && (
          <div className="text-sm px-3 py-2 rounded-lg bg-bg text-inksoft self-start">
            Thinking…
          </div>
        )}
      </div>

      <div className="p-3 border-t border-border flex gap-2">
        <input
          value={input}
          disabled={disabled}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder={disabled ? "Run a prediction first…" : "Type your query…"}
          className="flex-1 border border-border rounded-md px-3 py-2 text-sm bg-white focus:border-accent disabled:opacity-50"
        />
        <button
          onClick={send}
          disabled={disabled || loading}
          className="bg-accent disabled:opacity-50 text-white text-sm font-medium px-4 rounded-md hover:bg-[#0b5947] transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
