// Vehicles page functionality

let currentPage = 1;
let totalPages = 1;

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadVehicles();
    updateAuthUI();
});

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
    }
}

function getFilterParams() {
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
    if (fuelType) params.fuel_type = fuelType;
    if (transmission) params.transmission = transmission;
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    if (seats) params.seats = seats;

    if (sortBy === 'price_asc') params.sort = 'price_per_day';
    else if (sortBy === 'price_desc') params.sort = '-price_per_day';
    else if (sortBy === 'rating') params.sort = '-rating';
    else if (sortBy === 'newest') params.sort = '-created_at';

    return params;
}

function applyFilters() {
    currentPage = 1;
    loadVehicles();
}

function resetFilters() {
    ['searchInput', 'minPrice', 'maxPrice', 'seatsFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    ['brandFilter', 'typeFilter', 'fuelFilter', 'transmissionFilter', 'sortFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    currentPage = 1;
    loadVehicles();
}

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
}

function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadVehicles();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

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
    }
}
