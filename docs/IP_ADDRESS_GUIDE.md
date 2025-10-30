# Finding Your Host IP Address for Docker

When connecting from Docker to railwayStudio on the same PC, you need to use the host machine's IP address.

## Automatic Detection in RailwayStudio

**Easiest Method:**

1. Open railwayStudio
2. Go to **Monitor** view
3. Click **"Start Server"**
4. Look for the box titled **"Connect from Docker using:"**
5. Copy the IP address shown (e.g., `192.168.1.100:5555`)
6. Use this IP in your Docker container

## Manual Methods

### macOS

**Terminal:**
```bash
# Show all IP addresses
ifconfig | grep "inet " | grep -v 127.0.0.1

# Or get just the main IP
ipconfig getifaddr en0    # For WiFi
ipconfig getifaddr en1    # For Ethernet
```

**Common ranges:**
- WiFi: Usually starts with `192.168.`
- Ethernet: Usually starts with `192.168.` or `10.`

### Linux

**Terminal:**
```bash
# Show all IP addresses
ip addr show | grep "inet " | grep -v 127.0.0.1

# Or use hostname
hostname -I

# Or use ifconfig
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Windows

**Command Prompt or PowerShell:**
```cmd
ipconfig | findstr IPv4
```

**Or use Settings:**
1. Open **Settings**
2. Go to **Network & Internet**
3. Click on your connection (WiFi or Ethernet)
4. Scroll down to find **IPv4 address**

## Understanding IP Addresses

### Localhost (Won't Work from Docker)
- `127.0.0.1` or `localhost`
- Only accessible from the same machine
- Docker containers are isolated, so this won't work

### Private Network IPs (Use These!)
- `192.168.x.x` - Home/office networks (most common)
- `10.x.x.x` - Corporate networks
- `172.16.x.x` to `172.31.x.x` - Some corporate networks

### Docker Special Addresses
- `host.docker.internal` - Mac/Windows Docker Desktop only
- `172.17.0.1` - Linux Docker bridge gateway
- These may not always work, so prefer actual IP

## Using the IP in Docker

### Python Example

```python
import socket
import json

# Replace with your actual IP from railwayStudio Monitor view
HOST_IP = '192.168.1.100'  
PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST_IP, PORT))

# Send status update
update = {
    "type": "status_update",
    "block_id": "BL001001",
    "status": "blocked"
}
sock.send((json.dumps(update) + '\n').encode('utf-8'))
sock.close()
```

### Docker Compose Example

```yaml
version: '3'
services:
  railway-controller:
    build: .
    environment:
      - RAILWAY_STUDIO_HOST=192.168.1.100  # Your host IP
      - RAILWAY_STUDIO_PORT=5555
```

Then in your code:
```python
import os
HOST_IP = os.getenv('RAILWAY_STUDIO_HOST', '192.168.1.100')
PORT = int(os.getenv('RAILWAY_STUDIO_PORT', '5555'))
```

## Troubleshooting

### "Connection refused" or "Connection timed out"

**Check:**
1. ✅ railwayStudio TCP server is running (green status)
2. ✅ Using the correct IP (check Monitor view)
3. ✅ Port number matches (default: 5555)
4. ✅ Firewall allows connections on that port
5. ✅ Docker and railwayStudio on same network

**Test connection from host first:**
```bash
# Test if server is accessible
telnet 192.168.1.100 5555

# Or use netcat
nc -zv 192.168.1.100 5555
```

### IP Address Changes

**Problem:** IP addresses can change (DHCP)

**Solutions:**

1. **Use DHCP Reservation** (Recommended)
   - Configure your router to always give your PC the same IP
   - Check router documentation for "DHCP Reservation" or "Static DHCP"

2. **Set Static IP** on your PC
   - Network settings → Set manual IP
   - Choose an IP outside your router's DHCP range

3. **Use Dynamic Discovery**
   ```python
   # In your Docker container, make the host IP configurable
   HOST_IP = os.getenv('RAILWAY_STUDIO_HOST', '192.168.1.100')
   ```

### Multiple Network Interfaces

If you have multiple IPs (WiFi + Ethernet):

1. Check railwayStudio Monitor view - it shows all available IPs
2. Use the IP of the interface your Docker network uses
3. Usually WiFi = `192.168.x.x`, Ethernet = `10.x.x.x` or `192.168.x.x`

## Network Modes Comparison

| Mode | Host Value | Works On | Pros | Cons |
|------|-----------|----------|------|------|
| **Actual IP** | `192.168.1.100` | All | Most reliable | IP may change |
| **host.docker.internal** | `host.docker.internal` | Mac/Win | Simple | Doesn't work on Linux |
| **Bridge Gateway** | `172.17.0.1` | Linux | Simple | Doesn't work on Mac/Win |
| **Host Network** | `localhost` | Linux | Fast | No isolation, Mac/Win unsupported |

**Recommendation:** Use the actual IP address shown in railwayStudio Monitor view for maximum compatibility.

## Quick Reference

```python
# ✅ BEST - Use actual IP (shown in railwayStudio Monitor)
sock.connect(('192.168.1.100', 5555))

# ⚠️ OK - Docker special hostname (Mac/Windows only)
sock.connect(('host.docker.internal', 5555))

# ⚠️ OK - Docker bridge (Linux only)
sock.connect(('172.17.0.1', 5555))

# ❌ WON'T WORK - Localhost (Docker is isolated)
sock.connect(('localhost', 5555))
sock.connect(('127.0.0.1', 5555))
```

## Advanced: Firewall Configuration

If connection is refused, check firewall:

### macOS
```bash
# Allow incoming connections on port 5555
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/python
```

### Linux (ufw)
```bash
sudo ufw allow 5555/tcp
```

### Windows
1. Open **Windows Defender Firewall**
2. Click **Advanced Settings**
3. **Inbound Rules** → **New Rule**
4. Port: **5555**, TCP
5. Allow the connection

## Summary

1. ✅ **Start railwayStudio** and look at Monitor view
2. ✅ **Copy the IP address** shown (e.g., `192.168.1.100:5555`)
3. ✅ **Use that IP** in your Docker container
4. ✅ **Test the connection** before running your full application
5. ✅ **Make it configurable** using environment variables

This ensures your Docker container can always connect to railwayStudio on the host!

