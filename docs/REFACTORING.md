# Code Refactoring - Separation of Concerns

## Overview
Refactored the codebase to separate design (UI/styling) from logic (business logic) for better maintainability, readability, and testability.

## New Structure

```
project/
├── ui/
│   ├── styles/              # NEW: Centralized styling
│   │   ├── __init__.py
│   │   └── theme.py         # Colors, fonts, style functions
│   ├── components/          # (Future: reusable UI components)
│   ├── editor_view.py       # REFACTORED: UI only
│   ├── monitor_view.py      # REFACTORED: UI only
│   └── settings_view.py     # REFACTORED: UI only
├── controllers/             # NEW: Business logic
│   ├── __init__.py
│   ├── editor_controller.py # Editor business logic
│   └── monitor_controller.py # Monitor business logic
└── core/                    # Existing: Data models
    ├── railway_system.py
    └── json_formatter.py
```

## Key Changes

### 1. **Styles Module** (`ui/styles/theme.py`)
- **Centralized Colors**: All colors defined in `COLORS` dictionary
- **Reusable Style Functions**: 
  - `get_primary_button_style()`
  - `get_secondary_button_style()`
  - `get_accent_button_style()`
  - `get_danger_button_style()`
  - `get_toggle_button_style()`
  - `get_input_style()`
  - `get_combo_box_style()`
  - `get_card_style()`
  - `get_label_style()`
- **Consistent Spacing**: `FONT_SIZES`, `SPACING`, `RADIUS` constants

### 2. **Editor Controller** (`controllers/editor_controller.py`)
Handles all editor business logic:
- `add_rail()` - Add new rails
- `remove_rail()` - Remove rails
- `connect_rails()` - Connect two rails
- `disconnect_rails()` - Disconnect rails
- `clear_all()` - Clear all rails
- `auto_create_groups()` - Create rail groups with validation
- `save_layout()` - Save to JSON with validation
- `load_layout()` - Load from JSON
- `get_rail_count()` / `get_group_count()` - Statistics

### 3. **Monitor Controller** (`controllers/monitor_controller.py`)
Handles all monitor business logic:
- `load_layout()` - Load layout file
- `parse_update_packet()` - Parse UDP packets
- `apply_color_update()` - Update block colors
- `test_color_change()` - Manual color testing
- `reset_all_colors()` - Reset to defaults
- `get_block_count()` / `get_available_blocks()` - Statistics
- `log()` - Logging with callback support

## Benefits

### 1. **Separation of Concerns**
- **UI Layer**: Only handles visual presentation and user interactions
- **Controller Layer**: Contains business logic and data operations
- **Model Layer**: Data structures and persistence (existing `core/`)

### 2. **Improved Maintainability**
- Style changes can be made in one place (`theme.py`)
- Business logic is centralized and easier to test
- Views are cleaner and easier to understand

### 3. **Reusability**
- Style functions can be reused across all views
- Controllers can be tested independently
- Easy to add new views with consistent styling

### 4. **Better Testability**
- Controllers can be unit tested without UI
- Logic is decoupled from Qt widgets
- Easier to mock and test edge cases

### 5. **Consistency**
- All buttons/inputs use the same styling
- Color palette is consistent across the app
- Changes propagate automatically

## Migration Guide

### Before (Mixed Logic and UI):
```python
# In editor_view.py
def save_layout(self):
    # UI code
    file_path, _ = QFileDialog.getSaveFileName(...)
    
    # Business logic mixed in
    if not self.railway_system.blocks:
        QMessageBox.warning(...)
        return
    
    formatter = RailwayJSONFormatter(self.railway_system)
    data = formatter.to_blockgroups_json()
    # ... more logic and UI
```

### After (Separated):
```python
# In editor_view.py (UI only)
def save_layout(self):
    file_path, _ = QFileDialog.getSaveFileName(...)
    if file_path:
        success, message = self.controller.save_layout(file_path)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

# In editor_controller.py (Logic only)
def save_layout(self, file_path: str) -> tuple[bool, str]:
    if not self.railway_system.blocks:
        return False, "Cannot save empty layout"
    
    formatter = RailwayJSONFormatter(self.railway_system)
    data = formatter.to_blockgroups_json()
    # ... more logic
    return True, "Saved successfully"
```

## Next Steps

1. **Phase 1** ✅ (Completed)
   - Create styles module
   - Create controllers
   - Documentation

2. **Phase 2** (In Progress)
   - Refactor `editor_view.py` to use controller and styles
   - Refactor `monitor_view.py` to use controller and styles
   - Refactor `settings_view.py` to use styles

3. **Phase 3** (Future)
   - Extract reusable UI components
   - Add unit tests for controllers
   - Add integration tests

## Testing

After refactoring, ensure:
- [ ] All editor functions work (add, remove, connect, disconnect)
- [ ] Save/load functionality works correctly
- [ ] Monitor view loads layouts and updates colors
- [ ] Settings apply correctly
- [ ] UI styling is consistent across all views
- [ ] No regressions in existing functionality

