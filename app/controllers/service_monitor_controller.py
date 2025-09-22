"""
Service Monitor controller for systemd service status monitoring.
"""
from flask import render_template, jsonify, request
from app.auth import login_required
from .base_controller import BaseController


class ServiceMonitorController(BaseController):
    """Controller for service monitoring routes."""
    
    def _register_routes(self):
        """Register service monitoring routes."""
        self.blueprint.add_url_rule('/service-monitor', 'service_monitor', self.service_monitor, methods=['GET'])
        self.blueprint.add_url_rule('/service-status', 'service_status', self.service_status, methods=['GET'])
        self.blueprint.add_url_rule('/service-control', 'service_control', self.service_control, methods=['POST'])
    
    @login_required
    def service_monitor(self):
        """Service monitor page route."""
        self.log_user_action("accessed service monitor page")
        return render_template('service_monitor.html')
    
    @login_required
    def service_status(self):
        """Get real-time status of the jebi-switchboard-guard service."""
        self.log_user_action("requested service status")
        
        try:
            systemd_service = self.service_factory.get_systemd_service()
            status = systemd_service.get_service_status('jebi-switchboard-guard.service')
            
            return jsonify({
                'success': True,
                'service_name': 'jebi-switchboard-guard.service',
                'status': status['status'],
                'active': status['active'],
                'enabled': status['enabled'],
                'uptime': status.get('uptime', 'N/A'),
                'memory_usage': status.get('memory_usage', 'N/A'),
                'last_log': status.get('last_log', 'N/A')
            })
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @login_required
    def service_control(self):
        """Control systemd service (start/stop/restart)."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400
            
            action = data.get('action')
            service_name = data.get('service_name', 'jebi-switchboard-guard.service')
            
            if action not in ['start', 'stop', 'restart']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid action. Must be start, stop, or restart'
                }), 400
            
            self.log_user_action(f"requested service {action} for {service_name}")
            
            systemd_service = self.service_factory.get_systemd_service()
            
            if action == 'start':
                result = systemd_service.start_service(service_name)
            elif action == 'stop':
                result = systemd_service.stop_service(service_name)
            elif action == 'restart':
                result = systemd_service.restart_service(service_name)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            self.logger.error(f"Error controlling service: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
