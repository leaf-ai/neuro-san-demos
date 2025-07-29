import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
function StatsSection() {
  const [stats, setStats] = useState({});
  const refresh = () => {
    fetchJSON('/api/metrics').then(d => setStats(d.data || {}));
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
      <p className="mb-1">Cases: <span>{stats.case_count || 0}</span></p>
      <p className="mb-1">Uploaded files: <span>{stats.uploaded_files || 0}</span></p>
      <p className="mb-1">Vector documents: <span>{stats.vector_docs || 0}</span></p>
      <p className="mb-1">Graph nodes: <span>{stats.graph_nodes || 0}</span></p>
      <p>Tasks: <span>{stats.task_count || 0}</span></p>
      <p className="mb-1">Uploaded files: <span>{uploaded}</span></p>
      <p>Vector documents: <span>{vectorCount}</span></p>
      <button className="button-secondary mt-2" onClick={refresh}><i className="fa fa-sync mr-1"></i>Refresh</button>
    </section>
  );
}
export default StatsSection;