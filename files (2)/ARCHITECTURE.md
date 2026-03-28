🏗️ DrawScript Architecture Map (v1.8)
Project Goal: A "Sandbox Freedom" Design-to-Code engine for creating absolute-positioned HTML/CSS layouts via a visual 24px grid.

📂 File Structure & Responsibilities
1. styles.py — The Visual Identity
Purpose: Global DARK_QSS stylesheet and UI constants.

Themes: Defines the THEMES dictionary (WHITE, DARK, BLUEPRINT) which provides specific color tuples for the background and grid lines.

UI Styling: Includes specialized CSS for QComboBox (dropdowns) to maintain the "Midnight Arcade" aesthetic.

2. items.py — The Object DNA
CanvasItemMixin: Shared logic for snapping, resizing, hyperlinks, opacity, and the new Position Locking system.

Physics (Locking): The itemChange method intercepts ItemPositionChange signals; if an item is locked, it returns its current position, effectively freezing it in place.

Classes: StyledRectItem, StyledEllipseItem (with Ghost Corner Fix), DraggableTextItem (Mixin-powered), DraggableImageItem, and ButtonComponentItem.

3. widgets.py — The Engine Components
DarkCanvasView: Upgraded to support Grid Toggling and Theme Switching. It stores state for _show_grid and theme-specific colors (_bg_color, _dim_color, _bright_color).

PropertyInspector: A scrollable panel (v1.6) that now includes a specialized Lock Section with a toggle checkbox.

4. main.py — The Brain / Entry Point
KeyboardShortcutsMixin: Now features Ctrl+G to toggle grid visibility on the fly.

Toolbar: Includes a Theme Selection dropdown (QComboBox) to switch the workspace environment.

Save/Load System: Upgraded to Version 6 to persist the locked status of canvas elements.

HTML Generator: Compiles layouts with full support for opacity, box-shadows (v1.7), and absolute positioning.

🛠️ Technical Constraints (The "Rules")
Grid Snapping: Strictly enforced at 24px for all movement and resizing.

Selection Logic: Dashed Neon Cyan indicators follow exact item geometry. Note: Selection and Inspection still work on Locked items.

The Patch Contract: All AI updates must specify the Target File, Class/Method, and Replacement Type to prevent "coherence collapse".

One-Way Dependency: main.py → widgets.py → items.py → styles.py.



🏗️ DrawScript Architecture Map (v1.7)
Project Goal: A "Sandbox Freedom" Design-to-Code engine for creating absolute-positioned HTML/CSS layouts via a visual 24px grid.

📂 File Structure & Responsibilities
1. styles.py — The Visual Identity
Purpose: Contains the global DARK_QSS stylesheet and UI constants.

Constants: GRID_STEP = 24.

UI Tweaks: Scrollbar handles are brightened (#3D4F63) for visibility against dark backgrounds.

2. items.py — The Object DNA
CanvasItemMixin: Shared logic for snapping, resizing, hyperlinks, Opacity (0.0–1.0), and Drop Shadow state.

StyledRectItem: Rounded rectangles with custom borders and visual depth.

StyledEllipseItem: Free-form ovals with independent scaling and a shape() override to fix corner hit-detection.

DraggableTextItem: Now inherits from CanvasItemMixin, supporting full transparency and shadows.

DraggableImageItem: Scalable local images with opacity support.

ButtonComponentItem: Grouped component with an inline-editable centered text label (_ButtonLabelItem).

3. widgets.py — The Engine Components
DarkCanvasView: The 24px grid system with panning (Space+Drag), zooming (Ctrl+Scroll), and 1px/24px keyboard nudging.

PropertyInspector: A scrollable panel (v1.6) with dynamic sections for Colors, Borders, Opacity Sliders, and Collapsible Drop Shadow controls.

4. main.py — The Brain / Entry Point
Purpose: Initializes the app and connects all modules.

Save/Load System: Upgraded to Version 5 to archive opacity levels and drop shadow parameters.

HTML Generator: Compiles canvas items into CSS with opacity and box-shadow properties, using a qt_blur * 2 conversion for visual parity.

🛠️ Technical Constraints (The "Rules")
Grid Snapping: Everything must snap to GRID_STEP (24px) during move and resize.

Selection Visuals: Selected items show a Dashed Neon Cyan indicator that follows exact geometry.

Modular Patching: AI must return specific logic blocks (methods/classes) only, never full files.

The Patch Contract: Every code update must specify the target file, class/method, and replacement type.