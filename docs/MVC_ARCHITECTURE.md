# MVC Architecture

RailwayStudio follows the **Model-View-Controller (MVC)** pattern for clean separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                    USER                          │
└─────────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────┐
│              VIEW (ui/)                          │
│  • User interface & display                      │
│  • Handles user input events                     │
│  • Renders visual updates                        │
└─────────────────────────────────────────────────┘
      │                              ↑
      │ Actions                      │ Signals
      ↓                              │
┌─────────────────────────────────────────────────┐
│         CONTROLLER (controllers/)                │
│  • Business logic                                │
│  • Input validation                              │
│  • Coordinates Model & View                      │
└─────────────────────────────────────────────────┘
      │                              ↑
      │ Updates                      │ Signals
      ↓                              │
┌─────────────────────────────────────────────────┐
│            MODEL (core/)                         │
│  • Data structures                               │
│  • State management                              │
│  • Business rules                                │
└─────────────────────────────────────────────────┘
```

## Project Structure

```
railwayStudio/
├── core/                      # MODEL
│   ├── railway_system.py      # Data model & state
│   ├── tcp_server.py          # TCP server implementation
│   └── block_status.py        # Status definitions
│
├── controllers/               # CONTROLLER
│   ├── editor_controller.py   # Editor business logic
│   ├── monitor_controller.py  # Monitor & TCP logic
│   ├── files_controller.py    # File operations
│   └── settings_controller.py # Settings management
│
├── ui/                        # VIEW
│   ├── main_window.py         # Main window & navigation
│   ├── editor_view.py         # Editor UI
│   ├── monitor_view.py        # Monitor UI
│   ├── settings_view.py       # Settings UI
│   └── rail_graphics.py       # Graphics components
│
└── main.py                    # Entry point
```

## Component Responsibilities

### Model (core/)

**What it does:**
- Stores railway data (blocks, groups, connections)
- Manages application state
- Emits signals when data changes
- Enforces business rules

**What it doesn't do:**
- ❌ No UI code
- ❌ No user input handling
- ❌ No file I/O (delegated to controllers)

**Example:** `RailwaySystem`
```python
class RailwaySystem(QObject):
    block_color_changed = Signal(str, str)  # Notifies observers
    
    def set_block_color(self, block_id: str, color: str):
        if block_id in self.blocks:
            self.blocks[block_id].color = color
            self.block_color_changed.emit(block_id, color)
```

### Controller (controllers/)

**What it does:**
- Handles business logic
- Validates user input
- Coordinates between Model and View
- Manages external I/O (files, network)
- Emits signals for View updates

**What it doesn't do:**
- ❌ No direct UI manipulation (uses signals)
- ❌ No direct data storage (uses Model)

**Example:** `MonitorController`
```python
class MonitorController(QObject):
    log_message = Signal(str)
    tcp_server_started = Signal(int)
    
    def start_tcp_server(self, port: int, host: str):
        # Business logic
        self.tcp_server = RailwayTCPServer(...)
        self.tcp_server.start()
        self.tcp_server_started.emit(port)  # Notify View
```

### View (ui/)

**What it does:**
- Displays UI
- Captures user input
- Connects to Controller signals
- Updates display when notified

**What it doesn't do:**
- ❌ No business logic
- ❌ No direct Model manipulation
- ❌ No validation logic

**Example:** `MonitorView`
```python
class MonitorView(QWidget):
    def __init__(self, railway_system, settings_controller):
        self.controller = MonitorController(railway_system)
        self.connect_signals()
    
    def connect_signals(self):
        # Listen to Controller
        self.controller.log_message.connect(self.append_log)
        self.controller.tcp_server_started.connect(self.on_server_started)
    
    def start_network_listener(self):
        # Delegate to Controller
        port = self.port_spin.value()
        bind_address = self.bind_address_input.text()
        self.controller.start_tcp_server(port, bind_address)
    
    def on_server_started(self, port: int):
        # Update UI only
        self.status_label.setText(f"✓ Server running on port {port}")
```

## Data Flow Example

**Scenario:** User clicks "Start Server" in Monitor view

```
1. MonitorView.start_network_listener()
   ↓ Reads UI values
   
2. MonitorController.start_tcp_server(port, host)
   ↓ Validates inputs, starts server
   ↓ Emits tcp_server_started signal
   
3. MonitorView.on_server_started(port)
   ↓ Updates UI labels and buttons
```

**Scenario:** TCP message received with block status

```
1. RailwayTCPServer receives message
   ↓ Emits block_status_update signal
   
2. MonitorController._on_block_status_update(block_id, status)
   ↓ Converts status to color
   ↓ Calls RailwaySystem.set_block_color()
   
3. RailwaySystem.set_block_color()
   ↓ Updates internal state
   ↓ Emits block_color_changed signal
   
4. MonitorView.on_block_color_changed(block_id, color)
   ↓ Updates graphics item color
```

## Key Principles

### 1. Single Responsibility
Each component has one clear purpose.

### 2. Separation of Concerns
- Model = Data
- View = Display
- Controller = Logic

### 3. Signal-Based Communication
Use Qt signals instead of direct calls for loose coupling.

### 4. Controller as Mediator
Controllers coordinate between Model and View without them knowing about each other.

## Benefits

✅ **Testable** - Controllers can be tested without UI  
✅ **Maintainable** - Clear structure, easy to find code  
✅ **Flexible** - Swap Views without changing logic  
✅ **Scalable** - Add features without breaking existing code  

## Common Patterns

### Pattern 1: User Action
```
View (button click) 
  → Controller (business logic) 
  → Model (update state) 
  → View (signal → update display)
```

### Pattern 2: External Event
```
External (TCP message) 
  → Controller (process) 
  → Model (update) 
  → View (signal → display)
```

### Pattern 3: Settings Change
```
SettingsView (apply changes)
  → SettingsController (validate & save)
  → Emit network_settings_changed signal
  → MonitorController (receive signal)
  → Restart server with new settings
```

## See Also

- [TCP_QUICKSTART.md](TCP_QUICKSTART.md) - TCP integration guide
- [TCP_INTEGRATION.md](TCP_INTEGRATION.md) - Full protocol reference
