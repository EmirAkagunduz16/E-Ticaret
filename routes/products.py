from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from ..config.mongodb_db import get_db
from ..models.user import User
from ..utils.helpers import send_email
from ..decorators.auth import supplier_required
from datetime import datetime
from bson import ObjectId

products_bp = Blueprint('products', __name__)

# Koleksiyonları istek zamanında al
def get_products_collection():
    db = get_db()
    if db is not None:  # DB instance'ın var olup olmadığını kontrol etmenin doğru yolu
        return db['products']
    return None

def get_cart_collection():
    db = get_db()
    if db is not None:  # Proper way to check for DB instance
        return db['carts']
    return None

@products_bp.route('/products', methods=['POST'])
@supplier_required
def add_product():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Ürünler koleksiyonunu al
    products_collection = get_products_collection()
    if products_collection is None:
        return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
    
    product = {
        'supplier_id': current_user['id'],
        'name': data['name'],
        'description': data['description'],
        'price': data['price'],
        'stock': data['stock'],
        'created_at': datetime.utcnow(),
        'is_deleted': False
    }
    
    products_collection.insert_one(product)
    return jsonify({'message': 'Ürün başarıyla eklendi'}), 201

@products_bp.route('/products/<product_id>', methods=['PUT'])
@supplier_required
def update_product(product_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    
    products_collection = get_products_collection()
    if products_collection is None:
        return jsonify({'message': 'Database connection error'}), 500
        
    product = products_collection.find_one({
        '_id': ObjectId(product_id),
        'supplier_id': current_user['id'],
        'is_deleted': False
    })
    
    if not product:
        return jsonify({'message': 'Ürün bulunamadı'}), 404
    
    update_data = {
        'name': data.get('name', product['name']),
        'description': data.get('description', product['description']),
        'price': data.get('price', product['price']),
        'stock': data.get('stock', product['stock'])
    }
    
    products_collection.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': update_data}
    )
    
    return jsonify({'message': 'Ürün başarıyla güncellendi'}), 200

@products_bp.route('/products/<product_id>', methods=['DELETE'])
@supplier_required
def delete_product(product_id):
    current_user = get_jwt_identity()
    
    products_collection = get_products_collection()
    cart_collection = get_cart_collection()
    
    if products_collection is None or cart_collection is None:
        return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
    
    product = products_collection.find_one({
        '_id': ObjectId(product_id),
        'supplier_id': current_user['id'],
        'is_deleted': False
    })
    
    if not product:
        return jsonify({'message': 'Ürün bulunamadı'}), 404
    
    # Ürünün herhangi bir sepette olup olmadığını kontrol et
    carts_with_product = list(cart_collection.find({
        'product_id': product_id,
        'is_checked_out': False
    }))
    
    if carts_with_product:
        # Ürünü yazılımsal olarak sil
        products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'is_deleted': True}}
        )
        
        # Sepetinde bu ürünü olan kullanıcılara bildirim gönder
        for cart in carts_with_product:
            user = User.query.get(cart['user_id'])
            if user:
                send_email(
                    "Product Unavailable",
                    user.email,
                    f"Sepetinizdeki '{product['name']}' ürünü artık mevcut değil."
                )
        
        return jsonify({
            'message': 'Ürün yazılımsal olarak silindi. Sepetinde bu ürünü olan kullanıcılara bildirildi.'
        }), 200
    
    # Ürünün herhangi bir sepette olmadığını kontrol et
    products_collection.delete_one({'_id': ObjectId(product_id)})
    return jsonify({'message': 'Ürün başarıyla silindi'}), 200

@products_bp.route('/products', methods=['GET'])
def get_products():
    products_collection = get_products_collection()
    if products_collection is None:
        return jsonify({'message': 'Veritabanı bağlantı hatası'}), 500
    
    # Sorgu parametrelerini al
    page = int(request.args.get('page', 1))
    per_page = 12  # Ürünlerin sayfa başına düşeceği sayı
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    # Sorgu oluştur
    query = {'is_deleted': False}
    
    # Arama kriteri eğer sağlanmışsa ekle
    if search:
        query['name'] = {'$regex': search, '$options': 'i'}
    
    # Fiyat aralığı eğer sağlanmışsa ekle
    if min_price or max_price:
        price_filter = {}
        if min_price:
            price_filter['$gte'] = float(min_price)
        if max_price:
            price_filter['$lte'] = float(max_price)
        if price_filter:
            query['price'] = price_filter
    
    # Toplam ürün sayısını al
    total_products = products_collection.count_documents(query)
    
    # Toplam sayfa sayısını hesapla
    total_pages = (total_products + per_page - 1) // per_page
    
    # Şu anki sayfadaki ürünleri al
    products = list(products_collection.find(query)
                   .sort('created_at', -1)
                   .skip((page - 1) * per_page)
                   .limit(per_page))
    
    # Her ürünün ObjectId'ini string'e çevir
    for product in products:
        product['_id'] = str(product['_id'])
    
    # Sayfalanmış yanıt döndür
    return jsonify({
        'products': products,
        'total': total_products,
        'total_pages': total_pages,
        'page': page,
        'per_page': per_page
    }), 200

@products_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    products_collection = get_products_collection()
    if products_collection is None:
        return jsonify({'message': 'Database connection error'}), 500
        
    # En son 6 ürünü öne çıkaran
    featured_products = list(products_collection.find(
        {'is_deleted': False}
    ).sort('created_at', -1).limit(6))
    
    # Eğer hiç ürün yoksa, bir örnek ürün oluştur
    if len(featured_products) == 0:
        sample_product = {
            'name': 'Sample Product',
            'description': 'This is a sample product for demonstration',
            'price': 99.99,
            'stock': 10,
            'created_at': datetime.utcnow(),
            'is_deleted': False
        }
        product_id = products_collection.insert_one(sample_product).inserted_id
        sample_product['_id'] = str(product_id)
        featured_products = [sample_product]
    else:
        # Her ürünün ObjectId'ini string'e çevir
        for product in featured_products:
            product['_id'] = str(product['_id'])
    
    return jsonify(featured_products), 200 