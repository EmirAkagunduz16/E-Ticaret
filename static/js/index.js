document.addEventListener('DOMContentLoaded', function() {
    // Load featured products
    loadFeaturedProducts();
});

// Function to load featured products
function loadFeaturedProducts() {
    const featuredProductsContainer = document.getElementById('featured-products');
    
    axios.get('/api/products/featured')
        .then(function(response) {
            const products = response.data;
            
            // Clear featured products container
            featuredProductsContainer.innerHTML = '';
            
            if (products.length === 0) {
                featuredProductsContainer.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-info">
                            No featured products available at the moment.
                        </div>
                    </div>
                `;
                return;
            }
            
            // Add product cards
            products.forEach(function(product) {
                const productCard = createProductCard(product);
                featuredProductsContainer.appendChild(productCard);
            });
        })
        .catch(function(error) {
            console.error('Error fetching featured products:', error);
            featuredProductsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        Error loading featured products. Please try again later.
                    </div>
                </div>
            `;
        });
} 