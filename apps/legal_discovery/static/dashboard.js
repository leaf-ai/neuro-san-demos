function fetchFiles() {
  fetch('/api/files')
    .then(r => r.json())
    .then(d => buildTree(document.getElementById('file-tree'), d.data));
}

function buildTree(el, nodes) {
  if (!nodes) return;
  const ul = document.createElement('ul');
  nodes.forEach(n => {
    const li = document.createElement('li');
    li.textContent = n.name;
    if (n.children) buildTree(li, n.children);
    ul.appendChild(li);
  });
  el.appendChild(ul);
}

function upload() {
  const files = document.getElementById('file-input').files;
  if (!files.length) return;
  const fd = new FormData();
  for (const f of files) fd.append('files', f, f.webkitRelativePath || f.name);
  fetch('/api/upload', { method:'POST', body:fd })
    .then(r => r.json())
    .then(_ => fetchFiles());
}

function exportAll() {
  window.open('/api/export', '_blank');
}

function loadTimeline() {
  const query = document.getElementById('timeline-query').value;
  fetch('/api/timeline?query=' + encodeURIComponent(query))
    .then(r => r.json())
    .then(d => renderTimeline(d.data));
}

function renderTimeline(items) {
  const container = document.getElementById('timeline');
  container.innerHTML='';
  const dataset = new vis.DataSet(items.map(e => ({id:e.id, content:e.description, start:e.date, citation:e.citation})));
  const timeline = new vis.Timeline(container, dataset, {});
  timeline.on('click', props => {
    const item = dataset.get(props.item);
    if (item && item.citation) {
      const modal = document.getElementById('modal');
      modal.querySelector('iframe').src = item.citation;
      modal.style.display='flex';
    }
  });
}

function loadGraph() {
  fetch('/api/graph')
    .then(r => r.json())
    .then(d => {
      const cy = cytoscape({ container: document.getElementById('graph'), elements: [] });
      cy.add(d.data.nodes.map(n => ({ data:{ id:n.id, label:n.labels[0] }})));
      cy.add(d.data.edges.map(e => ({ data:{ id:e.source+'_'+e.target, source:e.source, target:e.target }})));
      cy.layout({ name:'breadthfirst', directed:true }).run();
    });
}

document.addEventListener('DOMContentLoaded', () => {
  fetchFiles();
  loadGraph();
  document.getElementById('upload-button').onclick = upload;
  document.getElementById('export-button').onclick = exportAll;
  document.getElementById('load-timeline').onclick = loadTimeline;
});
