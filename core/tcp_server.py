"""
TCP Server for Railway Block Status Updates
Receives real-time status updates from Docker containers or external systems
"""

from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
import json
from typing import Optional, Dict, List


class BlockStatus:
    """Block status enumeration"""
    UNKNOWN = "unknown"
    FREE = "free"
    RESERVED = "reserved"
    BLOCKED = "blocked"
    
    # Color mapping for each status
    COLORS = {
        UNKNOWN: "#888888",    # Gray
        FREE: "#48BB78",       # Green
        RESERVED: "#FFA500",   # Orange
        BLOCKED: "#E53E3E"     # Red
    }
    
    @staticmethod
    def is_valid(status: str) -> bool:
        """Check if status is valid"""
        return status in [BlockStatus.UNKNOWN, BlockStatus.FREE, 
                         BlockStatus.RESERVED, BlockStatus.BLOCKED]
    
    @staticmethod
    def get_color(status: str) -> str:
        """Get color for a status"""
        return BlockStatus.COLORS.get(status, "#888888")


class ClientConnection(QObject):
    """Represents a single TCP client connection"""
    
    message_received = Signal(str, dict)  # client_id, data
    connection_lost = Signal(str)  # client_id
    
    def __init__(self, socket: QTcpSocket, client_id: str):
        super().__init__()
        self.socket = socket
        self.client_id = client_id
        self.buffer = ""
        
        # Connect socket signals
        self.socket.readyRead.connect(self.on_data_ready)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.errorOccurred.connect(self.on_error)
        
    def on_data_ready(self):
        """Handle incoming data from client"""
        try:
            # Read all available data
            data = self.socket.readAll().data().decode('utf-8')
            self.buffer += data
            
            # Process complete messages (separated by newlines)
            while '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                line = line.strip()
                
                if line:
                    self.process_message(line)
                    
        except Exception as e:
            print(f"Error reading data from {self.client_id}: {e}")
    
    def process_message(self, message: str):
        """Process a single message"""
        try:
            # Parse JSON
            data = json.loads(message)
            self.message_received.emit(self.client_id, data)
            
        except json.JSONDecodeError as e:
            print(f"Invalid JSON from {self.client_id}: {e}")
            print(f"Message: {message}")
    
    def on_disconnected(self):
        """Handle client disconnection"""
        print(f"Client {self.client_id} disconnected")
        self.connection_lost.emit(self.client_id)
    
    def on_error(self, error):
        """Handle socket error"""
        print(f"Socket error from {self.client_id}: {error}")
    
    def send_response(self, data: dict):
        """Send response to client"""
        try:
            message = json.dumps(data) + '\n'
            self.socket.write(message.encode('utf-8'))
            self.socket.flush()
        except Exception as e:
            print(f"Error sending response to {self.client_id}: {e}")
    
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()


class RailwayTCPServer(QObject):
    """TCP Server for receiving railway block status updates"""
    
    # Signals
    client_connected = Signal(str)  # client_id
    client_disconnected = Signal(str)  # client_id
    block_status_update = Signal(str, str)  # block_id, status
    batch_status_update = Signal(list)  # List of (block_id, status) tuples
    error_occurred = Signal(str)  # error_message
    log_message = Signal(str)  # log_message
    
    def __init__(self, port: int = 5555, host: str = "0.0.0.0"):
        super().__init__()
        self.port = port
        self.host = host
        self.server = QTcpServer(self)
        self.clients: Dict[str, ClientConnection] = {}
        self.next_client_id = 1
        
        # Connect server signals
        self.server.newConnection.connect(self.on_new_connection)
        
    def start(self) -> bool:
        """Start the TCP server"""
        # Determine host address
        if self.host == "0.0.0.0" or self.host == "":
            host_address = QHostAddress.Any
        elif self.host == "localhost" or self.host == "127.0.0.1":
            host_address = QHostAddress.LocalHost
        else:
            host_address = QHostAddress(self.host)
        
        # Start listening
        if self.server.listen(host_address, self.port):
            self.log_message.emit(f"✓ TCP Server started on {self.host}:{self.port}")
            return True
        else:
            error_msg = f"Failed to start TCP server on {self.host}:{self.port}: {self.server.errorString()}"
            self.error_occurred.emit(error_msg)
            return False
    
    def stop(self):
        """Stop the TCP server"""
        # Close all client connections
        for client in list(self.clients.values()):
            client.close()
        self.clients.clear()
        
        # Stop server
        if self.server.isListening():
            self.server.close()
            self.log_message.emit("✓ TCP Server stopped")
    
    def on_new_connection(self):
        """Handle new client connection"""
        socket = self.server.nextPendingConnection()
        if not socket:
            return
        
        # Create client ID
        client_id = f"client_{self.next_client_id}"
        self.next_client_id += 1
        
        # Get client info
        peer_address = socket.peerAddress().toString()
        peer_port = socket.peerPort()
        
        # Create client connection handler
        client = ClientConnection(socket, client_id)
        client.message_received.connect(self.on_client_message)
        client.connection_lost.connect(self.on_client_lost)
        
        self.clients[client_id] = client
        
        self.log_message.emit(f"✓ New connection: {client_id} from {peer_address}:{peer_port}")
        self.client_connected.emit(client_id)
        
        # Send welcome message
        client.send_response({
            "type": "welcome",
            "message": "Connected to RailwayStudio TCP Server",
            "client_id": client_id,
            "protocol_version": "1.0"
        })
    
    def on_client_message(self, client_id: str, data: dict):
        """Handle message from client"""
        try:
            msg_type = data.get("type", "status_update")
            
            if msg_type == "status_update":
                # Single block status update
                block_id = data.get("block_id")
                status = data.get("status")
                
                if not block_id:
                    self.error_occurred.emit(f"Missing block_id in message from {client_id}")
                    return
                
                if not status:
                    self.error_occurred.emit(f"Missing status in message from {client_id}")
                    return
                
                if not BlockStatus.is_valid(status):
                    self.error_occurred.emit(
                        f"Invalid status '{status}' from {client_id}. "
                        f"Valid: {', '.join([BlockStatus.UNKNOWN, BlockStatus.FREE, BlockStatus.RESERVED, BlockStatus.BLOCKED])}"
                    )
                    return
                
                self.log_message.emit(f"📦 Status update: {block_id} → {status}")
                self.block_status_update.emit(block_id, status)
                
                # Send acknowledgment
                if client_id in self.clients:
                    self.clients[client_id].send_response({
                        "type": "ack",
                        "block_id": block_id,
                        "status": "received"
                    })
            
            elif msg_type == "batch_update":
                # Batch update of multiple blocks
                updates = data.get("updates", [])
                
                if not updates:
                    self.error_occurred.emit(f"Empty updates list in batch from {client_id}")
                    return
                
                valid_updates = []
                for update in updates:
                    block_id = update.get("block_id")
                    status = update.get("status")
                    
                    if block_id and status and BlockStatus.is_valid(status):
                        valid_updates.append((block_id, status))
                    else:
                        self.error_occurred.emit(
                            f"Invalid update in batch: block_id={block_id}, status={status}"
                        )
                
                if valid_updates:
                    self.log_message.emit(f"📦 Batch update: {len(valid_updates)} blocks")
                    self.batch_status_update.emit(valid_updates)
                    
                    # Send acknowledgment
                    if client_id in self.clients:
                        self.clients[client_id].send_response({
                            "type": "ack",
                            "updates_received": len(valid_updates),
                            "status": "received"
                        })
            
            elif msg_type == "ping":
                # Ping/pong for connection testing
                if client_id in self.clients:
                    self.clients[client_id].send_response({
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })
            
            else:
                self.error_occurred.emit(f"Unknown message type '{msg_type}' from {client_id}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error processing message from {client_id}: {str(e)}")
    
    def on_client_lost(self, client_id: str):
        """Handle client disconnection"""
        if client_id in self.clients:
            del self.clients[client_id]
        self.client_disconnected.emit(client_id)
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.clients.keys())
    
    def is_listening(self) -> bool:
        """Check if server is listening"""
        return self.server.isListening()

