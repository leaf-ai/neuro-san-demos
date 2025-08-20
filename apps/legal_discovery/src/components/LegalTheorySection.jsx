import React, { useEffect, useState } from "react";

function LegalTheorySection() {
  const [theories, setTheories] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    fetch("/api/theories/suggest").then(r => r.json()).then(d => {
      setTheories(d.theories || []);
      setLoading(false);
    });
  };

  const showGraph = (cause) => {
    window.dispatchEvent(new CustomEvent('loadTheoryGraph', { detail: { cause } }));
  };

  const act = (path, cause, extra={}) => {
    fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cause, ...extra })
    }).then(r=>r.json()).then(d=>{
      if(d.status==='ok'){
        load();
        window.dispatchEvent(new Event('graphRefresh'));
        window.dispatchEvent(new Event('timelineRefresh'));
      }
    });
  };

  const approve = (cause) => act('/api/theories/accept', cause);
  const reject = (cause) => act('/api/theories/reject', cause);
  const comment = (cause) => {
    const text = prompt('Comment on theory');
    if(text) act('/api/theories/comment', cause, { comment: text });
  };

  useEffect(() => { load(); }, []);

  return (
    <section className="card">
      <h2>
        Case Theory
        <i
          className="fa fa-question-circle ml-2 text-sm"
          title="Suggested causes of action with supporting evidence."
          aria-label="Case theory info"
        ></i>
      </h2>
      <p className="text-sm text-gray-600 mb-2">
        Approve, reject or comment on theories and inspect their supporting elements.
      </p>
      <button className="button-secondary mb-2" onClick={load} disabled={loading}>
        <i className="fa fa-sync mr-1"></i>{loading ? "Loading" : "Refresh"}
      </button>
      {theories.map(t => (
        <div key={t.cause} className="mb-4">
          <div className="flex items-center justify-between mb-1">
            <h3 className="font-bold">{t.cause} - {(t.score*100).toFixed(0)}%</h3>
            <button className="button-secondary" onClick={() => showGraph(t.cause)}>
              <i className="fa fa-project-diagram mr-1"></i>Graph
            </button>
          </div>
          <div className="theory-bar mb-2">
            <div className="theory-bar-fill" style={{width: `${t.score*100}%`}}></div>
          </div>
          <ul className="list-disc list-inside text-sm mb-2">
            {t.elements.map(e => (
              <li key={e.name} className={e.weight > 0 ? "theory-supported" : ""}>
                <div className="flex justify-between items-center">
                  <span>{e.name}</span>
                  <span className="text-xs text-gray-400">{(e.weight*100).toFixed(0)}%</span>
                </div>
                <div className="element-bar mt-1">
                  <div className="element-bar-fill" style={{width: `${e.weight*100}%`}}></div>
                </div>
              </li>
            ))}
          </ul>
          <div className="flex gap-2">
            <button className="button-primary" onClick={()=>approve(t.cause)}>Approve</button>
            <button className="button-secondary" onClick={()=>reject(t.cause)}>Reject</button>
            <button className="button-secondary" onClick={()=>comment(t.cause)}>Comment</button>
          </div>
        </div>
      ))}
    </section>
  );
}

export default LegalTheorySection;
