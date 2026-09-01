import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function SupplementSelector({ onChange }) {
  const [options, setOptions] = useState([]);
  const [values, setValues] = useState({});
  const [message, setMessage] = useState("Loading supplement options…");

  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}/supplements/options`)
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((data) => {
        if (!active) return;
        const supplements = Array.isArray(data?.supplements) ? data.supplements : [];
        const defaults = Object.fromEntries(supplements.map((item) => [item.id, item.default ?? 0]));
        setOptions(supplements);
        setValues(defaults);
        onChange(defaults);
        setMessage(supplements.length ? "" : "No supplement options are available right now.");
      })
      .catch(() => active && setMessage("Supplement options could not be loaded."));
    return () => { active = false; };
  }, [onChange]);

  const updateValue = (id, value) => {
    setValues((current) => {
      const next = { ...current, [id]: value };
      onChange(next);
      return next;
    });
  };

  const cycle = (item, direction) => {
    const choices = item.options || [0];
    const index = Math.max(0, choices.indexOf(values[item.id]));
    const nextIndex = (index + direction + choices.length) % choices.length;
    updateValue(item.id, choices[nextIndex]);
  };

  return (
    <section className="supplement-section">
      <div className="section-heading">
        <div><p className="eyebrow">Today’s extras</p><h2>Supplements received</h2></div>
        <span className="optional-label">Optional</span>
      </div>
      {message && <p className="inline-message">{message}</p>}
      <div className="supplement-grid">
        {options.map((item) => (
          <article className="supplement-card" key={item.id}>
            <span className="supplement-emoji" aria-hidden="true">{item.emoji}</span>
            <div className="supplement-info"><h3>{item.label}</h3><p>{item.nutrition_per_unit?.calories ?? "—"} kcal per serving</p></div>
            {item.type === "counter" ? (
              <div className="counter-control" aria-label={`${item.label} quantity`}>
                <button type="button" onClick={() => cycle(item, -1)}>−</button>
                <strong>{values[item.id] ?? item.default ?? 0}</strong>
                <button type="button" onClick={() => cycle(item, 1)}>+</button>
              </div>
            ) : (
              <div className="toggle-control">
                {(item.options || []).map((value, index) => (
                  <button
                    type="button"
                    className={values[item.id] === value ? "selected" : ""}
                    key={value}
                    onClick={() => updateValue(item.id, value)}
                  >
                    {item.option_labels?.[index] ?? value}
                  </button>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
