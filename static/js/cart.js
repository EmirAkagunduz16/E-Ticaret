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
    document.getElementById('cart-items').classList.add('d-none');
    
    // Get cart data from API
    axios.get('/api/cart', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        // Hide loading indicator
        document.getElementById('cart-loading').classList.add('d-none');
        
        // Fix: Get cart items from the correct property in the response
        const cartItems = response.data.items;
        
        // Debug: Log cart items to console
        console.log('Cart items received from server:', cartItems);
        
        if (cartItems && cartItems.length > 0) {
            // Show cart content
            document.getElementById('cart-items').classList.remove('d-none');
            
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

// Function to display cart items
function displayCartItems(cartItems) {
    const cartItemsBody = document.getElementById('cart-items-body');
    cartItemsBody.innerHTML = '';
    
    let subtotal = 0;
    
    cartItems.forEach(function(item) {
        const row = document.createElement('tr');
        
        // Calculate item subtotal
        const itemSubtotal = item.price * item.quantity;
        subtotal += itemSubtotal;
        
        // Get image URL with fallback
        const imageUrl = item.image_url || '/static/images/no-image.jpg';
        
        // Fix duplicated product names by checking if the name contains duplicated words
        let productName = item.product_name;
        const words = productName.split(' ');
        if (words.length > 1) {
            // Check if the first word is duplicated
            const firstWord = words[0];
            const isDuplicated = words.filter(word => word === firstWord).length > 1;
            if (isDuplicated) {
                // If duplicated, take only the first half of the name
                const halfLength = Math.floor(words.length / 2);
                productName = words.slice(0, halfLength).join(' ');
            }
        }
        
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <img src="${imageUrl}" alt="${productName}" class="img-thumbnail me-3" style="width: 50px;">
                    <div>
                        <h6 class="mb-0">${productName}</h6>
                        <small class="text-muted">${item.variant_info || ''}</small>
                    </div>
                </div>
            </td>
            <td>$${item.price.toFixed(2)}</td>
            <td>
                <div class="input-group input-group-sm" style="width: 100px;">
                    <button class="btn btn-outline-secondary decrease-qty" type="button" data-id="${item._id}">-</button>
                    <input type="text" class="form-control text-center" value="${item.quantity}" readonly>
                    <button class="btn btn-outline-secondary increase-qty" type="button" data-id="${item._id}">+</button>
                </div>
            </td>
            <td>$${itemSubtotal.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger remove-item" data-id="${item._id}">Remove</button>
            </td>
        `;
        
        cartItemsBody.appendChild(row);
        
        // Add event listeners for quantity buttons
        row.querySelector('.decrease-qty').addEventListener('click', function() {
            if (item.quantity > 1) {
                updateCartItemQuantity(item._id, item.quantity - 1);
            }
        });
        
        row.querySelector('.increase-qty').addEventListener('click', function() {
            updateCartItemQuantity(item._id, item.quantity + 1);
        });
        
        row.querySelector('.remove-item').addEventListener('click', function() {
            removeCartItem(item._id);
        });
    });
    
    // Update order summary
    const shipping = subtotal > 0 ? 10 : 0; // $10 shipping fee
    const total = subtotal + shipping;
    
    document.getElementById('cart-subtotal').textContent = '$' + subtotal.toFixed(2);
    document.getElementById('cart-shipping').textContent = '$' + shipping.toFixed(2);
    document.getElementById('cart-total').textContent = '$' + total.toFixed(2);
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
    axios.put(`/api/cart/update/${itemId}`, {
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
    axios.delete(`/api/cart/remove/${itemId}`, {
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
        shipping_address: shippingAddress,
        items: [] // This will be filled by the backend from the user's cart
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

// Function to fetch cart count
function fetchCartCount() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        return;
    }
    
    axios.get('/api/cart/count', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        const cartCount = response.data.count;
        
        // Update cart count in navbar
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = cartCount;
            
            // Show or hide the badge based on count
            if (cartCount > 0) {
                cartCountElement.classList.remove('d-none');
            } else {
                cartCountElement.classList.add('d-none');
            }
        }
    })
    .catch(function(error) {
        console.error('Error fetching cart count:', error);
    });
} 