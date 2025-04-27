document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login?redirect=/cart';
        return;
    }
    
    // Load cart items
    loadCartItems();
    
    // Add event listener for checkout button
    document.getElementById('checkout-btn').addEventListener('click', function() {
        showCheckoutModal();
    });
    
    // Add event listener for place order button
    document.getElementById('place-order-btn').addEventListener('click', function() {
        placeOrder();
    });
});

// Function to load cart items
function loadCartItems() {
    const token = localStorage.getItem('token');
    const cartLoading = document.getElementById('cart-loading');
    const cartEmpty = document.getElementById('cart-empty');
    const cartItems = document.getElementById('cart-items');
    
    axios.get('/api/cart', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        // Hide loading spinner
        cartLoading.classList.add('d-none');
        
        const items = response.data.items;
        
        if (items.length === 0) {
            // Show empty cart message
            cartEmpty.classList.remove('d-none');
            return;
        }
        
        // Show cart items
        cartItems.classList.remove('d-none');
        
        // Clear cart items body
        const cartItemsBody = document.getElementById('cart-items-body');
        cartItemsBody.innerHTML = '';
        
        // Calculate total
        let subtotal = 0;
        
        // Add cart items to table
        items.forEach(function(item) {
            const row = document.createElement('tr');
            
            const itemSubtotal = item.price * item.quantity;
            subtotal += itemSubtotal;
            
            row.innerHTML = `
                <td>${item.product_name}</td>
                <td>${formatPrice(item.price)}</td>
                <td>
                    <div class="input-group input-group-sm" style="max-width: 120px;">
                        <button class="btn btn-outline-secondary btn-decrease" data-id="${item._id}">-</button>
                        <input type="number" class="form-control text-center" value="${item.quantity}" min="1" readonly>
                        <button class="btn btn-outline-secondary btn-increase" data-id="${item._id}">+</button>
                    </div>
                </td>
                <td>${formatPrice(itemSubtotal)}</td>
                <td>
                    <button class="btn btn-sm btn-danger btn-remove" data-id="${item._id}">
                        <i class="bi bi-trash"></i> Remove
                    </button>
                </td>
            `;
            
            // Add event listeners for quantity changes
            const decreaseBtn = row.querySelector('.btn-decrease');
            const increaseBtn = row.querySelector('.btn-increase');
            const removeBtn = row.querySelector('.btn-remove');
            
            decreaseBtn.addEventListener('click', function() {
                updateCartItemQuantity(item._id, item.quantity - 1);
            });
            
            increaseBtn.addEventListener('click', function() {
                updateCartItemQuantity(item._id, item.quantity + 1);
            });
            
            removeBtn.addEventListener('click', function() {
                removeCartItem(item._id);
            });
            
            cartItemsBody.appendChild(row);
        });
        
        // Calculate and display totals
        const shipping = subtotal > 0 ? 5.00 : 0;
        const total = subtotal + shipping;
        
        document.getElementById('cart-subtotal').textContent = formatPrice(subtotal);
        document.getElementById('cart-shipping').textContent = formatPrice(shipping);
        document.getElementById('cart-total').textContent = formatPrice(total);
    })
    .catch(function(error) {
        console.error('Error loading cart items:', error);
        cartLoading.classList.add('d-none');
        
        // Show error message
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = 'Error loading cart items. Please try again later.';
        
        document.getElementById('cart-container').appendChild(errorAlert);
    });
}

// Function to update cart item quantity
function updateCartItemQuantity(itemId, quantity) {
    if (quantity < 1) {
        return;
    }
    
    const token = localStorage.getItem('token');
    
    axios.put(`/api/cart/update/${itemId}`, {
        quantity: quantity
    }, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        loadCartItems();
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error updating cart item:', error);
        alert('Failed to update cart item. Please try again.');
    });
}

// Function to remove cart item
function removeCartItem(itemId) {
    const token = localStorage.getItem('token');
    
    axios.delete(`/api/cart/remove/${itemId}`, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        loadCartItems();
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error removing cart item:', error);
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