import React from 'react';

export default function ErrorBanner({ message, className = '' }) {
  if (!message) return null;
  return (
    <div className={`p-2 mb-2 text-sm text-red-100 bg-red-800 rounded ${className}`} role="alert">
      {message}
    </div>
  );
}
