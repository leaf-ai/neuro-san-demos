import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
function PipelineSection() {
  const [metrics,setMetrics] = useState({files:0,vectors:0,graph:0,tasks:0,logs:0});
  const refresh = () => {
    fetchJSON('/api/metrics').then(d=>{
      const m=d.data||{};
      setMetrics({
        files:m.uploaded_files||0,
        vectors:m.vector_docs||0,
        graph:m.graph_nodes||0,
        tasks:m.task_count||0,
        logs:m.forensic_logs||0
      });
    });
  };
  useEffect(refresh, []);
  return (
    <section className="card">
      <h2>Team Pipeline</h2>
      <div className="pipeline">
        <div className="stage">
          <i className="fa fa-file-upload"></i>
          <span>Ingestion</span>
          <span className="count">{metrics.files}</span>
        </div>
        <div className="stage">
          <i className="fa fa-search-dollar"></i>
          <span>Forensics</span>
          <span className="count">{metrics.logs}</span>
        </div>
        <div className="stage">
          <i className="fa fa-database"></i>
          <span>Vector DB</span>
          <span className="count">{metrics.vectors}</span>
        </div>
        <div className="stage">
          <i className="fa fa-project-diagram"></i>
          <span>Graph</span>
          <span className="count">{metrics.graph}</span>
        </div>
        <div className="stage">
          <i className="fa fa-tasks"></i>
          <span>Tasks</span>
          <span className="count">{metrics.tasks}</span>
        </div>
      </div>
      <button className="button-secondary mt-2" onClick={refresh}><i className="fa fa-sync mr-1"></i>Refresh</button>
    </section>
  );
}
export default PipelineSection;