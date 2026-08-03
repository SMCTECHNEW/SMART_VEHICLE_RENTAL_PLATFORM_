/**
 * Authentication Module
 * Smart Vehicle Rental Platform
 */

// Login Function
async function login(email, password) {
    try {
        const response = await api.post(endpoints.auth.login, { email, password });
        const data = response.data;
        
        // Store tokens
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
        }
        
        // Decode token to get user info
        const userInfo = decodeToken(data.access_token);
        localStorage.setItem('user_id', userInfo.sub);
        localStorage.setItem('user_email', userInfo.email || email);
        localStorage.setItem('user_role', userInfo.role || 'user');
        localStorage.setItem('user_name', userInfo.full_name || '');
        
        showToast('Login successful!', 'success');
        
        // Redirect based on role
        setTimeout(() => {
            if (userInfo.role === 'admin') {
                window.location.href = '/admin/dashboard.html';
            } else {
                window.location.href = '/dashboard.html';
            }
        }, 1000);
        
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// Register Function
async function register(userData) {
    try {
        const response = await api.post(endpoints.auth.register, userData);
        const data = response.data;
        
        showToast('Registration successful! Please login.', 'success');
        
        setTimeout(() => {
            window.location.href = '/login.html';
        }, 1500);
        
        return data;
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

// Logout Function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    
    showToast('Logged out successfully!', 'success');
    
    setTimeout(() => {
        window.location.href = '/index.html';
    }, 1000);
}

// Forgot Password
async function forgotPassword(email) {
    try {
        const response = await api.post(endpoints.auth.forgotPassword, { email });
        
        showToast('Password reset link sent to your email!', 'success');
        return response.data;
    } catch (error) {
        console.error('Forgot password error:', error);
        throw error;
    }
}

// Reset Password
async function resetPassword(token, newPassword) {
    try {
        const response = await api.post(endpoints.auth.resetPassword, {
            token,
            new_password: newPassword
        });
        
        showToast('Password reset successful! Please login.', 'success');
        
        setTimeout(() => {
            window.location.href = '/login.html';
        }, 1500);
        
        return response.data;
    } catch (error) {
        console.error('Reset password error:', error);
        throw error;
    }
}

// Change Password
async function changePassword(currentPassword, newPassword) {
    try {
        const response = await api.post(endpoints.auth.changePassword, {
            current_password: currentPassword,
            new_password: newPassword
        });
        
        showToast('Password changed successfully!', 'success');
        return response.data;
    } catch (error) {
        console.error('Change password error:', error);
        throw error;
    }
}

// Get Current User Profile
async function getCurrentUser() {
    try {
        const response = await api.get(endpoints.auth.me);
        return response.data;
    } catch (error) {
        console.error('Get current user error:', error);
        throw error;
    }
}

// Update User Profile
async function updateProfile(profileData) {
    try {
        const response = await api.put(endpoints.users.updateProfile, profileData);
        
        // Update local storage with new info
        if (response.data.full_name) {
            localStorage.setItem('user_name', response.data.full_name);
        }
        if (response.data.email) {
            localStorage.setItem('user_email', response.data.email);
        }
        
        showToast('Profile updated successfully!', 'success');
        return response.data;
    } catch (error) {
        console.error('Update profile error:', error);
        throw error;
    }
}

// Upload Profile Photo
async function uploadProfilePhoto(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post(endpoints.users.uploadPhoto, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        showToast('Profile photo uploaded successfully!', 'success');
        return response.data;
    } catch (error) {
        console.error('Upload photo error:', error);
        throw error;
    }
}

// Helper: Decode JWT Token
function decodeToken(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Token decode error:', error);
        return {};
    }
}

// Check if user is logged in and redirect if needed
function checkAuth(redirectIfNotAuth = false) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        if (redirectIfNotAuth) {
            window.location.href = '/login.html';
        }
        return false;
    }
    
    // Check token expiry
    const userInfo = decodeToken(token);
    const now = Math.floor(Date.now() / 1000);
    
    if (userInfo.exp && userInfo.exp < now) {
        // Token expired
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        
        if (redirectIfNotAuth) {
            window.location.href = '/login.html';
        }
        return false;
    }
    
    return true;
}

// Update UI based on authentication state
function updateAuthUI() {
    const isLoggedIn = checkAuth();
    const userName = localStorage.getItem('user_name') || '';
    const userEmail = localStorage.getItem('user_email') || '';
    const userRole = localStorage.getItem('user_role') || '';
    
    // Update navbar
    const navAuthContainer = document.getElementById('navAuthContainer');
    if (navAuthContainer) {
        if (isLoggedIn) {
            navAuthContainer.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-circle me-1"></i>${userName || 'User'}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="/dashboard.html"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
                        <li><a class="dropdown-item" href="/profile.html"><i class="fas fa-user me-2"></i>Profile</a></li>
                        <li><a class="dropdown-item" href="/booking-history.html"><i class="fas fa-calendar-alt me-2"></i>My Bookings</a></li>
                        ${userRole === 'admin' ? '<li><hr class="dropdown-divider"></li>' : ''}
                        ${userRole === 'admin' ? '<li><a class="dropdown-item" href="/admin/dashboard.html"><i class="fas fa-shield-alt me-2"></i>Admin Panel</a></li>' : ''}
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                    </ul>
                </li>
            `;
        } else {
            navAuthContainer.innerHTML = `
                <li class="nav-item"><a class="nav-link" href="/login.html">Login</a></li>
                <li class="nav-item"><a class="nav-link btn-register" href="/register.html">Register</a></li>
            `;
        }
    }
    
    // Update user info display if exists
    const userInfoDisplay = document.getElementById('userInfoDisplay');
    if (userInfoDisplay && isLoggedIn) {
        userInfoDisplay.innerHTML = `
            <div class="user-info">
                <img src="/assets/images/default-avatar.png" alt="${userName}" class="user-avatar" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=4361ee&color=fff'">
                <div>
                    <h6 class="mb-0">${userName}</h6>
                    <small class="text-muted">${userEmail}</small>
                </div>
            </div>
        `;
    }
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
});

// Export functions
window.login = login;
window.register = register;
window.logout = logout;
window.forgotPassword = forgotPassword;
window.resetPassword = resetPassword;
window.changePassword = changePassword;
window.getCurrentUser = getCurrentUser;
window.updateProfile = updateProfile;
window.uploadProfilePhoto = uploadProfilePhoto;
window.checkAuth = checkAuth;
window.updateAuthUI = updateAuthUI;
window.decodeToken = decodeToken;
