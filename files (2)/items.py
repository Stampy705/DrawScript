"""
DrawScript — items.py  (v1.6)
Canvas item classes: CanvasItemMixin, StyledRectItem, StyledEllipseItem,
DraggableTextItem, DraggableImageItem, and ButtonComponentItem.

Changes (v1.6):
  - StyledRectItem: itemChange() added for position grid-snapping (was missing).
  - StyledRectItem / StyledEllipseItem: mouseMoveEvent guards _resize_start_rect
    against None so a stale pointer never causes a jump or AttributeError.
  - ButtonComponentItem: label is now a live child _ButtonLabelItem that the user
    can double-click to edit inline.  Text stays centred after resize.
  - ButtonComponentItem: paint() no longer draws the text itself; the child item
    handles all rendering so selection/resize handles never obscure the text.
"""

from PyQt6.QtWidgets import (
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsDropShadowEffect, QStyle,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath,
    QTextCursor, QTextCharFormat, QPixmap, QPainterPathStroker
)

from styles import GRID_STEP

def _snap(v: float) -> float:
    return round(v / GRID_STEP) * GRID_STEP


# ---------------------------------------------------------------------------
# CanvasItemMixin
# ---------------------------------------------------------------------------

class CanvasItemMixin:
    HANDLE_SIZE = 12
    ACCENT      = QColor("#00E5FF")
    HANDLE_CLR  = QColor("#FFD166")

    def _snap(self, v: float) -> float:
        return _snap(v)

    def _paint_handle(self, painter, is_selected: bool):
        if not is_selected:
            return
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(self._handle_rect(), self.HANDLE_CLR)

    def set_link_url(self, url: str):
        self._link_url = str(url).strip()

    def link_url(self) -> str:
        return self._link_url

    def set_opacity(self, val: float):
        """Clamps val to [0.0, 1.0], stores it, and pushes it to Qt."""
        self._opacity = max(0.0, min(1.0, float(val)))
        self.setOpacity(self._opacity)

    def opacity(self) -> float:
        return self._opacity

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton
                and self._handle_rect().contains(event.pos())):
            self._resizing = True
            self._resize_start_pos = event.scenePos()
            self._capture_resize_origin()
            event.accept()
        else:
            self._resizing = False
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)

    def _init_shadow_data(self):
        self._shadow_data = {
            "enabled": False, "x": 5, "y": 5, "blur": 10, "color": "#66000000"
        }
        self._locked = False

    def apply_shadow(self):
        if self._shadow_data["enabled"]:
            effect = QGraphicsDropShadowEffect()
            effect.setOffset(float(self._shadow_data["x"]), float(self._shadow_data["y"]))
            effect.setBlurRadius(float(self._shadow_data["blur"]))
            effect.setColor(QColor(self._shadow_data["color"]))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    def set_locked(self, locked: bool):
        self._locked = bool(locked)

    def locked(self) -> bool:
        return self._locked


# ---------------------------------------------------------------------------
# StyledRectItem
# ---------------------------------------------------------------------------

class StyledRectItem(CanvasItemMixin, QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float = 180, h: float = 90):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._fill_color    = QColor("#1E2A3A")
        self._border_color  = QColor("#000000")
        self._border_width  = 2
        self._border_radius = 0.0
        self._link_url      = ""
        self._opacity = 1.0
        self._init_shadow_data()
        self._resizing           = False
        self._resize_start_pos   = None
        self._resize_start_rect  = None

    def set_fill_color(self, c):    self._fill_color = QColor(c);          self.update()
    def fill_color(self):           return QColor(self._fill_color)
    def set_border_radius(self, r): self._border_radius = float(r);        self.update()
    def border_radius(self):        return self._border_radius
    def set_border_color(self, c):  self._border_color = QColor(c);        self.update()
    def border_color(self):         return QColor(self._border_color)
    def set_border_width(self, w):  self._border_width = max(0, int(w));   self.update()
    def border_width(self):         return self._border_width

    def _handle_rect(self):
        return QRectF(
            self.rect().right()  - self.HANDLE_SIZE,
            self.rect().bottom() - self.HANDLE_SIZE,
            self.HANDLE_SIZE, self.HANDLE_SIZE,
        )
    def _capture_resize_origin(self):
        self._resize_start_rect = QRectF(self.rect())

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        is_sel = bool(option.state & QStyle.StateFlag.State_Selected)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), self._border_radius, self._border_radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, self._fill_color)

        if self._border_width > 0:
            p = QPen(self._border_color, float(self._border_width))
            p.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(p)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        if is_sel:
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        self._paint_handle(painter, is_sel)

    def mouseMoveEvent(self, event):
        if self._resizing:
            # Guard: initialise origin if somehow None (prevents jump on first drag)
            if self._resize_start_rect is None:
                self._resize_start_rect = QRectF(self.rect())
            delta = event.scenePos() - self._resize_start_pos
            new_w = max(50, self._snap(self._resize_start_rect.width()  + delta.x()))
            new_h = max(24, self._snap(self._resize_start_rect.height() + delta.y()))
            self.setRect(0, 0, new_w, new_h)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    # FIX v1.6: grid-snap position on drag (was missing in v1.5)
    def itemChange(self, c, v):
        if c == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()  # This "throws away" the drag movement
            return QPointF(_snap(v.x()), _snap(v.y()))
        return super().itemChange(c, v)


# ---------------------------------------------------------------------------
# StyledEllipseItem
# ---------------------------------------------------------------------------

class StyledEllipseItem(CanvasItemMixin, QGraphicsEllipseItem):
    """
    Free-form oval/circle — width and height resize independently.

    v1.5: QPainterPath fill, independent W/H resize, position snap, inset selection.
    v1.6: mouseMoveEvent guards _resize_start_rect against None.
    """

    def __init__(self, x: float, y: float, w: float = 144, h: float = 144):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setFlags(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._fill_color   = QColor("#1E2A3A")
        self._border_color = QColor("#000000")
        self._border_width = 2
        self._link_url     = ""
        self._opacity = 1.0
        self._init_shadow_data()
        self._resizing           = False
        self._resize_start_pos   = None
        self._resize_start_rect  = None

    def shape(self):
        """
        FIX v1.6: Returns a rectangular path so the corners/handles
        are clickable, preventing deselection during resize.
        """
        path = QPainterPath()
        path.addRect(self.rect())
        return path

    def set_fill_color(self, c):    self._fill_color = QColor(c);           self.update()
    def fill_color(self):           return QColor(self._fill_color)
    def set_border_radius(self, r): pass                                     # no-op for ellipse
    def border_radius(self):        return 0.0
    def set_border_color(self, c):  self._border_color = QColor(c);         self.update()
    def border_color(self):         return QColor(self._border_color)
    def set_border_width(self, w):  self._border_width = max(0, int(w));    self.update()
    def border_width(self):         return self._border_width

    def _handle_rect(self):
        return QRectF(
            self.rect().right()  - self.HANDLE_SIZE,
            self.rect().bottom() - self.HANDLE_SIZE,
            self.HANDLE_SIZE, self.HANDLE_SIZE,
        )
    def _capture_resize_origin(self):
        self._resize_start_rect = QRectF(self.rect())

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        is_sel = bool(option.state & QStyle.StateFlag.State_Selected)

        path = QPainterPath()
        path.addEllipse(self.rect())           # uses current W×H — supports ovals

        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, self._fill_color)

        if self._border_width > 0:
            painter.setPen(QPen(self._border_color, float(self._border_width)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.rect())   # border follows the oval

        if is_sel:
            inset = 2.0
            sel_rect = self.rect().adjusted(inset, inset, -inset, -inset)
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(sel_rect)      # dashed cyan follows the oval shape

        self._paint_handle(painter, is_sel)

    def mouseMoveEvent(self, event):
        """FIX: Allows independent Width/Height scaling (ovals) with grid snapping."""
        if self._resizing:
            if self._resize_start_rect is None:
                self._resize_start_rect = QRectF(self.rect())
            delta = event.scenePos() - self._resize_start_pos
            # Independent scaling for true sandbox freedom
            new_w = max(GRID_STEP, _snap(self._resize_start_rect.width()  + delta.x()))
            new_h = max(GRID_STEP, _snap(self._resize_start_rect.height() + delta.y()))
            self.setRect(0, 0, new_w, new_h)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def itemChange(self, c, v):
        if c == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()  # This "throws away" the drag movement
            return QPointF(_snap(v.x()), _snap(v.y()))
        return super().itemChange(c, v)


# ---------------------------------------------------------------------------
# DraggableTextItem
# ---------------------------------------------------------------------------

class DraggableTextItem(CanvasItemMixin, QGraphicsTextItem):
    WEIGHT_CSS = {1: 100, 2: 200, 3: 300, 4: 400, 5: 500, 6: 600, 7: 700, 8: 800, 9: 900}
    _WEIGHT_QFONT = {
        1: QFont.Weight.Thin,       2: QFont.Weight.ExtraLight,
        3: QFont.Weight.Light,      4: QFont.Weight.Normal,
        5: QFont.Weight.Medium,     6: QFont.Weight.DemiBold,
        7: QFont.Weight.Bold,       8: QFont.Weight.ExtraBold,
        9: QFont.Weight.Black,
    }

    def __init__(self, text, x, y):
        super().__init__(text)
        self.setPos(x, y)
        self._text_color = QColor("#0A0E17")
        self._font_size  = 14
        self._weight_val = 7
        self._link_url   = ""
        self._opacity = 1.0
        self._init_shadow_data()
        self._resizing = False
        self.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsTextItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()

    def _apply_formatting(self):
        f = QFont("Courier New", self._font_size)
        f.setWeight(self._WEIGHT_QFONT.get(self._weight_val, QFont.Weight.Bold))
        self.setFont(f)
        self.setDefaultTextColor(self._text_color)
        cur = self.textCursor()
        cur.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setForeground(QBrush(self._text_color))
        fmt.setFont(f)
        cur.setCharFormat(fmt)
        self.setTextCursor(cur)
        self.update()

    def set_text_color(self, c): self._text_color = QColor(c); self._apply_formatting()
    def text_color(self):        return QColor(self._text_color)
    def set_font_size(self, s):  self._font_size = max(6, min(s, 96)); self._apply_formatting()
    def font_size(self):         return self._font_size
    def set_thickness(self, w):  self._weight_val = max(1, min(w, 9)); self._apply_formatting()
    def thickness(self):         return self._weight_val
    def thickness_css(self):     return self.WEIGHT_CSS.get(self._weight_val, 700)
    def set_link_url(self, url: str):
        self._link_url = str(url).strip()

    def link_url(self) -> str:
        return self._link_url

    def _handle_rect(self):
        return QRectF()  # Text has no resize handle, so we return empty space.

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()
        super().focusOutEvent(event)

    def itemChange(self, c, v):
        if c == QGraphicsTextItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()  # This "throws away" the drag movement
            return QPointF(_snap(v.x()), _snap(v.y()))
        return super().itemChange(c, v)


# ---------------------------------------------------------------------------
# DraggableImageItem
# ---------------------------------------------------------------------------

class DraggableImageItem(CanvasItemMixin, QGraphicsPixmapItem):
    def __init__(self, path, x, y, w=192, h=144):
        super().__init__()
        self._file_path  = path
        self._img_w      = float(w)
        self._img_h      = float(h)
        self._link_url   = ""
        self._opacity = 1.0
        self._init_shadow_data()
        self._source_pixmap = QPixmap(path)
        if self._source_pixmap.isNull():
            self._source_pixmap = QPixmap(int(w), int(h))
            self._source_pixmap.fill(QColor("#2A3A4A"))
        self._apply_scaled_pixmap()
        self.setPos(x, y)
        self.setFlags(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._resizing          = False
        self._resize_start_pos  = None
        self._resize_start_size = (w, h)

    def file_path(self):   return self._file_path
    def img_width(self):   return self._img_w
    def img_height(self):  return self._img_h

    def set_link_url(self, url: str):
        self._link_url = str(url).strip()

    def link_url(self) -> str:
        return self._link_url

    def _apply_scaled_pixmap(self):
        self.setPixmap(self._source_pixmap.scaled(
            int(self._img_w), int(self._img_h),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _handle_rect(self):
        return QRectF(
            self._img_w - self.HANDLE_SIZE,
            self._img_h - self.HANDLE_SIZE,
            self.HANDLE_SIZE, self.HANDLE_SIZE,
        )
    def _capture_resize_origin(self):
        self._resize_start_size = (self._img_w, self._img_h)

    def boundingRect(self):
        return QRectF(0, 0, self._img_w, self._img_h)

    def itemChange(self, c, v):
        if c == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()  # This "throws away" the drag movement
            return QPointF(_snap(v.x()), _snap(v.y()))
        return super().itemChange(c, v)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(0, 0, int(self._img_w), int(self._img_h), self.pixmap())
        if bool(option.state & QStyle.StateFlag.State_Selected):
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, self._img_w, self._img_h))
        self._paint_handle(painter, bool(option.state & QStyle.StateFlag.State_Selected))

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.scenePos() - self._resize_start_pos
            self._img_w = max(GRID_STEP, self._snap(self._resize_start_size[0] + delta.x()))
            self._img_h = max(GRID_STEP, self._snap(self._resize_start_size[1] + delta.y()))
            self.prepareGeometryChange()
            self._apply_scaled_pixmap()
            event.accept()
        else:
            super().mouseMoveEvent(event)


# ---------------------------------------------------------------------------
# _ButtonLabelItem  (internal helper — not exported)
# ---------------------------------------------------------------------------

class _ButtonLabelItem(QGraphicsTextItem):
    """
    Inline-editable label child of ButtonComponentItem.
    Cannot be independently selected or moved.
    Double-click on the parent button activates TextEditorInteraction here.
    """

    def __init__(self, text: str, parent: QGraphicsItem):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable,    False)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, False)

    def focusOutEvent(self, event):
        """Commit the edit and disable interaction when the item loses focus."""
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cur = self.textCursor()
        cur.clearSelection()
        self.setTextCursor(cur)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Escape or Enter commits the edit."""
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return):
            self.clearFocus()
            return
        super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# ButtonComponentItem  (v1.6 — inline-editable label via child text item)
# ---------------------------------------------------------------------------

class ButtonComponentItem(CanvasItemMixin, QGraphicsRectItem):
    """
    Pre-styled Button component: rounded rect + inline-editable centred label.

    The label is a _ButtonLabelItem child.  Double-clicking the button body
    activates text-editor interaction on the child so the user can type
    directly.  The label re-centres automatically after every resize.

    Property interface is a superset of StyledRectItem so the PropertyInspector
    rect-controls page works without modification.  Extra accessors:
        label() / set_label(str)
        label_color() / set_label_color(QColor)
        label_font_size() / set_label_font_size(int)
    """

    def __init__(
        self,
        x: float, y: float,
        w: float = 160, h: float = 48,
        label: str = "CLICK ME",
    ):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        # Background / border
        self._fill_color    = QColor("#FFD166")
        self._border_color  = QColor("#000000")
        self._border_width  = 3
        self._border_radius = 8.0
        # Label state
        self._label       = str(label)
        self._label_color = QColor("#000000")
        self._font_size   = 13
        # Common
        self._link_url          = ""
        self._opacity = 1.0
        self._init_shadow_data()
        self._resizing          = False
        self._resize_start_pos  = None
        self._resize_start_rect = None

        # Inline-editable child label
        self._label_item = _ButtonLabelItem(self._label, self)
        # Keep _label in sync as the user types
        self._label_item.document().contentsChanged.connect(self._sync_label_from_child)
        self._apply_label_style()
        self._center_text()

    # ── Shape / border accessors (StyledRectItem-compatible) ──────────
    def set_fill_color(self, c):    self._fill_color = QColor(c);          self.update()
    def fill_color(self):           return QColor(self._fill_color)
    def set_border_radius(self, r): self._border_radius = float(r);        self.update()
    def border_radius(self):        return self._border_radius
    def set_border_color(self, c):  self._border_color = QColor(c);        self.update()
    def border_color(self):         return QColor(self._border_color)
    def set_border_width(self, w):  self._border_width = max(0, int(w));   self.update()
    def border_width(self):         return self._border_width

    # ── Label accessors ───────────────────────────────────────────────
    def label(self) -> str:
        return self._label

    def set_label(self, text: str):
        self._label = str(text)
        # Block signal to avoid recursion through _sync_label_from_child
        self._label_item.document().blockSignals(True)
        self._label_item.setPlainText(self._label)
        self._label_item.document().blockSignals(False)
        self._apply_label_style()
        self._center_text()
        self.update()

    def label_color(self) -> QColor:
        return QColor(self._label_color)

    def set_label_color(self, c):
        self._label_color = QColor(c)
        self._apply_label_style()
        self.update()

    def label_font_size(self) -> int:
        return self._font_size

    def set_label_font_size(self, s: int):
        self._font_size = max(6, min(s, 48))
        self._apply_label_style()
        self._center_text()
        self.update()

    # ── Internal helpers ──────────────────────────────────────────────
    def _apply_label_style(self):
        """Push current font and colour onto the child text item."""
        f = QFont("Consolas", self._font_size)
        f.setWeight(QFont.Weight.Bold)
        self._label_item.setFont(f)
        self._label_item.setDefaultTextColor(self._label_color)

    def _center_text(self):
        """Reposition the child label so it is centred inside the button rect."""
        br = self._label_item.boundingRect()
        x = (self.rect().width()  - br.width())  / 2.0
        y = (self.rect().height() - br.height()) / 2.0
        self._label_item.setPos(x, y)

    def _sync_label_from_child(self):
        """Called by contentsChanged; keeps _label up-to-date for save/export."""
        self._label = self._label_item.toPlainText()
        self._center_text()

    # ── Resize internals ─────────────────────────────────────────────
    def _handle_rect(self):
        return QRectF(
            self.rect().right()  - self.HANDLE_SIZE,
            self.rect().bottom() - self.HANDLE_SIZE,
            self.HANDLE_SIZE, self.HANDLE_SIZE,
        )
    def _capture_resize_origin(self):
        self._resize_start_rect = QRectF(self.rect())

    # ── Paint: background + border + selection outline only ───────────
    # The child _ButtonLabelItem renders the text automatically.
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        is_sel = bool(option.state & QStyle.StateFlag.State_Selected)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), self._border_radius, self._border_radius)

        # Fill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, self._fill_color)

        # Border
        if self._border_width > 0:
            p = QPen(self._border_color, float(self._border_width))
            p.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(p)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # Dashed cyan selection outline (inset so it follows the rounded corners)
        if is_sel:
            inset = 2.0
            sel_rect = self.rect().adjusted(inset, inset, -inset, -inset)
            sel_path = QPainterPath()
            sel_path.addRoundedRect(sel_rect, self._border_radius, self._border_radius)
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(sel_path)

        self._paint_handle(painter, is_sel)

    # ── Mouse ─────────────────────────────────────────────────────────
    def mouseDoubleClickEvent(self, event):
        """FIX: Directly activates text editing on the button label."""
        self._label_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self._label_item.setFocus()
        # Ensure the label remains centered as the user types
        self._center_text()

    def mouseMoveEvent(self, event):
        if self._resizing:
            if self._resize_start_rect is None:
                self._resize_start_rect = QRectF(self.rect())
            delta = event.scenePos() - self._resize_start_pos
            new_w = max(60,        self._snap(self._resize_start_rect.width()  + delta.x()))
            new_h = max(GRID_STEP, self._snap(self._resize_start_rect.height() + delta.y()))
            self.setRect(0, 0, new_w, new_h)
            self._center_text()      # re-centre label as the button grows/shrinks
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def itemChange(self, c, v):
        if c == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()  # This "throws away" the drag movement
            return QPointF(_snap(v.x()), _snap(v.y()))
        return super().itemChange(c, v)


# ---------------------------------------------------------------------------
# CanvasGroupItem
# ---------------------------------------------------------------------------

class CanvasGroupItem(CanvasItemMixin, QGraphicsRectItem):
    """
    v1.9: A custom container for grouped items.
    Inherits from CanvasItemMixin to support Opacity, Hyperlinks, and Locking.
    """

    def __init__(self, items, x, y):
        super().__init__(0, 0, 1, 1)  # Bounding rect is computed dynamically
        self.setPos(x, y)
        self._children = list(items)
        for item in self._children:
            item.setParentItem(self)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._link_url = ""
        self._init_shadow_data()
        self._opacity = 1.0

    def _handle_rect(self):
        """Grouped containers do not expose a resize handle."""
        return QRectF()

    def _capture_resize_origin(self):
        """No-op: grouped containers currently do not resize."""
        return

    def boundingRect(self):
        """Returns the union of all children's bounding rects."""
        rect = QRectF()
        for item in self.childItems():
            rect = rect.united(item.mapToParent(item.boundingRect()).boundingRect())
        return rect

    def paint(self, painter, option, widget=None):
        """Draws the dashed neon selection indicator around the entire group."""
        if bool(option.state & QStyle.StateFlag.State_Selected):
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())


# ---------------------------------------------------------------------------
# _rdp_simplify — Ramer-Douglas-Peucker polyline simplification
# ---------------------------------------------------------------------------

def _rdp_simplify(points: list, epsilon: float = 0.5) -> list:
    """Reduces a list of (x, y) tuples using the RDP algorithm."""
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    dx, dy = end[0] - start[0], end[1] - start[1]
    dist_sq_line = dx * dx + dy * dy
    max_dist_sq, max_i = 0.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i][0] - start[0], points[i][1] - start[1]
        if dist_sq_line > 0:
            t = max(0.0, min(1.0, (px * dx + py * dy) / dist_sq_line))
            d_sq = (px - t * dx) ** 2 + (py - t * dy) ** 2
        else:
            d_sq = px * px + py * py
        if d_sq > max_dist_sq:
            max_dist_sq, max_i = d_sq, i
    if max_dist_sq > epsilon * epsilon:
        left  = _rdp_simplify(points[:max_i + 1], epsilon)
        right = _rdp_simplify(points[max_i:],     epsilon)
        return left[:-1] + right
    return [start, end]


# ---------------------------------------------------------------------------
# CanvasPathItem  (v2.1 — Unified Vector Ink Engine)
# ---------------------------------------------------------------------------

class CanvasPathItem(CanvasItemMixin, QGraphicsItem):
    ACCENT = QColor("#00E5FF")

    def __init__(self, points: list = None):
        super().__init__()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self._painter_path = QPainterPath()
        self._stroke_color = QColor("#A5D8FF")
        self._stroke_width = 2.0

        self._opacity  = 1.0
        self._link_url = ""
        self._init_shadow_data()
        self._locked = False

        if points:
            self._build_path_from_points(points)

    def _build_path_from_points(self, points: list):
        if not points or len(points) < 2:
            return
        # RDP simplification keeps file size low without losing visible detail
        if isinstance(points[0], (list, tuple)):
            simplified = _rdp_simplify(points, epsilon=0.5)
            self._painter_path = QPainterPath(QPointF(simplified[0][0], simplified[0][1]))
            for i in range(1, len(simplified)):
                self._painter_path.lineTo(QPointF(simplified[i][0], simplified[i][1]))
        else:
            # QPointF list (from mouseMoveEvent)
            self._painter_path = QPainterPath(points[0])
            for pt in points[1:]:
                self._painter_path.lineTo(pt)

    # ── QGraphicsItem overrides ────────────────────────────────────────

    def boundingRect(self):
        margin = self._stroke_width / 2.0 + 2
        return self._painter_path.boundingRect().adjusted(-margin, -margin, margin, margin)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(
            self._stroke_color, self._stroke_width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawPath(self._painter_path)
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setPen(QPen(self.ACCENT, 2.0, Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())

    def _handle_rect(self):
        br = self.boundingRect()
        return QRectF(
            br.right()  - self.HANDLE_SIZE,
            br.bottom() - self.HANDLE_SIZE,
            self.HANDLE_SIZE, self.HANDLE_SIZE,
        )

    def _capture_resize_origin(self):
        self._resize_start_rect = QRectF(self.boundingRect())

    def itemChange(self, c, v):
        if c == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if self._locked:
                return self.pos()
            return QPointF(self._snap(v.x()), self._snap(v.y()))
        return super().itemChange(c, v)

    # ── Stroke property accessors ──────────────────────────────────────

    def set_stroke_color(self, color):
        self._stroke_color = QColor(color)
        self.update()

    def stroke_color(self) -> QColor:
        return QColor(self._stroke_color)

    def set_stroke_width(self, width: float):
        self._stroke_width = max(0.5, float(width))
        self.update()

    def stroke_width(self) -> float:
        return self._stroke_width

    def path_to_svg_d(self) -> str:
        """Returns the path as an SVG 'd' attribute string."""
        d_parts = []
        for i in range(self._painter_path.elementCount()):
            elem = self._painter_path.elementAt(i)
            if elem.type == QPainterPath.ElementType.MoveToElement:
                d_parts.append(f"M {elem.x:.2f} {elem.y:.2f}")
            elif elem.type == QPainterPath.ElementType.LineToElement:
                d_parts.append(f"L {elem.x:.2f} {elem.y:.2f}")
            elif elem.type == QPainterPath.ElementType.CurveToElement:
                d_parts.append(f"C {elem.x:.2f} {elem.y:.2f}")
        return " ".join(d_parts)

    # ── v2.1 Vector Boolean Eraser Math ────────────────────────────────

    @classmethod
    def _from_painter_path(cls, new_path: QPainterPath, source: "CanvasPathItem") -> "CanvasPathItem":
        """Clone metadata from source onto a new path fragment."""
        item = cls()
        item._painter_path = new_path
        item._stroke_color = QColor(source._stroke_color)
        item._stroke_width = source._stroke_width
        item._opacity      = source._opacity
        item.setOpacity(item._opacity)
        item._link_url     = source._link_url
        item._init_shadow_data()
        item._shadow_data  = dict(source._shadow_data)
        item.apply_shadow()
        item._locked       = source._locked
        item.setZValue(source.zValue())
        item.setPos(0.0, 0.0)
        return item

    def apply_vector_erase(self, eraser_center_scene: QPointF, eraser_radius: float) -> list:
        """Returns a list of CanvasPathItem fragments with the erased region removed."""
        local_center = self.mapFromScene(eraser_center_scene)
        eraser_pp = QPainterPath()
        eraser_pp.addEllipse(local_center, eraser_radius, eraser_radius)

        stroker = QPainterPathStroker()
        stroker.setWidth(self._stroke_width + 2.0)
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        filled_stroke = stroker.createStroke(self._painter_path)

        if not filled_stroke.intersects(eraser_pp):
            return [self]   # eraser missed — return self unchanged

        local_pts = self._path_to_local_points()
        if len(local_pts) < 2:
            return []

        groups = self._split_around_eraser(local_pts, eraser_pp)
        if not groups:
            return []

        new_items = []
        for group in groups:
            if len(group) < 2:
                continue
            scene_pts = [self.mapToScene(p) for p in group]
            new_path = QPainterPath(scene_pts[0])
            for sp in scene_pts[1:]:
                new_path.lineTo(sp)
            new_items.append(CanvasPathItem._from_painter_path(new_path, self))
        return new_items

    def _path_to_local_points(self) -> list:
        pts = []
        for i in range(self._painter_path.elementCount()):
            elem = self._painter_path.elementAt(i)
            if elem.type in (
                QPainterPath.ElementType.MoveToElement,
                QPainterPath.ElementType.LineToElement,
                QPainterPath.ElementType.CurveToElement,
            ):
                pts.append(QPointF(elem.x, elem.y))
        return pts

    def _split_around_eraser(self, points: list, eraser_pp: QPainterPath) -> list:
        groups  = []
        current = []
        for pt in points:
            if eraser_pp.contains(pt):
                if len(current) >= 2:
                    groups.append(current)
                current = []
            else:
                current.append(pt)
        if len(current) >= 2:
            groups.append(current)
        return groups

    # ── Save / load helpers ────────────────────────────────────────────

    def get_path_elements_for_save(self) -> list:
        """Returns a flat [[x, y], ...] list of MoveTo/LineTo elements."""
        result = []
        for i in range(self._painter_path.elementCount()):
            elem = self._painter_path.elementAt(i)
            if elem.type in (
                QPainterPath.ElementType.MoveToElement,
                QPainterPath.ElementType.LineToElement,
            ):
                result.append([round(elem.x, 2), round(elem.y, 2)])
        return result