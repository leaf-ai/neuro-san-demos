document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.folder-tree .folder-header').forEach(header => {
    header.addEventListener('click', () => {
      const folder = header.parentElement;
      folder.classList.toggle('open');

      const icon = header.querySelector('.folder-icon');
      if (folder.classList.contains('open')) {
        icon.classList.replace('fa-folder', 'fa-folder-open');
      } else {
        icon.classList.replace('fa-folder-open', 'fa-folder');
      }
    });
  });
});