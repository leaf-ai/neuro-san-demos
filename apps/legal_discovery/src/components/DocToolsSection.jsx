import React, { useState } from "react";
import { alertResponse } from "../utils";
function DocToolsSection() {
  const [path,setPath] = useState('');
  const [redactText,setRedact] = useState('');
  const [prefix,setPrefix] = useState('');
  const [extracted,setExtracted] = useState('');
  const [output,setOutput] = useState('');
  const call = (url,body) => fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
      .then(r=>r.json()).then(d=>{setOutput(d.output||'');alertResponse(d);});
  const redact = () => call('/api/document/redact',{file_path:path,text:redactText});
  const stamp = () => call('/api/document/stamp',{file_path:path,prefix});
  const extract = () => fetch('/api/document/text',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file_path:path})}).then(r=>r.json()).then(d=>setExtracted(d.data||''));
  return (
    <section className="card">
      <h2>Document Tools</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Path to PDF" />
      <input type="text" value={redactText} onChange={e=>setRedact(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Text to redact" />
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={redact}><i className="fa fa-eraser mr-1"></i>Redact PDF</button>
      </div>
      <input type="text" value={prefix} onChange={e=>setPrefix(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Bates prefix" />
      <button className="button-secondary" onClick={stamp}><i className="fa fa-stamp mr-1"></i>Bates Stamp</button>
      <button className="button-secondary mt-2" onClick={extract}><i className="fa fa-file-lines mr-1"></i>Extract Text</button>
      {output && <p className="text-sm mb-2">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
      <pre className="text-sm mt-2">{extracted}</pre>
    </section>
  );
}
export default DocToolsSection;
