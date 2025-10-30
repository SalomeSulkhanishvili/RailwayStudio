"""
Files view - Modern file browser for layout management
Refactored to use FilesController for business logic
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem,
                               QMessageBox, QFileDialog, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import os
from controllers.files_controller import FilesController
from ui.styles import get_primary_button_style, get_secondary_button_style, get_danger_button_style


class FilesView(QWidget):
    """Files view for browsing and managing layout files"""
    
    # Signals
    file_selected = Signal(str)  # Emits file path when file is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use FilesController for all file operations
        self.controller = FilesController('layouts')
        self.current_directory = self.controller.get_layouts_directory()
        self.init_ui()
        self.refresh_file_list()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(12)
        
        title = QLabel("📁 Layout Files")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #1F2937;")
        header_layout.addWidget(title)
        
        # Directory section
        dir_container = QFrame()
        dir_container.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        dir_layout = QHBoxLayout(dir_container)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        
        dir_icon = QLabel("📂")
        dir_icon.setFont(QFont("Arial", 16))
        dir_layout.addWidget(dir_icon)
        
        self.dir_label = QLabel(self.current_directory)
        self.dir_label.setStyleSheet("color: #4B5563; font-size: 11px; font-family: monospace;")
        self.dir_label.setWordWrap(True)
        dir_layout.addWidget(self.dir_label, 1)
        
        change_dir_btn = QPushButton("Change")
        change_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #374151;
                border: 2px solid #D1D5DB;
                padding: 6px 16px;
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-color: #9CA3AF;
            }
        """)
        change_dir_btn.clicked.connect(self.change_directory)
        dir_layout.addWidget(change_dir_btn)
        
        header_layout.addWidget(dir_container)
        
        main_layout.addWidget(header)
        
        # File list container
        list_container = QFrame()
        list_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setSpacing(10)
        
        list_title = QLabel("Available Layouts")
        list_title.setFont(QFont("Arial", 13, QFont.Bold))
        list_title.setStyleSheet("color: #374151;")
        list_layout.addWidget(list_title)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                color: #1F2937;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E5E7EB;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #EFF6FF;
            }
            QListWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
                border: none;
            }
        """)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        list_layout.addWidget(self.file_list)
        
        main_layout.addWidget(list_container)
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: 2px solid #E5E7EB;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_file_list)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 2px solid #FCA5A5;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FEE2E2;
                border-color: #F87171;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_file)
        button_layout.addWidget(delete_btn)
        
        open_btn = QPushButton("📂 Open Selected")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        open_btn.clicked.connect(self.open_selected_file)
        button_layout.addWidget(open_btn)
        
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #F3F4F6; }")
        
    def refresh_file_list(self):
        """Refresh the list of JSON files - UI only, uses controller"""
        self.file_list.clear()
        
        # Get files from controller
        files = self.controller.list_files(self.current_directory)
        
        if not files:
            item = QListWidgetItem("📭 No JSON files found in this directory")
            item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            item.setForeground(Qt.gray)
            self.file_list.addItem(item)
            return
        
        # Display files (already sorted by controller)
        for file_info in files:
            # Format file size
            file_size = file_info.size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Format display with groups and blocks info
            if file_info.groups > 0 and file_info.blocks > 0:
                display_text = f"📊 {file_info.name}\n   └─ {file_info.groups} groups · {file_info.blocks} blocks · {size_str} · {file_info.modified.strftime('%Y-%m-%d %H:%M')}"
            else:
                display_text = f"📄 {file_info.name}\n   └─ {size_str} · {file_info.modified.strftime('%Y-%m-%d %H:%M')}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, file_info.path)  # Store full path
            self.file_list.addItem(item)
            
    def change_directory(self):
        """Change the current directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Directory",
            self.current_directory
        )
        
        if directory:
            self.current_directory = directory
            self.dir_label.setText(self.current_directory)
            self.refresh_file_list()
            
    def on_file_double_clicked(self, item):
        """Handle double-click on file"""
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.file_selected.emit(file_path)
            
    def open_selected_file(self):
        """Open the selected file"""
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            if file_path:
                self.file_selected.emit(file_path)
            else:
                QMessageBox.information(self, "Info", "No file selected")
        else:
            QMessageBox.information(self, "Info", "Please select a file first")
            
    def delete_selected_file(self):
        """Delete the selected file - UI only, uses controller"""
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Info", "Please select a file first")
            return
            
        file_path = current_item.data(Qt.UserRole)
        if not file_path:
            return
            
        # Get filename for display
        file_name = os.path.basename(file_path)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "⚠️ Confirm Delete",
            f"Are you sure you want to permanently delete:\n\n{file_name}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delegate to controller
            success, message = self.controller.delete_file(file_path)
            
            if success:
                self.refresh_file_list()
                QMessageBox.information(self, "✓ Success", message)
            else:
                QMessageBox.critical(self, "❌ Error", message)
