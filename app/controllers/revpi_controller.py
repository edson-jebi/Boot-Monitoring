"""
RevPi device controller for RevPi-specific routes.
"""
from flask import render_template, request, jsonify, session
from app.auth import login_required
from app.services import DeviceAction
from .base_controller import BaseController


class RevPiController(BaseController):
    """Controller for RevPi device management routes."""
    
    def _register_routes(self):
        """Register RevPi routes."""
        self.blueprint.add_url_rule('/revpi-control', 'revpi_control', self.revpi_control, methods=['GET'])
        self.blueprint.add_url_rule('/revpi-status', 'revpi_status', self.revpi_status, methods=['GET'])
        self.blueprint.add_url_rule('/revpi-toggle', 'revpi_toggle', self.revpi_toggle, methods=['POST'])
        self.blueprint.add_url_rule('/revpi-time', 'revpi_time', self.revpi_time, methods=['GET'])
        
        # Schedule management endpoints
        self.blueprint.add_url_rule('/revpi-schedule/save', 'save_schedule', self.save_schedule, methods=['POST'])
        self.blueprint.add_url_rule('/revpi-schedule/get/<device_id>', 'get_schedule', self.get_schedule, methods=['GET'])
        self.blueprint.add_url_rule('/revpi-schedule/all', 'get_all_schedules', self.get_all_schedules, methods=['GET'])
        self.blueprint.add_url_rule('/revpi-schedule/enable', 'enable_schedule', self.enable_schedule, methods=['POST'])
        self.blueprint.add_url_rule('/revpi-schedule/delete/<device_id>', 'delete_schedule', self.delete_schedule, methods=['DELETE'])
        self.blueprint.add_url_rule('/revpi-schedule/check', 'check_schedule', self.check_schedule, methods=['POST'])
        
        # Log download endpoint
        self.blueprint.add_url_rule('/download-logs-by-date', 'download_logs_by_date', self.download_logs_by_date, methods=['POST'])
        
        # Switchboard configuration endpoints
        self.blueprint.add_url_rule('/switchboard-config', 'get_switchboard_config', self.get_switchboard_config, methods=['GET'])
        self.blueprint.add_url_rule('/switchboard-config/update', 'update_switchboard_config', self.update_switchboard_config, methods=['POST'])

        # Relay activation events endpoint
        self.blueprint.add_url_rule('/api/relay-activations', 'get_relay_activations', self.get_relay_activations, methods=['GET'])
    
    @login_required
    def revpi_control(self):
        """RevPi control page route."""
        self.log_user_action("accessed RevPi control page")
        
        revpi_service = self.service_factory.get_revpi_service()
        devices = revpi_service.get_available_devices()
        
        return render_template('revpi_control.html', devices=devices)
    
    @login_required
    def revpi_status(self):
        """Get status of all RevPi devices."""
        self.log_user_action("requested RevPi status")
        
        try:
            revpi_service = self.service_factory.get_revpi_service()
            status_data = revpi_service.get_all_devices_status()
            return jsonify(status_data)
            
        except Exception as e:
            self.logger.error(f"RevPi status error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @login_required
    def revpi_toggle(self):
        """Toggle RevPi device state."""
        try:
            data = request.get_json()
            device_id = data.get('device')
            action_str = data.get('action')  # 'on' or 'off'

            if not device_id or not action_str:
                return jsonify({'success': False, 'message': 'Missing device or action'}), 400

            try:
                action = DeviceAction(action_str)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid action'}), 400

            self.log_user_action(f"toggled device {device_id}", f"action: {action_str}")

            revpi_service = self.service_factory.get_revpi_service()
            result = revpi_service.toggle_device(device_id, action)

            # Log activation to database
            try:
                from app.models import RelayActivation
                relay_activation = RelayActivation()
                relay_activation.log_activation(
                    device_id=device_id,
                    action=action_str,
                    user_id=session.get('user_id'),
                    username=session.get('username'),
                    is_automatic=False,
                    success=result.get('success', False)
                )
            except Exception as log_error:
                self.logger.error(f"Failed to log activation: {log_error}")

            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500

        except Exception as e:
            error_msg = f"Error toggling device: {str(e)}"
            self.logger.error(error_msg)
            return jsonify({'success': False, 'message': error_msg}), 500
    
    def log_service_activation(self):
        """
        Log relay activation from jebi-switchboard service.
        This endpoint does not require authentication as it's called by the system service.
        """
        try:
            data = request.get_json()
            device_id = data.get('device_id')
            action_str = data.get('action')  # 'on' or 'off'

            if not device_id or not action_str:
                return jsonify({'success': False, 'message': 'Missing device_id or action'}), 400

            # Log activation to database as automatic (from service)
            try:
                from app.models import RelayActivation
                relay_activation = RelayActivation()
                relay_activation.log_activation(
                    device_id=device_id,
                    action=action_str,
                    user_id=None,
                    username='jebi-switchboard',
                    is_automatic=True,
                    success=True
                )

                self.logger.info(f"Logged service activation: {device_id} {action_str}")
                return jsonify({'success': True, 'message': 'Activation logged'})

            except Exception as log_error:
                self.logger.error(f"Failed to log service activation: {log_error}")
                return jsonify({'success': False, 'message': 'Failed to log activation'}), 500

        except Exception as e:
            error_msg = f"Error logging service activation: {str(e)}"
            self.logger.error(error_msg)
            return jsonify({'success': False, 'message': error_msg}), 500

    @login_required
    def revpi_time(self):
        """Get current RevPi device time for schedule operations."""
        self.log_user_action("requested RevPi device time")
        
        try:
            import datetime
            now = datetime.datetime.now()
            time_data = {
                'success': True,
                'timestamp': now.isoformat(),
                'time': now.strftime('%H:%M'),
                'date': now.strftime('%Y-%m-%d'),
                'day': now.strftime('%a').lower(),  # 'mon', 'tue', etc.
                'day_of_week': now.weekday(),  # 0=Monday, 6=Sunday
                'unix_timestamp': int(now.timestamp()),
                'formatted_time': now.strftime('%Y-%m-%d %H:%M:%S')
            }
            return jsonify(time_data)
            
        except Exception as e:
            self.logger.error(f"RevPi time error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def system_time(self):
        """Get current system time formatted for display in UI."""
        try:
            import datetime
            import subprocess

            # Get current time
            now = datetime.datetime.now()

            # Get timezone name
            try:
                tz_result = subprocess.run(
                    ['timedatectl', 'show', '-p', 'Timezone', '--value'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                timezone = tz_result.stdout.strip() if tz_result.returncode == 0 else ''
            except:
                timezone = ''

            # Format: "Thu, Oct 24 2025, 20:15:30 (America/Vancouver)"
            formatted_time = now.strftime('%a, %b %d %Y, %H:%M:%S')
            if timezone:
                formatted_time += f' ({timezone})'

            return jsonify({
                'success': True,
                'time': formatted_time,
                'timestamp': now.isoformat(),
                'timezone': timezone
            })
        except Exception as e:
            self.logger.error(f"System time error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @login_required
    def save_schedule(self):
        """Save a device schedule."""
        self.log_user_action("saving device schedule")
        
        try:
            data = request.get_json()
            device_id = data.get('device_id')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            days = data.get('days', [])
            enabled = data.get('enabled', False)
            
            # Get current user ID from session
            user_id = session.get('user_id')
            
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.save_schedule(
                device_id, start_time, end_time, days, enabled, user_id
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            self.logger.error(f"Error saving schedule: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    @login_required
    def get_schedule(self, device_id):
        """Get schedule for a specific device."""
        self.log_user_action(f"getting schedule for device {device_id}")
        
        try:
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.get_schedule(device_id)
            return jsonify(result)
            
        except Exception as e:
            self.logger.error(f"Error getting schedule for {device_id}: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    @login_required
    def get_all_schedules(self):
        """Get all device schedules."""
        self.log_user_action("getting all device schedules")
        
        try:
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.get_all_schedules()
            return jsonify(result)
            
        except Exception as e:
            self.logger.error(f"Error getting all schedules: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    @login_required
    def enable_schedule(self):
        """Enable or disable a device schedule."""
        self.log_user_action("enabling/disabling device schedule")
        
        try:
            data = request.get_json()
            device_id = data.get('device_id')
            enabled = data.get('enabled', True)
            
            if not device_id:
                return jsonify({'success': False, 'message': 'Device ID is required'}), 400
            
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.enable_schedule(device_id, enabled)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 404
                
        except Exception as e:
            self.logger.error(f"Error enabling/disabling schedule: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    @login_required
    def delete_schedule(self, device_id):
        """Delete a device schedule."""
        self.log_user_action(f"deleting schedule for device {device_id}")
        
        try:
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.delete_schedule(device_id)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 404
                
        except Exception as e:
            self.logger.error(f"Error deleting schedule for {device_id}: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    def check_schedule(self):
        """
        Check schedule and enforce relay state for RelayLight.
        This endpoint is called periodically by the frontend to maintain schedule.
        No login required as it's called automatically by the app.
        """
        try:
            from datetime import datetime, time as dt_time
            
            schedule_service = self.service_factory.get_schedule_service()
            result = schedule_service.get_schedule('RelayLight')
            
            if not result.get('success') or not result.get('data'):
                return jsonify({'success': True, 'action': 'none', 'message': 'No schedule configured'})
            
            schedule = result['data']
            
            # Check if schedule is enabled
            if not schedule.get('enabled'):
                return jsonify({'success': True, 'action': 'none', 'message': 'Schedule disabled'})
            
            # Check if today is a scheduled day
            day_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            today = datetime.now().weekday()
            today_abbr = day_map.get(today, '')
            
            scheduled_days = schedule.get('days', [])
            if scheduled_days and today_abbr not in scheduled_days:
                return jsonify({'success': True, 'action': 'none', 'message': f'Not scheduled for {today_abbr}'})
            
            # Get current time and schedule times
            start_time_str = schedule.get('start_time')
            end_time_str = schedule.get('end_time')
            
            if not start_time_str or not end_time_str:
                return jsonify({'success': False, 'message': 'Invalid schedule times'})
            
            # Parse times
            # start_time = lights ON time
            # end_time = lights OFF time
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            
            on_time = dt_time(start_hour, start_min)
            off_time = dt_time(end_hour, end_min)
            current_time = datetime.now().time()
            
            # Determine if light should be on
            # Handle both daytime and overnight schedules
            if on_time < off_time:
                # Normal daytime schedule (e.g., ON at 08:00, OFF at 17:00)
                should_be_on = on_time <= current_time < off_time
            else:
                # Overnight schedule (e.g., ON at 18:00, OFF at 06:00)
                # Light should be ON if current time >= on_time OR current time < off_time
                should_be_on = current_time >= on_time or current_time < off_time
            
            # Get current relay status
            revpi_service = self.service_factory.get_revpi_service()
            status_data = revpi_service.get_all_devices_status()
            
            relay_light = status_data.get('RelayLight', {})
            current_status = relay_light.get('status', 'UNKNOWN')
            is_currently_on = current_status == 'ON'
            
            # Determine if we need to toggle
            if should_be_on and not is_currently_on:
                # Light should be ON but it's OFF - turn it ON
                toggle_result = revpi_service.toggle_device('RelayLight', DeviceAction.ON)
                if toggle_result.get('success'):
                    self.logger.info("Schedule check: Turned RelayLight ON")
                    return jsonify({'success': True, 'action': 'turned_on', 'message': 'Light turned ON per schedule'})
                else:
                    return jsonify({'success': False, 'action': 'failed', 'message': 'Failed to turn light ON'})
            
            elif not should_be_on and is_currently_on:
                # Light should be OFF but it's ON - turn it OFF
                toggle_result = revpi_service.toggle_device('RelayLight', DeviceAction.OFF)
                if toggle_result.get('success'):
                    self.logger.info("Schedule check: Turned RelayLight OFF")
                    return jsonify({'success': True, 'action': 'turned_off', 'message': 'Light turned OFF per schedule'})
                else:
                    return jsonify({'success': False, 'action': 'failed', 'message': 'Failed to turn light OFF'})
            
            else:
                # Light is in correct state
                return jsonify({
                    'success': True, 
                    'action': 'none', 
                    'message': f'Light already {"ON" if is_currently_on else "OFF"} (correct state)'
                })
        
        except Exception as e:
            self.logger.error(f"Error checking schedule: {e}", exc_info=True)
            return jsonify({'success': False, 'message': f'Error checking schedule: {str(e)}'}), 500
    
    @login_required
    def download_logs_by_date(self):
        """Download log files from jebi-switchboard directory filtered by date range"""
        try:
            import os
            import zipfile
            import io
            from datetime import datetime
            from flask import send_file
            
            # Get date range from request
            data = request.get_json()
            self.logger.info(f"Received download request with data: {data}")
            
            from_date_str = data.get('from_date')
            to_date_str = data.get('to_date')
            
            if not from_date_str or not to_date_str:
                return jsonify({
                    'success': False,
                    'message': 'Both from_date and to_date are required'
                }), 400
            
            # Parse dates
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
                # Set to_date to end of day
                to_date = to_date.replace(hour=23, minute=59, second=59)
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'message': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'
                }), 400
            
            log_directory = '/var/log/jebi-switchboard'
            
            # Check if directory exists
            if not os.path.exists(log_directory):
                return jsonify({
                    'success': False,
                    'message': f'Log directory not found: {log_directory}'
                }), 404
            
            # Find log files within date range
            matching_files = []
            try:
                for filename in os.listdir(log_directory):
                    filepath = os.path.join(log_directory, filename)
                    
                    # Only process files (not directories)
                    if not os.path.isfile(filepath):
                        continue
                    
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    # Check if file was modified within date range
                    if from_date <= file_mtime <= to_date:
                        matching_files.append({
                            'name': filename,
                            'path': filepath,
                            'modified': file_mtime
                        })
                
            except PermissionError:
                return jsonify({
                    'success': False,
                    'message': 'Permission denied accessing log directory'
                }), 403
            
            if not matching_files:
                return jsonify({
                    'success': False,
                    'message': f'No log files found between {from_date_str} and {to_date_str}'
                }), 404
            
            # Create zip file in memory
            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_info in matching_files:
                    try:
                        # Add file to zip with just the filename (not full path)
                        zf.write(file_info['path'], file_info['name'])
                    except Exception as e:
                        self.logger.warning(f"Could not add {file_info['name']} to zip: {e}")
            
            # Prepare the file for download
            memory_file.seek(0)
            
            # Generate filename with date range
            zip_filename = f"jebi-switchboard-logs_{from_date_str}_to_{to_date_str}.zip"
            
            self.log_user_action("downloaded logs", f"date range: {from_date_str} to {to_date_str}, files: {len(matching_files)}")
            
            return send_file(
                memory_file,
                mimetype='application/zip',
                as_attachment=True,
                download_name=zip_filename
            )
            
        except Exception as e:
            self.logger.error(f"Error downloading logs by date: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error downloading logs: {str(e)}'
            }), 500
    
    @login_required
    def get_switchboard_config(self):
        """Get switchboard configuration from JSON file"""
        try:
            import json
            
            config_path = '/home/pi/jebi-switchboard/config/strict_log_config.json'
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.log_user_action("retrieved switchboard configuration")
            
            return jsonify({
                'success': True,
                'config': {
                    'CHECK_INTERVAL_SEC': config.get('CHECK_INTERVAL_SEC', 10),
                    'FAIL_WINDOW': config.get('FAIL_WINDOW', 2),
                    'MAX_POWER_CYCLES': config.get('MAX_POWER_CYCLES', 4),
                    'REBOOT_WAIT_SEC': config.get('REBOOT_WAIT_SEC', 9),
                    'OFF_SECONDS': config.get('OFF_SECONDS', 10),
                    'STARTUP_DELAY_SEC': config.get('STARTUP_DELAY_SEC', 20),
                    'RelayScreen': {
                        'ip': config.get('RelayScreen', {}).get('ip', '192.168.1.143')
                    },
                    'RelayProcessor': {
                        'ip': config.get('RelayProcessor', {}).get('ip', '192.168.1.142')
                    }
                }
            })
            
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            return jsonify({
                'success': False,
                'message': 'Configuration file not found'
            }), 404
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return jsonify({
                'success': False,
                'message': 'Invalid configuration file format'
            }), 500
        except Exception as e:
            self.logger.error(f"Error reading switchboard config: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error reading configuration: {str(e)}'
            }), 500
    
    @login_required
    def update_switchboard_config(self):
        """Update switchboard configuration and restart service"""
        try:
            import json
            import subprocess
            
            config_path = '/home/pi/jebi-switchboard/config/strict_log_config.json'
            
            # Get updated values from request
            data = request.get_json()
            
            # Read current config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Track what was updated for logging
            updates = []
            
            # Update only the monitoring parameters
            if 'CHECK_INTERVAL_SEC' in data:
                config['CHECK_INTERVAL_SEC'] = int(data['CHECK_INTERVAL_SEC'])
                updates.append(f"CHECK_INTERVAL_SEC={config['CHECK_INTERVAL_SEC']}")
            if 'FAIL_WINDOW' in data:
                config['FAIL_WINDOW'] = int(data['FAIL_WINDOW'])
                updates.append(f"FAIL_WINDOW={config['FAIL_WINDOW']}")
            if 'MAX_POWER_CYCLES' in data:
                config['MAX_POWER_CYCLES'] = int(data['MAX_POWER_CYCLES'])
                updates.append(f"MAX_POWER_CYCLES={config['MAX_POWER_CYCLES']}")
            if 'REBOOT_WAIT_SEC' in data:
                config['REBOOT_WAIT_SEC'] = int(data['REBOOT_WAIT_SEC'])
                updates.append(f"REBOOT_WAIT_SEC={config['REBOOT_WAIT_SEC']}")
            
            # Update IP addresses for RelayScreen and RelayProcessor
            if 'RelayScreen_ip' in data:
                if 'RelayScreen' not in config:
                    config['RelayScreen'] = {}
                config['RelayScreen']['ip'] = str(data['RelayScreen_ip'])
                updates.append(f"RelayScreen.ip={config['RelayScreen']['ip']}")
            
            if 'RelayProcessor_ip' in data:
                if 'RelayProcessor' not in config:
                    config['RelayProcessor'] = {}
                config['RelayProcessor']['ip'] = str(data['RelayProcessor_ip'])
                updates.append(f"RelayProcessor.ip={config['RelayProcessor']['ip']}")
            
            # Write updated config back to file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.log_user_action("updated switchboard configuration", ", ".join(updates))
            
            # Only restart service if monitoring parameters were changed
            should_restart_service = any(key in data for key in ['CHECK_INTERVAL_SEC', 'FAIL_WINDOW', 'MAX_POWER_CYCLES', 'REBOOT_WAIT_SEC'])
            
            if should_restart_service:
                # Restart the jebi-switchboard-guard service
                try:
                    result = subprocess.run(
                        ['sudo', 'systemctl', 'restart', 'jebi-switchboard-guard.service'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        self.logger.info("jebi-switchboard-guard.service restarted successfully")
                        return jsonify({
                            'success': True,
                            'message': 'Configuration updated and service restarted successfully'
                        })
                    else:
                        self.logger.error(f"Failed to restart service: {result.stderr}")
                        return jsonify({
                            'success': False,
                            'message': f'Configuration saved but service restart failed: {result.stderr}'
                        }), 500
                        
                except subprocess.TimeoutExpired:
                    self.logger.error("Service restart timed out")
                    return jsonify({
                        'success': False,
                        'message': 'Configuration saved but service restart timed out'
                    }), 500
                except Exception as e:
                    self.logger.error(f"Error restarting service: {e}")
                    return jsonify({
                        'success': False,
                        'message': f'Configuration saved but service restart failed: {str(e)}'
                    }), 500
            else:
                # IP addresses updated, no service restart needed
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully'
                })
            
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            return jsonify({
                'success': False,
                'message': 'Configuration file not found'
            }), 404
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return jsonify({
                'success': False,
                'message': 'Invalid configuration file format'
            }), 500
        except ValueError as e:
            self.logger.error(f"Invalid parameter value: {e}")
            return jsonify({
                'success': False,
                'message': f'Invalid parameter value: {str(e)}'
            }), 400
        except Exception as e:
            self.logger.error(f"Error updating switchboard config: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error updating configuration: {str(e)}'
            }), 500

    @login_required
    def check_internet(self):
        """Check internet connectivity."""
        try:
            command_service = self.service_factory.get_command_service()
            result = command_service.check_internet_connectivity()
            return jsonify(result)
        except Exception as e:
            self.logger.error(f"Error checking internet: {e}")
            return jsonify({'success': False, 'connected': False, 'error': str(e)})

    @login_required
    def get_current_timezone(self):
        """Get current system timezone."""
        try:
            command_service = self.service_factory.get_command_service()
            result = command_service.get_current_timezone()
            return jsonify(result)
        except Exception as e:
            self.logger.error(f"Error getting timezone: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @login_required
    def list_timezones(self):
        """List available timezones, optionally filtered by region."""
        try:
            region = request.args.get('region', None)
            command_service = self.service_factory.get_command_service()
            result = command_service.list_timezones(region)
            return jsonify(result)
        except Exception as e:
            self.logger.error(f"Error listing timezones: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @login_required
    def set_timezone(self):
        """Set system timezone and update RTC."""
        try:
            data = request.get_json()
            timezone = data.get('timezone')

            if not timezone:
                return jsonify({'success': False, 'error': 'Timezone is required'}), 400

            username = self.get_current_user()
            command_service = self.service_factory.get_command_service()
            result = command_service.set_timezone(timezone, username)

            if result.get('success'):
                return jsonify(result)
            else:
                return jsonify(result), 500

        except Exception as e:
            self.logger.error(f"Error setting timezone: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @login_required
    def get_relay_activations(self):
        """Get relay activation events from database with optional time filtering."""
        try:
            from app.models import RelayActivation

            # Get query parameters
            start_time = request.args.get('start_time')  # ISO format or SQLite datetime
            end_time = request.args.get('end_time')
            device_id = request.args.get('device_id')
            limit = request.args.get('limit', 2000, type=int)

            # Get activations from database
            relay_activation = RelayActivation()
            activations = relay_activation.get_activations(
                start_time=start_time,
                end_time=end_time,
                device_id=device_id,
                limit=limit
            )

            self.logger.info(f"Retrieved {len(activations)} relay activation events")

            return jsonify({
                'success': True,
                'events': activations,
                'count': len(activations)
            })

        except Exception as e:
            self.logger.error(f"Error getting relay activations: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @login_required
    def get_system_info(self):
        """Get system information (system code, equipment, location)."""
        try:
            import json
            import os

            system_info_file = '/home/pi/Boot-Monitoring/system_info.json'

            # Return empty if file doesn't exist
            if not os.path.exists(system_info_file):
                return jsonify({
                    'success': True,
                    'system_code': '',
                    'equipment': '',
                    'location': ''
                })

            # Read from file
            with open(system_info_file, 'r') as f:
                data = json.load(f)

            self.logger.info("System information retrieved")
            return jsonify({
                'success': True,
                'system_code': data.get('system_code', ''),
                'equipment': data.get('equipment', ''),
                'location': data.get('location', '')
            })

        except Exception as e:
            self.logger.error(f"Error getting system info: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @login_required
    def save_system_info(self):
        """Save system information permanently."""
        try:
            import json
            import os

            data = request.get_json()
            system_code = data.get('system_code', '')
            equipment = data.get('equipment', '')
            location = data.get('location', '')

            system_info_file = '/home/pi/Boot-Monitoring/system_info.json'

            # Save to file
            system_info = {
                'system_code': system_code,
                'equipment': equipment,
                'location': location
            }

            with open(system_info_file, 'w') as f:
                json.dump(system_info, f, indent=2)

            username = self.get_current_user()
            self.logger.info(f"System information saved by user {username}: {system_info}")

            return jsonify({
                'success': True,
                'message': 'System information saved successfully',
                'system_code': system_code,
                'equipment': equipment,
                'location': location
            })

        except Exception as e:
            self.logger.error(f"Error saving system info: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
