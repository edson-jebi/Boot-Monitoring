"""
Systemd service management service.
"""
import subprocess
import re
from typing import Dict, Any
from .base_service import BaseService


class SystemdService(BaseService):
    """Service for managing systemd services."""
    
    def __init__(self, config):
        """Initialize the SystemdService.
        
        Args:
            config: Application configuration object
        """
        self.config = config
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Get comprehensive status of a systemd service.
        
        Args:
            service_name: Name of the systemd service
            
        Returns:
            Dictionary with service status information
        """
        try:
            status_info = {
                'status': 'unknown',
                'active': False,
                'enabled': False,
                'uptime': 'N/A',
                'memory_usage': 'N/A',
                'last_log': 'N/A'
            }
            
            # Get service status
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True, text=True, timeout=5
            )
            #print(result.stdout.strip())

            status_info['status'] = result.stdout.strip()
            status_info['active'] = status_info['status'] == 'active'
            #self.logger.error(f"Error getting service status for {service_name}: {e}")
            #self.logger.error(f"HOLA Service status information: {status_info}")
            # Get enabled status
            result = subprocess.run(
                ['systemctl', 'is-enabled', service_name],
                capture_output=True, text=True, timeout=5
            )
            enabled_status = result.stdout.strip()
            status_info['enabled'] = enabled_status == 'enabled'
            
            # Get detailed status if service is active
            if status_info['active']:
                result = subprocess.run(
                    ['systemctl', 'status', service_name, '--no-pager'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # Extract uptime
                    uptime_match = re.search(r'Active: active \(running\) since (.+?);', output)
                    if uptime_match:
                        status_info['uptime'] = uptime_match.group(1)
                    
                    # Extract memory usage
                    memory_match = re.search(r'Memory: (.+)', output)
                    if memory_match:
                        status_info['memory_usage'] = memory_match.group(1)
            
            # Get last log entry
            try:
                result = subprocess.run(
                    ['journalctl', '-u', service_name, '-n', '1', '--no-pager'],
                    capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        # Get the last non-empty line
                        for line in reversed(lines):
                            if line.strip():
                                status_info['last_log'] = line.strip()
                                break
            except Exception:
                # If journalctl fails, continue without last log
                pass
            
            return status_info
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout getting status for service {service_name}")
            return {
                'status': 'timeout',
                'active': False,
                'enabled': False,
                'uptime': 'N/A',
                'memory_usage': 'N/A',
                'last_log': 'Command timeout'
            }
        except Exception as e:
            self.logger.error(f"Error getting service status for {service_name}: {e}")
            return {
                'status': 'error',
                'active': False,
                'enabled': False,
                'uptime': 'N/A',
                'memory_usage': 'N/A',
                'last_log': f'Error: {str(e)}'
            }
    
    def start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a systemd service."""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'start', service_name],
                capture_output=True, text=True, timeout=10
            )
            
            success = result.returncode == 0
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return {
                'success': success,
                'message': 'Service started successfully' if success else f'Failed to start service: {error_msg}',
                'output': result.stdout,
                'error': error_msg if not success else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout error: Service start command took too long',
                'output': '',
                'error': 'Command timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting service: {str(e)}',
                'output': '',
                'error': str(e)
            }
    
    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a systemd service."""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'stop', service_name],
                capture_output=True, text=True, timeout=10
            )
            
            success = result.returncode == 0
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return {
                'success': success,
                'message': 'Service stopped successfully' if success else f'Failed to stop service: {error_msg}',
                'output': result.stdout,
                'error': error_msg if not success else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout error: Service stop command took too long',
                'output': '',
                'error': 'Command timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping service: {str(e)}',
                'output': '',
                'error': str(e)
            }
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a systemd service."""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True, text=True, timeout=15
            )
            
            success = result.returncode == 0
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return {
                'success': success,
                'message': 'Service restarted successfully' if success else f'Failed to restart service: {error_msg}',
                'output': result.stdout,
                'error': error_msg if not success else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout error: Service restart command took too long',
                'output': '',
                'error': 'Command timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error restarting service: {str(e)}',
                'output': '',
                'error': str(e)
            }
