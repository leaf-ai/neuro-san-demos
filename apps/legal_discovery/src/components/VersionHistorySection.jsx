import React, { useState } from "react";
import { alertResponse } from "../utils";

function VersionHistorySection() {
  const [docId, setDocId] = useState('');
  const [versions, setVersions] = useState([]);
  const [diff, setDiff] = useState('');
  const load = () => fetch(`/api/document/${docId}/versions`).then(r=>r.json()).then(d=>setVersions(d.versions||[]));
  const showDiff = (from, to) => fetch(`/api/document/${docId}/diff?from=${from}&to=${to}`).then(r=>r.json()).then(d=>{setDiff(d.diff||'');alertResponse(d);});
  return (
    <section className="card">
      <h2>Version History</h2>
      <input type="text" value={docId} onChange={e=>setDocId(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Document ID" />
      <button className="button-secondary mb-2" onClick={load}><i className="fa fa-history mr-1"></i>Load Versions</button>
      <ul className="text-sm mb-2">{versions.map(v=> <li key={v.version}>{v.version}: {v.bates_number} by {v.user} at {v.timestamp}</li>)}</ul>
      {versions.length>1 && <button className="button-secondary mb-2" onClick={()=>showDiff(versions[versions.length-2].version, versions[versions.length-1].version)}><i className="fa fa-code-compare mr-1"></i>Diff Last Two</button>}
      {diff && <pre className="text-sm whitespace-pre-wrap">{diff}</pre>}
    </section>
  );
}
export default VersionHistorySection;
