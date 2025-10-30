# Railway Editor - Quick Start Guide

## 📂 Layout Files Location

All railway layouts are stored in the **`layouts/`** folder in the project root. 

The application automatically:
- Creates this folder on first run
- Opens to this folder in the Files view
- Saves new layouts to this folder by default

This keeps all your railway layouts organized in one place!

## Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Key Features Added

### 1. **Improved Curved Rails**
- Curved rails now display as actual smooth curves using quadratic Bezier paths
- More realistic railway appearance with proper sleepers (ties)

### 2. **Drag-to-Connect Rails**
- **Draggable connection points**: Red dots (unconnected) and green dots (connected)
- **How to connect**: Drag a connection point close to another connection point (within 20 pixels)
- **Auto-snap**: Connection points automatically snap back to their position after connecting
- **Visual feedback**: Green dashed lines show connections between rails

### 3. **Disconnect Rails**
- **Double-click** any connection point to disconnect it
- All connected rails update automatically

### 4. **Linked-List Structure**
- Each rail knows its **next** and **previous** rails
- Connections automatically build the linked list
- Right-click a rail to see its next/prev rails in the context menu

### 5. **Rail Groups/Sections**
- Click **"Auto-Create Groups"** button to automatically organize connected rails into groups
- Groups represent logical sections (e.g., from turnout to turnout)
- Each rail stores its group membership
- Groups are saved in JSON format

## Usage Workflow

### Building a Railway Layout

1. **Add Rails**:
   - Select rail type (Straight, Curved, Switch)
   - Set length
   - Click on canvas to place

2. **Position Rails**:
   - Drag rails to move them
   - Right-click → Rotate 90° to rotate

3. **Connect Rails**:
   - Find the red connection points (dots) on each rail
   - Drag one connection point near another
   - They will auto-connect (turn green) when close enough
   - Green dashed lines show the connection

4. **Create Groups**:
   - After connecting rails, click "Auto-Create Groups"
   - This organizes your layout into logical sections

5. **Save Layout**:
   - File → Save Layout (or Ctrl+S)
   - Saves everything: rails, connections, groups, linked-list structure

### JSON Structure Example

```json
{
  "version": "1.0",
  "next_id": 5,
  "next_group_id": 2,
  "blocks": {
    "rail_0001": {
      "id": "rail_0001",
      "type": "straight",
      "x": 100.0,
      "y": 200.0,
      "rotation": 0,
      "length": 100,
      "color": "#888888",
      "connections": {
        "start": null,
        "end": ["rail_0002", "start"]
      },
      "next_rails": ["rail_0002"],
      "prev_rails": [],
      "group_id": "group_0001"
    },
    "rail_0002": {
      "id": "rail_0002",
      "type": "curved",
      "x": 200.0,
      "y": 200.0,
      "rotation": 0,
      "length": 100,
      "color": "#888888",
      "connections": {
        "start": ["rail_0001", "end"],
        "end": null
      },
      "next_rails": [],
      "prev_rails": ["rail_0001"],
      "group_id": "group_0001"
    }
  },
  "groups": {
    "group_0001": {
      "id": "group_0001",
      "name": "Section 1",
      "rail_ids": ["rail_0001", "rail_0002"],
      "color": "#888888"
    }
  }
}
```

## Monitoring Mode

1. **Switch to Monitor Mode**
2. **Start Listening** on UDP port 5000
3. **Send packets** to update train positions:

```bash
# Update rail color (shows train position)
echo '{"block_id":"rail_0001","color":"red"}' | nc -u localhost 5000

# Or simple format
echo 'rail_0001:green' | nc -u localhost 5000
```

## Tips

- **Connection order matters**: Connect `end` → `start` for proper linked-list order
- **Use groups** to manage sections (e.g., track sections between signals)
- **Groups are perfect** for controlling entire sections (e.g., color a whole section when a train enters)
- **Save often** - layouts with many connections take time to build!

## Troubleshooting

**Connection points won't connect?**
- Make sure you're dragging close enough (< 20 pixels)
- Try zooming in for precision

**Rails won't move?**
- Click on the rail itself, not the connection points
- Connection points are for connecting only

**Groups not created?**
- Make sure rails are connected first
- Groups follow the linked-list structure

Enjoy building your railway! 🚂

