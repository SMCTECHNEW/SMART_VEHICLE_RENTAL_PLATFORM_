const API_URL = 'http://localhost:8000/api';
let currentUser = null;
let authToken = null;
let currentVehicle = null;
let hiddenDealVehicle = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadVehicles();
    setupEventListeners();
    checkAuth();
});

function setupEventListeners() {
    // Register form
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('bookingForm').addEventListener('submit', handleBooking);
    
    // Vehicle filter
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filterVehicles(e.target.dataset.filter);
        });
    });
    
    // Chatbot
    document.getElementById('chatbot-toggle').addEventListener('click', toggleChatbot);
    document.getElementById('chatbot-close').addEventListener('click', toggleChatbot);
    document.getElementById('chatbot-send').addEventListener('click', sendChatMessage);
    document.getElementById('chatbot-input-field').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    
    // Date change for price calculation
    document.getElementById('pickupDate').addEventListener('change', calculatePrice);
    document.getElementById('dropoffDate').addEventListener('change', calculatePrice);
    document.getElementById('driverRequired').addEventListener('change', calculatePrice);
}

async function loadVehicles() {
    try {
        const response = await fetch(`${API_URL}/vehicles/`);
        const vehicles = await response.json();
        displayVehicles(vehicles);
    } catch (error) {
        console.error('Error loading vehicles:', error);
        // Load sample vehicles if API fails
        loadSampleVehicles();
    }
}

function loadSampleVehicles() {
    const sampleVehicles = [
        {id: 1, name: "Swift Dzire", brand: "Maruti", model: "Dzire", vehicle_type: "car", price_per_day: 1500, seats: 4, transmission: "Manual", fuel_type: "Petrol", has_driver_option: true, driver_charge_per_day: 500},
        {id: 2, name: "Creta", brand: "Hyundai", model: "Creta", vehicle_type: "suv", price_per_day: 2500, seats: 5, transmission: "Automatic", fuel_type: "Diesel", has_driver_option: true, driver_charge_per_day: 600},
        {id: 3, name: "City", brand: "Honda", model: "City", vehicle_type: "car", price_per_day: 1800, seats: 4, transmission: "Automatic", fuel_type: "Petrol", has_driver_option: true, driver_charge_per_day: 500},
        {id: 4, name: "Innova Crysta", brand: "Toyota", model: "Innova", vehicle_type: "suv", price_per_day: 3500, seats: 7, transmission: "Manual", fuel_type: "Diesel", has_driver_option: true, driver_charge_per_day: 700},
        {id: 5, name: "Splendor Plus", brand: "Hero", model: "Splendor", vehicle_type: "bike", price_per_day: 500, seats: 2, transmission: "Manual", fuel_type: "Petrol", has_driver_option: false},
        {id: 6, name: "Mercedes C-Class", brand: "Mercedes", model: "C-Class", vehicle_type: "luxury", price_per_day: 8000, seats: 4, transmission: "Automatic", fuel_type: "Petrol", has_driver_option: true, driver_charge_per_day: 1000},
        {id: 7, name: "Fortuner", brand: "Toyota", model: "Fortuner", vehicle_type: "suv", price_per_day: 4000, seats: 7, transmission: "Automatic", fuel_type: "Diesel", has_driver_option: true, driver_charge_per_day: 800},
        {id: 8, name: "i20", brand: "Hyundai", model: "i20", vehicle_type: "car", price_per_day: 1200, seats: 4, transmission: "Manual", fuel_type: "Petrol", has_driver_option: true, driver_charge_per_day: 450}
    ];
    displayVehicles(sampleVehicles);
}

function displayVehicles(vehicles) {
    const container = document.getElementById('vehicles-container');
    container.innerHTML = vehicles.map(vehicle => `
        <div class="col-md-6 col-lg-3 vehicle-item" data-type="${vehicle.vehicle_type}">
            <div class="vehicle-card">
                <img src="https://source.unsplash.com/400x300/?${vehicle.vehicle_type},car" alt="${vehicle.name}">
                <div class="vehicle-card-body">
                    <h5 class="vehicle-card-title">${vehicle.brand} ${vehicle.model}</h5>
                    <p class="text-muted">${vehicle.name}</p>
                    <div class="vehicle-specs">
                        <span><i class="fas fa-users"></i> ${vehicle.seats}</span>
                        <span><i class="fas fa-cog"></i> ${vehicle.transmission}</span>
                        <span><i class="fas fa-gas-pump"></i> ${vehicle.fuel_type}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="vehicle-price">₹${vehicle.price_per_day}/day</span>
                    </div>
                    ${vehicle.has_driver_option ? '<small class="text-success"><i class="fas fa-user-tie"></i> Driver available</small>' : ''}
                    <button class="btn btn-primary w-100 mt-3" onclick="openBookingModal(${vehicle.id})">Book Now</button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterVehicles(type) {
    const items = document.querySelectorAll('.vehicle-item');
    items.forEach(item => {
        if (type === 'all' || item.dataset.type === type) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

async function handleRegister(e) {
    e.preventDefault();
    const data = {
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        full_name: document.getElementById('regName').value,
        phone: document.getElementById('regPhone').value
    };
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
        } else {
            const error = await response.json();
            alert(error.detail || 'Registration failed');
        }
    } catch (error) {
        alert('Registration successful (demo mode)');
        bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const data = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const tokenData = await response.json();
            authToken = tokenData.access_token;
            currentUser = {email: data.email};
            localStorage.setItem('token', authToken);
            alert('Login successful!');
            bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
            updateUIForLoggedInUser();
        } else {
            alert('Login successful (demo mode)');
            bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
            currentUser = {email: data.email};
        }
    } catch (error) {
        alert('Login successful (demo mode)');
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
        currentUser = {email: data.email};
    }
}

function checkAuth() {
    authToken = localStorage.getItem('token');
    if (authToken) {
        updateUIForLoggedInUser();
    }
}

function updateUIForLoggedInUser() {
    document.querySelector('.btn-register').textContent = 'Dashboard';
    document.querySelector('.btn-register').setAttribute('onclick', 'window.location.href="dashboard.html"');
    document.querySelector('.btn-login').textContent = 'Logout';
    document.querySelector('.btn-login').setAttribute('onclick', 'logout()');
}

function logout() {
    localStorage.removeItem('token');
    authToken = null;
    currentUser = null;
    location.reload();
}

async function openBookingModal(vehicleId) {
    currentVehicle = vehicleId;
    const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
    modal.show();
    
    // Set minimum date to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('pickupDate').min = now.toISOString().slice(0, 16);
    
    document.getElementById('selectedVehicleInfo').innerHTML = `
        <div class="alert alert-info">
            <strong>Booking:</strong> Vehicle ID #${vehicleId}
        </div>
    `;
}

function calculatePrice() {
    const pickupDate = new Date(document.getElementById('pickupDate').value);
    const dropoffDate = new Date(document.getElementById('dropoffDate').value);
    const driverRequired = document.getElementById('driverRequired').checked;
    
    if (pickupDate && dropoffDate && dropoffDate > pickupDate) {
        const totalDays = Math.ceil((dropoffDate - pickupDate) / (1000 * 60 * 60 * 24));
        const basePrice = 1500 * totalDays; // Sample price
        let discount = 0;
        
        // 15% discount for bookings above 2 days
        if (totalDays > 2) {
            discount += basePrice * 0.15;
        }
        
        // 20% discount for new users (if logged in)
        if (!localStorage.getItem('hasBookedBefore')) {
            discount += basePrice * 0.20;
        }
        
        const driverCharge = driverRequired ? 500 * totalDays : 0;
        const finalAmount = basePrice + driverCharge - discount;
        
        document.getElementById('breakdownContent').innerHTML = `
            <div class="d-flex justify-content-between"><span>Base Price (${totalDays} days):</span><span>₹${basePrice}</span></div>
            ${driverRequired ? `<div class="d-flex justify-content-between"><span>Driver Charge:</span><span>₹${driverCharge}</span></div>` : ''}
            ${discount > 0 ? `<div class="d-flex justify-content-between text-success"><span>Discount:</span><span>-₹${discount.toFixed(2)}</span></div>` : ''}
            <hr>
            <div class="d-flex justify-content-between fw-bold"><span>Total:</span><span>₹${finalAmount.toFixed(2)}</span></div>
        `;
        
        // Check for hidden deals
        checkHiddenDeals(basePrice, totalDays);
    }
}

async function checkHiddenDeals(basePrice, totalDays) {
    try {
        const response = await fetch(`${API_URL}/vehicles/${currentVehicle}/similar`);
        if (response.ok) {
            const similarVehicles = await response.json();
            if (similarVehicles.length > 0) {
                const bestDeal = similarVehicles[0];
                const savings = (1500 - bestDeal.price_per_day) * totalDays;
                
                if (savings > 0) {
                    hiddenDealVehicle = bestDeal;
                    document.getElementById('hiddenDealAlert').classList.remove('d-none');
                    document.getElementById('hiddenDealMessage').innerHTML = `
                        Switch to ${bestDeal.brand} ${bestDeal.model} and save ₹${savings.toFixed(2)}!
                        <br><small>Same category, better price!</small>
                    `;
                }
            }
        }
    } catch (error) {
        console.log('Hidden deal check:', error);
    }
}

function switchToDeal() {
    if (hiddenDealVehicle) {
        currentVehicle = hiddenDealVehicle.id;
        document.getElementById('bookingVehicleId').value = hiddenDealVehicle.id;
        document.getElementById('selectedVehicleInfo').innerHTML = `
            <div class="alert alert-success">
                <strong>Switched to Deal:</strong> ${hiddenDealVehicle.brand} ${hiddenDealVehicle.model}
            </div>
        `;
        document.getElementById('hiddenDealAlert').classList.add('d-none');
        calculatePrice();
    }
}

async function validateCoupon() {
    const code = document.getElementById('couponCode').value;
    if (!code) return;
    
    try {
        const response = await fetch(`${API_URL}/coupons/validate/${code}`);
        const result = await response.json();
        
        const messageEl = document.getElementById('couponMessage');
        if (result.valid) {
            messageEl.textContent = `✓ Valid coupon! ${result.discount_percentage}% off`;
            messageEl.className = 'text-success';
        } else {
            messageEl.textContent = `✗ ${result.message}`;
            messageEl.className = 'text-danger';
        }
    } catch (error) {
        document.getElementById('couponMessage').textContent = 'Coupon applied (demo mode)';
    }
}

async function handleBooking(e) {
    e.preventDefault();
    
    const bookingData = {
        vehicle_id: currentVehicle,
        start_date: document.getElementById('pickupDate').value,
        end_date: document.getElementById('dropoffDate').value,
        driver_required: document.getElementById('driverRequired').checked,
        coupon_code: document.getElementById('couponCode').value
    };
    
    // Simulate Razorpay payment
    const options = {
        "key": "rzp_test_sample",
        "amount": 500000,
        "currency": "INR",
        "name": "Smart Vehicle Rental",
        "description": "Vehicle Booking Payment",
        "handler": function(response) {
            alert('Payment successful! Booking confirmed.');
            localStorage.setItem('hasBookedBefore', 'true');
            bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide();
        }
    };
    
    // In demo mode, just show success
    alert('Booking request submitted! Proceeding to payment...');
    const rzp = new Razorpay(options);
    rzp.open();
}

// Chatbot functions
function toggleChatbot() {
    const window = document.getElementById('chatbot-window');
    window.classList.toggle('d-none');
    if (!window.classList.contains('d-none')) {
        addBotMessage('Hello! I\'m your AI assistant. How can I help you today?');
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatbot-input-field');
    const message = input.value.trim();
    if (!message) return;
    
    addUserMessage(message);
    input.value = '';
    
    try {
        const response = await fetch(`${API_URL}/chatbot/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        if (response.ok) {
            const data = await response.json();
            addBotMessage(data.response);
        } else {
            addBotMessage('I understand you\'re asking about "' + message + '". Feel free to ask about vehicles, bookings, discounts, or our services!');
        }
    } catch (error) {
        addBotMessage('Thanks for your message! Ask me about vehicles, bookings, discounts, drivers, or loyalty rewards.');
    }
}

function addUserMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.innerHTML += `<div class="chatbot-message user">${message}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addBotMessage(message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.innerHTML += `<div class="chatbot-message bot">${message.replace(/\n/g, '<br>')}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
