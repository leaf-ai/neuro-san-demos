import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
import MetricCard from "./MetricCard";
function OverviewSection() {
  const [progress,setProgress] = useState({uploaded_files:0});
  const [tasks,setTasks] = useState([]);
  const [vector,setVector] = useState(0);
  const [graph,setGraph] = useState(0);
  useEffect(() => {
    fetchJSON('/api/progress').then(d=>setProgress(d.data||{}));
    fetchJSON('/api/tasks').then(d=>setTasks(d.data||[]));
    fetchJSON('/api/vector/count').then(d=>setVector(d.data||0));
    fetchJSON('/api/graph').then(d=>setGraph((d.data.nodes||[]).length||0));
  }, []);
  return (
    <section className="card">
      <h2>Overview</h2>
      <div className="metrics-grid">
        <MetricCard icon="fa-file-alt" label="Files" value={progress.uploaded_files||0} />
        <MetricCard icon="fa-tasks" label="Tasks" value={tasks.length||0} />
        <MetricCard icon="fa-database" label="Vectors" value={vector} />
        <MetricCard icon="fa-project-diagram" label="Graph" value={graph} />
      </div>
    </section>
  );
}
export default OverviewSection;
