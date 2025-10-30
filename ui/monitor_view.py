"""
Monitor View - Display railway layout and receive real-time updates
Modern UI with improved styling
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
                               QGraphicsScene, QLabel, QPushButton, QSpinBox,
                               QLineEdit, QGroupBox, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QFont
from PySide6.QtNetwork import QUdpSocket, QTcpServer, QTcpSocket, QHostAddress

from core.railway_system import RailwaySystem
from core.tcp_server import RailwayTCPServer, BlockStatus
from ui.rail_graphics import RailGraphicsItem
import json


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
        self.tcp_server: RailwayTCPServer = None
        self.listening = False
        
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
        """Connect railway system signals"""
        self.railway_system.block_color_changed.connect(self.on_block_color_changed)
        
        # Connect settings controller signals
        if self.settings_controller:
            self.settings_controller.network_settings_changed.connect(self.apply_network_settings)
        
    def start_network_listener(self):
        """Start the TCP server"""
        if self.listening:
            return
            
        port = self.port_spin.value()
        
        # Create and configure TCP server
        self.tcp_server = RailwayTCPServer(port=port, host="0.0.0.0")
        
        # Connect signals
        self.tcp_server.log_message.connect(self.log)
        self.tcp_server.error_occurred.connect(lambda msg: self.log(f"❌ {msg}"))
        self.tcp_server.client_connected.connect(self.on_client_connected)
        self.tcp_server.client_disconnected.connect(self.on_client_disconnected)
        self.tcp_server.block_status_update.connect(self.on_block_status_update)
        self.tcp_server.batch_status_update.connect(self.on_batch_status_update)
        
        # Start server
        if self.tcp_server.start():
            self.listening = True
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
            self.log(f"🟢 TCP Server started on 0.0.0.0:{port}")
        else:
            self.tcp_server = None
            self.log(f"❌ Failed to start TCP server on port {port}")
        
    def stop_network_listener(self):
        """Stop the TCP server"""
        if not self.listening:
            return
            
        if self.tcp_server:
            self.tcp_server.stop()
            self.tcp_server = None
            
        self.listening = False
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
        
        self.log("🔴 TCP Server stopped")
        
    def toggle_listening(self):
        """Toggle TCP server"""
        if self.listening:
            self.stop_network_listener()
        else:
            self.start_network_listener()
    
    def on_client_connected(self, client_id: str):
        """Handle new client connection"""
        if self.tcp_server:
            client_count = len(self.tcp_server.get_connected_clients())
            self.clients_label.setText(f"Connected clients: {client_count}")
    
    def on_client_disconnected(self, client_id: str):
        """Handle client disconnection"""
        if self.tcp_server:
            client_count = len(self.tcp_server.get_connected_clients())
            self.clients_label.setText(f"Connected clients: {client_count}")
    
    def on_block_status_update(self, block_id: str, status: str):
        """Handle single block status update from TCP server"""
        # Get color for status
        color = BlockStatus.get_color(status)
        
        # Update block color in railway system
        if block_id in self.railway_system.blocks:
            self.railway_system.set_block_color(block_id, color)
            self.log(f"✓ {block_id} → {status} ({color})")
        else:
            # Try to find by block_id (BL001001) instead of rail_id
            found = False
            for rail_id, block in self.railway_system.blocks.items():
                if hasattr(block, 'block_id') and block.block_id == block_id:
                    self.railway_system.set_block_color(rail_id, color)
                    self.log(f"✓ {block_id} (rail {rail_id}) → {status} ({color})")
                    found = True
                    break
            
            if not found:
                self.log(f"⚠️ Block not found: {block_id}")
    
    def on_batch_status_update(self, updates: list):
        """Handle batch status updates from TCP server"""
        success_count = 0
        for block_id, status in updates:
            color = BlockStatus.get_color(status)
            
            if block_id in self.railway_system.blocks:
                self.railway_system.set_block_color(block_id, color)
                success_count += 1
            else:
                # Try to find by block_id (BL001001)
                for rail_id, block in self.railway_system.blocks.items():
                    if hasattr(block, 'block_id') and block.block_id == block_id:
                        self.railway_system.set_block_color(rail_id, color)
                        success_count += 1
                        break
        
        self.log(f"✓ Batch update: {success_count}/{len(updates)} blocks updated")
            
    def on_block_color_changed(self, block_id: str, color: str):
        """Handle block color change"""
        # Update graphics item
        for item in self.scene.items():
            if isinstance(item, RailGraphicsItem) and item.block.id == block_id:
                item.update()
                break
                
    def test_color_change(self):
        """Test color change manually"""
        block_id = self.test_block_id.text().strip()
        color = self.test_color.text().strip()
        
        if block_id and color:
            self.apply_color_update(block_id, color)
        else:
            self.log("⚠️ Please enter both block ID and color")
            
    def reset_colors(self):
        """Reset all block colors to default"""
        count = 0
        for block_id in self.railway_system.blocks:
            self.railway_system.set_block_color(block_id, '#888888')
            count += 1
        self.log(f"↻ Reset {count} blocks to default color")
        
    def log(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def load_layout(self):
        """Load a layout from file"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        from core.json_formatter import RailwayJSONFormatter
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Layout",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
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
                    
                    self.refresh()
                    
                    # Count blocks
                    block_count = len(self.railway_system.blocks)
                    self.log(f"✓ Loaded layout with {block_count} blocks")
                    
                    QMessageBox.information(
                        self,
                        "✓ Success",
                        f"Layout loaded successfully!\n{block_count} blocks loaded."
                    )
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.log(f"❌ Failed to load layout: {str(e)}")
                QMessageBox.critical(
                    self,
                    "❌ Error",
                    f"Failed to load layout:\n{str(e)}"
                )
        
    def apply_network_settings(self, settings: dict):
        """Apply network settings from settings controller"""
        # Update TCP port (check both tcp_port and udp_port for backward compatibility)
        port = settings.get('tcp_port') or settings.get('udp_port')
        if port:
            self.port_spin.setValue(port)
            self.log(f"📡 Network settings updated: Port {port}")
        
        # If currently listening, restart with new settings
        if self.listening:
            self.log("🔄 Restarting TCP server with new settings...")
            self.stop_network_listener()
            self.start_network_listener()
    
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
        """Handle widget close"""
        self.stop_network_listener()
        super().closeEvent(event)
