"""
Monitor View - Display railway layout and receive real-time updates
Modern UI with improved styling
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
                               QGraphicsScene, QLabel, QPushButton, QSpinBox,
                               QLineEdit, QGroupBox, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QFont
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

from core.railway_system import RailwaySystem
from core.tcp_server import RailwayTCPServer, BlockStatus
from ui.rail_graphics import RailGraphicsItem
import json
import socket


class DotGridScene(QGraphicsScene):
    """Graphics scene with dot grid background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_spacing = 20
        self.dot_size = 2
        
    def drawBackground(self, painter, rect):
        """Draw dot grid background"""
        # Fill with light background
        painter.fillRect(rect, QColor("#F8F9FA"))
        
        # Set up dot pen
        dot_pen = painter.pen()
        dot_pen.setColor(QColor("#D0D7DE"))
        dot_pen.setWidth(self.dot_size)
        painter.setPen(dot_pen)
        
        # Calculate grid bounds
        left = int(rect.left()) - (int(rect.left()) % self.grid_spacing)
        top = int(rect.top()) - (int(rect.top()) % self.grid_spacing)
        
        # Draw dots
        x = left
        while x < rect.right():
            y = top
            while y < rect.bottom():
                painter.drawPoint(x, y)
                y += self.grid_spacing
            x += self.grid_spacing


# NetworkListener class removed - now using RailwayTCPServer directly


class MonitorView(QWidget):
    """Monitor view for displaying railway layout with real-time updates"""
    
    def __init__(self, railway_system: RailwaySystem, settings_controller=None):
        super().__init__()
        self.railway_system = railway_system
        self.settings_controller = settings_controller
        
        # Initialize controller (MVC pattern)
        from controllers.monitor_controller import MonitorController
        self.controller = MonitorController(railway_system)
        
        self.setup_ui()
        self.connect_signals()
        
        # Apply initial settings if controller provided
        if self.settings_controller:
            self.apply_network_settings(self.settings_controller.settings)
        
    def setup_ui(self):
        """Setup the UI layout"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Left side: Graphics view
        left_container = QFrame()
        left_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # Title
        title = QLabel("📊  Railway Monitor")
        title_font = QFont("Arial", 16, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1A202C;")
        left_layout.addWidget(title)
        
        # Graphics view with dot grid
        self.scene = DotGridScene()
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("""
            QGraphicsView {
                border: none;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)
        
        left_layout.addWidget(self.view)
        
        # Info label
        info = QLabel("💡 Real-time railway status monitoring · Read-only view")
        info.setStyleSheet("color: #718096; font-size: 11px; padding: 5px;")
        left_layout.addWidget(info)
        
        # Right side: Controls panel
        right_container = QWidget()
        right_container.setMaximumWidth(380)
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(12)
        
        # Load button
        load_btn = QPushButton("📂 Load Layout")
        load_btn.clicked.connect(self.load_layout)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #805AD5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6B46C1;
            }
            QPushButton:pressed {
                background-color: #553C9A;
            }
        """)
        right_layout.addWidget(load_btn)
        
        # Network settings
        network_card = self.create_card("🌐 TCP Server Settings")
        network_content = QVBoxLayout()
        network_content.setSpacing(10)
        
        # TCP Port
        port_layout = QHBoxLayout()
        port_label = QLabel("TCP Port:")
        port_label.setStyleSheet("color: #2D3748; font-weight: 600;")
        port_layout.addWidget(port_label)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(5555)
        self.port_spin.setStyleSheet("""
            QSpinBox {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px 10px;
                color: #2D3748;
            }
        """)
        port_layout.addWidget(self.port_spin)
        network_content.addLayout(port_layout)
        
        # Bind address selection
        bind_layout = QHBoxLayout()
        bind_label = QLabel("Bind to:")
        bind_label.setStyleSheet("color: #2D3748; font-weight: 600;")
        bind_layout.addWidget(bind_label)
        
        self.bind_address_input = QLineEdit()
        self.bind_address_input.setPlaceholderText("0.0.0.0 (all interfaces)")
        self.bind_address_input.setText("0.0.0.0")
        self.bind_address_input.setStyleSheet("""
            QLineEdit {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px 10px;
                color: #2D3748;
            }
        """)
        self.bind_address_input.setToolTip("IP address to bind to (0.0.0.0 = all interfaces)")
        bind_layout.addWidget(self.bind_address_input)
        network_content.addLayout(bind_layout)
        
        # Server address info
        # self.server_address_label = QLabel("💡 Use 0.0.0.0 to accept connections from any IP, or specify a specific interface")
        # self.server_address_label.setStyleSheet("color: #4A5568; font-size: 10px; padding: 5px;")
        # self.server_address_label.setWordWrap(True)
        # network_content.addWidget(self.server_address_label)
        
        # Host IP addresses (for Docker connection)
        # self.host_ip_label = QLabel("")
        # self.host_ip_label.setStyleSheet("""
        #     color: #2D3748; 
        #     font-size: 11px; 
        #     background-color: #EDF2F7;
        #     border-radius: 6px;
        #     padding: 8px;
        #     font-family: 'Courier New', monospace;
        # """)
        # self.host_ip_label.setWordWrap(True)
        # self.host_ip_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # network_content.addWidget(self.host_ip_label)
        self.update_host_ip_display()
        
        # Connected clients label
        self.clients_label = QLabel("Connected clients: 0")
        self.clients_label.setStyleSheet("color: #4A5568; font-size: 11px;")
        network_content.addWidget(self.clients_label)
        
        self.start_btn = QPushButton("▶ Start Listening")
        self.start_btn.clicked.connect(self.toggle_listening)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #38A169;
            }
        """)
        network_content.addWidget(self.start_btn)
        
        self.status_label = QLabel("● Not listening")
        self.status_label.setStyleSheet("""
            padding: 8px;
            background-color: #FFF5F5;
            color: #C53030;
            border-radius: 6px;
            font-weight: 600;
        """)
        network_content.addWidget(self.status_label)
        
        self.add_to_card(network_card, network_content)
        right_layout.addWidget(network_card)
        
        # # Packet format info
        # format_card = self.create_card("📋 Packet Format")
        # format_content = QVBoxLayout()
        # format_info = QLabel(
        #     '<b>JSON format:</b><br>'
        #     '<code style="background: #F7FAFC; padding: 2px 4px; border-radius: 3px;">'
        #     '{"block_id": "rail_0001", "color": "#FF0000"}'
        #     '</code><br><br>'
        #     '<b>Simple format:</b><br>'
        #     '<code style="background: #F7FAFC; padding: 2px 4px; border-radius: 3px;">'
        #     'rail_0001:red'
        #     '</code>'
        # )
        # format_info.setWordWrap(True)
        # format_info.setStyleSheet("font-size: 11px; color: #4A5568; line-height: 1.5;")
        # format_content.addWidget(format_info)
        # self.add_to_card(format_card, format_content)
        # right_layout.addWidget(format_card)
        
        # Test controls
        # test_card = self.create_card("🧪 Test Controls")
        # test_content = QVBoxLayout()
        # test_content.setSpacing(8)
        
        # test_content.addWidget(QLabel("Block ID:"))
        # self.test_block_id = QLineEdit()
        # self.test_block_id.setPlaceholderText("rail_0001")
        # self.test_block_id.setStyleSheet(self.get_input_style())
        # test_content.addWidget(self.test_block_id)
        
        # test_content.addWidget(QLabel("Color:"))
        # self.test_color = QLineEdit()
        # self.test_color.setPlaceholderText("#FF0000 or red")
        # self.test_color.setStyleSheet(self.get_input_style())
        # test_content.addWidget(self.test_color)
        
        # test_btn = QPushButton("Apply Color")
        # test_btn.clicked.connect(self.test_color_change)
        # test_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #4299E1;
        #         color: white;
        #         border: none;
        #         border-radius: 6px;
        #         padding: 8px;
        #         font-weight: 600;
        #     }
        #     QPushButton:hover {
        #         background-color: #3182CE;
        #     }
        # """)
        # test_content.addWidget(test_btn)
        
        # reset_btn = QPushButton("↻ Reset All Colors")
        # reset_btn.clicked.connect(self.reset_colors)
        # reset_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #F7FAFC;
        #         color: #2D3748;
        #         border: 2px solid #E2E8F0;
        #         border-radius: 6px;
        #         padding: 8px;
        #         font-weight: 600;
        #     }
        #     QPushButton:hover {
        #         background-color: #EDF2F7;
        #     }
        # """)
        # test_content.addWidget(reset_btn)
        
        # self.add_to_card(test_card, test_content)
        # right_layout.addWidget(test_card)
        
        # Log viewer
        log_card = self.create_card("📝 Network Log")
        log_content = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(180)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                color: #2D3748;
            }
        """)
        log_content.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #F7FAFC;
                color: #718096;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #EDF2F7;
            }
        """)
        log_content.addWidget(clear_log_btn)
        
        self.add_to_card(log_card, log_content)
        right_layout.addWidget(log_card)
        
        right_layout.addStretch()
        
        # Add to main layout
        main_layout.addWidget(left_container, 3)
        main_layout.addWidget(right_container, 1)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #E8EBF0;
            }
        """)
        
    def create_card(self, title: str) -> QFrame:
        """Create a styled card container"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #2D3748; font-weight: bold; font-size: 13px;")
        layout.addWidget(title_label)
        
        return card
        
    def add_to_card(self, card: QFrame, content_layout: QVBoxLayout):
        """Add content to a card"""
        card.layout().addLayout(content_layout)
        
    def get_input_style(self):
        """Get input field styling"""
        return """
            QLineEdit {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
                color: #2D3748;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4299E1;
            }
        """
        
    def connect_signals(self):
        """Connect signals - View listens to Controller and Model"""
        # Listen to Model (RailwaySystem) for data changes
        self.railway_system.block_color_changed.connect(self.on_block_color_changed)
        
        # Listen to Controller for business logic events
        self.controller.log_message.connect(self.append_log)
        self.controller.tcp_server_started.connect(self.on_tcp_server_started)
        self.controller.tcp_server_stopped.connect(self.on_tcp_server_stopped)
        self.controller.tcp_server_error.connect(self.on_tcp_server_error)
        self.controller.client_count_changed.connect(self.on_client_count_changed)
        
        # Connect settings controller signals
        if self.settings_controller:
            self.settings_controller.network_settings_changed.connect(self.apply_network_settings)
    
    def update_host_ip_display(self):
        """Update the display of host IP addresses for Docker connection"""
        try:
            # Get hostname
            hostname = socket.gethostname()
            
            # Get all IP addresses
            ip_addresses = []
            
            # Try to get the main IP address (connected to internet)
            try:
                # Create a socket to determine the main IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                main_ip = s.getsockname()[0]
                s.close()
                ip_addresses.append(("Primary", main_ip))
            except:
                pass
            
            # Get all network interface IPs
            try:
                all_ips = socket.getaddrinfo(hostname, None)
                for ip_info in all_ips:
                    ip = ip_info[4][0]
                    # Filter out IPv6, localhost, and duplicates
                    if ':' not in ip and ip != '127.0.0.1' and ip not in [addr[1] for addr in ip_addresses]:
                        ip_addresses.append(("Network", ip))
            except:
                pass
            
            # # Display the IP addresses
            # if ip_addresses:
            #     ip_text = "🔗 <b>Connect from Docker using:</b><br>"
            #     for label, ip in ip_addresses:
            #         ip_text += f"• {ip}:{self.port_spin.value()}<br>"
            #     ip_text += "<br><small>Copy and use in your Docker container</small>"
            #     self.host_ip_label.setText(ip_text)
            # else:
            #     self.host_ip_label.setText("⚠️ Could not detect IP addresses")
                
        except Exception as e:
            self.host_ip_label.setText(f"⚠️ Error detecting IP: {str(e)}")
        
    def start_network_listener(self):
        """Delegate to controller to start TCP server (View only triggers action)"""
        port = self.port_spin.value()
        bind_address = self.bind_address_input.text().strip() or "0.0.0.0"
        self.controller.start_tcp_server(port=port, host=bind_address)
        
    def stop_network_listener(self):
        """Delegate to controller to stop TCP server (View only triggers action)"""
        self.controller.stop_tcp_server()
        
    def toggle_listening(self):
        """Toggle TCP server (View only triggers action)"""
        if self.controller.is_listening:
            self.stop_network_listener()
        else:
            self.start_network_listener()
    
    # Controller Event Handlers (View responds to Controller events)
    # ---------------------------------------------------------------
    
    def on_tcp_server_started(self, port: int):
        """Handle TCP server started event from controller"""
        self.start_btn.setText("⏸ Stop Server")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #C53030;
            }
        """)
        self.status_label.setText(f"● Server running on port {port}")
        self.status_label.setStyleSheet("""
            padding: 8px;
            background-color: #F0FFF4;
            color: #22543D;
            border-radius: 6px;
            font-weight: 600;
        """)
        self.port_spin.setEnabled(False)
        self.update_host_ip_display()
    
    def on_tcp_server_stopped(self):
        """Handle TCP server stopped event from controller"""
        self.start_btn.setText("▶ Start Server")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #38A169;
            }
        """)
        self.status_label.setText("● Server stopped")
        self.status_label.setStyleSheet("""
            padding: 8px;
            background-color: #FFF5F5;
            color: #C53030;
            border-radius: 6px;
            font-weight: 600;
        """)
        self.port_spin.setEnabled(True)
        self.clients_label.setText("Connected clients: 0")
    
    def on_tcp_server_error(self, error_msg: str):
        """Handle TCP server error from controller"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "TCP Server Error", error_msg)
    
    def on_client_count_changed(self, count: int):
        """Handle client count change from controller"""
        self.clients_label.setText(f"Connected clients: {count}")
            
    def on_block_color_changed(self, block_id: str, color: str):
        """Handle block color change"""
        # Update graphics item
        for item in self.scene.items():
            if isinstance(item, RailGraphicsItem) and item.block.id == block_id:
                item.update()
                break
                
    # These methods are commented out as they're not used in current UI
    # def test_color_change(self):
    #     """Test color change manually (delegate to controller)"""
    #     block_id = self.test_block_id.text().strip()
    #     color = self.test_color.text().strip()
    #     self.controller.test_color_change(block_id, color)
            
    # def reset_colors(self):
    #     """Reset all block colors to default (delegate to controller)"""
    #     self.controller.reset_all_colors()
        
    def append_log(self, message: str):
        """Add message to log (View only displays, message formatting done in Controller)"""
        self.log_text.append(message)
    
    def load_layout(self):
        """Load a layout from file (View only handles UI, Controller handles logic)"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Layout",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Delegate to controller
            success, message, block_count = self.controller.load_layout(file_path)
            
            if success:
                self.refresh()
                QMessageBox.information(self, "✓ Success", message)
            else:
                QMessageBox.critical(self, "❌ Error", message)
        
    def apply_network_settings(self, settings: dict):
        """Apply network settings from settings controller"""
        # Update TCP port
        port = settings.get('tcp_port', 5555)
        self.port_spin.setValue(port)
        
        # Update bind address
        bind_address = settings.get('tcp_bind_address', '0.0.0.0')
        self.bind_address_input.setText(bind_address)
        
        # Log the update (only if log widget exists)
        if hasattr(self, 'log_text'):
            self.append_log(f"📡 Network settings updated: Port {port}, Bind address {bind_address}")
        
        # If currently listening, restart with new settings
        if self.controller.is_listening:
            self.controller.stop_tcp_server()
            self.controller.start_tcp_server(port=port, host=bind_address)
    
    def refresh(self):
        """Refresh the view from railway system"""
        from PySide6.QtWidgets import QGraphicsItem
        
        self.scene.clear()
        for block_id in self.railway_system.blocks:
            block = self.railway_system.blocks[block_id]
            graphics_item = RailGraphicsItem(block, self.railway_system)
            graphics_item.setFlag(QGraphicsItem.ItemIsMovable, False)
            graphics_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.scene.addItem(graphics_item)
            
    def closeEvent(self, event):
        """Handle widget close (cleanup through controller)"""
        if self.controller.is_listening:
            self.controller.stop_tcp_server()
        super().closeEvent(event)
