# TCP Integration Quick Start Guide

Get your Docker containers communicating with RailwayStudio in 5 minutes!

## Setup (One-Time)

### 1. Start RailwayStudio

```bash
cd /path/to/railwayStudio
python3 main.py
```

### 2. Prepare Railway Layout

1. Click **"Editor"** in the sidebar
2. Design railway layout or load an existing one
3. Click **"Auto-Create Groups"** to generate external Block IDs (`BL001001`, `BL001002`, etc.)
4. **Save the layout** to a JSON file
5. **Important**: Note the Block IDs displayed above each rail segment
   - These are the external IDs in format `BL00X00X`
   - These are also in your exported JSON file
   - **Use these IDs in your Docker container**, not the internal `rail_00XX` IDs

### 3. Start the TCP Server

1. Click **"Monitor"** in the sidebar
2. Set the TCP port (default: 5555)
3. Click **"▶ Start Server"**
4. Status should show: "● Server running on port 5555"

## Test the Connection

### From Host Machine (Quick Test)

```bash
cd railwayStudio
python3 examples/docker_tcp_client.py
```

You should see:
- Console output showing connection success
- Block colors changing in the Monitor view
- Network log showing received updates

### From Docker Container

#### Option 1: Using the Example Script

```bash
# Copy example to your container
docker cp examples/docker_tcp_client.py your_container:/app/

# Run it
docker exec your_container python3 /app/docker_tcp_client.py
```

#### Option 2: Integrate in Your Code

```python
import socket
import json

# Connect to RailwayStudio on host
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Choose the right host for your OS:
# - Mac/Windows Docker: 'host.docker.internal'
# - Linux Docker: '172.17.0.1'
# - Host network mode: 'localhost'
sock.connect(('host.docker.internal', 5555))

# Send block status update
# IMPORTANT: Use external Block IDs (BL00X00X format)
update = {
    "type": "status_update",
    "block_id": "BL001001",  # Use BL IDs from your JSON layout file
    "status": "blocked"
}
sock.send((json.dumps(update) + '\n').encode('utf-8'))

# Close
sock.close()
```

## Finding Your Block IDs

After creating groups in the Editor:

1. **Visual**: Look at the railway layout - Block IDs are displayed above each rail
2. **JSON File**: Open your saved layout file and find the `blockGroups` section:
   ```json
   "blockGroups": [
     {
       "groupId": "G001",
       "blocks": [
         {"blockId": "BL001001", ...},
         {"blockId": "BL001002", ...}
       ]
     }
   ]
   ```
3. **Use these `BL00X00X` IDs** in your Docker TCP messages

## Block Status Values

Send one of these status values:

| Status      | Color   | Use Case                    |
|-------------|---------|----------------------------|
| `"free"`    | Green   | Block is available          |
| `"reserved"`| Orange  | Block reserved for train    |
| `"blocked"` | Red     | Block occupied by train     |
| `"unknown"` | Gray    | Status cannot be determined |

## Message Format

### Single Block Update

```json
{
  "type": "status_update",
  "block_id": "BL001001",
  "status": "blocked"
}
```

**Use External Block IDs**: Use the `BL00X00X` format (not `rail_00XX`). These are the IDs visible in your railway layout and exported in JSON files.

### Multiple Blocks (Batch)

```json
{
  "type": "batch_update",
  "updates": [
    {"block_id": "BL001001", "status": "blocked"},
    {"block_id": "BL001002", "status": "reserved"},
    {"block_id": "BL001003", "status": "free"}
  ]
}
```

**Important**: 
- Each JSON message must end with `\n` (newline)!
- Use **external Block IDs** (`BL001001`) that match your JSON layout file
- Internal IDs (`rail_0001`) also work but are not recommended

## Docker Network Configuration

### Recommended: Host Network Mode

Simplest approach - container shares host network:

```bash
docker run --network host your-image
# Connect to localhost:5555 from inside container
```

### Alternative: Bridge Network (Default)

Container on separate network:

**Mac/Windows:**
```python
sock.connect(('host.docker.internal', 5555))
```

**Linux:**
```python
sock.connect(('172.17.0.1', 5555))  # Docker bridge gateway
```

## Troubleshooting

### "Connection refused"

✅ **Check:**
1. RailwayStudio is running
2. Monitor view is open
3. TCP server is started (green status)
4. Port number matches (default: 5555)
5. Firewall allows connection

### "Block not found"

✅ **Check:**
1. Layout is loaded in Monitor view
2. You ran "Auto-Create Groups" in Editor (this generates BL IDs)
3. Block ID matches exactly (case-sensitive): use `BL001001` not `bl001001`
4. The Block ID exists in your loaded layout (check the JSON file or look at the rails in Monitor view)
5. Check Network Log in Monitor view for the exact error message

### No visual update

✅ **Check:**
1. Status value is valid: `free`, `reserved`, `blocked`, or `unknown`
2. JSON format is correct (use a JSON validator)
3. Message ends with `\n` (newline)
4. Check Network Log for errors

### Docker can't connect to host

✅ **Try:**

**Mac/Windows:**
```python
sock.connect(('host.docker.internal', 5555))
```

**Linux:**
```python
sock.connect(('172.17.0.1', 5555))
```

**Or use host network:**
```bash
docker run --network host your-image
```

## Real-World Integration

### From Your Railway Controller

```python
import socket
import json
import time

class RailwayStudioClient:
    def __init__(self, host='host.docker.internal', port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        
    def update_block(self, block_id, status):
        msg = {"type": "status_update", "block_id": block_id, "status": status}
        self.sock.send((json.dumps(msg) + '\n').encode('utf-8'))
    
    def close(self):
        self.sock.close()

# Use in your railway logic
# IMPORTANT: Load Block IDs from your JSON layout file
studio = RailwayStudioClient()

# When train enters block (use BL IDs from your layout)
studio.update_block("BL001001", "blocked")

# When train leaves block
studio.update_block("BL001001", "free")

# When reserving block
studio.update_block("BL001002", "reserved")

studio.close()
```

### Continuous Monitoring Loop

```python
import time

studio = RailwayStudioClient()

try:
    while True:
        # Read block statuses from your microcontrollers
        block_status = read_from_microcontroller()
        
        # Send to RailwayStudio
        studio.update_block(block_status['id'], block_status['status'])
        
        time.sleep(0.1)  # 10 updates/second
        
except KeyboardInterrupt:
    studio.close()
```

## Next Steps

📚 **Read the full documentation:**
- [TCP Integration Guide](TCP_INTEGRATION.md) - Complete protocol reference
- [Usage Guide](USAGE.md) - How to use RailwayStudio

🔧 **Customize:**
- Modify `examples/docker_tcp_client.py` for your needs
- Integrate the client class into your existing code
- Add error handling and reconnection logic

💡 **Tips:**
- Use batch updates for better performance
- Keep the connection open (don't reconnect for each update)
- Handle disconnections gracefully
- Add logging for debugging

## Support

Having issues? Check:
1. [TCP Integration Guide](TCP_INTEGRATION.md) - Detailed troubleshooting
2. [GitHub Issues](https://github.com/your-repo/issues) - Report bugs
3. Network Log in RailwayStudio Monitor view - See what's being received

Happy railway monitoring! 🚂✨

