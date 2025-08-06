import React, { useState, useEffect } from "react";
function UploadSection() {
  const inputRef = React.useRef();
  const [tree, setTree] = useState([]);
  const [prog,setProg] = useState(0);
  const [vecProg,setVecProg] = useState(0);
  const [kgProg,setKgProg] = useState(0);
  const [neoProg,setNeoProg] = useState(0);
  const [current,setCurrent] = useState('');
  const [source,setSource] = useState('user');
  const [filter,setFilter] = useState('all');
  const togglePrivilege = (id, privileged) => {
    fetch(`/api/privilege/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ privileged })
    }).then(fetchFiles);
  };
  const upload = async () => {
    const files = Array.from(inputRef.current.files);
    if (!files.length) return;
    let uploaded = 0;
    for (let i = 0; i < files.length; i += 10) {
      const batch = files.slice(i, i + 10);
      setCurrent(batch[0]?.name || '');
      const fd = new FormData();
      batch.forEach(f => fd.append('files', f, f.webkitRelativePath || f.name));
      fd.append('source', source);
      await new Promise(res => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST','/api/upload');
        xhr.onload = xhr.onerror = () => res();
        xhr.send(fd);
      });
      uploaded += batch.length;
      const pct = Math.round((uploaded / files.length) * 100);
      setProg(pct);
      setVecProg(pct);
      setKgProg(pct);
      setNeoProg(pct);
    }
    setCurrent('');
    setProg(0);
    setVecProg(0);
    setKgProg(0);
    setNeoProg(0);
    fetchFiles();
    window.dispatchEvent(new Event('graphRefresh'));
  };
  const fetchFiles = () => {
    fetch('/api/files').then(r=>r.json()).then(d=>setTree(d.data||[]));
  };
  const exportAll = () => { window.open('/api/export', '_blank'); };
  const organize = () => {
    fetch('/api/organized-files').then(r=>r.json()).then(d=>setTree(d.data||[]));
  };
  useEffect(fetchFiles, []);
  const sourceClass = s => ({
    opp_counsel: 'text-red-400',
    court: 'text-yellow-400',
    user: 'text-blue-400'
  }[s] || 'text-blue-400');
  const renderNodes = nodes => nodes.map((n,i)=> {
    if (n.children) {
      const kids = renderNodes(n.children).filter(Boolean);
      if (!kids.length) return null;
      return (
        <li key={i} className="folder">
          <div className="folder-header" onClick={e=>e.currentTarget.parentNode.classList.toggle('open')}><i className="folder-icon fa fa-caret-right"></i>{n.name}</div>
          <div className="folder-contents"><ul>{kids}</ul></div>
        </li>
      );
    }
    if (filter !== 'all' && n.source !== filter) return null;
    return (
      <li key={i} className={`file ${n.privileged ? 'privileged' : ''} ${sourceClass(n.source)}`} onClick={() => window.open('/uploads/'+n.path,'_blank')}>
        {n.name}
        {n.privileged && <i className="fa fa-user-secret ml-1" />}
        {n.id && (
          <button
            className="button-secondary ml-2 text-xs"
            onClick={e => {e.stopPropagation(); togglePrivilege(n.id, !n.privileged);}}
          >
            {n.privileged ? 'Mark Public' : 'Mark Privileged'}
          </button>
        )}
      </li>
    );
  });
  return (
    <section className="card">
      <h2>Upload</h2>
      <input type="file" ref={inputRef} className="mb-3" webkitdirectory="" directory="" multiple />
      <div className="flex flex-wrap gap-2 mb-3">
        <select value={source} onChange={e=>setSource(e.target.value)} className="px-2 py-1 bg-gray-800 border border-gray-600 rounded">
          <option value="user">User</option>
          <option value="opp_counsel">Opposing Counsel</option>
          <option value="court">Court</option>
        </select>
        <select value={filter} onChange={e=>setFilter(e.target.value)} className="px-2 py-1 bg-gray-800 border border-gray-600 rounded">
          <option value="all">All Sources</option>
          <option value="user">User</option>
          <option value="opp_counsel">Opposing Counsel</option>
          <option value="court">Court</option>
        </select>
        <button className="button-primary" onClick={upload}><i className="fa fa-upload mr-1"></i>Upload</button>
        <button className="button-secondary" onClick={exportAll}><i className="fa fa-file-export mr-1"></i>Export All</button>
        <button className="button-secondary" onClick={organize}><i className="fa fa-folder-tree mr-1"></i>Organize</button>
      </div>
      {prog>0 && (
        <>
          <progress value={prog} max="100" className="w-full mb-2"></progress>
          {current && <p className="text-xs mb-2">Uploading: {current}</p>}
          <div className="mb-2">
            <p className="text-xs">Vector DB</p>
            <progress value={vecProg} max="100" className="w-full"></progress>
          </div>
          <div className="mb-2">
            <p className="text-xs">Knowledge DB</p>
            <progress value={kgProg} max="100" className="w-full"></progress>
          </div>
          <div className="mb-2">
            <p className="text-xs">Neo4j Graph</p>
            <progress value={neoProg} max="100" className="w-full"></progress>
          </div>
        </>
      )}
      <div className="folder-tree text-sm"><ul>{renderNodes(tree)}</ul></div>
    </section>
  );
}

export default UploadSection;
