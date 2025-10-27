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
            now = datetime.datetime.now()
            # Format: "Thu, Oct 24 2025, 20:15:30"
            formatted_time = now.strftime('%a, %b %d %Y, %H:%M:%S')
            return jsonify({
                'success': True,
                'time': formatted_time,
                'timestamp': now.isoformat()
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
