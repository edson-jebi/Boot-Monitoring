"""
Service factory for creating and managing services.
"""
from typing import Dict, Any
from .base_service import DeviceServiceInterface
from .revpi_service import RevPiService
from .command_service import CommandService
from .systemd_service import SystemdService


class ServiceFactory:
    """Factory for creating and managing application services."""
    
    def __init__(self, config):
        self.config = config
        self._services = {}
    
    def get_revpi_service(self) -> RevPiService:
        """Get or create RevPi service instance."""
        if 'revpi' not in self._services:
            from config import config_map_revpi
            self._services['revpi'] = RevPiService(self.config, config_map_revpi)
        return self._services['revpi']
    
    def get_command_service(self) -> CommandService:
        """Get or create command service instance."""
        if 'command' not in self._services:
            self._services['command'] = CommandService(self.config)
        return self._services['command']
    
    def get_systemd_service(self) -> SystemdService:
        """Get or create systemd service instance."""
        if 'systemd' not in self._services:
            self._services['systemd'] = SystemdService(self.config)
        return self._services['systemd']
    
    def register_device_service(self, name: str, service: DeviceServiceInterface):
        """Register a new device service for future expansion."""
        self._services[name] = service
    
    def get_device_service(self, name: str) -> DeviceServiceInterface:
        """Get a registered device service."""
        if name not in self._services:
            raise ValueError(f"Device service '{name}' not found")
        return self._services[name]
    
    def get_all_device_services(self) -> Dict[str, DeviceServiceInterface]:
        """Get all registered device services."""
        return {k: v for k, v in self._services.items() 
                if isinstance(v, DeviceServiceInterface)}
