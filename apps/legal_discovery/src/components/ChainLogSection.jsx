import React, { useState } from "react";

function ChainLogSection() {
  const [docId, setDocId] = useState("");
  const [events, setEvents] = useState([]);
  const load = () => {
    if (!docId) return;
    fetch(`/api/chain?document_id=${docId}`)
      .then((r) => r.json())
      .then((d) => setEvents(d.events || []));
  };
  return (
    <section className="card">
      <h2>Chain of Custody</h2>
      <input
        type="text"
        value={docId}
        onChange={(e) => setDocId(e.target.value)}
        className="w-full mb-2 p-2 rounded"
        placeholder="Document ID"
      />
      <button className="button-secondary mb-2" onClick={load}>
        <i className="fa fa-search mr-1"></i>Load
      </button>
      <ul className="text-sm">
        {events.map((e, i) => (
          <li key={i} className="mb-1">
            <span className="font-bold">{e.type}</span> {e.timestamp}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ChainLogSection;
