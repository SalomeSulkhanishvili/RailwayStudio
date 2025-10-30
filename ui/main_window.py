"""
Main Window for Railway Editor & Monitor Application  
Modern UI with enhanced sidebar navigation
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QFileDialog, QMessageBox,
                               QLabel, QStackedWidget, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction
import json

from ui.home_view import HomeView
from ui.editor_view import EditorView
from ui.monitor_view import MonitorView
from ui.files_view import FilesView
from ui.settings_view import SettingsView
from core.railway_system import RailwaySystem
from core.json_formatter import RailwayJSONFormatter
from controllers.settings_controller import SettingsController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.railway_system = RailwaySystem()
        self.current_file = None
        
        # Create shared settings controller
        self.settings_controller = SettingsController()
        
        self.setup_ui()
        self.setup_menubar()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        self.setWindowTitle("RailwayStudio")
        self.setGeometry(100, 100, 1400, 900)
        # Allow free resizing - no minimum or maximum size restrictions
        self.setMinimumSize(800, 600)  # Reasonable minimum for usability
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right content area
        self.stacked_widget = QStackedWidget()
        
        # Create views (pass settings_controller to views that need it)
        self.home_view = HomeView()
        self.editor_view = EditorView(self.railway_system)
        self.monitor_view = MonitorView(self.railway_system, self.settings_controller)
        self.files_view = FilesView()
        self.settings_view = SettingsView(self.settings_controller)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.home_view)       # Index 0
        self.stacked_widget.addWidget(self.editor_view)     # Index 1
        self.stacked_widget.addWidget(self.monitor_view)    # Index 2
        self.stacked_widget.addWidget(self.files_view)      # Index 3
        self.stacked_widget.addWidget(self.settings_view)   # Index 4
        
        # Connect signals
        self.files_view.file_selected.connect(self.load_file_from_path)
        self.settings_view.settings_changed.connect(self.on_settings_changed)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Show home by default
        self.show_view(0)
        
    def create_sidebar(self):
        """Create the modern left sidebar with navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-right: 2px solid #34495E;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title section
        title_section = QFrame()
        title_section.setStyleSheet("""
            QFrame {
                background-color: #34495E;
                padding: 15px 10px;
            }
        """)
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Railway\nStudio")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ECF0F1; line-height: 1.2;")
        title_layout.addWidget(title)
        
        layout.addWidget(title_section)
        
        layout.addSpacing(10)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Home button
        btn_home = self.create_nav_button("🏠", "Home", 0)
        layout.addWidget(btn_home)
        self.nav_buttons.append(btn_home)
        
        # Editor button
        btn_editor = self.create_nav_button("✏️", "Editor", 1)
        layout.addWidget(btn_editor)
        self.nav_buttons.append(btn_editor)
        
        # Monitor button
        btn_monitor = self.create_nav_button("📊", "Monitor", 2)
        layout.addWidget(btn_monitor)
        self.nav_buttons.append(btn_monitor)
        
        # Files button
        btn_files = self.create_nav_button("📁", "Files", 3)
        layout.addWidget(btn_files)
        self.nav_buttons.append(btn_files)
        
        layout.addSpacing(10)
        
        # Settings button
        btn_settings = self.create_nav_button("⚙️", "Settings", 4)
        layout.addWidget(btn_settings)
        self.nav_buttons.append(btn_settings)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return sidebar
        
    def create_nav_button(self, icon, text, view_index):
        """Create a navigation button"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Arial", 14))
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #BDC3C7;
                text-align: left;
                padding-left: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #34495E;
                color: #ECF0F1;
            }
        """)
        btn.clicked.connect(lambda: self.show_view(view_index))
        return btn
        
    def show_view(self, index):
        """Show a specific view and update button styles"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update button styles
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                # Active state
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: #FFFFFF;
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                        border-left: 4px solid #2980B9;
                    }
                """)
            else:
                # Inactive state
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #BDC3C7;
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #34495E;
                        color: #ECF0F1;
                    }
                """)
        
        # Special handling for monitor view
        if index == 2:  # Monitor view
            self.monitor_view.refresh()
            
    def setup_menubar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1F2937;
                color: #F3F4F6;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #374151;
            }
            QMenu {
                background-color: #1F2937;
                color: #F3F4F6;
                border: 1px solid #374151;
            }
            QMenu::item {
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #374151;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Layout", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_layout)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Layout...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_layout)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Layout", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_layout)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_layout_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        home_action = QAction("Home", self)
        home_action.triggered.connect(lambda: self.show_view(0))
        view_menu.addAction(home_action)
        
        editor_action = QAction("Editor", self)
        editor_action.triggered.connect(lambda: self.show_view(1))
        view_menu.addAction(editor_action)
        
        monitor_action = QAction("Monitor", self)
        monitor_action.triggered.connect(lambda: self.show_view(2))
        view_menu.addAction(monitor_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def new_layout(self):
        """Create a new layout"""
        reply = QMessageBox.question(
            self,
            "New Layout",
            "Create a new layout? Unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.railway_system.clear()
            self.current_file = None
            self.editor_view.refresh()
            self.monitor_view.refresh()
            self.show_view(1)  # Switch to editor
            
    def open_layout(self):
        """Open a layout from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Layout",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            self.load_file_from_path(file_path)
            
    def save_layout(self):
        """Save the current layout"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_layout_as()
            
    def save_layout_as(self):
        """Save the layout to a new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Layout As",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            self._save_to_file(file_path)
            self.current_file = file_path
            
    def _save_to_file(self, file_path):
        """Internal method to save to a specific file"""
        try:
            # Check if there are any blocks
            if not self.railway_system.blocks:
                QMessageBox.warning(
                    self,
                    "Empty Layout",
                    "Cannot save an empty layout. Please add some rails first."
                )
                return
            
            # Convert to blockGroups format
            formatter = RailwayJSONFormatter(self.railway_system)
            try:
                data = formatter.to_blockgroups_json()
            except ValueError as e:
                # Validation error
                QMessageBox.critical(
                    self,
                    "❌ CANNOT SAVE - Connection Validation Failed!",
                    f"{str(e)}\n\n"
                    f"Please fix these issues before saving:\n"
                    f"1. Connect all disconnected rails\n"
                    f"2. Ensure all blocks are properly linked\n"
                    f"3. Click 'Auto-Create Groups' to validate"
                )
                return
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(
                self,
                "✓ Layout Saved",
                f"Layout saved successfully to:\n{file_path}"
            )
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save layout:\n{str(e)}\n\n{error_details}"
            )
            
    def load_file_from_path(self, file_path):
        """Load a layout file from the given path"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Check if it's the new blockGroups format or old format
                if "blockGroups" in data:
                    # New format
                    formatter = RailwayJSONFormatter(self.railway_system)
                    formatter.from_blockgroups_json(data)
                else:
                    # Old format (backward compatibility)
                    self.railway_system.load_from_json(data)
                
                self.editor_view.refresh()
                self.monitor_view.refresh()
                self.current_file = file_path
                
                # Switch to editor view
                self.show_view(1)
                
                QMessageBox.information(
                    self,
                    "✓ Success",
                    f"Layout loaded successfully:\n{file_path}"
                )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self,
                "❌ Error",
                f"Failed to load layout:\n{str(e)}\n\n{error_details}"
            )
            
    def on_settings_changed(self, settings):
        """Handle settings changes"""
        print(f"Settings updated: {settings}")
        # TODO: Apply settings to views
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About RailwayStudio",
            "<h2>RailwayStudio</h2>"
            "<p>Version 1.0</p>"
            "<p>A modern application for designing and monitoring railway layouts.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Visual railway layout editor</li>"
            "<li>Real-time monitoring via Ethernet</li>"
            "<li>JSON-based layout storage</li>"
            "<li>Automatic track grouping</li>"
            "</ul>"
            "<p>Built with PySide6 (Qt for Python)</p>"
        )
