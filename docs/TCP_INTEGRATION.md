# TCP Integration Guide for Docker Containers

This guide explains how to integrate your Docker containers with railwayStudio using TCP communication to send real-time railway block status updates.

## Overview

RailwayStudio includes a built-in TCP server that receives block status updates from external systems (like Docker containers running railway control logic). The server listens for JSON-formatted messages and automatically updates the visual representation of railway blocks based on their status.

## Connection Details

- **Protocol**: TCP
- **Default Port**: 5555 (configurable in the Monitor view)
- **Host**: localhost / 127.0.0.1 (when Docker and railwayStudio are on the same PC)
- **Format**: JSON messages, one per line (newline-delimited)

## Block Status Types

The following status types are supported:

| Status    | Description                          | Color   | Hex Code  |
|-----------|--------------------------------------|---------|-----------|
| `free`    | Block is free/available              | Green   | #48BB78   |
| `reserved`| Block is reserved for a train        | Orange  | #FFA500   |
| `blocked` | Block is occupied/blocked            | Red     | #E53E3E   |
| `unknown` | Block status is unknown              | Gray    | #888888   |

## Message Protocol

### 1. Single Block Status Update

Send a single status update for one block:

```json
{
  "type": "status_update",
  "block_id": "BL001001",
  "status": "blocked"
}
```

**Fields:**
- `type`: Must be `"status_update"` (optional, defaults to this)
- `block_id`: **The external Block ID** (e.g., `BL001001`, `BL001002`)
  - **Recommended**: Use BL IDs from your JSON layout file
  - Internal rail IDs (`rail_0001`) also work but should be avoided
- `status`: One of: `free`, `reserved`, `blocked`, `unknown`

**Response:**
```json
{
  "type": "ack",
  "block_id": "BL001001",
  "status": "received"
}
```

### 2. Batch Status Update

Send multiple status updates in a single message:

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

**Fields:**
- `type`: Must be `"batch_update"`
- `updates`: Array of update objects, each containing `block_id` and `status`

**Response:**
```json
{
  "type": "ack",
  "updates_received": 3,
  "status": "received"
}
```

### 3. Ping/Pong (Connection Testing)

Test the connection:

```json
{
  "type": "ping",
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": 1234567890
}
```

## Message Format Requirements

1. **Newline-Delimited**: Each JSON message must be on a single line, terminated with `\n`
2. **Valid JSON**: Messages must be valid JSON
3. **UTF-8 Encoding**: All messages must be UTF-8 encoded
4. **Persistent Connection**: Keep the TCP connection open for continuous updates

## Connection Flow

1. **Connect**: Client connects to railwayStudio TCP server
2. **Welcome**: Server sends welcome message with client ID and protocol version
3. **Send Updates**: Client sends status updates as needed
4. **Receive ACKs**: Server acknowledges each message
5. **Disconnect**: Client can close connection when done

### Welcome Message

When you first connect, the server sends:

```json
{
  "type": "welcome",
  "message": "Connected to RailwayStudio TCP Server",
  "client_id": "client_1",
  "protocol_version": "1.0"
}
```

## Python Example (for Docker Containers)

See `examples/docker_tcp_client.py` for a complete working example.

### Quick Example

```python
import socket
import json
import time

# Connect to railwayStudio
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5555))

# Read welcome message
welcome = sock.recv(1024).decode('utf-8')
print(f"Connected: {welcome}")

# Send a status update
# IMPORTANT: Use Block IDs (BL00X00X) from your JSON layout file
update = {
    "type": "status_update",
    "block_id": "BL001001",  # External Block ID
    "status": "blocked"
}
message = json.dumps(update) + '\n'
sock.send(message.encode('utf-8'))

# Read acknowledgment
response = sock.recv(1024).decode('utf-8')
print(f"Response: {response}")

# Close connection
sock.close()
```

## Docker Networking

Since Docker and railwayStudio are on the same PC:

### Option 1: Host Network Mode (Simplest)

Run your Docker container with `--network host`:

```bash
docker run --network host your-railway-container
```

Then connect to `localhost:5555` from inside the container.

### Option 2: Bridge Network (Default)

Connect to the host machine's IP:

```python
# From inside Docker container
sock.connect(('host.docker.internal', 5555))  # On Mac/Windows
# OR
sock.connect(('172.17.0.1', 5555))  # On Linux (Docker bridge gateway)
```

### Option 3: Custom Network

Create a custom Docker network and use the host's IP address within that network.

## Block ID Formats

The TCP server accepts two types of block identifiers:

1. **External Block ID** (Recommended): `BL001001`, `BL001002`, etc.
   - These are generated when you run "Auto-Create Groups" in the Editor
   - These IDs appear in your JSON layout file under `blockGroups`
   - These are visible above each rail in the Editor/Monitor views
   - **Use these IDs in your Docker containers**

2. **Internal Rail ID** (Not Recommended): `rail_0001`, `rail_0002`, etc.
   - These are internal identifiers used by railwayStudio
   - Not exposed in JSON exports
   - Should only be used for debugging

The server will automatically search for both formats, but **you should always use External Block IDs (BL00X00X)** in your Docker containers.

### How to Get Block IDs

1. **In the Editor**: Click "Auto-Create Groups" - this generates BL IDs
2. **Visually**: Block IDs are displayed above each rail segment
3. **In JSON**: Open your layout file and look for:
   ```json
   "blockGroups": [
     {
       "groupId": "G001",
       "blocks": [
         {
           "blockId": "BL001001",
           "rails": ["rail_0001", "rail_0002"]
         }
       ]
     }
   ]
   ```
4. **Use the `blockId` values** in your TCP messages

## Error Handling

If the server receives an invalid message, it will:
- Log the error in the Network Log
- **NOT** close the connection
- Continue accepting new messages

Common errors:
- Missing `block_id` or `status` field
- Invalid status value (not one of: free, reserved, blocked, unknown)
- Malformed JSON
- Unknown block ID (block not found in current layout)

## Testing

1. **Start railwayStudio**
2. **Load a layout** in the Monitor view
3. **Click "Start Server"** (default port 5555)
4. **Run the example client** from your Docker container
5. **Watch blocks change color** in real-time

## Troubleshooting

### Connection Refused
- Check that railwayStudio TCP server is running (green "Server running" status)
- Verify the port number matches
- Check firewall settings

### Block Not Found
- Ensure the layout is loaded in railwayStudio Monitor view
- Run "Auto-Create Groups" in Editor to generate BL IDs
- Verify the block_id matches exactly (case-sensitive)
- **Use External Block IDs** (`BL001001`) from your JSON layout file
- Check the Network Log for the exact error message

### No Visual Update
- Check the Network Log for error messages
- Verify the status value is valid
- Ensure the block exists in the current layout

## Performance

- **Batch Updates**: Use batch updates for better performance when updating multiple blocks
- **Keep-Alive**: Maintain a persistent connection rather than reconnecting for each update
- **Rate Limiting**: The server can handle hundreds of updates per second

## Security Note

The TCP server binds to `0.0.0.0` (all interfaces) by default. If you need to restrict access:
- Use firewall rules to limit connections
- Consider running railwayStudio and Docker on an isolated network
- The protocol currently does not include authentication (add if needed)

## Future Enhancements

Planned features:
- Bidirectional communication (railwayStudio → Docker)
- Switch control messages
- Signal control messages
- Authentication/authorization
- SSL/TLS support

