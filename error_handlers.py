from flask import jsonify, request, render_template

def register_error_handlers(app):
    """Uygulamaya hata işleyicileri kaydet"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Yetkisiz', 'message': 'Kimlik doğrulama gerekli'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Yasak', 'message': 'Bu kaynağa erişmek için yeterli yetkiye sahip değilsiniz'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        # For API requests, return JSON
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bulunamadı', 'message': 'İstenilen kaynak bulunamadı'}), 404
        
        # For browser requests, redirect to index
        try:
            # First try to serve the 404.html static file
            return app.send_static_file('404.html')
        except:
            # If that fails, return JSON
            return jsonify({'error': 'Bulunamadı', 'message': 'İstenilen kaynak bulunamadı'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Sunucu hatası', 'message': 'Beklenmedik bir hata oluştu'}), 500 