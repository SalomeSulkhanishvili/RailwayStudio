"""
Monitor Controller
Handles business logic for the railway monitor
"""
import json
from datetime import datetime
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal

from core.railway_system import RailwaySystem
from core.json_formatter import RailwayJSONFormatter
from core.tcp_server import RailwayTCPServer, BlockStatus


class MonitorController(QObject):
    """Controller for monitor operations - handles all business logic"""
    
    # Signals for View updates
    tcp_server_started = Signal(int)  # port
    tcp_server_stopped = Signal()
    tcp_server_error = Signal(str)  # error_message
    client_count_changed = Signal(int)  # client_count
    log_message = Signal(str)  # message
    
    def __init__(self, railway_system: RailwaySystem):
        super().__init__()
        self.railway_system = railway_system
        self.formatter = RailwayJSONFormatter(railway_system)
        self.tcp_server: Optional[RailwayTCPServer] = None
        self.is_listening = False
        
    def log(self, message: str):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_message.emit(f"[{timestamp}] {message}")
    
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
    
    # TCP Server Management
    # ----------------------
    
    def start_tcp_server(self, port: int, host: str = "0.0.0.0") -> bool:
        """
        Start the TCP server
        Returns: success
        """
        if self.is_listening:
            self.log("⚠️ Server is already running")
            return False
        
        # Create and configure TCP server
        self.tcp_server = RailwayTCPServer(port=port, host=host)
        
        # Connect TCP server signals to controller methods
        self.tcp_server.log_message.connect(self.log)
        self.tcp_server.error_occurred.connect(self._on_tcp_error)
        self.tcp_server.client_connected.connect(self._on_client_connected)
        self.tcp_server.client_disconnected.connect(self._on_client_disconnected)
        self.tcp_server.block_status_update.connect(self._on_block_status_update)
        self.tcp_server.batch_status_update.connect(self._on_batch_status_update)
        
        # Start server
        if self.tcp_server.start():
            self.is_listening = True
            self.log(f"🟢 TCP Server started on {host}:{port}")
            self.log(f"📡 Accepting connections from any IP address")
            self.tcp_server_started.emit(port)
            return True
        else:
            self.tcp_server = None
            self.log(f"❌ Failed to start TCP server on port {port}")
            self.tcp_server_error.emit(f"Failed to start server on port {port}")
            return False
    
    def stop_tcp_server(self):
        """Stop the TCP server"""
        if not self.is_listening:
            return
        
        if self.tcp_server:
            self.tcp_server.stop()
            self.tcp_server = None
        
        self.is_listening = False
        self.log("🔴 TCP Server stopped")
        self.tcp_server_stopped.emit()
        self.client_count_changed.emit(0)
    
    def get_connected_client_count(self) -> int:
        """Get number of connected clients"""
        if self.tcp_server:
            return len(self.tcp_server.get_connected_clients())
        return 0
    
    def _on_tcp_error(self, error_msg: str):
        """Handle TCP server error"""
        self.log(f"❌ {error_msg}")
        self.tcp_server_error.emit(error_msg)
    
    def _on_client_connected(self, client_id: str):
        """Handle new client connection"""
        if self.tcp_server:
            client_count = len(self.tcp_server.get_connected_clients())
            self.client_count_changed.emit(client_count)
    
    def _on_client_disconnected(self, client_id: str):
        """Handle client disconnection"""
        if self.tcp_server:
            client_count = len(self.tcp_server.get_connected_clients())
            self.client_count_changed.emit(client_count)
    
    def _on_block_status_update(self, block_id: str, status: str):
        """Handle single block status update from TCP server"""
        # Get color for status
        color = BlockStatus.get_color(status)
        
        # Update block color in railway system
        if block_id in self.railway_system.blocks:
            self.railway_system.set_block_color(block_id, color)
            self.log(f"✓ {block_id} → {status} ({color})")
        else:
            # Try to find by block_id (BL001001) instead of rail_id
            found = False
            for rail_id, block in self.railway_system.blocks.items():
                if hasattr(block, 'block_id') and block.block_id == block_id:
                    self.railway_system.set_block_color(rail_id, color)
                    self.log(f"✓ {block_id} (rail {rail_id}) → {status} ({color})")
                    found = True
                    break
            
            if not found:
                self.log(f"⚠️ Block not found: {block_id}")
    
    def _on_batch_status_update(self, updates: list):
        """Handle batch status updates from TCP server"""
        success_count = 0
        for block_id, status in updates:
            color = BlockStatus.get_color(status)
            
            if block_id in self.railway_system.blocks:
                self.railway_system.set_block_color(block_id, color)
                success_count += 1
            else:
                # Try to find by block_id (BL001001)
                for rail_id, block in self.railway_system.blocks.items():
                    if hasattr(block, 'block_id') and block.block_id == block_id:
                        self.railway_system.set_block_color(rail_id, color)
                        success_count += 1
                        break
        
        self.log(f"✓ Batch update: {success_count}/{len(updates)} blocks updated")

