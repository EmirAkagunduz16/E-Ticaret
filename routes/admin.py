from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product import Product
from models.user import User
from werkzeug.utils import secure_filename
import os
from functools import wraps
import logging

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Admin yetkisi kontrolü decorator'ü"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Basit admin kontrolü - gerçek uygulamada JWT token kullanılabilir
        if 'admin_logged_in' not in session:
            flash('Bu sayfaya erişmek için admin girişi yapmanız gerekiyor.', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Basit admin kontrolü (gerçek uygulamada hash kontrolü yapılmalı)
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Admin girişi başarılı!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/admin/logout')
def admin_logout():
    """Admin çıkış"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Admin çıkışı yapıldı.', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin')
@admin_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin ana sayfası"""
    try:
        # Ürün sayısını al
        products = Product.get_all(limit=100)
        product_count = len(products)
        
        # Son eklenen ürünleri al
        recent_products = Product.get_all(limit=5)
        
        return render_template('admin/dashboard.html', 
                             product_count=product_count,
                             recent_products=recent_products)
    except Exception as e:
        logging.error(f"Admin dashboard hatası: {str(e)}")
        flash('Dashboard yüklenirken bir hata oluştu.', 'error')
        return render_template('admin/dashboard.html', 
                             product_count=0,
                             recent_products=[])

@admin_bp.route('/admin/products')
@admin_required
def admin_products():
    """Admin ürün listesi"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        skip = (page - 1) * per_page
        
        products = Product.get_all(limit=per_page, skip=skip)
        
        return render_template('admin/products.html', 
                             products=products,
                             page=page)
    except Exception as e:
        logging.error(f"Admin products hatası: {str(e)}")
        flash('Ürünler yüklenirken bir hata oluştu.', 'error')
        return render_template('admin/products.html', 
                             products=[], 
                             page=1)

@admin_bp.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Yeni ürün ekleme"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            stock = int(request.form.get('stock'))
            supplier_id = int(request.form.get('supplier_id', 1))  # Form'dan al, varsayılan 1
            
            # Ürünü oluştur
            product_id = Product.create(
                supplier_id=supplier_id,
                name=name,
                description=description,
                price=price,
                stock=stock
            )
            
            if product_id:
                flash(f'Ürün başarıyla eklendi! ID: {product_id}', 'success')
                return redirect(url_for('admin.admin_products'))
            else:
                flash('Ürün eklenirken bir hata oluştu.', 'error')
                
        except Exception as e:
            logging.error(f"Ürün ekleme hatası: {str(e)}")
            flash(f'Ürün eklenirken bir hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/add_product.html')

@admin_bp.route('/admin/products/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Ürün düzenleme"""
    try:
        product = Product.get_by_id(product_id)
        if not product:
            flash('Ürün bulunamadı.', 'error')
            return redirect(url_for('admin.admin_products'))
        
        if request.method == 'POST':
            update_data = {}
            
            if request.form.get('name'):
                update_data['name'] = request.form.get('name')
            if request.form.get('description'):
                update_data['description'] = request.form.get('description')
            if request.form.get('price'):
                update_data['price'] = float(request.form.get('price'))
            if request.form.get('stock'):
                update_data['stock'] = int(request.form.get('stock'))
            
            if update_data:
                success = Product.update(product_id, update_data)
                if success:
                    flash('Ürün başarıyla güncellendi!', 'success')
                    return redirect(url_for('admin.admin_products'))
                else:
                    flash('Ürün güncellenirken bir hata oluştu.', 'error')
        
        return render_template('admin/edit_product.html', product=product)
        
    except Exception as e:
        logging.error(f"Ürün düzenleme hatası: {str(e)}")
        flash(f'Ürün düzenlenirken bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('admin.admin_products'))

@admin_bp.route('/admin/products/delete/<product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    """Ürün silme"""
    try:
        success = Product.delete(product_id)
        if success:
            flash('Ürün başarıyla silindi!', 'success')
        else:
            flash('Ürün silinirken bir hata oluştu.', 'error')
    except Exception as e:
        logging.error(f"Ürün silme hatası: {str(e)}")
        flash(f'Ürün silinirken bir hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_products'))

# API endpoints for AJAX operations
@admin_bp.route('/admin/api/products', methods=['GET'])
@admin_required
def admin_api_products():
    """API: Ürün listesi"""
    try:
        products = Product.get_all(limit=100)
        return jsonify({
            'status': 'success',
            'products': products
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/admin/api/products/<product_id>', methods=['GET'])
@admin_required
def admin_api_get_product(product_id):
    """API: Tekil ürün getir"""
    try:
        product = Product.get_by_id(product_id)
        if product:
            return jsonify({
                'status': 'success',
                'product': product
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Ürün bulunamadı'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 