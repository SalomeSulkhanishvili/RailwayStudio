# RailwayStudio

A professional railway layout editor and real-time monitoring application built with Python and Qt.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚂 Overview

RailwayStudio is a desktop application that allows you to:
- **Design** complex railway layouts with an intuitive drag-and-drop editor
- **Monitor** railway systems in real-time via UDP network updates
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
- Receive UDP packets for block color updates
- Simulate train positions with color changes
- Network status monitoring and logging

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
2. Configure UDP port in Network Settings
3. Click "Start Listening" to begin monitoring
4. Send UDP packets in format: `BLOCK_ID:COLOR`
5. Watch rail colors update in real-time

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
├── layouts/                # 📂 Your railway layout files
│   ├── README.md           # Layout folder documentation
│   └── *.json              # Saved layout files
│
├── ui/                     # User Interface
│   ├── main_window.py      # Main application window
│   ├── editor_view.py      # Railway editor
│   ├── monitor_view.py     # Real-time monitor
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
│   └── json_formatter.py   # JSON serialization
│
└── docs/                   # Documentation
    ├── ARCHITECTURE.md     # Architecture details
    ├── REFACTORING.md      # Refactoring guide
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

### Network Updates
UDP packet format:
```
BLOCK_ID:COLOR
```
Example: `BL001:green` or `BL002:red`

## 🔧 Configuration

### Network Settings
- **UDP Port**: 5000 (default)
- **IP Address**: Configurable in settings
- **Gateway/Subnet**: Full network configuration available

### Display Settings
- **Grid**: Toggle dot grid for alignment
- **Colors**: Customize block colors
- **Zoom**: Mousewheel to zoom in/out

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

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

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with:
- [PySide6](https://doc.qt.io/qtforpython-6/) - Qt for Python
- [Python 3.13](https://www.python.org/) - Programming language

---

**Made with ❤️ for railway enthusiasts and system integrators**
