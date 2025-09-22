"""
RevPi device controller for RevPi-specific routes.
"""
from flask import render_template, request, jsonify
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
