// Authentication utilities

async function login(email, password) {
    try {
        const response = await api.login(email, password);
        
        if (response.access_token) {
            setToken(response.access_token);
            setUser(response.user || response);
            
            // Redirect based on role
            if (response.user?.is_admin || response.is_admin) {
                window.location.href = 'admin/dashboard.html';
            } else {
                window.location.href = 'dashboard.html';
            }
        }
    } catch (error) {
        throw error;
    }
}

async function register(userData) {
    try {
        const response = await api.register(userData);
        
        if (response.access_token) {
            setToken(response.access_token);
            setUser(response.user || response);
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        throw error;
    }
}

async function logout() {
    removeToken();
    window.location.href = 'index.html';
}

async function forgotPassword(email) {
    try {
        await api.forgotPassword(email);
        return true;
    } catch (error) {
        throw error;
    }
}

async function resetPassword(token, newPassword) {
    try {
        await api.resetPassword(token, newPassword);
        return true;
    } catch (error) {
        throw error;
    }
}

async function loadUserProfile() {
    try {
        const user = await api.getCurrentUser();
        setUser(user);
        return user;
    } catch (error) {
        console.error('Failed to load profile:', error);
        throw error;
    }
}

async function updateProfile(userData) {
    try {
        const user = await api.updateProfile(userData);
        setUser(user);
        return user;
    } catch (error) {
        throw error;
    }
}

async function changePassword(currentPassword, newPassword) {
    try {
        await api.changePassword({
            current_password: currentPassword,
            new_password: newPassword
        });
        return true;
    } catch (error) {
        throw error;
    }
}

// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (token) {
        try {
            await autoLogin();
            updateUserInterface();
        } catch (error) {
            console.error('Auth initialization failed:', error);
        }
    }
});

function updateUserInterface() {
    const user = getUser();
    if (!user) return;

    // Update user info in sidebar/header
    const userNameElements = document.querySelectorAll('#userName, .user-name');
    userNameElements.forEach(el => {
        if (el) el.textContent = user.full_name || user.name || user.email;
    });

    const userRoleElements = document.querySelectorAll('#userRole, .user-role');
    userRoleElements.forEach(el => {
        if (el) el.textContent = user.is_admin ? 'Admin' : 'User';
    });

    const userAvatarElements = document.querySelectorAll('#userAvatar, .user-avatar');
    userAvatarElements.forEach(el => {
        if (el && user.profile_image_url) {
            el.src = user.profile_image_url;
        }
    });

    // Show/hide admin links
    if (user.is_admin) {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = '';
        });
    } else {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'none';
        });
    }
}

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Theme toggle
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
    
    // Update icon
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    }
}

// Load saved theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        const icon = document.querySelector('.theme-toggle i');
        if (icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
});
