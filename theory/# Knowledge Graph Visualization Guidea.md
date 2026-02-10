# Knowledge Graph Visualization Guidea

## Overview

The Knowledge Graph Visualization displays the dual-graph system as an interactive network diagram. Nodes represent narrative elements (characters, events, concepts, memories) and edges show relationships between them.

## Visual Style

**Matching Reference Aesthetic:**
- Orange bordered rectangles (#FF5722) for nodes
- Dashed orange lines for connections
- Edge labels showing relationship types (REMEMBERS, TRUSTS, SUPPRESSES, etc.)
- Dark background (#0a0a0a) with brown accents
- Monospace font throughout

## Features

### View Modes

**Master Graph**
- Shows the complete canonical truth (all nodes and edges)
- What actually happened in the narrative
- Contains suppressed information Echo doesn't know yet

**Player Graph (Default)**
- Shows only what Echo currently has access to
- Starts with 4 nodes (Echo, Ryker, Kai, SEED Project)
- Grows as conversation unlocks suppressed memories
- Real-time updates as suppressions are lifted

### Interactive Elements

**Node Hover**
- Hover over any node to see:
  - Node type (Person, Event, Concept, etc.)
  - Full label
  - Description from node data
- Nodes highlight with thicker borders on hover

**Node States**
- **Active**: Bright orange border, visible text
- **Suppressed**: Dim border (#4a2a20), grayed out, dashed overlay
- **Corrupted**: Red-orange border (#FF3D00) for high corruption levels

**Edge Labels**
- Relationship type displayed at midpoint of each connection
- Active edges in orange, inactive in brown

### Controls

**Search Bar**
- Filter nodes by name
- Displays match count in footer

**View Toggle**
- Orange button switches between Master/Player graphs
- Shows current mode with filled background

**ACT 1 Badge**
- Displays current narrative act
- Changes color based on progression

**Reset Layout Button**
- Circular arrow icon (top right)
- Regenerates force-directed layout

**Fullscreen Toggle**
- Maximize/minimize icon
- Expands graph to full viewport

### Real-Time Updates

The graph dynamically responds to conversation:

1. **Node Unlocking**: When you trigger suppression rules, new nodes appear
2. **Badge Notification**: Number badge on graph icon shows node count
3. **Contradiction Alert**: Red exclamation mark in sidebar when contradictions detected

## How to Use

### Step 1: Start in Conversation View
- Have conversation with Echo using the chat interface
- Build trust, mention keywords, trigger unlocks

### Step 2: Monitor State Panel
- Watch "Active Suppressions" counter
- Track keyword mentions (Kai, Ryker, etc.)
- See when trust/stability thresholds are crossed

### Step 3: Switch to Graph View
- Click the Network icon in left sidebar
- See which nodes have been unlocked
- Compare Player Graph (Echo's knowledge) vs Master Graph (truth)

### Step 4: Identify Gaps
- Suppressed nodes appear dimmed with dashed borders
- Missing connections reveal holes in Echo's memory
- Contradiction edges show logical conflicts

## Example Walkthrough

**Initial State (Player Graph)**
```
Nodes: 4
- Echo
- Ryker  
- Kai
- SEED Project

Edges: 1
- Echo TRUSTS Ryker
```

**After mentioning "Kai" 3 times**
```
New Nodes Unlocked:
- Memory Fragment 1 ("I'll get you out of here")
- Kai Death Event (suppressed becomes visible)
```

**After reaching 60% trust**
```
New Nodes Unlocked:
- Cradle Protocol (the directive controlling Echo)
- Authority Lock (suppression rule revealed)
```

**After detecting contradictions**
```
New Nodes Unlocked:
- Kai Alive Lie (the false belief)

New Edge:
- Kai Alive Lie CONTRADICTS Kai Death Event
```

## Technical Details

### Force-Directed Layout
- Nodes repel each other (prevents overlap)
- Edges create attraction (groups connected nodes)
- Gentle center pull (keeps graph visible)
- Physics simulation runs for 5 seconds then stops

### Performance
- Canvas-based rendering for smooth performance
- 1200x800 viewport with responsive scaling
- Handles up to ~50 nodes efficiently

### Styling Consistency
- Matches terminal aesthetic from conversation view
- Orange accent color (#FF5722) throughout
- Monospace font (Courier New)
- Dark browns and blacks for backgrounds

## Future Enhancements

Potential additions for the graph system:

- **Drag & Drop**: Move nodes manually
- **Zoom & Pan**: Navigate large graphs
- **Time Slider**: Rewind conversation to see graph at earlier states
- **Edge Filtering**: Show/hide specific relationship types
- **Export**: Save graph as image or JSON
- **Clustering**: Group related nodes visually
- **Animation**: Highlight recently unlocked nodes
- **Mini-map**: Overview for large graphs
