document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status on page load
    checkAuthStatus();
    
    // Add logout event listener
    document.getElementById('logout-link').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
});

// Function to check if the user is authenticated
function checkAuthStatus() {
    const token = localStorage.getItem('token');
    
    if (token) {
        // User is logged in
        document.getElementById('login-item').classList.add('d-none');
        document.getElementById('register-item').classList.add('d-none');
        document.getElementById('profile-item').classList.remove('d-none');
        document.getElementById('logout-item').classList.remove('d-none');
        
        // Get cart count
        fetchCartCount();
    } else {
        // User is not logged in
        document.getElementById('login-item').classList.remove('d-none');
        document.getElementById('register-item').classList.remove('d-none');
        document.getElementById('profile-item').classList.add('d-none');
        document.getElementById('logout-item').classList.add('d-none');
    }
}

// Function to fetch cart count
function fetchCartCount() {
    const token = localStorage.getItem('token');
    
    // Make the request regardless of token - the backend will handle anonymous users
    axios.get('/api/cart/count', {
        headers: token && token !== 'undefined' ? {
            'Authorization': 'Bearer ' + token
        } : {}
    })
    .then(function(response) {
        const cartCount = response.data.count;
        document.getElementById('cart-count').textContent = cartCount;
    })
    .catch(function(error) {
        console.error('Error fetching cart count:', error);
        // Set cart count to 0 on error
        document.getElementById('cart-count').textContent = '0';
        
        // If token is invalid, clear it
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
        }
    });
}

// Function to handle logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Update UI to reflect logged out state
    checkAuthStatus();
    
    // Redirect to home page
    window.location.href = '/';
}

// Function to handle API requests with token refresh if needed
function apiRequest(method, url, data = null) {
    return new Promise((resolve, reject) => {
        const token = localStorage.getItem('token');
        
        if (!token) {
            reject(new Error('No authentication token available'));
            return;
        }
        
        const headers = {
            'Authorization': 'Bearer ' + token
        };
        
        const config = {
            method: method,
            url: url,
            headers: headers
        };
        
        if (data) {
            if (method.toLowerCase() === 'get') {
                config.params = data;
            } else {
                config.data = data;
            }
        }
        
        axios(config)
            .then(response => resolve(response))
            .catch(error => {
                // If token expired error, redirect to login
                if (error.response && error.response.status === 401) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                    reject(error);
                } else {
                    reject(error);
                }
            });
    });
}

// Function to format price
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
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

// Function to create a product card
function createProductCard(product) {
    const productCol = document.createElement('div');
    productCol.className = 'col-md-4 mb-4';
    
    productCol.innerHTML = `
        <div class="card product-card">
            <div class="card-body">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text">${product.description}</p>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="product-price">${formatPrice(product.price)}</span>
                    <button class="btn btn-outline-primary btn-add-to-cart" data-product-id="${product._id}">Add to Cart</button>
                </div>
            </div>
        </div>
    `;
    
    // Add event listener for the "Add to Cart" button
    const addToCartBtn = productCol.querySelector('.btn-add-to-cart');
    addToCartBtn.addEventListener('click', function() {
        addToCart(product._id, product.price);
    });
    
    return productCol;
}

// Function to add a product to the cart
function addToCart(productId, price) {
    const token = localStorage.getItem('token');
    
    if (!token || token === 'undefined') {
        alert('Please log in to add items to your cart.');
        window.location.href = '/login';
        return;
    }
    
    console.log(`Adding product to cart. ID: ${productId}, Price: ${price}`);
    
    axios.post('/api/cart/add', {
        product_id: productId,
        quantity: 1,
        price: price
    }, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        console.log('Product added successfully:', response.data);
        alert('Product added to cart!');
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error adding product to cart:', error);
        if (error.response && error.response.data) {
            console.error('Server response:', error.response.data);
            
            // If authentication error or token expired, redirect to login
            if (error.response.status === 401 || 
                (error.response.data.message && 
                 (error.response.data.message.includes('Authentication') || 
                  error.response.data.message.includes('Token süresi dolmuş') ||
                  error.response.data.error === 'Signature has expired'))) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                alert('Your session has expired. Please log in again.');
                window.location.href = '/login';
                return;
            }
            
            alert(`Failed to add product to cart: ${error.response.data.message || 'Unknown error'}`);
        } else {
            alert('Failed to add product to cart. Please try again.');
        }
    });
} 