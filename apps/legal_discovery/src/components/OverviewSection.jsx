import React, { useState, useEffect } from "react";
import { fetchJSON } from "../utils";
function OverviewSection() {
  const [progress,setProgress] = useState({uploaded_files:0});
  const [tasks,setTasks] = useState([]);
  const [vector,setVector] = useState(0);
  useEffect(() => {
    fetchJSON('/api/progress').then(d=>setProgress(d.data||{}));
    fetchJSON('/api/tasks').then(d=>setTasks(d.data||[]));
    fetchJSON('/api/vector/count').then(d=>setVector(d.data||0));
  }, []);
  return (
    <section className="card">
      <h2>Overview</h2>
      <p className="mb-1">Uploaded Files: {progress.uploaded_files||0}</p>
      <p className="mb-1">Open Tasks: {tasks.length||0}</p>
      <p className="mb-1">Vector Docs: {vector}</p>
    </section>
  );
}
export default OverviewSection;
