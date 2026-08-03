// Booking History page functionality

let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadBookings();
});

async function loadBookings() {
    try {
        showLoading('bookingsTableBody');
        
        let bookings;
        if (currentFilter === 'all') {
            bookings = await api.getBookingHistory();
        } else {
            bookings = await api.getMyBookings(currentFilter);
        }
        
        const tbody = document.getElementById('bookingsTableBody');
        
        if (!bookings || bookings.length === 0) {
            showEmpty('bookingsTableBody', 'No bookings found');
            return;
        }
        
        tbody.innerHTML = bookings.map(booking => createBookingRow(booking)).join('');
    } catch (error) {
        console.error('Failed to load bookings:', error);
        showErrorState('bookingsTableBody', 'Failed to load bookings. Please try again.');
    }
}

function filterBookings(status) {
    currentFilter = status;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadBookings();
}

function createBookingRow(booking) {
    const startDate = new Date(booking.start_date);
    const endDate = new Date(booking.end_date);
    const duration = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
    
    return `
        <tr>
            <td>#${booking.id}</td>
            <td>${booking.vehicle?.name || 'N/A'}</td>
            <td>${formatDate(booking.start_date)} - ${formatDate(booking.end_date)}</td>
            <td>${duration} day${duration > 1 ? 's' : ''}</td>
            <td>${formatCurrency(booking.total_amount)}</td>
            <td><span class="booking-status ${getStatusBadgeClass(booking.status)}">${booking.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewBooking('${booking.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                ${(booking.status === 'confirmed' || booking.status === 'pending') ? `
                    <button class="btn btn-sm btn-outline-danger" onclick="cancelBooking('${booking.id}')">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                ` : ''}
            </td>
        </tr>
    `;
}

async function viewBooking(bookingId) {
    try {
        const booking = await api.getBooking(bookingId);
        
        const modalContent = document.getElementById('modalContent');
        const driverInfo = booking.driver ? `
            <div class="info-row">
                <strong>Driver:</strong>
                <span>${booking.driver.name}</span>
            </div>
            <div class="info-row">
                <strong>Driver Phone:</strong>
                <span>${booking.driver.phone}</span>
            </div>
        ` : '<p class="text-muted">No driver assigned yet</p>';
        
        modalContent.innerHTML = `
            <div class="booking-details">
                <div class="detail-section">
                    <h3>Booking Information</h3>
                    <div class="info-grid">
                        <div class="info-row">
                            <strong>Booking ID:</strong>
                            <span>#${booking.id}</span>
                        </div>
                        <div class="info-row">
                            <strong>Status:</strong>
                            <span class="booking-status ${getStatusBadgeClass(booking.status)}">${booking.status}</span>
                        </div>
                        <div class="info-row">
                            <strong>Vehicle:</strong>
                            <span>${booking.vehicle?.name || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <strong>Pick-up Date:</strong>
                            <span>${formatDate(booking.start_date)}</span>
                        </div>
                        <div class="info-row">
                            <strong>Return Date:</strong>
                            <span>${formatDate(booking.end_date)}</span>
                        </div>
                        <div class="info-row">
                            <strong>Total Amount:</strong>
                            <span>${formatCurrency(booking.total_amount)}</span>
                        </div>
                        <div class="info-row">
                            <strong>Payment Status:</strong>
                            <span class="booking-status ${getStatusBadgeClass(booking.payment_status)}">${booking.payment_status || 'Pending'}</span>
                        </div>
                    </div>
                </div>
                
                ${driverInfo ? `
                <div class="detail-section">
                    <h3>Driver Information</h3>
                    ${driverInfo}
                </div>
                ` : ''}
                
                ${booking.cancellation_reason ? `
                <div class="detail-section">
                    <h3>Cancellation Details</h3>
                    <div class="info-row">
                        <strong>Reason:</strong>
                        <span>${booking.cancellation_reason}</span>
                    </div>
                    <div class="info-row">
                        <strong>Cancelled At:</strong>
                        <span>${formatDateTime(bookings.cancelled_at)}</span>
                    </div>
                    ${booking.refund_status ? `
                    <div class="info-row">
                        <strong>Refund Status:</strong>
                        <span class="booking-status ${getStatusBadgeClass(booking.refund_status)}">${booking.refund_status}</span>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
                
                <div class="modal-actions">
                    ${booking.status === 'confirmed' && booking.payment_status !== 'completed' ? `
                        <button class="btn btn-primary" onclick="payForBooking('${booking.id}')">
                            <i class="fas fa-credit-card"></i> Pay Now
                        </button>
                    ` : ''}
                    ${(booking.status === 'confirmed' || booking.status === 'pending') ? `
                        <button class="btn btn-danger" onclick="cancelBooking('${booking.id}')">
                            <i class="fas fa-times"></i> Cancel Booking
                        </button>
                    ` : ''}
                    <button class="btn btn-outline" onclick="closeModal()">Close</button>
                </div>
            </div>
        `;
        
        document.getElementById('bookingModal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load booking details:', error);
        showToast('Failed to load booking details', 'error');
    }
}

async function cancelBooking(bookingId) {
    if (!confirmAction('Are you sure you want to cancel this booking? Refund will be processed as per cancellation policy.')) {
        return;
    }
    
    try {
        const reason = prompt('Please provide a reason for cancellation (optional):');
        
        await api.cancelBooking(bookingId, reason || '');
        
        showToast('Booking cancelled successfully. Refund will be processed.', 'success');
        closeModal();
        loadBookings();
    } catch (error) {
        console.error('Failed to cancel booking:', error);
        showToast(error.message || 'Failed to cancel booking', 'error');
    }
}

async function payForBooking(bookingId) {
    try {
        const order = await api.createPaymentOrder(bookingId);
        
        // Initialize Razorpay
        const options = {
            key: order.razorpay_key_id,
            amount: order.amount,
            currency: order.currency,
            name: 'Smart Vehicle Rental',
            description: `Booking #${bookingId}`,
            order_id: order.id,
            handler: async function(response) {
                try {
                    await api.verifyPayment({
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_signature: response.razorpay_signature,
                        booking_id: bookingId
                    });
                    
                    showToast('Payment successful!', 'success');
                    closeModal();
                    loadBookings();
                } catch (error) {
                    showToast('Payment verification failed', 'error');
                }
            },
            prefill: {
                name: getUser()?.full_name,
                email: getUser()?.email,
                contact: getUser()?.phone
            },
            theme: {
                color: '#FF7A00'
            }
        };
        
        const rzp = new Razorpay(options);
        rzp.open();
    } catch (error) {
        console.error('Failed to create payment order:', error);
        showToast(error.message || 'Failed to initiate payment', 'error');
    }
}

function closeModal() {
    document.getElementById('bookingModal').style.display = 'none';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('bookingModal');
    if (event.target === modal) {
        closeModal();
    }
};
