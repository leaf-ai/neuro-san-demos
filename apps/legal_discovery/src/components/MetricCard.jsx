import React from "react";
import { theme } from "../theme";

function MetricCard({ icon, label, value }) {
  return (
    <div className="metric-card">
      <i className={`fa ${icon} text-xl mb-1`} style={{ color: theme.colors.accent }}></i>
      <span className="value">{value}</span>
      <span className="label">{label}</span>
    </div>
  );
}

export default MetricCard;
