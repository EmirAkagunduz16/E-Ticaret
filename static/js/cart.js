document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login?redirect=/cart';
        return;
    }
    
    // Load cart items
    loadCartData();
    
    // Add event listener for checkout button
    document.getElementById('checkout-btn').addEventListener('click', function() {
        showCheckoutModal();
    });
    
    // Add event listener for place order button
    document.getElementById('place-order-btn').addEventListener('click', function() {
        placeOrder();
    });
});

// Function to load cart data
function loadCartData() {
    const token = localStorage.getItem('token');
    
    if (!token || token === 'undefined') {
        // Redirect to login if not logged in
        window.location.href = '/login?redirect=/cart';
        return;
    }
    
    // Show loading indicator
    document.getElementById('cart-loading').classList.remove('d-none');
    document.getElementById('cart-empty').classList.add('d-none');
    document.getElementById('cart-content').classList.add('d-none');
    
    // Get cart data from API
    axios.get('/api/cart', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        // Hide loading indicator
        document.getElementById('cart-loading').classList.add('d-none');
        
        const cartItems = response.data.cart_items;
        
        if (cartItems && cartItems.length > 0) {
            // Show cart content
            document.getElementById('cart-content').classList.remove('d-none');
            
            // Display cart items
            displayCartItems(cartItems);
        } else {
            // Show empty cart message
            document.getElementById('cart-empty').classList.remove('d-none');
        }
    })
    .catch(function(error) {
        console.error('Error loading cart data:', error);
        
        // Handle expired token or authentication errors
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            alert('Your session has expired. Please log in again.');
            window.location.href = '/login?redirect=/cart';
            return;
        }
        
        // Hide loading indicator and show error message
        document.getElementById('cart-loading').classList.add('d-none');
        
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = 'Error loading cart data. Please try again later.';
        
        document.getElementById('cart-container').prepend(errorAlert);
    });
}

// Function to update cart item quantity
function updateCartItemQuantity(itemId, quantity) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        // Redirect to login if not logged in
        window.location.href = '/login?redirect=/cart';
        return;
    }
    
    // Update cart item quantity in API
    axios.put('/api/cart/update', {
        item_id: itemId,
        quantity: quantity
    }, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        // Reload cart data
        loadCartData();
        
        // Update cart count
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error updating cart item quantity:', error);
        
        // Handle expired token or authentication errors
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            alert('Your session has expired. Please log in again.');
            window.location.href = '/login?redirect=/cart';
            return;
        }
        
        alert('Failed to update cart item quantity. Please try again.');
    });
}

// Function to remove item from cart
function removeCartItem(itemId) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        // Redirect to login if not logged in
        window.location.href = '/login?redirect=/cart';
        return;
    }
    
    // Remove cart item in API
    axios.delete('/api/cart/remove', {
        headers: {
            'Authorization': 'Bearer ' + token
        },
        data: {
            item_id: itemId
        }
    })
    .then(function(response) {
        // Reload cart data
        loadCartData();
        
        // Update cart count
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error removing cart item:', error);
        
        // Handle expired token or authentication errors
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            alert('Your session has expired. Please log in again.');
            window.location.href = '/login?redirect=/cart';
            return;
        }
        
        alert('Failed to remove cart item. Please try again.');
    });
}

// Function to show checkout modal
function showCheckoutModal() {
    const checkoutModal = new bootstrap.Modal(document.getElementById('checkoutModal'));
    checkoutModal.show();
}

// Function to place order
function placeOrder() {
    const token = localStorage.getItem('token');
    
    // Get shipping address from form
    const fullName = document.getElementById('full-name').value;
    const address = document.getElementById('address').value;
    const city = document.getElementById('city').value;
    const zip = document.getElementById('zip').value;
    const country = document.getElementById('country').value;
    
    // Validate form
    if (!fullName || !address || !city || !zip || !country) {
        alert('Please fill in all shipping information fields.');
        return;
    }
    
    // Get payment information (in a real app, we would process payment)
    const cardName = document.getElementById('card-name').value;
    const cardNumber = document.getElementById('card-number').value;
    const expiryDate = document.getElementById('expiry-date').value;
    const cvv = document.getElementById('cvv').value;
    
    // Validate payment form
    if (!cardName || !cardNumber || !expiryDate || !cvv) {
        alert('Please fill in all payment information fields.');
        return;
    }
    
    // Create shipping address string
    const shippingAddress = `${fullName}, ${address}, ${city}, ${zip}, ${country}`;
    
    // Place order
    axios.post('/api/orders', {
        shipping_address: shippingAddress
    }, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        alert('Order placed successfully!');
        
        // Close modal
        const checkoutModal = bootstrap.Modal.getInstance(document.getElementById('checkoutModal'));
        checkoutModal.hide();
        
        // Redirect to orders page or home page
        window.location.href = '/';
    })
    .catch(function(error) {
        console.error('Error placing order:', error);
        alert('Failed to place order. Please try again.');
    });
} 