import React, { useState, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { io } from 'socket.io-client';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function DocumentViewer({ mode, docId }) {
  const [page, setPage] = useState(1);
  const [numPages, setNumPages] = useState(null);
  const [zoom, setZoom] = useState(1.0);
  const socketRef = useRef(null);

  useEffect(() => {
    const s = io('/present');
    s.emit('join', { doc_id: docId, role: mode });
    s.on('command', (data) => {
      if (data.doc_id !== docId) return;
      if (data.command === 'goto_page' && typeof data.page === 'number') {
        setPage(data.page);
      } else if (data.command === 'zoom' && typeof data.zoom === 'number') {
        setZoom(data.zoom);
      }
    });
    socketRef.current = s;
    return () => s.disconnect();
  }, [docId, mode]);

  const sendCommand = (command, payload) => {
    if (mode !== 'presenter' || !socketRef.current) return;
    socketRef.current.emit('command', { doc_id: docId, command, ...payload });
  };

  const onLoad = ({ numPages: np }) => setNumPages(np);

  const nextPage = () => {
    const next = Math.min(page + 1, numPages || page + 1);
    setPage(next);
    sendCommand('goto_page', { page: next });
  };
  const prevPage = () => {
    const prev = Math.max(page - 1, 1);
    setPage(prev);
    sendCommand('goto_page', { page: prev });
  };
  const zoomIn = () => {
    const z = zoom + 0.1;
    setZoom(z);
    sendCommand('zoom', { zoom: z });
  };
  const zoomOut = () => {
    const z = Math.max(zoom - 0.1, 0.1);
    setZoom(z);
    sendCommand('zoom', { zoom: z });
  };

  return (
    <div className="flex flex-col items-center p-4 gap-2">
      {mode === 'presenter' && (
        <div className="flex gap-2">
          <button className="button-secondary" onClick={prevPage}>Prev</button>
          <button className="button-primary" onClick={nextPage}>Next</button>
          <button className="button-secondary" onClick={zoomOut}>-</button>
          <button className="button-secondary" onClick={zoomIn}>+</button>
        </div>
      )}
      <Document file={`/uploads/${docId}`} onLoadSuccess={onLoad} loading="Loading PDF…">
        <Page pageNumber={page} scale={zoom} />
      </Document>
      <p className="text-sm">Page {page}{numPages ? ` / ${numPages}` : ''}</p>
    </div>
  );
}

export default DocumentViewer;
