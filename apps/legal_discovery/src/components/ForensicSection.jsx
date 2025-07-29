import React, { useState } from "react";
import { fetchJSON } from "../utils";
function ForensicSection() {
  const [path,setPath] = useState('');
  const [type,setType] = useState('authenticity');
  const [log,setLog] = useState('');
  const [result,setResult] = useState('');
  const analyze = () =>
    fetchJSON('/api/agents/forensic_analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: path, analysis_type: type })
    }).then(d => setResult(d.result || d.error || ''));
  const loadLogs = () => fetch('/api/forensic/logs').then(r=>r.json()).then(d=>setLog((d.data||[]).join('\n')));
  return (
    <section className="card">
      <h2>Forensic Analysis</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="File path" />
      <select value={type} onChange={e=>setType(e.target.value)} className="w-full mb-2 p-2 rounded">
        <option value="authenticity">Authenticity</option>
        <option value="financial">Financial</option>
      </select>
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={analyze}><i className="fa fa-search-dollar mr-1"></i>Analyze</button>
        <button className="button-secondary" onClick={loadLogs}><i className="fa fa-book mr-1"></i>Logs</button>
      </div>
      {result && <pre className="text-sm mb-2">{result}</pre>}
      <pre className="text-sm">{log}</pre>
    </section>
  );
}
export default ForensicSection;