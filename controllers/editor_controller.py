"""
Editor Controller
Handles business logic for the railway editor
"""
from PySide6.QtWidgets import QMessageBox
import json

from core.railway_system import RailwaySystem
from core.json_formatter import RailwayJSONFormatter


class EditorController:
    """Controller for editor operations"""
    
    def __init__(self, railway_system: RailwaySystem):
        self.railway_system = railway_system
        self.formatter = RailwayJSONFormatter(railway_system)
        
    def add_rail(self, rail_type: str, length: int, position: tuple) -> str:
        """Add a new rail to the system"""
        x, y = position
        
        # Map UI names to system names
        type_map = {
            'Straight': 'straight',
            'Curved': 'curved',
            'Switch Left': 'switch_left',
            'Switch Right': 'switch_right'
        }
        
        system_type = type_map.get(rail_type, 'straight')
        block_id = self.railway_system.add_block(
            rail_type=system_type,
            x=x,
            y=y,
            rotation=0,
            length=length
        )
        
        return block_id
    
    def remove_rail(self, block_id: str) -> bool:
        """Remove a rail from the system"""
        if block_id in self.railway_system.blocks:
            self.railway_system.remove_block(block_id)
            return True
        return False
    
    def connect_rails(self, block1_id: str, point1: str, block2_id: str, point2: str) -> bool:
        """Connect two rails"""
        try:
            self.railway_system.connect_blocks(block1_id, point1, block2_id, point2)
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect_rails(self, block1_id: str, point1: str, block2_id: str, point2: str) -> bool:
        """Disconnect two rails"""
        try:
            self.railway_system.disconnect_blocks(block1_id, point1, block2_id, point2)
            return True
        except Exception as e:
            print(f"Failed to disconnect: {e}")
            return False
    
    def clear_all(self) -> None:
        """Clear all rails from the system"""
        self.railway_system.blocks.clear()
        self.railway_system.groups.clear()
    
    def auto_create_groups(self) -> tuple[bool, str]:
        """
        Automatically create groups from connected rails
        Returns: (success, message)
        """
        try:
            self.railway_system.auto_create_groups()
            
            # Also assign block IDs through the formatter
            self.formatter.to_blockgroups_json()
            
            num_groups = len(self.railway_system.groups)
            num_blocks = len(self.railway_system.blocks)
            
            message = (
                f"✓ Successfully created {num_groups} group(s)\n"
                f"Total blocks: {num_blocks}\n\n"
                f"All blocks are properly connected and validated!"
            )
            return True, message
            
        except ValueError as e:
            # Validation failed
            error_msg = (
                f"❌ GROUP VALIDATION FAILED\n\n"
                f"{str(e)}\n\n"
                f"📋 How to fix:\n"
                f"1. Check all rails are connected properly\n"
                f"2. Ensure no isolated rails exist\n"
                f"3. Verify connection points match correctly\n"
                f"4. Use double-click on connections to disconnect and reconnect"
            )
            return False, error_msg
    
    def save_layout(self, file_path: str) -> tuple[bool, str]:
        """
        Save the layout to a file
        Returns: (success, message)
        """
        if not self.railway_system.blocks:
            return False, "Cannot save an empty layout. Please add some rails first."
        
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            # Convert to blockGroups format (includes validation)
            try:
                data = self.formatter.to_blockgroups_json()
            except ValueError as e:
                # Validation error
                error_msg = (
                    f"❌ CANNOT SAVE - Validation Failed!\n\n"
                    f"{str(e)}\n\n"
                    f"Please fix these issues before saving:\n"
                    f"1. Connect all disconnected rails\n"
                    f"2. Ensure all blocks are properly linked\n"
                    f"3. Click 'Auto-Create Groups' to validate"
                )
                return False, error_msg
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True, "Layout saved successfully!"
            
        except Exception as e:
            return False, f"Failed to save layout:\n{str(e)}"
    
    def load_layout(self, file_path: str) -> tuple[bool, str]:
        """
        Load a layout from a file
        Returns: (success, message)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Check if it's the new blockGroups format or old format
                if "blockGroups" in data:
                    # New format
                    self.formatter.from_blockgroups_json(data)
                else:
                    # Old format (backward compatibility)
                    self.railway_system.load_from_json(data)
                
                return True, "Layout loaded successfully!"
                
        except Exception as e:
            return False, f"Failed to load layout:\n{str(e)}"
    
    def get_rail_count(self) -> int:
        """Get the number of rails in the system"""
        return len(self.railway_system.blocks)
    
    def get_group_count(self) -> int:
        """Get the number of groups in the system"""
        return len(self.railway_system.groups)

