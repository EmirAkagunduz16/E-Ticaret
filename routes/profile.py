from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from utils.helpers import hash_password

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.find_by_id(current_user['id'])
    
    if user:
        return jsonify({
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role']
        }), 200
    
    return jsonify({'message': 'User not found'}), 404

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.find_by_id(current_user['id'])
    data = request.get_json()
    
    if user:
        user_data = {
            'username': user['username'],
            'email': data.get('email', user['email']),
            'first_name': data.get('first_name', user['first_name']),
            'last_name': data.get('last_name', user['last_name'])
        }
        
        # Check if email is already in use by another user
        if 'email' in data and data['email'] != user['email']:
            existing_user = User.find_by_email(data['email'])
            if existing_user:
                return jsonify({'message': 'Email already in use'}), 400
        
        # Update password if provided
        if 'password' in data:
            user_data['password'] = hash_password(data['password'])
            
        # Update user
        success = User.update(user['id'], user_data)
        
        if success:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'message': 'Error updating profile'}), 500
    
    return jsonify({'message': 'User not found'}), 404 