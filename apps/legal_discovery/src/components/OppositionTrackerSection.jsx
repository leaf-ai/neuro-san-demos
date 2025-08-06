import React, { useEffect, useState } from "react";

function OppositionTrackerSection() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState(0);

  useEffect(() => {
    fetch("/api/narrative_discrepancies")
      .then((res) => res.json())
      .then(setItems);
  }, []);

  const filtered = items.filter((i) => i.confidence >= filter);

  const flag = (c) => {
    if (c >= 0.8) return "text-red-400";
    if (c >= 0.5) return "text-yellow-400";
    return "text-green-400";
  };

  const exportData = (fmt) => {
    window.open(`/api/narrative_discrepancies/export?format=${fmt}`, "_blank");
  };

  return (
    <div className="card">
      <h2 className="mb-2">Narrative Discrepancies</h2>
      <div className="mb-2 flex gap-2 items-center">
        <label>Min Confidence</label>
        <select
          value={filter}
          onChange={(e) => setFilter(parseFloat(e.target.value))}
          className="bg-gray-800 text-white p-1"
        >
          <option value={0}>0%</option>
          <option value={0.5}>50%</option>
          <option value={0.8}>80%</option>
        </select>
        <button className="btn" onClick={() => exportData("csv")}>CSV</button>
        <button className="btn" onClick={() => exportData("pdf")}>PDF</button>
      </div>
      <table className="table-auto w-full text-sm">
        <thead>
          <tr>
            <th className="text-left p-2">Claim</th>
            <th className="text-left p-2">Evidence</th>
            <th className="text-left p-2">Conf.</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((i) => (
            <tr key={i.id}>
              <td className="p-2 w-1/3">{i.conflicting_claim}</td>
              <td className="p-2 w-1/2">{i.evidence_excerpt}</td>
              <td className={`p-2 ${flag(i.confidence)}`}>
                {(i.confidence * 100).toFixed(1)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default OppositionTrackerSection;
