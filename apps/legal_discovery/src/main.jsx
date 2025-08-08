import React from 'react';
import ReactDOM from 'react-dom/client';
import Dashboard from './Dashboard';
import DocumentViewer from './components/DocumentViewer';

const path = window.location.pathname.split('/');
const root = document.getElementById('root');

if (path[1] === 'present') {
  const mode = path[2];
  const docId = decodeURIComponent(path.slice(3).join('/'));
  ReactDOM.createRoot(root).render(
    <DocumentViewer mode={mode} docId={docId} />
  );
} else {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <Dashboard />
    </React.StrictMode>
  );
}
