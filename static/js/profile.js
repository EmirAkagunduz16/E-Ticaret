document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login?redirect=/profile';
        return;
    }
    
    // Load profile data
    loadProfileData();
    
    // Load orders
    loadOrders();
    
    // Add event listeners
    document.getElementById('edit-profile-btn').addEventListener('click', function() {
        showEditProfileModal();
    });
    
    document.getElementById('save-profile-btn').addEventListener('click', function() {
        updateProfile();
    });
});

// Function to load profile data
function loadProfileData() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!token || token === 'undefined') {
        window.location.href = '/login?redirect=/profile';
        return;
    }
    
    if (user) {
        // Show profile data from localStorage (quick display before API call)
        displayProfileData(user);
    }
    
    // Get updated profile data from API
    axios.get('/api/profile', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        const userData = response.data.user;
        
        // Update localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Display profile data
        displayProfileData(userData);
    })
    .catch(function(error) {
        console.error('Error loading profile data:', error);
        
        // Handle expired token or authentication errors
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            alert('Your session has expired. Please log in again.');
            window.location.href = '/login?redirect=/profile';
            return;
        }
        
        // If API call fails, at least show data from localStorage
        if (user) {
            displayProfileData(user);
        } else {
            // Show error message
            document.getElementById('profile-loading').classList.add('d-none');
            
            const errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger';
            errorAlert.textContent = 'Error loading profile data. Please try again later.';
            
            document.querySelector('.card-body').appendChild(errorAlert);
        }
    });
}

// Function to display profile data
function displayProfileData(user) {
    // Hide loading spinner
    document.getElementById('profile-loading').classList.add('d-none');
    
    // Show profile content
    document.getElementById('profile-content').classList.remove('d-none');
    
    // Format the name correctly from first_name and last_name
    let fullName = "";
    if (user.name) {
        fullName = user.name;
    } else if (user.first_name) {
        fullName = user.first_name;
        if (user.last_name) {
            fullName += " " + user.last_name;
        }
    }
    
    // Set profile data
    document.getElementById('profile-name').textContent = fullName;
    document.getElementById('profile-email').textContent = user.email;
    
    // Handle account_type display with fallback
    let accountType = "Customer";
    if (user.account_type) {
        accountType = user.account_type.charAt(0).toUpperCase() + user.account_type.slice(1);
    } else if (user.role) {
        accountType = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    }
    document.getElementById('profile-type').textContent = accountType;
    
    // Format joined date
    let joinedDate;
    if (user.created_at) {
        joinedDate = new Date(user.created_at);
        document.getElementById('profile-joined').textContent = joinedDate.toLocaleDateString();
    } else {
        document.getElementById('profile-joined').textContent = "N/A";
    }
}

// Function to show edit profile modal
function showEditProfileModal() {
    const user = JSON.parse(localStorage.getItem('user'));
    
    // Set current profile data in the form
    let fullName = "";
    if (user.name) {
        fullName = user.name;
    } else if (user.first_name) {
        fullName = user.first_name;
        if (user.last_name) {
            fullName += " " + user.last_name;
        }
    }
    
    document.getElementById('edit-name').value = fullName;
    document.getElementById('edit-email').value = user.email;
    
    // Clear password fields
    document.getElementById('edit-password').value = '';
    document.getElementById('edit-confirm-password').value = '';
    
    // Hide error message
    hideError('edit-profile-error');
    
    // Show modal
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    editProfileModal.show();
}

// Function to update profile
function updateProfile() {
    const token = localStorage.getItem('token');
    
    // Get form data
    const name = document.getElementById('edit-name').value;
    const password = document.getElementById('edit-password').value;
    const confirmPassword = document.getElementById('edit-confirm-password').value;
    
    // Validate form
    if (!name) {
        showError('edit-profile-error', 'Please enter your name.');
        return;
    }
    
    if (password && password !== confirmPassword) {
        showError('edit-profile-error', 'Passwords do not match.');
        return;
    }
    
    // Hide error message
    hideError('edit-profile-error');
    
    // Prepare data for API - Fixed field names to match backend expectations
    const data = {
        first_name: name.split(' ')[0],
        last_name: name.includes(' ') ? name.substring(name.indexOf(' ') + 1) : ''
    };
    
    if (password) {
        data.password = password;
    }
    
    // Show loading indicator
    const saveButton = document.getElementById('save-profile-btn');
    const originalText = saveButton.textContent;
    saveButton.disabled = true;
    saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    console.log('Sending profile update data:', data);
    
    // Send update request to API
    axios.put('/api/profile', data, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        console.log('Profile update response:', response.data);
        // Update localStorage
        const user = JSON.parse(localStorage.getItem('user'));
        user.first_name = data.first_name;
        user.last_name = data.last_name;
        user.name = name;
        localStorage.setItem('user', JSON.stringify(user));
        
        // Update profile display
        document.getElementById('profile-name').textContent = name;
        
        // Close modal
        const editProfileModal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
        editProfileModal.hide();
        
        // Show success message
        alert('Profile updated successfully.');
    })
    .catch(function(error) {
        console.error('Error updating profile:', error);
        
        let errorMessage = 'Failed to update profile. Please try again.';
        
        if (error.response && error.response.data && error.response.data.message) {
            errorMessage = error.response.data.message;
        }
        
        showError('edit-profile-error', errorMessage);
        
        // Reset button
        saveButton.disabled = false;
        saveButton.textContent = originalText;
    });
}

// Function to load orders
function loadOrders() {
    const token = localStorage.getItem('token');
    
    axios.get('/api/orders', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        // Hide loading spinner
        document.getElementById('orders-loading').classList.add('d-none');
        
        const orders = response.data.orders;
        
        if (orders.length === 0) {
            // Show empty orders message
            document.getElementById('orders-empty').classList.remove('d-none');
            return;
        }
        
        // Show orders content
        document.getElementById('orders-content').classList.remove('d-none');
        
        // Display orders
        displayOrders(orders);
    })
    .catch(function(error) {
        console.error('Error loading orders:', error);
        
        // Hide loading spinner
        document.getElementById('orders-loading').classList.add('d-none');
        
        // Show error message
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = 'Error loading orders. Please try again later.';
        
        document.querySelector('.card-body:nth-child(2)').appendChild(errorAlert);
    });
}

// Function to display orders
function displayOrders(orders) {
    const ordersTableBody = document.getElementById('orders-table-body');
    ordersTableBody.innerHTML = '';
    
    orders.forEach(function(order) {
        const row = document.createElement('tr');
        
        // Format date
        const orderDate = new Date(order.created_at);
        const formattedDate = orderDate.toLocaleDateString();
        
        // Create status badge
        let statusBadgeClass = 'bg-secondary';
        
        switch (order.status.toLowerCase()) {
            case 'pending':
                statusBadgeClass = 'bg-warning text-dark';
                break;
            case 'processing':
                statusBadgeClass = 'bg-info text-dark';
                break;
            case 'shipped':
                statusBadgeClass = 'bg-primary';
                break;
            case 'delivered':
                statusBadgeClass = 'bg-success';
                break;
            case 'cancelled':
                statusBadgeClass = 'bg-danger';
                break;
        }
        
        row.innerHTML = `
            <td>${order._id}</td>
            <td>${formattedDate}</td>
            <td>${order.items.length}</td>
            <td>${formatPrice(order.total_amount)}</td>
            <td><span class="badge ${statusBadgeClass}">${order.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-order-btn" data-id="${order._id}">
                    View Details
                </button>
            </td>
        `;
        
        // Add event listener for view order button
        row.querySelector('.view-order-btn').addEventListener('click', function() {
            showOrderDetails(order._id);
        });
        
        ordersTableBody.appendChild(row);
    });
}

// Function to show order details
function showOrderDetails(orderId) {
    const token = localStorage.getItem('token');
    
    // Show loading spinner
    document.getElementById('order-details-loading').classList.remove('d-none');
    document.getElementById('order-details-content').classList.add('d-none');
    
    // Show modal
    const orderDetailsModal = new bootstrap.Modal(document.getElementById('orderDetailsModal'));
    orderDetailsModal.show();
    
    // Fetch order details
    axios.get(`/api/orders/${orderId}`, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        const order = response.data.order;
        
        // Hide loading spinner
        document.getElementById('order-details-loading').classList.add('d-none');
        
        // Show order details
        document.getElementById('order-details-content').classList.remove('d-none');
        
        // Set order information
        document.getElementById('order-id').textContent = order._id;
        document.getElementById('order-status').textContent = order.status;
        document.getElementById('order-total').textContent = formatPrice(order.total_amount);
        document.getElementById('order-address').textContent = order.shipping_address;
        
        // Format date
        const orderDate = new Date(order.created_at);
        document.getElementById('order-date').textContent = orderDate.toLocaleString();
        
        // Display order items
        const orderItemsBody = document.getElementById('order-items-body');
        orderItemsBody.innerHTML = '';
        
        order.items.forEach(function(item) {
            const itemSubtotal = item.price * item.quantity;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.product_name}</td>
                <td>${formatPrice(item.price)}</td>
                <td>${item.quantity}</td>
                <td>${formatPrice(itemSubtotal)}</td>
            `;
            
            orderItemsBody.appendChild(row);
        });
    })
    .catch(function(error) {
        console.error('Error loading order details:', error);
        
        // Hide loading spinner
        document.getElementById('order-details-loading').classList.add('d-none');
        
        // Show error message
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = 'Error loading order details. Please try again later.';
        
        document.getElementById('order-details-content').innerHTML = '';
        document.getElementById('order-details-content').appendChild(errorAlert);
        document.getElementById('order-details-content').classList.remove('d-none');
    });
}

// Function to show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.classList.remove('d-none');
}

// Function to hide error message
function hideError(elementId) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = '';
    errorElement.classList.add('d-none');
} 