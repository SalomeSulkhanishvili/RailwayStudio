# RailwayStudio

A railway layout editor and real-time monitoring application built with Python and Qt.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚂 Overview

RailwayStudio is a desktop application that allows you to:
- **Design** complex railway layouts with an intuitive drag-and-drop editor
- **Monitor** railway systems in real-time via TCP/UDP network updates
- **Integrate** with Docker containers and microcontrollers for live status updates
- **Validate** rail connections and automatically create logical track groups
- **Save/Load** layouts in a structured JSON format

## ✨ Key Features

### 🎨 Visual Editor
- Drag-and-drop rail placement (straight, curved, switch left/right)
- Visual connection system with snap-to-grid alignment
- Real-time validation of rail connections
- Automatic grouping of connected track sections
- Customizable rail lengths and rotations

### 📊 Real-Time Monitor
- Load and display railway layouts
- **TCP Server** for receiving block status updates from Docker containers
- Receive status updates: free, reserved, blocked, unknown
- Automatic color coding based on block status
- Multi-client support with connection tracking
- Network status monitoring and logging
- JSON-based protocol for easy integration

### ⚙️ Advanced Features
- **Auto-Grouping**: Automatically creates logical groups based on turnouts
- **Connection Validation**: Ensures all rails are properly connected
- **JSON Format**: Clean, readable layout format with metadata
- **Network Configuration**: Customizable IP, port, and network settings

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd railwayStudio
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

## 📖 Usage

### Editor Mode
1. Select rail type (Straight, Curved, Switch Left, Switch Right)
2. Click on canvas to place rails
3. Drag red connection dots together to connect rails
4. Click "Auto-Create Groups" to validate and organize
5. Save your layout with the "Save" button (saved to `layouts/` folder)

### Monitor Mode
1. Load a layout with the "Load Layout" button
2. Configure TCP port (default: 5555)
3. Click "Start Server" to begin monitoring
4. Connect from Docker containers or external systems
5. Send block status updates via TCP
6. Watch rail colors update in real-time

**TCP Integration with Docker:**
```python
import socket, json
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('host.docker.internal', 5555))  # Mac/Windows Docker

# IMPORTANT: Use external Block IDs (BL00X00X) from your JSON layout file
update = {"type": "status_update", "block_id": "BL001001", "status": "blocked"}
sock.send((json.dumps(update) + '\n').encode('utf-8'))
sock.close()
```

**Note**: Use External Block IDs (`BL001001`) not internal IDs (`rail_0001`). 
See [Block ID Mapping Guide](docs/BLOCK_ID_MAPPING.md) for details.

See [TCP Quick Start Guide](docs/TCP_QUICKSTART.md) for full Docker integration guide.

### Files Management
- All layouts are stored in the `layouts/` folder
- Use the **Files** tab to browse, load, or delete layouts
- The Files view automatically opens to the `layouts/` folder

## 🏗️ Project Structure

```
railwaystudio/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── layouts/                # 📂 Railway layout files
│   ├── README.md           # Layout folder documentation
│   └── *.json              # Saved layout files
│
├── examples/               # 📂 Example integration code
│   ├── docker_tcp_client.py    # Docker TCP client example
│   ├── extract_block_ids.py    # Extract Block IDs from JSON layout
│   └── README.md           # Examples documentation
│
├── ui/                     # User Interface
│   ├── main_window.py      # Main application window
│   ├── editor_view.py      # Railway editor
│   ├── monitor_view.py     # Real-time monitor with TCP server
│   ├── settings_view.py    # Settings panel
│   ├── home_view.py        # Welcome screen
│   ├── files_view.py       # File management
│   ├── rail_graphics.py    # Rail graphics rendering
│   │
│   └── styles/             # Centralized styling
│       └── theme.py        # Colors, fonts, styles
│
├── controllers/            # Business Logic
│   ├── editor_controller.py    # Editor operations
│   └── monitor_controller.py   # Monitor operations
│
├── core/                   # Data Models
│   ├── railway_system.py   # Core data structures
│   ├── json_formatter.py   # JSON serialization
│   └── tcp_server.py       # TCP server for network updates
│
└── docs/                   # Documentation
    ├── TCP_QUICKSTART.md   # Quick start for Docker integration
    ├── TCP_INTEGRATION.md  # Complete TCP protocol guide
    ├── ARCHITECTURE.md     # Architecture details
    └── ...                 # Additional docs
```

## 🎯 Key Concepts

### Rail Blocks
Individual track segments with:
- Type (straight, curved, switch)
- Position (x, y coordinates)
- Rotation and length
- Connections to other blocks

### Rail Groups
Logical sections of connected rails:
- Defined by turnouts (switches)
- Each group has start/end blocks
- Used for train tracking and signaling

### Network Updates (TCP Protocol)

**Block Status Update** (recommended):
```json
{
  "type": "status_update",
  "block_id": "BL001001",
  "status": "blocked"
}
```

**Status Values:**
- `"free"` → Green (block available)
- `"reserved"` → Orange (reserved for train)
- `"blocked"` → Red (occupied by train)
- `"unknown"` → Gray (status unknown)

**Batch Update** (for multiple blocks):
```json
{
  "type": "batch_update",
  "updates": [
    {"block_id": "BL001001", "status": "blocked"},
    {"block_id": "BL001002", "status": "free"}
  ]
}
```

**Getting Block IDs for Docker:**
```bash
# Extract Block IDs from your layout file
python3 examples/extract_block_ids.py layouts/your_layout.json
```

## 🔧 Configuration

### Network Settings
- **TCP Port**: 5555 (default, configurable)
- **Protocol**: TCP server (listens on 0.0.0.0)
- **Multi-Client**: Supports multiple simultaneous connections
- **Auto-Reconnect**: Clients can reconnect automatically

### Display Settings
- **Grid**: Toggle dot grid for alignment
- **Colors**: Customize block colors
- **Zoom**: Mousewheel to zoom in/out

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

**TCP Integration (New! 🔥)**
- **[TCP Quick Start](docs/TCP_QUICKSTART.md)** - Get started with Docker in 5 minutes
- **[TCP Integration Guide](docs/TCP_INTEGRATION.md)** - Complete protocol documentation
- **[Block ID Mapping Guide](docs/BLOCK_ID_MAPPING.md)** - Understanding Block IDs (BL00X00X)

**General Documentation**
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[Refactoring Guide](docs/REFACTORING.md)** - Code structure and refactoring details
- **[Connection Validation](docs/CONNECTION_VALIDATION.md)** - How validation works
- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions

## 🐛 Troubleshooting

### "Cannot save - Validation Failed"
- Ensure all rails are properly connected
- Check for isolated (disconnected) rails
- Run "Auto-Create Groups" to identify issues

### "Import PySide6 could not be resolved"
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### Layout not loading
- Check JSON format is valid
- Ensure all block IDs are unique
- Verify connections in metadata

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with:
- [PySide6](https://doc.qt.io/qtforpython-6/) - Qt for Python
- [Python 3.13](https://www.python.org/) - Programming language
