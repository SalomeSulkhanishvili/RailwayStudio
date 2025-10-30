# Block ID Mapping Guide

## Understanding Block IDs in RailwayStudio

RailwayStudio uses two types of identifiers for railway blocks:

### 1. Internal Rail IDs (rail_00XX)

**Format**: `rail_0001`, `rail_0002`, `rail_0003`, etc.

**Purpose**: Internal identifiers used by railwayStudio's core system

**Where they appear**:
- In the Python code (RailwaySystem class)
- In memory during runtime
- In debug logs

**Usage**: 
- ❌ **DO NOT use these in your Docker containers**
- They are implementation details
- Not guaranteed to be stable across sessions

### 2. External Block IDs (BL00X00X)

**Format**: `BL001001`, `BL001002`, `BL002001`, etc.

**Purpose**: User-facing identifiers for railway blocks

**Where they appear**:
- Displayed above each rail in Editor/Monitor views
- In JSON export files (blockGroups section)
- In printed documentation

**Usage**:
- ✅ **USE these in your Docker containers**
- These are the official, stable identifiers
- These match your railway system documentation

## Block ID Structure

External Block IDs follow this pattern:

```
BL GGG BBB
│  │   └── Block number within the group (001, 002, 003, ...)
│  └────── Group number (001, 002, 003, ...)
└───────── "BL" prefix (Block)
```

**Example**: `BL001001`
- `BL` = Block identifier
- `001` = Group 1
- `001` = First block in Group 1

**Example**: `BL002003`
- `BL` = Block identifier
- `002` = Group 2
- `003` = Third block in Group 2

## How Block IDs Are Generated

1. **Create Railway Layout** in Editor
   - Place rails (straight, curved, switches)
   - Connect them by dragging red connection dots

2. **Click "Auto-Create Groups"**
   - RailwayStudio analyzes your layout
   - Creates logical groups (sections between turnouts)
   - Assigns Block IDs to each rail segment

3. **Block IDs Appear**
   - Displayed above each rail
   - Saved in JSON export
   - Ready to use in TCP messages

## Getting Block IDs for Your Docker Container

### Method 1: From JSON Layout File

1. Save your layout in Editor
2. Open the JSON file (in `layouts/` folder)
3. Find the `blockGroups` section:

```json
{
  "blockGroups": [
    {
      "groupId": "G001",
      "blocks": [
        {
          "blockId": "BL001001",
          "rails": ["rail_0001", "rail_0002"],
          "startRail": "rail_0001",
          "endRail": "rail_0002"
        },
        {
          "blockId": "BL001002",
          "rails": ["rail_0003"],
          "startRail": "rail_0003",
          "endRail": "rail_0003"
        }
      ]
    }
  ]
}
```

4. **Use the `blockId` values** in your Docker container

### Method 2: Visual Inspection

1. Open Monitor view
2. Load your layout
3. Look at the railway - Block IDs are displayed above each rail
4. Write down the IDs you need

### Method 3: Parse JSON Programmatically

Python example for your Docker container:

```python
import json

# Load layout file
with open('railway_layout.json', 'r') as f:
    layout = json.load(f)

# Extract all Block IDs
block_ids = []
for group in layout['blockGroups']:
    for block in group['blocks']:
        block_id = block['blockId']
        block_ids.append(block_id)
        print(f"Block ID: {block_id}")

# Now use these IDs in TCP messages
# Example: block_ids[0] = "BL001001"
```

## Using Block IDs in TCP Messages

### Correct ✅

```python
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('host.docker.internal', 5555))

# Use External Block ID
update = {
    "type": "status_update",
    "block_id": "BL001001",  # ✅ Correct
    "status": "blocked"
}
sock.send((json.dumps(update) + '\n').encode('utf-8'))
sock.close()
```

### Incorrect ❌

```python
# DON'T do this:
update = {
    "type": "status_update",
    "block_id": "rail_0001",  # ❌ Wrong - internal ID
    "status": "blocked"
}
```

## Mapping Between Internal and External IDs

If you need to understand the relationship:

```json
{
  "blockId": "BL001001",      // External ID (use this)
  "rails": ["rail_0001", "rail_0002"]  // Internal IDs (don't use)
}
```

- One **Block** can contain multiple **Rails**
- Blocks represent logical sections (between turnouts)
- Rails represent individual physical track segments

## Best Practices

1. **Always use External Block IDs** (`BL00X00X`) in your Docker containers
2. **Parse them from the JSON file** - don't hardcode
3. **Validate Block IDs** before sending TCP messages
4. **Handle "Block not found" errors** gracefully
5. **Keep your layout JSON file synced** with your Docker containers

## Example: Complete Docker Integration

```python
import socket
import json

class RailwayController:
    def __init__(self, layout_file, tcp_host='host.docker.internal', tcp_port=5555):
        # Load Block IDs from layout file
        with open(layout_file, 'r') as f:
            self.layout = json.load(f)
        
        self.block_ids = self._extract_block_ids()
        print(f"Loaded {len(self.block_ids)} Block IDs: {self.block_ids}")
        
        # Connect to RailwayStudio
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((tcp_host, tcp_port))
    
    def _extract_block_ids(self):
        """Extract all Block IDs from layout"""
        ids = []
        for group in self.layout.get('blockGroups', []):
            for block in group.get('blocks', []):
                ids.append(block['blockId'])
        return ids
    
    def update_block_status(self, block_id, status):
        """Send block status update"""
        if block_id not in self.block_ids:
            print(f"Warning: Block ID {block_id} not in layout!")
            return False
        
        update = {
            "type": "status_update",
            "block_id": block_id,
            "status": status
        }
        self.sock.send((json.dumps(update) + '\n').encode('utf-8'))
        return True
    
    def close(self):
        self.sock.close()

# Usage
controller = RailwayController('railway_layout.json')

# Now you can use Block IDs confidently
controller.update_block_status("BL001001", "blocked")
controller.update_block_status("BL001002", "reserved")

controller.close()
```

## Summary

| Aspect | Internal Rail IDs | External Block IDs |
|--------|------------------|-------------------|
| Format | `rail_0001` | `BL001001` |
| Purpose | Internal use | User-facing |
| Visibility | Code only | UI + JSON |
| Stability | May change | Stable |
| **Use in Docker** | ❌ No | ✅ Yes |

**Remember**: Always use External Block IDs (`BL00X00X`) in your Docker TCP messages!

