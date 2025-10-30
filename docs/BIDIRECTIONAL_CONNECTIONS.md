# Bidirectional Connection Logic

## Overview
Every connection between two blocks creates a **bidirectional relationship** where one block's `next` corresponds to the other block's `prev`.

## Core Principle

**"For one block, the given rail is PREV; for another, it is NEXT"**

This means:
- If Block A has Block B in its `next_rails`, then Block B MUST have Block A in its `prev_rails` (for normal connections)
- The relationship is determined by which connection points are used

## The 4 Connection Types

### Type 1: End-to-Start (Normal Forward)
```
[Block A]━━end → start━━[Block B]
```

**Logic:**
- Block A's **end** connects to Block B's **start**
- Block A points **TO** Block B → B is **NEXT** for A
- Block A comes **BEFORE** Block B → A is **PREV** for B

**Code:**
```python
block1.next_rails.append(block2)  # B is next for A
block2.prev_rails.append(block1)  # A is prev for B
```

**Result:**
```
A.next_rails = [..., B]
B.prev_rails = [..., A]
```

### Type 2: Start-to-End (Normal Reverse)
```
start[Block A]━━← end━━[Block B]
```

**Logic:**
- Block A's **start** connects to Block B's **end**
- Block B points **TO** Block A → B is **PREV** for A  
- Block B comes **BEFORE** Block A → A is **NEXT** for B

**Code:**
```python
block1.prev_rails.append(block2)  # B is prev for A
block2.next_rails.append(block1)  # A is next for B
```

**Result:**
```
A.prev_rails = [..., B]
B.next_rails = [..., A]
```

### Type 3: Start-to-Start (Facing Away)
```
start[Block A]━━↔━━[Block B]start
```

**Logic:**
- Block A's **start** connects to Block B's **start**
- Both blocks point **AWAY** from the connection
- Each block considers the other as **PREVIOUS** (coming from behind)

**Code:**
```python
block1.prev_rails.append(block2)  # B is prev for A
block2.prev_rails.append(block1)  # A is prev for B
```

**Result:**
```
A.prev_rails = [..., B]
B.prev_rails = [..., A]
```

### Type 4: End-to-End (Facing Together)
```
[Block A]end━━↔━━end[Block B]
```

**Logic:**
- Block A's **end** connects to Block B's **end**
- Both blocks point **TOWARD** the connection
- Each block considers the other as **NEXT** (pointing forward to it)

**Code:**
```python
block1.next_rails.append(block2)  # B is next for A
block2.next_rails.append(block1)  # A is next for B
```

**Result:**
```
A.next_rails = [..., B]
B.next_rails = [..., A]
```

## Visual Summary

```
Connection Type          │ Block A        │ Block B        │ Bidirectional?
─────────────────────────┼────────────────┼────────────────┼──────────────
end → start (forward)    │ next=[B]       │ prev=[A]       │ ✅ A→B, B←A
start ← end (reverse)    │ prev=[B]       │ next=[A]       │ ✅ A←B, B→A
start ↔ start (away)     │ prev=[B]       │ prev=[A]       │ ✅ Both ←
end ↔ end (together)     │ next=[B]       │ next=[A]       │ ✅ Both →
```

## Implementation Details

### Connection Function Signature:
```python
def connect_blocks(self, 
                  block_id1: str, point1: str,  # First block and its connection point
                  block_id2: str, point2: str   # Second block and its connection point
                  ) -> bool:
```

### Full Algorithm:

```python
# 1. Set bidirectional connection in connections dict
block1.connections[point1] = (block_id2, point2)
block2.connections[point2] = (block_id1, point1)

# 2. Determine next/prev based on connection points
if 'end' in point1 and 'start' in point2:
    # Type 1: end→start
    block1.next_rails.append(block2)
    block2.prev_rails.append(block1)

elif 'start' in point1 and 'end' in point2:
    # Type 2: start←end
    block1.prev_rails.append(block2)
    block2.next_rails.append(block1)

elif 'start' in point1 and 'start' in point2:
    # Type 3: start↔start
    block1.prev_rails.append(block2)
    block2.prev_rails.append(block1)

elif 'end' in point1 and 'end' in point2:
    # Type 4: end↔end
    block1.next_rails.append(block2)
    block2.next_rails.append(block1)

# 3. Immediate verification
verify_connection_consistency(block1, block2)
```

### Immediate Verification:

After every connection, the system verifies:

```python
def _verify_connection_consistency(block_id1, block_id2):
    # If A has B in next_rails:
    #   → B should have A in prev_rails OR next_rails
    
    if block2 in block1.next_rails:
        if block1 not in block2.prev_rails and block1 not in block2.next_rails:
            ⚠️  WARNING: Inconsistency detected!
    
    # If A has B in prev_rails:
    #   → B should have A in next_rails OR prev_rails
    
    if block2 in block1.prev_rails:
        if block1 not in block2.next_rails and block1 not in block2.prev_rails:
            ⚠️  WARNING: Inconsistency detected!
```

## Examples

### Example 1: Building a Linear Track

```python
# Create 3 blocks: A, B, C
A = create_block("straight")  # A has start and end points
B = create_block("straight")  # B has start and end points
C = create_block("straight")  # C has start and end points

# Connect A.end → B.start
connect_blocks(A.id, "end", B.id, "start")
# Result:
#   A.next_rails = [B]
#   B.prev_rails = [A]

# Connect B.end → C.start
connect_blocks(B.id, "end", C.id, "start")
# Result:
#   B.next_rails = [C]
#   C.prev_rails = [B]

# Final structure:
[A]━━→[B]━━→[C]
A: next=[B], prev=[]     # Start of chain
B: next=[C], prev=[A]    # Middle of chain
C: next=[], prev=[B]     # End of chain
```

### Example 2: U-Turn with Start-to-Start

```python
# Create 2 blocks
A = create_block("straight")
B = create_block("straight")

# Connect A.start ↔ B.start (both facing away)
connect_blocks(A.id, "start", B.id, "start")
# Result:
#   A.prev_rails = [B]
#   B.prev_rails = [A]

# Visual:
    ← [A]start ↔ start[B] →
    
# Both blocks point away from the connection point
```

### Example 3: Meeting Point with End-to-End

```python
# Create 2 blocks
A = create_block("straight")
B = create_block("straight")

# Connect A.end ↔ B.end (both facing together)
connect_blocks(A.id, "end", B.id, "end")
# Result:
#   A.next_rails = [B]
#   B.next_rails = [A]

# Visual:
    [A] → end ↔ end ← [B]
    
# Both blocks point toward the connection point
```

### Example 4: Turnout (Multiple Next)

```python
# Create turnout and 2 branches
T = create_block("switch_left")   # Turnout
B1 = create_block("straight")      # Branch 1
B2 = create_block("straight")      # Branch 2

# Connect T.end → B1.start
connect_blocks(T.id, "end", B1.id, "start")
# T.next_rails = [B1]

# Connect T.branch_left → B2.start
connect_blocks(T.id, "branch_left", B2.id, "start")
# T.next_rails = [B1, B2]  # Turnout has multiple next!

# Visual:
         [B1]
        ╱
    [T]
        ╲
         [B2]
```

## Validation Checks

### At Connection Time:
1. ✅ Both blocks exist
2. ✅ Connection points exist on both blocks
3. ✅ Bidirectional `connections` dict updated
4. ✅ Proper `next_rails` / `prev_rails` updated based on points
5. ✅ **Immediate verification** of consistency

### At Save/Group Creation Time:
1. ✅ All blocks in groups
2. ✅ No isolated blocks (empty next+prev)
3. ✅ Proper next/prev structure
4. ✅ **Bidirectional consistency** (A→B ⟺ B←A)

## Common Patterns

### Pattern 1: Linear Chain
```
[A]end→start[B]end→start[C]end→start[D]

A: next=[B], prev=[]
B: next=[C], prev=[A]
C: next=[D], prev=[B]
D: next=[], prev=[C]
```

### Pattern 2: Loop
```
[A]end→start[B]end→start[C]end→start[A]

A: next=[B], prev=[C]
B: next=[C], prev=[A]
C: next=[A], prev=[B]
```

### Pattern 3: Y-Junction (Turnout)
```
         [B]
        ╱
[A]→[T]
        ╲
         [C]

A: next=[T], prev=[]
T: next=[B, C], prev=[A]
B: next=[], prev=[T]
C: next=[], prev=[T]
```

### Pattern 4: Reverse Connection
```
start[A]←end[B]←end[C]

A: next=[], prev=[B]
B: next=[A], prev=[C]
C: next=[B], prev=[]
```

## Error Detection

If a connection is created incorrectly, the system will:

1. **Immediate Warning** (at connection time):
```
⚠️  WARNING: Connection inconsistency detected immediately after connect!
   rail_0001 has rail_0002 in next_rails
   BUT rail_0002 has neither rail_0001 in prev_rails nor next_rails
```

2. **Validation Error** (at save/group time):
```
❌ Connection inconsistency: 'rail_0001' → 'rail_0002'
   'rail_0001' has 'rail_0002' in next_rails
   BUT 'rail_0002' does NOT have 'rail_0001' in prev_rails!
```

## Summary

✅ **Bidirectional**: Every connection updates both blocks
✅ **Reciprocal**: One block's `next` = other block's `prev` (usually)
✅ **Point-Aware**: Logic depends on which connection points are used
✅ **Verified**: Immediate check after connection
✅ **Validated**: Full check before save/group creation

**The principle:** *"For one block, the given rail is PREV; for another, it is NEXT"* is enforced at connection time and verified at save time!

