document.addEventListener('DOMContentLoaded', () => {
  const cy = cytoscape({
    container: document.getElementById('graph-container'),
    elements: [
      { data: { id: 'Case Files' } },
      { data: { id: 'Briefs' } },
      { data: { id: 'complaint.pdf' } },
      { data: { id: 'evidence.zip' } },
      { data: { id: 'opening_brief.docx' } },
      { data: { id: 'reply_brief.docx' } },
      { data: { source: 'Case Files', target: 'complaint.pdf' } },
      { data: { source: 'Case Files', target: 'evidence.zip' } },
      { data: { source: 'Briefs', target: 'opening_brief.docx' } },
      { data: { source: 'Briefs', target: 'reply_brief.docx' } }
    ],
    style: [
      {
        selector: 'node',
        style: {
          label: 'data(id)',
          'background-color': '#3498db',
          color: '#fff',
          'text-valign': 'center',
          'text-halign': 'center',
          width: 'label',
          height: 'label',
          padding: '6px'
        }
      },
      {
        selector: "node[id $= '.pdf']",
        style: { 'background-color': '#e74c3c' }
      },
      {
        selector: "node[id $= '.docx']",
        style: { 'background-color': '#2ecc71' }
      },
      {
        selector: 'edge',
        style: {
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'line-color': '#aaa',
          'target-arrow-color': '#aaa'
        }
      }
    ],
    layout: {
      name: 'breadthfirst',
      directed: true,
      padding: 10,
      spacingFactor: 1.2
    }
  });

  cy.on('tap', 'node', evt => {
    const nodeId = evt.target.id();
    const header = Array.from(
      document.querySelectorAll('.folder-header .title')
    ).find(el => el.textContent === nodeId);
    if (header) header.parentElement.classList.toggle('open');
  });
});