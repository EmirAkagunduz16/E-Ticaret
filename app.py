from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
import sys
from config.settings import Config

# Uzantıları başlat
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    # Flask uygulamasını başlat
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # CORS'ı yapılandır
    CORS(app) # butun domainlerden erişebilir hale getirir
    
    # Uzantıları uygulamayla başlat
    jwt.init_app(app)
    mail.init_app(app)
    
    # MongoDB zaten modülünde başlatıldı
    from config.mongodb_db import init_mongodb
    # MongoDB'nin başlatılmasını sağla
    if not init_mongodb():
        print("MongoDB bağlantısı başlatılamadı")
        sys.exit(1)
    
    # Veritabanı tablolarını başlat
    from utils.db_init import init_tables
    init_tables()
    
    # API yönlendiricilerini içe aktar ve kaydet
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.dev import dev_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api')
    app.register_blueprint(dev_bp, url_prefix='')
    
    # Hata işleyicilerini kaydet
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Ön uç yönlendiricileri
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/products')
    def products():
        return render_template('products.html')
    
    @app.route('/cart')
    def cart():
        return render_template('cart.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    @app.route('/reset-password', strict_slashes=False)
    @app.route('/reset-password/', strict_slashes=False)
    def reset_password_page():
        # Log that we reached this route - for debugging
        print("RESET PASSWORD ROUTE ACCESSED")
        
        try:
            # Get token from URL
            token = request.args.get('token', '')
            print(f"Token received: {token}")
            
            # Render the template
            return render_template('reset-password.html')
        except Exception as e:
            print(f"Error in reset_password_page: {str(e)}")
            return app.send_static_file('404.html'), 404
    
    @app.route('/password/reset')
    def password_reset_page():
        print("PASSWORD RESET ROUTE ACCESSED")
        token = request.args.get('token', '')
        print(f"Token for password reset: {token}")
        return render_template('reset-password.html')
    
    # Statik dosyaları sun
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Hata ayıklama yöntemi: reset-password.html'in varlığını kontrol et
    @app.route('/check-reset-template')
    def check_reset_template():
        import os
        template_path = os.path.join(app.template_folder, 'reset-password.html')
        exists = os.path.exists(template_path)
        return {
            'template_exists': exists,
            'template_path': template_path,
            'template_folder': app.template_folder
        }
    
    # Özel yöntem: şablonları doğrudan test etmek için
    @app.route('/test-template/<template_name>')
    def test_template(template_name):
        try:
            print(f"Şablon testi: {template_name}")
            return render_template(f"{template_name}.html")
        except Exception as e:
            print(f"Şablon hatası: {template_name}: {str(e)}")
            return jsonify({
                'error': f"Şablon hatası: {template_name}",
                'message': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 