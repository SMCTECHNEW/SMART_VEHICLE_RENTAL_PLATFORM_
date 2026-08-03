/**
 * API Configuration and Axios Setup
 * Smart Vehicle Rental Platform
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

// Axios instance with interceptors
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor - Add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Handle 401 Unauthorized
            if (error.response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_role');
                window.location.href = '/login.html';
                return;
            }
            
            // Handle 403 Forbidden
            if (error.response.status === 403) {
                showToast('Access denied. You do not have permission.', 'error');
                return;
            }
            
            // Handle 404 Not Found
            if (error.response.status === 404) {
                showToast('Resource not found.', 'error');
                return;
            }
            
            // Handle validation errors
            if (error.response.status === 422) {
                const errors = error.response.detail;
                if (Array.isArray(errors)) {
                    errors.forEach(err => {
                        showToast(`${err.loc.join('.')}: ${err.msg}`, 'error');
                    });
                }
                return;
            }
            
            // Handle server errors
            if (error.response.status >= 500) {
                showToast('Server error. Please try again later.', 'error');
                return;
            }
            
            // Show error message from backend
            const errorMessage = error.response.data?.detail || error.response.data?.message || 'An error occurred';
            showToast(errorMessage, 'error');
        } else if (error.request) {
            showToast('Network error. Please check your connection.', 'error');
        } else {
            showToast(error.message || 'An error occurred', 'error');
        }
        
        return Promise.reject(error);
    }
);

// API Endpoints
const endpoints = {
    // Authentication
    auth: {
        login: '/auth/login',
        register: '/auth/register',
        forgotPassword: '/auth/forgot-password',
        resetPassword: '/auth/reset-password',
        changePassword: '/auth/change-password',
        me: '/auth/me'
    },
    
    // Users
    users: {
        profile: '/users/profile',
        updateProfile: '/users/profile',
        uploadPhoto: '/users/profile/photo'
    },
    
    // Vehicles
    vehicles: {
        list: '/vehicles/',
        available: '/vehicles/available',
        checkAvailability: (id) => `/vehicles/check-availability/${id}`,
        details: (id) => `/vehicles/${id}`,
        create: '/vehicles/',
        update: (id) => `/vehicles/${id}`,
        delete: (id) => `/vehicles/${id}`,
        images: (id) => `/vehicles/${id}/images`,
        uploadImage: (id) => `/vehicles/${id}/images`,
        deleteImage: (vehicleId, imageId) => `/vehicles/${vehicleId}/images/${imageId}`,
        setPrimaryImage: (vehicleId, imageId) => `/vehicles/${vehicleId}/images/set-primary/${imageId}`
    },
    
    // Bookings
    bookings: {
        create: '/bookings/',
        history: '/bookings/history',
        myBookings: '/bookings/my-bookings',
        details: (id) => `/bookings/${id}`,
        cancel: (id) => `/bookings/${id}/cancel`,
        refunds: (id) => `/bookings/${id}/refunds`,
        assignDriver: (id) => `/bookings/${id}/assign-driver`,
        updateStatus: (id) => `/bookings/${id}/status`,
        adminAll: '/bookings/admin/all'
    },
    
    // Payments
    payments: {
        createOrder: '/payments/create-order',
        verify: '/payments/verify',
        myPayments: '/payments/my-payments',
        bookingPayment: (bookingId) => `/payments/${bookingId}`,
        refunds: (bookingId) => `/payments/${bookingId}/refunds`,
        adminAll: '/payments/admin/all'
    },
    
    // Drivers
    drivers: {
        list: '/drivers/',
        details: (id) => `/drivers/${id}`,
        create: '/drivers/',
        update: (id) => `/drivers/${id}`,
        delete: (id) => `/drivers/${id}`,
        toggleStatus: (id) => `/drivers/${id}/toggle-status`
    },
    
    // Reviews
    reviews: {
        create: '/reviews/',
        vehicleReviews: (vehicleId) => `/reviews/vehicle/${vehicleId}`,
        myReviews: '/reviews/my-reviews',
        update: (id) => `/reviews/${id}`,
        delete: (id) => `/reviews/${id}`,
        approve: (id) => `/reviews/${id}/approve`,
        adminAll: '/reviews/admin/all'
    },
    
    // Admin Analytics
    admin: {
        analytics: '/admin/analytics',
        users: '/admin/users',
        vehicles: '/admin/vehicles',
        bookings: '/admin/bookings',
        revenue: '/admin/revenue',
        reports: '/admin/reports'
    }
};

// Helper Functions
function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
}

function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

function getUserRole() {
    return localStorage.getItem('user_role');
}

function isAdmin() {
    return getUserRole() === 'admin';
}

function isUser() {
    return getUserRole() === 'user';
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

function requireAdmin() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    if (!isAdmin()) {
        showToast('Access denied. Admin privileges required.', 'error');
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 2000);
        return false;
    }
    return true;
}

function requireUser() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    if (!isUser()) {
        showToast('Access denied.', 'error');
        setTimeout(() => {
            window.location.href = '/admin/dashboard.html';
        }, 2000);
        return false;
    }
    return true;
}

// Export for use in other modules
window.api = api;
window.endpoints = endpoints;
window.getAuthHeader = getAuthHeader;
window.isAuthenticated = isAuthenticated;
window.getUserRole = getUserRole;
window.isAdmin = isAdmin;
window.isUser = isUser;
window.requireAuth = requireAuth;
window.requireAdmin = requireAdmin;
window.requireUser = requireUser;
