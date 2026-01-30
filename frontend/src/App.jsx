import { useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("https://tank-plate-taking-contributing.trycloudflare.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      const agentMsg = {
        role: "agent",
        content: data.response || "No response from agent.",
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: "❌ Backend not reachable." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ fontFamily: "Arial", maxWidth: 900, margin: "40px auto" }}>
      <h1>NIST CSF AI Agent (Demo)</h1>
      <p>
        This agent teaches and assesses the NIST Cybersecurity Framework using
        the official NIST document.
      </p>

      <div
        style={{
          border: "1px solid #ccc",
          padding: 20,
          height: 400,
          overflowY: "auto",
          marginBottom: 20,
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              marginBottom: 12,
              textAlign: m.role === "user" ? "right" : "left",
            }}
          >
            <strong>{m.role === "user" ? "You" : "Agent"}:</strong>
            <div>{m.content}</div>
          </div>
        ))}
        {loading && <em>Agent is thinking…</em>}
      </div>

      <div style={{ display: "flex", gap: 10 }}>
        <input
          style={{ flex: 1, padding: 10 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about NIST CSF or start an assessment…"
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>

      <hr style={{ margin: "30px 0" }} />

      <h3>Demo Prompts</h3>
      <ul>
        <li>Explain GV.PO-01</li>
        <li>Start an assessment for GV.PO-01</li>
        <li>What evidence is required for GV.PO-01?</li>
      </ul>
    </div>
  );
}
