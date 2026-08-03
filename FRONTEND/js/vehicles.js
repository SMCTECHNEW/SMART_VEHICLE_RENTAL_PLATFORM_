// Vehicles page functionality

let currentPage = 1;
let currentView = 'grid';
let totalPages = 1;

document.addEventListener('DOMContentLoaded', () => {
    loadVehicles();
    updateAuthUI();
});

async function loadVehicles() {
    try {
        const params = getFilterParams();
        const response = await api.getVehicles(params);
        
        const vehicles = response.items || response;
        totalPages = response.total_pages || 1;
        currentPage = response.page || 1;
        
        const grid = document.getElementById('vehiclesGrid');
        const countEl = document.getElementById('vehicleCount');
        
        if (vehicles.length === 0) {
            showEmpty('vehiclesGrid', 'No vehicles found matching your criteria');
            countEl.textContent = '0 vehicles found';
            return;
        }
        
        countEl.textContent = `${response.total || vehicles.length} vehicles found`;
        grid.innerHTML = vehicles.map(vehicle => createVehicleCard(vehicle)).join('');
        
        renderPagination();
    } catch (error) {
        console.error('Failed to load vehicles:', error);
        showErrorState('vehiclesGrid', 'Failed to load vehicles. Please try again.');
    }
}

function getFilterParams() {
    const search = document.getElementById('searchInput')?.value.trim();
    const vehicleType = document.getElementById('vehicleType')?.value;
    const brand = document.getElementById('brand')?.value;
    const fuelType = document.getElementById('fuelType')?.value;
    const transmission = document.getElementById('transmission')?.value;
    const minPrice = document.getElementById('minPrice')?.value;
    const maxPrice = document.getElementById('maxPrice')?.value;
    const seats = document.getElementById('seats')?.value;
    const sortBy = document.getElementById('sortBy')?.value || 'newest';
    
    const params = {
        page: currentPage,
        limit: 12
    };
    
    if (search) params.search = search;
    if (vehicleType) params.vehicle_type = vehicleType;
    if (brand) params.brand = brand;
    if (fuelType) params.fuel_type = fuelType;
    if (transmission) params.transmission = transmission;
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    if (seats) params.seats = seats;
    
    // Map sort values
    const sortMap = {
        'newest': '-created_at',
        'price_asc': 'price_per_day',
        'price_desc': '-price_per_day',
        'rating': '-rating'
    };
    params.sort = sortMap[sortBy] || '-created_at';
    
    return params;
}

function applyFilters() {
    currentPage = 1;
    loadVehicles();
}

function resetFilters() {
    document.querySelectorAll('.filters-sidebar input, .filters-sidebar select').forEach(el => {
        el.value = '';
    });
    document.getElementById('sortBy').value = 'newest';
    currentPage = 1;
    loadVehicles();
}

function setView(view) {
    currentView = view;
    const grid = document.getElementById('vehiclesGrid');
    
    document.querySelectorAll('.view-toggle .btn-icon').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.btn-icon').classList.add('active');
    
    if (view === 'list') {
        grid.classList.add('list-view');
    } else {
        grid.classList.remove('list-view');
    }
}

function renderPagination() {
    const container = document.getElementById('pagination');
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="pagination">';
    
    // Previous
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">
        <i class="fas fa-chevron-left"></i>
    </button>`;
    
    // Pages
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<span class="ellipsis">...</span>';
        }
    }
    
    // Next
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">
        <i class="fas fa-chevron-right"></i>
    </button>`;
    
    html += '</div>';
    container.innerHTML = html;
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateAuthUI() {
    const user = getUser();
    const authLinks = document.getElementById('authLinks');
    
    if (user) {
        authLinks.innerHTML = `
            <li><a href="dashboard.html">Dashboard</a></li>
            <li><a href="#" onclick="logout()">Logout</a></li>
        `;
    } else {
        authLinks.innerHTML = `
            <li><a href="login.html">Login</a></li>
            <li><a href="register.html" class="btn btn-primary">Register</a></li>
        `;
    }
}
