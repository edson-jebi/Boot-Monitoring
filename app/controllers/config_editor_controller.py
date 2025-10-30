"""
Configuration Editor controller for managing JSON configuration files.
"""
import json
import os
import zipfile
import tempfile
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
        self.blueprint.add_url_rule('/download-selected-logs', 'download_selected_logs', self.download_selected_logs, methods=['POST'])

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

                        # Extract logging period (first and last timestamp) from log file
                        log_period = self._extract_log_period(file_path)

                        files.append({
                            'name': filename,
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'readable': os.access(file_path, os.R_OK),
                            'log_period_start': log_period['start'],
                            'log_period_end': log_period['end']
                        })
                    except OSError as e:
                        self.logger.warning(f"Could not get stats for {filename}: {e}")
                        files.append({
                            'name': filename,
                            'size': None,
                            'modified': None,
                            'readable': False,
                            'log_period_start': None,
                            'log_period_end': None
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

    @login_required
    def download_selected_logs(self):
        """Download multiple selected log files as a ZIP archive."""
        try:
            files = request.form.getlist('files[]')
            
            if not files:
                return jsonify({
                    'success': False,
                    'error': 'No files selected'
                }), 400
            
            self.log_user_action(f"downloading selected log files: {', '.join(files)}")
            
            # Security check: prevent path traversal for all files
            for filename in files:
                if '..' in filename or '/' in filename or '\\' in filename:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid filename: {filename}'
                    }), 400
            
            # Create a temporary zip file
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.close()
            
            try:
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    added_files = []
                    for filename in files:
                        file_path = os.path.join(log_path, filename)
                        
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            try:
                                zipf.write(file_path, filename)
                                added_files.append(filename)
                            except Exception as e:
                                self.logger.warning(f"Could not add file {filename} to zip: {e}")
                        else:
                            self.logger.warning(f"File not found: {filename}")
                
                if not added_files:
                    os.unlink(temp_zip.name)
                    return jsonify({
                        'success': False,
                        'error': 'No valid files found to download'
                    }), 404
                
                # Generate a descriptive filename for the zip
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"log_files_{timestamp}.zip"
                
                return send_file(
                    temp_zip.name,
                    as_attachment=True,
                    download_name=zip_filename,
                    mimetype='application/zip'
                )
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_zip.name):
                    os.unlink(temp_zip.name)
                raise e
                
        except Exception as e:
            self.logger.error(f"Error creating zip download: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to create download: {str(e)}'
            }), 500

    def _extract_log_period(self, file_path):
        """
        Extract the logging period (first and last timestamp) from a log file.

        Args:
            file_path: Path to the log file

        Returns:
            Dict with 'start' and 'end' timestamps (ISO format) or None if not found
        """
        import re
        from datetime import datetime

        # Common log timestamp patterns
        patterns = [
            # ISO format: 2025-10-22 20:31:33
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            # ISO format with milliseconds: 2025-10-22 20:31:33.123
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)',
            # ISO format with timezone: 2025-10-22T20:31:33+00:00
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})',
            # Standard log format: [2025-10-22 20:31:33]
            r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]',
            # Common format: 22/Oct/2025:20:31:33
            r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        ]

        first_timestamp = None
        last_timestamp = None

        try:
            # Check if file is readable and not too large (max 100MB for scanning)
            if not os.access(file_path, os.R_OK) or os.path.getsize(file_path) > 100 * 1024 * 1024:
                return {'start': None, 'end': None}

            # Read first few lines for start timestamp
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for _ in range(50):  # Check first 50 lines
                    try:
                        line = f.readline()
                        if not line:
                            break

                        # Try each pattern
                        for pattern in patterns:
                            match = re.search(pattern, line)
                            if match:
                                timestamp_str = match.group(1)
                                first_timestamp = self._parse_timestamp(timestamp_str)
                                if first_timestamp:
                                    break

                        if first_timestamp:
                            break
                    except Exception:
                        continue

            # Read last few lines for end timestamp
            # Use tail-like approach for large files
            with open(file_path, 'rb') as f:
                # Seek to end of file
                f.seek(0, 2)
                file_size = f.tell()

                # Read last 8KB (should contain plenty of log lines)
                chunk_size = min(8192, file_size)
                f.seek(max(0, file_size - chunk_size))
                last_chunk = f.read().decode('utf-8', errors='ignore')

                # Split into lines and check last 50 lines
                lines = last_chunk.split('\n')
                for line in reversed(lines[-50:]):
                    if not line.strip():
                        continue

                    # Try each pattern
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            timestamp_str = match.group(1)
                            last_timestamp = self._parse_timestamp(timestamp_str)
                            if last_timestamp:
                                break

                    if last_timestamp:
                        break

            return {
                'start': first_timestamp.isoformat() if first_timestamp else None,
                'end': last_timestamp.isoformat() if last_timestamp else None
            }

        except Exception as e:
            self.logger.debug(f"Could not extract log period from {file_path}: {e}")
            return {'start': None, 'end': None}

    def _parse_timestamp(self, timestamp_str):
        """
        Parse various timestamp formats.

        Args:
            timestamp_str: Timestamp string to parse

        Returns:
            datetime object or None if parsing fails
        """
        from datetime import datetime

        # Common datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%d/%b/%Y:%H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        return None
