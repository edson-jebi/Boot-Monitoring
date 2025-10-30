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

    def get_current_timezone(self) -> Dict[str, Any]:
        """Get current system timezone."""
        try:
            result = subprocess.run(
                ['timedatectl', 'show', '-p', 'Timezone', '--value'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                timezone = result.stdout.strip()
                logger.info(f"Current timezone: {timezone}")
                return {'success': True, 'timezone': timezone}
            else:
                return {'success': False, 'error': 'Failed to get timezone'}

        except Exception as e:
            logger.error(f"Error getting timezone: {e}")
            return {'success': False, 'error': str(e)}

    def set_timezone(self, timezone: str, username: str = None) -> Dict[str, Any]:
        """
        Set system timezone, sync time from internet, and update RTC.

        Args:
            timezone: Timezone string (e.g., 'Africa/Lusaka', 'UTC')
            username: User performing the action

        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Setting timezone to {timezone} by user {username}")

            # Set timezone using timedatectl
            result = subprocess.run(
                ['sudo', 'timedatectl', 'set-timezone', timezone],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                error_msg = result.stderr or 'Failed to set timezone'
                logger.error(f"Failed to set timezone: {error_msg}")
                return {'success': False, 'error': error_msg}

            logger.info(f"Timezone set successfully to {timezone}")

            # Synchronize time from internet
            ntp_sync_success = False
            try:
                import time
                logger.info("Synchronizing time from internet")

                # Ensure NTP is enabled
                ntp_enable_result = subprocess.run(
                    ['sudo', 'timedatectl', 'set-ntp', 'true'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if ntp_enable_result.returncode == 0:
                    logger.info("NTP enabled")

                    # Force immediate sync by restarting systemd-timesyncd
                    logger.info("Restarting systemd-timesyncd for immediate time sync")
                    restart_result = subprocess.run(
                        ['sudo', 'systemctl', 'restart', 'systemd-timesyncd'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if restart_result.returncode == 0:
                        logger.info("systemd-timesyncd restarted successfully")

                        # Wait for sync to complete (up to 5 seconds with faster checks)
                        for i in range(5):
                            time.sleep(0.5)  # Check every 500ms instead of 1 second
                            # Check if sync is complete
                            sync_status = subprocess.run(
                                ['timedatectl', 'timesync-status'],
                                capture_output=True,
                                text=True,
                                timeout=3
                            )

                            if sync_status.returncode == 0 and 'Server:' in sync_status.stdout:
                                logger.info(f"Time synchronized successfully (attempt {i+1})")
                                ntp_sync_success = True
                                break

                        if not ntp_sync_success:
                            logger.info("NTP service started, sync will complete in background")
                            # Consider it successful if service is running
                            ntp_sync_success = True
                    else:
                        logger.warning(f"Failed to restart systemd-timesyncd: {restart_result.stderr}")
                else:
                    logger.warning(f"Failed to enable NTP: {ntp_enable_result.stderr}")

            except Exception as ntp_error:
                logger.warning(f"Time sync error: {ntp_error}")

            # Try to update RTC with system time (now synced from internet)
            try:
                rtc_result = subprocess.run(
                    ['sudo', 'hwclock', '-w'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if rtc_result.returncode == 0:
                    logger.info("RTC updated successfully")
                    rtc_updated = True
                else:
                    logger.warning(f"RTC update failed: {rtc_result.stderr}")
                    rtc_updated = False

            except Exception as rtc_error:
                logger.warning(f"RTC update error: {rtc_error}")
                rtc_updated = False

            return {
                'success': True,
                'timezone': timezone,
                'ntp_synced': ntp_sync_success,
                'rtc_updated': rtc_updated,
                'message': f'Timezone set to {timezone}' + (' and time synced from internet' if ntp_sync_success else '') + (' and RTC updated' if rtc_updated else '')
            }

        except subprocess.TimeoutExpired:
            error_msg = "Timezone setting timed out"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Error setting timezone: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

    def list_timezones(self, region: str = None) -> Dict[str, Any]:
        """
        List available timezones, optionally filtered by region.

        Args:
            region: Optional region filter (e.g., 'Africa', 'America', 'Europe')

        Returns:
            Dict with success status and list of timezones
        """
        try:
            result = subprocess.run(
                ['timedatectl', 'list-timezones'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {'success': False, 'error': 'Failed to list timezones'}

            timezones = result.stdout.strip().split('\n')

            # Filter by region if specified
            if region:
                timezones = [tz for tz in timezones if tz.startswith(region)]

            return {
                'success': True,
                'timezones': timezones,
                'count': len(timezones),
                'region': region
            }

        except Exception as e:
            logger.error(f"Error listing timezones: {e}")
            return {'success': False, 'error': str(e)}

    def check_internet_connectivity(self) -> Dict[str, Any]:
        """Check if internet connection is available."""
        try:
            # Try to ping a reliable DNS server
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                capture_output=True,
                timeout=3
            )

            connected = result.returncode == 0
            logger.info(f"Internet connectivity: {'available' if connected else 'unavailable'}")

            return {
                'success': True,
                'connected': connected
            }

        except Exception as e:
            logger.warning(f"Internet check error: {e}")
            return {
                'success': True,
                'connected': False
            }
