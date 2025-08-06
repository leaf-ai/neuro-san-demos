import React, { useState } from "react";
import { alertResponse } from "../utils";

function DocToolsSection() {
  const [path,setPath] = useState('');
  const [redactText,setRedact] = useState('');
  const [prefix,setPrefix] = useState('');
  const [docId,setDocId] = useState('');
  const [userId,setUserId] = useState('');
  const [extracted,setExtracted] = useState('');
  const [output,setOutput] = useState('');
  const [versions,setVersions] = useState([]);
  const [v1,setV1] = useState('');
  const [v2,setV2] = useState('');
  const [diff,setDiff] = useState('');
  const call = (url,body) => fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
      .then(r=>r.json()).then(d=>{setOutput(d.output||'');alertResponse(d);});
  const redact = () => call('/api/document/redact',{file_path:path,text:redactText});
  const stamp = () => call('/api/document/stamp',{file_path:path,prefix,document_id:parseInt(docId),user_id:parseInt(userId)});
  const extract = () => fetch('/api/document/text',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file_path:path})}).then(r=>r.json()).then(d=>setExtracted(d.data||''));
  const loadVersions = () => fetch(`/api/document/versions?file_path=${encodeURIComponent(path)}`)
        .then(r=>r.json()).then(setVersions);
  const viewDiff = () => fetch(`/api/document/versions/diff?v1=${v1}&v2=${v2}`)
        .then(r=>r.json()).then(d=>setDiff(d.diff||''));
  return (
    <section className="card">
      <h2>Document Tools</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Path to PDF" />
      <input type="text" value={redactText} onChange={e=>setRedact(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Text to redact" />
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={redact}><i className="fa fa-eraser mr-1"></i>Redact PDF</button>
      </div>
      <input type="text" value={prefix} onChange={e=>setPrefix(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Bates prefix" />
      <input type="text" value={docId} onChange={e=>setDocId(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Document ID" />
      <input type="text" value={userId} onChange={e=>setUserId(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="User ID" />
      <button className="button-secondary" onClick={stamp}><i className="fa fa-stamp mr-1"></i>Bates Stamp</button>
      <button className="button-secondary mt-2" onClick={extract}><i className="fa fa-file-lines mr-1"></i>Extract Text</button>
      <button className="button-secondary mt-2" onClick={loadVersions}><i className="fa fa-clock-rotate-left mr-1"></i>Load Versions</button>
      {output && <p className="text-sm mb-2">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
      <pre className="text-sm mt-2">{extracted}</pre>
      {versions.length > 0 && (
        <div className="mt-4">
          <h3 className="mb-2">Version History</h3>
          <ul className="mb-2">
            {versions.map(v => (
              <li key={v.id} className="flex items-center gap-2 text-sm">
                <input type="radio" name="v1" value={v.id} onChange={e=>setV1(e.target.value)} />
                <input type="radio" name="v2" value={v.id} onChange={e=>setV2(e.target.value)} />
                <span>{v.bates_number} ({v.timestamp})</span>
              </li>
            ))}
          </ul>
          <button className="button-secondary" onClick={viewDiff} disabled={!v1 || !v2}><i className="fa fa-code-compare mr-1"></i>View Diff</button>
          {diff && <pre className="text-xs mt-2 whitespace-pre-wrap">{diff}</pre>}
        </div>
      )}
    </section>
  );
}
export default DocToolsSection;
