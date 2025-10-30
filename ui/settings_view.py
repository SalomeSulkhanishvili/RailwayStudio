"""
Settings view - Modern application settings and preferences
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QColorDialog, QSpinBox, QGroupBox,
                               QFormLayout, QScrollArea, QLineEdit, QFrame, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


class SettingsView(QWidget):
    """Settings view for configuring application preferences"""
    
    # Signals
    settings_changed = Signal(dict)
    
    def __init__(self, settings_controller=None, parent=None):
        super().__init__(parent)
        
        # Use controller if provided, otherwise create local settings
        self.settings_controller = settings_controller
        if settings_controller:
            self.settings = settings_controller.settings
        else:
            # Fallback default settings
            self.settings = {
                'rail_color': '#888888',
                'connection_color': '#00FF00',
                'background_color': '#FFFFFF',
                'selected_color': '#FF0000',
                'grid_size': 20,
                'snap_distance': 30,
                'udp_port': 5000,
                'ip_address': '192.168.1.100',
                'gateway': '192.168.1.1',
                'subnet_mask': '255.255.255.0',
                'dns_server': '8.8.8.8',
            }
        
        # Temporary settings (for preview before applying)
        self.temp_settings = self.settings.copy()
        
        # Store color buttons and input fields for updates
        self.color_buttons = {}
        self.input_fields = {}
        
        self.init_ui()
        
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
        
        title = QLabel("⚙️  Settings & Configuration")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #1F2937;")
        header_layout.addWidget(title)
        
        # subtitle = QLabel("Configure application preferences and network settings")
        # subtitle.setFont(QFont("Arial", 12))
        # subtitle.setStyleSheet("color: #6B7280;")
        # header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header)
        
        # Scrollable area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # # Color Settings Group
        # color_group = self.create_color_settings_group()
        # scroll_layout.addWidget(color_group)
        
        # # Editor Settings Group
        # editor_group = self.create_editor_settings_group()
        # scroll_layout.addWidget(editor_group)
        
        # Ethernet Configuration Group (includes UDP port)
        ethernet_group = self.create_ethernet_config_group()
        scroll_layout.addWidget(ethernet_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Action Buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        reset_btn = QPushButton("↻ Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: 2px solid #E5E7EB;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: 2px solid #E5E7EB;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_changes)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("✓ Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
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
        apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(apply_btn)
        
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        self.setStyleSheet("QWidget { background-color: #F3F4F6; }")
        
    def create_card_group(self, title: str, icon: str = "") -> tuple:
        """Create a styled card group box"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        main_layout = QVBoxLayout(card)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(f"{icon} {title}" if icon else title)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: #1F2937;")
        main_layout.addWidget(title_label)
        
        # Form layout for content
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        return card, main_layout, form_layout
        
    def create_color_settings_group(self):
        """Create color settings group"""
        card, main_layout, form_layout = self.create_card_group("Color Settings", "🎨")
        
        # Rail Color
        rail_color_btn = self.create_color_button('rail_color', "Default Rail Color")
        form_layout.addRow(self.create_label("Rail Color:"), rail_color_btn)
        self.color_buttons['rail_color'] = rail_color_btn
        
        # Connection Color
        conn_color_btn = self.create_color_button('connection_color', "Connection Line Color")
        form_layout.addRow(self.create_label("Connection:"), conn_color_btn)
        self.color_buttons['connection_color'] = conn_color_btn
        
        # Background Color
        bg_color_btn = self.create_color_button('background_color', "Editor Background")
        form_layout.addRow(self.create_label("Background:"), bg_color_btn)
        self.color_buttons['background_color'] = bg_color_btn
        
        # Selected Color
        sel_color_btn = self.create_color_button('selected_color', "Selected Rail Highlight")
        form_layout.addRow(self.create_label("Selected:"), sel_color_btn)
        self.color_buttons['selected_color'] = sel_color_btn
        
        main_layout.addLayout(form_layout)
        return card
        
    def create_editor_settings_group(self):
        """Create editor settings group"""
        card, main_layout, form_layout = self.create_card_group("Editor Settings", "✏️")
        
        # Grid Size
        grid_spin = QSpinBox()
        grid_spin.setRange(10, 50)
        grid_spin.setValue(self.temp_settings['grid_size'])
        grid_spin.setSuffix(" px")
        grid_spin.setStyleSheet(self.get_input_style())
        grid_spin.valueChanged.connect(lambda v: self.update_temp_setting('grid_size', v))
        form_layout.addRow(self.create_label("Grid Spacing:"), grid_spin)
        self.input_fields['grid_size'] = grid_spin
        
        # Snap Distance
        snap_spin = QSpinBox()
        snap_spin.setRange(10, 100)
        snap_spin.setValue(self.temp_settings['snap_distance'])
        snap_spin.setSuffix(" px")
        snap_spin.setStyleSheet(self.get_input_style())
        snap_spin.valueChanged.connect(lambda v: self.update_temp_setting('snap_distance', v))
        form_layout.addRow(self.create_label("Snap Distance:"), snap_spin)
        self.input_fields['snap_distance'] = snap_spin
        
        main_layout.addLayout(form_layout)
        return card
        
    def create_network_settings_group(self):
        """Create network settings group - placeholder for future network features"""
        # This section is kept for potential future network monitoring settings
        # UDP port has been moved to Ethernet Configuration
        return None
        
    def create_ethernet_config_group(self):
        """Create ethernet configuration group"""
        card, main_layout, form_layout = self.create_card_group("Ethernet Configuration", "🔌")
        
        # UDP Port (for monitoring)
        port_spin = QSpinBox()
        port_spin.setRange(1024, 65535)
        port_spin.setValue(self.temp_settings['udp_port'])
        port_spin.setStyleSheet(self.get_input_style())
        port_spin.valueChanged.connect(lambda v: self.update_temp_setting('udp_port', v))
        form_layout.addRow(self.create_label("UDP Port:"), port_spin)
        self.input_fields['udp_port'] = port_spin
        
        # IP Address
        ip_input = QLineEdit()
        ip_input.setText(self.temp_settings['ip_address'])
        ip_input.setPlaceholderText("192.168.1.100")
        ip_input.setStyleSheet(self.get_input_style())
        ip_input.textChanged.connect(lambda v: self.update_temp_setting('ip_address', v))
        form_layout.addRow(self.create_label("IP Address:"), ip_input)
        self.input_fields['ip_address'] = ip_input
        
        # Subnet Mask
        subnet_input = QLineEdit()
        subnet_input.setText(self.temp_settings['subnet_mask'])
        subnet_input.setPlaceholderText("255.255.255.0")
        subnet_input.setStyleSheet(self.get_input_style())
        subnet_input.textChanged.connect(lambda v: self.update_temp_setting('subnet_mask', v))
        form_layout.addRow(self.create_label("Subnet Mask:"), subnet_input)
        self.input_fields['subnet_mask'] = subnet_input
        
        # Gateway
        gateway_input = QLineEdit()
        gateway_input.setText(self.temp_settings['gateway'])
        gateway_input.setPlaceholderText("192.168.1.1")
        gateway_input.setStyleSheet(self.get_input_style())
        gateway_input.textChanged.connect(lambda v: self.update_temp_setting('gateway', v))
        form_layout.addRow(self.create_label("Gateway:"), gateway_input)
        self.input_fields['gateway'] = gateway_input
        
        # DNS Server
        dns_input = QLineEdit()
        dns_input.setText(self.temp_settings['dns_server'])
        dns_input.setPlaceholderText("8.8.8.8")
        dns_input.setStyleSheet(self.get_input_style())
        dns_input.textChanged.connect(lambda v: self.update_temp_setting('dns_server', v))
        form_layout.addRow(self.create_label("DNS Server:"), dns_input)
        self.input_fields['dns_server'] = dns_input
        
        hint = QLabel(
            "⚠️ These settings configure the application's network interface. "
            "Changes will be applied when you click 'Apply Changes' button."
        )
        hint.setStyleSheet("color: #F59E0B; font-size: 11px; font-style: italic; padding: 10px; "
                          "background-color: #FEF3C7; border-radius: 6px;")
        hint.setWordWrap(True)
        main_layout.addWidget(hint)
        
        main_layout.addLayout(form_layout)
        return card
        
    def create_label(self, text: str) -> QLabel:
        """Create a styled form label"""
        label = QLabel(text)
        label.setStyleSheet("color: #374151; font-weight: 600; font-size: 12px;")
        return label
        
    def get_input_style(self):
        """Get input field styling"""
        return """
            QLineEdit, QSpinBox {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px 12px;
                color: #1F2937;
                font-size: 12px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #3B82F6;
                background-color: #FFFFFF;
            }
        """
        
    def create_color_button(self, setting_key, tooltip):
        """Create a color picker button"""
        btn = QPushButton()
        btn.setFixedSize(120, 36)
        btn.setToolTip(tooltip)
        color = self.temp_settings[setting_key]
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #E5E7EB;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border: 2px solid #3B82F6;
            }}
        """)
        btn.clicked.connect(lambda: self.pick_color(setting_key, btn))
        return btn
        
    def pick_color(self, setting_key, button):
        """Open color picker dialog"""
        current_color = QColor(self.temp_settings[setting_key])
        color = QColorDialog.getColor(current_color, self, f"Choose {setting_key}")
        
        if color.isValid():
            color_hex = color.name()
            self.temp_settings[setting_key] = color_hex
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 2px solid #E5E7EB;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    border: 2px solid #3B82F6;
                }}
            """)
            
    def update_temp_setting(self, key, value):
        """Update a temporary setting value (not applied yet)"""
        self.temp_settings[key] = value
        
    def apply_changes(self):
        """Apply all pending changes"""
        # Use controller if available
        if self.settings_controller:
            success, message = self.settings_controller.apply_settings(self.temp_settings)
            if success:
                self.settings = self.settings_controller.settings
                QMessageBox.information(self, "✓ Success", message)
            else:
                QMessageBox.critical(self, "❌ Error", message)
        else:
            # Fallback: local settings
            self.settings = self.temp_settings.copy()
            self.settings_changed.emit(self.settings)
            QMessageBox.information(
                self,
                "✓ Settings Applied",
                "All settings have been applied successfully!"
            )
        
    def cancel_changes(self):
        """Cancel all pending changes"""
        self.temp_settings = self.settings.copy()
        
        # Reset all color buttons
        for key, button in self.color_buttons.items():
            color = self.settings[key]
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #E5E7EB;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    border: 2px solid #3B82F6;
                }}
            """)
        
        QMessageBox.information(
            self,
            "Changes Cancelled",
            "All changes have been discarded."
        )
        
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults using controller if available
            if self.settings_controller:
                defaults = self.settings_controller.reset_to_defaults()
                self.settings = defaults.copy()
                self.temp_settings = defaults.copy()
            else:
                # Fallback: local defaults
                self.settings = {
                    'rail_color': '#888888',
                    'connection_color': '#FF5252',
                    'selected_color': '#4A90E2',
                    'grid_size': 20,
                    'snap_distance': 30,
                    'udp_port': 5000,
                    'ip_address': '192.168.1.100',
                    'gateway': '192.168.1.1',
                    'subnet_mask': '255.255.255.0',
                    'dns_server': '8.8.8.8',
                }
                self.temp_settings = self.settings.copy()
            
            # Update all UI fields with reset values from settings
            # Update spinboxes
            if 'grid_size' in self.input_fields and 'grid_size' in self.settings:
                self.input_fields['grid_size'].setValue(self.settings['grid_size'])
            if 'snap_distance' in self.input_fields and 'snap_distance' in self.settings:
                self.input_fields['snap_distance'].setValue(self.settings['snap_distance'])
            if 'udp_port' in self.input_fields and 'udp_port' in self.settings:
                self.input_fields['udp_port'].setValue(self.settings['udp_port'])
            
            # Update line edits
            if 'ip_address' in self.input_fields and 'ip_address' in self.settings:
                self.input_fields['ip_address'].setText(self.settings['ip_address'])
            if 'gateway' in self.input_fields and 'gateway' in self.settings:
                self.input_fields['gateway'].setText(self.settings['gateway'])
            if 'subnet_mask' in self.input_fields and 'subnet_mask' in self.settings:
                self.input_fields['subnet_mask'].setText(self.settings['subnet_mask'])
            if 'dns_server' in self.input_fields and 'dns_server' in self.settings:
                self.input_fields['dns_server'].setText(self.settings['dns_server'])
            
            # Update color buttons with reset values
            for key, button in self.color_buttons.items():
                if key in self.settings:
                    color = self.settings[key]
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            border: 2px solid #E5E7EB;
                            border-radius: 6px;
                        }}
                        QPushButton:hover {{
                            border: 2px solid #3B82F6;
                        }}
                    """)
            
            # Only emit if not using controller (controller already emits)
            if not self.settings_controller:
                self.settings_changed.emit(self.settings)
            
            QMessageBox.information(
                self,
                "Settings Reset",
                "All settings have been reset to default values!"
            )
