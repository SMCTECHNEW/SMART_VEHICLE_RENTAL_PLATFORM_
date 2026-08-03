// Utility functions

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// Show loading state on button
function setButtonLoading(buttonId, loading = true) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (loading) {
        button.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (btnLoader) btnLoader.style.display = 'inline';
    } else {
        button.disabled = false;
        if (btnText) btnText.style.display = 'inline';
        if (btnLoader) btnLoader.style.display = 'none';
    }
}

// Clear error messages
function clearErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.querySelectorAll('.error-msg').forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });
    
    form.querySelectorAll('.form-group').forEach(el => {
        el.classList.remove('has-error');
    });
}

// Show validation error
function showError(fieldId, message) {
    const errorEl = document.getElementById(`${fieldId}Error`);
    const formGroup = document.getElementById(fieldId)?.closest('.form-group');
    
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    if (formGroup) {
        formGroup.classList.add('has-error');
    }
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]{10,}$/;
    return re.test(phone);
}

// Validate password strength
function validatePassword(password) {
    const errors = [];
    
    if (password.length < 8) {
        errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain an uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
        errors.push('Password must contain a lowercase letter');
    }
    if (!/\d/.test(password)) {
        errors.push('Password must contain a number');
    }
    
    return errors;
}

// Format currency
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Get status badge class
function getStatusBadgeClass(status) {
    const classes = {
        pending: 'status-pending',
        confirmed: 'status-confirmed',
        active: 'status-active',
        completed: 'status-completed',
        cancelled: 'status-cancelled',
        failed: 'status-failed'
    };
    return classes[status?.toLowerCase()] || '';
}

// Create vehicle card HTML
function createVehicleCard(vehicle) {
    return `
        <div class="vehicle-card" onclick="window.location.href='vehicle-details.html?id=${vehicle.id}'">
            <div class="vehicle-image">
                <img src="${vehicle.images?.[0]?.image_url || vehicle.image_url || 'assets/images/default-vehicle.jpg'}" 
                     alt="${vehicle.name}" 
                     onerror="this.src='assets/images/default-vehicle.jpg'">
                ${!vehicle.available && '<span class="unavailable-badge">Unavailable</span>'}
            </div>
            <div class="vehicle-details">
                <h3>${vehicle.name}</h3>
                <p class="vehicle-brand">${vehicle.brand} ${vehicle.model}</p>
                <div class="vehicle-specs">
                    <span><i class="fas fa-users"></i> ${vehicle.seats || 4}</span>
                    <span><i class="fas fa-gas-pump"></i> ${vehicle.fuel_type}</span>
                    <span><i class="fas fa-cog"></i> ${vehicle.transmission}</span>
                </div>
                <div class="vehicle-footer">
                    <div class="vehicle-price">
                        <span class="price">${formatCurrency(vehicle.price_per_day)}</span>
                        <span class="period">/day</span>
                    </div>
                    ${vehicle.rating ? `
                        <div class="vehicle-rating">
                            <i class="fas fa-star"></i>
                            <span>${vehicle.rating.toFixed(1)}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Create booking row HTML
function createBookingRow(booking) {
    return `
        <tr>
            <td>#${booking.id || booking.booking_id}</td>
            <td>${booking.vehicle?.name || 'N/A'}</td>
            <td>${formatDate(booking.start_date)} - ${formatDate(booking.end_date)}</td>
            <td>${formatCurrency(booking.total_amount)}</td>
            <td><span class="booking-status ${getStatusBadgeClass(booking.status)}">${booking.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewBooking('${booking.id}')">View</button>
                ${booking.status === 'confirmed' || booking.status === 'pending' ? `
                    <button class="btn btn-sm btn-outline-danger" onclick="cancelBooking('${booking.id}')">Cancel</button>
                ` : ''}
            </td>
        </tr>
    `;
}

// Loading skeleton
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i> Loading...
            </div>
        `;
    }
}

// Show empty state
function showEmpty(elementId, message = 'No data available') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// Show error state
function showErrorState(elementId, message = 'An error occurred') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">Retry</button>
            </div>
        `;
    }
}

// Pagination helper
function createPagination(currentPage, totalPages, onPageChange) {
    let html = '<div class="pagination">';
    
    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="${onPageChange}(${currentPage - 1})">
        <i class="fas fa-chevron-left"></i>
    </button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="${onPageChange}(${i})">${i}</button>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<span class="ellipsis">...</span>';
        }
    }
    
    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="${onPageChange}(${currentPage + 1})">
        <i class="fas fa-chevron-right"></i>
    </button>`;
    
    html += '</div>';
    return html;
}

// Sidebar toggle for mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// Confirm dialog
function confirmAction(message = 'Are you sure?') {
    return window.confirm(message);
}
