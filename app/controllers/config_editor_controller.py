"""
Configuration Editor controller for managing JSON configuration files.
"""
import json
import os
from flask import render_template, jsonify, request
from app.auth import login_required
from .base_controller import BaseController
from config import device_map_path


class ConfigEditorController(BaseController):
    """Controller for configuration file editing."""
    
    def _register_routes(self):
        """Register configuration editor routes."""
        self.blueprint.add_url_rule('/config-editor', 'config_editor', self.config_editor, methods=['GET'])
        self.blueprint.add_url_rule('/config-data', 'config_data', self.config_data, methods=['GET'])
        self.blueprint.add_url_rule('/config-save', 'config_save', self.config_save, methods=['POST'])
    
    @login_required
    def config_editor(self):
        """Configuration editor page route."""
        self.log_user_action("accessed config editor page")
        return render_template('config_editor.html', config_path=device_map_path)
    
    @login_required
    def config_data(self):
        """Get current configuration data."""
        self.log_user_action("requested config data")
        
        try:
            if os.path.exists(device_map_path):
                with open(device_map_path, 'r') as f:
                    config_data = json.load(f)
            else:
                # Create default configuration if file doesn't exist
                config_data = {
                    "log_level": "INFO",
                    "max_log_size": "10MB",
                    "log_rotation": True,
                    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "handlers": {
                        "console": {
                            "enabled": True,
                            "level": "INFO"
                        },
                        "file": {
                            "enabled": True,
                            "level": "DEBUG",
                            "filename": "/var/log/jebi-switchboard.log"
                        }
                    }
                }
                
            return jsonify({
                'success': True,
                'data': config_data,
                'path': device_map_path,
                'file_exists': os.path.exists(device_map_path)
            })
            
        except Exception as e:
            self.logger.error(f"Error reading config file: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @login_required
    def config_save(self):
        """Save configuration data to file."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            config_data = data.get('config_data')
            if not config_data:
                return jsonify({
                    'success': False,
                    'error': 'No configuration data provided'
                }), 400
            
            self.log_user_action(f"saving config to {device_map_path}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(device_map_path), exist_ok=True)
            
            # Save the configuration
            with open(device_map_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            return jsonify({
                'success': True,
                'message': f'Configuration saved successfully to {device_map_path}'
            })
            
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid JSON format: {str(e)}'
            }), 400
        except Exception as e:
            self.logger.error(f"Error saving config file: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
