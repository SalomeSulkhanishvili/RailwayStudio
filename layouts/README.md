# Railway Layouts

This folder contains all your saved railway layout files.

## About Layout Files

Layout files are stored in JSON format with the `.json` extension. Each file contains:
- **Rail blocks**: Individual track segments with their positions and properties
- **Block groups**: Logical sections of connected rails
- **Connections**: How rails are connected to each other
- **Metadata**: Additional information about the layout

## File Management

### From the Application
- Use the **Files** tab to browse and manage layouts
- Load layouts in **Editor** or **Monitor** mode
- Save new layouts with the **Save** button in the editor

### File Naming
- Use descriptive names for your layouts (e.g., `station_yard.json`, `main_line.json`)
- Avoid special characters in filenames
- Files are automatically saved with `.json` extension

## Example Layouts

The application may include example layouts to help you get started:
- `first_layout.json` - Simple example with straight and curved rails
- `second_layout.json` - More complex layout with switches and groups

## JSON Format

Layout files follow a structured format with:
```json
{
  "blockGroups": [...],
  "turnouts": [...],
  "metadata": {
    "version": "1.0",
    "created": "timestamp",
    "_legacy_data": {...}
  }
}
```

For detailed format documentation, see [docs/USAGE.md](../docs/USAGE.md).

## Backup Recommendations

- Regularly backup important layouts
- Version control is recommended for complex projects
- Consider exporting layouts to a separate backup location

---

**Tip**: You can also open and edit layout files in any text editor, but be careful to maintain valid JSON format!

