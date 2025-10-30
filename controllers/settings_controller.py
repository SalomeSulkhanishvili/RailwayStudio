"""
Settings Controller
Handles application settings management and persistence
"""
import json
import os
from typing import Dict, Any, Tuple
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor


class SettingsController(QObject):
    """Controller for settings operations"""
    
    # Signals
    settings_changed = Signal(dict)  # Emits when settings are updated
    network_settings_changed = Signal(dict)  # Emits when network settings change
    
    def __init__(self, settings_file: str = "settings.json"):
        super().__init__()
        self.settings_file = settings_file
        self.settings = self.load_settings()
        self.default_settings = self.get_default_settings()
        
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            # Display settings
            'grid_size': 20,
            'rail_color': '#888888',
            'selected_color': '#4A90E2',
            'connection_color': '#FF5252',
            
            # Network settings
            'udp_port': 5000,
            'ip_address': '192.168.1.100',
            'subnet_mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns_server': '8.8.8.8',
            
            # Editor settings
            'auto_save': False,
            'show_grid': True,
            'snap_to_grid': True,
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file
        Returns: settings dictionary
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    defaults = self.get_default_settings()
                    defaults.update(settings)
                    return defaults
            else:
                return self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.get_default_settings()
    
    def save_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Save settings to file
        Returns: (success, message)
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Check if network settings changed
            network_keys = ['udp_port', 'ip_address', 'subnet_mask', 'gateway', 'dns_server']
            network_changed = any(
                self.settings.get(key) != settings.get(key) 
                for key in network_keys
            )
            
            self.settings = settings
            
            # Emit signals
            self.settings_changed.emit(settings)
            if network_changed:
                network_settings = {k: settings.get(k) for k in network_keys if k in settings}
                self.network_settings_changed.emit(network_settings)
            
            return True, "Settings saved successfully!"
        except Exception as e:
            return False, f"Failed to save settings: {str(e)}"
    
    def apply_settings(self, new_settings: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate and apply settings
        Returns: (success, message)
        """
        # Validate network settings
        if 'udp_port' in new_settings:
            port = new_settings['udp_port']
            if not (1024 <= port <= 65535):
                return False, "UDP port must be between 1024 and 65535"
        
        if 'ip_address' in new_settings:
            if not self.validate_ip(new_settings['ip_address']):
                return False, "Invalid IP address format"
        
        if 'subnet_mask' in new_settings:
            if not self.validate_ip(new_settings['subnet_mask']):
                return False, "Invalid subnet mask format"
        
        if 'gateway' in new_settings:
            if not self.validate_ip(new_settings['gateway']):
                return False, "Invalid gateway format"
        
        if 'dns_server' in new_settings:
            if not self.validate_ip(new_settings['dns_server']):
                return False, "Invalid DNS server format"
        
        # Save settings
        return self.save_settings(new_settings)
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Reset settings to default values
        Returns: default settings dictionary
        """
        defaults = self.get_default_settings()
        self.save_settings(defaults)
        return defaults
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def update_setting(self, key: str, value: Any) -> None:
        """Update a single setting (in memory only, call apply_settings to save)"""
        self.settings[key] = value
    
    def validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if not (0 <= num <= 255):
                    return False
            return True
        except:
            return False
    
    def get_color_as_qcolor(self, key: str) -> QColor:
        """Get a color setting as QColor"""
        color_str = self.settings.get(key, '#888888')
        return QColor(color_str)
    
    def set_color_from_qcolor(self, key: str, color: QColor) -> None:
        """Set a color setting from QColor"""
        self.settings[key] = color.name()
    
    def export_settings(self, file_path: str) -> Tuple[bool, str]:
        """
        Export settings to a file
        Returns: (success, message)
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True, f"Settings exported to {file_path}"
        except Exception as e:
            return False, f"Failed to export settings: {str(e)}"
    
    def import_settings(self, file_path: str) -> Tuple[bool, str]:
        """
        Import settings from a file
        Returns: (success, message)
        """
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
            
            # Validate before applying
            return self.apply_settings(imported_settings)
        except Exception as e:
            return False, f"Failed to import settings: {str(e)}"

