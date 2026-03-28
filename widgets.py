"""
DrawScript — widgets.py  (v1.6)
Reusable Qt widgets: DarkCanvasView and PropertyInspector.
Also exports the _h_rule() factory used by both this module and main.py.

Changes (v1.6):
  - PropertyInspector: all controls are now wrapped in a QScrollArea so the
    panel never overlaps when loaded with many sections.  setFixedHeight() is
    gone; the inspector grows to fill whatever space the panel gives it and
    scrolls when the content is taller than that space.
  - PropertyInspector: vertical spacing between UI elements increased to 12 px
    to give the design breathing room.
  - DarkCanvasView: THEMES-based background/grid; set_theme / toggle_grid.
  - PropertyInspector: lock position checkbox.
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QColorDialog, QFrame, QStackedWidget,
    QSizePolicy, QLineEdit, QScrollArea, QCheckBox,
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QPolygonF

from styles import GRID_STEP, THEMES
from items import (
    _snap,
    StyledRectItem,
    StyledEllipseItem,
    DraggableTextItem,
    DraggableImageItem,
    ButtonComponentItem,
)


# ---------------------------------------------------------------------------
# Shared UI helper
# ---------------------------------------------------------------------------

def _h_rule() -> QFrame:
    """Return a styled horizontal separator line."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


# ---------------------------------------------------------------------------
# RulerWidget
# ---------------------------------------------------------------------------

class RulerWidget(QWidget):
    """v1.9: A separate widget that paints pixel markers based on zoom/pan."""

    def __init__(self, orientation=Qt.Orientation.Horizontal):
        super().__init__()
        self.orientation = orientation
        self.offset = 0
        self.zoom = 1.0
        if self.orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(24)
        else:
            self.setMinimumWidth(24)

    def set_view_state(self, offset: int, zoom: float):
        self.offset = int(offset)
        self.zoom = max(0.01, float(zoom))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#111827"))
        painter.setPen(QColor("#7B8EA8"))
        # Painting logic: marks every 24px * zoom, labeled with canvas coords
        step = max(8.0, GRID_STEP * self.zoom)
        ruler_len = self.width() if self.orientation == Qt.Orientation.Horizontal else self.height()
        major_h = 10
        minor_h = 5
        phase = self.offset % step
        pos = -phase
        index = int((self.offset - phase) / step)

        while pos <= ruler_len:
            is_major = (index % 6 == 0)
            if self.orientation == Qt.Orientation.Horizontal:
                y1 = self.height() - 1
                y0 = y1 - (major_h if is_major else minor_h)
                painter.drawLine(int(pos), y0, int(pos), y1)
                if is_major:
                    canvas_coord = int(round((self.offset + pos) / self.zoom))
                    painter.drawText(int(pos) + 2, 10, str(canvas_coord))
            else:
                x1 = self.width() - 1
                x0 = x1 - (major_h if is_major else minor_h)
                painter.drawLine(x0, int(pos), x1, int(pos))
                if is_major:
                    canvas_coord = int(round((self.offset + pos) / self.zoom))
                    painter.drawText(2, int(pos) + 10, str(canvas_coord))
            pos += step
            index += 1

# ---------------------------------------------------------------------------
# DarkCanvasView  (v2.1 — Canvas Engine with Ink/Eraser tool modes)
# ---------------------------------------------------------------------------

class DarkCanvasView(QGraphicsView):
    zoomChanged    = pyqtSignal(float)
    scrollChanged  = pyqtSignal(int, int)
    stroke_completed = pyqtSignal(list)
    SCENE_W = 1000
    SCENE_H = 700

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(0, 0, self.SCENE_W, self.SCENE_H)

        self._show_grid = True
        self._theme_key = "WHITE"
        _bg, _dim, _bright, _ruler_text = THEMES[self._theme_key]
        self._bg_color   = QColor(_bg)
        self._grid_dim   = QColor(_dim)
        self._grid_bright = QColor(_bright)
        self.scene.setBackgroundBrush(QBrush(self._bg_color))

        self.setScene(self.scene)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._zoom = 1.0
        self.horizontalScrollBar().valueChanged.connect(self._emit_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._emit_scroll_changed)

        self._box_counter   = 0
        self._text_counter  = 0
        self._image_counter = 0
        self._z_counter     = 0

        self.nudge_callback = None

        # ── Tool-mode flags (v2.1) ─────────────────────────────────────────
        self._brush_mode  = False
        self._eraser_mode = False
        self._pen_color   = QColor("#A5D8FF")
        self._pen_width   = 2.0
        self._eraser_size = 20.0
        self._eraser_pos  = None
        self._brush_stroke_points = []
        self._path_counter        = 0

        self._emit_scroll_changed()

    def _emit_scroll_changed(self):
        self.scrollChanged.emit(
            self.horizontalScrollBar().value(),
            self.verticalScrollBar().value(),
        )

    # ── Background / foreground painting ───────────────────────────────

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if not self._show_grid:
            return
        dim_pen    = QPen(self._grid_dim, 1)
        bright_pen = QPen(self._grid_bright, 1)
        x = int(rect.left()) - (int(rect.left()) % GRID_STEP)
        while x <= rect.right():
            painter.setPen(bright_pen if (x // GRID_STEP) % 6 == 0 else dim_pen)
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += GRID_STEP
        y = int(rect.top()) - (int(rect.top()) % GRID_STEP)
        while y <= rect.bottom():
            painter.setPen(bright_pen if (y // GRID_STEP) % 6 == 0 else dim_pen)
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += GRID_STEP

    def drawForeground(self, painter, rect):
        """Live pen preview and eraser cursor drawn above all scene items."""
        super().drawForeground(painter, rect)
        # Live ink preview while a stroke is in progress
        if self._brush_mode and len(self._brush_stroke_points) > 1:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            pen = QPen(
                self._pen_color, self._pen_width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
            painter.setPen(pen)
            painter.drawPolyline(QPolygonF(self._brush_stroke_points))
        # Eraser circle cursor
        if self._eraser_mode and self._eraser_pos is not None:
            r = self._eraser_size / 2.0
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 0, 127, 25)))
            painter.drawEllipse(self._eraser_pos, r, r)
            painter.setPen(QPen(QColor("#FF007F"), 1.5, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self._eraser_pos, r, r)

    # ── Theme / grid ──────────────────────────────────────────────────

    def set_theme(self, name: str):
        if name not in THEMES:
            return
        self._theme_key = name
        bg, dim, bright, _ruler_text = THEMES[name]
        self._bg_color    = QColor(bg)
        self._grid_dim    = QColor(dim)
        self._grid_bright = QColor(bright)
        self.scene.setBackgroundBrush(QBrush(self._bg_color))
        self.viewport().update()

    def toggle_grid(self):
        self._show_grid = not self._show_grid
        self.viewport().update()

    # ── Tool setters (called from main.py slots) ─────────────────────────

    def set_brush_mode(self, active: bool):
        self._brush_mode = active
        if active:
            # Fade the grid slightly so strokes are easier to see
            self._grid_dim.setAlpha(int(self._grid_dim.alpha() * 0.3))
            self._grid_bright.setAlpha(int(self._grid_bright.alpha() * 0.3))
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self._grid_dim.setAlpha(255)
            self._grid_bright.setAlpha(255)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.viewport().update()

    def set_eraser_mode(self, active: bool):
        self._eraser_mode = active
        self._eraser_pos  = None
        if active:
            self.setCursor(Qt.CursorShape.BlankCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.viewport().update()

    def set_pen_color(self, color: QColor):
        self._pen_color = QColor(color)
        self.viewport().update()

    def set_pen_width(self, width: float):
        self._pen_width = max(0.5, float(width))
        self.viewport().update()

    def set_eraser_size(self, size: float):
        self._eraser_size = max(4.0, float(size))
        if self._eraser_mode:
            self.viewport().update()

    # ── Vector erase ─────────────────────────────────────────────────

    def _vector_erase_at(self, view_pos):
        scene_pos = self.mapToScene(view_pos)
        radius    = self._eraser_size / 2.0
        self._eraser_pos = scene_pos
        self.viewport().update()
        eraser_rect = QRectF(
            scene_pos.x() - radius, scene_pos.y() - radius,
            self._eraser_size, self._eraser_size,
        )
        for item in list(self.scene.items(eraser_rect)):
            from items import CanvasPathItem
            if isinstance(item, CanvasPathItem):
                replacement = item.apply_vector_erase(scene_pos, radius)
                if replacement == [item]:
                    continue
                z_base = item.zValue()
                self.scene.removeItem(item)
                for i, new_item in enumerate(replacement):
                    new_item.setZValue(z_base + i * 0.001)
                    self.scene.addItem(new_item)
            elif hasattr(item, "set_opacity"):
                self.scene.removeItem(item)

    # ── Canvas item factories ──────────────────────────────────────

    def add_box(self):
        offset = (self._box_counter * 24) % 192
        item   = StyledRectItem(60 + offset, 60 + offset)
        item.setZValue(self._z_counter)
        self._z_counter   += 1
        self._box_counter += 1
        self.scene.addItem(item)

    def add_circle(self):
        offset = (self._box_counter * 24) % 192
        item   = StyledEllipseItem(60 + offset, 60 + offset)
        item.setZValue(self._z_counter)
        self._z_counter   += 1
        self._box_counter += 1
        self.scene.addItem(item)

    def add_text(self):
        offset = (self._text_counter * 24) % 192
        item   = DraggableTextItem(
            f"BLOCK_{self._text_counter + 1:02d}", 80 + offset, 80 + offset
        )
        item.setZValue(self._z_counter)
        self._z_counter    += 1
        self._text_counter += 1
        self.scene.addItem(item)

    def add_image(self, file_path: str):
        offset = (self._image_counter * 24) % 192
        item   = DraggableImageItem(file_path, 72 + offset, 72 + offset)
        item.setZValue(self._z_counter)
        self._z_counter     += 1
        self._image_counter += 1
        self.scene.addItem(item)

    def add_button_component(self):
        """Drop a pre-styled Button Component onto the canvas."""
        offset = (self._box_counter * 24) % 192
        item   = ButtonComponentItem(72 + offset, 72 + offset)
        item.setZValue(self._z_counter)
        self._z_counter   += 1
        self._box_counter += 1
        self.scene.addItem(item)

    def clear_canvas(self):
        self.scene.clear()
        self._box_counter   = 0
        self._text_counter  = 0
        self._image_counter = 0
        self._z_counter     = 0

    # ── Key / mouse / wheel events ────────────────────────────────

    def keyPressEvent(self, event):
        key  = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            return

        is_text_editing = any(
            isinstance(it, DraggableTextItem)
            and it.textInteractionFlags() != Qt.TextInteractionFlag.NoTextInteraction
            for it in self.scene.items()
        )

        _ARROW_DELTA = {
            Qt.Key.Key_Left:  (-1,  0),
            Qt.Key.Key_Right: ( 1,  0),
            Qt.Key.Key_Up:    ( 0, -1),
            Qt.Key.Key_Down:  ( 0,  1),
        }

        if key in _ARROW_DELTA and not is_text_editing:
            selected = self.scene.selectedItems()
            if selected:
                dx_unit, dy_unit = _ARROW_DELTA[key]
                step    = GRID_STEP if (mods & Qt.KeyboardModifier.ShiftModifier) else 1
                scene_r = self.scene.sceneRect()
                for item in selected:
                    br = item.boundingRect()
                    nx = max(scene_r.left(),
                             min(scene_r.right()  - br.width(),  item.x() + dx_unit * step))
                    ny = max(scene_r.top(),
                             min(scene_r.bottom() - br.height(), item.y() + dy_unit * step))
                    item.setPos(nx, ny)
                if callable(self.nudge_callback):
                    if step == GRID_STEP:
                        self.nudge_callback(f"GRID SNAP NUDGE — {step}PX SHIFT APPLIED.")
                    else:
                        self.nudge_callback("1PX NUDGE EXECUTED. PRECISION MODE ACTIVE.")
                event.accept()
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.viewport().unsetCursor()
        else:
            super().keyReleaseEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            self._zoom *= factor
            self.zoomChanged.emit(self._zoom)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self._eraser_mode:
            if event.button() == Qt.MouseButton.LeftButton:
                self._vector_erase_at(event.pos())
            event.accept()
            return
        if self._brush_mode:
            # BUGFIX: Only start drawing if the Left Mouse Button is clicked
            if event.button() == Qt.MouseButton.LeftButton:
                self._brush_stroke_points = [self.mapToScene(event.pos())]
            event.accept()
            return
        if self.dragMode() != QGraphicsView.DragMode.ScrollHandDrag:
            hit = self.itemAt(event.pos())
            self.setDragMode(
                QGraphicsView.DragMode.RubberBandDrag if hit is None
                else QGraphicsView.DragMode.NoDrag
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._eraser_mode:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self._vector_erase_at(event.pos())
            else:
                self._eraser_pos = self.mapToScene(event.pos())
                self.viewport().update()
            event.accept()
            return
        if self._brush_mode:
            # BUGFIX: Only draw ink if the Left Mouse Button is actively held down
            if event.buttons() & Qt.MouseButton.LeftButton:
                self._brush_stroke_points.append(self.mapToScene(event.pos()))
                self.viewport().update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._eraser_mode:
            event.accept()
            return
        if self._brush_mode:
            # BUGFIX: Only commit the stroke when the Left Mouse Button is released
            if event.button() == Qt.MouseButton.LeftButton:
                if len(self._brush_stroke_points) >= 2:
                    self.stroke_completed.emit(self._brush_stroke_points)
                self._brush_stroke_points = []
            event.accept()
            return
        super().mouseReleaseEvent(event)
        if self.dragMode() != QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def leaveEvent(self, event):
        if self._eraser_mode:
            self._eraser_pos = None
            self.viewport().update()
        super().leaveEvent(event)


# ---------------------------------------------------------------------------
# PropertyInspector
# ---------------------------------------------------------------------------

class PropertyInspector(QWidget):
    """
    Right-panel property inspector.

    v1.6: All controls live inside a QScrollArea so the panel never overlaps
    when many sections are visible.  Vertical spacing raised to 12 px.
    setFixedHeight() has been removed from the constructor; callers should
    also not set it externally.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item  = None
        self._current_items = []
        self._scene         = None
        self.status_callback = None

        # ── Outer layout: just the scroll area filling the widget ─────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Scroll area wrapping all inspector content ─────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        # Inherit the panel's background so the scrollarea blends in
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        # ── Content widget that holds all the actual controls ──────────
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)          # ← raised from 6 to 12 for breathing room

        heading = QLabel("[ PROPERTIES ]")
        heading.setObjectName("heading")
        root.addWidget(heading)
        root.addWidget(_h_rule())

        # Stack pages: 0=empty, 1=rect/ellipse/button, 2=text, 3=image, 4=alignment
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_empty_page())           # index 0
        self._stack.addWidget(self._build_rect_controls_page())   # index 1
        self._stack.addWidget(self._build_text_controls_page())   # index 2
        self._stack.addWidget(self._build_image_controls_page())  # index 3
        self._stack.addWidget(self._build_alignment_page())       # index 4
        root.addWidget(self._stack)

        # Persistent sections shown below the stack for single-item selections
        self._link_widget    = self._build_link_section()
        self._layer_widget   = self._build_layer_section()
        self._opacity_widget = self._build_opacity_section()
        self._shadow_widget = self._build_shadow_section()
        self._lock_widget = self._build_lock_section()
        root.addWidget(self._link_widget)
        root.addWidget(self._layer_widget)
        root.addWidget(self._opacity_widget)
        root.addWidget(self._shadow_widget)
        root.addWidget(self._lock_widget)
        self._link_widget.setVisible(False)
        self._layer_widget.setVisible(False)
        self._opacity_widget.setVisible(False)
        self._shadow_widget.setVisible(False)
        self._lock_widget.setVisible(False)

        root.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self._show_empty()

    # ------------------------------------------------------------------
    # Small UI helpers
    # ------------------------------------------------------------------

    def _muted(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("muted")
        return lbl

    def _add_color_btn(self, layout, label_text: str, slot) -> QPushButton:
        layout.addWidget(self._muted(label_text))
        btn = QPushButton("[ CHANGE ]")
        btn.setObjectName("btn_color")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        layout.addWidget(btn)
        layout.addWidget(_h_rule())
        return btn

    def _add_slider_row(self, layout, label_text: str, lo: int, hi: int,
                        default: int, slot, fmt=str, tick: int = 0):
        row = QHBoxLayout()
        row.addWidget(self._muted(label_text))
        row.addStretch()
        val_lbl = QLabel(fmt(default))
        val_lbl.setObjectName("muted")
        row.addWidget(val_lbl)
        layout.addLayout(row)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(lo, hi)
        slider.setValue(default)
        if tick:
            slider.setTickInterval(tick)
        slider.valueChanged.connect(slot)
        layout.addWidget(slider)
        layout.addWidget(_h_rule())
        return slider, val_lbl

    def _add_info_block(self, layout, header_text: str) -> QLabel:
        layout.addWidget(self._muted(header_text))
        val = QLabel("--")
        val.setObjectName("muted")
        val.setWordWrap(True)
        layout.addWidget(val)
        return val

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _build_empty_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)
        lbl = QLabel("> SELECT A BLOCK")
        lbl.setObjectName("muted")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        layout.addStretch()
        return page

    def _build_rect_controls_page(self) -> QWidget:
        """Shared by StyledRectItem, StyledEllipseItem, and ButtonComponentItem."""
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(12)

        # ── Fill ─────────────────────────────────────────────────────
        self.btn_rect_color = self._add_color_btn(
            layout, "> FILL COLOR", self._on_rect_color_click
        )

        # ── Corner radius — shown for rects/buttons; hidden for ellipses ──
        self._radius_container = QWidget()
        rc_layout = QVBoxLayout(self._radius_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(0)
        self.slider_radius, self.lbl_radius_val = self._add_slider_row(
            rc_layout, "> CORNER RAD", 0, 60, 0, self._on_radius_change,
            fmt=lambda v: f"{v}px",
        )
        layout.addWidget(self._radius_container)

        self._lbl_radius_na = self._muted("> CORNER RAD: N/A (ELLIPSE)")
        layout.addWidget(self._lbl_radius_na)
        self._lbl_radius_na.setVisible(False)

        # ── Border ───────────────────────────────────────────────────
        layout.addWidget(self._muted("> BORDER"))
        layout.addWidget(_h_rule())
        self.btn_border_color = self._add_color_btn(
            layout, "> BORDER COLOR", self._on_border_color_click
        )
        self.slider_border_width, self.lbl_border_width_val = self._add_slider_row(
            layout, "> BORDER WIDTH", 0, 20, 2, self._on_border_width_change,
            fmt=lambda v: f"{v}px",
        )

        # ── Geometry readout ─────────────────────────────────────────
        self.lbl_rect_geometry = self._add_info_block(layout, "> GEOMETRY")
        layout.addStretch()
        return page

    def _build_text_controls_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(12)
        self.btn_text_color = self._add_color_btn(
            layout, "> TEXT COLOR", self._on_text_color_click
        )
        self.slider_size, self.lbl_size_val = self._add_slider_row(
            layout, "> FONT SIZE", 6, 96, 14, self._on_size_change,
            fmt=lambda v: f"{v}pt", tick=6,
        )
        self.slider_thick, self.lbl_thick_val = self._add_slider_row(
            layout, "> THICKNESS", 1, 9, 7, self._on_thick_change,
            fmt=lambda v: str(DraggableTextItem.WEIGHT_CSS.get(v, v * 100)),
        )
        self.lbl_text_geometry = self._add_info_block(layout, "> POSITION")
        layout.addStretch()
        return page

    def _build_image_controls_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._muted("> IMAGE ASSET"))
        layout.addWidget(_h_rule())
        self.lbl_img_path     = self._add_info_block(layout, "> FILE PATH")
        layout.addWidget(_h_rule())
        self.lbl_img_geometry = self._add_info_block(layout, "> GEOMETRY")
        layout.addStretch()
        return page

    def _build_alignment_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(self._muted("> ALIGNMENT"))
        layout.addWidget(_h_rule())

        self._lbl_multi_count = self._muted("> 0 BLOCKS SELECTED")
        layout.addWidget(self._lbl_multi_count)
        layout.addSpacing(4)

        self.btn_align_left     = QPushButton("[ |← ] LEFT")
        self.btn_align_right    = QPushButton("[ →| ] RIGHT")
        self.btn_align_top      = QPushButton("[ ↑ ] TOP")
        self.btn_align_bottom   = QPushButton("[ ↓ ] BOTTOM")
        self.btn_align_center_h = QPushButton("[ ↔ ] CENTER H")

        for btn in (self.btn_align_left, self.btn_align_right,
                    self.btn_align_top,  self.btn_align_bottom,
                    self.btn_align_center_h):
            btn.setObjectName("btn_align")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        row1 = QHBoxLayout()
        row1.setSpacing(4)
        row1.addWidget(self.btn_align_left)
        row1.addWidget(self.btn_align_right)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.addWidget(self.btn_align_top)
        row2.addWidget(self.btn_align_bottom)
        layout.addLayout(row2)

        layout.addWidget(self.btn_align_center_h)

        self.btn_align_left    .clicked.connect(self._on_align_left)
        self.btn_align_right   .clicked.connect(self._on_align_right)
        self.btn_align_top     .clicked.connect(self._on_align_top)
        self.btn_align_bottom  .clicked.connect(self._on_align_bottom)
        self.btn_align_center_h.clicked.connect(self._on_align_center_h)

        layout.addStretch()
        return page

    # ------------------------------------------------------------------
    # Hyperlink section
    # ------------------------------------------------------------------
    # ── Inside PropertyInspector ──────────────────────────────────────────────

    def _build_link_section(self) -> QWidget:
        w      = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(_h_rule())
        layout.addWidget(self._muted("> HYPERLINK URL"))

        self.txt_link_url = QLineEdit()
        self.txt_link_url.setPlaceholderText("https://...")
        self.txt_link_url.setClearButtonEnabled(True)
        self.txt_link_url.textChanged.connect(self._on_link_url_changed)
        layout.addWidget(self.txt_link_url)
        return w

    # ------------------------------------------------------------------
    # Layer-order section
    # ------------------------------------------------------------------

    def _build_layer_section(self) -> QWidget:
        w      = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(_h_rule())

        hdr = QHBoxLayout()
        hdr.addWidget(self._muted("> LAYER ORDER"))
        hdr.addStretch()
        self.lbl_layer_val = self._muted("Z: 0")
        hdr.addWidget(self.lbl_layer_val)
        layout.addLayout(hdr)

        self.btn_bring_front = QPushButton("[▲] FRONT")
        self.btn_forward     = QPushButton("[↑] FORWARD")
        self.btn_backward    = QPushButton("[↓] BACKWARD")
        self.btn_send_back   = QPushButton("[▼] BACK")

        for btn in (self.btn_bring_front, self.btn_forward,
                    self.btn_backward,    self.btn_send_back):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        row1 = QHBoxLayout()
        row1.setSpacing(4)
        row1.addWidget(self.btn_bring_front)
        row1.addWidget(self.btn_forward)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.addWidget(self.btn_backward)
        row2.addWidget(self.btn_send_back)
        layout.addLayout(row2)

        self.btn_bring_front.clicked.connect(self._on_bring_front)
        self.btn_forward    .clicked.connect(self._on_forward)
        self.btn_backward   .clicked.connect(self._on_backward)
        self.btn_send_back  .clicked.connect(self._on_send_back)
        return w

    def _build_opacity_section(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(_h_rule())
        self.slider_opacity, self.lbl_opacity_val = self._add_slider_row(
            layout, "> OPACITY", 0, 100, 100,
            self._on_opacity_change, fmt=lambda v: f"{v}%"
        )
        return w

    def _build_shadow_section(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(_h_rule())

        hdr = QHBoxLayout()
        self._btn_shadow_collapse = QPushButton("▼ SHADOW")
        self._btn_shadow_collapse.setCheckable(True)
        self._btn_shadow_collapse.setChecked(True)
        self._btn_shadow_collapse.setCursor(Qt.CursorShape.PointingHandCursor)

        def _collapse_shadow_body(on: bool):
            self._shadow_panel.setVisible(on)
            self._btn_shadow_collapse.setText("▼ SHADOW" if on else "▶ SHADOW")

        self._btn_shadow_collapse.toggled.connect(_collapse_shadow_body)
        hdr.addWidget(self._btn_shadow_collapse)
        hdr.addStretch()
        layout.addLayout(hdr)

        self._shadow_panel = QWidget()
        inner = QVBoxLayout(self._shadow_panel)
        inner.setContentsMargins(8, 0, 0, 0)
        inner.setSpacing(6)

        self.chk_shadow = QCheckBox("Enable shadow")
        self.chk_shadow.stateChanged.connect(self._on_shadow_toggle)
        inner.addWidget(self.chk_shadow)

        self.slider_shadow_x, self.lbl_shadow_x_val = self._add_slider_row(
            inner, "> OFFSET X", -50, 50, 5,
            self._on_shadow_x_change, fmt=lambda v: f"{v}px",
        )
        self.slider_shadow_y, self.lbl_shadow_y_val = self._add_slider_row(
            inner, "> OFFSET Y", -50, 50, 5,
            self._on_shadow_y_change, fmt=lambda v: f"{v}px",
        )
        self.slider_shadow_blur, self.lbl_shadow_blur_val = self._add_slider_row(
            inner, "> BLUR", 0, 64, 10,
            self._on_shadow_blur_change, fmt=lambda v: f"{v}px",
        )

        self.btn_shadow_color = self._add_color_btn(
            inner, "> SHADOW COLOR", self._on_shadow_color_click
        )

        layout.addWidget(self._shadow_panel)
        return w

    def _build_lock_section(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(_h_rule())
        self.chk_lock = QCheckBox("LOCK POSITION")
        self.chk_lock.stateChanged.connect(self._on_lock_toggle)
        layout.addWidget(self.chk_lock)
        return w

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_item(self, item, scene=None):
        self._current_item = item
        self._scene        = scene

        if isinstance(item, (StyledRectItem, StyledEllipseItem, ButtonComponentItem)):
            self._refresh_rect_controls()
            self._stack.setCurrentIndex(1)
        elif isinstance(item, DraggableTextItem):
            self._refresh_text_controls()
            self._stack.setCurrentIndex(2)
        elif isinstance(item, DraggableImageItem):
            self._refresh_image_controls()
            self._stack.setCurrentIndex(3)

        # ── Hyperlink — shown for ALL item types ──────────────────────────
        self.txt_link_url.blockSignals(True)
        self.txt_link_url.setText(item.link_url())
        self.txt_link_url.blockSignals(False)
        self._link_widget.setVisible(True)      # always visible

        self._update_layer_label()
        self._layer_widget.setVisible(True)

        self.slider_opacity.blockSignals(True)
        self.slider_opacity.setValue(round(item.opacity() * 100))
        self.lbl_opacity_val.setText(f"{self.slider_opacity.value()}%")
        self.slider_opacity.blockSignals(False)
        self._opacity_widget.setVisible(True)

        sd = item._shadow_data
        self.chk_shadow.blockSignals(True)
        self.chk_shadow.setChecked(sd["enabled"])
        self.chk_shadow.blockSignals(False)

        self.slider_shadow_x.blockSignals(True)
        self.slider_shadow_x.setValue(int(sd["x"]))
        self.lbl_shadow_x_val.setText(f"{int(sd['x'])}px")
        self.slider_shadow_x.blockSignals(False)

        self.slider_shadow_y.blockSignals(True)
        self.slider_shadow_y.setValue(int(sd["y"]))
        self.lbl_shadow_y_val.setText(f"{int(sd['y'])}px")
        self.slider_shadow_y.blockSignals(False)

        self.slider_shadow_blur.blockSignals(True)
        self.slider_shadow_blur.setValue(int(sd["blur"]))
        self.lbl_shadow_blur_val.setText(f"{int(sd['blur'])}px")
        self.slider_shadow_blur.blockSignals(False)

        self._apply_swatch(self.btn_shadow_color, QColor(sd["color"]))
        self._shadow_widget.setVisible(True)

        self.chk_lock.blockSignals(True)
        self.chk_lock.setChecked(item.locked())
        self.chk_lock.blockSignals(False)
        self._lock_widget.setVisible(True)

    def load_multi_select(self, items: list, scene=None):
        self._current_item  = None
        self._current_items = list(items)
        self._scene         = scene
        self._lbl_multi_count.setText(f"> {len(items)} BLOCKS SELECTED")
        self._stack.setCurrentIndex(4)
        self._link_widget.setVisible(False)
        self._layer_widget.setVisible(False)
        self._opacity_widget.setVisible(False)
        self._shadow_widget.setVisible(False)
        self._lock_widget.setVisible(False)

    def clear(self):
        self._current_item  = None
        self._current_items = []
        self._scene         = None
        self._link_widget.setVisible(False)
        self._layer_widget.setVisible(False)
        self._opacity_widget.setVisible(False)
        self._shadow_widget.setVisible(False)
        self._lock_widget.setVisible(False)
        self._show_empty()

    # ------------------------------------------------------------------
    # Private refresh helpers
    # ------------------------------------------------------------------

    def _show_empty(self):
        self._stack.setCurrentIndex(0)

    def _update_layer_label(self):
        if self._current_item:
            self.lbl_layer_val.setText(f"Z: {int(self._current_item.zValue())}")

    def _refresh_rect_controls(self):
        item = self._current_item

        is_ellipse = isinstance(item, StyledEllipseItem)
        self._radius_container.setVisible(not is_ellipse)
        self._lbl_radius_na.setVisible(is_ellipse)
        if not is_ellipse:
            self.slider_radius.blockSignals(True)
            self.slider_radius.setValue(int(item.border_radius()))
            self.lbl_radius_val.setText(f"{int(item.border_radius())}px")
            self.slider_radius.blockSignals(False)

        self._apply_swatch(self.btn_rect_color, item.fill_color())

        self._apply_swatch(self.btn_border_color, item.border_color())
        self.slider_border_width.blockSignals(True)
        self.slider_border_width.setValue(int(item.border_width()))
        self.lbl_border_width_val.setText(f"{int(item.border_width())}px")
        self.slider_border_width.blockSignals(False)

        pos  = item.pos()
        rect = item.rect()
        self.lbl_rect_geometry.setText(
            f"X:{pos.x():.0f} Y:{pos.y():.0f}  W:{rect.width():.0f} H:{rect.height():.0f}"
        )

    def _refresh_text_controls(self):
        item = self._current_item
        self._apply_swatch(self.btn_text_color, item.text_color())
        self.slider_size.blockSignals(True)
        self.slider_size.setValue(item.font_size())
        self.lbl_size_val.setText(f"{item.font_size()}pt")
        self.slider_size.blockSignals(False)
        self.slider_thick.blockSignals(True)
        self.slider_thick.setValue(item.thickness())
        self.lbl_thick_val.setText(str(item.thickness_css()))
        self.slider_thick.blockSignals(False)
        pos = item.pos()
        self.lbl_text_geometry.setText(f"X:{pos.x():.0f} Y:{pos.y():.0f}")

    def _refresh_image_controls(self):
        item      = self._current_item
        full_path = item.file_path()
        display   = full_path if len(full_path) <= 42 else f"...{full_path[-40:]}"
        self.lbl_img_path.setText(display)
        self.lbl_img_path.setToolTip(full_path)
        pos = item.pos()
        self.lbl_img_geometry.setText(
            f"X:{pos.x():.0f} Y:{pos.y():.0f}  "
            f"W:{item.img_width():.0f} H:{item.img_height():.0f}"
        )

    def _apply_swatch(self, btn: QPushButton, color: QColor):
        luminance = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
        text_col  = "#00E5FF" if luminance < 140 else "#000000"
        btn.setStyleSheet(
            f"QPushButton#btn_color {{"
            f"  background-color: {color.name()}; color: {text_col};"
            f"  border-top: 2px solid #6a6a6a; border-left: 2px solid #6a6a6a;"
            f"  border-bottom: 2px solid #1a1a1a; border-right: 2px solid #1a1a1a;"
            f"  border-radius: 0px;"
            f"}}"
        )
        btn.setText(color.name().upper())

    # ------------------------------------------------------------------
    # Slot handlers
    # ------------------------------------------------------------------

    def _on_rect_color_click(self):
        if not self._current_item:
            return
        color = QColorDialog.getColor(
            self._current_item.fill_color(), self, "CHOOSE FILL COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_item.set_fill_color(color)
            self._apply_swatch(self.btn_rect_color, color)

    def _on_border_color_click(self):
        if not self._current_item:
            return
        color = QColorDialog.getColor(
            self._current_item.border_color(), self, "CHOOSE BORDER COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_item.set_border_color(color)
            self._apply_swatch(self.btn_border_color, color)

    def _on_text_color_click(self):
        if not self._current_item:
            return
        color = QColorDialog.getColor(
            self._current_item.text_color(), self, "CHOOSE TEXT COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_item.set_text_color(color)
            self._apply_swatch(self.btn_text_color, color)

    def _on_radius_change(self, value: int):
        self.lbl_radius_val.setText(f"{value}px")
        if self._current_item:
            self._current_item.set_border_radius(value)

    def _on_border_width_change(self, value: int):
        self.lbl_border_width_val.setText(f"{value}px")
        if self._current_item:
            self._current_item.set_border_width(value)

    def _on_size_change(self, value: int):
        self.lbl_size_val.setText(f"{value}pt")
        if self._current_item:
            self._current_item.set_font_size(value)

    def _on_thick_change(self, value: int):
        self.lbl_thick_val.setText(str(DraggableTextItem.WEIGHT_CSS.get(value, value * 100)))
        if self._current_item:
            self._current_item.set_thickness(value)

    def _on_link_url_changed(self, text: str):
        if self._current_item:
            self._current_item.set_link_url(text)

    def _on_opacity_change(self, value: int):
        self.lbl_opacity_val.setText(f"{value}%")
        if self._current_item:
            self._current_item.set_opacity(value / 100.0)

    def _on_lock_toggle(self, state: int):
        if self._current_item:
            self._current_item.set_locked(
                Qt.CheckState(state) == Qt.CheckState.Checked
            )

    # ------------------------------------------------------------------
    # Alignment slot handlers
    # ------------------------------------------------------------------

    @staticmethod
    def _item_size(item) -> tuple:
        br = item.boundingRect()
        return br.width(), br.height()

    def _emit_status(self, msg: str):
        if callable(self.status_callback):
            self.status_callback(msg)

    def _on_align_left(self):
        items = self._current_items
        if len(items) < 2:
            return
        target = _snap(min(it.x() for it in items))
        for it in items:
            it.setX(target)
        self._emit_status("LAYOUT SYNCHRONIZED — LEFT EDGE LOCKED.")

    def _on_align_right(self):
        items = self._current_items
        if len(items) < 2:
            return
        target = _snap(max(it.x() + self._item_size(it)[0] for it in items))
        for it in items:
            it.setX(_snap(target - self._item_size(it)[0]))
        self._emit_status("BLOCKS ALIGNED TO GRID — RIGHT EDGE FLUSH.")

    def _on_align_top(self):
        items = self._current_items
        if len(items) < 2:
            return
        target = _snap(min(it.y() for it in items))
        for it in items:
            it.setY(target)
        self._emit_status("TOP RAIL ESTABLISHED. GRID INTEGRITY CONFIRMED.")

    def _on_align_bottom(self):
        items = self._current_items
        if len(items) < 2:
            return
        target = _snap(max(it.y() + self._item_size(it)[1] for it in items))
        for it in items:
            it.setY(_snap(target - self._item_size(it)[1]))
        self._emit_status("BLOCKS ALIGNED TO GRID — BOTTOM BASELINE SET.")

    def _on_align_center_h(self):
        items = self._current_items
        if len(items) < 2:
            return
        min_x  = min(it.x() for it in items)
        max_x  = max(it.x() + self._item_size(it)[0] for it in items)
        center = (min_x + max_x) / 2.0
        for it in items:
            it.setX(_snap(center - self._item_size(it)[0] / 2.0))
        self._emit_status("HORIZONTAL CENTER MASS COMPUTED. BLOCKS REALIGNED.")

    # ------------------------------------------------------------------
    # Layer-order slot handlers
    # ------------------------------------------------------------------

    def _on_bring_front(self):
        if not self._current_item:
            return
        peers = [it for it in (self._scene.items() if self._scene else [])
                 if it is not self._current_item]
        self._current_item.setZValue(max((it.zValue() for it in peers), default=0) + 1)
        self._update_layer_label()

    def _on_send_back(self):
        if not self._current_item:
            return
        peers = [it for it in (self._scene.items() if self._scene else [])
                 if it is not self._current_item]
        self._current_item.setZValue(min((it.zValue() for it in peers), default=0) - 1)
        self._update_layer_label()

    def _on_forward(self):
        if not self._current_item:
            return
        self._current_item.setZValue(self._current_item.zValue() + 1)
        self._update_layer_label()

    def _on_backward(self):
        if not self._current_item:
            return
        self._current_item.setZValue(self._current_item.zValue() - 1)
        self._update_layer_label()

    # ------------------------------------------------------------------
    # Shadow slot handlers
    # ------------------------------------------------------------------

    def _on_shadow_toggle(self, state: int):
        if not self._current_item:
            return
        self._current_item._shadow_data["enabled"] = (
            Qt.CheckState(state) == Qt.CheckState.Checked
        )
        self._current_item.apply_shadow()

    def _on_shadow_x_change(self, value: int):
        self.lbl_shadow_x_val.setText(f"{value}px")
        if self._current_item:
            self._current_item._shadow_data["x"] = value
            self._current_item.apply_shadow()

    def _on_shadow_y_change(self, value: int):
        self.lbl_shadow_y_val.setText(f"{value}px")
        if self._current_item:
            self._current_item._shadow_data["y"] = value
            self._current_item.apply_shadow()

    def _on_shadow_blur_change(self, value: int):
        self.lbl_shadow_blur_val.setText(f"{value}px")
        if self._current_item:
            self._current_item._shadow_data["blur"] = value
            self._current_item.apply_shadow()

    def _on_shadow_color_click(self):
        if not self._current_item:
            return
        c = QColor(self._current_item._shadow_data["color"])
        if not c.isValid():
            c = QColor("#66000000")
        color = QColorDialog.getColor(
            c, self, "SHADOW COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_item._shadow_data["color"] = color.name(
                QColor.NameFormat.HexArgb
            )
            self._apply_swatch(self.btn_shadow_color, color)
            self._current_item.apply_shadow()