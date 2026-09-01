import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";
const apiError = "⚠️ Something went wrong, please try again.";
const keyWarning = "🔑 AI chatbot needs an API key to work. Please add ANTHROPIC_API_KEY to the .env file and restart the server.";

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([{ role: "bot", text: "Hello! Ask me anything about today’s meal." }]);
  const [loading, setLoading] = useState(false);

  const send = async (event) => {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading) return;
    setMessages((items) => [...items, { role: "user", text: message }]);
    setInput(""); setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
      const data = await response.json().catch(() => null);
      const text = data?.error === "missing_api_key" ? keyWarning : data?.error === "api_error" || !response.ok ? apiError : data?.reply || apiError;
      setMessages((items) => [...items, { role: "bot", text, warning: data?.error === "missing_api_key", error: data?.error === "api_error" || !response.ok }]);
    } catch {
      setMessages((items) => [...items, { role: "bot", text: apiError, error: true }]);
    } finally { setLoading(false); }
  };

  return <div className="chatbot">
    {open && <section className="chat-panel" aria-label="NutriSense assistant"><header><div><span>🌿</span><div><b>NutriSense Assistant</b><small>Meal guidance</small></div></div><button type="button" onClick={() => setOpen(false)} aria-label="Close chat">×</button></header><div className="chat-messages">{messages.map((message, index) => <p key={index} className={`bubble ${message.role} ${message.warning ? "warning" : ""} ${message.error ? "api-error" : ""}`}>{message.text}</p>)}{loading && <p className="bubble bot typing"><i /><i /><i /></p>}</div><form onSubmit={send}><input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about nutrition…" aria-label="Chat message" /><button type="submit" disabled={loading || !input.trim()}>Send</button></form></section>}
    <button type="button" className="chat-launcher" onClick={() => setOpen((value) => !value)} aria-label="Open nutrition chat">{open ? "×" : "💬"}</button>
  </div>;
}
