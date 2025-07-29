import React, { useState } from "react";
import { fetchJSON, alertResponse } from "../utils";
function PresentationSection() {
  const [path,setPath] = useState('');
  const [slides,setSlides] = useState('');
  const [output,setOutput] = useState('');
  const create = () => {
    const slidesArr = slides.split('\n').map(l=>{const [t,...c]=l.split('|');return {title:t||'',content:c.join('|')||''};});
    fetchJSON('/api/presentation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filepath:path,slides:slidesArr})}).then(d=>{setOutput(d.output||'');alertResponse(d);});
  };
  return (
    <section className="card">
      <h2>Presentation</h2>
      <input type="text" value={path} onChange={e=>setPath(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="PPTX path" />
      <textarea rows="4" value={slides} onChange={e=>setSlides(e.target.value)} className="w-full mb-2 p-2 rounded" placeholder="title|content per line" />
      <button className="button-secondary" onClick={create}><i className="fa fa-slideshare mr-1"></i>Create/Update</button>
      {output && <p className="text-sm mt-2">Output: <a href={'/uploads/'+output} target="_blank" rel="noopener noreferrer">{output}</a></p>}
    </section>
  );
}

export default PresentationSection;