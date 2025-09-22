"""
Base service interface for device management.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum


class DeviceAction(Enum):
    """Device action enumeration."""
    ON = "on"
    OFF = "off"


class DeviceStatus(Enum):
    """Device status enumeration."""
    ON = "ON"
    OFF = "OFF"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class DeviceServiceInterface(ABC):
    """Abstract interface for device services."""
    
    @abstractmethod
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status of a specific device."""
        pass
    
    @abstractmethod
    def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all devices."""
        pass
    
    @abstractmethod
    def toggle_device(self, device_id: str, action: DeviceAction) -> Dict[str, Any]:
        """Toggle a device on/off."""
        pass
    
    @abstractmethod
    def get_available_devices(self) -> Dict[str, str]:
        """Get list of available devices."""
        pass
