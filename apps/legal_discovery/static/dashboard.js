function fetchFiles() {
  fetch('/api/files')
    .then(r => r.json())
    .then(d => buildTree(document.getElementById('file-tree'), d.data));
}

function buildTree(el, nodes) {
  if (!nodes) return;
  el.innerHTML = '';
  const ul = document.createElement('ul');
  nodes.forEach(n => {
    if (n.children) {
      const folder = document.createElement('li');
      folder.className = 'folder';
      const header = document.createElement('div');
      header.className = 'folder-header';
      const icon = document.createElement('i');
      icon.className = 'folder-icon fa fa-caret-right';
      const title = document.createElement('span');
      title.className = 'title';
      title.textContent = n.name;
      header.appendChild(icon);
      header.appendChild(title);
      folder.appendChild(header);
      const contents = document.createElement('div');
      contents.className = 'folder-contents';
      buildTree(contents, n.children);
      folder.appendChild(contents);
      header.onclick = () => {
        folder.classList.toggle('open');
        icon.classList.toggle('fa-caret-right', !folder.classList.contains('open'));
        icon.classList.toggle('fa-caret-down', folder.classList.contains('open'));
      };
      ul.appendChild(folder);
    } else {
      const file = document.createElement('li');
      file.className = 'file';
      file.textContent = n.name;
      file.onclick = () => window.open('/uploads/' + n.path, '_blank');
      ul.appendChild(file);
    }
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

function refreshStats() {
  fetch('/api/progress')
    .then(r => r.json())
    .then(d => {
      document.getElementById('upload-count').textContent = d.data.uploaded_files || 0;
    });
  fetch('/api/vector/count')
    .then(r => r.json())
    .then(d => {
      document.getElementById('vector-count').textContent = d.data || 0;
    });
}

function forensicAnalyze() {
  const path = document.getElementById('forensic-path').value;
  const analysis = document.getElementById('analysis-type').value;
  fetch('/api/agents/forensic_analysis', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({file_path: path, analysis_type: analysis})
  })
    .then(r => r.json())
    .then(d => alert(d.result || d.error || 'Done'));
}

function loadForensicLogs() {
  fetch('/api/forensic/logs')
    .then(r => r.json())
    .then(d => {
      document.getElementById('forensic-log').textContent = (d.data || []).join('\n');
    });
}

function researchSearch() {
  const q = document.getElementById('research-query').value;
  fetch('/api/research?query=' + encodeURIComponent(q))
    .then(r => r.json())
    .then(d => {
      document.getElementById('research-results').textContent = JSON.stringify(d.data, null, 2);
    });
}

function upload() {
  const files = document.getElementById('file-input').files;
  if (!files.length) return;
  const fd = new FormData();
  for (const f of files) fd.append('files', f, f.webkitRelativePath || f.name);
  fetch('/api/upload', { method:'POST', body:fd })
    .then(r => r.json())
    .then(_ => { fetchFiles(); refreshStats(); });
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
  refreshStats();
  document.getElementById('upload-button').onclick = upload;
  document.getElementById('export-button').onclick = exportAll;
  document.getElementById('load-timeline').onclick = loadTimeline;
  const orgBtn = document.getElementById('organized-button');
  if (orgBtn) orgBtn.onclick = fetchOrganized;

  const refreshBtn = document.getElementById('refresh-stats');
  if (refreshBtn) refreshBtn.onclick = refreshStats;

  const redactBtn = document.getElementById('redact-button');
  const stampBtn = document.getElementById('stamp-button');
  const vecSearchBtn = document.getElementById('vector-search-button');
  const extractBtn = document.getElementById('extract-text-button');
  const forensicBtn = document.getElementById('forensic-analyze');
  const forensicLogBtn = document.getElementById('load-forensic-logs');
  const researchBtn = document.getElementById('research-button');
  const addTaskBtn = document.getElementById('add-task');
  const listTaskBtn = document.getElementById('list-tasks');
  const clearTaskBtn = document.getElementById('clear-tasks');
  if (redactBtn) redactBtn.onclick = redact;
  if (stampBtn) stampBtn.onclick = stamp;
  if (vecSearchBtn) vecSearchBtn.onclick = vectorSearch;
  if (extractBtn) extractBtn.onclick = extractText;
  if (forensicBtn) forensicBtn.onclick = forensicAnalyze;
  if (forensicLogBtn) forensicLogBtn.onclick = loadForensicLogs;
  if (researchBtn) researchBtn.onclick = researchSearch;
  if (addTaskBtn) addTaskBtn.onclick = addTask;
  if (listTaskBtn) listTaskBtn.onclick = listTasks;
  if (clearTaskBtn) clearTaskBtn.onclick = clearTasks;
  setupTabs();
  setupSettingsModal();
  setupChat();
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

function setupTabs() {
  const buttons = document.querySelectorAll('.tab-button');
  const contents = document.querySelectorAll('.tab-content');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      contents.forEach(c => c.classList.remove('active'));
      buttons.forEach(b => b.classList.remove('active'));
      document.getElementById(btn.dataset.target).classList.add('active');
      btn.classList.add('active');
    });
  });
  if (buttons.length) buttons[0].click();
}

let socket;
function setupChat() {
  socket = io('/chat');
  socket.on('update_thoughts', d => addMessage('thought', d.data));
  socket.on('update_speech', d => addMessage('speech', d.data));
  socket.on('update_user_input', d => addMessage('user', d.data));
  document.getElementById('chat-send').onclick = sendChat;
}

function addMessage(type, text) {
  const box = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = type === 'user' ? 'user-msg' : type === 'speech' ? 'speech-msg' : 'thought-msg';
  div.innerHTML = text.replace(/\n/g, '<br>');
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function sendChat() {
  const input = document.getElementById('chat-input');
  const txt = input.value.trim();
  if (!txt) return;
  socket.emit('user_input', {data: txt}, '/chat');
  input.value = '';
}

function setupSettingsModal() {
  const modal = document.getElementById('settings-modal');
  const btn = document.getElementById('settings-btn');
  const span = modal.querySelector('.close-btn');
  btn.onclick = () => {
    modal.style.display = 'block';
    fetch('/api/settings')
      .then(r => r.json())
      .then(d => {
        document.getElementById('courtlistener-api-key').value = d.courtlistener_api_key || '';
        document.getElementById('gemini-api-key').value = d.gemini_api_key || '';
        document.getElementById('california-codes-url').value = d.california_codes_url || '';
      });
  };
  span.onclick = () => { modal.style.display = 'none'; };
  window.onclick = e => { if (e.target === modal) modal.style.display = 'none'; };
  document.getElementById('settings-form').addEventListener('submit', e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)})
      .then(() => { modal.style.display = 'none'; });
  });
}
