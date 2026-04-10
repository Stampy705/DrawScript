# DrawScript v2.0 — The Ink Engine

> A **modular vector design suite** built on PyQt6 that translates freehand sketches and geometric blocks into production-ready HTML, CSS, and SVG code.

![DrawScript v2.0](https://img.shields.io/badge/DrawScript-v2.0_beta-ff6b00?style=flat-square&logo=python&logoColor=white)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab?style=flat-square)
![PyQt6](https://img.shields.io/badge/PyQt6-required-41cd52?style=flat-square)
![Status: Beta](https://img.shields.io/badge/status-beta-orange?style=flat-square)
![License MIT](https://img.shields.io/badge/license-MIT-gray?style=flat-square)

---

## 🎨 What is DrawScript?

DrawScript is a **freehand vector editor + semantic code compiler**. Sketch on a 24px-snapped canvas, apply professional styling (shadows, opacity, border-radius), and export directly to production-ready HTML/CSS/SVG. Built for designers who code, and developers who draw.

**Perfect for:**
- 🎨 Rapid UI prototyping with pixel-perfect precision
- 💻 Vector art + instant code generation
- 🏗️ Design system component creation
- ✏️ Freehand sketching with automatic path optimization

---

## 🏗️ Architecture: The "Patch Contract" System

DrawScript follows a **strict one-way dependency chain** for maximum modularity and extensibility:

```
main.py (Orchestration)
   ↓
widgets.py (Interaction Layer)
   ↓
items.py (Geometry Engine)
   ↓
styles.py (Design System)
```

### Module Breakdown

**`main.py` — The Orchestrator**
- `DarkMainWindow` lifecycle and signal/slot wiring
- **Semantic HTML Compiler** (CSS layouts, SVG wrapping, hyperlink injection)
- **Version 8 State Persistence** (save/load projects with delta-encoded paths)
- Project management and export workflows

**`widgets.py` — The Interaction Layer**
- `DarkCanvasView` — High-performance 1000×700 infinite canvas with `QPainter`-based rendering
- `PropertyInspector` — Real-time sidebar for opacity, shadows, corner-radius, pen color/width
- Mouse tracking, tool mode management, `drawForeground` overlays
- Active tool state storage (`_pen_color`, `_pen_width`)

**`items.py` — The Geometry Engine**
- Canvas object classes: `CanvasRectItem`, `CanvasEllipseItem`, `CanvasTextItem`, `CanvasImageItem`, `CanvasButtonItem`, `CanvasPathItem`
- **Ramer-Douglas-Peucker (RDP) curve simplification** (30–70% point reduction)
- **Vector Boolean Eraser** (mathematical path subtraction via `QPainterPath` intersection)
- Collision detection, bounding box calculation, JSON serialization/deserialization
- Shared `CanvasItemMixin` base class for common logic

**`styles.py` — The Design System**
- Global constants: `GRID_SIZE = 24`, color palettes, opacity ramps
- Master QSS (Qt Style Sheets) engine
- `CSSValidator` for theme injection with safety guardrails
- Custom theme loader (user `.qss` files)

### Design Philosophy

✅ **One-way dependency chain** — No circular imports; clear signal flow  
✅ **Composition over inheritance** — `CanvasItemMixin` provides shared logic  
✅ **Separation of concerns** — Rendering, persistence, compilation are independent  
✅ **Grid-first layout** — 24px snap-to-grid for geometric precision  
✅ **Extensibility** — Add new shape types or export formats with minimal refactoring  

---

## ✨ Core v2.0 Features

### 🖋️ The Ink Engine — Freehand Vector Art

**Ramer-Douglas-Peucker (RDP) Simplification**
```python
# Raw mouse points: [P0, P1, P2, ... P1000]
# After RDP: [P0, P15, P312, ... P987]  ← 30–70% fewer points, same visual fidelity
# Result: Lightweight SVG exports, faster rendering, smaller file sizes
```
- Preserves curve integrity while aggressively reducing redundant points
- Configurable epsilon for tuning reduction vs. fidelity trade-off

**Active Tool State**
- Users select **pen color** and **pen width** in the toolbar *before* drawing
- State stored in `DarkCanvasView._pen_color` and `DarkCanvasView._pen_width`
- Live `drawForeground` preview shows the selected color/width as you hover
- Applied immediately to the new `CanvasPathItem` when drawing completes

**Coordinate Alignment**
- During HTML export, the engine calculates the exact bounding box of each path
- SVG containers are perfectly framed without cropping or unnecessary padding
- Paths maintain visual position and scale across all export formats

### 🔄 Vector Boolean Eraser

**The Cutter Logic**
Unlike raster erasers that wipe pixels, DrawScript's eraser performs **mathematical Boolean subtraction** on vector paths.

```
Traditional raster eraser: ❌ Converts path to raster, deletes pixels
DrawScript vector eraser:  ✓ Performs Boolean Subtraction on QPainterPath
                           ✓ Severs paths into independent segments
                           ✓ Maintains clean SVG export integrity
```

**Mathematical Severing**
- When an eraser stroke (a circular `QPainterPath`) intersects a `CanvasPathItem`:
  1. The engine walks the path's points in order
  2. Detects entry/exit intersections with the eraser region
  3. Creates new independent segments for the remaining path
  4. Replaces the original item with severed children

**Fast Rejection Test**
- Uses `QPainterPathStroker` to inflate paths into filled regions for high-speed intersection detection
- Only runs expensive point-walk math on paths that actually collide
- Scales to 50+ path items without performance degradation

**Variable Eraser Size**
- Adjust eraser diameter on-the-fly during editing
- `Shift+Scroll` or property panel adjustment
- Real-time preview of erasure region before confirming

### 📝 The Semantic Compiler

**CSS Layouts**
```python
# A CanvasRectItem becomes:
<div style="position: absolute; 
            left: 100px; top: 150px; 
            width: 200px; height: 80px;
            background: #ff0066;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            opacity: 0.95;">
</div>
```

**SVG Integration**
```html
<!-- A CanvasPathItem with RDP simplification becomes: -->
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <path d="M 50 100 Q 100 50 150 100 T 200 100" 
        stroke="#000" 
        stroke-width="2" 
        fill="none"/>
</svg>
```

**Hyperlink Wrapping**
- If an object has a URL assigned, the compiler wraps the entire block:
```html
<a href="https://example.com" style="position: absolute; ...">
  <div style="...">Clickable Block</div>
</a>
```

**Button Elements**
- `CanvasButtonItem` exports as semantic `<button>` tags
- Maintains accessible HTML semantics for web standards

### 🎛️ State & Customization

**Undo/Redo v2.0**
- Action stack stores tuples: `("add", [item])` or `("delete", [items])`
- `Ctrl+Z` accurately removes a new drawing or restores a deleted block
- Supports multi-item operations (group add/delete)

**UI Skinning & Theme Injection**
- Users create custom `.qss` (Qt Style Sheets) files
- `CSSValidator` safety pipeline ensures critical UI elements remain visible
- Load themes on startup with persistent state
- Live reload support during development

**Save System v8**
- Compressed JSON schema with delta-encoded path coordinates
- Reduces file sizes by **60%** compared to uncompressed exports
- Version migration from v7 projects (backward compatible)
- Persistent theme settings saved with project

---

## ⌨️ Command & Interface Reference

| Category | Shortcut / Feature | Purpose |
|----------|-------------------|---------|
| **Tools** | `[B]` (or toolbar click) | Activate **Pen Mode** — freehand drawing |
| | `[E]` | Activate **Eraser Mode** — vector Boolean subtraction |
| | `[R]`, `[C]`, `[T]` | Rect, Circle/Ellipse, Text tools |
| **Navigation** | `Space + Drag` | Pan across the infinite canvas |
| | `Ctrl + Wheel` | Zoom in/out |
| **Precision** | `Arrow Keys` | 1px nudge movement |
| | `Shift + Arrows` | 24px grid-snap movement |
| **Management** | `[G]` | **Group** items into a Syndicate |
| | `[U]` | **Ungroup** — dismantle a Syndicate |
| | `Ctrl+Z` | Undo last action |
| | `Ctrl+Shift+Z` | Redo |
| **Styling** | Property Inspector | Live editing of Opacity, Shadows, Corner-Radius, Pen Color/Width |
| **File Ops** | `Ctrl+S` | Save project (v8 format) |
| | `Ctrl+Shift+E` | Export as HTML/CSS/SVG |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10 or higher**
- **PyQt6** (`pip install PyQt6`)

### Installation

```bash
# Clone the repository
git clone https://github.com/Stampy705/DrawScript.git
cd DrawScript

# Install dependencies
pip install PyQt6

# Run DrawScript
python main.py
```

### Your First Design

1. **Launch** — You'll see the main window with a 24px grid overlay
2. **Sketch with the Pen Tool** — Press `[B]`, select a pen color in the Property Inspector, and draw freely on the canvas
3. **Create Shapes** — Press `[R]` for rectangles, `[C]` for circles, `[T]` for text
4. **Refine with the Eraser** — Press `[E]` and erase parts of your drawings (paths are severed, not deleted)
5. **Style** — Use the Property Inspector to adjust opacity, shadows, border-radius
6. **Export** — Press `Ctrl+Shift+E` to generate production-ready HTML/CSS/SVG
7. **Save** — Press `Ctrl+S` to persist your project in v8 format

---

## 💡 Use Cases

### Use Case 1: Rapid UI Prototyping
```
1. Sketch button layouts and form fields by hand
2. Apply styles (shadows, rounded corners) in real-time
3. Export semantic HTML and integrate into your web app
4. Iterate without leaving DrawScript
```

### Use Case 2: Icon Design & SVG Export
```
1. Draw an icon freehand with the Pen tool
2. Apply RDP simplification (automatic during save)
3. Export as clean SVG with minimal path points
4. Use in web, mobile, or print projects
```

### Use Case 3: Design System Component Library
```
1. Create reusable component templates
2. Apply custom `.qss` themes for brand consistency
3. Sketch variations and export them as a component set
4. Version control with git
```

---

## 🔧 Advanced: Extending DrawScript

### Adding a New Shape Type

**Step 1: Define the item in `items.py`**
```python
class CanvasTriangleItem(CanvasItemMixin, QGraphicsItem):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x, self.y = x, y
        self.width, self.height = width, height
    
    def paint(self, painter, option, widget):
        # Draw triangle geometry
        points = [QPointF(self.x, self.y + self.height),
                  QPointF(self.x + self.width / 2, self.y),
                  QPointF(self.x + self.width, self.y + self.height)]
        painter.fillPath(QPolygonF(points), self.brush)
    
    def boundingRect(self):
        return QRectF(self.x, self.y, self.width, self.height)
```

**Step 2: Register in `widgets.py` toolbar**
```python
# In DarkCanvasView.__init__()
self.triangle_tool = ToolMode("TRIANGLE", CanvasTriangleItem)
self.toolbar.add_tool("Triangle", self.triangle_tool)
```

**Step 3: Add serialization in `main.py`**
```python
def item_to_dict(item):
    if isinstance(item, CanvasTriangleItem):
        return {
            "type": "triangle",
            "x": item.x,
            "y": item.y,
            "width": item.width,
            "height": item.height,
        }

def dict_to_item(data):
    if data["type"] == "triangle":
        return CanvasTriangleItem(data["x"], data["y"], data["width"], data["height"])
```

### Custom Theme Injection

**Create a `.qss` file (e.g., `themes/neon.qss`):**
```css
/* Neon Terminal Theme */
QMainWindow {
    background-color: #0a0a0a;
    color: #00ff00;
}

QToolBar {
    background-color: #1a1a1a;
    border: 1px solid #00ff00;
}

QPushButton {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #00ff00;
    font-family: 'Courier New';
    padding: 4px;
}

QPushButton:hover {
    background-color: #00ff00;
    color: #0a0a0a;
}
```

**Load in DrawScript:**
```python
# In main.py on startup
qss_path = "themes/neon.qss"
with open(qss_path) as f:
    app.setStyleSheet(f.read())
```

---

## 📊 Performance Characteristics

| Operation | Behavior |
|-----------|----------|
| **RDP Simplification** | O(n log n) time; 30–70% point reduction |
| **Large Projects** | Tested with 500+ objects, 50k+ path points |
| **Export Speed** | HTML/SVG generation in <500ms for typical designs |
| **Eraser Math** | Fast rejection + point-walk; scales to 50+ intersecting paths |
| **Save Format** | Delta-encoded v8 reduces file size by ~60% |

---

## ⚠️ Beta Status & Known Limitations

DrawScript v2.0 is **actively in development**. Users should be aware of:

### Current Limitations
- 🔴 **Bezier Curve Editing UI** — Curves are simplified via RDP; full control points not exposed
- 🔴 **PDF Export** — Use OS print-to-PDF as workaround
- 🔴 **No Multi-User Editing** — Single-user local projects only
- 🟡 **Complex Vector Operations** — Boolean eraser may miss edge cases with overlapping paths
- 🟡 **Memory Management** — Very large projects (500+ objects) may cause slowdowns

### Known Issues
- When erasing paths that self-intersect or overlap, occasional orphaned segments may remain
- Coordinate precision may shift after 100+ undo/redo cycles (recommend saving)
- Theme injection with incomplete `.qss` files may break UI; use `CSSValidator`

### Roadmap for v2.1+

- ✅ **Variable Eraser Size** — Adjust on-the-fly during editing
- ✅ **Active Tool Properties** — Pre-select pen color/thickness before drawing
- 🔜 **Smart Guides** — Visual alignment helpers and snap lines
- 🔜 **Layer Panels** — Organize and manage object hierarchy
- 🔜 **Animation Export** — CSS keyframes and transition effects
- 🔜 **Typography Panel** — Advanced text styling and font management
- 🔜 **Bezier Editor** — Full curve point manipulation UI

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/your-idea`)
3. **Follow the Patch Contract architecture** — maintain the one-way dependency chain
4. **Write clear, modular code** with docstrings
5. **Test thoroughly** with keyboard shortcuts and export workflows
6. **Submit a pull request** with a detailed description

### Code Style
- Follow **PEP 8** with 4-space indentation
- Use **type hints** where possible
- Write **docstrings** for all public methods and classes
- Keep functions small and testable
- Avoid modifying `styles.py` constants without discussion

---


## 🎨 The Evolution: "drawscript > drawscript > 2"

This project has grown from a simple box-drawing tool into a **vector art engine with semantic code generation**:

- **v1.0** → Basic canvas and shape tools
- **v1.5** → Grid snapping and basic HTML export
- **v1.9** → Multi-item grouping, rulers, Version 7 save format
- **v2.0** ✨ → **The Ink Engine** (RDP simplification, Boolean eraser, active tool state, Version 8 save, theme injection)

---

## 💬 Support & Community

- **Report Issues**: [GitHub Issues](https://github.com/Stampy705/DrawScript/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Stampy705/DrawScript/discussions)

---

## 🙏 Acknowledgments

DrawScript builds on:
- **PyQt6** — For a robust, responsive GUI framework
- **Ramer-Douglas-Peucker Algorithm** — For elegant curve simplification
- **Qt's QPainterPath** — For reliable vector path mathematics
- **The Open Source Community** — For inspiration, algorithms, and feedback

---

## 📝 License

MIT — do whatever you want with it.

---

<div align="center">

**Built with ❤️ and a lot of vector math**  
*Bridging freehand creativity and production-ready code.*

[⭐ Star us on GitHub](https://github.com/Stampy705/DrawScript) | [🐛 Report Issues](https://github.com/Stampy705/DrawScript/issues) | [💬 Discuss](https://github.com/Stampy705/DrawScript/discussions)

</div>
