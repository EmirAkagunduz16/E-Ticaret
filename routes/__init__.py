from .auth import auth_bp
from .profile import profile_bp
from .products import products_bp
from .cart import cart_bp
from .dev import dev_bp
from .orders import orders_bp

__all__ = ['auth_bp', 'profile_bp', 'products_bp', 'cart_bp', 'dev_bp', 'orders_bp'] 