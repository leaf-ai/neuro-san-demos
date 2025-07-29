import React from "react";
function MetricCard({ icon, label, value }) {
  return (
    <div className="metric-card">
      <i className={`fa ${icon} text-xl mb-1`}></i>
      <span className="value">{value}</span>
      <span className="label">{label}</span>
    </div>
  );
}
export default MetricCard;
