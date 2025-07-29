import React, { useState } from "react";
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

export default ResearchSection;
