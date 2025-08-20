import React from 'react';

export default function Spinner({ className = '' }) {
  return (
    <div className={`flex items-center justify-center ${className}`} role="status">
      <i className="fa fa-spinner fa-spin mr-2" />
      <span className="sr-only">Loading...</span>
    </div>
  );
}
