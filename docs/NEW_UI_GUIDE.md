# New UI Design Guide

## Overview
The Railway Editor application now features a modern, sidebar-based navigation UI with five main sections.

## UI Structure

### Sidebar Navigation
Located on the left side with a dark blue theme (#3A4A6A):
- **Home** 🏠 - Welcome page with feature overview
- **Editor** ✏️ - Build and edit railway layouts
- **View** 👁️ - Monitor railway status in real-time
- **Files** 📁 - Browse and manage JSON layout files
- **Settings** ⚙️ - Configure application preferences

### Color Scheme
```
Primary Background: #4A5A7A (Medium Blue-Gray)
Sidebar: #3A4A6A (Darker Blue)
Accent: #5B8A5A (Green for active items)
Text: #FFFFFF (White)
Secondary Text: #B0C0D0 (Light Gray)
Hover: #7B8AAA (Lighter Blue)
```

## Views Description

### 1. Home View 🏠
**Purpose**: Welcome screen with application overview

**Features**:
- Large welcoming title
- Three feature cards with icons:
  - 🎯 Build layouts with track blocks, turnouts, and signals
  - 💾 Save and load layouts in JSON format
  - 🌐 Monitor and update your layout in real-time via Ethernet
- Clean, informative design

**File**: `ui/home_view.py`

### 2. Editor View ✏️
**Purpose**: Create and edit railway layouts

**Features**:
- Drag and drop rail components
- Visual connection system
- Auto-snap connections
- Block ID display
- Auto-create groups
- Save/load functionality
- Zoom and pan controls

**File**: `ui/editor_view.py` (existing, unchanged)

### 3. View (Monitor) 👁️
**Purpose**: Real-time monitoring of railway status

**Features**:
- Read-only display of layouts
- Network listener for UDP packets
- Real-time color updates based on train positions
- Status display

**File**: `ui/monitor_view.py` (existing, unchanged)

### 4. Files View 📁
**Purpose**: Browse and manage JSON layout files

**Features**:
- List all JSON files in current directory
- Show file info (size, number of groups)
- Sort by modification time (newest first)
- Double-click to open
- Delete files with confirmation
- Change directory
- Refresh list

**Actions**:
- 🔄 **Refresh**: Reload file list
- 📂 **Open Selected**: Load the selected layout
- 🗑️ **Delete**: Remove file permanently

**File**: `ui/files_view.py`

### 5. Settings View ⚙️
**Purpose**: Configure application preferences

**Features**:

#### Color Settings
- **Rail Color**: Default color for railway tracks
- **Connection Color**: Color of connection lines
- **Background Color**: Editor background
- **Selected Color**: Highlight color for selected rails

#### Editor Settings
- **Grid Size**: Spacing between grid points (10-200 px)
- **Snap Distance**: Auto-connect threshold (10-100 px)

#### Network Settings
- **UDP Port**: Port for monitoring (1000-65535)

**Actions**:
- Color pickers for all color settings
- Spin boxes for numerical values
- **Reset to Defaults** button

**File**: `ui/settings_view.py`

## Navigation Flow

```
┌─────────────┐
│   Sidebar   │
├─────────────┤
│ 🏠 Home      │ ──> Welcome & Info
│ ✏️  Editor   │ ──> Build Layouts
│ 👁️  View     │ ──> Monitor Status
│ 📁 Files     │ ──> Browse/Open Files
│ ⚙️  Settings │ ──> Configure App
└─────────────┘
```

### User Flow Example

1. **Start**: Home view displays welcome message
2. **Create**: Click "Editor" to build a new layout
3. **Save**: Layout saved automatically in current directory
4. **Browse**: Click "Files" to see all layouts
5. **Open**: Double-click a file to load it
6. **Monitor**: Click "View" to see real-time status
7. **Customize**: Click "Settings" to change colors/preferences

## Key Improvements

### From Old Design:
- ❌ Menu bar with dropdowns
- ❌ Toolbar buttons
- ❌ Mode indicator label
- ❌ Configuration menu (removed)

### To New Design:
- ✅ Modern sidebar navigation
- ✅ Active view highlighting with green accent
- ✅ Icon-based navigation
- ✅ Dedicated home page
- ✅ Files browser integration
- ✅ Settings page with color customization
- ✅ Consistent color scheme throughout

## Technical Details

### Main Window Structure
```python
MainWindow
├── Sidebar (QFrame)
│   ├── Title: "RailwayEditor"
│   └── Navigation Buttons (5)
│       ├── Home (index 0)
│       ├── Editor (index 1)
│       ├── View (index 2)
│       ├── Files (index 3)
│       └── Settings (index 4)
└── Content Area (QStackedWidget)
    ├── HomeView
    ├── EditorView
    ├── MonitorView
    ├── FilesView
    └── SettingsView
```

### View Switching
When a navigation button is clicked:
1. Content area switches to corresponding view
2. Active button gets green left border
3. Button text becomes white
4. Other buttons return to gray

### File Integration
Files view is directly integrated:
- Lists all JSON files in working directory
- Double-click or click "Open Selected" to load
- Automatically switches to Editor view after loading
- Shows file metadata (size, groups)

### Settings Integration
Settings view allows customization:
- Color pickers for visual preferences
- Spin boxes for numerical settings
- Changes emit signals for live updates
- Reset button restores defaults

## Future Enhancements

Potential additions:
- [ ] Recent files list on Home page
- [ ] File preview thumbnails
- [ ] Settings import/export
- [ ] Custom themes
- [ ] Keyboard shortcuts display
- [ ] Help/Documentation view
- [ ] Layout statistics on Home page

## File Structure

```
ui/
├── __init__.py          # Package exports
├── main_window.py       # Main window with sidebar (NEW)
├── home_view.py         # Welcome page (NEW)
├── editor_view.py       # Layout editor (EXISTING)
├── monitor_view.py      # Real-time monitor (EXISTING)
├── files_view.py        # File browser (NEW)
├── settings_view.py     # Settings page (NEW)
└── rail_graphics.py     # Rail graphics (EXISTING)
```

## Screenshots Description

### Home View
- Dark blue background (#4A5A7A)
- Large welcome title in white
- Three features with large emoji icons
- Feature titles in bold light gray
- Descriptions in softer gray

### Editor View
- White/light gray background
- Rail graphics with block IDs
- Connection points (red/green dots)
- Toolbar with rail type buttons
- Auto-Create Groups button

### Files View
- List of JSON files
- Dark blue list background (#5A6A8A)
- File information (size, groups)
- Action buttons at bottom
- Directory path display

### Settings View
- Grouped settings sections
- Color picker buttons showing current colors
- Spin boxes for numeric values
- Bordered group boxes
- Reset to Defaults button

## Usage Tips

1. **Start on Home**: Read feature overview
2. **Editor First**: Create your first layout
3. **Save Often**: Use Ctrl+S or File menu
4. **Browse Files**: Use Files view to organize layouts
5. **Customize**: Adjust colors in Settings
6. **Monitor**: Switch to View for real-time status

## Responsive Design

- Sidebar: Fixed 200px width
- Content area: Flexible, fills remaining space
- Minimum window size: 1000x600
- Recommended size: 1400x900

## Accessibility

- High contrast text on backgrounds
- Clear visual hierarchy
- Large, easy-to-click navigation buttons
- Tooltips on color picker buttons
- Confirmation dialogs for destructive actions

## Summary

The new UI provides:
- ✅ Modern, clean design
- ✅ Easy navigation
- ✅ Integrated file management
- ✅ Customizable settings
- ✅ Consistent visual theme
- ✅ Improved user experience

All previous functionality is preserved while adding new features in an intuitive interface!

