// File Upload Handler Class
class FileUploadHandler {
  constructor() {
    this.fileInput = document.getElementById('cv-file-input');
    this.uploadTrigger = document.querySelector('[hs-file-upload-trigger]');
    this.previewsContainer = document.querySelector('[hs-file-upload-previews]');
    this.progressBar = document.querySelector('[hs-file-upload-progress-bar-pane]');
    this.progressValue = document.querySelector('[hs-file-upload-progress-bar-value]');
    this.fileNameElement = document.querySelector('[hs-file-upload-file-name]');
    this.fileExtElement = document.querySelector('[hs-file-upload-file-ext]');
    
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    // Trigger file input when clicking the upload area
    this.uploadTrigger.addEventListener('click', () => {
      this.fileInput.click();
    });

    // Handle drag and drop
    this.uploadTrigger.addEventListener('dragover', (e) => {
      e.preventDefault();
      this.uploadTrigger.classList.add('border-blue-500');
    });

    this.uploadTrigger.addEventListener('dragleave', () => {
      this.uploadTrigger.classList.remove('border-blue-500');
    });

    this.uploadTrigger.addEventListener('drop', (e) => {
      e.preventDefault();
      this.uploadTrigger.classList.remove('border-blue-500');
      const files = e.dataTransfer.files;
      if (files.length) {
        this.handleFileSelect(files[0]);
      }
    });

    // Handle file input change
    this.fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        this.handleFileSelect(e.target.files[0]);
      }
    });

    // Handle remove button click
    document.querySelector('[hs-file-upload-remove]')?.addEventListener('click', () => {
      this.resetUpload();
    });
  }

  handleFileSelect(file) {
    // Check file size (2MB limit)
    if (file.size > 2 * 1024 * 1024) {
      alert('File size exceeds 2MB limit');
      return;
    }

    // Check file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a PDF, DOC, or DOCX file');
      return;
    }

    // Update file info
    const fileName = file.name;
    const fileExt = fileName.split('.').pop();
    this.fileNameElement.textContent = fileName.replace(`.${fileExt}`, '');
    this.fileExtElement.textContent = fileExt;

    // Show preview container
    this.previewsContainer.style.display = 'block';

    // Upload file
    this.uploadFile(file);
  }

  uploadFile(file) {
    const formData = new FormData();
    formData.append('cv_file', file);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        this.updateProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        this.updateProgress(100);
        this.progressBar.classList.add('hs-file-upload-complete');
      } else {
        alert('Upload failed. Please try again.');
        this.resetUpload();
      }
    });

    xhr.addEventListener('error', () => {
      alert('Upload failed. Please try again.');
      this.resetUpload();
    });

    xhr.open('POST', '/upload');
    xhr.send(formData);
  }

  updateProgress(percent) {
    const roundedPercent = Math.round(percent);
    this.progressBar.style.width = `${roundedPercent}%`;
    this.progressValue.textContent = roundedPercent;
  }

  resetUpload() {
    this.fileInput.value = '';
    this.previewsContainer.style.display = 'none';
    this.progressBar.style.width = '0%';
    this.progressValue.textContent = '0';
    this.progressBar.classList.remove('hs-file-upload-complete');
    this.fileNameElement.textContent = '';
    this.fileExtElement.textContent = '';
  }
}

// Initialize the upload handler when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new FileUploadHandler();
});