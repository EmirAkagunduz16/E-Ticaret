document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/';
        return;
    }
    
    // Add event listener for register form submit
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        register();
    });
});

// Function to handle registration
function register() {
    // Get form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const accountType = document.querySelector('input[name="account-type"]:checked').value;
    
    // Validate form
    if (!name || !email || !password || !confirmPassword) {
        showError('register-error', 'Please fill in all fields.');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('register-error', 'Passwords do not match.');
        return;
    }
    
    if (password.length < 8) {
        showError('register-error', 'Password must be at least 8 characters long.');
        return;
    }
    
    // Hide error message
    hideError('register-error');
    
    // Show loading indicator
    const submitButton = document.querySelector('#register-form button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';
    
    // Send registration request
    axios.post('/api/auth/register', {
        name: name,
        email: email,
        password: password,
        account_type: accountType
    })
    .then(function(response) {
        // Store token and user info
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect to home page
        window.location.href = '/';
    })
    .catch(function(error) {
        console.error('Registration error:', error);
        
        let errorMessage = 'Failed to register. Please try again.';
        
        if (error.response) {
            switch (error.response.status) {
                case 409:
                    errorMessage = 'Email already in use. Please use a different email.';
                    break;
                default:
                    errorMessage = error.response.data.message || errorMessage;
            }
        }
        
        showError('register-error', errorMessage);
        
        // Reset button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
} 