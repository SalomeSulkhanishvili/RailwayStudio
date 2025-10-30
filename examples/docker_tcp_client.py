#!/usr/bin/env python3
"""
Example TCP Client for RailwayStudio
--------------------------------------
This script demonstrates how to send block status updates from a Docker container
to railwayStudio running on the same PC.

Usage:
    python docker_tcp_client.py

Requirements:
    - Python 3.6+
    - No external dependencies (uses only standard library)

Author: RailwayStudio
License: MIT
"""

import socket
import json
import time
import sys
from typing import Optional


class RailwayStudioClient:
    """TCP Client for sending block status updates to RailwayStudio"""
    
    # Block status constants
    STATUS_FREE = "free"
    STATUS_RESERVED = "reserved"
    STATUS_BLOCKED = "blocked"
    STATUS_UNKNOWN = "unknown"
    
    def __init__(self, host: str = 'localhost', port: int = 5555):
        """
        Initialize the client
        
        Args:
            host: RailwayStudio server host (use 'host.docker.internal' from Docker on Mac/Windows)
            port: RailwayStudio server port (default: 5555)
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.client_id = None
        
    def connect(self) -> bool:
        """
        Connect to RailwayStudio TCP server
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            print(f"Connecting to RailwayStudio at {self.host}:{self.port}...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.host, self.port))
            
            # Read welcome message
            welcome_data = self.socket.recv(1024).decode('utf-8')
            if welcome_data:
                # Parse welcome message (might have multiple lines)
                for line in welcome_data.split('\n'):
                    if line.strip():
                        try:
                            welcome = json.loads(line)
                            if welcome.get('type') == 'welcome':
                                self.client_id = welcome.get('client_id')
                                print(f"✓ Connected! Client ID: {self.client_id}")
                                print(f"  Protocol version: {welcome.get('protocol_version')}")
                                self.connected = True
                                return True
                        except json.JSONDecodeError:
                            pass
            
            print("✓ Connected (no welcome message received)")
            self.connected = True
            return True
            
        except socket.timeout:
            print(f"✗ Connection timeout - is RailwayStudio running?")
            return False
        except ConnectionRefusedError:
            print(f"✗ Connection refused - is RailwayStudio TCP server started?")
            return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
                print("✓ Disconnected")
            except:
                pass
            finally:
                self.socket = None
                self.connected = False
    
    def send_status_update(self, block_id: str, status: str) -> bool:
        """
        Send a single block status update
        
        Args:
            block_id: Block ID (e.g., 'rail_0001' or 'BL001001')
            status: Block status ('free', 'reserved', 'blocked', or 'unknown')
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected:
            print("✗ Not connected to server")
            return False
        
        # Validate status
        valid_statuses = [self.STATUS_FREE, self.STATUS_RESERVED, 
                         self.STATUS_BLOCKED, self.STATUS_UNKNOWN]
        if status not in valid_statuses:
            print(f"✗ Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}")
            return False
        
        # Create message
        message = {
            "type": "status_update",
            "block_id": block_id,
            "status": status
        }
        
        return self._send_message(message)
    
    def send_batch_update(self, updates: list) -> bool:
        """
        Send multiple block status updates in a single message
        
        Args:
            updates: List of tuples (block_id, status)
                    e.g., [('rail_0001', 'blocked'), ('rail_0002', 'free')]
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected:
            print("✗ Not connected to server")
            return False
        
        # Create message
        message = {
            "type": "batch_update",
            "updates": [
                {"block_id": block_id, "status": status}
                for block_id, status in updates
            ]
        }
        
        return self._send_message(message)
    
    def ping(self) -> bool:
        """
        Send a ping to test the connection
        
        Returns:
            True if pong received, False otherwise
        """
        if not self.connected:
            print("✗ Not connected to server")
            return False
        
        message = {
            "type": "ping",
            "timestamp": int(time.time())
        }
        
        return self._send_message(message)
    
    def _send_message(self, message: dict) -> bool:
        """
        Internal method to send a JSON message
        
        Args:
            message: Dictionary to send as JSON
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Convert to JSON and add newline
            json_str = json.dumps(message) + '\n'
            
            # Send message
            self.socket.send(json_str.encode('utf-8'))
            
            # Try to read acknowledgment (non-blocking)
            self.socket.settimeout(0.5)
            try:
                response_data = self.socket.recv(1024).decode('utf-8')
                if response_data:
                    for line in response_data.split('\n'):
                        if line.strip():
                            try:
                                response = json.loads(line)
                                if response.get('type') == 'ack':
                                    print(f"✓ Message acknowledged by server")
                                    return True
                            except json.JSONDecodeError:
                                pass
            except socket.timeout:
                # No response received, but message was sent
                pass
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to send message: {e}")
            self.connected = False
            return False


def demo_simple_updates(client: RailwayStudioClient):
    """Demo: Send simple status updates"""
    print("\n" + "="*60)
    print("DEMO 1: Simple Status Updates")
    print("="*60)
    
    # Update individual blocks
    updates = [
        ("rail_0001", RailwayStudioClient.STATUS_BLOCKED),
        ("rail_0002", RailwayStudioClient.STATUS_RESERVED),
        ("rail_0003", RailwayStudioClient.STATUS_FREE),
        ("rail_0004", RailwayStudioClient.STATUS_UNKNOWN),
    ]
    
    for block_id, status in updates:
        print(f"\nSending: {block_id} → {status}")
        client.send_status_update(block_id, status)
        time.sleep(1)  # Wait 1 second between updates


def demo_batch_updates(client: RailwayStudioClient):
    """Demo: Send batch status updates"""
    print("\n" + "="*60)
    print("DEMO 2: Batch Status Updates")
    print("="*60)
    
    # Update multiple blocks at once
    batch = [
        ("rail_0001", RailwayStudioClient.STATUS_FREE),
        ("rail_0002", RailwayStudioClient.STATUS_FREE),
        ("rail_0003", RailwayStudioClient.STATUS_BLOCKED),
        ("rail_0004", RailwayStudioClient.STATUS_BLOCKED),
        ("rail_0005", RailwayStudioClient.STATUS_RESERVED),
    ]
    
    print(f"\nSending batch update for {len(batch)} blocks...")
    client.send_batch_update(batch)
    time.sleep(2)


def demo_train_movement(client: RailwayStudioClient):
    """Demo: Simulate train movement through blocks"""
    print("\n" + "="*60)
    print("DEMO 3: Simulated Train Movement")
    print("="*60)
    
    # Simulate a train moving through blocks
    blocks = ["rail_0001", "rail_0002", "rail_0003", "rail_0004", "rail_0005"]
    
    print("\nSimulating train movement through 5 blocks...")
    
    for i, current_block in enumerate(blocks):
        # Reserve next block
        if i < len(blocks) - 1:
            next_block = blocks[i + 1]
            print(f"  Reserving {next_block}...")
            client.send_status_update(next_block, RailwayStudioClient.STATUS_RESERVED)
            time.sleep(0.3)
        
        # Block current block (train enters)
        print(f"  Train enters {current_block}")
        client.send_status_update(current_block, RailwayStudioClient.STATUS_BLOCKED)
        time.sleep(1)
        
        # Free previous block (train leaves)
        if i > 0:
            prev_block = blocks[i - 1]
            print(f"  Train leaves {prev_block}")
            client.send_status_update(prev_block, RailwayStudioClient.STATUS_FREE)
            time.sleep(0.3)
    
    # Free the last block
    print(f"  Train leaves {blocks[-1]}")
    client.send_status_update(blocks[-1], RailwayStudioClient.STATUS_FREE)


def demo_ping(client: RailwayStudioClient):
    """Demo: Test connection with ping"""
    print("\n" + "="*60)
    print("DEMO 4: Connection Test (Ping)")
    print("="*60)
    
    print("\nSending ping...")
    client.ping()


def main():
    """Main function"""
    print("RailwayStudio TCP Client - Example")
    print("===================================\n")
    
    # Determine host based on environment
    # Use 'host.docker.internal' if running in Docker on Mac/Windows
    # Use '172.17.0.1' if running in Docker on Linux
    # Use 'localhost' if running directly on the host
    
    host = 'localhost'  # Change this if needed
    port = 5555
    
    # Check if running in Docker
    try:
        with open('/proc/1/cgroup', 'r') as f:
            if 'docker' in f.read():
                # Running in Docker on Linux
                host = '172.17.0.1'
                print("🐳 Detected Docker environment (Linux)")
                print(f"   Using host: {host}")
    except:
        pass
    
    # Create client
    client = RailwayStudioClient(host=host, port=port)
    
    # Connect
    if not client.connect():
        print("\n❌ Failed to connect to RailwayStudio")
        print("\nMake sure:")
        print("  1. RailwayStudio is running")
        print("  2. Monitor view is open")
        print("  3. TCP server is started (green 'Server running' status)")
        print("  4. Port matches (default: 5555)")
        return 1
    
    try:
        # Run demos
        demo_ping(client)
        time.sleep(1)
        
        demo_simple_updates(client)
        time.sleep(2)
        
        demo_batch_updates(client)
        time.sleep(2)
        
        demo_train_movement(client)
        
        print("\n" + "="*60)
        print("All demos completed!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        # Disconnect
        client.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

