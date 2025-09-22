"""
Command execution service for general system commands.
"""
import logging
import subprocess
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CommandService:
    """Service for executing system commands."""
    
    def __init__(self, config):
        self.config = config
        self.default_command = getattr(config, 'DEFAULT_COMMAND', ['echo', 'No default command configured'])
        self.command_timeout = getattr(config, 'COMMAND_TIMEOUT', 10)
    
    def execute_default_command(self, username: str = None) -> Dict[str, Any]:
        """Execute the default configured command."""
        try:
            logger.info(f"Executing command: {' '.join(self.default_command)} by user {username}")
            
            result = subprocess.run(
                self.default_command,
                capture_output=True,
                text=True,
                timeout=self.command_timeout
            )
            
            # Format the output
            command_output = f"Command: {' '.join(self.default_command)}\n"
            command_output += f"Return Code: {result.returncode}\n\n"
            command_output += f"Output:\n{result.stdout}\n\n"
            command_output += f"Errors:\n{result.stderr}"
            
            logger.info(f"Command executed successfully with return code: {result.returncode}")
            
            return {
                'success': True,
                'output': command_output,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {self.command_timeout} seconds"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except FileNotFoundError:
            error_msg = f"Error: '{self.default_command[0]}' command not found. Please ensure it's installed and in your PATH."
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(f"Command execution error: {e}")
            return {'success': False, 'error': error_msg}
    
    def execute_custom_command(self, command: List[str], username: str = None, timeout: int = None) -> Dict[str, Any]:
        """Execute a custom command with safety checks."""
        if timeout is None:
            timeout = self.command_timeout
            
        # Basic security check - prevent dangerous commands
        dangerous_commands = ['rm', 'del', 'format', 'mkfs', 'dd', 'fdisk']
        if any(cmd in command[0].lower() for cmd in dangerous_commands):
            return {'success': False, 'error': 'Command not allowed for security reasons'}
        
        try:
            logger.info(f"Executing custom command: {' '.join(command)} by user {username}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            logger.info(f"Custom command executed with return code: {result.returncode}")
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(f"Custom command execution error: {e}")
            return {'success': False, 'error': error_msg}
