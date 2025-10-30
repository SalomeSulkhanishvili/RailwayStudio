"""
Railway System - Core data model
Manages all rails, connections, and state
"""

from typing import Dict, List, Optional, Tuple
from PySide6.QtCore import QObject, Signal


class RailBlock:
    """Represents a single rail block in the system"""
    
    def __init__(self, block_id: str, rail_type: str, x: float, y: float, 
                 rotation: float = 0, length: float = 100, color: str = "#888888"):
        self.id = block_id
        self.type = rail_type  # 'straight', 'curved', 'switch_left', 'switch_right'
        self.x = x
        self.y = y
        self.rotation = rotation  # in degrees
        self.length = length
        self.color = color  # Current color (for monitoring)
        
        # Connection points: each rail has connection points
        # For straight: ['start', 'end']
        # For curved: ['start', 'end']  
        # For switch: ['start', 'end1', 'end2']
        self.connections: Dict[str, Optional[Tuple[str, str]]] = {}
        self._init_connection_points()
        
        # Linked-list structure - neighboring rails
        self.next_rails: List[str] = []  # List of rail IDs connected after this one
        self.prev_rails: List[str] = []  # List of rail IDs connected before this one
        
        # Group membership
        self.group_id: Optional[str] = None  # Which group/section this rail belongs to
        
        # Railway system metadata (for blockGroups format)
        self.block_id: Optional[str] = None  # BL ID (e.g., BL001001)
        self.axle_counter: Optional[str] = None  # AC ID (e.g., AC001001)
        self.signals: List[dict] = []  # Signal data
        
    def _init_connection_points(self):
        """Initialize connection points based on rail type"""
        if self.type in ['straight', 'curved']:
            self.connections = {'start': None, 'end': None}
        elif self.type in ['switch_left', 'switch_right']:
            self.connections = {'start': None, 'end1': None, 'end2': None}
            
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'rotation': self.rotation,
            'length': self.length,
            'color': self.color,
            'connections': {
                point: (conn[0], conn[1]) if conn else None 
                for point, conn in self.connections.items()
            },
            'next_rails': self.next_rails,
            'prev_rails': self.prev_rails,
            'group_id': self.group_id
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'RailBlock':
        """Create RailBlock from dictionary"""
        block = RailBlock(
            block_id=data['id'],
            rail_type=data['type'],
            x=data['x'],
            y=data['y'],
            rotation=data.get('rotation', 0),
            length=data.get('length', 100),
            color=data.get('color', '#888888')
        )
        
        # Restore connections (will be validated after all blocks are loaded)
        if 'connections' in data:
            block.connections = {
                point: tuple(conn) if conn else None
                for point, conn in data['connections'].items()
            }
        
        # Restore linked-list structure
        block.next_rails = data.get('next_rails', [])
        block.prev_rails = data.get('prev_rails', [])
        block.group_id = data.get('group_id', None)
            
        return block
    
    def get_next_block(self, railway_system: 'RailwaySystem') -> Optional['RailBlock']:
        """Get the next block in the linked list (primary path)"""
        if self.next_rails:
            return railway_system.blocks.get(self.next_rails[0])
        return None
        
    def get_prev_block(self, railway_system: 'RailwaySystem') -> Optional['RailBlock']:
        """Get the previous block in the linked list (primary path)"""
        if self.prev_rails:
            return railway_system.blocks.get(self.prev_rails[0])
        return None


class RailGroup:
    """Represents a group/section of connected rails"""
    
    def __init__(self, group_id: str, name: str = ""):
        self.id = group_id
        self.name = name or group_id
        self.rail_ids: List[str] = []  # Ordered list of rails in this group
        self.color: str = "#888888"  # Default color for this group
        
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'rail_ids': self.rail_ids,
            'color': self.color
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'RailGroup':
        group = RailGroup(data['id'], data.get('name', ''))
        group.rail_ids = data.get('rail_ids', [])
        group.color = data.get('color', '#888888')
        return group


class RailwaySystem(QObject):
    """Manages the entire railway system"""
    
    # Signals for UI updates
    block_added = Signal(str)  # block_id
    block_removed = Signal(str)  # block_id
    block_updated = Signal(str)  # block_id
    block_color_changed = Signal(str, str)  # block_id, new_color
    system_cleared = Signal()
    group_created = Signal(str)  # group_id
    group_updated = Signal(str)  # group_id
    
    def __init__(self):
        super().__init__()
        self.blocks: Dict[str, RailBlock] = {}
        self.groups: Dict[str, RailGroup] = {}
        self._next_id = 1
        self._next_group_id = 1
        
    def generate_id(self) -> str:
        """Generate a unique ID for a new block"""
        block_id = f"rail_{self._next_id:04d}"
        self._next_id += 1
        return block_id
        
    def add_block(self, rail_type: str, x: float, y: float, 
                  rotation: float = 0, length: float = 100) -> str:
        """Add a new rail block to the system"""
        block_id = self.generate_id()
        block = RailBlock(block_id, rail_type, x, y, rotation, length)
        self.blocks[block_id] = block
        self.block_added.emit(block_id)
        return block_id
        
    def remove_block(self, block_id: str):
        """Remove a rail block from the system"""
        if block_id in self.blocks:
            # Remove all connections to this block
            self._remove_connections_to_block(block_id)
            del self.blocks[block_id]
            self.block_removed.emit(block_id)
            
    def update_block_position(self, block_id: str, x: float, y: float):
        """Update block position"""
        if block_id in self.blocks:
            self.blocks[block_id].x = x
            self.blocks[block_id].y = y
            self.block_updated.emit(block_id)
            
    def update_block_rotation(self, block_id: str, rotation: float):
        """Update block rotation"""
        if block_id in self.blocks:
            self.blocks[block_id].rotation = rotation
            self.block_updated.emit(block_id)
            
    def connect_blocks(self, block_id1: str, point1: str, 
                      block_id2: str, point2: str) -> bool:
        """Connect two blocks at specified connection points
        
        This creates a bidirectional connection and updates next_rails/prev_rails
        based on which connection points are used:
        
        - block1.end → block2.start: block1.next=[...block2], block2.prev=[...block1]
        - block1.start → block2.end: block1.prev=[...block2], block2.next=[...block1]
        - block1.start → block2.start: block1.prev=[...block2], block2.prev=[...block1]
        - block1.end → block2.end: block1.next=[...block2], block2.next=[...block1]
        """
        if block_id1 not in self.blocks or block_id2 not in self.blocks:
            return False
            
        block1 = self.blocks[block_id1]
        block2 = self.blocks[block_id2]
        
        if point1 not in block1.connections or point2 not in block2.connections:
            return False
            
        # Create bidirectional connection in connections dict
        block1.connections[point1] = (block_id2, point2)
        block2.connections[point2] = (block_id1, point1)
        
        # Update linked-list structure (next_rails / prev_rails)
        # IMPORTANT: The relationship depends on which connection points are used
        # For one block, the other is "next"; for the other block, the first is "prev"
        
        if 'end' in point1 and 'start' in point2:
            # Case 1: block1.end → block2.start (normal forward connection)
            # block1 points TO block2 (block2 is NEXT for block1)
            # block1 comes BEFORE block2 (block1 is PREV for block2)
            if block_id2 not in block1.next_rails:
                block1.next_rails.append(block_id2)
            if block_id1 not in block2.prev_rails:
                block2.prev_rails.append(block_id1)
                
        elif 'start' in point1 and 'end' in point2:
            # Case 2: block1.start ← block2.end (normal reverse connection)
            # block2 points TO block1 (block2 is PREV for block1)
            # block2 comes BEFORE block1 (block1 is NEXT for block2)
            if block_id2 not in block1.prev_rails:
                block1.prev_rails.append(block_id2)
            if block_id1 not in block2.next_rails:
                block2.next_rails.append(block_id1)
                
        elif 'start' in point1 and 'start' in point2:
            # Case 3: block1.start ↔ block2.start (both point away from connection)
            # Both blocks have their "start" at the connection point
            # Each block considers the other as "previous" (coming from behind)
            if block_id2 not in block1.prev_rails:
                block1.prev_rails.append(block_id2)
            if block_id1 not in block2.prev_rails:
                block2.prev_rails.append(block_id1)
                
        elif 'end' in point1 and 'end' in point2:
            # Case 4: block1.end ↔ block2.end (both point toward connection)
            # Both blocks have their "end" at the connection point
            # Each block considers the other as "next" (pointing forward to it)
            if block_id2 not in block1.next_rails:
                block1.next_rails.append(block_id2)
            if block_id1 not in block2.next_rails:
                block2.next_rails.append(block_id1)
        
        # Verify the connection was set up correctly (immediate validation)
        self._verify_connection_consistency(block_id1, block_id2)
        
        self.block_updated.emit(block_id1)
        self.block_updated.emit(block_id2)
        return True
    
    def _verify_connection_consistency(self, block_id1: str, block_id2: str):
        """Verify that the connection between two blocks is properly bidirectional"""
        block1 = self.blocks.get(block_id1)
        block2 = self.blocks.get(block_id2)
        
        if not block1 or not block2:
            return
        
        # Check if the connection is properly mirrored
        # If block1 has block2 in next, block2 should have block1 in prev (or both in next for end-end)
        # If block1 has block2 in prev, block2 should have block1 in next (or both in prev for start-start)
        
        if block_id2 in block1.next_rails:
            # block1 → block2, so block2 should have block1 in prev OR next (depending on connection type)
            if block_id1 not in block2.prev_rails and block_id1 not in block2.next_rails:
                print(f"⚠️  WARNING: Connection inconsistency detected immediately after connect!")
                print(f"   {block_id1} has {block_id2} in next_rails")
                print(f"   BUT {block_id2} has neither {block_id1} in prev_rails nor next_rails")
                print(f"   {block_id1}.next_rails: {block1.next_rails}")
                print(f"   {block_id2}.prev_rails: {block2.prev_rails}")
                print(f"   {block_id2}.next_rails: {block2.next_rails}")
        
        if block_id2 in block1.prev_rails:
            # block2 → block1, so block2 should have block1 in next OR prev (depending on connection type)
            if block_id1 not in block2.next_rails and block_id1 not in block2.prev_rails:
                print(f"⚠️  WARNING: Connection inconsistency detected immediately after connect!")
                print(f"   {block_id1} has {block_id2} in prev_rails")
                print(f"   BUT {block_id2} has neither {block_id1} in next_rails nor prev_rails")
                print(f"   {block_id1}.prev_rails: {block1.prev_rails}")
                print(f"   {block_id2}.next_rails: {block2.next_rails}")
                print(f"   {block_id2}.prev_rails: {block2.prev_rails}")
        
    def disconnect_blocks(self, block_id: str, point: str):
        """Disconnect a specific connection point"""
        if block_id not in self.blocks:
            return
            
        block = self.blocks[block_id]
        if point in block.connections and block.connections[point]:
            # Get connected block
            conn_id, conn_point = block.connections[point]
            
            # Remove from linked-list structure
            if conn_id in block.next_rails:
                block.next_rails.remove(conn_id)
            if conn_id in block.prev_rails:
                block.prev_rails.remove(conn_id)
                
            if conn_id in self.blocks:
                conn_block = self.blocks[conn_id]
                if block_id in conn_block.next_rails:
                    conn_block.next_rails.remove(block_id)
                if block_id in conn_block.prev_rails:
                    conn_block.prev_rails.remove(block_id)
            
            # Remove both sides of connection
            block.connections[point] = None
            if conn_id in self.blocks:
                self.blocks[conn_id].connections[conn_point] = None
                self.block_updated.emit(conn_id)
                
            self.block_updated.emit(block_id)
            
    def _remove_connections_to_block(self, block_id: str):
        """Remove all connections pointing to a specific block"""
        if block_id not in self.blocks:
            return
            
        block = self.blocks[block_id]
        
        # Disconnect all connections from this block
        for point in list(block.connections.keys()):
            if block.connections[point]:
                conn_id, conn_point = block.connections[point]
                if conn_id in self.blocks:
                    self.blocks[conn_id].connections[conn_point] = None
                    self.block_updated.emit(conn_id)
                    
    def set_block_color(self, block_id: str, color: str):
        """Set the color of a block (for monitoring/train position)"""
        if block_id in self.blocks:
            self.blocks[block_id].color = color
            self.block_color_changed.emit(block_id, color)
            
    def create_group(self, name: str = "") -> str:
        """Create a new rail group"""
        group_id = f"group_{self._next_group_id:04d}"
        self._next_group_id += 1
        
        group = RailGroup(group_id, name)
        self.groups[group_id] = group
        self.group_created.emit(group_id)
        return group_id
        
    def add_rail_to_group(self, rail_id: str, group_id: str):
        """Add a rail to a group"""
        if rail_id in self.blocks and group_id in self.groups:
            # Remove from old group if any
            if self.blocks[rail_id].group_id:
                old_group = self.groups.get(self.blocks[rail_id].group_id)
                if old_group and rail_id in old_group.rail_ids:
                    old_group.rail_ids.remove(rail_id)
                    
            # Add to new group
            self.blocks[rail_id].group_id = group_id
            if rail_id not in self.groups[group_id].rail_ids:
                self.groups[group_id].rail_ids.append(rail_id)
            self.group_updated.emit(group_id)
            self.block_updated.emit(rail_id)
            
    def auto_create_groups(self):
        """Automatically create groups from turnout to turnout
        
        Groups consist of directly connected rails WITHOUT turnouts.
        Groups are separated ONLY by turnouts (switch_left, switch_right).
        If no turnouts exist, all connected rails form ONE group.
        """
        # Clear existing groups
        self.groups.clear()
        for block in self.blocks.values():
            block.group_id = None
            
        visited = set()
        
        # Find all turnouts (switches) - these are the ONLY group boundaries
        turnout_ids = {bid for bid, block in self.blocks.items() 
                      if block.type in ['switch_left', 'switch_right']}
        
        # DON'T mark turnouts as visited yet - we need to process blocks on their other side
        # Turnouts are boundaries, not isolated blocks
        
        # Process all non-turnout blocks
        for block_id, block in self.blocks.items():
            # Skip turnouts - they are boundaries, not group members
            if block_id in turnout_ids:
                continue
                
            # Skip if already in a group
            if block_id in visited:
                continue
            
            # Create a new group and traverse all connected non-turnout rails
            group_id = self.create_group(f"Section {self._next_group_id}")
            
            # Use a stack (DFS) to traverse connected rails
            # Stop when hitting turnouts (they are boundaries)
            stack = [block_id]
            blocks_in_group = []
            
            while stack:
                current_id = stack.pop()
                
                # Skip if already visited
                if current_id in visited:
                    continue
                
                # If this is a turnout, don't add it to group
                # Turnouts are boundaries between groups
                if current_id in turnout_ids:
                    continue
                
                # Mark as visited and add to group
                visited.add(current_id)
                blocks_in_group.append(current_id)
                
                current_block = self.blocks.get(current_id)
                if not current_block:
                    continue
                
                # Traverse to connected rails
                # When we hit a turnout in next_rails or prev_rails,
                # we'll skip it (boundary) but continue searching other directions
                for next_id in current_block.next_rails:
                    if next_id not in visited:
                        stack.append(next_id)
                        
                for prev_id in current_block.prev_rails:
                    if prev_id not in visited:
                        stack.append(prev_id)
            
            # Add all blocks to the group
            if blocks_in_group:
                for bid in blocks_in_group:
                    self.add_rail_to_group(bid, group_id)
            else:
                # No blocks in group, remove the empty group
                del self.groups[group_id]
        
        # Validate groups after creation
        try:
            self._validate_groups()
        except ValueError as e:
            # Validation failed - clean up groups and block IDs
            for block in self.blocks.values():
                block.group_id = None
                block.block_id = None  # Clear block IDs from failed attempt
            self.groups.clear()
            # Re-raise the error
            raise
    
    def _validate_groups(self):
        """Validate that all blocks in groups are properly connected"""
        errors = []
        warnings = []
        
        # First, check if all blocks are in groups
        blocks_in_groups = set()
        for group in self.groups.values():
            blocks_in_groups.update(group.rail_ids)
        
        ungrouped_blocks = set(self.blocks.keys()) - blocks_in_groups
        if ungrouped_blocks:
            for block_id in ungrouped_blocks:
                block = self.blocks[block_id]
                errors.append(
                    f"❌ Block '{block_id}' ({block.type}) is NOT in any group!\n"
                    f"   This usually means it has no connections or is isolated.\n"
                    f"   → Action: Connect it to other rails or delete it."
                )
        
        # Then validate each group
        for group_id, group in self.groups.items():
            if not group.rail_ids:
                continue
            
            # Check each block in the group
            for rail_id in group.rail_ids:
                if rail_id not in self.blocks:
                    continue
                
                block = self.blocks[rail_id]
                
                # Count connections within this group
                connections_in_group = []
                for next_id in block.next_rails:
                    if next_id in group.rail_ids:
                        connections_in_group.append(next_id)
                
                for prev_id in block.prev_rails:
                    if prev_id in group.rail_ids:
                        connections_in_group.append(prev_id)
                
                # Check if block is isolated (no connections at all)
                total_connections = len(block.next_rails) + len(block.prev_rails)
                next_count = len(block.next_rails)
                prev_count = len(block.prev_rails)
                
                if total_connections == 0:
                    errors.append(
                        f"❌ Block '{rail_id}' ({block.type}) in group '{group_id}' has NO connections!\n"
                        f"   It is completely isolated.\n"
                        f"   next_rails: {block.next_rails} (empty)\n"
                        f"   prev_rails: {block.prev_rails} (empty)\n"
                        f"   → Action: Connect it to other rails or delete it.\n"
                        f"   → Hint: Drag red connection dots together to connect."
                    )
                
                # Check next/prev structure for blocks in multi-block groups
                elif len(group.rail_ids) > 1:
                    # For groups with multiple blocks, check proper connectivity
                    if len(connections_in_group) == 0:
                        # Already handled below, but this is a structural issue
                        pass
                    elif len(connections_in_group) == 1:
                        # Terminus block (start or end) - should have only next OR prev within group
                        # This is OK - it's a valid end point
                        pass
                    elif len(connections_in_group) >= 2:
                        # Middle block - should have proper next/prev structure
                        # Check if it has both next and prev connections within group
                        has_next_in_group = any(nid in group.rail_ids for nid in block.next_rails)
                        has_prev_in_group = any(pid in group.rail_ids for pid in block.prev_rails)
                        
                        if not has_next_in_group and not has_prev_in_group:
                            errors.append(
                                f"❌ Block '{rail_id}' ({block.type}) in group '{group_id}' has broken next/prev structure!\n"
                                f"   Connected to {len(connections_in_group)} blocks but neither as next nor prev.\n"
                                f"   next_rails: {block.next_rails}\n"
                                f"   prev_rails: {block.prev_rails}\n"
                                f"   → This indicates a connection logic error.\n"
                                f"   → Try disconnecting and reconnecting this block."
                            )
                
                # Check if block is connected within the group
                elif len(connections_in_group) == 0 and len(group.rail_ids) > 1:
                    # Show which blocks it IS connected to (outside the group)
                    external_connections = []
                    for next_id in block.next_rails:
                        if next_id not in group.rail_ids:
                            external_connections.append(next_id)
                    for prev_id in block.prev_rails:
                        if prev_id not in group.rail_ids:
                            external_connections.append(prev_id)
                    
                    if external_connections:
                        conn_str = ", ".join(external_connections)
                        errors.append(
                            f"❌ Block '{rail_id}' ({block.type}) is connected to blocks outside its group!\n"
                            f"   Connected to: {conn_str}\n"
                            f"   Group '{group_id}' has {len(group.rail_ids)} blocks but '{rail_id}' is isolated within it.\n"
                            f"   → This indicates the grouping algorithm found a problem.\n"
                            f"   → Try connecting all rails properly and run Auto-Create Groups again."
                        )
                    else:
                        errors.append(
                            f"❌ Block '{rail_id}' ({block.type}) in group '{group_id}' has no internal connections!\n"
                            f"   → Action: Connect it to other blocks in the group."
                        )
                
                # Warning for terminus blocks (only 1 connection in large groups)
                elif len(connections_in_group) == 1 and len(group.rail_ids) > 2:
                    # This is OK for terminus blocks, but let's track it
                    pass
        
        # Additional check: Validate bidirectional connections
        # Important: Handle ALL 4 connection types correctly:
        # 1. end→start: A.next=[B] AND B.prev=[A]
        # 2. start←end: A.prev=[B] AND B.next=[A]
        # 3. start↔start: A.prev=[B] AND B.prev=[A] (both in prev!)
        # 4. end↔end: A.next=[B] AND B.next=[A] (both in next!)
        
        for block_id, block in self.blocks.items():
            # Check next_rails consistency
            for next_id in block.next_rails:
                if next_id in self.blocks:
                    next_block = self.blocks[next_id]
                    # Valid cases:
                    # 1. Normal: block_id in next_block.prev_rails (end→start)
                    # 2. End-to-End: block_id in next_block.next_rails (both pointing toward each other)
                    if block_id not in next_block.prev_rails and block_id not in next_block.next_rails:
                        errors.append(
                            f"❌ Connection inconsistency: '{block_id}' → '{next_id}'\n"
                            f"   '{block_id}' has '{next_id}' in next_rails\n"
                            f"   BUT '{next_id}' has '{block_id}' in neither prev_rails nor next_rails!\n"
                            f"   {next_id}.prev_rails: {next_block.prev_rails}\n"
                            f"   {next_id}.next_rails: {next_block.next_rails}\n"
                            f"   → This is a data corruption issue.\n"
                            f"   → Try disconnecting and reconnecting these blocks."
                        )
            
            # Check prev_rails consistency
            for prev_id in block.prev_rails:
                if prev_id in self.blocks:
                    prev_block = self.blocks[prev_id]
                    # Valid cases:
                    # 1. Normal: block_id in prev_block.next_rails (start←end)
                    # 2. Start-to-Start: block_id in prev_block.prev_rails (both pointing away from each other)
                    if block_id not in prev_block.next_rails and block_id not in prev_block.prev_rails:
                        errors.append(
                            f"❌ Connection inconsistency: '{prev_id}' → '{block_id}'\n"
                            f"   '{block_id}' has '{prev_id}' in prev_rails\n"
                            f"   BUT '{prev_id}' has '{block_id}' in neither next_rails nor prev_rails!\n"
                            f"   {prev_id}.next_rails: {prev_block.next_rails}\n"
                            f"   {prev_id}.prev_rails: {prev_block.prev_rails}\n"
                            f"   → This is a data corruption issue.\n"
                            f"   → Try disconnecting and reconnecting these blocks."
                        )
        
        # Raise errors if found
        if errors:
            error_msg = "❌ GROUP VALIDATION ERRORS:\n\n" + "\n\n".join(errors)
            raise ValueError(error_msg)
        
        if warnings:
            print("⚠️  GROUP VALIDATION WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
    
    def clear(self):
        """Clear all blocks and groups from the system"""
        self.blocks.clear()
        self.groups.clear()
        self._next_id = 1
        self._next_group_id = 1
        self.system_cleared.emit()
        
    def to_json(self) -> dict:
        """Export system to JSON format"""
        return {
            'version': '1.0',
            'next_id': self._next_id,
            'next_group_id': self._next_group_id,
            'blocks': {
                block_id: block.to_dict() 
                for block_id, block in self.blocks.items()
            },
            'groups': {
                group_id: group.to_dict()
                for group_id, group in self.groups.items()
            }
        }
        
    def load_from_json(self, data: dict):
        """Load system from JSON format"""
        self.clear()
        
        if 'next_id' in data:
            self._next_id = data['next_id']
            
        if 'next_group_id' in data:
            self._next_group_id = data['next_group_id']
            
        if 'blocks' in data:
            # Load all blocks
            for block_id, block_data in data['blocks'].items():
                block = RailBlock.from_dict(block_data)
                self.blocks[block_id] = block
                self.block_added.emit(block_id)
                
        if 'groups' in data:
            # Load all groups
            for group_id, group_data in data['groups'].items():
                group = RailGroup.from_dict(group_data)
                self.groups[group_id] = group
                self.group_created.emit(group_id)

