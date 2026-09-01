import { useCallback, useState } from "react";
import SupplementSelector from "./SupplementSelector";
import NutritionChart from "./NutritionChart";

const API_BASE = "http://127.0.0.1:8000";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [supplements, setSupplements] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const updateSupplements = useCallback((values) => setSupplements(values), []);

  const analyze = async () => {
    if (!file) { setError("Please choose a tray image before analyzing."); return; }
    setLoading(true); setError(""); setResult(null);
    const body = new FormData();
    body.append("file", file);
    body.append("supplements", JSON.stringify(supplements));
    try {
      const response = await fetch(`${API_BASE}/analyze-tray-complete`, { method: "POST", body });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data) throw new Error(data?.detail || "The analysis could not be completed.");
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (requestError) {
      setError(requestError.message || "Could not reach the NutriSense server. Please try again.");
    } finally { setLoading(false); }
  };

  const score = Number(result?.compliance?.compliance_score) || 0;
  const scoreClass = score >= 80 ? "score-good" : score >= 50 ? "score-fair" : "score-low";
  const deficits = Array.isArray(result?.compliance?.deficits) ? result.compliance.deficits : [];

  return (
    <div className="dashboard">
      <header className="hero"><div><p className="brand">NUTRISENSE</p><h1>Every tray tells a nutrition story.</h1><p>Check meal quality against Karnataka’s Mid-Day Meal standards.</p></div><span className="hero-mark">🍱</span></header>
      <section className="upload-card">
        <p className="eyebrow">Step 1</p><h2>Upload a meal tray</h2>
        <label className={`drop-zone ${file ? "has-file" : ""}`}>
          <input type="file" accept="image/*" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          <span>{file ? "✓" : "📷"}</span><strong>{file ? file.name : "Choose a tray photo"}</strong><small>{file ? "Ready to analyze" : "JPG, PNG, or any image format"}</small>
        </label>
      </section>
      <SupplementSelector onChange={updateSupplements} />
      <button type="button" className="analyze-button" onClick={analyze} disabled={loading}>{loading ? <><span className="spinner" /> Analyzing the meal…</> : "Analyze nutrition"}</button>
      {error && <p className="error-message">{error}</p>}
      {result && <section className="results-section">
        <div className="result-header"><div><p className="eyebrow">Analysis complete</p><h2>Meal compliance report</h2></div><div className={`score-badge ${scoreClass}`}><b>{Math.round(score)}</b><span>score</span></div></div>
        <p className="compliance-summary">{result.compliance?.summary || "Your meal analysis is ready."}</p>
        <div className="result-grid">
          <article className="tray-card"><h3>🍽️ Tray items</h3>{Array.isArray(result.tray_items) && result.tray_items.length ? <ul>{result.tray_items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul> : <p>No tray items were identified.</p>}</article>
          <article className="deficit-card"><h3>Nutrition gaps</h3>{deficits.length ? <ul>{deficits.map((deficit, index) => <li key={`${deficit.nutrient}-${index}`}><span><b>{deficit.nutrient}</b><small>Needs {deficit.gap} {deficit.unit || ""} more</small></span><em className={`severity ${deficit.severity === "high" ? "high" : "medium"}`}>{deficit.severity || "medium"}</em></li>)}</ul> : <p className="all-clear">✓ No nutrient deficits found.</p>}</article>
        </div>
        <NutritionChart nutrition={result.meal_nutrition_total} />
      </section>}
    </div>
  );
}
