// Profile page functionality

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadProfile();
    
    // Setup form handlers
    document.getElementById('profileForm')?.addEventListener('submit', handleProfileUpdate);
    document.getElementById('passwordForm')?.addEventListener('submit', handlePasswordChange);
});

async function loadProfile() {
    try {
        const user = await loadUserProfile();
        
        if (user) {
            // Update profile info
            document.getElementById('profileName').textContent = user.full_name || user.name;
            document.getElementById('profileEmail').textContent = user.email;
            
            // Fill form fields
            document.getElementById('fullName').value = user.full_name || user.name || '';
            document.getElementById('email').value = user.email || '';
            document.getElementById('phone').value = user.phone || '';
            
            // Update avatar if available
            if (user.profile_image_url) {
                document.getElementById('profileAvatar').src = user.profile_image_url;
            }
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
        showToast('Failed to load profile information', 'error');
    }
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    
    clearErrors('profileForm');
    
    const fullName = document.getElementById('fullName').value.trim();
    const phone = document.getElementById('phone').value.trim();
    
    // Validation
    let hasError = false;
    
    if (!fullName) {
        showError('fullName', 'Full name is required');
        hasError = true;
    }
    
    if (!phone) {
        showError('phone', 'Phone number is required');
        hasError = true;
    } else if (!isValidPhone(phone)) {
        showError('phone', 'Please enter a valid phone number');
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        setButtonLoading('updateProfileBtn', true);
        
        await updateProfile({
            full_name: fullName,
            phone: phone
        });
        
        showToast('Profile updated successfully!', 'success');
        loadProfile();
    } catch (error) {
        console.error('Failed to update profile:', error);
        showToast(error.message || 'Failed to update profile', 'error');
    } finally {
        setButtonLoading('updateProfileBtn', false);
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();
    
    clearErrors('passwordForm');
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validation
    let hasError = false;
    
    if (!currentPassword) {
        showError('currentPassword', 'Current password is required');
        hasError = true;
    }
    
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
    
    if (!confirmPassword) {
        showError('confirmPassword', 'Please confirm your new password');
        hasError = true;
    } else if (newPassword !== confirmPassword) {
        showError('confirmPassword', 'Passwords do not match');
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        setButtonLoading('changePasswordBtn', true);
        
        await changePassword(currentPassword, newPassword);
        
        showToast('Password changed successfully!', 'success');
        
        // Clear form
        document.getElementById('passwordForm').reset();
    } catch (error) {
        console.error('Failed to change password:', error);
        showToast(error.message || 'Failed to change password', 'error');
    } finally {
        setButtonLoading('changePasswordBtn', false);
    }
}

function showProfileSection(section) {
    // Hide all sections
    document.getElementById('personalSection').style.display = 'none';
    document.getElementById('securitySection').style.display = 'none';
    
    // Show selected section
    document.getElementById(`${section}Section`).style.display = 'block';
    
    // Update active tab
    document.querySelectorAll('.profile-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.tab-btn').classList.add('active');
}

async function uploadAvatar(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showToast('Please select a valid image file (JPEG, PNG, GIF, or WebP)', 'error');
        return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('Image size must be less than 5MB', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Note: This assumes a profile image upload endpoint exists
        // Adjust the API call based on your backend implementation
        const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        
        // Update avatar display
        document.getElementById('profileAvatar').src = result.avatar_url + '?t=' + Date.now();
        
        // Update user data
        const user = getUser();
        user.profile_image_url = result.avatar_url;
        setUser(user);
        
        showToast('Profile picture updated successfully!', 'success');
    } catch (error) {
        console.error('Failed to upload avatar:', error);
        showToast(error.message || 'Failed to upload profile picture', 'error');
    }
}
