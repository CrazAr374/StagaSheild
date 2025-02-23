// Add these utility functions at the top
function showLoading(message = 'Processing...') {
    const overlay = document.querySelector('.processing-overlay');
    const loadingText = overlay.querySelector('.loading-text');
    loadingText.textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.querySelector('.processing-overlay').style.display = 'none';
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Update image preview loading
async function updateImagePreview(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        preview.parentElement.classList.add('processing');
        const optimizedImage = await optimizeImagePreview(input.files[0]);
        preview.src = optimizedImage;
        preview.style.display = 'block';
        preview.parentElement.classList.remove('processing');
    }
}

function updateProgress(percent) {
    const progressBar = document.querySelector('.progress-bar .progress');
    const overlay = document.querySelector('.preview-overlay');
    overlay.style.display = 'flex';
    progressBar.style.width = `${percent}%`;
    
    if (percent >= 100) {
        setTimeout(() => {
            overlay.style.display = 'none';
            progressBar.style.width = '0%';
        }, 1000);
    }
}

// Add this after the existing utility functions

function updateMessageLength() {
    const textarea = document.getElementById('secretMessage');
    const lengthDisplay = document.querySelector('.message-length');
    const maxLengthDisplay = document.querySelector('.max-length');
    const image = document.getElementById('embedImage');

    const messageLength = textarea.value.length;
    lengthDisplay.textContent = `Length: ${messageLength} characters`;

    // If image is selected, calculate and show max length
    if (image.files && image.files[0]) {
        const img = new Image();
        img.onload = function() {
            // Rough estimation of max characters (width * height * 3 channels - 32 bits for header) / 8 bits
            const maxLength = Math.floor((this.width * this.height * 3 - 32) / 8);
            maxLengthDisplay.textContent = `Maximum: ${maxLength} characters`;
            
            // Add visual feedback
            if (messageLength > maxLength) {
                lengthDisplay.style.color = '#dc3545'; // red
            } else {
                lengthDisplay.style.color = '#198754'; // green
            }
        };
        img.src = URL.createObjectURL(image.files[0]);
    }
}

// Add event listeners for image preview
document.getElementById('embedImage').addEventListener('change', function() {
    updateImagePreview(this, 'embedPreview');
});

// Add these event listeners after the existing ones
document.getElementById('secretMessage').addEventListener('input', updateMessageLength);
document.getElementById('embedImage').addEventListener('change', function() {
    updateMessageLength();
    updateImagePreview(this, 'embedPreview');
});

// Update the embed form submission
document.getElementById('embedForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Embedding message...');
    updateProgress(0);
    
    const formData = new FormData();
    formData.append('image', document.getElementById('embedImage').files[0]);
    formData.append('message', document.getElementById('secretMessage').value);
    
    try {
        updateProgress(50);
        const response = await fetch('/embed', {
            method: 'POST',
            body: formData
        });
        
        updateProgress(75);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'stego_image.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            updateProgress(100);
            
            // Add to dashboard
            updateDashboard({
                filename: 'stego_image.png',
                timestamp: new Date().toISOString(),
                status: 'success'
            });
        } else {
            const data = await response.json();
            alert(data.error || 'Error embedding message');
            updateProgress(0);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        updateProgress(0);
    } finally {
        hideLoading();
    }
});

// Update the extract form submission
document.getElementById('extractForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Extracting message...');
    
    const formData = new FormData();
    const imageFile = document.getElementById('extractImage').files[0];
    formData.append('image', imageFile);
    
    try {
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        const messageBox = document.getElementById('extractedMessage');
        
        if (response.ok && data.success) {
            messageBox.textContent = data.message;
            messageBox.classList.add('success');
            messageBox.classList.remove('error');
        } else {
            messageBox.textContent = data.error || 'Failed to extract message';
            messageBox.classList.add('error');
            messageBox.classList.remove('success');
        }
        
        // Scroll message into view with smooth animation
        messageBox.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest'
        });
    } catch (error) {
        const messageBox = document.getElementById('extractedMessage');
        messageBox.textContent = 'Error: Failed to process request';
        messageBox.classList.add('error');
        messageBox.classList.remove('success');
    } finally {
        hideLoading();
    }
});

// Update the detect form submission
document.getElementById('detectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Analyzing image...');
    
    const formData = new FormData();
    const imageFile = document.getElementById('detectImage').files[0];
    formData.append('image', imageFile);
    
    try {
        // Show loading state
        document.getElementById('detectForm').querySelector('button').disabled = true;
        
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            showAnalysisResults(data);
        } else {
            const error = await response.json();
            alert(error.error || 'Error analyzing image');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('detectForm').querySelector('button').disabled = false;
        hideLoading();
    }
});

function showAnalysisResults(data) {
    const results = document.getElementById('analysisResults');
    results.style.display = 'block';
    
    // Update probability meter
    const probability = data.probability * 100;
    document.getElementById('probabilityMeter').style.width = `${probability}%`;
    document.getElementById('probabilityValue').textContent = `${probability.toFixed(1)}%`;
    
    // Update visualizations
    document.getElementById('modificationMap').src = `data:image/png;base64,${data.modification_map}`;
    document.getElementById('histogram').src = `data:image/png;base64,${data.histogram}`;
    
    // Update analysis details
    document.getElementById('analysisDetails').innerHTML = `
        <div class="detail-item">
            <span>LSB Distribution</span>
            <span>${(data.lsb_ratio * 100).toFixed(1)}%</span>
        </div>
        <div class="detail-item">
            <span>Randomness Score</span>
            <span>${(data.randomness_score * 100).toFixed(1)}%</span>
        </div>
    `;
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Dashboard functionality
function updateDashboard(item) {
    const dashboard = document.getElementById('dashboard');
    const entry = document.createElement('div');
    entry.className = 'dashboard-item';
    entry.innerHTML = `
        <img src="${item.preview || '#'}" alt="Preview" class="dashboard-preview">
        <div class="dashboard-info">
            <div class="filename">${item.filename}</div>
            <div class="timestamp">${new Date(item.timestamp).toLocaleString()}</div>
            <div class="status ${item.status}">${item.status}</div>
        </div>
    `;
    dashboard.insertBefore(entry, dashboard.firstChild);
}

// Batch processing
document.getElementById('batchMode').addEventListener('change', function() {
    const messageGroup = document.getElementById('batchMessageGroup');
    messageGroup.style.display = this.value === 'embed' ? 'block' : 'none';
});

document.getElementById('batchImages').addEventListener('change', function() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    
    Array.from(this.files).forEach(file => {
        const reader = new FileReader();
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        reader.onload = e => {
            fileItem.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <span>${file.name}</span>
            `;
        };
        
        reader.readAsDataURL(file);
        fileList.appendChild(fileItem);
    });
});

// Update batch processing
document.getElementById('batchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    showLoading('Processing batch...');
    
    const mode = document.getElementById('batchMode').value;
    const files = document.getElementById('batchImages').files;
    const message = document.getElementById('batchMessage').value;
    const resultsContainer = document.getElementById('batchResults');
    
    if (!files.length) {
        alert('Please select files to process');
        hideLoading();
        return;
    }
    
    if (mode === 'embed' && !message) {
        alert('Please enter a message to embed');
        hideLoading();
        return;
    }
    
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('images', file);
    });
    
    if (mode === 'embed') {
        formData.append('message', message);
    }
    
    try {
        const response = await fetch(`/batch-${mode}`, {
            method: 'POST',
            body: formData
        });
        
        if (mode === 'embed') {
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'stego_images.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            }
        } else {
            const data = await response.json();
            resultsContainer.innerHTML = data.results.map(result => `
                <div class="result-item ${result.error ? 'error' : 'success'}">
                    <strong>${result.filename}</strong>: 
                    ${result.error || result.message}
                </div>
            `).join('');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        hideLoading();
    }
});

// Mobile menu handling
const mobileMenuToggle = document.createElement('button');
mobileMenuToggle.className = 'mobile-menu-toggle';
mobileMenuToggle.innerHTML = '<span></span><span></span><span></span>';
document.querySelector('.app-nav').insertBefore(mobileMenuToggle, document.querySelector('.app-nav-links'));

mobileMenuToggle.addEventListener('click', () => {
    mobileMenuToggle.classList.toggle('active');
    document.querySelector('.app-nav-links').classList.toggle('show');
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!mobileMenuToggle.contains(e.target) && 
        !document.querySelector('.app-nav-links').contains(e.target)) {
        mobileMenuToggle.classList.remove('active');
        document.querySelector('.app-nav-links').classList.remove('show');
    }
});

// Handle tab scrolling on mobile
const tabsContainer = document.querySelector('.tabs');
let isScrolling = false;
let startX;
let scrollLeft;

tabsContainer.addEventListener('touchstart', (e) => {
    isScrolling = true;
    startX = e.touches[0].pageX - tabsContainer.offsetLeft;
    scrollLeft = tabsContainer.scrollLeft;
});

tabsContainer.addEventListener('touchmove', (e) => {
    if (!isScrolling) return;
    e.preventDefault();
    const x = e.touches[0].pageX - tabsContainer.offsetLeft;
    const walk = (x - startX) * 2;
    tabsContainer.scrollLeft = scrollLeft - walk;
});

tabsContainer.addEventListener('touchend', () => {
    isScrolling = false;
});

// Optimize image preview on mobile
function optimizeImagePreview(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const MAX_SIZE = 1024;
                let width = img.width;
                let height = img.height;
                
                if (width > height && width > MAX_SIZE) {
                    height *= MAX_SIZE / width;
                    width = MAX_SIZE;
                } else if (height > MAX_SIZE) {
                    width *= MAX_SIZE / height;
                    height = MAX_SIZE;
                }
                
                canvas.width = width;
                canvas.height = height;
                canvas.getContext('2d').drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL('image/jpeg', 0.85));
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}
