# RailwayStudio

A railway layout editor and real-time monitoring application with Docker/microcontroller integration.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

RailwayStudio is a desktop application for:
- **Designing** railway layouts with drag-and-drop editor
- **Monitoring** railway systems in real-time via TCP
- **Integrating** with Docker containers and microcontrollers
- **Managing** track groups and connections automatically

## Key Features

- 🎨 **Visual Editor** - Drag-and-drop rail placement (straight, curved, switches)
- 📊 **Real-Time Monitor** - TCP server for receiving block status updates
- 🐳 **Docker Integration** - JSON protocol for easy container integration
- 🔄 **Auto-Grouping** - Automatic logical track grouping
- 🌐 **Multi-Client** - Support for multiple simultaneous connections
- 📝 **JSON Format** - Clean, readable layout files

## Quick Start

### Installation

```bash
git clone <repository-url>
cd railwayStudio
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

## Usage

### Editor Mode
1. Select rail type and click to place
2. Drag connection dots to connect rails
3. Click "Auto-Create Groups" to validate
4. Save layout to `layouts/` folder

### Monitor Mode
1. Load a layout
2. Set TCP port and bind address (default: 5555, 0.0.0.0)
3. Click "Start Server"
4. Note the IP address shown for Docker connections
5. Send status updates from your containers

### Docker Integration

**Quick Example:**
```python
import socket, json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 5555))  # Use IP from Monitor view

update = {
    "type": "status_update",
    "block_id": "BL001001",  # Use Block IDs from your layout
    "status": "blocked"      # free, reserved, blocked, unknown
}
sock.send((json.dumps(update) + '\n').encode('utf-8'))
sock.close()
```

**Extract Block IDs from your layout:**
```bash
python examples/extract_block_ids.py layouts/your_layout.json
```

**📖 Complete Guide:** See [TCP_QUICKSTART.md](docs/TCP_QUICKSTART.md) for step-by-step setup.

## Architecture

RailwayStudio follows **MVC (Model-View-Controller)** pattern:

```
View (ui/)
  ↕ signals
Controller (controllers/)
  ↕ updates
Model (core/)
```

**Benefits:**
- ✅ Testable - Each layer independent
- ✅ Maintainable - Clear separation of concerns
- ✅ Scalable - Easy to extend

See [MVC_ARCHITECTURE.md](docs/MVC_ARCHITECTURE.md) for details.

## Project Structure

```
railwayStudio/
├── main.py                     # Entry point
├── core/                       # MODEL - Data & business rules
│   ├── railway_system.py       # Core data structures
│   ├── tcp_server.py           # TCP server
│   └── block_status.py         # Status definitions
├── controllers/                # CONTROLLER - Business logic
│   ├── editor_controller.py    # Editor operations
│   ├── monitor_controller.py   # Monitor & TCP handling
│   ├── files_controller.py     # File operations
│   └── settings_controller.py  # Settings management
├── ui/                         # VIEW - User interface
│   ├── main_window.py          # Main window
│   ├── editor_view.py          # Editor UI
│   ├── monitor_view.py         # Monitor UI
│   └── rail_graphics.py        # Graphics components
├── layouts/                    # Layout files (.json)
├── examples/                   # Integration examples
│   ├── docker_tcp_client.py    # TCP client example
│   └── extract_block_ids.py    # Extract IDs utility
└── docs/                       # Documentation
    ├── TCP_QUICKSTART.md       # 5-min setup guide
    ├── TCP_INTEGRATION.md      # Protocol reference
    └── MVC_ARCHITECTURE.md     # Architecture guide
```

## TCP Protocol

### Status Update
```json
{
  "type": "status_update",
  "block_id": "BL001001",
  "status": "blocked"
}
```

### Batch Update
```json
{
  "type": "batch_update",
  "updates": [
    {"block_id": "BL001001", "status": "blocked"},
    {"block_id": "BL001002", "status": "free"}
  ]
}
```

### Status Colors
- `free` → Green
- `reserved` → Orange  
- `blocked` → Red
- `unknown` → Gray

**Full Protocol:** [TCP_INTEGRATION.md](docs/TCP_INTEGRATION.md)

## Configuration

### Network Settings
- **TCP Port**: 5555 (configurable in Settings)
- **Bind Address**: 0.0.0.0 (all interfaces) or specific IP
- **Protocol**: JSON over TCP, newline-delimited
- **Multi-Client**: Unlimited connections

### Display Settings
- Grid toggle and snap-to-grid
- Customizable colors
- Zoom with mousewheel

## Documentation

- **[TCP Quick Start](docs/TCP_QUICKSTART.md)** - Get started with Docker in 5 minutes
- **[TCP Integration](docs/TCP_INTEGRATION.md)** - Complete protocol reference
- **[MVC Architecture](docs/MVC_ARCHITECTURE.md)** - Codebase architecture

## Troubleshooting

**Connection refused:**
- Ensure TCP server is started (green status in Monitor)
- Verify port and IP address
- Check firewall settings

**Block not found:**
- Run "Auto-Create Groups" in Editor
- Use Block IDs (BL001001) from JSON, not rail IDs (rail_0001)
- Check Network Log for details

**Import errors:**
- Activate virtual environment
- Run `pip install -r requirements.txt`

## License

MIT License

## Built With

- [PySide6](https://doc.qt.io/qtforpython-6/) - Qt for Python
- [Python 3.13](https://www.python.org/)
