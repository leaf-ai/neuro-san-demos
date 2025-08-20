import React, { useState, useEffect } from "react";
import { fetchJSON, alertResponse } from "../utils";
import { theme } from "../theme";

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
      <div className="flex items-center" style={{ gap: theme.spacing.sm, marginBottom: theme.spacing.sm }}>
        <input
          type="number"
          value={caseId}
          onChange={(e) => setCaseId(Number(e.target.value))}
          className="w-24"
          style={{ padding: theme.spacing.sm, borderRadius: theme.spacing.xs }}
        />
        <label className="flex items-center" style={{ gap: theme.spacing.xs, fontSize: theme.typography.sizeSm }}>
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
          style={{ padding: theme.spacing.sm, borderRadius: theme.spacing.xs }}
        >
          <option value="">All Sources</option>
          <option value="user">User</option>
          <option value="opp_counsel">Opposing Counsel</option>
          <option value="court">Court</option>
        </select>
        <button className="button-secondary" style={{ padding: theme.spacing.xs }} onClick={load}>
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
            className={`${ex.privileged ? "privileged" : ""}`}
            style={{ padding: theme.spacing.sm, marginBottom: theme.spacing.xs, border: `1px solid ${theme.colors.border}`, borderRadius: theme.spacing.xs }}
          >
            <div className="flex justify-between" style={{ marginBottom: theme.spacing.xs }}>
              <span>
                {ex.exhibit_number} - {ex.title}
              </span>
              <span style={{ fontSize: theme.typography.sizeSm }}>{ex.source}</span>
            </div>
            {ex.theories && ex.theories.length > 0 && (
              <div style={{ fontSize: theme.typography.sizeSm, marginTop: theme.spacing.xs }}>
                <strong>Theories:</strong> {ex.theories.join(", ")}
              </div>
            )}
            {ex.timeline && ex.timeline.length > 0 && (
              <div style={{ fontSize: theme.typography.sizeSm, marginTop: theme.spacing.xs }}>
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

