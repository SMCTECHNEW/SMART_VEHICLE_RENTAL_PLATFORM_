// Forgot Password page functionality

document.addEventListener('DOMContentLoaded', () => {
    const forgotForm = document.getElementById('forgotPasswordForm');
    const resetForm = document.getElementById('resetPasswordForm');
    
    // Check for token in URL (reset password step)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Show reset password form
        document.getElementById('resetToken').value = token;
        forgotForm.style.display = 'none';
        resetForm.style.display = 'block';
    }
    
    if (forgotForm) {
        forgotForm.addEventListener('submit', handleForgotPassword);
    }
    
    if (resetForm) {
        resetForm.addEventListener('submit', handleResetPassword);
    }
});

async function handleForgotPassword(event) {
    event.preventDefault();
    
    clearErrors('forgotPasswordForm');
    
    const email = document.getElementById('email').value.trim();
    
    // Validation
    if (!email) {
        showError('email', 'Email is required');
        return;
    }
    
    if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email');
        return;
    }
    
    try {
        setButtonLoading('sendResetBtn', true);
        
        await forgotPassword(email);
        
        showToast('Password reset link sent to your email!', 'success');
        
        // Show success message
        document.getElementById('forgotPasswordForm').style.display = 'none';
        document.getElementById('successMessage').style.display = 'block';
        
    } catch (error) {
        console.error('Forgot password error:', error);
        showToast(error.message || 'Failed to send reset link. Please try again.', 'error');
    } finally {
        setButtonLoading('sendResetBtn', false);
    }
}

async function handleResetPassword(event) {
    event.preventDefault();
    
    clearErrors('resetPasswordForm');
    
    const token = document.getElementById('resetToken').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    // Validation
    let hasError = false;
    
    if (!newPassword) {
        showError('newPassword', 'New password is required');
        hasError = true;
    } else {
        const passwordErrors = validatePassword(newPassword);
        if (passwordErrors.length > 0) {
            showError('newPassword', passwordErrors[0]);
            hasError = true;
        }
    }
    
    if (!confirmNewPassword) {
        showError('confirmNewPassword', 'Please confirm your new password');
        hasError = true;
    } else if (newPassword !== confirmNewPassword) {
        showError('confirmNewPassword', 'Passwords do not match');
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        setButtonLoading('resetPasswordBtn', true);
        
        await resetPassword(token, newPassword);
        
        showToast('Password reset successful!', 'success');
        
        // Show success message
        document.getElementById('resetPasswordForm').style.display = 'none';
        document.getElementById('successMessage').style.display = 'block';
        
    } catch (error) {
        console.error('Reset password error:', error);
        showToast(error.message || 'Failed to reset password. The link may have expired.', 'error');
    } finally {
        setButtonLoading('resetPasswordBtn', false);
    }
}
