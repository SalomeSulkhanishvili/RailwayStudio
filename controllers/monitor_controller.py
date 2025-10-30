"""
Monitor Controller
Handles business logic for the railway monitor
"""
import json
from datetime import datetime
from typing import Callable, Optional

from core.railway_system import RailwaySystem
from core.json_formatter import RailwayJSONFormatter


class MonitorController:
    """Controller for monitor operations"""
    
    def __init__(self, railway_system: RailwaySystem):
        self.railway_system = railway_system
        self.formatter = RailwayJSONFormatter(railway_system)
        self.log_callback: Optional[Callable] = None
        
    def set_log_callback(self, callback: Callable):
        """Set callback for logging messages"""
        self.log_callback = callback
    
    def log(self, message: str):
        """Log a message"""
        if self.log_callback:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_callback(f"[{timestamp}] {message}")
    
    def load_layout(self, file_path: str) -> tuple[bool, str, int]:
        """
        Load a layout from a file
        Returns: (success, message, block_count)
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
                
                block_count = len(self.railway_system.blocks)
                self.log(f"✓ Loaded layout with {block_count} blocks")
                
                return True, f"Layout loaded successfully!\n{block_count} blocks loaded.", block_count
                
        except Exception as e:
            self.log(f"❌ Failed to load layout: {str(e)}")
            return False, f"Failed to load layout:\n{str(e)}", 0
    
    def parse_update_packet(self, data: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Parse update packet
        Format: BLOCK_ID:COLOR
        Returns: (success, block_id, color)
        """
        try:
            parts = data.strip().split(':')
            if len(parts) == 2:
                block_id = parts[0].strip()
                color = parts[1].strip()
                return True, block_id, color
            else:
                self.log(f"⚠️ Invalid packet format: {data}")
                return False, None, None
        except Exception as e:
            self.log(f"❌ Parse error: {str(e)}")
            return False, None, None
    
    def apply_color_update(self, block_id: str, color: str) -> bool:
        """
        Apply color update to a block
        Returns: success
        """
        # Color name mapping
        color_map = {
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'orange': '#FFA500',
            'purple': '#800080',
            'gray': '#888888',
            'black': '#000000',
            'white': '#FFFFFF'
        }
        
        if color.lower() in color_map:
            color = color_map[color.lower()]
        
        # Update block color
        if block_id in self.railway_system.blocks:
            self.railway_system.set_block_color(block_id, color)
            self.log(f"✓ Updated {block_id} → {color}")
            return True
        else:
            self.log(f"❌ Block not found: {block_id}")
            return False
    
    def test_color_change(self, block_id: str, color: str) -> bool:
        """
        Test color change manually
        Returns: success
        """
        if not block_id or not color:
            self.log("⚠️ Please enter both block ID and color")
            return False
        
        return self.apply_color_update(block_id, color)
    
    def reset_all_colors(self) -> int:
        """
        Reset all block colors to default
        Returns: number of blocks reset
        """
        count = 0
        for block_id in self.railway_system.blocks:
            self.railway_system.set_block_color(block_id, '#888888')
            count += 1
        self.log(f"↻ Reset {count} blocks to default color")
        return count
    
    def get_block_count(self) -> int:
        """Get the number of blocks in the system"""
        return len(self.railway_system.blocks)
    
    def get_available_blocks(self) -> list[str]:
        """Get list of available block IDs"""
        return list(self.railway_system.blocks.keys())

