import React, { useState, useEffect } from "react";
import { alertResponse } from "../utils";

function DepositionPrepSection() {
  const [cases, setCases] = useState([]);
  const [caseId, setCaseId] = useState("");
  const [witnesses, setWitnesses] = useState([]);
  const [witnessId, setWitnessId] = useState("");
  const [includePriv, setIncludePriv] = useState(false);
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    fetch("/api/cases").then(r => r.json()).then(d => setCases(d.data || []));
  }, []);

  useEffect(() => {
    if (caseId) {
      fetch(`/api/witnesses?case_id=${caseId}`)
        .then(r => r.json())
        .then(d => setWitnesses(d.data || []));
    }
  }, [caseId]);

  const generate = () => {
    if (!witnessId) return;
    fetch("/api/deposition/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ witness_id: witnessId, include_privileged: includePriv })
    })
      .then(r => r.json())
      .then(d => { setQuestions(d.data || []); alertResponse(d); });
  };

  const flag = id => {
    fetch(`/api/deposition/questions/${id}/flag`, { method: "POST" })
      .then(r => r.json()).then(alertResponse);
  };

  const exportDoc = () => {
    if (!witnessId) return;
    window.open(`/api/deposition/export/${witnessId}?format=docx`, "_blank");
  };

  const exportPdf = () => {
    if (!witnessId) return;
    window.open(`/api/deposition/export/${witnessId}?format=pdf`, "_blank");
  };

  return (
    <section className="card">
      <h2>Deposition Prep</h2>
      <select value={caseId} onChange={e => setCaseId(e.target.value)} className="p-2 rounded w-full mb-2">
        <option value="">Select Case</option>
        {cases.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
      <select value={witnessId} onChange={e => setWitnessId(e.target.value)} className="p-2 rounded w-full mb-2">
        <option value="">Select Witness</option>
        {witnesses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
      </select>
      <label className="flex items-center mb-2">
        <input type="checkbox" checked={includePriv} onChange={e => setIncludePriv(e.target.checked)} className="mr-2" />
        Include documents marked as privileged?
      </label>
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={generate}><i className="fa fa-question mr-1"></i>Generate</button>
        <button className="button-secondary" onClick={generate}><i className="fa fa-sync mr-1"></i>Regenerate</button>
        <button className="button-secondary" onClick={exportDoc}><i className="fa fa-file-word mr-1"></i>Export DOCX</button>
        <button className="button-secondary" onClick={exportPdf}><i className="fa fa-file-pdf mr-1"></i>Export PDF</button>
      </div>
      <ul className="text-sm space-y-2">
        {questions.map(q => (
          <li key={q.id} className="p-2 rounded" style={{ background: "var(--color-bg-alt)", borderLeft: "2px solid var(--color-accent)" }}>
            [{q.category}] {q.question}{q.source && <span style={{color:'var(--color-text-muted)'}}> ({q.source})</span>}
            <button className="ml-2 text-xs button-secondary" onClick={() => flag(q.id)}><i className="fa fa-flag mr-1"></i>Flag</button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default DepositionPrepSection;

