// Main JavaScript for HTML to PDF converter

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const htmlInput = document.getElementById('html-input');
    const previewBtn = document.getElementById('preview-btn');
    const convertBtn = document.getElementById('convert-btn');
    const downloadBtn = document.getElementById('download-btn');
    const previewFrame = document.getElementById('preview-frame');
    const emptyState = document.getElementById('empty-state');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');
    const companyDomain = document.getElementById('company-domain');
    const fetchLogoBtn = document.getElementById('fetch-logo-btn');
    const logoPreview = document.getElementById('logo-preview');
    const logoImage = document.getElementById('logo-image');
    const removeLogoBtn = document.getElementById('remove-logo-btn');
    const templatesDropdown = document.getElementById('templates-dropdown');
    
    // Bootstrap Toast instance
    const toastInstance = new bootstrap.Toast(errorToast);
    
    // Current state
    let currentLogoUrl = null;
    let templates = [];
    let pdfData = null;
    
    // Initialize the application
    init();
    
    // Function to initialize the application
    function init() {
        // Load templates
        loadTemplates();
        
        // Set up event listeners
        previewBtn.addEventListener('click', generatePreview);
        convertBtn.addEventListener('click', convertToPdf);
        downloadBtn.addEventListener('click', downloadPdf);
        fetchLogoBtn.addEventListener('click', fetchCompanyLogo);
        removeLogoBtn.addEventListener('click', removeLogo);
        htmlInput.addEventListener('input', function() {
            // Disable download button when HTML is changed
            downloadBtn.disabled = true;
        });
    }
    
    // Function to load templates from the server
    function loadTemplates() {
        // Show loading state in dropdown
        const loadingItem = templatesDropdown.querySelector('.dropdown-item.text-center');
        
        fetch('/templates')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load templates');
                }
                return response.json();
            })
            .then(data => {
                templates = data.templates;
                
                // Remove loading indicator
                if (loadingItem) {
                    loadingItem.remove();
                }
                
                // Add templates to dropdown
                templates.forEach(template => {
                    const li = document.createElement('li');
                    const button = document.createElement('button');
                    button.className = 'dropdown-item';
                    button.type = 'button';
                    button.dataset.templateId = template.id;
                    
                    // Create a container for template info
                    const infoContainer = document.createElement('div');
                    infoContainer.className = 'd-flex flex-column align-items-start';
                    
                    // Add template name
                    const nameSpan = document.createElement('span');
                    nameSpan.textContent = template.name;
                    infoContainer.appendChild(nameSpan);
                    
                    // Add template description
                    const descSpan = document.createElement('small');
                    descSpan.className = 'text-muted';
                    descSpan.textContent = template.description;
                    infoContainer.appendChild(descSpan);
                    
                    button.appendChild(infoContainer);
                    
                    button.addEventListener('click', () => loadTemplate(template));
                    li.appendChild(button);
                    templatesDropdown.appendChild(li);
                });
            })
            .catch(error => {
                showError('Failed to load templates: ' + error.message);
                
                // Remove loading indicator and show error
                if (loadingItem) {
                    loadingItem.textContent = 'Failed to load templates';
                }
            });
    }
    
    // Function to load a template
    function loadTemplate(template) {
        // Ask for confirmation if the HTML editor is not empty
        if (htmlInput.value.trim() !== '' && 
            !confirm('Loading a template will replace your current HTML. Continue?')) {
            return;
        }
        
        // If template ID is 0, clear the input
        if (template === 0) {
            htmlInput.value = '';
            return;
        }
        
        let html = template.html;
        
        // Replace placeholders with actual values if available
        if (currentLogoUrl) {
            html = html.replace(/LOGO_PLACEHOLDER/g, currentLogoUrl);
        }
        
        const domain = companyDomain.value.trim();
        if (domain) {
            const companyName = domain.split('.')[0].toUpperCase();
            html = html.replace(/COMPANY_NAME/g, companyName);
            html = html.replace(/DOMAIN_PLACEHOLDER/g, domain);
        }
        
        htmlInput.value = html;
        
        // Generate preview after loading template
        generatePreview();
    }
    
    // Function to generate preview
    function generatePreview() {
        const html = htmlInput.value.trim();
        
        if (!html) {
            emptyState.classList.remove('d-none');
            previewFrame.classList.add('d-none');
            return;
        }
        
        // Show loading overlay
        loadingOverlay.classList.remove('d-none');
        loadingMessage.textContent = 'Generating preview...';
        
        // Create a blob with the HTML content
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        // Set the iframe source to the blob URL
        previewFrame.onload = function() {
            // Hide loading overlay when iframe is loaded
            loadingOverlay.classList.add('d-none');
            emptyState.classList.add('d-none');
            previewFrame.classList.remove('d-none');
            
            // Clean up the URL object
            URL.revokeObjectURL(url);
        };
        
        previewFrame.src = url;
    }
    
    // Function to convert HTML to PDF
    function convertToPdf() {
        const html = htmlInput.value.trim();
        
        if (!html) {
            showError('Please enter HTML content to convert');
            return;
        }
        
        // Show loading overlay
        loadingOverlay.classList.remove('d-none');
        loadingMessage.textContent = 'Converting to PDF...';
        
        // Create form data to send
        const formData = new FormData();
        formData.append('html_content', html);
        
        // Send request to server
        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to convert HTML to PDF');
                });
            }
            return response.blob();
        })
        .then(blob => {
            // Store the PDF data for later download
            pdfData = blob;
            
            // Enable download button
            downloadBtn.disabled = false;
            
            // Hide loading overlay
            loadingOverlay.classList.add('d-none');
            
            // Show success message
            showSuccess('PDF generated successfully! Click "Download PDF" to save it.');
        })
        .catch(error => {
            // Hide loading overlay
            loadingOverlay.classList.add('d-none');
            
            // Show error message
            showError(error.message);
        });
    }
    
    // Function to download the generated PDF
    function downloadPdf() {
        if (!pdfData) {
            showError('No PDF data available. Please convert HTML to PDF first.');
            return;
        }
        
        // Create a download link
        const url = URL.createObjectURL(pdfData);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted.pdf';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }
    
    // Function to fetch company logo from Clearbit
    function fetchCompanyLogo() {
        const domain = companyDomain.value.trim();
        
        if (!domain) {
            showError('Please enter a company domain');
            return;
        }
        
        // Show loading overlay
        loadingOverlay.classList.remove('d-none');
        loadingMessage.textContent = 'Fetching company logo...';
        
        // Send request to server
        fetch(`/get_logo?domain=${encodeURIComponent(domain)}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to fetch logo');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Hide loading overlay
                loadingOverlay.classList.add('d-none');
                
                // Update logo preview
                logoImage.src = data.logo_url;
                logoPreview.classList.remove('d-none');
                
                // Store logo URL
                currentLogoUrl = data.logo_url;
                
                // If HTML input contains LOGO_PLACEHOLDER, replace it with the logo URL
                if (htmlInput.value.includes('LOGO_PLACEHOLDER')) {
                    htmlInput.value = htmlInput.value.replace(/LOGO_PLACEHOLDER/g, currentLogoUrl);
                    // Generate preview after replacing logo
                    generatePreview();
                }
            })
            .catch(error => {
                // Hide loading overlay
                loadingOverlay.classList.add('d-none');
                
                // Show error message
                showError(error.message);
            });
    }
    
    // Function to remove logo
    function removeLogo() {
        logoPreview.classList.add('d-none');
        logoImage.src = '';
        currentLogoUrl = null;
    }
    
    // Function to show error message
    function showError(message) {
        errorMessage.textContent = message;
        toastInstance.show();
    }
    
    // Function to show success message
    function showSuccess(message) {
        // Change the toast header to success style
        const toastHeader = errorToast.querySelector('.toast-header');
        toastHeader.classList.remove('bg-danger');
        toastHeader.classList.add('bg-success');
        
        // Update icon and text
        const icon = toastHeader.querySelector('i');
        icon.classList.remove('fa-exclamation-circle');
        icon.classList.add('fa-check-circle');
        
        const title = toastHeader.querySelector('strong');
        title.textContent = 'Success';
        
        // Set message
        errorMessage.textContent = message;
        
        // Show toast
        toastInstance.show();
        
        // Reset to error style after toast is hidden
        errorToast.addEventListener('hidden.bs.toast', function() {
            toastHeader.classList.remove('bg-success');
            toastHeader.classList.add('bg-danger');
            
            icon.classList.remove('fa-check-circle');
            icon.classList.add('fa-exclamation-circle');
            
            title.textContent = 'Error';
        }, { once: true });
    }
});
