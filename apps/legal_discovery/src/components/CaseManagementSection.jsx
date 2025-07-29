import React, { useState, useEffect, useRef } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
function CaseManagementSection() {
  const [task,setTask] = useState('');
  const [tasks,setTasks] = useState([]);
  const [caseId,setCaseId] = useState('');
  const [cases,setCases] = useState([]);
  const [newCase,setNewCase] = useState('');
  const [events,setEvents] = useState([]);
  const [calendarEvents,setCalendarEvents] = useState([]);
  const [newEventDate,setNewEventDate] = useState(new Date());
  const [newEventTitle,setNewEventTitle] = useState('');
  const containerRef = useRef();
  const add = () => fetch('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task})}).then(r=>r.json()).then(()=>{setTask('');listAll();});
  const listAll = () => fetch('/api/tasks').then(r=>r.json()).then(d=>{const arr=(d.data||'').split('\n').filter(Boolean).map(l=>l.replace(/^\-\s*/,''));setTasks(arr);});
  const clear = () => fetch('/api/tasks',{method:'DELETE'}).then(r=>r.json()).then(()=>{setTasks([]);});
  const refreshCases = () =>
    fetch('/api/cases')
      .then(r=>r.json())
      .then(d=>{const arr=d.data||[];setCases(arr);if(!caseId && arr.length) setCaseId(String(arr[0].id));});
  const createCase = () => {
    if(!newCase.trim()) return;
    fetch('/api/cases',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:newCase})})
      .then(()=>{setNewCase('');refreshCases();});
  };
  const deleteCase = () => {
    if(!caseId) return;
    fetch('/api/cases',{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:caseId})})
      .then(()=>{setCaseId('');refreshCases();setEvents([]);});
  };
  const loadTimeline = () => {
    if(!caseId) return;
    fetch('/api/timeline?query='+encodeURIComponent(caseId)).then(r=>r.json()).then(d=>setEvents(d.data||[]));
    fetch('/api/calendar?case_id='+encodeURIComponent(caseId)).then(r=>r.json()).then(d=>setCalendarEvents(d.data||[]));
  };
  useEffect(()=>{listAll();refreshCases();}, []);
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
        <select value={caseId} onChange={e=>setCaseId(e.target.value)} className="p-1 rounded">
          <option value="">Select case...</option>
          {cases.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input type="text" value={newCase} onChange={e=>setNewCase(e.target.value)} className="p-1 rounded" placeholder="New case" />
        <button className="button-secondary" onClick={createCase}><i className="fa fa-plus mr-1"></i>Create</button>
        <button className="button-secondary" onClick={refreshCases}><i className="fa fa-sync mr-1"></i>Refresh</button>
        <button className="button-secondary" onClick={deleteCase}><i className="fa fa-trash mr-1"></i>Delete</button>
      </div>
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
        <button className="button-secondary" onClick={loadTimeline}><i className="fa fa-clock mr-1"></i>Load Timeline</button>
      </div>
      <div ref={containerRef} style={{height:'200px'}}></div>
      <div className="mt-4">
        <h3 className="font-bold mb-1">Case Calendar</h3>
        <Calendar
          value={newEventDate}
          onClickDay={(val)=>setNewEventDate(val)}
          tileContent={({ date }) => calendarEvents.some(e=>e.date===date.toISOString().slice(0,10)) ? <span className="dot"></span> : null}
        />
        <div className="flex flex-wrap gap-2 mt-2">
          <input type="text" value={newEventTitle} onChange={e=>setNewEventTitle(e.target.value)} className="p-1 rounded" placeholder="Event title" />
          <button className="button-secondary" onClick={()=>{
            fetch('/api/calendar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({case_id:caseId,date:newEventDate.toISOString().slice(0,10),title:newEventTitle})})
              .then(()=>{setNewEventTitle('');loadTimeline();});
          }}><i className="fa fa-plus mr-1"></i>Add</button>
        </div>
        <ul className="list-disc list-inside text-sm mt-2">
          {calendarEvents.map(ev=>(
            <li key={ev.id}>{ev.date} - {ev.title}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
export default CaseManagementSection;
