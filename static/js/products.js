document.addEventListener('DOMContentLoaded', function() {
    // Fetch products on page load
    fetchProducts();
    
    // Add event listeners
    document.getElementById('search-btn').addEventListener('click', function() {
        const searchQuery = document.getElementById('search-input').value;
        fetchProducts(searchQuery);
    });
    
    document.getElementById('apply-filters').addEventListener('click', function() {
        applyFilters();
    });
    
    document.getElementById('reset-filters').addEventListener('click', function() {
        resetFilters();
    });
    
    // Search on Enter key press
    document.getElementById('search-input').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            const searchQuery = document.getElementById('search-input').value;
            fetchProducts(searchQuery);
        }
    });
});

// Function to fetch products
function fetchProducts(searchQuery = '', page = 1) {
    const productsContainer = document.getElementById('products-container');
    const paginationContainer = document.getElementById('pagination-container');
    
    // Show loading spinner
    productsContainer.innerHTML = `
        <div class="col-12 text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Build query parameters
    let queryParams = `?page=${page}`;
    
    if (searchQuery) {
        queryParams += `&search=${encodeURIComponent(searchQuery)}`;
    }
    
    // Add price filters if applied
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    
    if (minPrice) {
        queryParams += `&min_price=${minPrice}`;
    }
    
    if (maxPrice) {
        queryParams += `&max_price=${maxPrice}`;
    }
    
    // Fetch products from API
    axios.get(`/api/products${queryParams}`)
        .then(function(response) {
            const products = response.data.products;
            const totalProducts = response.data.total;
            const totalPages = response.data.total_pages;
            
            // Clear products container
            productsContainer.innerHTML = '';
            
            if (products.length === 0) {
                productsContainer.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-info">
                            No products found. Try different search criteria.
                        </div>
                    </div>
                `;
                return;
            }
            
            // Add product cards
            products.forEach(function(product) {
                const productCard = createProductCard(product);
                productsContainer.appendChild(productCard);
            });
            
            // Create pagination
            createPagination(page, totalPages);
        })
        .catch(function(error) {
            console.error('Error fetching products:', error);
            productsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        Error loading products. Please try again later.
                    </div>
                </div>
            `;
        });
}

// Function to create pagination
function createPagination(currentPage, totalPages) {
    const paginationContainer = document.getElementById('pagination-container');
    
    // Clear pagination container
    paginationContainer.innerHTML = '';
    
    if (totalPages <= 1) {
        return;
    }
    
    // Create pagination element
    const ul = document.createElement('ul');
    ul.className = 'pagination';
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    
    const prevLink = document.createElement('a');
    prevLink.className = 'page-link';
    prevLink.href = '#';
    prevLink.innerHTML = '&laquo;';
    
    if (currentPage > 1) {
        prevLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetchProducts(document.getElementById('search-input').value, currentPage - 1);
        });
    }
    
    prevLi.appendChild(prevLink);
    ul.appendChild(prevLi);
    
    // Page buttons
    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        
        const link = document.createElement('a');
        link.className = 'page-link';
        link.href = '#';
        link.textContent = i;
        
        link.addEventListener('click', function(e) {
            e.preventDefault();
            fetchProducts(document.getElementById('search-input').value, i);
        });
        
        li.appendChild(link);
        ul.appendChild(li);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    
    const nextLink = document.createElement('a');
    nextLink.className = 'page-link';
    nextLink.href = '#';
    nextLink.innerHTML = '&raquo;';
    
    if (currentPage < totalPages) {
        nextLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetchProducts(document.getElementById('search-input').value, currentPage + 1);
        });
    }
    
    nextLi.appendChild(nextLink);
    ul.appendChild(nextLi);
    
    // Add pagination to container
    paginationContainer.appendChild(ul);
}

// Function to apply filters
function applyFilters() {
    fetchProducts(document.getElementById('search-input').value);
}

// Function to reset filters
function resetFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('min-price').value = '';
    document.getElementById('max-price').value = '';
    fetchProducts();
}

// Function to create a product card
function createProductCard(product) {
    const col = document.createElement('div');
    col.className = 'col-md-4 col-sm-6 mb-4';
    
    col.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text">${product.description}</p>
                <p class="card-text text-primary fw-bold">${formatPrice(product.price)}</p>
                <p class="card-text"><small class="text-muted">In stock: ${product.stock}</small></p>
                <button class="btn btn-primary btn-add-to-cart" data-id="${product._id}" data-price="${product.price}">
                    Add to Cart
                </button>
            </div>
        </div>
    `;
    
    // Add event listener for Add to Cart button
    const addToCartBtn = col.querySelector('.btn-add-to-cart');
    addToCartBtn.addEventListener('click', function() {
        addToCart(product._id, product.price);
    });
    
    return col;
}

// Function to format price
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

// Function to add product to cart
function addToCart(productId, price) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = '/login?redirect=/products';
        return;
    }
    
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
        alert('Product added to cart!');
        // Update cart count
        fetchCartCount();
    })
    .catch(function(error) {
        console.error('Error adding to cart:', error);
        alert('Failed to add product to cart. Please try again.');
    });
}

// Function to update cart count in header
function fetchCartCount() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    axios.get('/api/cart/count', {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
    .then(function(response) {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            const count = response.data.count;
            cartCount.textContent = count;
            
            if (count > 0) {
                cartCount.classList.remove('d-none');
            } else {
                cartCount.classList.add('d-none');
            }
        }
    })
    .catch(function(error) {
        console.error('Error fetching cart count:', error);
    });
} 