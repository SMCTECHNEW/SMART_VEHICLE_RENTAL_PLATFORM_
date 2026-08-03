// Admin Dashboard functionality

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAdmin()) return;
    loadAdminDashboard();
    setupNavigation();
});

async function loadAdminDashboard() {
    try {
        await loadOverviewStats();
        await loadUsers();
        await loadVehicles();
        await loadAdminBookings('all');
        await loadReviews();
    } catch (error) {
        console.error('Failed to load admin dashboard:', error);
        showToast('Failed to load admin dashboard', 'error');
    }
}

async function loadOverviewStats() {
    try {
        const [users, vehicles, bookings] = await Promise.all([
            api.getAllUsers(),
            api.getAllVehicles(),
            api.getAllBookings()
        ]);
        
        document.getElementById('totalUsers').textContent = users.length || 0;
        document.getElementById('totalVehicles').textContent = vehicles.length || 0;
        document.getElementById('totalBookings').textContent = bookings.length || 0;
        
        const totalRevenue = bookings
            .filter(b => b.status === 'completed')
            .reduce((sum, b) => sum + (b.total_amount || 0), 0);
        document.getElementById('totalRevenue').textContent = formatCurrency(totalRevenue);
        
        // Recent activity
        const recentBookings = bookings.slice(0, 5);
        const activityContainer = document.getElementById('recentActivity');
        
        if (recentBookings.length === 0) {
            activityContainer.innerHTML = '<p class="text-muted">No recent activity</p>';
        } else {
            activityContainer.innerHTML = `
                <div class="activity-list">
                    ${recentBookings.map(b => `
                        <div class="activity-item">
                            <i class="fas fa-calendar-check"></i>
                            <div class="activity-details">
                                <p><strong>Booking #${b.id}</strong> - ${b.vehicle?.name || 'N/A'}</p>
                                <small>${formatDateTime(b.created_at)} - ${b.status}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadUsers() {
    try {
        const users = await api.getAllUsers();
        const tbody = document.getElementById('usersTableBody');
        
        if (users.length === 0) {
            showEmpty('usersTableBody', 'No users found');
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>#${user.id}</td>
                <td>${user.full_name || user.name || 'N/A'}</td>
                <td>${user.email}</td>
                <td>${user.phone || 'N/A'}</td>
                <td><span class="badge ${user.is_admin ? 'status-confirmed' : 'status-pending'}">${user.is_admin ? 'Admin' : 'User'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editUser('${user.id}')">Edit</button>
                    ${!user.is_admin ? `<button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${user.id}')">Delete</button>` : ''}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load users:', error);
        showErrorState('usersTableBody', 'Failed to load users');
    }
}

async function loadVehicles() {
    try {
        const vehicles = await api.getAllVehicles();
        const tbody = document.getElementById('vehiclesTableBody');
        
        if (vehicles.length === 0) {
            showEmpty('vehiclesTableBody', 'No vehicles found');
            return;
        }
        
        tbody.innerHTML = vehicles.map(vehicle => `
            <tr>
                <td>#${vehicle.id}</td>
                <td>${vehicle.name}</td>
                <td>${vehicle.brand} ${vehicle.model}</td>
                <td>${formatCurrency(vehicle.price_per_day)}</td>
                <td><span class="booking-status ${vehicle.available ? 'status-confirmed' : 'status-cancelled'}">${vehicle.available ? 'Available' : 'Unavailable'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editVehicle('${vehicle.id}')">Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteVehicle('${vehicle.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load vehicles:', error);
        showErrorState('vehiclesTableBody', 'Failed to load vehicles');
    }
}

async function loadAdminBookings(status) {
    try {
        const bookings = await api.getAllBookings();
        let filtered = bookings;
        
        if (status !== 'all') {
            filtered = bookings.filter(b => b.status === status);
        }
        
        const tbody = document.getElementById('adminBookingsTableBody');
        
        if (filtered.length === 0) {
            showEmpty('adminBookingsTableBody', 'No bookings found');
            return;
        }
        
        tbody.innerHTML = filtered.map(booking => `
            <tr>
                <td>#${booking.id}</td>
                <td>${booking.user?.full_name || booking.user?.email || 'N/A'}</td>
                <td>${booking.vehicle?.name || 'N/A'}</td>
                <td>${formatDate(booking.start_date)} - ${formatDate(booking.end_date)}</td>
                <td>${formatCurrency(booking.total_amount)}</td>
                <td><span class="booking-status ${getStatusBadgeClass(booking.status)}">${booking.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewBooking('${booking.id}')">View</button>
                    ${booking.status === 'pending' ? `
                        <button class="btn btn-sm btn-success" onclick="confirmBooking('${booking.id}')">Confirm</button>
                        <button class="btn btn-sm btn-danger" onclick="rejectBooking('${booking.id}')">Reject</button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
        
        // Update active tab
        document.querySelectorAll('#bookingsSection .tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event?.target?.classList.add('active');
    } catch (error) {
        console.error('Failed to load bookings:', error);
        showErrorState('adminBookingsTableBody', 'Failed to load bookings');
    }
}

async function loadReviews() {
    try {
        // Note: This assumes there's an endpoint to get all reviews
        // Adjust based on your backend implementation
        const tbody = document.getElementById('reviewsTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No reviews management endpoint available</p>
                </td>
            </tr>
        `;
    } catch (error) {
        console.error('Failed to load reviews:', error);
    }
}

function setupNavigation() {
    document.querySelectorAll('.sidebar-nav .nav-item[data-section]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            
            // Update active nav
            document.querySelectorAll('.sidebar-nav .nav-item').forEach(nav => {
                nav.classList.remove('active');
            });
            item.classList.add('active');
            
            // Show/hide sections
            document.querySelectorAll('.admin-section').forEach(sec => {
                sec.style.display = 'none';
            });
            document.getElementById(`${section}Section`).style.display = 'block';
        });
    });
}

// CRUD Actions
async function confirmBooking(bookingId) {
    if (!confirm('Confirm this booking?')) return;
    
    try {
        // Implement booking confirmation
        showToast('Booking confirmed', 'success');
        loadAdminBookings('all');
    } catch (error) {
        showToast('Failed to confirm booking', 'error');
    }
}

async function rejectBooking(bookingId) {
    if (!confirm('Reject this booking?')) return;
    
    try {
        // Implement booking rejection
        showToast('Booking rejected', 'success');
        loadAdminBookings('all');
    } catch (error) {
        showToast('Failed to reject booking', 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        // Implement user deletion
        showToast('User deleted', 'success');
        loadUsers();
    } catch (error) {
        showToast('Failed to delete user', 'error');
    }
}

async function deleteVehicle(vehicleId) {
    if (!confirm('Are you sure you want to delete this vehicle?')) return;
    
    try {
        // Implement vehicle deletion
        showToast('Vehicle deleted', 'success');
        loadVehicles();
    } catch (error) {
        showToast('Failed to delete vehicle', 'error');
    }
}

function showAddUserModal() {
    alert('Add User modal - implement based on your requirements');
}

function showAddVehicleModal() {
    alert('Add Vehicle modal - implement based on your requirements');
}

function editUser(userId) {
    alert(`Edit User ${userId} - implement based on your requirements`);
}

function editVehicle(vehicleId) {
    alert(`Edit Vehicle ${vehicleId} - implement based on your requirements`);
}

function viewBooking(bookingId) {
    window.location.href = `../booking-history.html?id=${bookingId}`;
}
