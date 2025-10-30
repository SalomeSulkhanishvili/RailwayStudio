# Changes Summary - All 6 Issues Fixed

## ✅ Issue 1: Curved Rails Now 30 Degrees
- **Changed**: Curved rails now use 30-degree angle instead of 90 degrees
- **Updated**: Connection points match the 30-degree endpoint
- **Applied to**: Curved rails, switch left, and switch right (diverging tracks)
- **Formula**: `end_x = length * cos(30°)`, `end_y = length * sin(30°)`

## ✅ Issue 2: JSON Loading Error Fixed
- **Added**: Proper error handling with detailed traceback
- **Added**: Support for both old and new JSON formats (backward compatibility)
- **Detection**: Automatically detects if JSON has "blockGroups" (new) or "blocks" (old)
- **Error messages**: Now show full error details for debugging

## ✅ Issue 3: New JSON Format with BlockGroups
- **Created**: `core/json_formatter.py` - handles conversion to/from blockGroups format
- **Structure**: Matches your exact specification:
  - `blockGroups`: Groups of connected rails
  - `turnouts`: Switch/turnout connections
  - `metadata`: System metadata
  
### New JSON Structure:
```json
{
  "blockGroups": {
    "BG001": {
      "id": "BG001",
      "description": "Main Line Section 1",
      "blocks": [
        {
          "id": "BL001001",
          "description": "Block BL001001 (straight)",
          "axleCounter": "AC001001",
          "signals": [
            {"id": "SG001001_F", "direction": 0},
            {"id": "SG001002_B", "direction": 1}
          ],
          "grid_pos": [4, 5]
        }
      ],
      "direction": "Forward",
      "start_block_id": "BL001001",
      "end_block_id": "BL001002",
      "last_block_axleCounter": "AC001003"
    }
  },
  "turnouts": {
    "groups": [
      {
        "id": "TG000001",
        "heads": [{"id": "BL001001"}],
        "tails": [{"id": "BL002001"}, {"id": "BL003001"}]
      }
    ]
  },
  "metadata": {
    "next_block_id": "BL004001",
    "next_group_id": "BG004",
    "app_mode": "SetConnections",
    "last_updated": "2025-10-23T...",
    "version": "1.0.0"
  }
}
```

## ✅ Issue 4: Auto-Snap Connected Rails
- **Added**: `snap_rails_together()` method in ConnectionPointItem
- **Behavior**: When you drag a connection point to another, the rails automatically snap together perfectly
- **Result**: Connection points align exactly - no need to manually position rails

### How it works:
1. User drags connection point A toward connection point B
2. Points connect when within 20 pixels
3. **AUTO-SNAP**: Rail A automatically moves so point A aligns perfectly with point B
4. Rails are now perfectly connected

## ✅ Issue 5: Visual Artifacts Fixed
- **Fixed**: Added `scene().update()` call when item position changes
- **Result**: No more "ghost" images or color trails when moving rails
- **Implementation**: Force scene redraw during `ItemPositionChange` event

## ✅ Issue 6: Auto-Generate Axle Counters and Signals
- **Every block automatically gets**:
  - **Block ID**: `BL{group}{number}` (e.g., BL001001)
  - **Axle Counter**: `AC{group}{number}` (e.g., AC001001)
  - **Signals**: 
    - Forward signal: `SG{group}{number}_F` (direction: 0)
    - Backward signal: `SG{group}{number}_B` (direction: 1)
  - **Grid Position**: Calculated from x, y coordinates
  
- **Groups get**:
  - Last block axle counter for the section
  - Start and end block IDs
  - Direction (Forward)

- **Turnouts**: Automatically detected from switch rails
  - ID: `TG{number}`
  - Heads: Incoming connection blocks
  - Tails: Outgoing connection blocks

## How to Use the New System

### Creating a Layout:
1. Build your railway layout as before
2. Connect rails (they auto-snap!)
3. Click "Auto-Create Groups" button
4. Save → Automatically generates blockGroups JSON with all IDs

### JSON Format:
- **Save**: Always saves in new blockGroups format with axle counters
- **Load**: Can load BOTH old format and new blockGroups format
- **IDs are auto-generated**: BL, AC, SG, TG, BG all created automatically

### Example Workflow:
```bash
# 1. Run the app
python main.py

# 2. Build layout in Editor mode
# 3. Connect rails (they snap together automatically)
# 4. Click "Auto-Create Groups"
# 5. Save → get blockGroups JSON

# 6. The JSON will have:
#    - All blocks with unique BL IDs
#    - Axle counters (AC IDs) for each block
#    - Signals (SG IDs) for forward/backward
#    - Turnout groups (TG IDs) for switches
#    - Block groups (BG IDs) for sections
```

## Files Modified/Created:

### Created:
- `core/json_formatter.py` - New JSON format handler

### Modified:
- `ui/rail_graphics.py`:
  - 30-degree curves
  - Auto-snap functionality
  - Visual artifacts fix
  
- `core/railway_system.py`:
  - Added block_id, axle_counter, signals fields
  
- `ui/main_window.py`:
  - Integrated JSON formatter
  - Better error handling
  - Format detection

## Testing:
1. Create a simple layout with 3 rails
2. Connect them (watch them snap!)
3. Click "Auto-Create Groups"
4. Save the file
5. Open the JSON - see blockGroups format!
6. Load it back - everything restores perfectly

All 6 issues are now resolved! 🎉

