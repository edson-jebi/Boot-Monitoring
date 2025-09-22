"""
Error handling utilities for JEBI Web Application.
"""
import logging
from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers for the Flask application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request from {request.remote_addr}: {error}")
        if request.is_json:
            return jsonify(error='Bad request'), 400
        return render_template('error.html', 
                             error_code=400, 
                             error_message="Bad request"), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access from {request.remote_addr}: {error}")
        if request.is_json:
            return jsonify(error='Unauthorized'), 401
        return render_template('error.html', 
                             error_code=401, 
                             error_message="Unauthorized access"), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access from {request.remote_addr}: {error}")
        if request.is_json:
            return jsonify(error='Forbidden'), 403
        return render_template('error.html', 
                             error_code=403, 
                             error_message="Access forbidden"), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"Page not found from {request.remote_addr}: {request.url}")
        if request.is_json:
            return jsonify(error='Not found'), 404
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        logger.warning(f"Rate limit exceeded from {request.remote_addr}")
        if request.is_json:
            return jsonify(error='Rate limit exceeded'), 429
        return render_template('error.html', 
                             error_code=429, 
                             error_message="Too many requests"), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error from {request.remote_addr}: {error}")
        if request.is_json:
            return jsonify(error='Internal server error'), 500
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle unexpected exceptions."""
        if isinstance(e, HTTPException):
            return e
        
        logger.exception(f"Unexpected error from {request.remote_addr}: {e}")
        if request.is_json:
            return jsonify(error='Internal server error'), 500
        return render_template('error.html', 
                             error_code=500, 
                             error_message="An unexpected error occurred"), 500
