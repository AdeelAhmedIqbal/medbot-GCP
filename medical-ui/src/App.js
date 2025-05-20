import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [history, setHistory]   = useState([]);

  // Fetch shared history from backend
  const loadHistory = async () => {
    try {
      const res  = await fetch("/history");
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("History load error:", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // Send prompt, get label+response, reload history
  const classify = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res  = await fetch("/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResult(data);
      await loadHistory();
    } catch (err) {
      console.error(err);
      setResult({ label: "error", response: "Something went wrong." });
    }
    setLoading(false);
    setQuestion("");
  };

  return (
    <div className="wrapper">
      <div className="card">

        {/* Header */}
        <div className="heading">
          <img src="/med-logo.png" alt="Logo" className="logo" />
          <div className="title-block">
            <h1>Medical Misinformation Detection</h1>
          </div>
        </div>

        {/* Input */}
        <div className="input-area">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Enter your medical question…"
          />
          <button onClick={classify} disabled={loading}>
            {loading ? "Analyzing…" : "Submit"}
          </button>
        </div>

        {/* Prediction Box (full-box colouring) */}
        {result && (
          <div className={`result ${result.label.toLowerCase()}`}>
            <h3>Prediction: <em>{result.label}</em></h3>
            {result.response && (
              <p><strong>Explanation:</strong> {result.response}</p>
            )}
          </div>
        )}

        {/* Shared History */}
        <div className="history">
          <h2>Chat History</h2>
          <ul>
            {history.map((item, i) => (
              <li key={i}>
                <strong>[{item.label}]</strong> {item.prompt}
              </li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  );
}

export default App;
