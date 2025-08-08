import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
function TimelineSection() {
  const [query,setQuery] = useState('');
  const [events,setEvents] = useState([]);
  const containerRef = useRef();
  const socketRef = useRef();
  const [exporting,setExporting] = useState(false);
  const [startDate,setStartDate] = useState('');
  const [endDate,setEndDate] = useState('');
  const load = () => {
    fetch('/api/timeline?query='+encodeURIComponent(query))
      .then(r=>r.json()).then(d=>setEvents(d.data||[]));
  };
  const exportTimeline = () => {
    setExporting(true);
    fetch('/api/export/report', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'timeline',timeline_id:query})})
      .then(r=>r.text()).then(html=>{const w=window.open('about:blank'); w.document.write(html);})
      .finally(()=>setExporting(false));
  };
  useEffect(() => {
    socketRef.current = io('/present');
    return () => socketRef.current && socketRef.current.disconnect();
  }, []);
  useEffect(() => {
    if(!containerRef.current) return;
    let filtered = events;
    if(startDate) filtered = filtered.filter(e=>e.date>=startDate);
    if(endDate) filtered = filtered.filter(e=>e.date<=endDate);
    if(!filtered.length) { containerRef.current.innerHTML=''; return; }
    const dataset = new vis.DataSet(filtered.map(e => ({
      id: e.id,
      content: e.description,
      start: e.date,
      citation: e.citation,
      excerpt: e.excerpt,
    })));
    
    const timeline = new vis.Timeline(containerRef.current, dataset, {});
    timeline.on('click', props => {
      const item = dataset.get(props.item);
      if(!item) return;
      const modal = document.getElementById('modal');
      const frame = modal.querySelector('iframe');
      if(item.citation) {
        frame.src = item.citation;
      } else if(item.excerpt) {
        frame.srcdoc = `<pre style="white-space:pre-wrap">${item.excerpt}</pre>`;
      } else {
        return;
      }
      modal.style.display='flex';
      if(item.doc_id && typeof item.page === 'number' && socketRef.current){
        socketRef.current.emit('command',{doc_id:item.doc_id,command:'goto_page',page:item.page});
      }
    });
  }, [events]);

  useEffect(() => {
    const handler = () => load();
    window.addEventListener('timelineRefresh', handler);
    return () => window.removeEventListener('timelineRefresh', handler);
  });
  return (
    <section className="card">
      <h2>Timeline</h2>
      <textarea rows="2" className="w-full mb-3 p-2 rounded" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Request events…"></textarea>
      <div className="flex gap-2 mb-2">
        <input type="date" value={startDate} onChange={e=>setStartDate(e.target.value)} className="p-1 rounded" />
        <input type="date" value={endDate} onChange={e=>setEndDate(e.target.value)} className="p-1 rounded" />
      </div>
      <div className="flex gap-2 mb-2">
        <button className="button-primary" onClick={load}>Load Timeline</button>
        <button className="button-secondary" onClick={exportTimeline}><i className="fa fa-file-export mr-1"></i>Export</button>
      </div>
      {exporting && <p className="text-sm mb-1">Exporting...</p>}
      <div ref={containerRef} style={{height:'200px'}}></div>
    </section>
  );
}
export default TimelineSection;
