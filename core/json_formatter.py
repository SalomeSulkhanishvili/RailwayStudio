"""
JSON Formatter - Converts railway system to/from blockGroups format
"""

from typing import Dict, List, Set
from datetime import datetime
from core.railway_system import RailwaySystem, RailBlock


class RailwayJSONFormatter:
    """Handles conversion to/from blockGroups JSON format"""
    
    def __init__(self, railway_system: RailwaySystem):
        self.railway_system = railway_system
        self.block_counter = 1
        self.group_counter = 1
        self.ac_counter = 1
        self.turnout_counter = 1
        
    def to_blockgroups_json(self) -> dict:
        """Export to blockGroups JSON format with axle counters and signals"""
        # First, auto-create groups based on current connections
        self.railway_system.auto_create_groups()
            
        block_groups = {}
        turnout_groups = []
        block_id_mapping = {}  # Map rail_id to BL_id
        
        # Process each group
        for group_id, group in self.railway_system.groups.items():
            bg_id = f"BG{self.group_counter:03d}"
            self.group_counter += 1
            
            blocks_in_group = []
            
            # Process each rail in the group
            for rail_id in group.rail_ids:
                if rail_id not in self.railway_system.blocks:
                    continue
                    
                rail = self.railway_system.blocks[rail_id]
                
                # Generate block ID and assign it to the rail immediately
                bl_id = f"BL{self.group_counter-1:03d}{self.block_counter:03d}"
                self.block_counter += 1
                block_id_mapping[rail_id] = bl_id
                
                # Assign the block ID to the rail so it shows in editor
                rail.block_id = bl_id
                
                # Generate axle counter ID and assign it
                ac_id = f"AC{self.group_counter-1:03d}{self.ac_counter:03d}"
                self.ac_counter += 1
                rail.axle_counter = ac_id
                
                # Create block with axle counter and signals
                block_data = {
                    "id": bl_id,
                    "description": f"Block {bl_id} ({rail.type})",
                    "axleCounter": ac_id,
                    "signals": [
                        {
                            "id": f"SG{self.group_counter-1:03d}{len(blocks_in_group)+1:03d}_F",
                            "direction": 0  # Forward
                        },
                        {
                            "id": f"SG{self.group_counter-1:03d}{len(blocks_in_group)+1:03d}_B",
                            "direction": 1  # Backward
                        }
                    ],
                    "grid_pos": [int(rail.x / 100), int(rail.y / 100)],
                    # Store original data for reconstruction
                    "_original": {
                        "rail_id": rail_id,
                        "type": rail.type,
                        "x": rail.x,
                        "y": rail.y,
                        "rotation": rail.rotation,
                        "length": rail.length,
                        "color": rail.color
                    }
                }
                
                blocks_in_group.append(block_data)
                
            # Reset block counter for next group
            self.block_counter = 1
            self.ac_counter = 1
            
            if blocks_in_group:
                # Generate last axle counter for the group
                last_ac_id = f"AC{self.group_counter-1:03d}{len(blocks_in_group)+1:03d}"
                
                # Find the actual start and end blocks (terminus points)
                # Start: block with no prev_rails (or fewest connections to prev)
                # End: block with no next_rails (or fewest connections to next)
                start_rail_id = None
                end_rail_id = None
                
                # Find terminus blocks (blocks at the ends of the chain)
                terminus_blocks = []
                for rail_id in group.rail_ids:
                    if rail_id in self.railway_system.blocks:
                        rail = self.railway_system.blocks[rail_id]
                        # Count connections within this group only
                        prev_count = sum(1 for r in rail.prev_rails if r in group.rail_ids)
                        next_count = sum(1 for r in rail.next_rails if r in group.rail_ids)
                        total_conn = prev_count + next_count
                        
                        # Terminus: only 1 connection within the group
                        if total_conn <= 1:
                            terminus_blocks.append((rail_id, prev_count, next_count))
                
                # Assign start and end based on terminus blocks
                if len(terminus_blocks) >= 2:
                    # Pick one with no prev as start, one with no next as end
                    for rail_id, prev_count, next_count in terminus_blocks:
                        if prev_count == 0 and start_rail_id is None:
                            start_rail_id = rail_id
                        if next_count == 0 and end_rail_id is None:
                            end_rail_id = rail_id
                
                # Fallback: use first and last in the list
                if start_rail_id is None:
                    start_rail_id = group.rail_ids[0] if group.rail_ids else None
                if end_rail_id is None:
                    end_rail_id = group.rail_ids[-1] if group.rail_ids else None
                
                # Map to block IDs
                start_block_id = block_id_mapping.get(start_rail_id) if start_rail_id else None
                end_block_id = block_id_mapping.get(end_rail_id) if end_rail_id else None
                
                block_groups[bg_id] = {
                    "id": bg_id,
                    "description": group.name or f"Section {self.group_counter-1}",
                    "blocks": blocks_in_group,
                    "direction": "Forward",
                    "start_block_id": start_block_id,
                    "end_block_id": end_block_id,
                    "last_block_axleCounter": last_ac_id
                }
                
        # Find turnouts (switches)
        turnouts = self._find_turnouts(block_id_mapping)
        
        # Store legacy data for connection restoration
        legacy_data = self.railway_system.to_json()
        
        return {
            "blockGroups": block_groups,
            "turnouts": {
                "groups": turnouts
            },
            "metadata": {
                "next_block_id": f"BL{self.group_counter:03d}001",
                "next_group_id": f"BG{self.group_counter:03d}",
                "app_mode": "SetConnections",
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0",
                "_legacy_data": legacy_data  # Store original connections
            }
        }
        
    def _find_turnouts(self, block_id_mapping: Dict[str, str]) -> List[dict]:
        """Find turnout/switch points in the railway system"""
        turnouts = []
        turnout_id_counter = 1
        
        for rail_id, rail in self.railway_system.blocks.items():
            # A turnout is a switch rail with multiple connections
            if rail.type in ['switch_left', 'switch_right']:
                heads = []
                tails = []
                
                # Get connections
                for point, conn in rail.connections.items():
                    if conn:
                        conn_rail_id, conn_point = conn
                        bl_id = block_id_mapping.get(conn_rail_id)
                        if bl_id:
                            if 'start' in point:
                                heads.append({"id": bl_id})
                            else:
                                tails.append({"id": bl_id})
                                
                if heads or tails:
                    turnout_data = {
                        "id": f"TG{turnout_id_counter:06d}",
                        "heads": heads,
                        "tails": tails,
                        "_switch_rail_id": rail_id  # Store for reconstruction
                    }
                    turnouts.append(turnout_data)
                    turnout_id_counter += 1
                    
        return turnouts
        
    def _restore_connections_from_legacy(self, legacy_data: dict):
        """Restore connections from legacy data"""
        if "blocks" not in legacy_data:
            return
            
        # Create mapping from old IDs to new IDs
        old_to_new = {}
        for new_id, rail in self.railway_system.blocks.items():
            if hasattr(rail, '_temp_original_id'):
                old_to_new[rail._temp_original_id] = new_id
        
        # Restore connections
        for old_id, block_data in legacy_data["blocks"].items():
            if old_id not in old_to_new:
                continue
                
            new_id = old_to_new[old_id]
            rail = self.railway_system.blocks[new_id]
            
            # Restore connections
            if "connections" in block_data:
                for point, conn in block_data["connections"].items():
                    if conn and len(conn) == 2:
                        conn_old_id, conn_point = conn
                        if conn_old_id in old_to_new:
                            conn_new_id = old_to_new[conn_old_id]
                            # Only connect if not already connected (avoid duplicates)
                            if rail.connections.get(point) is None:
                                self.railway_system.connect_blocks(new_id, point, conn_new_id, conn_point)
        
        # Clean up temporary IDs
        for rail in self.railway_system.blocks.values():
            if hasattr(rail, '_temp_original_id'):
                delattr(rail, '_temp_original_id')
    
    def from_blockgroups_json(self, data: dict):
        """Load from blockGroups JSON format"""
        self.railway_system.clear()
        
        if "blockGroups" not in data:
            raise ValueError("Invalid JSON format: missing 'blockGroups'")
            
        # Reconstruct rails from block groups
        for bg_id, bg_data in data["blockGroups"].items():
            # Create a group
            group_id = self.railway_system.create_group(bg_data.get("description", bg_id))
            
            for block_data in bg_data.get("blocks", []):
                # Get original rail data if available
                original = block_data.get("_original", {})
                
                if original:
                    # Reconstruct rail with original data
                    rail_type = original.get("type", "straight")
                    x = original.get("x", block_data["grid_pos"][0] * 100)
                    y = original.get("y", block_data["grid_pos"][1] * 100)
                    rotation = original.get("rotation", 0)
                    length = original.get("length", 100)
                    color = original.get("color", "#888888")
                    
                    rail_id = self.railway_system.add_block(rail_type, x, y, rotation, length)
                    rail = self.railway_system.blocks[rail_id]
                    rail.color = color
                    
                    # Store block metadata
                    rail.block_id = block_data["id"]
                    rail.axle_counter = block_data.get("axleCounter")
                    rail.signals = block_data.get("signals", [])
                    
                    # Store the original rail_id for connection restoration
                    rail._temp_original_id = original.get("rail_id")
                    
                    # Don't add to group yet - will be done after connections are restored
                else:
                    # Create from grid position
                    x = block_data["grid_pos"][0] * 100
                    y = block_data["grid_pos"][1] * 100
                    rail_id = self.railway_system.add_block("straight", x, y, 0, 100)
                    
                    # Store metadata
                    rail = self.railway_system.blocks[rail_id]
                    rail.block_id = block_data["id"]
                    rail.axle_counter = block_data.get("axleCounter")
                    rail.signals = block_data.get("signals", [])
        
        # Now restore connections from the old format data if available
        if "metadata" in data and "_legacy_data" in data["metadata"]:
            legacy_data = data["metadata"]["_legacy_data"]
            self._restore_connections_from_legacy(legacy_data)
        
        # After restoring connections, recreate groups properly
        self.railway_system.auto_create_groups()

