#!/usr/bin/env python3
"""
Extract Block IDs from Railway Layout JSON
-------------------------------------------
This utility script extracts all Block IDs from a railway layout JSON file.
Use this in your Docker container to get the list of valid Block IDs.

Usage:
    python extract_block_ids.py <layout_file.json>
    
Example:
    python extract_block_ids.py ../layouts/first_layout.json

Output:
    - List of all Block IDs (BL00X00X format)
    - Can be used to validate IDs before sending TCP messages
    - Can be piped to other scripts or saved to a file

Author: RailwayStudio
License: MIT
"""

import json
import sys
from typing import List, Dict


def extract_block_ids(layout_file: str) -> List[Dict[str, any]]:
    """
    Extract all Block IDs from a railway layout JSON file
    
    Args:
        layout_file: Path to the JSON layout file
        
    Returns:
        List of dictionaries containing block information
    """
    try:
        with open(layout_file, 'r') as f:
            layout = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{layout_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{layout_file}': {e}")
        sys.exit(1)
    
    # Check if file has blockGroups (new format)
    if 'blockGroups' not in layout:
        print("Error: This layout file doesn't have 'blockGroups'.")
        print("Please open the layout in Editor and click 'Auto-Create Groups' to generate Block IDs.")
        sys.exit(1)
    
    # Extract block information
    blocks = []
    for group in layout['blockGroups']:
        group_id = group.get('groupId', 'Unknown')
        
        for block in group.get('blocks', []):
            block_info = {
                'block_id': block.get('blockId'),
                'group_id': group_id,
                'rail_count': len(block.get('rails', [])),
                'start_rail': block.get('startRail'),
                'end_rail': block.get('endRail')
            }
            blocks.append(block_info)
    
    return blocks


def print_block_ids(blocks: List[Dict], format: str = 'simple'):
    """
    Print Block IDs in various formats
    
    Args:
        blocks: List of block dictionaries
        format: Output format ('simple', 'detailed', 'json', 'python_list')
    """
    if format == 'simple':
        # Just print Block IDs, one per line
        for block in blocks:
            print(block['block_id'])
    
    elif format == 'detailed':
        # Print detailed information
        print(f"Found {len(blocks)} blocks:\n")
        for i, block in enumerate(blocks, 1):
            print(f"{i}. {block['block_id']}")
            print(f"   Group: {block['group_id']}")
            print(f"   Rails: {block['rail_count']} ({block['start_rail']} → {block['end_rail']})")
            print()
    
    elif format == 'json':
        # Print as JSON array
        block_ids = [block['block_id'] for block in blocks]
        print(json.dumps(block_ids, indent=2))
    
    elif format == 'python_list':
        # Print as Python list
        block_ids = [block['block_id'] for block in blocks]
        print(f"block_ids = {block_ids}")
    
    elif format == 'cpp_array':
        # Print as C++ array
        block_ids = [f'"{block["block_id"]}"' for block in blocks]
        print(f'const char* blockIds[] = {{{", ".join(block_ids)}}};')
    
    elif format == 'csv':
        # Print as CSV
        print("block_id,group_id,rail_count,start_rail,end_rail")
        for block in blocks:
            print(f"{block['block_id']},{block['group_id']},{block['rail_count']},{block['start_rail']},{block['end_rail']}")


def main():
    """Main function"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python extract_block_ids.py <layout_file.json> [format]")
        print()
        print("Formats:")
        print("  simple       - Just Block IDs, one per line (default)")
        print("  detailed     - Detailed information about each block")
        print("  json         - JSON array of Block IDs")
        print("  python_list  - Python list of Block IDs")
        print("  cpp_array    - C++ array declaration")
        print("  csv          - CSV format with all fields")
        print()
        print("Examples:")
        print("  python extract_block_ids.py layout.json")
        print("  python extract_block_ids.py layout.json detailed")
        print("  python extract_block_ids.py layout.json json > block_ids.json")
        sys.exit(1)
    
    layout_file = sys.argv[1]
    format = sys.argv[2] if len(sys.argv) > 2 else 'simple'
    
    # Validate format
    valid_formats = ['simple', 'detailed', 'json', 'python_list', 'cpp_array', 'csv']
    if format not in valid_formats:
        print(f"Error: Invalid format '{format}'")
        print(f"Valid formats: {', '.join(valid_formats)}")
        sys.exit(1)
    
    # Extract Block IDs
    blocks = extract_block_ids(layout_file)
    
    if not blocks:
        print("No blocks found in layout file.")
        print("Make sure you've run 'Auto-Create Groups' in the Editor.")
        sys.exit(1)
    
    # Print results
    print_block_ids(blocks, format)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

