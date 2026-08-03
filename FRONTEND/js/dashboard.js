// Dashboard page functionality

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Load user info
        const user = getUser();
        if (user) {
            document.getElementById('userName').textContent = user.full_name || user.name || user.email;
            document.getElementById('userRole').textContent = user.is_admin ? 'Admin' : 'User';
            
            if (user.profile_image_url) {
                document.getElementById('userAvatar').src = user.profile_image_url;
            }
        }
        
        // Load bookings stats
        await loadBookingStats();
        
        // Load recent bookings
        await loadRecentBookings();
        
        // Load available vehicles
        await loadAvailableVehicles();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

async function loadBookingStats() {
    try {
        const bookings = await api.getBookingHistory();
        
        const total = bookings.length;
        const completed = bookings.filter(b => b.status === 'completed').length;
        const upcoming = bookings.filter(b => 
            ['pending', 'confirmed', 'active'].includes(b.status)
        ).length;
        
        const totalSpent = bookings
            .filter(b => b.status === 'completed')
            .reduce((sum, b) => sum + (b.total_amount || 0), 0);
        
        document.getElementById('totalBookings').textContent = total;
        document.getElementById('completedBookings').textContent = completed;
        document.getElementById('upcomingBookings').textContent = upcoming;
        document.getElementById('totalSpent').textContent = formatCurrency(totalSpent);
    } catch (error) {
        console.error('Failed to load booking stats:', error);
    }
}

async function loadRecentBookings() {
    try {
        const bookings = await api.getBookingHistory();
        const recent = bookings.slice(0, 5);
        
        const tbody = document.getElementById('recentBookingsTable');
        
        if (recent.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No bookings yet</p>
                        <a href="vehicles.html" class="btn btn-primary btn-sm">Browse Vehicles</a>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = recent.map(booking => `
            <tr>
                <td>#${booking.id}</td>
                <td>${booking.vehicle?.name || 'N/A'}</td>
                <td>${formatDate(booking.start_date)} - ${formatDate(booking.end_date)}</td>
                <td>${formatCurrency(booking.total_amount)}</td>
                <td><span class="booking-status ${getStatusBadgeClass(booking.status)}">${booking.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="window.location.href='booking-history.html'">View</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load recent bookings:', error);
        showErrorState('recentBookingsTable', 'Failed to load bookings');
    }
}

async function loadAvailableVehicles() {
    try {
        const response = await api.getVehicles({ limit: 4 });
        const vehicles = response.items || response;
        
        const container = document.getElementById('availableVehicles');
        
        if (vehicles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-car"></i>
                    <p>No vehicles available</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = vehicles.map(vehicle => createVehicleCard(vehicle)).join('');
    } catch (error) {
        console.error('Failed to load vehicles:', error);
        showErrorState('availableVehicles', 'Failed to load vehicles');
    }
}
