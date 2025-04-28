from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..config.mongodb_db import get_db
from ..models.user import User
from ..utils.helpers import send_email
from ..config.settings import Config
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Modül yükleme zamanı yerine istek zamanında şifre sıfırlama jetonlarını oluştur
def get_password_reset_tokens():
    db = get_db()
    if db is not None:  # DB örneğinin doğru şekilde kontrol edilmesi
        return db['password_reset_tokens']
    return None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Kullanıcının zaten var olup olmadığını kontrol et
    if User.find_by_email(data['email']):
        return jsonify({'message': 'Kullanıcı zaten mevcut'}), 400
    
    # Kullanıcı verilerini oluştur
    user_data = {
        'username': data.get('username', data['email'].split('@')[0]),
        'email': data['email'],
        'password': data['password'],
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'role': data.get('role', 'customer')
    }
    
    # Yeni kullanıcı oluştur
    user_id = User.create(user_data)
    
    if user_id:
        return jsonify({'message': 'Kullanıcı başarıyla oluşturuldu'}), 201
    else:
        return jsonify({'message': 'Kullanıcı oluşturma hatası'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.verify_password(data['email'], data['password'])
    
    if user:
        access_token = create_access_token(identity={'id': user['id'], 'role': user['role']})
        return jsonify({
            'access_token': access_token,
            'role': user['role']
        }), 200
    
    return jsonify({'message': 'Geçersiz kimlik bilgileri'}), 401

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.find_by_email(data['email'])
    
    if user:
        # Şifre sıfırlama token'ı oluştur
        token = User.create_reset_token(data['email'])
        if token:
            # Token'ı MongoDB'de sakla
            password_reset_tokens = get_password_reset_tokens()
            if password_reset_tokens is not None:  # Düzeltildi: MongoDB koleksiyonunun var olup olmadığını kontrol etmenin doğru yolu    
                try:
                    password_reset_tokens.insert_one({
                        'email': data['email'],
                        'token': token,
                        'expires': datetime.utcnow() + timedelta(hours=24)
                    })
                except Exception as e:
                    print(f"Error inserting token into MongoDB: {str(e)}")
                    # Devam etmek, MySQL'de hala token olduğu için
            
            # E-posta gönder
            # Geliştirme için sabit URL kullan
            app_url = Config.APP_URL
            if app_url is None or "localhost" in app_url:
                app_url = "http://127.0.0.1:5000"
                
            # Yeni rotayı kullan
            reset_link = f"{app_url}/password/reset?token={token}"
            print(f"Reset linki oluşturuldu: {reset_link}")
            
            email_sent = send_email(
                "Şifre Sıfırlama İstek",
                user['email'],
                f"Lütfen aşağıdaki linki tıklayarak şifrenizi sıfırlayın: {reset_link}"
            )
            
            if email_sent:
                return jsonify({'message': 'Şifre sıfırlama e-postası gönderildi'}), 200
            else:
                return jsonify({'message': 'E-posta gönderilemedi, ancak token oluşturuldu'}), 200
    
    return jsonify({'message': 'E-posta bulunamadı'}), 404

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    # İlk olarak MongoDB'de geçerli token'ı kontrol et
    password_reset_tokens = get_password_reset_tokens()
    if password_reset_tokens is not None:  # Düzeltildi: MongoDB koleksiyonunun var olup olmadığını kontrol etmenin doğru yolu
        try:
            mongo_token = password_reset_tokens.find_one({
                'token': token,
                'expires': {'$gt': datetime.utcnow()}
            })
            
            if mongo_token:
                # MongoDB token'ından e-posta adresine göre kullanıcıyı bul
                user = User.find_by_email(mongo_token['email'])
                if user:
                    # Kullanıcı modelini kullanarak şifreyi sıfırla
                    success = User.reset_password(token, new_password)
                    if success:
                        # Kullanılan token'ı kaldır
                        password_reset_tokens.delete_one({'token': token})
                        return jsonify({'message': 'Şifre sıfırlama başarılı'}), 200
        except Exception as e:
            print(f"Error checking MongoDB token: {str(e)}")
            # MySQL'e geri dönmek için geriye dönüş
    
    # MySQL'e geri dönmek için geriye dönüş
    # Kullanıcı modelini kullanarak şifreyi doğrudan sıfırla
    success = User.reset_password(token, new_password)
    
    if success:
        return jsonify({'message': 'Şifre sıfırlama başarılı'}), 200
    
    return jsonify({'message': 'Geçersiz veya süresi dolmuş token'}), 400 