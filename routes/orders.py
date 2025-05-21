from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order import Order, OrderItem
from models.product import Product
from models.cart import Cart

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get all orders for the current user"""
    current_user = get_jwt_identity()
    user_id = current_user['id']
    
    # Get all orders for the user
    orders = Order.get_by_user(user_id)
    
    # Process orders for JSON serialization
    processed_orders = []
    for order in orders:
        # Convert datetime objects to ISO format strings
        processed_order = {
            'id': order['id'],
            'user_id': order['user_id'],
            'total_amount': float(order['total_amount']),
            'shipping_address': order['shipping_address'],
            'status': order['status'],
            'created_at': order['created_at'].isoformat() if order['created_at'] else None,
            'updated_at': order['updated_at'].isoformat() if order['updated_at'] else None
        }
        processed_orders.append(processed_order)
    
    # Return the orders
    return jsonify({
        'success': True,
        'orders': processed_orders
    })

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """Get details for a specific order"""
    current_user = get_jwt_identity()
    user_id = current_user['id']
    
    # Get the order
    order = Order.get_by_id(order_id)
    
    # Check if order exists and belongs to the current user
    if not order or order['user_id'] != user_id:
        return jsonify({
            'success': False,
            'message': 'Order not found'
        }), 404
    
    # Get order items
    items = OrderItem.get_by_order(order_id)
    
    # Get product details for each item
    for item in items:
        product = Product.get_by_id(item['product_id'])
        if product:
            item['product_name'] = product['name']
            item['product_image'] = product['image']
        else:
            item['product_name'] = 'Product not found'
            item['product_image'] = None
    
    # Process order for JSON serialization
    processed_order = {
        'id': order['id'],
        'user_id': order['user_id'],
        'total_amount': float(order['total_amount']),
        'shipping_address': order['shipping_address'],
        'status': order['status'],
        'created_at': order['created_at'].isoformat() if order['created_at'] else None,
        'updated_at': order['updated_at'].isoformat() if order['updated_at'] else None,
        'items': items
    }
    
    # Return the order with items
    return jsonify({
        'success': True,
        'order': processed_order
    })

@orders_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    current_user = get_jwt_identity()
    user_id = current_user['id']
    data = request.get_json()
    
    # Validate shipping address
    if not data or 'shipping_address' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing shipping address'
        }), 400
    
    # Get items from user's cart
    cart_items = Cart.get_items(user_id)
    
    # Check if cart is empty
    if not cart_items:
        return jsonify({
            'success': False,
            'message': 'Your cart is empty'
        }), 400
    
    # Calculate total amount
    total_amount = 0
    for item in cart_items:
        total_amount += item['price'] * item['quantity']
    
    # Create the order
    order_id = Order.create(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=data['shipping_address']
    )
    
    # Create order items
    for item in cart_items:
        OrderItem.create(
            order_id=order_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
    
    # Clear the user's cart
    Cart.clear(user_id)
    
    # Return the new order ID
    return jsonify({
        'success': True,
        'order_id': order_id,
        'message': 'Order created successfully'
    }), 201 