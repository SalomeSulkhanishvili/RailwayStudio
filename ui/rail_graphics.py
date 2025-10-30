"""
Rail Graphics Items - QGraphicsItem implementations for different rail types
"""

from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QMenu, QGraphicsLineItem
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QTransform

from core.railway_system import RailBlock, RailwaySystem
import math


class ConnectionPointItem(QGraphicsEllipseItem):
    """Draggable connection point"""
    
    def __init__(self, parent_rail: 'RailGraphicsItem', point_name: str, x: float, y: float):
        super().__init__(-6, -6, 12, 12)
        self.parent_rail = parent_rail
        self.point_name = point_name
        self.setPos(x, y)
        self.setParentItem(parent_rail)
        
        # Make draggable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(10)
        
        self.update_appearance()
        
    def update_appearance(self):
        """Update color based on connection status"""
        is_connected = self.parent_rail.block.connections.get(self.point_name) is not None
        if is_connected:
            self.setBrush(QBrush(QColor(0, 200, 0)))
            self.setPen(QPen(QColor(0, 100, 0), 2))
        else:
            self.setBrush(QBrush(QColor(255, 100, 100)))
            self.setPen(QPen(QColor(150, 0, 0), 2))
            
    def itemChange(self, change, value):
        """Handle dragging to connect to nearby points"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Check for nearby connection points
            scene_pos = self.scenePos()
            self.check_for_connection(scene_pos)
            
            # Snap back to original position after connection check
            original_pos = self.parent_rail.get_connection_point_positions()[self.point_name]
            self.setPos(original_pos[0], original_pos[1])
            
            # Update the parent rail's connection items
            self.parent_rail.update()
            
        return super().itemChange(change, value)
        
    def check_for_connection(self, scene_pos: QPointF):
        """Check if dragged near another connection point"""
        connection_threshold = 30  # pixels - increased for easier connection
        
        scene = self.scene()
        if not scene:
            return
            
        # Find nearby connection points
        for item in scene.items():
            if isinstance(item, ConnectionPointItem) and item != self:
                distance = (item.scenePos() - scene_pos).manhattanLength()
                
                if distance < connection_threshold:
                    # Connect these two points
                    self.connect_to(item)
                    return
                    
    def connect_to(self, other: 'ConnectionPointItem'):
        """Create connection between two points"""
        rail1_id = self.parent_rail.block.id
        rail2_id = other.parent_rail.block.id
        point1 = self.point_name
        point2 = other.point_name
        
        # Don't connect to self
        if rail1_id == rail2_id:
            return
            
        # Create connection in railway system
        success = self.parent_rail.railway_system.connect_blocks(
            rail1_id, point1, rail2_id, point2
        )
        
        if success:
            # Auto-snap: align the rails so connection points match perfectly
            self.snap_rails_together(other)
            
            self.update_appearance()
            other.update_appearance()
            self.parent_rail.update()
            other.parent_rail.update()
            
    def snap_rails_together(self, other: 'ConnectionPointItem'):
        """Snap two rails together by aligning their connection points"""
        # Get world positions of both connection points BEFORE moving
        my_world_pos = self.mapToScene(QPointF(0, 0))
        other_world_pos = other.mapToScene(QPointF(0, 0))
        
        # Calculate the offset needed to align the connection points
        offset = other_world_pos - my_world_pos
        
        # Move the rail that was dragged (this rail's parent) to align perfectly
        current_rail_pos = self.parent_rail.pos()
        new_rail_pos = current_rail_pos + offset
        
        # Apply the position change
        self.parent_rail.setPos(new_rail_pos)
        self.parent_rail.block.x = new_rail_pos.x()
        self.parent_rail.block.y = new_rail_pos.y()
        
        # Update the railway system
        self.parent_rail.railway_system.update_block_position(
            self.parent_rail.block.id, 
            new_rail_pos.x(), 
            new_rail_pos.y()
        )
        
        # Force visual update
        self.parent_rail.update()
        if self.parent_rail.scene():
            self.parent_rail.scene().update()
            
    def mouseDoubleClickEvent(self, event):
        """Double-click to disconnect"""
        if event.button() == Qt.LeftButton:
            self.parent_rail.railway_system.disconnect_blocks(
                self.parent_rail.block.id, self.point_name
            )
            self.update_appearance()
            self.parent_rail.update()
            
            # Update the connected point
            for item in self.scene().items():
                if isinstance(item, ConnectionPointItem):
                    item.update_appearance()


class RailGraphicsItem(QGraphicsItem):
    """Graphics item for rendering a rail block"""
    
    def __init__(self, block: RailBlock, railway_system: RailwaySystem):
        super().__init__()
        self.block = block
        self.railway_system = railway_system
        
        # Make item movable and selectable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Set position and rotation
        self.setPos(block.x, block.y)
        self.setRotation(block.rotation)
        
        # Connection points (visual indicators)
        self.connection_items = []
        self.create_connection_points()
        
    def boundingRect(self) -> QRectF:
        """Return bounding rectangle for the item"""
        length = self.block.length
        if self.block.type == 'straight':
            return QRectF(-15, -15, length + 30, 30)
        elif self.block.type == 'curved':
            # 30-degree curve bounding box
            angle_rad = math.radians(30)
            end_x = length * math.cos(angle_rad)
            end_y = length * math.sin(angle_rad)
            return QRectF(-15, -15, end_x + 30, end_y + 30)
        elif self.block.type in ['switch_left', 'switch_right']:
            angle_rad = math.radians(30)
            div_y = length * math.sin(angle_rad)
            return QRectF(-15, -div_y - 15, length + 30, div_y * 2 + 30)
        return QRectF(-15, -15, length + 30, 30)
        
    def paint(self, painter: QPainter, option, widget):
        """Paint the rail block"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set color based on selection and block color
        if self.isSelected():
            pen = QPen(QColor(0, 120, 255), 3)
        else:
            pen = QPen(QColor(self.block.color), 2)
            
        painter.setPen(pen)
        
        # Draw based on type
        if self.block.type == 'straight':
            self.paint_straight(painter)
        elif self.block.type == 'curved':
            self.paint_curved(painter)
        elif self.block.type == 'switch_left':
            self.paint_switch_left(painter)
        elif self.block.type == 'switch_right':
            self.paint_switch_right(painter)
            
        # Draw connection lines to connected blocks
        self.draw_connection_lines(painter)
            
        # Draw connection points
        self.paint_connection_points(painter)
        
        # Draw rail ID label
        self.paint_rail_id(painter)
        
    def draw_connection_lines(self, painter: QPainter):
        """Draw visual lines showing connections between rails"""
        painter.save()
        painter.setPen(QPen(QColor(0, 150, 0, 100), 2, Qt.DashLine))
        
        points = self.get_connection_point_positions()
        for point_name, (x, y) in points.items():
            conn = self.block.connections.get(point_name)
            if conn:
                conn_block_id, conn_point_name = conn
                conn_block = self.railway_system.blocks.get(conn_block_id)
                if conn_block:
                    # Calculate world position of this connection point
                    local_pos = QPointF(x, y)
                    world_pos = self.mapToScene(local_pos)
                    
                    # Calculate world position of connected point
                    # Find the graphics item for the connected block
                    for item in self.scene().items():
                        if isinstance(item, RailGraphicsItem) and item.block.id == conn_block_id:
                            conn_points = item.get_connection_point_positions()
                            if conn_point_name in conn_points:
                                conn_x, conn_y = conn_points[conn_point_name]
                                conn_world_pos = item.mapToScene(QPointF(conn_x, conn_y))
                                
                                # Draw line in scene coordinates
                                line_start = self.mapFromScene(world_pos)
                                line_end = self.mapFromScene(conn_world_pos)
                                painter.drawLine(line_start, line_end)
                            break
        
        painter.restore()
        
    def paint_straight(self, painter: QPainter):
        """Paint a straight rail"""
        length = self.block.length
        
        # Draw two parallel lines for rails
        painter.drawLine(0, -3, length, -3)
        painter.drawLine(0, 3, length, 3)
        
        # Draw sleepers (ties)
        for i in range(0, int(length), 15):
            painter.drawLine(i, -5, i, 5)
            
    def paint_curved(self, painter: QPainter):
        """Paint a curved rail (30-degree curve)"""
        length = self.block.length
        rail_width = 6
        
        # 30-degree curve
        angle_rad = math.radians(30)
        end_x = length * math.cos(angle_rad)
        end_y = length * math.sin(angle_rad)
        
        # Control point for smooth curve
        ctrl_x = length * 0.5
        ctrl_y = 0
        
        # Draw outer rail (curved)
        path_outer = QPainterPath()
        path_outer.moveTo(0, 0)
        path_outer.quadTo(ctrl_x, ctrl_y, end_x, end_y)
        
        # Draw inner rail (curved, parallel)
        path_inner = QPainterPath()
        path_inner.moveTo(rail_width * math.sin(0), -rail_width * math.cos(0))
        path_inner.quadTo(ctrl_x + rail_width * 0.5, ctrl_y + rail_width, 
                         end_x + rail_width * math.sin(angle_rad), 
                         end_y - rail_width * math.cos(angle_rad))
        
        painter.drawPath(path_outer)
        painter.drawPath(path_inner)
        
        # Draw sleepers (ties) along the curve
        for i in range(0, 8):
            t = i / 8.0
            # Bezier curve position
            x = (1-t)*(1-t)*0 + 2*(1-t)*t*ctrl_x + t*t*end_x
            y = (1-t)*(1-t)*0 + 2*(1-t)*t*ctrl_y + t*t*end_y
            
            # Tangent angle
            local_angle = math.atan2(y, x)
            sleeper_len = 12
            dx = math.cos(local_angle + math.pi/2) * sleeper_len
            dy = math.sin(local_angle + math.pi/2) * sleeper_len
            
            painter.drawLine(int(x - dx/2), int(y - dy/2), 
                           int(x + dx/2), int(y + dy/2))
        
    def paint_switch_left(self, painter: QPainter):
        """Paint a left switch rail (30-degree diverging)"""
        length = self.block.length
        angle_rad = math.radians(30)
        
        # Main track (straight)
        painter.drawLine(0, -3, length, -3)
        painter.drawLine(0, 3, length, 3)
        
        # Diverging track (to the left/up at 30 degrees)
        div_x = length * math.cos(angle_rad)
        div_y = -length * math.sin(angle_rad)
        painter.drawLine(int(length * 0.2), 0, int(div_x), int(div_y))
        painter.drawLine(int(length * 0.2), 0, int(div_x - 6), int(div_y + 3))
        
    def paint_switch_right(self, painter: QPainter):
        """Paint a right switch rail (30-degree diverging)"""
        length = self.block.length
        angle_rad = math.radians(30)
        
        # Main track (straight)
        painter.drawLine(0, -3, length, -3)
        painter.drawLine(0, 3, length, 3)
        
        # Diverging track (to the right/down at 30 degrees)
        div_x = length * math.cos(angle_rad)
        div_y = length * math.sin(angle_rad)
        painter.drawLine(int(length * 0.2), 0, int(div_x), int(div_y))
        painter.drawLine(int(length * 0.2), 0, int(div_x - 6), int(div_y - 3))
        
    def paint_connection_points(self, painter: QPainter):
        """Paint connection point indicators"""
        # Connection points are now drawn as separate items
        pass
        
    def paint_rail_id(self, painter: QPainter):
        """Paint the block ID label on the rail"""
        from PySide6.QtGui import QFont
        
        painter.save()
        
        # Set font for ID label
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Set text color to gray
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        # Get the block ID (BL001001) if available, otherwise use rail ID
        display_id = getattr(self.block, 'block_id', self.block.id)
        
        # Calculate position for text - further from the rail for visibility
        length = self.block.length
        
        if self.block.type == 'straight':
            # Center of straight rail, further above
            text_x = length / 2
            text_y = -25  # Further above the rail
            text_rotation = 0
        elif self.block.type == 'curved':
            # For curved rail: position at midpoint of the 30-degree arc
            # and rotate text to match the curve orientation
            angle_rad = math.radians(15)  # Midpoint of 30-degree curve
            
            # Position at the outer edge of the curve, further away
            radius_offset = 40  # Distance from the curve
            text_x = (length + radius_offset) * math.cos(angle_rad)
            text_y = (length + radius_offset) * math.sin(angle_rad)
            
            # Rotate text to align with curve tangent at midpoint
            text_rotation = 15  # Degrees
        elif self.block.type in ['switch_left', 'switch_right']:
            # For switches: position above and to the side to avoid both tracks
            # The switch has a straight track and a diverging track at 30 degrees
            text_x = length / 2
            if self.block.type == 'switch_left':
                # Position to the right (away from left diverging track)
                text_y = -35
            else:  # switch_right
                # Position to the right (away from right diverging track)
                text_y = -35
            text_rotation = 0
        else:
            text_x = length / 2
            text_y = -25
            text_rotation = 0
        
        # Apply rotation if needed (for curved rails)
        if text_rotation != 0:
            painter.save()
            painter.translate(text_x, text_y)
            painter.rotate(-text_rotation)  # Negative because Qt rotates clockwise
            painter.drawText(-40, -10, 80, 20, Qt.AlignCenter, display_id)
            painter.restore()
        else:
            # Draw the block ID with larger text area (no rotation)
            painter.drawText(int(text_x - 40), int(text_y - 10), 80, 20, 
                            Qt.AlignCenter, display_id)
        
        painter.restore()
            
    def get_connection_point_positions(self) -> dict:
        """Get positions of connection points in item coordinates"""
        points = {}
        length = self.block.length
        
        if self.block.type == 'straight':
            points['start'] = (0, 0)
            points['end'] = (length, 0)
        elif self.block.type == 'curved':
            # 30-degree curve endpoint
            angle_rad = math.radians(30)
            end_x = length * math.cos(angle_rad)
            end_y = length * math.sin(angle_rad)
            points['start'] = (0, 0)
            points['end'] = (end_x, end_y)
        elif self.block.type in ['switch_left', 'switch_right']:
            points['start'] = (0, 0)
            points['end1'] = (length, 0)
            if self.block.type == 'switch_left':
                # 30-degree diverging track
                angle_rad = math.radians(30)
                points['end2'] = (length * math.cos(angle_rad), -length * math.sin(angle_rad))
            else:
                angle_rad = math.radians(30)
                points['end2'] = (length * math.cos(angle_rad), length * math.sin(angle_rad))
                
        return points
        
    def create_connection_points(self):
        """Create visual connection point items"""
        # Clear existing connection items
        for item in self.connection_items:
            if item.scene():
                item.scene().removeItem(item)
        self.connection_items.clear()
        
        # Create new connection point items
        points = self.get_connection_point_positions()
        for point_name, (x, y) in points.items():
            conn_item = ConnectionPointItem(self, point_name, x, y)
            self.connection_items.append(conn_item)
        
    def itemChange(self, change, value):
        """Handle item changes (e.g., position)"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update block position in railway system
            pos = self.pos()
            self.railway_system.update_block_position(self.block.id, pos.x(), pos.y())
            self.block.x = pos.x()
            self.block.y = pos.y()
        elif change == QGraphicsItem.ItemPositionChange:
            # Force scene update to prevent visual artifacts
            if self.scene():
                self.scene().update()
            
        return super().itemChange(change, value)
        
    def contextMenuEvent(self, event):
        """Show context menu on right click"""
        menu = QMenu()
        
        rotate_action90 = menu.addAction("Rotate 90°")
        rotate_action30 = menu.addAction("Rotate 30°")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        
        # Show connection info
        info_action = menu.addAction(f"ID: {self.block.id}")
        info_action.setEnabled(False)
        
        # Show next/previous rails
        if self.block.next_rails:
            next_action = menu.addAction(f"Next: {', '.join(self.block.next_rails)}")
            next_action.setEnabled(False)
        if self.block.prev_rails:
            prev_action = menu.addAction(f"Prev: {', '.join(self.block.prev_rails)}")
            prev_action.setEnabled(False)
            
        # Show group info
        if self.block.group_id:
            group = self.railway_system.groups.get(self.block.group_id)
            if group:
                group_action = menu.addAction(f"Group: {group.name}")
                group_action.setEnabled(False)
        
        action = menu.exec_(event.screenPos())
        
        if action == rotate_action90:
            new_rotation = (self.block.rotation + 90) % 360
            self.setRotation(new_rotation)
            self.railway_system.update_block_rotation(self.block.id, new_rotation)
            self.block.rotation = new_rotation
        elif action == rotate_action30:
            new_rotation = (self.block.rotation + 30) % 360
            self.setRotation(new_rotation)
            self.railway_system.update_block_rotation(self.block.id, new_rotation)
            self.block.rotation = new_rotation
        elif action == delete_action:
            self.railway_system.remove_block(self.block.id)

