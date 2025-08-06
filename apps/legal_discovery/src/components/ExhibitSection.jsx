import React, { useState, useEffect } from "react";
import { fetchJSON, alertResponse } from "../utils";

function ExhibitSection() {
  const [caseId, setCaseId] = useState(1);
  const [docId, setDocId] = useState("");
  const [title, setTitle] = useState("");
  const [exhibits, setExhibits] = useState([]);
  const [links, setLinks] = useState({ binder: "", zip: "" });

  const load = () => {
    fetchJSON(`/api/exhibits?case_id=${caseId}`).then(setExhibits);
  };

  useEffect(() => {
    load();
  }, [caseId]);

  const assign = () => {
    fetchJSON("/api/exhibits/assign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: Number(docId), title }),
    }).then((d) => {
      alertResponse(d);
      load();
    });
  };

  const exportBinder = () => {
    fetchJSON("/api/exhibits/binder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId }),
    }).then((d) => {
      alertResponse(d);
      setLinks((l) => ({ ...l, binder: d.binder_path }));
    });
  };

  const exportZip = () => {
    fetchJSON("/api/exhibits/zip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: caseId }),
    }).then((d) => {
      alertResponse(d);
      setLinks((l) => ({ ...l, zip: d.zip_path }));
    });
  };

  return (
    <section className="card">
      <h2>Exhibits</h2>
      <div className="mb-2 flex gap-2">
        <input
          type="number"
          value={caseId}
          onChange={(e) => setCaseId(Number(e.target.value))}
          className="w-24 p-2 rounded"
          placeholder="Case"
        />
        <input
          type="number"
          value={docId}
          onChange={(e) => setDocId(e.target.value)}
          className="w-24 p-2 rounded"
          placeholder="Doc ID"
        />
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="flex-1 p-2 rounded"
          placeholder="Title"
        />
        <button className="button-secondary" onClick={assign}>
          <i className="fa fa-tag mr-1"></i>
          Assign
        </button>
      </div>
      <table className="w-full exhibit-table text-sm">
        <thead>
          <tr>
            <th>Order</th>
            <th>No.</th>
            <th>Title</th>
            <th>Bates</th>
            <th>Pages</th>
            <th>Priv</th>
          </tr>
        </thead>
        <tbody>
          {exhibits.map((ex) => (
            <tr key={ex.id} className={ex.privileged ? "privileged" : ""}>
              <td>{ex.order}</td>
              <td>{ex.exhibit_number}</td>
              <td>{ex.title}</td>
              <td>{ex.bates_number || ""}</td>
              <td>{ex.page_count}</td>
              <td>{ex.privileged ? "Y" : "N"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2 flex gap-2">
        <button className="button-secondary" onClick={exportBinder}>
          <i className="fa fa-book mr-1"></i>
          Binder
        </button>
        <button className="button-secondary" onClick={exportZip}>
          <i className="fa fa-file-archive mr-1"></i>
          ZIP
        </button>
      </div>
      <div className="mt-2 text-xs">
        {links.binder && (
          <p>
            Binder: <a href={links.binder}>{links.binder}</a>
          </p>
        )}
        {links.zip && (
          <p>
            ZIP: <a href={links.zip}>{links.zip}</a>
          </p>
        )}
      </div>
    </section>
  );
}

export default ExhibitSection;
