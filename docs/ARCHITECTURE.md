# RailwayStudio Architecture

## Project Structure

```
railway_studio/
│
├── main.py                      # Application entry point
│
├── ui/                          # User Interface Layer
│   ├── __init__.py
│   ├── main_window.py           # Main application window & navigation
│   ├── editor_view.py           # Railway editor UI (uses EditorController)
│   ├── monitor_view.py          # Railway monitor UI (uses MonitorController)
│   ├── settings_view.py         # Settings UI
│   ├── files_view.py            # File management UI
│   ├── home_view.py             # Home/welcome screen
│   ├── rail_graphics.py         # Qt Graphics items for rails
│   │
│   └── styles/                  # Styling & Theming ✨ NEW
│       ├── __init__.py
│       └── theme.py             # Centralized colors, fonts, style functions
│
├── controllers/                 # Business Logic Layer ✨ NEW
│   ├── __init__.py
│   ├── editor_controller.py     # Editor operations & validation
│   └── monitor_controller.py    # Monitor operations & packet handling
│
└── core/                        # Data Model Layer
    ├── __init__.py
    ├── railway_system.py        # Core data structures (RailBlock, RailGroup)
    └── json_formatter.py        # JSON serialization/deserialization
```

## Architecture Layers

### 1. **UI Layer** (`ui/`)
**Responsibility**: Visual presentation and user interaction

- **What it does**:
  - Renders widgets and layouts
  - Handles user input events (clicks, drags)
  - Displays messages and dialogs
  - Delegates business logic to controllers
  
- **What it doesn't do**:
  - Business logic or validation
  - Direct data manipulation
  - File I/O or network operations

**Example**: `editor_view.py`
```python
def save_layout(self):
    # UI only - get file path from user
    file_path, _ = QFileDialog.getSaveFileName(...)
    
    # Delegate to controller
    success, message = self.controller.save_layout(file_path)
    
    # UI only - show result
    if success:
        QMessageBox.information(self, "Success", message)
```

### 2. **Controller Layer** (`controllers/`) ✨ NEW
**Responsibility**: Business logic and orchestration

- **What it does**:
  - Validates user actions
  - Coordinates between UI and data models
  - Handles complex operations (save, load, auto-group)
  - Formats error messages
  - Manages state transitions

- **What it doesn't do**:
  - Display UI elements
  - Handle Qt events directly
  - Define styling

**Example**: `editor_controller.py`
```python
def save_layout(self, file_path: str) -> tuple[bool, str]:
    # Validation
    if not self.railway_system.blocks:
        return False, "Cannot save empty layout"
    
    # Business logic
    try:
        data = self.formatter.to_blockgroups_json()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True, "Saved successfully!"
    except ValueError as e:
        return False, f"Validation failed: {e}"
```

### 3. **Styles Module** (`ui/styles/`) ✨ NEW
**Responsibility**: Centralized theming and styling

- **Centralized Colors**: `COLORS` dictionary with named colors
- **Style Functions**: Reusable stylesheet generators
- **Consistent Spacing**: `FONT_SIZES`, `SPACING`, `RADIUS` constants

**Example**: `theme.py`
```python
COLORS = {
    'primary': '#48BB78',
    'secondary': '#4299E1',
    'danger': '#F56565',
    ...
}

def get_primary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            ...
        }}
    """
```

### 4. **Data Model Layer** (`core/`)
**Responsibility**: Data structures and persistence

- **What it does**:
  - Defines data structures (`RailBlock`, `RailGroup`)
  - Manages relationships (connections, groups)
  - Provides data access methods
  - Handles JSON serialization

**Example**: `railway_system.py`
```python
class RailwaySystem:
    def add_block(self, rail_type, x, y, rotation, length):
        block = RailBlock(...)
        self.blocks[block.id] = block
        return block.id
```

## Data Flow

### User Action → Display

```
User clicks "Save"
     ↓
[UI Layer] editor_view.save_layout()
  - Shows file dialog
  - Gets file path
     ↓
[Controller] editor_controller.save_layout(path)
  - Validates data
  - Calls formatter
  - Handles file I/O
  - Returns (success, message)
     ↓
[UI Layer] Shows success/error message
```

### Data Update → UI Refresh

```
UDP packet received
     ↓
[Controller] monitor_controller.parse_update_packet()
  - Parses packet format
  - Validates block ID
     ↓
[Controller] monitor_controller.apply_color_update()
  - Updates railway_system data
  - Triggers signal
     ↓
[UI Layer] Receives signal → refresh graphics
```

## Design Patterns

### 1. **MVC (Model-View-Controller)**
- **Model**: `core/` (RailwaySystem, RailBlock, RailGroup)
- **View**: `ui/` (QWidget subclasses)
- **Controller**: `controllers/` (EditorController, MonitorController)

### 2. **Observer Pattern**
- Qt Signals/Slots for event communication
- Controllers emit events, views listen and update

### 3. **Strategy Pattern**
- Different rail types (straight, curved, switch)
- Pluggable validators in formatter

### 4. **Factory Pattern**
- `RailGraphicsItem` creates appropriate graphics per rail type
- JSON formatter creates appropriate data structures

## Key Benefits

### ✅ **Separation of Concerns**
Each layer has a single, well-defined responsibility

### ✅ **Testability**
Controllers can be unit tested without Qt/UI

### ✅ **Maintainability**
Changes in one layer don't cascade to others

### ✅ **Reusability**
Styles and controllers can be reused across views

### ✅ **Consistency**
Centralized theming ensures UI consistency

## Development Guidelines

### When adding a new feature:

1. **Define Data Model** (if needed)
   - Add to `core/railway_system.py` or create new model

2. **Create Controller Logic**
   - Add methods to appropriate controller
   - Return `(success, message)` tuples for UI feedback

3. **Build UI**
   - Use styles from `ui/styles/theme.py`
   - Delegate logic to controller
   - Handle only UI concerns

4. **Test**
   - Unit test controller logic
   - Integration test UI flow

### Style Guidelines:

- **Always** use `ui/styles/theme.py` for colors and styles
- **Never** hardcode colors in views
- Use `get_*_button_style()` functions for buttons
- Use `COLORS` dictionary for all color references

### Controller Guidelines:

- Return `tuple[bool, str]` for operations (success, message)
- Accept only primitive types or model objects
- No Qt imports in controllers (except in rare cases)
- Log errors, don't display UI

### View Guidelines:

- Minimal business logic (just UI state)
- Delegate to controller for operations
- Handle Qt events and signals
- Show feedback using QMessageBox

## Future Improvements

1. **Component Library**: Reusable UI components (`ui/components/`)
2. **Service Layer**: Network, file, settings services
3. **Dependency Injection**: Pass controllers via factory
4. **State Management**: Redux-like state for complex flows
5. **Type Hints**: Full type coverage for better IDE support
6. **Documentation**: Auto-generated API docs

