import React, { useState, useEffect, useRef, useCallback } from "react";
import { fetchJSON } from "../utils";
/* global cytoscape */
function GraphSection() {
  const [nodes,setNodes] = useState([]);
  const [edges,setEdges] = useState([]);
  const [subnet,setSubnet] = useState('');
  const [search,setSearch] = useState('');
  const [cypher,setCypher] = useState('');
  const [cypherResult,setCypherResult] = useState(null);
  const cyRef = useRef(null);
  const [exporting,setExporting] = useState(false);
  const [analysis,setAnalysis] = useState([]);
  const load = useCallback(() => {
    const url = '/api/graph' + (subnet?`?subnet=${encodeURIComponent(subnet)}`:'');
    fetchJSON(url).then(d=>{setNodes(d.data.nodes||[]);setEdges(d.data.edges||[]);});
  }, [subnet]);
  useEffect(load, []);
  useEffect(() => {
    const handler = () => load();
    window.addEventListener('graphRefresh', handler);
    return () => window.removeEventListener('graphRefresh', handler);
  }, [load]);

  useEffect(() => {
    const handler = (e) => {
      const cause = e.detail && e.detail.cause;
      if (!cause) return;
      fetchJSON(`/api/theories/graph?cause=${encodeURIComponent(cause)}`).then(d => {
        setNodes(d.nodes || []);
        setEdges(d.edges || []);
      });
    };
    window.addEventListener('loadTheoryGraph', handler);
    return () => window.removeEventListener('loadTheoryGraph', handler);
  }, []);
  useEffect(() => {
    if(!nodes.length && !edges.length) return;
    const cy = cytoscape({
      container: document.getElementById('graph'),
      elements: [],
      style:[
        { selector:'node', style:{ label:'data(label)', 'background-color':'#64748b', color:'#fff' } },
        { selector:'.highlight', style:{ 'background-color':'#f97316', color:'#fff' } }
      ]
    });
    cy.add(nodes.map(n => ({ data:{ id:n.id, label:(n.labels||[''])[0] }})));
    cy.add(edges.map(e => ({ data:{ id:e.source+'_'+e.target, source:e.source, target:e.target }})));
    cy.layout({ name:'breadthfirst', directed:true }).run();
    cyRef.current = cy;
  }, [nodes,edges]);
  const highlight = () => {
    if(!cyRef.current) return;
    const node = cyRef.current.getElementById(search);
    if(node) {
      cyRef.current.elements().removeClass('highlight');
      node.addClass('highlight');
      cyRef.current.center(node);
    }
  };
  const exportGraph = () => {
    setExporting(true);
    fetch('/api/graph/export')
      .then(r=>r.text()).then(html=>{const w=window.open('about:blank'); w.document.write(html);})
      .finally(()=>setExporting(false));
  };
  const analyze = () => {
    const url = '/api/graph/analyze' + (subnet?`?subnet=${encodeURIComponent(subnet)}`:'');
    fetchJSON(url).then(d=>setAnalysis(d.data||[]));
  };
  const runCypher = (preset) => {
    const query = preset || cypher;
    if(!query) return;
    fetch('/api/graph/cypher',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query})})
      .then(r=>r.json()).then(d=>setCypherResult(d.data||d.error||null));
  };
  return (
    <section className="card">
      <h2>Knowledge Graph</h2>
      <div className="flex flex-wrap gap-2 mb-2">
        <input type="text" value={subnet} onChange={e=>setSubnet(e.target.value)} placeholder="subnet" className="p-1 rounded" />
        <button className="button-secondary" onClick={load}><i className="fa fa-sync mr-1"></i>Load</button>
        <input type="text" value={search} onChange={e=>setSearch(e.target.value)} placeholder="find node" className="p-1 rounded" />
        <button className="button-secondary" onClick={highlight}><i className="fa fa-search mr-1"></i>Find</button>
        <button className="button-secondary" onClick={exportGraph}><i className="fa fa-file-export mr-1"></i>Export</button>
        <button className="button-secondary" onClick={analyze}><i className="fa fa-network-wired mr-1"></i>Analyze</button>
      </div>
      <div className="flex flex-wrap gap-2 mb-2">
        <textarea value={cypher} onChange={e=>setCypher(e.target.value)} placeholder="MATCH (n) RETURN n LIMIT 25" className="p-1 rounded flex-1" rows={2}></textarea>
        <div className="flex flex-col gap-2">
          <button className="button-secondary" onClick={()=>runCypher()}>Run</button>
          <button className="button-secondary" onClick={()=>runCypher("MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50")}>Populate</button>
          <button className="button-secondary" onClick={()=>runCypher("MATCH (d:Document) WHERE d.category='fraud' RETURN d LIMIT 25")}>Fraud</button>
          <button className="button-secondary" onClick={()=>runCypher("MATCH (d:Document) WHERE d.category='financial' RETURN d LIMIT 25")}>Financial Docs</button>
        </div>
      </div>
      {exporting && <p className="text-sm mb-1">Exporting...</p>}
      <div id="graph" style={{height:'300px', border:'1px solid var(--border-colour)'}}></div>
      {cypherResult && (
        <pre className="mt-2 p-2 text-xs overflow-x-auto" style={{background:'rgba(0,0,0,0.3)'}}>{JSON.stringify(cypherResult,null,2)}</pre>
      )}
      {!!analysis.length && (
        <div className="mt-2 text-sm">
          <h3 className="font-bold mb-1">Central Entities</h3>
          <ul className="list-disc list-inside">
            {analysis.map(a=>(
              <li key={a.id}>{a.id}: {a.score}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
export default GraphSection;
