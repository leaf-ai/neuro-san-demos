import React, { useState } from "react";
function ResearchSection() {
  const [q,setQ] = useState('');
  const [source,setSource] = useState('all');
  const [summary,setSummary] = useState('');
  const [cases,setCases] = useState([]);
  const [statutes,setStatutes] = useState('');
  const search = () => {
    fetch('/api/research?query='+encodeURIComponent(q)+'&source='+source)
      .then(r=>r.json())
      .then(d => {
        const data=d.data||{};
        setSummary(data.summary||'');
        setCases((data.cases&&data.cases.results)||[]);
        setStatutes(typeof data.statutes==='string'?data.statutes:'');
      });
  };
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
      {summary && <p className="mb-2 whitespace-pre-wrap text-sm">{summary}</p>}
      {cases.length>0 && <ul className="mb-2 list-disc list-inside text-sm">{cases.slice(0,5).map((c,i)=>(<li key={i}><a href={c.absolute_url} target="_blank" rel="noopener noreferrer">{c.caseName||c.short_name||c.absolute_url}</a></li>))}</ul>}
      {statutes && <pre className="text-sm max-h-40 overflow-y-auto">{statutes.slice(0,1000)}</pre>}
    </section>
  );
}

export default ResearchSection;
