from flask import Blueprint, render_template, jsonify
from config.settings import Config

dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/dev/preview-email/<template>')
def preview_email_template(template):
    """Örnek verilerle bir e-posta şablonunu önizle"""
    if template == 'cart_updated':
        # Örnek veriler sepet güncellendi e-postası için
        data = {
            'user_name': 'Test User',
            'cart_items': [
                {'product_name': 'Product 1', 'quantity': 2, 'price': 99.99},
                {'product_name': 'Product 2', 'quantity': 1, 'price': 149.99}
            ],
            'app_url': Config.APP_URL
        }
        return render_template('emails/cart_updated.html', **data)
    
    elif template == 'order_received':
        # Örnek veriler sipariş alındı e-postası için
        data = {
            'user_name': 'Test User',
            'order_id': '6065c1234567890123456789',
            'order_date': '01.01.2023 14:30',
            'payment_method': 'Kredi Kartı',
            'order_items': [
                {'product_name': 'Product 1', 'quantity': 2, 'price': 99.99, 'subtotal': 199.98},
                {'product_name': 'Product 2', 'quantity': 1, 'price': 149.99, 'subtotal': 149.99}
            ],
            'order_total': 349.97,
            'app_url': Config.APP_URL
        }
        return render_template('emails/order_received.html', **data)
    
    return jsonify({'error': 'Şablon bulunamadı'}), 404 