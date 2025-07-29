import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
function PipelineSection() {
  const [metrics,setMetrics] = useState({files:0,vectors:0,graph:0,tasks:0,logs:0});
  const refresh = () => {
    fetchJSON('/api/progress').then(d=>setMetrics(m=>({...m,files:d.data.uploaded_files||0})));
    fetchJSON('/api/vector/count').then(d=>setMetrics(m=>({...m,vectors:d.data||0})));
    fetchJSON('/api/tasks').then(d=>setMetrics(m=>({...m,tasks:(d.data||[]).length})));
    fetchJSON('/api/graph').then(d=>setMetrics(m=>({...m,graph:(d.data.nodes||[]).length})));
    fetchJSON('/api/forensic/logs').then(d=>setMetrics(m=>({...m,logs:(d.data||[]).length})));
  };
  useEffect(refresh, []);
  return (
    <section className="card">
      <h2>Team Pipeline</h2>
      <div className="pipeline">
        <div className="stage"><span>Ingestion</span><span>{metrics.files}</span></div>
        <div className="stage"><span>Forensics</span><span>{metrics.logs}</span></div>
        <div className="stage"><span>Vector DB</span><span>{metrics.vectors}</span></div>
        <div className="stage"><span>Graph</span><span>{metrics.graph}</span></div>
        <div className="stage"><span>Tasks</span><span>{metrics.tasks}</span></div>
      </div>
      <button className="button-secondary mt-2" onClick={refresh}><i className="fa fa-sync mr-1"></i>Refresh</button>
    </section>
  );
}
export default PipelineSection;
