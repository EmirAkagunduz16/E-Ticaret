from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import traceback

def supplier_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        try:
            current_user = get_jwt_identity()
            if current_user['role'] != 'supplier':
                return jsonify({'message': 'Bu uç noktaya yalnızca tedarikçiler erişebilir'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Kimlik doğrulama hatası', 'error': str(e)}), 422
    return wrapper

def customer_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Authorization başlığını kontrol et
            auth_header = request.headers.get('Authorization', '')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'message': 'Kimlik doğrulama gerekli',
                    'error': 'Eksik veya geçersiz Authorization başlığı'
                }), 401
                
            # JWT'yi manuel olarak doğrula
            verify_jwt_in_request()
            
            # Kullanıcı kimliğini al
            current_user = get_jwt_identity()
            
            # Hata ayıklama bilgisi
            print(f"JWT Kimliği: {current_user}")
            
            # Beklenen yapıya sahip mi kontrol et
            if not isinstance(current_user, dict) or 'role' not in current_user:
                return jsonify({
                    'message': 'Geçersiz token yapısı', 
                    'details': f"'role' anahtarı olan bir dict bekleniyordu, alınan: {type(current_user)} - {current_user}"
                }), 422
            
            # Rolü kontrol et
            if current_user['role'] != 'customer':
                return jsonify({
                    'message': 'Bu uç noktaya yalnızca müşteriler erişebilir',
                    'current_role': current_user.get('role', 'bilinmiyor')
                }), 403
                
            return fn(*args, **kwargs)
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(f"customer_required decorator'ında hata: {str(e)}\n{traceback_str}")
            
            # Authorization başlığı var mı kontrol et
            auth_header = request.headers.get('Authorization', 'Authorization başlığı yok')
            print(f"Authorization başlığı: {auth_header}")
            
            # Token yapısı hatalarını işle
            if "Not enough segments" in str(e):
                return jsonify({
                    'message': 'Geçersiz token formatı',
                    'error': 'Kimlik doğrulama tokenı hatalı biçimlendirilmiş'
                }), 401
            
            # İmza doğrulama hatalarını işle
            if "signature verification failed" in str(e).lower():
                return jsonify({
                    'message': 'Geçersiz token',
                    'error': 'Token imza doğrulaması başarısız oldu'
                }), 401
                
            # Süresi dolmuş token hatalarını işle
            if "expired" in str(e).lower():
                return jsonify({
                    'message': 'Token süresi dolmuş',
                    'error': 'Kimlik doğrulama tokenının süresi dolmuş'
                }), 401
            
            # Genel kimlik doğrulama hatası
            return jsonify({
                'message': 'Kimlik doğrulama hatası',
                'error': str(e),
                'auth_header_present': 'Authorization' in request.headers
            }), 422
    return wrapper
