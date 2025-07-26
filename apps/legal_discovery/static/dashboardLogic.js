document.getElementById('queryForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const formData = new FormData(this);

  fetch('/query', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('outputBox').textContent = JSON.stringify(data, null, 2);
  })
  .catch(err => {
    document.getElementById('outputBox').textContent = 'Error: ' + err;
  });
});