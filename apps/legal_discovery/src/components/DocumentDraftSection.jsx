import React, { useState } from "react";
import { alertResponse } from "../utils";

function DocumentDraftSection() {
  const [path, setPath] = useState('');
  const [content, setContent] = useState('');
  const [action, setAction] = useState('create');
  const [level, setLevel] = useState(1);
  const [output, setOutput] = useState('');
  const submit = () => {
    const body = { filepath: path, content, action };
    if (action === 'heading') body.level = level;
    fetch('/api/document/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(r => r.json()).then(d => {
      setOutput(d.output || '');
      alertResponse(d);
    });
  };
  return (
    <section className="card">
      <h2>Document Drafting</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="DOCX path" />
      <textarea rows="4" value={content} onChange={e=>setContent(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Content" />
      <div className="flex items-center gap-2 mb-2">
        <select value={action} onChange={e=>setAction(e.target.value)} className="p-2 rounded bg-gray-800">
          <option value="create">Create</option>
          <option value="paragraph">Add Paragraph</option>
          <option value="heading">Add Heading</option>
        </select>
        {action === 'heading' && (
          <input type="number" min="1" max="9" value={level} onChange={e=>setLevel(parseInt(e.target.value))} className="w-16 p-2 rounded" />
        )}
        <button className="button-secondary" onClick={submit}><i className="fa fa-file-word mr-1"></i>Apply</button>
      </div>
      {output && <p className="text-sm">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
    </section>
  );
}

export default DocumentDraftSection;
