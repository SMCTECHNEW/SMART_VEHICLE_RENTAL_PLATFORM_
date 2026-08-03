// Register page functionality

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    
    if (form) {
        form.addEventListener('submit', handleRegister);
    }
});

async function handleRegister(event) {
    event.preventDefault();
    
    clearErrors('registerForm');
    
    // Get form values
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const terms = document.getElementById('terms').checked;
    
    // Validation
    let hasError = false;
    
    if (!fullName) {
        showError('fullName', 'Full name is required');
        hasError = true;
    }
    
    if (!email) {
        showError('email', 'Email is required');
        hasError = true;
    } else if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email');
        hasError = true;
    }
    
    if (!phone) {
        showError('phone', 'Phone number is required');
        hasError = true;
    } else if (!isValidPhone(phone)) {
        showError('phone', 'Please enter a valid phone number');
        hasError = true;
    }
    
    if (!password) {
        showError('password', 'Password is required');
        hasError = true;
    } else {
        const passwordErrors = validatePassword(password);
        if (passwordErrors.length > 0) {
            showError('password', passwordErrors[0]);
            hasError = true;
        }
    }
    
    if (!confirmPassword) {
        showError('confirmPassword', 'Please confirm your password');
        hasError = true;
    } else if (password !== confirmPassword) {
        showError('confirmPassword', 'Passwords do not match');
        hasError = true;
    }
    
    if (!terms) {
        showToast('You must agree to the terms and conditions', 'warning');
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        setButtonLoading('registerBtn', true);
        
        await register({
            email: email,
            password: password,
            full_name: fullName,
            phone: phone
        });
        
        showToast('Registration successful! Redirecting...', 'success');
        
        // Redirect happens in auth.js after successful registration
    } catch (error) {
        console.error('Registration error:', error);
        showToast(error.message || 'Registration failed. Please try again.', 'error');
    } finally {
        setButtonLoading('registerBtn', false);
    }
}
