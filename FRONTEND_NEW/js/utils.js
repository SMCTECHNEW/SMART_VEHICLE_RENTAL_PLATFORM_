/**
 * Toast Notification System
 * Smart Vehicle Rental Platform
 */

// Show Toast Notification
function showToast(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.setAttribute('role', 'alert');
    
    const icon = getToastIcon(type);
    
    toast.innerHTML = `
        <div class="toast-body d-flex align-items-center">
            <i class="${icon} me-2 fa-lg"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Get icon based on toast type
function getToastIcon(type) {
    switch (type) {
        case 'success':
            return 'fas fa-check-circle text-success';
        case 'error':
            return 'fas fa-exclamation-circle text-danger';
        case 'warning':
            return 'fas fa-exclamation-triangle text-warning';
        default:
            return 'fas fa-info-circle text-primary';
    }
}

// Show Loading Indicator
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">${message}</span>
                </div>
                <p class="mt-2 text-muted">${message}</p>
            </div>
        `;
    }
}

// Hide Loading Indicator
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const loading = element.querySelector('.spinner-border');
        if (loading) {
            loading.parentElement.remove();
        }
    }
}

// Show Page Loading Overlay
function showPageLoading(message = 'Loading...') {
    let overlay = document.getElementById('pageLoadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'pageLoadingOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        document.body.appendChild(overlay);
    }
    
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">${message}</span>
            </div>
            <p class="mt-3 text-muted fw-semibold">${message}</p>
        </div>
    `;
    
    overlay.style.display = 'flex';
}

// Hide Page Loading Overlay
function hidePageLoading() {
    const overlay = document.getElementById('pageLoadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Confirm Dialog
async function showConfirm(title, message) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade show';
        modal.style.display = 'block';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title">${title}</h5>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="confirmCancel">Cancel</button>
                        <button type="button" class="btn btn-warning" id="confirmYes">Yes, Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('confirmCancel').addEventListener('click', () => {
            modal.remove();
            resolve(false);
        });
        
        document.getElementById('confirmYes').addEventListener('click', () => {
            modal.remove();
            resolve(true);
        });
    });
}

// Format Currency
function formatCurrency(amount, currency = 'INR') {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

// Format Date
function formatDate(dateString, format = 'short') {
    const date = new Date(dateString);
    
    if (format === 'short') {
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    } else if (format === 'long') {
        return date.toLocaleDateString('en-IN', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } else if (format === 'time') {
        return date.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    return dateString;
}

// Calculate Date Difference in Days
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round(Math.abs((date1 - date2) / oneDay));
}

// Validate Email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate Phone
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]{10,}$/;
    return re.test(phone);
}

// Export functions
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showPageLoading = showPageLoading;
window.hidePageLoading = hidePageLoading;
window.showConfirm = showConfirm;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.daysBetween = daysBetween;
window.isValidEmail = isValidEmail;
window.isValidPhone = isValidPhone;
