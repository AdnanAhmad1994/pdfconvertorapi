/**
 * PDF Converter UI Script
 * Handles the PDF conversion process in the UI
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const pdfFileInput = document.getElementById('pdf-file');
    const formatSelect = document.getElementById('format');
    const pagesInput = document.getElementById('pages');
    const qualityInput = document.getElementById('quality');
    const qualityValue = document.getElementById('quality-value');
    const dpiSelect = document.getElementById('dpi');
    const preserveLayoutCheckbox = document.getElementById('preserve-layout');
    const preserveLayoutHtmlCheckbox = document.getElementById('preserve-layout-html');
    const convertButton = document.getElementById('convert-button');
    const jpegOptions = document.getElementById('jpeg-options');
    const docxOptions = document.getElementById('docx-options');
    const htmlOptions = document.getElementById('html-options');
    const pptOptions = document.getElementById('ppt-options');
    
    const uploadSection = document.getElementById('upload-section');
    const progressPanel = document.getElementById('progress-panel');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressStatus = document.getElementById('progress-status');
    const resultPanel = document.getElementById('result-panel');
    const downloadLink = document.getElementById('download-link');
    const resultFileInfo = document.getElementById('result-file-info');
    const newConversionButton = document.getElementById('new-conversion-button');
    const errorPanel = document.getElementById('error-panel');
    const errorMessage = document.getElementById('error-message');
    const tryAgainButton = document.getElementById('try-again-button');
    
    // Variables
    let taskId = null;
    let statusCheckInterval = null;
    
    // Event listeners
    pdfFileInput.addEventListener('change', function() {
        convertButton.disabled = !pdfFileInput.files.length;
        if (pdfFileInput.files.length) {
            const file = pdfFileInput.files[0];
            validatePdf(file);
        }
    });
    
    formatSelect.addEventListener('change', function() {
        const format = formatSelect.value;
        jpegOptions.style.display = format === 'jpeg' ? 'block' : 'none';
        docxOptions.style.display = format === 'docx' ? 'block' : 'none';
        htmlOptions.style.display = format === 'html' ? 'block' : 'none';
        pptOptions.style.display = format === 'ppt' ? 'block' : 'none';
        
        // Reset conversion button
        convertButton.textContent = 'Convert PDF';
        convertButton.disabled = !pdfFileInput.files.length;
    });
    
    qualityInput.addEventListener('input', function() {
        qualityValue.textContent = qualityInput.value;
    });
    
    convertButton.addEventListener('click', startConversion);
    newConversionButton.addEventListener('click', resetForm);
    tryAgainButton.addEventListener('click', resetForm);
    
    // Initialize
    formatSelect.dispatchEvent(new Event('change'));
    
    // Functions
    function validatePdf(file) {
        // Simple client-side validation
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError('Please select a PDF file.');
            return false;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            showError('File size exceeds the limit of 10MB.');
            return false;
        }
        
        return true;
    }
    
    function startConversion() {
        const pdfFile = pdfFileInput.files[0];
        if (!pdfFile || !validatePdf(pdfFile)) {
            return;
        }
        
        const format = formatSelect.value;
        const pages = pagesInput.value;
        const quality = qualityInput.value;
        const dpi = dpiSelect.value;
        const preserveLayout = format === 'docx' ? preserveLayoutCheckbox.checked : preserveLayoutHtmlCheckbox.checked;
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', pdfFile);
        formData.append('format', format);
        
        if (pages) {
            formData.append('pages', pages);
        }
        
        if (format === 'jpeg') {
            formData.append('quality', quality);
            formData.append('dpi', dpi);
        }
        
        if (format === 'docx' || format === 'html') {
            formData.append('preserve_layout', preserveLayout);
        }
        
        // Show progress panel
        uploadSection.style.display = 'none';
        progressPanel.style.display = 'block';
        resultPanel.style.display = 'none';
        errorPanel.style.display = 'none';
        progressBarFill.style.width = '5%';
        
        // Send conversion request
        fetch('/api/v1/conversion/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'An error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            taskId = data.task_id;
            progressBarFill.style.width = '10%';
            progressStatus.textContent = 'Starting conversion...';
            
            // Start checking status
            statusCheckInterval = setInterval(checkStatus, 1000);
        })
        .catch(error => {
            showError(error.message || 'Failed to start conversion');
        });
    }
    
    function checkStatus() {
        if (!taskId) {
            clearInterval(statusCheckInterval);
            return;
        }
        
        fetch(`/api/v1/conversion/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to get conversion status');
            }
            return response.json();
        })
        .then(data => {
            // Update progress
            const progress = data.progress || 0;
            progressBarFill.style.width = `${progress}%`;
            progressStatus.textContent = `Converting... ${Math.round(progress)}%`;
            
            // Check status
            switch (data.status) {
                case 'completed':
                    clearInterval(statusCheckInterval);
                    showResult(data.result_url);
                    break;
                case 'failed':
                    clearInterval(statusCheckInterval);
                    showError(data.message || 'Conversion failed');
                    break;
                case 'cancelled':
                    clearInterval(statusCheckInterval);
                    showError('Conversion was cancelled');
                    break;
            }
        })
        .catch(error => {
            clearInterval(statusCheckInterval);
            showError(error.message || 'Failed to check conversion status');
        });
    }
    
    function showResult(resultUrl) {
        uploadSection.style.display = 'none';
        progressPanel.style.display = 'none';
        resultPanel.style.display = 'block';
        errorPanel.style.display = 'none';
        
        downloadLink.href = resultUrl;
        resultFileInfo.textContent = `Format: ${formatSelect.value.toUpperCase()}`;
    }
    
    function showError(message) {
        uploadSection.style.display = 'none';
        progressPanel.style.display = 'none';
        resultPanel.style.display = 'none';
        errorPanel.style.display = 'block';
        
        errorMessage.textContent = message;
    }
    
    function resetForm() {
        // Reset task
        taskId = null;
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
        
        // Reset form inputs
        pdfFileInput.value = '';
        pagesInput.value = '';
        qualityInput.value = 90;
        qualityValue.textContent = '90';
        dpiSelect.value = '300';
        preserveLayoutCheckbox.checked = true;
        preserveLayoutHtmlCheckbox.checked = true;
        
        // Reset button state
        convertButton.disabled = true;
        formatSelect.dispatchEvent(new Event('change'));
        
        // Show upload section
        uploadSection.style.display = 'block';
        progressPanel.style.display = 'none';
        resultPanel.style.display = 'none';
        errorPanel.style.display = 'none';
    }
});
