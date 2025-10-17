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
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            error_msg = f"Error toggling device: {str(e)}"
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
