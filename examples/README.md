# RailwayStudio Examples

This directory contains example scripts for integrating with RailwayStudio.

## Quick Reference: Block IDs

**Important**: Your Docker containers should use **External Block IDs** in the format `BL001001`, `BL001002`, etc.

- ✅ Use: `BL001001` (external Block ID from JSON)
- ❌ Don't use: `rail_0001` (internal Rail ID)

See [Block ID Mapping Guide](../docs/BLOCK_ID_MAPPING.md) for details.

## Extract Block IDs from Layout

### `extract_block_ids.py`

Extract all Block IDs from a railway layout JSON file. This helps you get the correct IDs to use in your Docker containers.

**Usage:**

```bash
# Simple list of Block IDs
python3 extract_block_ids.py ../layouts/first_layout.json

# Detailed information
python3 extract_block_ids.py ../layouts/first_layout.json detailed

# JSON format (for parsing in code)
python3 extract_block_ids.py ../layouts/first_layout.json json

# Python list format
python3 extract_block_ids.py ../layouts/first_layout.json python_list

# Save to file
python3 extract_block_ids.py ../layouts/first_layout.json json > block_ids.json
```

**Example Output (detailed)**:
```
Found 5 blocks:

1. BL001001
   Group: G001
   Rails: 2 (rail_0001 → rail_0002)

2. BL001002
   Group: G001
   Rails: 1 (rail_0003 → rail_0003)
...
```

Use these Block IDs in your TCP messages!

## TCP Client for Docker Containers

### `docker_tcp_client.py`

A complete Python example demonstrating how to send railway block status updates from Docker containers to RailwayStudio.

**Features:**
- Simple status updates (single block)
- Batch updates (multiple blocks)
- Train movement simulation
- Connection testing (ping/pong)
- Automatic Docker environment detection

**Usage:**

```bash
# Run directly on the host
python3 docker_tcp_client.py

# Run from Docker container
docker run -v $(pwd):/app -w /app python:3.9 python docker_tcp_client.py

# Run with custom host/port
python3 docker_tcp_client.py --host localhost --port 5555
```

**Requirements:**
- Python 3.6+
- No external dependencies (uses only standard library)

**Before Running:**
1. Start RailwayStudio
2. Open the Monitor view
3. Load a railway layout
4. Click "Start Server" (default port: 5555)
5. Run the example script

**Output:**
The script will:
1. Connect to RailwayStudio
2. Run 4 demos showing different features
3. Update block colors in real-time
4. Display progress in the terminal

**Customization:**

1. First, extract Block IDs from your layout:
   ```bash
   python3 extract_block_ids.py ../layouts/your_layout.json
   ```

2. Edit the script to use your Block IDs:
   ```python
   # Update these block IDs to match your layout
   # Use BL IDs, not rail IDs!
   blocks = ["BL001001", "BL001002", "BL001003"]

   # Send status updates
   client.send_status_update("BL001001", RailwayStudioClient.STATUS_BLOCKED)
   ```

**Docker Integration:**

From your Docker container's Python code:

```python
import json
from docker_tcp_client import RailwayStudioClient

# Step 1: Load Block IDs from your layout file
with open('/app/railway_layout.json', 'r') as f:
    layout = json.load(f)

# Extract Block IDs
block_ids = []
for group in layout['blockGroups']:
    for block in group['blocks']:
        block_ids.append(block['blockId'])

print(f"Loaded Block IDs: {block_ids}")

# Step 2: Create client and connect
client = RailwayStudioClient(host='host.docker.internal', port=5555)

if client.connect():
    # Step 3: Send updates using the correct Block IDs
    # Example: Update first block to blocked status
    client.send_status_update(block_ids[0], RailwayStudioClient.STATUS_BLOCKED)
    client.disconnect()
```

**See Also:**
- [TCP Integration Guide](../docs/TCP_INTEGRATION.md) - Complete protocol documentation
- [Monitor View Guide](../docs/USAGE.md) - How to use the Monitor view

## Contributing

Have an example to share? Please submit a pull request!

## License

MIT License - See main repository LICENSE file

