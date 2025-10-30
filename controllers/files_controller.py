"""
Files Controller
Handles file operations and metadata for railway layouts
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional


class FileInfo:
    """Data class for file information"""
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.size = 0
        self.modified = None
        self.groups = 0
        self.blocks = 0
        self.is_valid = False
        
        self._load_info()
    
    def _load_info(self):
        """Load file information"""
        try:
            # Get file stats - always succeed for basic info
            stat = os.stat(self.path)
            self.size = stat.st_size
            self.modified = datetime.fromtimestamp(stat.st_mtime)
            self.is_valid = True  # File exists, so it's valid
            
            # Try to parse JSON for metadata (optional)
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    
                    # Count groups and blocks
                    if 'blockGroups' in data:
                        # blockGroups is a dict with group IDs as keys
                        block_groups_dict = data['blockGroups']
                        self.groups = len(block_groups_dict)
                        # Sum blocks across all groups (iterate over values)
                        self.blocks = sum(len(group.get('blocks', [])) 
                                        for group in block_groups_dict.values())
                    elif 'blocks' in data:  # Old format
                        self.blocks = len(data['blocks'])
                        self.groups = 1  # Assume single group for old format
            except Exception as parse_error:
                # Can't parse JSON, but file is still valid
                print(f"Warning: Could not parse JSON metadata for {self.name}: {parse_error}")
                self.groups = 0
                self.blocks = 0
                
        except Exception as e:
            # Only mark invalid if we can't even stat the file
            print(f"Error loading file info for {self.path}: {e}")
            self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'name': self.name,
            'size': self.size,
            'modified': self.modified.isoformat() if self.modified else None,
            'groups': self.groups,
            'blocks': self.blocks,
            'is_valid': self.is_valid
        }


class FilesController:
    """Controller for file operations"""
    
    def __init__(self, layouts_dir: str = "layouts"):
        self.layouts_dir = os.path.abspath(layouts_dir)
        self.ensure_layouts_dir()
    
    def ensure_layouts_dir(self) -> None:
        """Ensure layouts directory exists"""
        os.makedirs(self.layouts_dir, exist_ok=True)
    
    def get_layouts_directory(self) -> str:
        """Get the layouts directory path"""
        return self.layouts_dir
    
    def list_files(self, directory: Optional[str] = None) -> List[FileInfo]:
        """
        List all JSON files in directory
        Returns: list of FileInfo objects
        """
        target_dir = directory or self.layouts_dir
        files = []
        
        try:
            for filename in os.listdir(target_dir):
                if filename.endswith('.json') and not filename.startswith('.'):
                    file_path = os.path.join(target_dir, filename)
                    file_info = FileInfo(file_path)
                    # Include all files that exist, even if metadata can't be parsed
                    if file_info.is_valid:
                        files.append(file_info)
            
            # Sort by modified date (newest first)
            files.sort(key=lambda f: f.modified or datetime.min, reverse=True)
            
        except Exception as e:
            print(f"Error listing files in {target_dir}: {e}")
        
        return files
    
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """
        Get information about a specific file
        Returns: FileInfo or None if error
        """
        try:
            return FileInfo(file_path)
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete a file
        Returns: (success, message)
        """
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            os.remove(file_path)
            return True, f"Deleted {os.path.basename(file_path)}"
        except Exception as e:
            return False, f"Failed to delete file: {str(e)}"
    
    def rename_file(self, old_path: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a file
        Returns: (success, message, new_path)
        """
        try:
            if not os.path.exists(old_path):
                return False, "File does not exist", None
            
            # Ensure .json extension
            if not new_name.endswith('.json'):
                new_name += '.json'
            
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_path):
                return False, "A file with that name already exists", None
            
            os.rename(old_path, new_path)
            return True, f"Renamed to {new_name}", new_path
        except Exception as e:
            return False, f"Failed to rename file: {str(e)}", None
    
    def copy_file(self, src_path: str, dest_name: str) -> Tuple[bool, str]:
        """
        Copy a file
        Returns: (success, message)
        """
        try:
            if not os.path.exists(src_path):
                return False, "Source file does not exist"
            
            # Ensure .json extension
            if not dest_name.endswith('.json'):
                dest_name += '.json'
            
            directory = os.path.dirname(src_path)
            dest_path = os.path.join(directory, dest_name)
            
            if os.path.exists(dest_path):
                return False, "A file with that name already exists"
            
            import shutil
            shutil.copy2(src_path, dest_path)
            return True, f"Copied to {dest_name}"
        except Exception as e:
            return False, f"Failed to copy file: {str(e)}"
    
    def validate_layout_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate a layout file
        Returns: (is_valid, error_message)
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check for required fields
            if 'blockGroups' in data:
                # New format
                if not isinstance(data['blockGroups'], list):
                    return False, "blockGroups must be a list"
                
                for group in data['blockGroups']:
                    if 'blocks' not in group:
                        return False, "Each group must have blocks"
            
            elif 'blocks' in data:
                # Old format
                if not isinstance(data['blocks'], dict):
                    return False, "blocks must be a dictionary"
            
            else:
                return False, "No blockGroups or blocks found in file"
            
            return True, "Valid layout file"
            
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_file_count(self, directory: Optional[str] = None) -> int:
        """Get count of JSON files in directory"""
        return len(self.list_files(directory))
    
    def get_total_size(self, directory: Optional[str] = None) -> int:
        """Get total size of all JSON files in bytes"""
        files = self.list_files(directory)
        return sum(f.size for f in files)
    
    def search_files(self, query: str, directory: Optional[str] = None) -> List[FileInfo]:
        """
        Search for files by name
        Returns: list of matching FileInfo objects
        """
        all_files = self.list_files(directory)
        query_lower = query.lower()
        return [f for f in all_files if query_lower in f.name.lower()]

