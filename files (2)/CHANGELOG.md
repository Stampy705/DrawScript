# 📜 DrawScript Changelog

## v1.7 — "Visual Mastery" Release
- **Opacity Engine**: Implemented 0–100% transparency sliders for all item types (Rect, Ellipse, Text, Image, Button).
- **Drop Shadow Support**: Added performance-optimized depth effects using `QGraphicsDropShadowEffect`.
- **Refined CSS Export**: HTML generation now includes `opacity` and professional `box-shadow` strings with alpha-channel support.
- **Code Refactor**: `DraggableTextItem` now inherits from `CanvasItemMixin` for unified feature support.
- **Persistence Upgrade**: Bumped to **Version 5** Save/Load with backward compatibility for Version 4 files.

## v1.6
- **Ghost Corner Fix**: Repaired hit-detection for circles so handles are clickable.
- **Modularized Architecture**: Successfully split the project into specialized modules.
- **Scrollable UI**: Implemented `QScrollArea` in the Property Inspector to prevent overlap.


## v1.7 (Planning Phase)
- **Roadmap Established**: Focusing on "Visual Mastery" through Opacity, Drop Shadows, and Canvas Themes.
- **Performance Strategy**: Identified `QGraphicsDropShadowEffect` as the mandatory implementation for heavy shadow rendering to prevent UI lag.

## v1.6 (Current Build)
- **Ghost Corner Fix**: Overrode `shape()` in `StyledEllipseItem` to ensure corners/handles are clickable, preventing deselection during resize.
- **Modularized Architecture**: Successfully split the project into `main`, `items`, `widgets`, and `styles` for better context management.
- **Scroll Area Implementation**: Wrapped `PropertyInspector` in a `QScrollArea` to prevent UI overlap in complex designs.
- **Oval Scaling**: Unlocked independent Width/Height resizing for `StyledEllipseItem`.
- **Editable Buttons**: Implemented `ButtonComponentItem` with an inline-editable `_ButtonLabelItem` child.
- **Hyperlink Engine**: Verified full integration of URL support across all shapes, images, and text.

## v1.5
- **Power Shortcuts**: Added Ctrl+D (Duplicate), Ctrl+A (Select All), and Arrow Key nudging (1px/24px).