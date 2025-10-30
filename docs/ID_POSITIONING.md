# Block ID Positioning Guide

## Overview
Block IDs (like BL001001) are displayed in gray text on each rail in the editor. The positioning is optimized for each rail type to ensure maximum visibility.

## Positioning by Rail Type

### 1. **Straight Rails** 🟦
```
Position: Center, 25 pixels above
Rotation: None (horizontal text)
Color: Gray (100, 100, 100)
Font: Arial, 9pt

    [BL001001]
        |
    ━━━━━━━━━━
```

### 2. **Curved Rails** 🔄
```
Position: Outer edge, 40 pixels from curve
Rotation: 15° (matches curve midpoint)
Color: Gray (100, 100, 100)
Font: Arial, 9pt

        BL001002
       ╱ (rotated)
      ╱
     ╱
    ╱ 30° curve
```

**Why rotated?**
- The 15° rotation aligns the text with the tangent of the 30° curve at its midpoint
- This prevents the text from overlapping with the curved track
- Makes the ID more readable when the rail is at any orientation

**Calculation:**
```python
# Midpoint of 30-degree curve = 15 degrees
angle_rad = math.radians(15)
radius_offset = 40  # pixels from curve

text_x = (length + radius_offset) * cos(15°)
text_y = (length + radius_offset) * sin(15°)
text_rotation = 15°
```

### 3. **Switch Rails** 🔀
```
Position: Center, 35 pixels above
Rotation: None
Color: Gray (100, 100, 100)
Font: Arial, 9pt

    [BL003001]
        |
    ━━━━━━━╱
    ━━━━━━━━ (switch has 2 tracks)
```

**Why higher?**
- Switches have both a straight track and a diverging track (30°)
- Positioned 35 pixels above (vs 25 for straight) to clear both tracks

## Implementation Details

### Text Drawing Logic

```python
if text_rotation != 0:
    # For curved rails: rotate the text
    painter.save()
    painter.translate(text_x, text_y)
    painter.rotate(-text_rotation)  # Negative = counterclockwise
    painter.drawText(-40, -10, 80, 20, Qt.AlignCenter, display_id)
    painter.restore()
else:
    # For straight/switch rails: no rotation
    painter.drawText(text_x - 40, text_y - 10, 80, 20, 
                    Qt.AlignCenter, display_id)
```

### Text Area Size
- Width: 80 pixels (centered on position)
- Height: 20 pixels
- Alignment: Center

## Visual Examples

### Before (Curved Rails):
```
Problem: Text was flat and could overlap with curve
    BL001002
       ╱╱╱  ← Text overlaps here
      ╱
     ╱
```

### After (Curved Rails):
```
Solution: Text rotated to follow curve
        BL001002
       ╱ ← Text follows curve
      ╱
     ╱
```

## Dynamic Behavior

### Following Rails
The IDs automatically follow rails when you:
- **Move rails**: Drag rails around, IDs move with them
- **Rotate rails**: Use right-click → Rotate, IDs maintain their offset
- **Connect rails**: IDs stay visible during connections

### Visibility States
- **Before grouping**: Shows rail IDs (rail_0001, rail_0002, etc.)
- **After grouping**: Shows block IDs (BL001001, BL001002, etc.)
- **Always visible**: IDs are always drawn on top of rails

## Customization

To adjust ID positioning, edit `ui/rail_graphics.py`:

```python
# Straight rails
text_y = -25  # Change this value

# Curved rails
radius_offset = 40  # Change distance from curve
text_rotation = 15  # Change rotation angle

# Switch rails
text_y = -35  # Change this value
```

## Color Scheme

```python
Text Color: RGB(100, 100, 100)  # Medium gray
Background: Transparent
Font: Arial, 9pt
Style: Plain (not bold)
```

**Why gray?**
- Visible but not distracting
- Distinguishes from rail graphics (which are darker)
- Easy to read against light backgrounds

## Tips for Best Visibility

1. **Zoom in** when working with many rails
2. **Use white background** for better contrast
3. **Rotate rails** if IDs overlap with other elements
4. **Space out rails** to prevent ID crowding
5. **Auto-create groups** to assign proper block IDs

## Troubleshooting

### ID Not Visible?
- Check if you've run "Auto-Create Groups"
- Zoom in - IDs might be small at low zoom
- Check if rail is selected (IDs always visible)

### ID Overlapping with Other Rails?
- Move rails further apart
- Rotate the rail to change ID position
- Adjust zoom level

### ID Shows rail_XXXX Instead of BL###?
- You need to click "Auto-Create Groups" first
- Block IDs are only assigned after grouping
- Rail IDs are temporary internal identifiers

## Related Files

- `ui/rail_graphics.py` - ID positioning logic
- `core/json_formatter.py` - Block ID generation
- `core/railway_system.py` - Group management

