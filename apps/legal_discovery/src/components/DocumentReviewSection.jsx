import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";

function DocumentReviewSection() {
  const [docs, setDocs] = useState([]);
  const [sort, setSort] = useState({ field: "probative_value", dir: "desc" });
  const [minProb, setMinProb] = useState(0);
  const [maxRisk, setMaxRisk] = useState(1);

  const load = () => fetchJSON("/api/documents").then(d => setDocs(d.data || []));
  useEffect(load, []);

  const setSortField = f =>
    setSort(s => ({ field: f, dir: s.field === f && s.dir === "desc" ? "asc" : "desc" }));

  const bar = (v, color) => (
    <div className="score-bar"><div className="score-fill" style={{ width: `${v * 100}%`, backgroundColor: color }}></div></div>
  );

  const filtered = docs
    .filter(d => d.probative_value >= minProb && d.admissibility_risk <= maxRisk)
    .sort((a, b) => {
      const f = sort.field;
      return sort.dir === "asc" ? a[f] - b[f] : b[f] - a[f];
    });

  return (
    <section className="card">
      <h2>Document Review</h2>
      <div className="flex gap-2 mb-2 items-center">
        <label className="text-xs">Min Prob {minProb.toFixed(2)}</label>
        <input type="range" min="0" max="1" step="0.01" value={minProb} onChange={e=>setMinProb(parseFloat(e.target.value))} />
        <label className="text-xs">Max Risk {maxRisk.toFixed(2)}</label>
        <input type="range" min="0" max="1" step="0.01" value={maxRisk} onChange={e=>setMaxRisk(parseFloat(e.target.value))} />
        <button className="button-secondary ml-auto" onClick={load}><i className="fa fa-sync mr-1"/>Refresh</button>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th onClick={()=>setSortField('name')}>Name</th>
            <th onClick={()=>setSortField('probative_value')}>Probative</th>
            <th onClick={()=>setSortField('admissibility_risk')}>Admissibility</th>
            <th onClick={()=>setSortField('narrative_alignment')}>Narrative</th>
            <th onClick={()=>setSortField('score_confidence')}>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(d => (
            <tr key={d.id}>
              <td>{d.name}</td>
              <td>{bar(d.probative_value, '#38bdf8')}</td>
              <td>{bar(d.admissibility_risk, '#f87171')}</td>
              <td>{bar(d.narrative_alignment, '#a3e635')}</td>
              <td>{bar(d.score_confidence, '#facc15')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export default DocumentReviewSection;
