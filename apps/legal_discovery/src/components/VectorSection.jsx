import React, { useState } from "react";
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
export default VectorSection;
