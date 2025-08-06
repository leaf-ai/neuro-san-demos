import React, { useState, useEffect } from "react";
import { fetchJSON, alertResponse } from "../utils";

function ExhibitTab() {
  const [caseId, setCaseId] = useState(1);
  const [includePriv, setIncludePriv] = useState(false);
  const [source, setSource] = useState("");
  const [exhibits, setExhibits] = useState([]);

  const load = () => {
    const params = new URLSearchParams({ case_id: caseId });
    if (includePriv) params.set("include_privileged", "true");
    if (source) params.set("source", source);
    fetchJSON(`/api/exhibits?${params.toString()}`).then(async (items) => {
      const detailed = await Promise.all(
        items.map(async (ex) => {
          const links = await fetchJSON(`/api/exhibits/${ex.id}/links`);
          return { ...ex, ...links };
        })
      );
      setExhibits(detailed);
    });
  };

  useEffect(() => {
    load();
  }, [caseId, includePriv, source]);

  const onDragStart = (e, idx) => {
    e.dataTransfer.setData("text/plain", idx);
  };

  const onDrop = (e, idx) => {
    e.preventDefault();
    const from = e.dataTransfer.getData("text/plain");
    if (from === "") return;
    const list = [...exhibits];
    const [moved] = list.splice(Number(from), 1);
    list.splice(idx, 0, moved);
    setExhibits(list);
    fetchJSON("/api/exhibits/reorder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId, order: list.map((e) => e.id) }),
    }).then(alertResponse);
  };

  const allowDrop = (e) => e.preventDefault();

  return (
    <section className="card">
      <h2>Exhibits</h2>
      <div className="mb-2 flex gap-2 items-center">
        <input
          type="number"
          value={caseId}
          onChange={(e) => setCaseId(Number(e.target.value))}
          className="w-24 p-2 rounded"
        />
        <label className="flex items-center gap-1 text-sm">
          <input
            type="checkbox"
            checked={includePriv}
            onChange={(e) => setIncludePriv(e.target.checked)}
          />
          Include Privileged
        </label>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="p-2 rounded"
        >
          <option value="">All Sources</option>
          <option value="user">User</option>
          <option value="opp_counsel">Opposing Counsel</option>
          <option value="court">Court</option>
        </select>
        <button className="button-secondary" onClick={load}>
          <i className="fa fa-sync mr-1"></i>Refresh
        </button>
      </div>
      <ul>
        {exhibits.map((ex, idx) => (
          <li
            key={ex.id}
            draggable
            onDragStart={(e) => onDragStart(e, idx)}
            onDragOver={allowDrop}
            onDrop={(e) => onDrop(e, idx)}
            className={`p-2 mb-1 border rounded ${ex.privileged ? "privileged" : ""}`}
          >
            <div className="flex justify-between">
              <span>
                {ex.exhibit_number} - {ex.title}
              </span>
              <span className="text-xs">{ex.source}</span>
            </div>
            {ex.theories && ex.theories.length > 0 && (
              <div className="text-xs mt-1">
                <strong>Theories:</strong> {ex.theories.join(", ")}
              </div>
            )}
            {ex.timeline && ex.timeline.length > 0 && (
              <div className="text-xs mt-1">
                <strong>Timeline:</strong> {ex.timeline.map((t) => t.date).join(", ")}
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ExhibitTab;

