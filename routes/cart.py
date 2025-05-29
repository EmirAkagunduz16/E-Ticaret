from flask import Blueprint, request, jsonify
from config.mongodb_db import get_db
from models.user import User
from utils.helpers import send_email
from decorators.auth import customer_required
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity, jwt_required
from bson import ObjectId
import traceback


cart_bp = Blueprint('cart', __name__)

# Koleksiyonları import zamanı yerine istek zamanında al
def get_cart_collection():
    db = get_db()
    if db is not None:  # Düzeltildi: DB instance'ın var olup olmadığını kontrol etmenin doğru yolu
        return db['carts']
    return None

def get_products_collection():
    db = get_db()
    if db is not None:  # Düzeltildi: DB instance'ın var olup olmadığını kontrol etmenin doğru yolu
        return db['products']
    return None

@cart_bp.route('/cart/add', methods=['POST'])
@customer_required
def add_to_cart():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Koleksiyonları al
        cart_collection = get_cart_collection()
        products_collection = get_products_collection()
        
        if cart_collection is None or products_collection is None:
            return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
        
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Ürünü kontrol et
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return jsonify({'message': 'Ürün bulunamadı'}), 404
        
        # Sepette bu ürün zaten var mı kontrol et
        existing_item = cart_collection.find_one({
            'user_id': current_user['id'],
            'product_id': product_id,
            'is_checked_out': False
        })
        
        if existing_item:
            # Varolan öğeyi güncelle
            cart_collection.update_one(
                {'_id': existing_item['_id']},
                {'$inc': {'quantity': quantity}}
            )
        else:
            # Yeni bir sepet öğesi ekle
            cart_item = {
                'user_id': current_user['id'],
                'product_id': product_id,
                'product_name': product['name'],
                'quantity': quantity,
                'price': product['price'],
                'image_url': product.get('image_url', ''),
                'created_at': datetime.now(timezone.utc),
                'is_checked_out': False
            }
            cart_collection.insert_one(cart_item)
        
        # Ürün bilgilerini al
        products_with_details = []
        updated_cart = cart_collection.find({
            'user_id': current_user['id'],
            'is_checked_out': False
        })
        
        for cart_item in updated_cart:
            product_info = products_collection.find_one({'_id': ObjectId(cart_item['product_id'])})
            if product_info:
                item_details = {
                    'product_id': str(product_info['_id']),
                    'product_name': product_info['name'],
                    'quantity': cart_item['quantity'],
                    'price': product_info['price'],
                    'image_url': product_info.get('image_url', ''),
                    'subtotal': cart_item['quantity'] * product_info['price']
                }
                products_with_details.append(item_details)
        
        # Sepet güncelleme e-postası gönder
        try:
            # Kullanıcı bilgilerini al
            user = User.find_by_id(current_user['id'])
            if not user:
                raise Exception("Kullanıcı bulunamadı")
            
            # Sepet öğelerini e-posta için biçimlendir
            formatted_items = []
            cart_total = 0
            
            for item in products_with_details:
                subtotal = item['quantity'] * item['price']
                cart_total += subtotal
                
                formatted_items.append({
                    'product_name': item['product_name'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'subtotal': subtotal
                })
                
                # Kullanıcı adını al
                user_name = user['first_name']
                if 'last_name' in user and user['last_name']:
                    user_name += f" {user['last_name']}"
                
                from config.settings import Config
                
                # Gönderici email parametresini al (varsa)
                sender_email = data.get('sender_email', None)
                
                # "Sepetiniz Güncellendi" e-postası gönder
                send_email(
                    "Sepetiniz Güncellendi",
                    user['email'],
                    "Sepetinize yeni bir ürün eklediniz.",
                    template="emails/cart_updated.html",
                    template_data={
                        'user_name': user_name,
                        'cart_items': formatted_items,
                        'app_url': Config.APP_URL or "http://localhost:5000"
                    },
                    sender=sender_email
                )
        except Exception as e:
            # Sadece hata logla, e-posta başarısız olursa istek başarısız olma
            print(f"Sepet güncelleme e-postası gönderimi hatası: {str(e)}")
        
        return jsonify({'message': 'Ürün sepete başarıyla eklendi'}), 201
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"Sepete ürün ekleme hatası: {str(e)}\n{traceback_str}")
        return jsonify({'message': f'Sepete ürün ekleme hatası: {str(e)}'}), 500

@cart_bp.route('/cart/checkout', methods=['POST'])
@customer_required
def checkout_cart():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Koleksiyonları al
    cart_collection = get_cart_collection()
    products_collection = get_products_collection()
    
    if cart_collection is None:
        return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
    
    # Sepetteki tüm öğeleri al
    cart_items = list(cart_collection.find({
        'user_id': current_user['id'],
        'is_checked_out': False
    }))
    
    if not cart_items:
        return jsonify({'message': 'Sepet boş'}), 400
    
    # Sipariş ID'si oluştur
    order_id = str(ObjectId())
    order_date = datetime.now(timezone.utc)
    
    # Sipariş ID'siyle sepet öğelerini işaretle
    cart_collection.update_many(
        {'user_id': current_user['id'], 'is_checked_out': False},
        {
            '$set': {
                'is_checked_out': True,
                'checked_out_at': order_date,
                'order_id': order_id
            }
        }
    )
    
    # Yeni şablonla sipariş onay e-postası gönder
    try:
        user = User.find_by_id(current_user['id'])
        if user:
            # Sepet öğelerini e-posta için biçimlendir
            formatted_items = []
            order_total = 0
            
            for item in cart_items:
                product_id = item['product_id']
                product_info = products_collection.find_one({'_id': ObjectId(product_id)})
                if product_info:
                    subtotal = item['quantity'] * item['price']
                    order_total += subtotal
                    
                    formatted_items.append({
                        'product_name': product_info['name'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'subtotal': subtotal
                    })
            
            # Kullanıcı adını al
            user_name = user['first_name']
            if 'last_name' in user and user['last_name']:
                user_name += f" {user['last_name']}"
            
            from config.settings import Config
            app_url = Config.APP_URL or "http://localhost:5000"
            
            # Gönderici email parametresini al (varsa)
            sender_email = data.get('sender_email', None)
            
            # "Siparişiniz Alındı" e-postası gönder
            send_email(
                "Siparişiniz Alındı",
                user['email'],
                "Siparişiniz başarıyla alındı.",
                template="emails/order_received.html",
                template_data={
                    'user_name': user_name,
                    'order_id': order_id,
                    'order_date': order_date.strftime("%d.%m.%Y %H:%M"),
                    'payment_method': 'Kredi Kartı',  # Bu bilgiyi siparişten alabilirsiniz
                    'order_items': formatted_items,
                    'order_total': order_total,
                    'app_url': app_url
                },
                sender=sender_email
            )
            
    except Exception as e:
        print(f"Sipariş onay e-postası gönderimi hatası: {str(e)}")
    
    return jsonify({
        'message': 'Sipariş başarıyla oluşturuldu',
        'order_id': order_id
    }), 200

@cart_bp.route('/cart', methods=['GET'])
@customer_required
def get_cart():
    current_user = get_jwt_identity()
    
    # Koleksiyonları al
    cart_collection = get_cart_collection()
    products_collection = get_products_collection()
    
    if cart_collection is None or products_collection is None:
        return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
    
    cart_items = list(cart_collection.find({
        'user_id': current_user['id'],
        'is_checked_out': False
    }))
    
    # ObjectId'i JSON serileştirme için dizeye çevir
    for item in cart_items:
        item['_id'] = str(item['_id'])
        # Ürün hala var mı kontrol et
        product = products_collection.find_one({
            '_id': ObjectId(item['product_id']),
            'is_deleted': False
        })
        # Don't overwrite the product_name to avoid duplication
        item['product_available'] = product is not None
    
    return jsonify({"items": cart_items}), 200

@cart_bp.route('/cart/count', methods=['GET'])
def get_cart_count():
    # Sepet koleksiyonunu al
    cart_collection = get_cart_collection()
    if cart_collection is None:
        return jsonify({'count': 0}), 200
    
    try:
        # İlk olarak Authorization başlığı var mı kontrol et
        auth_header = request.headers.get('Authorization', '')
        
        # Eğer Authorization başlığı yok veya boş token, 0 dön
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'count': 0}), 200
            
        # JWT kullanma ve hata işleme
        try:
            # Circular import önlemek için burada import et
            from flask_jwt_extended import decode_token
            from flask_jwt_extended.exceptions import JWTDecodeError
            
            # Başlıktan token'ı çıkar
            token = auth_header.split(' ')[1]
            
            # Token'ı çözümle
            decoded_token = decode_token(token)
            if decoded_token and 'sub' in decoded_token:
                user_data = decoded_token['sub']
                if isinstance(user_data, dict) and 'id' in user_data:
                    # Kullanıcının sepetindeki öğeleri say
                    count = cart_collection.count_documents({
                        'user_id': user_data['id'],
                        'is_checked_out': False
                    })
                    return jsonify({'count': count}), 200
        except (JWTDecodeError, Exception) as e:
            # Hata logla, istek başarısız olma
            print(f"JWT çözümleme hatası: {str(e)}")
    except Exception as e:
        # Herhangi bir hata oluşursa, hata logla ama 0 dön
        print(f"Sepet sayısı alma hatası: {str(e)}")
    
    # Varsayılan yanıt, yetkisiz veya hata durumları için
    return jsonify({'count': 0}), 200

@cart_bp.route('/cart/remove/<cart_id>', methods=['DELETE'])
@customer_required
def remove_cart_item(cart_id):
    try:
        current_user = get_jwt_identity()
        
        # Sepet koleksiyonunu al
        cart_collection = get_cart_collection()
        if cart_collection is None:
            return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
        
        # Sepet öğesini bul
        cart_item = cart_collection.find_one({
            '_id': ObjectId(cart_id),
            'user_id': current_user['id'],
            'is_checked_out': False
        })
        
        if not cart_item:
            return jsonify({'message': 'Sepet öğesi bulunamadı'}), 404
        
        # Sepet öğesini sil
        result = cart_collection.delete_one({
            '_id': ObjectId(cart_id),
            'user_id': current_user['id']
        })
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Ürün sepetten kaldırıldı'}), 200
        else:
            return jsonify({'message': 'Ürün sepetten kaldırılamadı'}), 500
    except Exception as e:
        print(f"Sepetten ürün kaldırma hatası: {str(e)}")
        return jsonify({'message': f'Sepetten ürün kaldırma hatası: {str(e)}'}), 500

@cart_bp.route('/cart/update/<cart_id>', methods=['PUT'])
@customer_required
def update_cart_item(cart_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return jsonify({'message': 'Miktar belirtilmedi'}), 400
        
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({'message': 'Miktar 1 veya daha fazla olmalıdır'}), 400
        
        # Sepet koleksiyonunu al
        cart_collection = get_cart_collection()
        if cart_collection is None:
            return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
        
        # Sepet öğesini bul
        cart_item = cart_collection.find_one({
            '_id': ObjectId(cart_id),
            'user_id': current_user['id'],
            'is_checked_out': False
        })
        
        if not cart_item:
            return jsonify({'message': 'Sepet öğesi bulunamadı'}), 404
        
        # Sepet öğesini güncelle
        result = cart_collection.update_one(
            {'_id': ObjectId(cart_id), 'user_id': current_user['id']},
            {'$set': {'quantity': quantity}}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Sepet öğesi güncellendi'}), 200
        else:
            return jsonify({'message': 'Sepet öğesi güncellenemedi'}), 500
    except Exception as e:
        print(f"Sepet öğesi güncelleme hatası: {str(e)}")
        return jsonify({'message': f'Sepet öğesi güncelleme hatası: {str(e)}'}), 500 