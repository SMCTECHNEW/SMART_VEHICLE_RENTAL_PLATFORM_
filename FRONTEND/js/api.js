// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Axios-like fetch wrapper
const api = {
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        const url = `${API_BASE_URL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Auth endpoints
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    },

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    async forgotPassword(email) {
        return this.request('/auth/forgot-password', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    },

    async resetPassword(token, newPassword) {
        return this.request('/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ token, new_password: newPassword }),
        });
    },

    async getCurrentUser() {
        return this.request('/users/me');
    },

    async updateProfile(userData) {
        return this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(userData),
        });
    },

    async changePassword(passwordData) {
        return this.request('/users/change-password', {
            method: 'POST',
            body: JSON.stringify(passwordData),
        });
    },

    // Vehicle endpoints
    async getVehicles(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/vehicles?${queryString}`);
    },

    async getVehicle(id) {
        return this.request(`/vehicles/${id}`);
    },

    async checkAvailability(vehicleId, startDate, endDate) {
        return this.request(`/vehicles/check-availability/${vehicleId}?start_date=${startDate}&end_date=${endDate}`);
    },

    // Booking endpoints
    async createBooking(bookingData) {
        return this.request('/bookings', {
            method: 'POST',
            body: JSON.stringify(bookingData),
        });
    },

    async getMyBookings(status = null) {
        const params = status ? `?status=${status}` : '';
        return this.request(`/bookings/my-bookings${params}`);
    },

    async getBookingHistory() {
        return this.request('/bookings/history');
    },

    async getBooking(id) {
        return this.request(`/bookings/${id}`);
    },

    async cancelBooking(id, reason = '') {
        return this.request(`/bookings/${id}/cancel`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    },

    // Payment endpoints
    async createPaymentOrder(bookingId) {
        return this.request('/payments/create-order', {
            method: 'POST',
            body: JSON.stringify({ booking_id: bookingId }),
        });
    },

    async verifyPayment(paymentData) {
        return this.request('/payments/verify', {
            method: 'POST',
            body: JSON.stringify(paymentData),
        });
    },

    async getPayments() {
        return this.request('/payments/my-payments');
    },

    // Review endpoints
    async createReview(reviewData) {
        return this.request('/reviews', {
            method: 'POST',
            body: JSON.stringify(reviewData),
        });
    },

    async getReviews(vehicleId) {
        return this.request(`/vehicles/${vehicleId}/reviews`);
    },

    async updateReview(id, reviewData) {
        return this.request(`/reviews/${id}`, {
            method: 'PUT',
            body: JSON.stringify(reviewData),
        });
    },

    async deleteReview(id) {
        return this.request(`/reviews/${id}`, {
            method: 'DELETE',
        });
    },

    // Admin endpoints
    async getAllUsers() {
        return this.request('/admin/users');
    },

    async getAllBookings() {
        return this.request('/admin/bookings');
    },

    async getAllVehicles() {
        return this.request('/admin/vehicles');
    },

    async getAnalytics(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/analytics?${queryString}`);
    },

    // Driver endpoints
    async getDrivers() {
        return this.request('/drivers');
    },

    async createDriver(driverData) {
        return this.request('/drivers', {
            method: 'POST',
            body: JSON.stringify(driverData),
        });
    },

    async updateDriver(id, driverData) {
        return this.request(`/drivers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(driverData),
        });
    },

    async deleteDriver(id) {
        return this.request(`/drivers/${id}`, {
            method: 'DELETE',
        });
    },

    async assignDriver(bookingId, driverId) {
        return this.request(`/bookings/${bookingId}/assign-driver`, {
            method: 'PATCH',
            body: JSON.stringify({ driver_id: driverId }),
        });
    },

    // Image upload
    async uploadVehicleImage(vehicleId, formData) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/images`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        return response.json();
    },

    async deleteVehicleImage(vehicleId, imageId) {
        return this.request(`/vehicles/${vehicleId}/images/${imageId}`, {
            method: 'DELETE',
        });
    },
};

// Token management
function setToken(token) {
    localStorage.setItem('token', token);
}

function getToken() {
    return localStorage.getItem('token');
}

function removeToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function isAuthenticated() {
    return !!getToken();
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function isAdmin() {
    const user = getUser();
    return user && user.is_admin;
}

// Protected route check
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function requireAdmin() {
    if (!requireAuth()) return false;
    if (!isAdmin()) {
        alert('Access denied. Admin privileges required.');
        window.location.href = 'dashboard.html';
        return false;
    }
    return true;
}

// Auto-login on page load
async function autoLogin() {
    const token = getToken();
    if (!token) return null;
    
    try {
        const user = await api.getCurrentUser();
        setUser(user);
        return user;
    } catch (error) {
        console.error('Auto-login failed:', error);
        removeToken();
        return null;
    }
}
