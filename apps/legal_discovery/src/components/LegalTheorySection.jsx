import React, { useEffect, useState } from "react";

function LegalTheorySection() {
  const [theories, setTheories] = useState([]);
  const [loading, setLoading] = useState(false);
  const load = () => {
    setLoading(true);
    fetch("/api/theories/suggest").then(r => r.json()).then(d => {
      setTheories(d.theories || []);
      setLoading(false);
    });
  };
  useEffect(() => { load(); }, []);
  return (
    <section className="card">
      <h2>Case Theory</h2>
      <button className="button-secondary mb-2" onClick={load} disabled={loading}>
        <i className="fa fa-sync mr-1"></i>{loading ? "Loading" : "Refresh"}
      </button>
      {theories.map(t => (
        <div key={t.cause} className="mb-2">
          <h3 className="font-bold">{t.cause} - {(t.score*100).toFixed(0)}%</h3>
          <ul className="list-disc list-inside text-sm">
            {t.elements.map(e => (
              <li key={e.name} className={e.facts.length ? "theory-supported" : ""}>
                {e.name}
                {e.facts.length ? <span className="text-xs text-gray-400 ml-1">({e.facts.length})</span> : null}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}

export default LegalTheorySection;
