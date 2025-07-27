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
    if (n.children) {
      buildTree(li, n.children);
    } else {
      li.onclick = () => window.open('/uploads/' + n.path, '_blank');
    }
    ul.appendChild(li);
  });
  el.appendChild(ul);
}

function fetchOrganized() {
  fetch('/api/organized-files')
    .then(r => r.json())
    .then(d => {
      const container = document.getElementById('organized-tree');
      container.innerHTML = '';
      Object.entries(d.data).forEach(([cat, nodes]) => {
        const section = document.createElement('div');
        const h3 = document.createElement('h3');
        h3.textContent = cat;
        section.appendChild(h3);
        buildTree(section, nodes);
        container.appendChild(section);
      });
    });
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
  const orgBtn = document.getElementById('organized-button');
  if (orgBtn) orgBtn.onclick = fetchOrganized;

  const redactBtn = document.getElementById('redact-button');
  const stampBtn = document.getElementById('stamp-button');
  const vecSearchBtn = document.getElementById('vector-search-button');
  const extractBtn = document.getElementById('extract-text-button');
  const addTaskBtn = document.getElementById('add-task');
  const listTaskBtn = document.getElementById('list-tasks');
  const clearTaskBtn = document.getElementById('clear-tasks');
  if (redactBtn) redactBtn.onclick = redact;
  if (stampBtn) stampBtn.onclick = stamp;
  if (vecSearchBtn) vecSearchBtn.onclick = vectorSearch;
  if (extractBtn) extractBtn.onclick = extractText;
  if (addTaskBtn) addTaskBtn.onclick = addTask;
  if (listTaskBtn) listTaskBtn.onclick = listTasks;
  if (clearTaskBtn) clearTaskBtn.onclick = clearTasks;
});

function redact() {
  const path = document.getElementById('doc-path').value;
  const text = document.getElementById('redact-text').value;
  fetch('/api/document/redact', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({file_path: path, text})
  })
    .then(r => r.json())
    .then(alertResponse);
}

function stamp() {
  const path = document.getElementById('doc-path').value;
  const prefix = document.getElementById('stamp-prefix').value;
  fetch('/api/document/stamp', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({file_path: path, prefix})
  })
    .then(r => r.json())
    .then(alertResponse);
}

function vectorSearch() {
  const q = document.getElementById('vector-query').value;
  fetch('/api/vector/search?q=' + encodeURIComponent(q))
    .then(r => r.json())
    .then(d => {
      document.getElementById('vector-results').textContent = JSON.stringify(d.data, null, 2);
    });
}

function extractText() {
  const path = document.getElementById('doc-path').value;
  fetch('/api/document/text', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({file_path: path})
  })
    .then(r => r.json())
    .then(d => {
      document.getElementById('extracted-text').textContent = d.data || '';
    });
}

function addTask() {
  const task = document.getElementById('task-input').value;
  fetch('/api/tasks', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task})
  })
    .then(r => r.json())
    .then(alertResponse);
}

function listTasks() {
  fetch('/api/tasks')
    .then(r => r.json())
    .then(d => {
      document.getElementById('task-list').textContent = d.data || '';
    });
}

function clearTasks() {
  fetch('/api/tasks', {method:'DELETE'})
    .then(r => r.json())
    .then(d => {
      document.getElementById('task-list').textContent = '';
      alert(d.message || 'Cleared');
    });
}

function alertResponse(d) {
  alert(d.message || 'Done');
}
