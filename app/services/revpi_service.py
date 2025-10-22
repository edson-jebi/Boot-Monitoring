"""
RevPi device service implementation.
"""
import logging
import subprocess
import signal
import os
import random
from typing import Dict, Any
from .base_service import DeviceServiceInterface, DeviceAction, DeviceStatus

logger = logging.getLogger(__name__)


class RevPiService(DeviceServiceInterface):
    """Service for managing RevPi devices."""
    
    def __init__(self, config, device_map: Dict[str, str]):
        self.config = config
        self.device_map = device_map
        self.command_timeout = getattr(config, 'COMMAND_TIMEOUT', 10)
    
    def _check_pitest_available(self) -> bool:
        """Check if piTest command is available."""
        try:
            result = subprocess.run(
                ['which', 'piTest'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _execute_pitest_command(self, command: list) -> subprocess.CompletedProcess:
        """Execute a piTest command safely."""
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=self.command_timeout
        )
    
    def _simulate_device_status(self, device_id: str) -> Dict[str, Any]:
        """Simulate device status for development."""
        simulated_value = random.choice([0, 1])
        logger.info(f"Simulated status for {device_id}: {simulated_value}")
        return {
            'status': DeviceStatus.ON.value if simulated_value == 0 else DeviceStatus.OFF.value,
            'value': simulated_value,
            'simulated': True
        }
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status of a specific device."""
        if device_id not in self.device_map:
            return {'status': DeviceStatus.ERROR.value, 'error': 'Invalid device ID'}
        
        if not self._check_pitest_available():
            return self._simulate_device_status(device_id)
        
        try:
            # Try single reading first
            command = ['piTest', '-1', '-r', device_id]
            result = self._execute_pitest_command(command)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                first_line = output.split('\n')[0] if output else ''
                logger.debug(f"piTest output for {device_id}: {first_line}")
                try:
                    value = int(first_line.split(":")[1])
                    return {
                        'status': DeviceStatus.ON.value if value == 0 else DeviceStatus.OFF.value,
                        'value': value,
                        'simulated': False
                    }
                except ValueError:
                    return {
                        'status': DeviceStatus.UNKNOWN.value,
                        'value': first_line,
                        'simulated': False
                    }
            else:
                # Fallback to process control method
                return self._get_status_with_process_control(device_id)
                
        except subprocess.TimeoutExpired:
            return self._get_status_with_process_control(device_id)
        except Exception as e:
            logger.error(f"Error getting status for {device_id}: {e}")
            return {'status': DeviceStatus.ERROR.value, 'error': str(e)}
    
    def _get_status_with_process_control(self, device_id: str) -> Dict[str, Any]:
        """Get status using process control for continuous commands."""
        try:
            proc = subprocess.Popen(
                ['piTest', '-r', device_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            
            # Read first line quickly
            line = proc.stdout.readline()
            
            # Kill the process group
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=1)
            
            if line:
                try:
                    value = int(line.strip())
                    return {
                        'status': DeviceStatus.ON.value if value == 0 else DeviceStatus.OFF.value,
                        'value': value,
                        'simulated': False
                    }
                except ValueError:
                    return {'status': DeviceStatus.UNKNOWN.value, 'simulated': False}
            else:
                return {'status': DeviceStatus.ERROR.value, 'simulated': False}
                
        except Exception as e:
            logger.error(f"Process control method failed for {device_id}: {e}")
            return {'status': DeviceStatus.ERROR.value, 'error': str(e)}
    
    def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all devices."""
        status_data = {}
        for device_id in self.device_map.keys():
            status_data[device_id] = self.get_device_status(device_id)
        return status_data
    
    def toggle_device(self, device_id: str, action: DeviceAction) -> Dict[str, Any]:
        """Toggle a device on/off."""
        if device_id not in self.device_map:
            return {'success': False, 'message': 'Invalid device ID'}
        
        if not self._check_pitest_available():
            logger.info(f"Simulated RevPi {device_id} {action.value}")
            return {
                'success': True,
                'message': f'{device_id} turned {action.value} successfully (simulated)',
                'output': 'Simulated command executed',
                'simulated': True
            }
        
        try:
            # Determine command value based on action
            value = '0' if action == DeviceAction.ON else '1'
            command = ['piTest', '-w', f'{device_id},{value}']
            
            logger.info(f"RevPi {device_id} {action.value}: {' '.join(command)}")
            
            result = self._execute_pitest_command(command)
            
            if result.returncode == 0:
                logger.info(f"RevPi {device_id} {action.value} successfully")
                return {
                    'success': True,
                    'message': f'{device_id} turned {action.value} successfully',
                    'output': result.stdout.strip(),
                    'simulated': False
                }
            else:
                error_msg = f"Command failed with return code {result.returncode}: {result.stderr}"
                logger.error(error_msg)
                return {'success': False, 'message': error_msg}
                
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {self.command_timeout} seconds"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(f"RevPi control error: {e}")
            return {'success': False, 'message': error_msg}
    
    def get_available_devices(self) -> Dict[str, str]:
        """Get list of available devices."""
        return self.device_map.copy()
