// Vehicles page functionality

let currentPage = 1;
<<<<<<< HEAD
let currentView = 'grid';
let totalPages = 1;

document.addEventListener('DOMContentLoaded', () => {
=======
let totalPages = 1;

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
>>>>>>> origin/main
    loadVehicles();
    updateAuthUI();
});

<<<<<<< HEAD
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
=======
function initializeEventListeners() {
    const applyBtn = document.getElementById('applyFilters');
    if (applyBtn) applyBtn.addEventListener('click', applyFilters);

    const resetBtn = document.getElementById('resetFilters');
    if (resetBtn) resetBtn.addEventListener('click', resetFilters);

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(applyFilters, 500);
        });
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const registerForm = document.getElementById('registerForm');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
}

async function loadVehicles() {
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const emptyState = document.getElementById('emptyState');
    const vehiclesGrid = document.getElementById('vehiclesGrid');
    const pagination = document.getElementById('pagination');

    if (loadingState) loadingState.classList.remove('d-none');
    if (errorState) errorState.classList.add('d-none');
    if (emptyState) emptyState.classList.add('d-none');
    if (vehiclesGrid) vehiclesGrid.innerHTML = '';
    if (pagination) pagination.classList.add('d-none');

    try {
        const params = getFilterParams();
        const response = await api.getVehicles(params);

        if (loadingState) loadingState.classList.add('d-none');

        const vehicles = response.items || response;
        totalPages = response.total_pages || 1;
        currentPage = response.page || 1;

        if (!vehicles || vehicles.length === 0) {
            if (emptyState) emptyState.classList.remove('d-none');
            return;
        }

        if (vehiclesGrid) {
            vehiclesGrid.innerHTML = vehicles.map(vehicle => createVehicleCard(vehicle)).join('');
        }

        if (pagination && totalPages > 1) {
            renderPagination();
            pagination.classList.remove('d-none');
        }

    } catch (error) {
        console.error('Failed to load vehicles:', error);
        if (loadingState) loadingState.classList.add('d-none');
        if (errorState) {
            document.getElementById('errorMessage').textContent = error.message || 'Failed to load vehicles';
            errorState.classList.remove('d-none');
        }
>>>>>>> origin/main
    }
}

function getFilterParams() {
<<<<<<< HEAD
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
=======
    const search = document.getElementById('searchInput')?.value?.trim() || '';
    const brand = document.getElementById('brandFilter')?.value || '';
    const vehicleType = document.getElementById('typeFilter')?.value || '';
    const fuelType = document.getElementById('fuelFilter')?.value || '';
    const transmission = document.getElementById('transmissionFilter')?.value || '';
    const minPrice = document.getElementById('minPrice')?.value || '';
    const maxPrice = document.getElementById('maxPrice')?.value || '';
    const seats = document.getElementById('seatsFilter')?.value || '';
    const sortBy = document.getElementById('sortFilter')?.value || '';

    const params = { page: currentPage, limit: 9 };

    if (search) params.search = search;
    if (brand) params.brand = brand;
    if (vehicleType) params.vehicle_type = vehicleType;
>>>>>>> origin/main
    if (fuelType) params.fuel_type = fuelType;
    if (transmission) params.transmission = transmission;
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    if (seats) params.seats = seats;
<<<<<<< HEAD
    
    // Map sort values
    const sortMap = {
        'newest': '-created_at',
        'price_asc': 'price_per_day',
        'price_desc': '-price_per_day',
        'rating': '-rating'
    };
    params.sort = sortMap[sortBy] || '-created_at';
    
=======

    if (sortBy === 'price_asc') params.sort = 'price_per_day';
    else if (sortBy === 'price_desc') params.sort = '-price_per_day';
    else if (sortBy === 'rating') params.sort = '-rating';
    else if (sortBy === 'newest') params.sort = '-created_at';

>>>>>>> origin/main
    return params;
}

function applyFilters() {
    currentPage = 1;
    loadVehicles();
}

function resetFilters() {
<<<<<<< HEAD
    document.querySelectorAll('.filters-sidebar input, .filters-sidebar select').forEach(el => {
        el.value = '';
    });
    document.getElementById('sortBy').value = 'newest';
=======
    ['searchInput', 'minPrice', 'maxPrice', 'seatsFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    ['brandFilter', 'typeFilter', 'fuelFilter', 'transmissionFilter', 'sortFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

>>>>>>> origin/main
    currentPage = 1;
    loadVehicles();
}

<<<<<<< HEAD
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
=======
function renderPagination() {
    const paginationList = document.getElementById('paginationList');
    if (!paginationList || totalPages <= 1) return;

    let html = '';
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="goToPage(${currentPage - 1}); return false;">
            <i class="fas fa-chevron-left"></i>
        </a>
    </li>`;

    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToPage(${i}); return false;">${i}</a>
            </li>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }

    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="goToPage(${currentPage + 1}); return false;">
            <i class="fas fa-chevron-right"></i>
        </a>
    </li>`;

    paginationList.innerHTML = html;
>>>>>>> origin/main
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

<<<<<<< HEAD
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
=======
function createVehicleCard(vehicle) {
    const imageUrl = vehicle.images?.[0]?.image_url || vehicle.image_url || 'https://via.placeholder.com/400x250?text=No+Image';
    const rating = vehicle.rating ? vehicle.rating.toFixed(1) : 'N/A';
    
    return `
        <div class="col-md-6 col-lg-4">
            <div class="card vehicle-card h-100" style="cursor: pointer;" onclick="window.location.href='vehicle-details.html?id=${vehicle.id}'">
                <img src="${imageUrl}" class="card-img-top" alt="${vehicle.name}" onerror="this.src='https://via.placeholder.com/400x250?text=No+Image'">
                <div class="card-body">
                    <h5 class="card-title">${vehicle.name}</h5>
                    <p class="text-muted mb-2">${vehicle.brand} ${vehicle.model || ''}</p>
                    <div class="d-flex justify-content-between mb-3">
                        <small><i class="fas fa-users"></i> ${vehicle.seats || 4} seats</small>
                        <small><i class="fas fa-gas-pump"></i> ${vehicle.fuel_type}</small>
                        <small><i class="fas fa-cog"></i> ${vehicle.transmission}</small>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="h5 mb-0 text-primary">$${vehicle.price_per_day}</span>
                            <small class="text-muted">/day</small>
                        </div>
                        ${vehicle.rating ? `<div class="text-warning"><i class="fas fa-star"></i> ${rating}</div>` : ''}
                    </div>
                    <div class="mt-3 d-grid gap-2">
                        <a href="vehicle-details.html?id=${vehicle.id}" class="btn btn-outline-primary">View Details</a>
                        <a href="../user/booking.html?vehicle_id=${vehicle.id}" class="btn btn-primary">Book Now</a>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateAuthUI() {
    const user = getUser();
    const authOnlyElements = document.querySelectorAll('.auth-only');
    const guestOnlyElements = document.querySelectorAll('.guest-only');

    if (user) {
        authOnlyElements.forEach(el => el.style.display = '');
        guestOnlyElements.forEach(el => el.style.display = 'none');
    } else {
        authOnlyElements.forEach(el => el.style.display = 'none');
        guestOnlyElements.forEach(el => el.style.display = '');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await api.login(email, password);
        if (response.access_token) {
            setToken(response.access_token);
            setUser(response.user || response);
            showToast('Login successful!', 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            modal.hide();
            setTimeout(() => window.location.reload(), 500);
        }
    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await api.register({
            full_name: name,
            email: email,
            password: password
        });
        
        if (response.access_token) {
            setToken(response.access_token);
            setUser(response.user || response);
            showToast('Registration successful!', 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            modal.hide();
            setTimeout(() => window.location.href = '../user/dashboard.html', 500);
        }
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
>>>>>>> origin/main
    }
}
