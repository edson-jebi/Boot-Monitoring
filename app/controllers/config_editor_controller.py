"""
Configuration Editor controller for managing JSON configuration files.
"""
import json
import os
from flask import render_template, jsonify, request, send_file, redirect, url_for
from app.auth import login_required
from .base_controller import BaseController
from config import device_map_path, log_path


class ConfigEditorController(BaseController):
    """Controller for configuration file editing."""

    def _register_routes(self):
        """Register configuration editor routes."""
        self.blueprint.add_url_rule('/config-editor', 'config_editor', self.config_editor, methods=['GET'])
        self.blueprint.add_url_rule('/config-data', 'config_data', self.config_data, methods=['GET'])
        self.blueprint.add_url_rule('/config-save', 'config_save', self.config_save, methods=['POST'])
        self.blueprint.add_url_rule('/log-directory', 'log_directory', self.log_directory, methods=['GET'])
        self.blueprint.add_url_rule('/download-log-file/<filename>', 'download_log_file', self.download_log_file, methods=['GET'])

    @login_required
    def config_editor(self):
        """Configuration editor page route - now redirects to service monitor."""
        self.log_user_action("redirected from config editor to service monitor")
        return redirect(url_for('main.service_monitor'))
    
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
    
    @login_required
    def log_directory(self):
        """Get list of files in the log directory."""
        self.log_user_action("browsed log directory")
        
        try:
            if not os.path.exists(log_path):
                return jsonify({
                    'success': False,
                    'error': f'Log directory does not exist: {log_path}'
                }), 404
            
            if not os.path.isdir(log_path):
                return jsonify({
                    'success': False,
                    'error': f'Path is not a directory: {log_path}'
                }), 400
            
            files = []
            for filename in os.listdir(log_path):
                file_path = os.path.join(log_path, filename)
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        files.append({
                            'name': filename,
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'readable': os.access(file_path, os.R_OK)
                        })
                    except OSError as e:
                        self.logger.warning(f"Could not get stats for {filename}: {e}")
                        files.append({
                            'name': filename,
                            'size': None,
                            'modified': None,
                            'readable': False
                        })
            
            # Sort files by modification time (newest first)
            files.sort(key=lambda x: x['modified'] or 0, reverse=True)
            
            return jsonify({
                'success': True,
                'log_path': log_path,
                'files': files
            })
            
        except Exception as e:
            self.logger.error(f"Error browsing log directory: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @login_required
    def download_log_file(self, filename):
        """Download a specific log file."""
        self.log_user_action(f"downloaded log file: {filename}")
        
        # Security check: prevent path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        file_path = os.path.join(log_path, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        if not os.path.isfile(file_path):
            return jsonify({
                'success': False,
                'error': 'Path is not a file'
            }), 400
        
        try:
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='text/plain'
            )
        except Exception as e:
            self.logger.error(f"Error downloading file {filename}: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to download file: {str(e)}'
            }), 500
