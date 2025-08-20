import React, { useState } from "react";
import { fetchJSON, alertResponse } from "../utils";
import ErrorBoundary from "./ErrorBoundary";
import Spinner from "./common/Spinner";
import ErrorBanner from "./common/ErrorBanner";

function PresentationSection() {
  const [path,setPath] = useState('');
  const [slides,setSlides] = useState('');
  const [output,setOutput] = useState('');
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState(null);
  const create = () => {
    const slidesArr = slides.split('\n').map(l=>{const [t,...c]=l.split('|');return {title:t||'',content:c.join('|')||''};});
    setLoading(true);
    setError(null);
    fetchJSON('/api/presentation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filepath:path,slides:slidesArr})})
      .then(d=>{setOutput(d.output||'');alertResponse(d);})
      .catch(e=>setError(e.message || 'Creation failed'))
      .finally(()=>setLoading(false));
  };
  return (
    <ErrorBoundary>
      <section className="card">
        <h2>Presentation</h2>
        <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="PPTX path" />
        <textarea rows="4" value={slides} onChange={e=>setSlides(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="title|content per line" />
        <button className="button-secondary" onClick={create}><i className="fa fa-slideshare mr-1"></i>Create/Update</button>
        {loading && <Spinner />}
        {error && <ErrorBanner message={error} />}
        {output && <p className="text-sm mt-2">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
      </section>
    </ErrorBoundary>
  );
}

export default PresentationSection;
