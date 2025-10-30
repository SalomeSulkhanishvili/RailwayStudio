# Test Grouping Logic

## Rule: Groups Only Split at Turnouts

### Test Case 1: No Turnouts
**Layout**: [Straight] -> [Straight] -> [Curved] -> [Straight] -> [Curved]

**Expected Result**: **1 GROUP** (all rails together)

**Why**: No turnouts = all connected rails are in one group

---

### Test Case 2: One Turnout in Middle
**Layout**: 
```
[Straight] -> [Straight] -> [Turnout] -> [Straight] -> [Straight]
                                |
                                v
                            [Straight]
```

**Expected Result**: **2 GROUPS**
- Group 1: First 2 straight rails (before turnout)
- Group 2: Rails after turnout (both paths)

**Why**: Turnout splits the groups

---

### Test Case 3: Multiple Sections
**Layout**:
```
[Straight] -> [Curved] -> [Straight] -> [Turnout] -> [Straight] -> [Curved]
                                           |
                                           v
                                       [Straight] -> [Straight]
```

**Expected Result**: **2 GROUPS**
- Group 1: All rails before turnout (straight, curved, straight)
- Group 2: All rails after turnout (both branches combined)

**Why**: Only one turnout = only one split point

---

### Test Case 4: Two Turnouts
**Layout**:
```
[Straight] -> [Turnout1] -> [Straight] -> [Turnout2] -> [Straight]
```

**Expected Result**: **3 GROUPS**
- Group 1: Rails before Turnout1
- Group 2: Rails between Turnout1 and Turnout2
- Group 3: Rails after Turnout2

**Why**: Two turnouts = two split points

---

## How to Test:

1. **Build layout without turnouts**:
   - Add 5 straight/curved rails
   - Connect them all
   - Click "Auto-Create Groups"
   - Should see: **"Created 1 rail groups/sections"**

2. **Add a turnout**:
   - Add a switch/turnout in the middle
   - Connect rails through it
   - Click "Auto-Create Groups" again
   - Should see: **"Created 2 rail groups/sections"**

3. **Check group membership**:
   - Right-click any rail
   - Look at "Group: Section X"
   - All rails before turnout should show same group
   - All rails after turnout should show different group

---

## The Algorithm:

1. **Find all turnouts** (switch_left, switch_right)
2. **Mark turnouts as boundaries** (not in any group)
3. **For each non-turnout rail**:
   - If not yet grouped, start a new group
   - Traverse to all connected rails (next and prev)
   - Stop when hitting a turnout
   - Add all found rails to the same group
4. **Result**: Groups only split where turnouts exist

---

## Key Points:

✅ **Straight + Curved + Straight = 1 GROUP** (no turnout)
✅ **Any path without turnout = 1 GROUP**
✅ **Turnout = boundary between groups**
❌ **NOT split by rail type** (straight, curved don't matter)
❌ **NOT split by distance or position**

