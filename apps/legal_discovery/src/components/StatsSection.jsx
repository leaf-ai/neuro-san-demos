import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
function StatsSection() {
  const [stats, setStats] = useState({});
  const refresh = () => {
    fetchJSON('/api/metrics').then(d => setStats(d.data || {}));
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
      <button className="button-secondary mt-2" onClick={refresh}><i className="fa fa-sync mr-1"></i>Refresh</button>
    </section>
  );
}
export default StatsSection;