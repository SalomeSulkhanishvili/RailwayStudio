"""
Home view - Simple welcome page with better colors
Refactored to use centralized styles from theme
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import COLORS


class HomeView(QWidget):
    """Home/Welcome view with application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("Welcome to RailwayStudio")
        title_font = QFont("Arial", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Feature 1: Build layouts
        feature1_layout = QVBoxLayout()
        feature1_layout.setSpacing(10)
        
        feature1_icon = QLabel("🎯")
        feature1_icon.setFont(QFont("Arial", 32))
        feature1_icon.setStyleSheet("background: transparent;")
        feature1_layout.addWidget(feature1_icon)
        
        feature1_title = QLabel("Build layouts with track blocks, turnouts, and signals")
        feature1_title.setFont(QFont("Arial", 16, QFont.Bold))
        feature1_title.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        feature1_layout.addWidget(feature1_title)
        
        feature1_desc = QLabel(
            "Drag and drop rail components to create your railway layout.\n"
            "Connect tracks, add turnouts, and organize your railway system visually."
        )
        feature1_desc.setFont(QFont("Arial", 12))
        feature1_desc.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        feature1_desc.setWordWrap(True)
        feature1_layout.addWidget(feature1_desc)
        
        layout.addLayout(feature1_layout)
        layout.addSpacing(10)
        
        # Feature 2: Save and load
        feature2_layout = QVBoxLayout()
        feature2_layout.setSpacing(10)
        
        feature2_icon = QLabel("💾")
        feature2_icon.setFont(QFont("Arial", 32))
        feature2_icon.setStyleSheet("background: transparent;")
        feature2_layout.addWidget(feature2_icon)
        
        feature2_title = QLabel("Save and load layouts in JSON format")
        feature2_title.setFont(QFont("Arial", 16, QFont.Bold))
        feature2_title.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        feature2_layout.addWidget(feature2_title)
        
        feature2_desc = QLabel(
            "Export your railway layouts to JSON files with full track connections.\n"
            "Load and continue editing your saved layouts at any time."
        )
        feature2_desc.setFont(QFont("Arial", 12))
        feature2_desc.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        feature2_desc.setWordWrap(True)
        feature2_layout.addWidget(feature2_desc)
        
        layout.addLayout(feature2_layout)
        layout.addSpacing(10)
        
        # Feature 3: Monitor
        feature3_layout = QVBoxLayout()
        feature3_layout.setSpacing(10)
        
        feature3_icon = QLabel("🌐")
        feature3_icon.setFont(QFont("Arial", 32))
        feature3_icon.setStyleSheet("background: transparent;")
        feature3_layout.addWidget(feature3_icon)
        
        feature3_title = QLabel("Monitor and update your layout in real-time via Ethernet")
        feature3_title.setFont(QFont("Arial", 16, QFont.Bold))
        feature3_title.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        feature3_layout.addWidget(feature3_title)
        
        feature3_desc = QLabel(
            "Connect to your railway control system via TCP network.\n"
            "See real-time updates of train positions and track status."
        )
        feature3_desc.setFont(QFont("Arial", 12))
        feature3_desc.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        feature3_desc.setWordWrap(True)
        feature3_layout.addWidget(feature3_desc)
        
        layout.addLayout(feature3_layout)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Set layout
        self.setLayout(layout)
        
        # Set background color - clean light background using theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
