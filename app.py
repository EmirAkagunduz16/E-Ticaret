from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
import sys
import os
import logging
from datetime import timedelta
# Replace the relative path with absolute path to project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import Config

# Uzantıları başlat
jwt = JWTManager()
mail = Mail()

# Test modunu kontrol et
is_test_mode = 'pytest' in sys.modules

# Loglama yapılandırması
def configure_logging(app):
    # Log dizinini oluştur
    log_dir = os.path.join(os.getcwd(), 'sent_emails', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Uygulama logları için
    app_log_file = os.path.join(log_dir, 'app.log')
    
    # Handler'ları yapılandır
    file_handler = logging.FileHandler(app_log_file)
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Flask logger'ını yapılandır
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # E-posta ve diğer loglar için ana dizin
    email_dir = os.path.join(os.getcwd(), 'sent_emails', 'messages')
    if not os.path.exists(email_dir):
        os.makedirs(email_dir)
    
    app.logger.info("Loglama sistemi yapılandırıldı")

def create_app(config_class=Config):
    # Flask uygulamasını başlat
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Test modunda SERVER_NAME'i ayarla
    if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
        app.config['SERVER_NAME'] = f"localhost:{os.environ.get('FLASK_TEST_PORT', '5000')}"
        app.config['APPLICATION_ROOT'] = '/'
    
    # Loglama sistemini yapılandır
    configure_logging(app)
    
    # CORS'ı yapılandır
    CORS(app) # butun domainlerden erişebilir hale getirir
    
    # JWT yapılandırması
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)  # 7 günlük token süresi
    
    # Uzantıları uygulamayla başlat
    jwt.init_app(app)
    mail.init_app(app)
    
    # SMTP debug bilgilerini log dosyasına yönlendir
    if app.debug:
        app.logger.info("SMTP debug modu etkinleştirildi, tüm SMTP iletişim logları sent_emails/logs dizinine kaydedilecek")
        # E-posta gönderim detaylarını kaydetmek için loglama düzeyini ayarla
        logging.getLogger('mail').setLevel(logging.DEBUG)
        logging.getLogger('mail.log').setLevel(logging.DEBUG)
    
    # MongoDB zaten modülünde başlatıldı
    from config.mongodb_db import init_mongodb
    # MongoDB'nin başlatılmasını sağla
    if not init_mongodb():
        app.logger.error("MongoDB bağlantısı başlatılamadı")
        if not is_test_mode:
            sys.exit(1)
        else:
            app.logger.warn("Test modu: MongoDB bağlantısı başarısız oldu, mock ile devam ediliyor")
    
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
        app.logger.info("RESET PASSWORD ROUTE ACCESSED")
        
        try:
            # Get token from URL
            token = request.args.get('token', '')
            app.logger.info(f"Token received: {token}")
            
            # Render the template
            return render_template('reset-password.html')
        except Exception as e:
            app.logger.error(f"Error in reset_password_page: {str(e)}")
            return app.send_static_file('404.html'), 404
    
    @app.route('/password/reset')
    def password_reset_page():
        app.logger.info("PASSWORD RESET ROUTE ACCESSED")
        token = request.args.get('token', '')
        app.logger.info(f"Token for password reset: {token}")
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
            app.logger.info(f"Şablon testi: {template_name}")
            return render_template(f"{template_name}.html")
        except Exception as e:
            app.logger.error(f"Şablon hatası: {template_name}: {str(e)}")
            return jsonify({
                'error': f"Şablon hatası: {template_name}",
                'message': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 