"""
Editor View - Railway layout editor with drag and drop
Modern UI with dot grid background
Refactored to use EditorController for business logic and centralized styles
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
                               QGraphicsScene, QToolBar, QPushButton, QLabel,
                               QComboBox, QSpinBox, QGroupBox, QFrame, QFileDialog,
                               QMessageBox)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from core.railway_system import RailwaySystem
from ui.rail_graphics import RailGraphicsItem
from controllers.editor_controller import EditorController
from ui.styles import (
    COLORS, get_primary_button_style, get_secondary_button_style,
    get_accent_button_style, get_danger_button_style,
    get_toggle_button_style, get_combo_box_style, get_button_style
)


class DotGridScene(QGraphicsScene):
    """Graphics scene with dot grid background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_spacing = 20  # Spacing between dots in pixels
        self.dot_size = 2      # Size of each dot
        self.show_grid = True
        
    def drawBackground(self, painter, rect):
        """Draw dot grid background"""
        # Fill with light background
        painter.fillRect(rect, QColor("#F8F9FA"))
        
        if not self.show_grid:
            return
        
        # Set up dot pen
        dot_pen = QPen(QColor("#D0D7DE"))
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
        
    def set_grid_color_from_theme(self):
        """Use color from centralized theme"""
        # Grid colors are already handled in drawBackground
        # This method is for future theme updates
        pass


class EditorView(QWidget):
    """Editor view for designing railway layouts"""
    
    def __init__(self, railway_system: RailwaySystem):
        super().__init__()
        self.railway_system = railway_system
        self.controller = EditorController(railway_system)  # Business logic controller
        self.selected_rail_type = 'straight'
        self.selected_length = 100
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title and toolbar container
        header = self.create_header()
        layout.addWidget(header)
        
        # Graphics view for railway layout with dot grid
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
        
        # Modern styling for the view
        self.view.setStyleSheet("""
            QGraphicsView {
                border: none;
                border-radius: 12px;
                background-color: #F8F9FA;
            }
        """)
        
        # Enable mouse tracking
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)
        
        layout.addWidget(self.view)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #E8EBF0;
            }
        """)
        
    def create_header(self) -> QWidget:
        """Create modern header with title and toolbar"""
        header_widget = QFrame()
        header_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(12)
        
        # Title row
        title_layout = QHBoxLayout()
        
        title = QLabel("✏️  Railway Layout Editor")
        title_font = QFont("Arial", 18, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1A202C; padding: 0;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Instructions
        instructions = QLabel("💡 Click to place · Drag red dots to connect · Double-click to disconnect · Right-click for options")
        instructions.setStyleSheet("color: #718096; font-size: 12px;")
        title_layout.addWidget(instructions)
        
        header_layout.addLayout(title_layout)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        # Rail type label
        type_label = QLabel("Rail Type:")
        type_label.setStyleSheet("color: #2D3748; font-weight: 600; font-size: 13px;")
        toolbar_layout.addWidget(type_label)
        
        # Rail type selector
        self.rail_type_combo = QComboBox()
        self.rail_type_combo.addItems(['Straight', 'Curved', 'Switch Left', 'Switch Right'])
        self.rail_type_combo.currentTextChanged.connect(self.on_rail_type_changed)
        self.rail_type_combo.setStyleSheet(get_combo_box_style())
        toolbar_layout.addWidget(self.rail_type_combo)
        
        # Length label
        length_label = QLabel("Length:")
        length_label.setStyleSheet("color: #2D3748; font-weight: 600; font-size: 13px; margin-left: 10px;")
        toolbar_layout.addWidget(length_label)
        
        # Length selector
        self.length_spin = QSpinBox()
        self.length_spin.setRange(50, 300)
        self.length_spin.setValue(100)
        self.length_spin.setSingleStep(10)
        self.length_spin.setSuffix(" px")
        self.length_spin.valueChanged.connect(self.on_length_changed)
        self.length_spin.setStyleSheet("""
            QSpinBox {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #2D3748;
                font-size: 13px;
                min-width: 90px;
            }
            QSpinBox:hover {
                border-color: #CBD5E0;
                background-color: #EDF2F7;
            }
        """)
        toolbar_layout.addWidget(self.length_spin)
        
        toolbar_layout.addStretch()
        
        # Grid toggle
        self.grid_btn = QPushButton("⊞ Grid")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        self.grid_btn.toggled.connect(self.toggle_grid)
        self.grid_btn.setStyleSheet(get_toggle_button_style())
        toolbar_layout.addWidget(self.grid_btn)
        
        # Save button
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_layout)
        save_btn.setToolTip("Save layout to file")
        save_btn.setStyleSheet(get_secondary_button_style())
        toolbar_layout.addWidget(save_btn)
        
        # Load button
        load_btn = QPushButton("📂 Load")
        load_btn.clicked.connect(self.load_layout)
        load_btn.setToolTip("Load layout from file")
        load_btn.setStyleSheet(get_accent_button_style())
        toolbar_layout.addWidget(load_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_all)
        clear_btn.setStyleSheet(get_danger_button_style())
        toolbar_layout.addWidget(clear_btn)
        
        # Auto-create groups button
        groups_btn = QPushButton("✓ Auto-Create Groups")
        groups_btn.clicked.connect(self.auto_create_groups)
        groups_btn.setToolTip("Automatically create groups of connected rails")
        groups_btn.setStyleSheet(get_primary_button_style())
        toolbar_layout.addWidget(groups_btn)
        
        header_layout.addLayout(toolbar_layout)
        
        return header_widget
        
    def connect_signals(self):
        """Connect railway system signals"""
        self.railway_system.block_added.connect(self.on_block_added)
        self.railway_system.block_removed.connect(self.on_block_removed)
        self.railway_system.system_cleared.connect(self.on_system_cleared)
        
    def on_rail_type_changed(self, text: str):
        """Handle rail type selection change"""
        type_map = {
            'Straight': 'straight',
            'Curved': 'curved',
            'Switch Left': 'switch_left',
            'Switch Right': 'switch_right'
        }
        self.selected_rail_type = type_map.get(text, 'straight')
        
    def on_length_changed(self, value: int):
        """Handle length change"""
        self.selected_length = value
        
    def mousePressEvent(self, event):
        """Handle mouse press in the view"""
        # Map to scene coordinates
        scene_pos = self.view.mapToScene(self.view.mapFromGlobal(event.globalPos()))
        
        if event.button() == Qt.LeftButton:
            # Check if clicking on background (not on an item)
            item = self.scene.itemAt(scene_pos, self.view.transform())
            if item is None:
                # Add new rail at clicked position
                self.add_rail_at_position(scene_pos.x(), scene_pos.y())
                
        super().mousePressEvent(event)
        
    def add_rail_at_position(self, x: float, y: float):
        """Add a rail at the specified position"""
        block_id = self.railway_system.add_block(
            self.selected_rail_type, x, y, 0, self.selected_length
        )
        
    def on_block_added(self, block_id: str):
        """Handle block added to system"""
        block = self.railway_system.blocks.get(block_id)
        if block:
            # Create graphics item for this block
            graphics_item = RailGraphicsItem(block, self.railway_system)
            self.scene.addItem(graphics_item)
            
    def on_block_removed(self, block_id: str):
        """Handle block removed from system"""
        # Find and remove graphics item
        for item in self.scene.items():
            if isinstance(item, RailGraphicsItem) and item.block.id == block_id:
                self.scene.removeItem(item)
                break
                
    def on_system_cleared(self):
        """Handle system cleared"""
        self.scene.clear()
        
    def clear_all(self):
        """Clear all rails from the layout"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            'Clear Layout',
            'Are you sure you want to clear all rails?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.railway_system.clear()
        
    def toggle_grid(self, checked: bool):
        """Toggle grid display"""
        self.scene.show_grid = checked
        self.scene.invalidate()  # Force redraw
        if checked:
            self.grid_btn.setText("⊞ Grid")
        else:
            self.grid_btn.setText("⊞ Grid")
            
    def refresh(self):
        """Refresh the view from railway system"""
        self.scene.clear()
        for block_id in self.railway_system.blocks:
            self.on_block_added(block_id)
            
    def auto_create_groups(self):
        """Automatically create groups of connected rails - UI only"""
        # Ensure the scene is fully updated
        self.scene.update()
        
        # Delegate to controller
        success, message = self.controller.auto_create_groups()
        
        # Refresh to show updated block IDs
        self.refresh()
        
        if success:
            QMessageBox.information(self, "✓ Groups Created Successfully", message)
        else:
            QMessageBox.critical(self, "❌ Validation Failed", message)
    
    def save_layout(self):
        """Save the current layout - UI only"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Layout",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Delegate to controller
            success, message = self.controller.save_layout(file_path)
            
            if success:
                QMessageBox.information(self, "✓ Layout Saved", message)
            else:
                QMessageBox.critical(self, "❌ Error", message)
    
    def load_layout(self):
        """Load a layout from file - UI only"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Layout",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Delegate to controller
            success, message = self.controller.load_layout(file_path)
            
            if success:
                self.refresh()
                QMessageBox.information(self, "✓ Success", message)
            else:
                QMessageBox.critical(self, "❌ Error", message)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        # Zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Set zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.view.scale(zoom_factor, zoom_factor)
