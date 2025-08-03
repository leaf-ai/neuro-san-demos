import React, { useState, useEffect } from "react";
function UploadSection() {
  const inputRef = React.useRef();
  const [tree, setTree] = useState([]);
  const [prog,setProg] = useState(0);
  const upload = async () => {
    const files = Array.from(inputRef.current.files);
    if (!files.length) return;
    for (let i = 0; i < files.length; i += 10) {
      const fd = new FormData();
      for (const f of files.slice(i, i + 10)) {
        fd.append('files', f, f.webkitRelativePath || f.name);
      }
      await new Promise(res => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST','/api/upload');
        xhr.upload.onprogress = e=>{if(e.lengthComputable) setProg(Math.round((e.loaded/e.total)*100));};
        xhr.onload = xhr.onerror = () => res();
        xhr.send(fd);
      });
    }
    setProg(0);
    fetchFiles();
  };
  const fetchFiles = () => {
    fetch('/api/files').then(r=>r.json()).then(d=>setTree(d.data||[]));
  };
  const exportAll = () => { window.open('/api/export', '_blank'); };
  const organize = () => {
    fetch('/api/organized-files').then(r=>r.json()).then(d=>setTree(d.data||[]));
  };
  useEffect(fetchFiles, []);
  const renderNodes = nodes => nodes.map((n,i)=> n.children ? (
    <li key={i} className="folder">
      <div className="folder-header" onClick={e=>e.currentTarget.parentNode.classList.toggle('open')}><i className="folder-icon fa fa-caret-right"></i>{n.name}</div>
      <div className="folder-contents"><ul>{renderNodes(n.children)}</ul></div>
    </li>
  ) : (
    <li key={i} className="file" onClick={() => window.open('/uploads/'+n.path,'_blank')}>{n.name}</li>
  ));
  return (
    <section className="card">
      <h2>Upload</h2>
      <input type="file" ref={inputRef} className="mb-3" webkitdirectory="" directory="" multiple />
      <div className="flex flex-wrap gap-2 mb-3">
        <button className="button-primary" onClick={upload}><i className="fa fa-upload mr-1"></i>Upload</button>
        <button className="button-secondary" onClick={exportAll}><i className="fa fa-file-export mr-1"></i>Export All</button>
        <button className="button-secondary" onClick={organize}><i className="fa fa-folder-tree mr-1"></i>Organize</button>
      </div>
      {prog>0 && <progress value={prog} max="100" className="w-full mb-2"></progress>}
      <div className="folder-tree text-sm"><ul>{renderNodes(tree)}</ul></div>
    </section>
  );
}

export default UploadSection;
