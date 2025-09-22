"""
Main controller for home and general routes.
"""
from flask import render_template, request, jsonify, redirect, url_for
from app.auth import login_required
from .base_controller import BaseController


class MainController(BaseController):
    """Controller for main application routes."""
    
    def _register_routes(self):
        """Register main routes."""
        self.blueprint.add_url_rule('/', 'home', self.home, methods=['GET'])
        self.blueprint.add_url_rule('/execute', 'execute_command', self.execute_command, methods=['GET'])
    
    @login_required
    def home(self):
        """Home page route - redirects to service monitor."""
        return redirect(url_for('main.service_monitor'))
    
    @login_required
    def execute_command(self):
        """Execute default piTest command route."""
        self.log_user_action("executed default command")
        
        command_service = self.service_factory.get_command_service()
        result = command_service.execute_default_command(self.get_current_user())
        
        if result['success']:
            return render_template('home.html', result=result['output'])
        else:
            return render_template('home.html', result=result['error'])
