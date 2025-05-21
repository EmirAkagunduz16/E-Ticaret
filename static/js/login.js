document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        // Redirect to home page or to the page they were trying to access
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect') || '/';
        window.location.href = redirectUrl;
        return;
    }
    
    // Add event listener for login form submit
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        login();
    });
    
    // Add event listener for forgot password link
    document.getElementById('forgot-password-link').addEventListener('click', function(e) {
        e.preventDefault();
        showForgotPasswordModal();
    });
    
    // Add event listener for send reset link button
    document.getElementById('send-reset-link-btn').addEventListener('click', function() {
        sendPasswordResetLink();
    });
});

// Function to handle login
function login() {
    // Get form data
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Validate form
    if (!email || !password) {
        showError('login-error', 'Please enter both email and password.');
        return;
    }
    
    // Hide error message
    hideError('login-error');
    
    // Show loading indicator
    const submitButton = document.querySelector('#login-form button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
    
    // Send login request
    axios.post('/api/auth/login', {
        email: email,
        password: password
    })
    .then(function(response) {
        console.log('Login response:', response.data);
        
        // Store token and user info - use the correct property name from response
        const token = response.data.access_token || response.data.token;
        localStorage.setItem('token', token);
        
        // Store user role and other info
        const userInfo = {
            role: response.data.role || (response.data.user && response.data.user.role) || 'customer',
            id: response.data.user && response.data.user.id
        };
        localStorage.setItem('user', JSON.stringify(userInfo));
        
        // Redirect to home page or to the page they were trying to access
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect') || '/';
        window.location.href = redirectUrl;
    })
    .catch(function(error) {
        console.error('Login error:', error);
        
        let errorMessage = 'Failed to log in. Please try again.';
        
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    errorMessage = 'Invalid email or password.';
                    break;
                case 404:
                    errorMessage = 'User not found.';
                    break;
                default:
                    errorMessage = error.response.data.message || errorMessage;
            }
        }
        
        showError('login-error', errorMessage);
        
        // Reset button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

// Function to show the forgot password modal
function showForgotPasswordModal() {
    // Clear any previous input and messages
    document.getElementById('forgot-email').value = '';
    hideError('forgot-password-error');
    hideError('forgot-password-success');
    
    // Show the modal
    const forgotPasswordModal = new bootstrap.Modal(document.getElementById('forgotPasswordModal'));
    forgotPasswordModal.show();
}

// Function to send password reset link
function sendPasswordResetLink() {
    const email = document.getElementById('forgot-email').value;
    
    // Validate email
    if (!email) {
        showError('forgot-password-error', 'Lütfen email adresinizi girin.');
        return;
    }
    
    // Hide error message and show loading indicator
    hideError('forgot-password-error');
    hideError('forgot-password-success');
    
    const submitButton = document.getElementById('send-reset-link-btn');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Gönderiliyor...';
    
    // Send forgot password request
    axios.post('/api/auth/forgot-password', {
        email: email
    })
    .then(function(response) {
        // Show success message
        document.getElementById('forgot-password-success').textContent = 'Şifre sıfırlama bağlantısı email adresinize gönderildi.';
        document.getElementById('forgot-password-success').classList.remove('d-none');
        
        // Reset button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        
        // Auto close modal after 3 seconds
        setTimeout(function() {
            const forgotPasswordModal = bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal'));
            forgotPasswordModal.hide();
        }, 3000);
    })
    .catch(function(error) {
        console.error('Forgot password error:', error);
        
        let errorMessage = 'Şifre sıfırlama bağlantısı gönderilemedi. Lütfen tekrar deneyin.';
        
        if (error.response) {
            switch (error.response.status) {
                case 404:
                    errorMessage = 'Bu email adresi sistemde kayıtlı değil.';
                    break;
                default:
                    errorMessage = error.response.data.message || errorMessage;
            }
        }
        
        showError('forgot-password-error', errorMessage);
        
        // Reset button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
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
    errorElement.classList.add('d-none');
} 