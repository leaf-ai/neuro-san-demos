const { useState, useEffect, useRef } = React;

function fetchJSON(url, options) {
  return fetch(url, options).then(r => r.json());
}

function alertResponse(d) {
  alert(d.message || 'Done');
}

function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  useEffect(() => {
    const socket = io('/chat');
    socket.on('update_speech', d => setMessages(m => [...m, {type:'speech', text:d.data}]));
    socket.on('update_user_input', d => setMessages(m => [...m, {type:'user', text:d.data}]));
    return () => socket.disconnect();
  }, []);
  const send = () => {
    if (!input.trim()) return;
    fetch('/api/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text: input})})
      .then(() => setInput(''));
  };
  return (
    <section className="card">
      <h2>Chat</h2>
      <div className="chat-box" style={{maxHeight:'160px'}}>
        {messages.map((m,i) => <div key={i} className={m.type==='user'?'user-msg':'speech-msg'}>{m.text}</div>)}
      </div>
      <textarea value={input} onChange={e=>setInput(e.target.value)} rows="2" className="w-full mb-2 p-2 rounded" placeholder="Ask the assistant..."></textarea>
      <button className="button-primary" onClick={send}>Send</button>
    </section>
  );
}

function StatsSection() {
  const [uploaded, setUploaded] = useState(0);
  const [vectorCount, setVector] = useState(0);
  const refresh = () => {
    fetch('/api/progress').then(r=>r.json()).then(d=>setUploaded(d.data.uploaded_files||0));
    fetch('/api/vector/count').then(r=>r.json()).then(d=>setVector(d.data||0));
  };
  useEffect(refresh, []);
  return (
    <section className="card" id="stats-card">
      <h2>Stats</h2>
      <p className="mb-1">Uploaded files: <span>{uploaded}</span></p>
      <p>Vector documents: <span>{vectorCount}</span></p>
      <button className="button-secondary mt-2" onClick={refresh}><i className="fa fa-sync mr-1"></i>Refresh</button>
    </section>
  );
}

function OverviewSection() {
  const [progress,setProgress] = useState({uploaded_files:0});
  const [tasks,setTasks] = useState([]);
  useEffect(() => {
    fetchJSON('/api/progress').then(d=>setProgress(d.data||{}));
    fetchJSON('/api/tasks').then(d=>setTasks(d.data||[]));
  }, []);
  return (
    <section className="card">
      <h2>Overview</h2>
      <p className="mb-1">Uploaded Files: {progress.uploaded_files||0}</p>
      <p className="mb-1">Open Tasks: {tasks.length||0}</p>
    </section>
  );
}

function UploadSection() {
  const inputRef = React.useRef();
  const [tree, setTree] = useState([]);
  const upload = () => {
    const files = inputRef.current.files;
    if (!files.length) return;
    const fd = new FormData();
    for (const f of files) fd.append('files', f, f.webkitRelativePath||f.name);
    fetch('/api/upload', {method:'POST', body:fd}).then(r=>r.json()).then(() => {fetchFiles();});
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
      <div className="folder-tree text-sm"><ul>{renderNodes(tree)}</ul></div>
    </section>
  );
}

function TimelineSection() {
  const [query,setQuery] = useState('');
  const [events,setEvents] = useState([]);
  const containerRef = useRef();
  const load = () => {
    fetch('/api/timeline?query='+encodeURIComponent(query))
      .then(r=>r.json()).then(d=>setEvents(d.data||[]));
  };
  const exportTimeline = () => {
    fetch('/api/export/report', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'timeline',timeline_id:query})})
      .then(r=>r.text()).then(html=>{const w=window.open('about:blank'); w.document.write(html);});
  };
  useEffect(() => {
    if(!containerRef.current) return;
    if(!events.length) { containerRef.current.innerHTML=''; return; }
    const dataset = new vis.DataSet(events.map(e=>({id:e.id, content:e.description, start:e.date, citation:e.citation})));
    const timeline = new vis.Timeline(containerRef.current, dataset, {});
    timeline.on('click', props => {
      const item = dataset.get(props.item);
      if(item && item.citation) {
        const modal = document.getElementById('modal');
        modal.querySelector('iframe').src = item.citation;
        modal.style.display='flex';
      }
    });
  }, [events]);
  return (
    <section className="card">
      <h2>Timeline</h2>
      <textarea rows="2" className="w-full mb-3 p-2 rounded" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Request events…"></textarea>
      <div className="flex gap-2 mb-2">
        <button className="button-primary" onClick={load}>Load Timeline</button>
        <button className="button-secondary" onClick={exportTimeline}><i className="fa fa-file-export mr-1"></i>Export</button>
      </div>
      <div ref={containerRef} style={{height:'200px'}}></div>
    </section>
  );
}

function GraphSection() {
  const [nodes,setNodes] = useState([]);
  const [edges,setEdges] = useState([]);
  useEffect(() => {
    fetch('/api/graph').then(r=>r.json()).then(d=>{setNodes(d.data.nodes||[]);setEdges(d.data.edges||[]);});
  }, []);
  useEffect(() => {
    if(!nodes.length && !edges.length) return;
    const cy = cytoscape({ container: document.getElementById('graph'), elements: [] });
    cy.add(nodes.map(n => ({ data:{ id:n.id, label:n.labels[0] }})));
    cy.add(edges.map(e => ({ data:{ id:e.source+'_'+e.target, source:e.source, target:e.target }})));
    cy.layout({ name:'breadthfirst', directed:true }).run();
  }, [nodes,edges]);
  const exportGraph = () => { window.open('/api/graph/export', '_blank'); };
  return (
    <section className="card">
      <h2>Knowledge Graph</h2>
      <div className="flex gap-2 mb-2">
        <button className="button-secondary" onClick={exportGraph}><i className="fa fa-file-export mr-1"></i>Export</button>
      </div>
      <div id="graph" style={{height:'300px', border:'1px solid var(--border-colour)'}}></div>
    </section>
  );
}

function DocToolsSection() {
  const [path,setPath] = useState('');
  const [redactText,setRedact] = useState('');
  const [prefix,setPrefix] = useState('');
  const [extracted,setExtracted] = useState('');
  const call = (url,body) => fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json()).then(alertResponse);
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
      <pre className="text-sm mt-2">{extracted}</pre>
    </section>
  );
}

function ForensicSection() {
  const [path,setPath] = useState('');
  const [type,setType] = useState('authenticity');
  const [log,setLog] = useState('');
  const analyze = () => fetch('/api/agents/forensic_analysis',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file_path:path,analysis_type:type})}).then(r=>r.json()).then(d=>alert(d.result||d.error||'Done'));
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
      <pre className="text-sm">{log}</pre>
    </section>
  );
}

function VectorSection() {
  const [q,setQ] = useState('');
  const [res,setRes] = useState('');
  const search = () => fetch('/api/vector/search?q='+encodeURIComponent(q)).then(r=>r.json()).then(d=>setRes(JSON.stringify(d.data,null,2)));
  return (
    <section className="card">
      <h2>Vector Search</h2>
      <input type="text" value={q} onChange={e=>setQ(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Search text" />
      <button className="button-secondary mb-2" onClick={search}><i className="fa fa-search mr-1"></i>Search</button>
      <pre className="text-sm">{res}</pre>
    </section>
  );
}

function TasksSection() {
  const [task,setTask] = useState('');
  const [list,setList] = useState('');
  const add = () => fetch('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task})}).then(r=>r.json()).then(alertResponse);
  const listAll = () => fetch('/api/tasks').then(r=>r.json()).then(d=>setList(d.data||''));
  const clear = () => fetch('/api/tasks',{method:'DELETE'}).then(r=>r.json()).then(d=>{setList('');alert(d.message||'Cleared');});
  return (
    <section className="card">
      <h2>Task Tracker</h2>
      <input type="text" value={task} onChange={e=>setTask(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="New task" />
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={add}><i className="fa fa-plus mr-1"></i>Add</button>
        <button className="button-secondary" onClick={listAll}><i className="fa fa-list mr-1"></i>List</button>
        <button className="button-secondary" onClick={clear}><i className="fa fa-trash mr-1"></i>Clear</button>
      </div>
      <pre className="text-sm">{list}</pre>
    </section>
  );
}

function ResearchSection() {
  const [q,setQ] = useState('');
  const [res,setRes] = useState('');
  const [source,setSource] = useState('all');
  const search = () => fetch('/api/research?query='+encodeURIComponent(q)+'&source='+source).then(r=>r.json()).then(d=>setRes(JSON.stringify(d.data,null,2)));
  return (
    <section className="card">
      <h2>Research</h2>
      <input type="text" value={q} onChange={e=>setQ(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Search references" />
      <select value={source} onChange={e=>setSource(e.target.value)} className="w-full mb-2 p-2 rounded">
        <option value="all">All</option>
        <option value="cases">Cases</option>
        <option value="statutes">Statutes</option>
      </select>
      <div className="flex flex-wrap gap-2 mb-2">
        <button className="button-secondary" onClick={search}><i className="fa fa-book-open mr-1"></i>Search</button>
      </div>
      <pre className="text-sm">{res}</pre>
    </section>
  );
}

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

function PresentationSection() {
  const [path,setPath] = useState('');
  const [slides,setSlides] = useState('');
  const create = () => {
    const slidesArr = slides.split('\n').map(l=>{const [t,...c]=l.split('|');return {title:t||'',content:c.join('|')||''};});
    fetchJSON('/api/presentation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filepath:path,slides:slidesArr})}).then(alertResponse);
  };
  return (
    <section className="card">
      <h2>Presentation</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="PPTX path" />
      <textarea rows="4" value={slides} onChange={e=>setSlides(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="title|content per line" />
      <button className="button-secondary" onClick={create}><i className="fa fa-slideshare mr-1"></i>Create/Update</button>
    </section>
  );
}

function SettingsModal({open,onClose}) {
  const [form,setForm] = useState({});
  const ref = useRef();
  useEffect(() => {
    if(open) {
      fetch('/api/settings').then(r=>r.json()).then(d=>setForm(d||{}));
    }
  }, [open]);
  const update = e => setForm({...form,[e.target.name]:e.target.value});
  const submit = e => {
    e.preventDefault();
    fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(form)})
      .then(()=>onClose());
  };
  if(!open) return null;
  return (
    <div className="modal" onClick={e=>{if(e.target===ref.current) onClose();}} ref={ref}>
      <div className="modal-content">
        <span className="close-btn" onClick={onClose}>&times;</span>
        <h2>API Settings</h2>
        <form id="settings-form" onSubmit={submit} className="space-y-2 overflow-y-auto" style={{maxHeight:'60vh'}}>
          <label>CourtListener API Key<input type="text" name="courtlistener_api_key" value={form.courtlistener_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>CourtListener Endpoint<input type="text" name="courtlistener_com_api_endpoint" value={form.courtlistener_com_api_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>California Codes URL<input type="text" name="california_codes_url" value={form.california_codes_url||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Gemini API Key<input type="text" name="gemini_api_key" value={form.gemini_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Google API Endpoint<input type="text" name="google_api_endpoint" value={form.google_api_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>VerifyPDF API Key<input type="text" name="verifypdf_api_key" value={form.verifypdf_api_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>VerifyPDF Endpoint<input type="text" name="verify_pdf_endpoint" value={form.verify_pdf_endpoint||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Riza Key<input type="text" name="riza_key" value={form.riza_key||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j URI<input type="text" name="neo4j_uri" value={form.neo4j_uri||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Username<input type="text" name="neo4j_username" value={form.neo4j_username||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Password<input type="password" name="neo4j_password" value={form.neo4j_password||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Neo4j Database<input type="text" name="neo4j_database" value={form.neo4j_database||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Aura Instance ID<input type="text" name="aura_instance_id" value={form.aura_instance_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>Aura Instance Name<input type="text" name="aura_instance_name" value={form.aura_instance_name||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Project ID<input type="text" name="gcp_project_id" value={form.gcp_project_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Vertex Data Store<input type="text" name="gcp_vertex_ai_data_store_id" value={form.gcp_vertex_ai_data_store_id||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Search App<input type="text" name="gcp_vertex_ai_search_app" value={form.gcp_vertex_ai_search_app||''} onChange={update} className="w-full p-2 rounded"/></label>
          <label>GCP Service Account Key<textarea name="gcp_service_account_key" value={form.gcp_service_account_key||''} onChange={update} className="w-full p-2 rounded" rows="2"/></label>
          <button className="button-primary" type="submit">Save</button>
        </form>
      </div>
    </div>
  );
}

function Dashboard() {
  const [tab, setTab] = useState('overview');
  const [showSettings,setShowSettings] = useState(false);
  useEffect(()=>{
    const btn=document.getElementById('settings-btn');
    if(btn) btn.onclick=()=>setShowSettings(true);
  },[]);
  return (
    <div>
      <div className="tab-buttons">
        {['overview','chat','stats','upload','timeline','graph','docs','forensic','vector','tasks','research','subpoena','presentation'].map(t => (
          <button key={t} className={`tab-button ${tab===t?'active':''}`} onClick={()=>setTab(t)} data-target={`tab-${t}`}>{t.charAt(0).toUpperCase()+t.slice(1)}</button>
        ))}
      </div>
      <div className="tab-content" style={{display: tab==='overview'?'block':'none'}}><OverviewSection/></div>
      <div className="tab-content" style={{display: tab==='chat'?'block':'none'}}><ChatSection/></div>
      <div className="tab-content" style={{display: tab==='stats'?'block':'none'}}><StatsSection/></div>
      <div className="tab-content" style={{display: tab==='upload'?'block':'none'}}><UploadSection/></div>
      <div className="tab-content" style={{display: tab==='timeline'?'block':'none'}}><TimelineSection/></div>
      <div className="tab-content" style={{display: tab==='graph'?'block':'none'}}><GraphSection/></div>
      <div className="tab-content" style={{display: tab==='docs'?'block':'none'}}><DocToolsSection/></div>
      <div className="tab-content" style={{display: tab==='forensic'?'block':'none'}}><ForensicSection/></div>
      <div className="tab-content" style={{display: tab==='vector'?'block':'none'}}><VectorSection/></div>
      <div className="tab-content" style={{display: tab==='tasks'?'block':'none'}}><TasksSection/></div>
      <div className="tab-content" style={{display: tab==='research'?'block':'none'}}><ResearchSection/></div>
      <div className="tab-content" style={{display: tab==='subpoena'?'block':'none'}}><SubpoenaSection/></div>
      <div className="tab-content" style={{display: tab==='presentation'?'block':'none'}}><PresentationSection/></div>
      <SettingsModal open={showSettings} onClose={()=>setShowSettings(false)}/>
    </div>
  );
}

ReactDOM.render(<Dashboard/>, document.getElementById('root'));
