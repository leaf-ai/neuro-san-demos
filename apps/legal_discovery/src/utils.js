export function fetchJSON(url, options) {
  return fetch(url, options).then(r => r.json());
}

export function alertResponse(d) {
  alert(d.message || 'Done');
}
