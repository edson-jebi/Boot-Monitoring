"""
Authentication routes blueprint for JEBI Web Application.
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth import AuthManager, anonymous_required, rate_limiter

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """User login route."""
    if request.method == 'POST':
        # Rate limiting
        client_ip = request.remote_addr
        if rate_limiter.is_rate_limited(f"login_{client_ip}"):
            flash('Too many login attempts. Please try again later.', 'error')
            logger.warning(f"Rate limited login attempt from {client_ip}")
            return render_template('login.html'), 429
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        auth_manager = AuthManager()
        if auth_manager.login_user(username, password):
            return redirect(url_for('main.home'))
    
    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """User logout route with enhanced security."""
    auth_manager = AuthManager()
    auth_manager.logout_user()
    
    # Create response with cache control headers
    response = redirect(url_for('auth.login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    flash('You have been logged out successfully.', 'info')
    return response
