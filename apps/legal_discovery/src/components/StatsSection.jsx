import React, { useState, useEffect } from "react";
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
export default StatsSection;
