# TCP Quick Start Guide

Get your Docker container connected to RailwayStudio in 5 minutes.

## Prerequisites

- RailwayStudio installed and running
- A railway layout loaded with Block Groups created (click "Auto-Create Groups" in Editor)
- Docker container on the same PC

## Step 1: Start TCP Server

1. Open RailwayStudio → **Monitor** tab
2. Click **"Load Layout"** and select your `.json` layout file
3. Set your TCP port (default: 5555) and bind address (default: 0.0.0.0)
4. Click **"Start Server"**
5. **Note the IP address** shown in "Connect from Docker using:" (e.g., `192.168.1.100:5555`)

## Step 2: Get Your Block IDs

Block IDs are in format `BL001001`, `BL002001`, etc.

**Option A - From UI:**
- Block IDs are displayed above each rail in the Editor/Monitor views

**Option B - From JSON:**
```bash
# Extract all Block IDs from your layout
cd examples
python extract_block_ids.py ../layouts/your_layout.json
```

**Option C - From Layout File:**
```json
"blockGroups": [
  {
    "blocks": [
      {"blockId": "BL001001", ...},
      {"blockId": "BL001002", ...}
    ]
  }
]
```

## Step 3: Connect from Docker

### Python Example

```python
import socket
import json

# Use the IP from Step 1
HOST = '192.168.1.100'  # Your actual IP from Monitor view
PORT = 5555

# Connect
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Read welcome message
welcome = sock.recv(1024).decode('utf-8')
print(f"Connected: {welcome}")

# Send status update
update = {
    "type": "status_update",
    "block_id": "BL001001",  # Use your Block ID from Step 2
    "status": "blocked"      # free, reserved, blocked, or unknown
}
sock.send((json.dumps(update) + '\n').encode('utf-8'))

# Read response
response = sock.recv(1024).decode('utf-8')
print(f"Response: {response}")

sock.close()
```

### Docker Connection Options

**Option 1: Use actual IP (Recommended)**
```python
sock.connect(('192.168.1.100', 5555))  # From Monitor view
```

**Option 2: Host network mode**
```bash
docker run --network host your-container
```
```python
sock.connect(('localhost', 5555))
```

**Option 3: host.docker.internal (Mac/Windows)**
```python
sock.connect(('host.docker.internal', 5555))
```

## Step 4: Test It

1. Run your Docker container with the code from Step 3
2. Watch the block change color in RailwayStudio Monitor view
3. Check the Network Log for confirmation messages

## Block Statuses

| Status     | Color  | When to Use                |
|------------|--------|----------------------------|
| `free`     | Green  | Block is available         |
| `reserved` | Orange | Block reserved for train   |
| `blocked`  | Red    | Block occupied             |
| `unknown`  | Gray   | Status unknown/error       |

## Batch Updates

Update multiple blocks at once:

```python
batch = {
    "type": "batch_update",
    "updates": [
        {"block_id": "BL001001", "status": "blocked"},
        {"block_id": "BL001002", "status": "reserved"},
        {"block_id": "BL001003", "status": "free"}
    ]
}
sock.send((json.dumps(batch) + '\n').encode('utf-8'))
```

## Troubleshooting

### "Connection refused"
- Make sure TCP server is started (green "Server running" in Monitor)
- Check you're using the correct IP and port
- Verify firewall isn't blocking the connection

### "Block not found"
- Make sure you clicked "Auto-Create Groups" in Editor
- Use Block IDs (BL001001) from your layout, NOT rail IDs (rail_0001)
- Check the Network Log for the exact error

### Docker can't reach host
- Try using the actual IP shown in Monitor view
- On Linux, try `172.17.0.1` (Docker bridge IP)
- On Mac/Windows, try `host.docker.internal`
- Or use `--network host` when running Docker

## Complete Example

See `examples/docker_tcp_client.py` for a full working example with multiple demo modes.

## Next Steps

- Read [TCP_INTEGRATION.md](TCP_INTEGRATION.md) for full protocol details
- Read [MVC_ARCHITECTURE.md](MVC_ARCHITECTURE.md) to understand the codebase
- Modify the example to fit your railway control logic
