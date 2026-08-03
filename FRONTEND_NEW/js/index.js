/**
 * Index Page - Home Page Functionality
 * Smart Vehicle Rental Platform
 */

let currentPage = 1;
const itemsPerPage = 8;
let allVehicles = [];

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadVehicles();
    setupChatbot();
    setupThemeToggle();
});

// Load vehicles from API
async function loadVehicles() {
    const container = document.getElementById('vehicles-container');
    
    try {
        showPageLoading('Loading vehicles...');
        
        // Get filter values
        const search = document.getElementById('vehicleSearch')?.value || '';
        const vehicleType = document.getElementById('vehicleTypeFilter')?.value || '';
        const priceSort = document.getElementById('priceSort')?.value || '';
        
        // Build query parameters
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (vehicleType) params.append('vehicle_type', vehicleType);
        if (priceSort) params.append('sort', priceSort === 'low' ? 'price_asc' : 'price_desc');
        params.append('page', currentPage);
        params.append('limit', itemsPerPage);
        
        const response = await api.get(`${endpoints.vehicles.list}?${params}`);
        const data = response.data;
        
        allVehicles = data.items || data;
        
        if (allVehicles.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-car fa-4x text-muted mb-3"></i>
                    <h4>No vehicles found</h4>
                    <p class="text-muted">Try adjusting your filters</p>
                </div>
            `;
            return;
        }
        
        displayVehicles(allVehicles);
        
        // Update pagination if data has pagination info
        if (data.total && data.pages) {
            updatePagination(data.total, data.pages);
        }
        
    } catch (error) {
        console.error('Error loading vehicles:', error);
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
                <h4>Error loading vehicles</h4>
                <p class="text-muted">${error.message || 'Please try again later'}</p>
                <button class="btn btn-primary" onclick="loadVehicles()">Retry</button>
            </div>
        `;
    } finally {
        hidePageLoading();
    }
}

// Display vehicles in grid
function displayVehicles(vehicles) {
    const container = document.getElementById('vehicles-container');
    
    container.innerHTML = vehicles.map(vehicle => {
        const primaryImage = vehicle.images?.find(img => img.is_primary)?.image_url 
                           || vehicle.image_url 
                           || 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400&h=300&fit=crop';
        
        return `
            <div class="col-md-6 col-lg-3">
                <div class="vehicle-card h-100">
                    <img src="${primaryImage}" alt="${vehicle.name}" onerror="this.src='https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400&h=300&fit=crop'">
                    <div class="vehicle-card-body">
                        <h5 class="vehicle-card-title">${vehicle.brand} ${vehicle.model}</h5>
                        <p class="text-muted mb-2">${vehicle.name}</p>
                        <div class="vehicle-specs">
                            <span><i class="fas fa-users"></i> ${vehicle.seats || 4}</span>
                            <span><i class="fas fa-cog"></i> ${vehicle.transmission || 'Manual'}</span>
                            <span><i class="fas fa-gas-pump"></i> ${vehicle.fuel_type || 'Petrol'}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="vehicle-price">₹${vehicle.price_per_day}/day</span>
                            ${vehicle.rating ? `<span class="text-warning"><i class="fas fa-star"></i> ${vehicle.rating.toFixed(1)}</span>` : ''}
                        </div>
                        ${vehicle.has_driver_option ? '<small class="text-success d-block mt-2"><i class="fas fa-user-tie"></i> Driver available</small>' : ''}
                        <a href="vehicle-details.html?id=${vehicle.id}" class="btn btn-outline-primary w-100 mt-3">View Details</a>
                        <button class="btn btn-primary w-100 mt-2" onclick="quickBook(${vehicle.id})">Book Now</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Update pagination
function updatePagination(total, pages) {
    const pagination = document.getElementById('vehiclePagination');
    
    let html = '';
    
    // Previous button
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">Previous</a>
    </li>`;
    
    // Page numbers
    for (let i = 1; i <= pages; i++) {
        if (i === 1 || i === pages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>
            </li>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    // Next button
    html += `<li class="page-item ${currentPage === pages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">Next</a>
    </li>`;
    
    pagination.innerHTML = html;
}

// Change page
function changePage(page) {
    if (page < 1) return;
    currentPage = page;
    loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Quick book function
function quickBook(vehicleId) {
    if (!checkAuth(true)) {
        return;
    }
    
    // Store vehicle ID and redirect to booking page
    sessionStorage.setItem('booking_vehicle_id', vehicleId);
    window.location.href = 'booking.html';
}

// Setup Chatbot
function setupChatbot() {
    const toggle = document.getElementById('chatbot-toggle');
    const close = document.getElementById('chatbot-close');
    const send = document.getElementById('chatbot-send');
    const input = document.getElementById('chatbot-input-field');
    const window = document.getElementById('chatbot-window');
    
    toggle.addEventListener('click', () => {
        window.classList.toggle('d-none');
        if (!window.classList.contains('d-none')) {
            addBotMessage('Hello! I\'m your AI assistant. How can I help you today?');
        }
    });
    
    close.addEventListener('click', () => {
        window.classList.add('d-none');
    });
    
    send.addEventListener('click', sendChatMessage);
    
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
}

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById('chatbot-input-field');
    const message = input.value.trim();
    
    if (!message) return;
    
    addUserMessage(message);
    input.value = '';
    
    // Show typing indicator
    const messagesDiv = document.getElementById('chatbot-messages');
    const typingId = 'typing-' + Date.now();
    messagesDiv.innerHTML += `<div class="chatbot-message bot" id="${typingId}"><i class="fas fa-ellipsis-h fa-beat"></i></div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        // Try to call chatbot API if available
        const response = await api.post('/chatbot/', { message: message });
        document.getElementById(typingId).remove();
        addBotMessage(response.data.response || response.data.message);
    } catch (error) {
        document.getElementById(typingId).remove();
        // Fallback response
        addBotMessage('Thanks for your message! Ask me about vehicles, bookings, discounts, drivers, or our services.');
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.innerHTML += `<div class="chatbot-message user">${message}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add bot message to chat
function addBotMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.innerHTML += `<div class="chatbot-message bot">${message.replace(/\n/g, '<br>')}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Theme Toggle
function setupThemeToggle() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
});
