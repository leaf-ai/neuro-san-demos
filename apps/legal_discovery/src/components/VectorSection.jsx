import React, { useState } from "react";
import ErrorBoundary from "./ErrorBoundary";
import Spinner from "./common/Spinner";
import ErrorBanner from "./common/ErrorBanner";

function VectorSection() {
  const [q,setQ] = useState('');
  const [results,setResults] = useState([]);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState(null);
  const search = () => {
    setLoading(true);
    setError(null);
    fetch('/api/vector/search?q='+encodeURIComponent(q))
      .then(r=>r.json())
      .then(d=>{
        const data=d.data||{};
        const docs=(data.documents&&data.documents[0])||[];
        const ids=(data.ids&&data.ids[0])||[];
        const items=docs.map((t,i)=>({id:ids[i]||i,text:t}));
        setResults(items);
      })
      .catch(e=>setError(e.message || 'Search failed'))
      .finally(()=>setLoading(false));
  };
  return (
    <ErrorBoundary>
      <section className="card">
        <h2>Vector Search</h2>
        <input type="text" value={q} onChange={e=>setQ(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="Search text" />
        <button className="button-secondary mb-2" onClick={search}><i className="fa fa-search mr-1"></i>Search</button>
        {loading && <Spinner />}
        {error && <ErrorBanner message={error} />}
        <ul className="text-sm list-disc list-inside">
          {results.map((r,i)=>(<li key={i}><strong>{r.id}:</strong> {r.text}</li>))}
        </ul>
      </section>
    </ErrorBoundary>
  );
}
export default VectorSection;
