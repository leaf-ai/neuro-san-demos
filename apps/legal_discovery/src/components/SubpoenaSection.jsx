import React, { useState } from "react";
import { fetchJSON } from "../utils";
function SubpoenaSection() {
  const [path,setPath] = useState('');
  const [text,setText] = useState('');
  const draft = () => fetchJSON('/api/subpoena/draft',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file_path:path,content:text})}).then(alertResponse);
  return (
    <section className="card">
      <h2>Subpoena Drafting</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Template path" />
      <textarea rows="3" value={text} onChange={e=>setText(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Content" />
      <button className="button-secondary" onClick={draft}><i className="fa fa-file-signature mr-1"></i>Draft</button>
    </section>
  );
}

export default SubpoenaSection;
