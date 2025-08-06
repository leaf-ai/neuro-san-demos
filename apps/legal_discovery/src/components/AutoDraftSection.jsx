import React, { useState, useEffect } from "react";
import { alertResponse } from "../utils";

function AutoDraftSection() {
  const [types, setTypes] = useState([]);
  const [motion, setMotion] = useState("");
  const [draft, setDraft] = useState("");
  const [output, setOutput] = useState("");
  const [reviewed, setReviewed] = useState(false);

  useEffect(() => {
    fetch("/api/auto_draft/templates").then(r => r.json()).then(d => setTypes(d.data || []));
  }, []);

  const generate = () => {
    if (!motion) return;
    fetch("/api/auto_draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ motion_type: motion })
    }).then(r => r.json()).then(d => { setDraft(d.data || ""); setReviewed(false); alertResponse(d); });
  };

  const exportFile = fmt => {
    if (!draft || !reviewed) return;
    fetch("/api/auto_draft/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: draft, format: fmt })
    }).then(r => r.json()).then(d => {
      alertResponse(d);
      if (d.output) {
        setOutput(d.output);
        window.open(`/uploads/${d.output}`, "_blank");
      }
    });
  };

  return (
    <section className="card">
      <h2>Auto Draft</h2>
      <select value={motion} onChange={e=>setMotion(e.target.value)} className="p-2 rounded w-full mb-2">
        <option value="">Select Motion Type</option>
        {types.map(t => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
      </select>
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={generate}><i className="fa fa-magic mr-1"></i>Generate</button>
        <button className="button-secondary" onClick={() => { setDraft(""); setReviewed(false); }}><i className="fa fa-eraser mr-1"></i>Clear</button>
        <button className="button-secondary" onClick={() => setReviewed(true)}><i className="fa fa-check mr-1"></i>Mark Reviewed</button>
        <button className="button-secondary" onClick={() => exportFile('docx')} disabled={!reviewed}><i className="fa fa-file-word mr-1"></i>Export DOCX</button>
        <button className="button-secondary" onClick={() => exportFile('pdf')} disabled={!reviewed}><i className="fa fa-file-pdf mr-1"></i>Export PDF</button>
      </div>
      <textarea rows="10" value={draft} onChange={e=>{ setDraft(e.target.value); setReviewed(false); }} className="w-full p-2 rounded" placeholder="Draft output for review..." />
      {output && <p className="text-sm">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
    </section>
  );
}

export default AutoDraftSection;
