# ⚠️ Known Issues & Technical Debts

## 🖥️ Performance
- **Shadow Heavy**: Shadow rendering in PyQt can be computationally heavy; the team must use `QGraphicsDropShadowEffect` for all v1.7 shadow implementations to maintain 60fps canvas performance.
- **Layer Refresh**: The Property Inspector Z-index labels may lag during rapid multi-select alignment operations (widgets.py ~line 350).

## 📐 Geometry & Logic
- **Zoom Drift**: Text labels inside `ButtonComponentItem` may experience minor visual center-drift when resizing at zoom levels > 150% (items.py ~line 400).
- **Path Portability**: Exported HTML uses absolute local file paths for images; manual relative path adjustment is required for web hosting (main.py ~line 500).

## 🎨 UI/UX
- **Invisible Fold**: Due to the dark theme, the Property Inspector scrollbar can be difficult to see against the background; requires a color update in `styles.py`.