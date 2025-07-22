document.getElementById('upload-button').addEventListener('click', () => {
    const fileInput = document.getElementById('file-input');
    const files = fileInput.files;

    if (files.length === 0) {
        alert('Please select files to upload.');
        return;
    }

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file, file.webkitRelativePath || file.name);
    }

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error uploading files:', error);
        alert('An error occurred during file upload.');
    });
});

document.getElementById('export-button').addEventListener('click', () => {
    window.location.href = '/api/export';
});
