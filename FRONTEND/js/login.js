// Login page functionality

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    
    if (form) {
        form.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(event) {
    event.preventDefault();
    
    clearErrors('loginForm');
    
    // Get form values
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    
    // Validation
    let hasError = false;
    
    if (!email) {
        showError('email', 'Email is required');
        hasError = true;
    } else if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email');
        hasError = true;
    }
    
    if (!password) {
        showError('password', 'Password is required');
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        setButtonLoading('loginBtn', true);
        
        await login(email, password);
        
        showToast('Login successful! Redirecting...', 'success');
        
        // Redirect happens in auth.js after successful login
    } catch (error) {
        console.error('Login error:', error);
        showToast(error.message || 'Login failed. Please check your credentials.', 'error');
    } finally {
        setButtonLoading('loginBtn', false);
    }
}
