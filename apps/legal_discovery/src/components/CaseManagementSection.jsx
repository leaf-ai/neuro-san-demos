import React, { useState, useEffect, useRef } from "react";
function CaseManagementSection() {
  const [task,setTask] = useState('');
  const [tasks,setTasks] = useState([]);
  const [caseId,setCaseId] = useState('');
  const [events,setEvents] = useState([]);
  const containerRef = useRef();
  const add = () => fetch('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task})}).then(r=>r.json()).then(()=>{setTask('');listAll();});
  const listAll = () => fetch('/api/tasks').then(r=>r.json()).then(d=>{const arr=(d.data||'').split('\n').filter(Boolean).map(l=>l.replace(/^\-\s*/,''));setTasks(arr);});
  const clear = () => fetch('/api/tasks',{method:'DELETE'}).then(r=>r.json()).then(()=>{setTasks([]);});
  const loadTimeline = () => {
    if(!caseId) return;
    fetch('/api/timeline?query='+encodeURIComponent(caseId)).then(r=>r.json()).then(d=>setEvents(d.data||[]));
  };
  useEffect(listAll, []);
  useEffect(() => {
    if(!containerRef.current) return;
    if(!events.length) { containerRef.current.innerHTML=''; return; }
    const ds = new vis.DataSet(events.map(e=>({id:e.id, content:e.description, start:e.date})));
    new vis.Timeline(containerRef.current, ds, {});
  }, [events]);
  return (
    <section className="card">
      <h2>Case Management</h2>
      <div className="flex flex-wrap gap-2 mb-2">
        <input type="text" value={task} onChange={e=>setTask(e.target.value)} className="p-1 rounded" placeholder="New task" />
        <button className="button-secondary" onClick={add}><i className="fa fa-plus mr-1"></i>Add</button>
        <button className="button-secondary" onClick={listAll}><i className="fa fa-list mr-1"></i>List</button>
        <button className="button-secondary" onClick={clear}><i className="fa fa-trash mr-1"></i>Clear</button>
      </div>
      <ul className="mb-2 list-disc list-inside text-sm">
        {tasks.map((t,i)=><li key={i}>{t}</li>)}
      </ul>
      <div className="flex flex-wrap gap-2 mb-2">
        <input type="text" value={caseId} onChange={e=>setCaseId(e.target.value)} placeholder="Case ID" className="p-1 rounded" />
        <button className="button-secondary" onClick={loadTimeline}><i className="fa fa-clock mr-1"></i>Load Timeline</button>
      </div>
      <div ref={containerRef} style={{height:'200px'}}></div>
    </section>
  );
}
export default CaseManagementSection;
