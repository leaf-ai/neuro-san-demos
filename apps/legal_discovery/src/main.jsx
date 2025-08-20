import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom';
import { AppProvider } from './AppContext';
import Dashboard from './Dashboard';
import DocumentViewer from './components/DocumentViewer';

function DocumentViewerWrapper() {
  const { mode, '*': docId } = useParams();
  return <DocumentViewer mode={mode} docId={decodeURIComponent(docId)} />;
}

const root = document.getElementById('root');
ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/present/:mode/*" element={<DocumentViewerWrapper />} />
          <Route path="/*" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  </React.StrictMode>
);
