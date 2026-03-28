"""
DrawScript — WHITE CANVAS EDITION
Now with Multi-Select & Alignment Tools (v1.2)!
"""

import sys
import json
import random
import pathlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPixmapItem, QTextEdit, QSizePolicy,
    QLabel, QSlider, QColorDialog, QFrame, QStackedWidget, QTabWidget,
    QTextBrowser, QFileDialog, QStatusBar,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath,
    QKeySequence, QShortcut, QTextCursor, QTextCharFormat, QPixmap,
)
from PyQt6.QtWidgets import QStyle


DARK_QSS = """
* {
    outline: none;
    box-sizing: border-box;
}

QMainWindow, QWidget {
    background-color: #0A0E17;
    color: #E8EAF0;
    font-family: "Consolas", "Courier New", "Lucida Console",
                 "Terminal", monospace;
    font-size: 12px;
    font-weight: bold;
    border-radius: 0px;
}

QWidget#Toolbar {
    background-color: #111827;
    border-right: 2px solid #000000;
}

QWidget#RightPanel {
    background-color: #111827;
    border-left: 2px solid #000000;
}

QPushButton {
    background-color: #1E2A3A;
    color: #E8EAF0;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: "Consolas", "Courier New", "Lucida Console", monospace;
    font-size: 12px;
    font-weight: bold;
    text-align: left;
}

QPushButton:hover {
    background-color: #253347;
    color: #00E5FF;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
}

QPushButton:pressed {
    background-color: #111827;
    color: #00E5FF;
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton:disabled {
    background-color: #111827;
    color: #3D4F63;
    border-top:    2px solid #1E2A3A;
    border-left:   2px solid #1E2A3A;
    border-right:  2px solid #1E2A3A;
    border-bottom: 4px solid #1E2A3A;
}

QPushButton#btn_generate {
    background-color: #FFD166;
    color: #000000;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    font-weight: bold;
    text-align: center;
}

QPushButton#btn_generate:hover {
    background-color: #FFC107;
    color: #000000;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_generate:pressed {
    background-color: #E5A800;
    color: #000000;
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton#btn_clear:hover {
    background-color: #2A0F1F;
    color: #FF007F;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_clear:pressed {
    background-color: #1A0010;
    color: #CC0066;
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton#btn_color {
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    min-height: 26px;
    text-align: center;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    background-color: #1E2A3A;
    color: #E8EAF0;
    padding: 0 8px;
}

QPushButton#btn_color:hover {
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    color: #00E5FF;
}

QPushButton#btn_color:pressed {
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 2px 6px 0px 10px;
}

QPushButton#btn_img {
    background-color: #1A2B1A;
    color: #6EE68A;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    font-weight: bold;
    text-align: left;
}

QPushButton#btn_img:hover {
    background-color: #213521;
    color: #A8F0B8;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_img:pressed {
    background-color: #0F1E0F;
    color: #6EE68A;
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton#btn_save {
    background-color: #0D2137;
    color: #00E5FF;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    font-weight: bold;
    text-align: left;
}

QPushButton#btn_save:hover {
    background-color: #0A3050;
    color: #7FFFFF;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_save:pressed {
    background-color: #061828;
    border-top:    4px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton#btn_open {
    background-color: #0D2137;
    color: #FFD166;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    font-weight: bold;
    text-align: left;
}

QPushButton#btn_open:hover {
    background-color: #0A3050;
    color: #FFC107;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_open:pressed {
    background-color: #061828;
    border-top:    4px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 8px 4px 12px;
}

QPushButton#btn_align {
    background-color: #0D2137;
    color: #00E5FF;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    padding: 6px 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    text-align: center;
}

QPushButton#btn_align:hover {
    background-color: #0A3050;
    color: #7FFFFF;
    border-bottom: 4px solid #000000;
}

QPushButton#btn_align:pressed {
    background-color: #061828;
    border-top:    4px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 8px 4px 4px 4px;
}

QGraphicsView {
    background-color: #ffffff;
    border: none;
}

QLabel#heading {
    color: #7B8EA8;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 2px 0;
}

QLabel#muted {
    color: #7B8EA8;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #1E2A3A;
    border: 2px solid #000000;
    border-radius: 2px;
    margin: 0 4px;
}

QSlider::sub-page:horizontal {
    background: #FFD166;
    border: none;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width:  14px;
    height: 14px;
    background: #253347;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
    border-radius: 4px;
    margin: -5px -2px;
}

QSlider::handle:horizontal:hover {
    background: #FFD166;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 4px solid #000000;
}

QSlider::handle:horizontal:pressed {
    background: #FFC107;
    border-top:    4px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
}

QTabWidget::pane {
    border: 2px solid #000000;
    border-radius: 4px;
    background: #111827;
}

QTabBar::tab {
    background: #1E2A3A;
    color: #7B8EA8;
    padding: 5px 14px;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: none;
    border-radius: 4px 4px 0px 0px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background: #111827;
    color: #FFD166;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #111827;
}

QTabBar::tab:hover:!selected {
    color: #00E5FF;
    background: #253347;
}

QTextEdit, QTextBrowser {
    background-color: #0A0E17;
    color: #A5D8FF;
    border: 2px solid #000000;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", "Lucida Console", monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 6px;
    selection-background-color: #1E3A5F;
    selection-color: #E8EAF0;
}

QStatusBar {
    background-color: #111827;
    color: #7B8EA8;
    border-top: 2px solid #000000;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 0 8px;
}

QScrollBar:vertical {
    background: #111827;
    width: 12px;
    border-left: 2px solid #000000;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #1E2A3A;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover  { background: #FFD166; }

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical      { height: 0; background: none; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical      { background: none; }

QScrollBar:horizontal {
    background: #111827;
    height: 12px;
    border-top: 2px solid #000000;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #1E2A3A;
    border-top:    2px solid #000000;
    border-left:   2px solid #000000;
    border-right:  2px solid #000000;
    border-bottom: 2px solid #000000;
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover { background: #FFD166; }

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal     { width: 0; background: none; }

QFrame[frameShape="4"] {
    color: #000000;
    max-height: 2px;
    background: #000000;
    border: none;
}
"""


GRID_STEP = 24


def _snap(v: float) -> float:
    return round(v / GRID_STEP) * GRID_STEP


def _h_rule() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


class KeyboardShortcutsMixin:
    def setup_keyboard_shortcuts(self):
        self._clipboard_shape_data = None
        self._undo_stack = []

        self._witty_prefixes = [
            ">> ", "[SYS] ", "[OK]  ", "[INF] ", "[MSG] ", "*** ",
        ]

        QShortcut(QKeySequence("Ctrl+C"),    self).activated.connect(self._copy_shape)
        QShortcut(QKeySequence("Ctrl+V"),    self).activated.connect(self._paste_shape)
        QShortcut(QKeySequence("Delete"),    self).activated.connect(self._delete_selected)
        QShortcut(QKeySequence("Backspace"), self).activated.connect(self._delete_selected)
        QShortcut(QKeySequence("Ctrl+Z"),    self).activated.connect(self._undo_delete)
        QShortcut(QKeySequence("Ctrl+E"),    self).activated.connect(self._on_generate)

        if self.statusBar() is None:
            self.setStatusBar(QStatusBar())

        self._show_witty("KEYBOARD INTERFACE ONLINE. CTRL+C/V/Z/E/DEL")

    def _copy_shape(self):
        selected = self.canvas.scene.selectedItems()
        if not selected:
            return
        item = selected[0]
        if isinstance(item, StyledRectItem):
            self._clipboard_shape_data = {
                "type": "rect",
                "w": item.rect().width(), "h": item.rect().height(),
                "fill": item.fill_color(), "rad": item.border_radius(),
                "src_x": item.x(), "src_y": item.y(),
            }
        elif isinstance(item, DraggableTextItem):
            self._clipboard_shape_data = {
                "type": "text",
                "text": item.toPlainText(), "color": item.text_color(),
                "size": item.font_size(), "weight": item.thickness(),
                "src_x": item.x(), "src_y": item.y(),
            }
        elif isinstance(item, DraggableImageItem):
            self._clipboard_shape_data = {
                "type": "image",
                "path": item.file_path(),
                "w": item.img_width(), "h": item.img_height(),
                "src_x": item.x(), "src_y": item.y(),
            }
        else:
            return
        self._show_witty("BLOCK COPIED TO BUFFER.")

    def _paste_shape(self):
        if not self._clipboard_shape_data:
            self._show_witty("BUFFER IS EMPTY.")
            return
        data   = self._clipboard_shape_data
        offset = 24
        ox, oy = data["src_x"] + offset, data["src_y"] + offset
        if data["type"] == "rect":
            new_item = StyledRectItem(ox, oy, data["w"], data["h"])
            new_item.set_fill_color(data["fill"])
            new_item.set_border_radius(data["rad"])
        elif data["type"] == "text":
            new_item = DraggableTextItem(data["text"], ox, oy)
            new_item.set_text_color(data["color"])
            new_item.set_font_size(data["size"])
            new_item.set_thickness(data["weight"])
        elif data["type"] == "image":
            new_item = DraggableImageItem(data["path"], ox, oy, data["w"], data["h"])
        else:
            return
        self.canvas.scene.addItem(new_item)
        self._show_witty("BLOCK PASTED FROM BUFFER.")

    def _delete_selected(self):
        selected = self.canvas.scene.selectedItems()
        if not selected:
            return
        self._undo_stack.append(list(selected))
        for item in selected:
            self.canvas.scene.removeItem(item)
        count = len(selected)
        self._show_witty(f"{count} {'BLOCK' if count == 1 else 'BLOCKS'} DELETED. CTRL+Z TO RESTORE.")

    def _undo_delete(self):
        if not self._undo_stack:
            self._show_witty("NOTHING TO UNDO.")
            return
        items = self._undo_stack.pop()
        for item in items:
            self.canvas.scene.addItem(item)
        self._show_witty(f"RESTORED {len(items)} BLOCK(S).")

    def _show_witty(self, message: str):
        prefix = random.choice(self._witty_prefixes)
        self.statusBar().showMessage(prefix + message, 3500)


class CanvasItemMixin:
    """Shared constants, grid-snap helper, resize-handle paint, and
    press/release event pattern for StyledRectItem and DraggableImageItem."""

    HANDLE_SIZE = 12
    ACCENT      = QColor("#00E5FF")
    HANDLE_CLR  = QColor("#FFD166")

    def _snap(self, v: float) -> float:
        return _snap(v)

    def _paint_handle(self, painter, is_selected: bool):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(self._handle_rect(), self.HANDLE_CLR if is_selected else QColor("#111827"))

    def _capture_resize_origin(self):
        """Subclass stores its starting geometry (rect or w/h tuple) here."""

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton
                and self._handle_rect().contains(event.pos())):
            self._resizing         = True
            self._resize_start_pos = event.scenePos()
            self._capture_resize_origin()
            event.accept()
        else:
            self._resizing = False
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)


class StyledRectItem(CanvasItemMixin, QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float = 180, h: float = 90):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable    |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges,
        )
        self._fill_color    = QColor("#1E2A3A")
        self._border_color  = QColor("#000000")
        self._border_radius = 0.0
        self._resizing          = False
        self._resize_start_pos  = None
        self._resize_start_rect = None

    def set_fill_color(self, color: QColor):
        self._fill_color = color
        self.update()

    def set_border_radius(self, radius: float):
        self._border_radius = float(radius)
        self.update()

    def fill_color(self) -> QColor:
        return QColor(self._fill_color)

    def border_radius(self) -> float:
        return self._border_radius

    def _handle_rect(self) -> QRectF:
        r = self.rect()
        s = self.HANDLE_SIZE
        return QRectF(r.right() - s, r.bottom() - s, s, s)

    def _capture_resize_origin(self):
        self._resize_start_rect = QRectF(self.rect())

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)

        body = QPainterPath()
        body.addRoundedRect(self.rect(), self._border_radius, self._border_radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(body, self._fill_color)

        border_pen = QPen(self.ACCENT if is_selected else self._border_color, 2.0)
        border_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(border_pen)
        painter.drawPath(body)

        if is_selected:
            glow_path = QPainterPath()
            glow_path.addRect(self.rect().adjusted(-3, -3, 3, 3))
            painter.setPen(QPen(QColor(0, 229, 255, 100), 2))
            painter.drawPath(glow_path)

        self._paint_handle(painter, is_selected)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.scenePos() - self._resize_start_pos
            new_w = max(50, self._resize_start_rect.width()  + delta.x())
            new_h = max(24, self._resize_start_rect.height() + delta.y())
            self.setRect(0, 0, new_w, new_h)
            event.accept()
        else:
            super().mouseMoveEvent(event)


class DraggableTextItem(QGraphicsTextItem):
    """
    A movable, selectable, double-click-editable text item.
    Three independently controllable style axes:
      - color  — any QColor via set_text_color()
      - size   — point size 6–96 via set_font_size()
      - weight — nine levels (Thin->Black) via set_thickness()
    """

    WEIGHT_CSS = {
        1: 100, 2: 200, 3: 300, 4: 400, 5: 500,
        6: 600, 7: 700, 8: 800, 9: 900,
    }
    _WEIGHT_QFONT = {
        1: QFont.Weight.Thin,      2: QFont.Weight.ExtraLight,
        3: QFont.Weight.Light,     4: QFont.Weight.Normal,
        5: QFont.Weight.Medium,    6: QFont.Weight.DemiBold,
        7: QFont.Weight.Bold,      8: QFont.Weight.ExtraBold,
        9: QFont.Weight.Black,
    }

    def __init__(self, text: str, x: float, y: float):
        super().__init__(text)
        self.setPos(x, y)
        self._text_color = QColor("#0A0E17")
        self._font_size  = 14
        self._weight_val = 7
        self.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable    |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsTextItem.GraphicsItemFlag.ItemSendsGeometryChanges,
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()

    def _build_font(self) -> QFont:
        font = QFont("Courier New", self._font_size)
        font.setWeight(self._WEIGHT_QFONT.get(self._weight_val, QFont.Weight.Bold))
        return font

    def _apply_formatting(self):
        font = self._build_font()
        self.setFont(font)
        self.setDefaultTextColor(self._text_color)
        char_fmt = QTextCharFormat()
        char_fmt.setForeground(QBrush(self._text_color))
        char_fmt.setFont(font)
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(char_fmt)
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.update()

    def set_text_color(self, color: QColor):
        self._text_color = QColor(color)
        self._apply_formatting()

    def text_color(self) -> QColor:
        return QColor(self._text_color)

    def set_font_size(self, size: int):
        self._font_size = max(6, min(size, 96))
        self._apply_formatting()

    def font_size(self) -> int:
        return self._font_size

    def set_thickness(self, weight_level: int):
        self._weight_val = max(1, min(weight_level, 9))
        self._apply_formatting()

    def thickness(self) -> int:
        return self._weight_val

    def thickness_css(self) -> int:
        return self.WEIGHT_CSS.get(self._weight_val, 700)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()
        super().focusOutEvent(event)


class DraggableImageItem(CanvasItemMixin, QGraphicsPixmapItem):
    """
    A movable, resizable image item that renders a local image file on the canvas.
    Bottom-right resize handle, 24-px grid snapping on move, cyan selection border.
    """

    def __init__(self, file_path: str, x: float, y: float,
                 w: float = 192, h: float = 144):
        super().__init__()
        self._file_path = file_path
        self._img_w     = float(w)
        self._img_h     = float(h)

        self._source_pixmap = QPixmap(file_path)
        if self._source_pixmap.isNull():
            self._source_pixmap = QPixmap(int(w), int(h))
            self._source_pixmap.fill(QColor("#2A3A4A"))

        self._apply_scaled_pixmap()
        self.setPos(x, y)
        self.setFlags(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable    |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges,
        )
        self._resizing          = False
        self._resize_start_pos  = None
        self._resize_start_size = (w, h)

    def file_path(self) -> str:
        return self._file_path

    def img_width(self) -> float:
        return self._img_w

    def img_height(self) -> float:
        return self._img_h

    def _apply_scaled_pixmap(self):
        scaled = self._source_pixmap.scaled(
            int(self._img_w), int(self._img_h),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def _handle_rect(self) -> QRectF:
        s = self.HANDLE_SIZE
        return QRectF(self._img_w - s, self._img_h - s, s, s)

    def _capture_resize_origin(self):
        self._resize_start_size = (self._img_w, self._img_h)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._img_w, self._img_h)

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionChange:
            return QPointF(self._snap(value.x()), self._snap(value.y()))
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(0, 0, int(self._img_w), int(self._img_h), self.pixmap())
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        if is_selected:
            painter.setPen(QPen(self.ACCENT, 2.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, self._img_w, self._img_h))
            painter.setPen(QPen(QColor(0, 229, 255, 100), 2))
            painter.drawRect(QRectF(-3, -3, self._img_w + 6, self._img_h + 6))
        self._paint_handle(painter, is_selected)

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


class DarkCanvasView(QGraphicsView):
    SCENE_W = 1000
    SCENE_H = 700

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(0, 0, self.SCENE_W, self.SCENE_H)
        self.scene.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.setScene(self.scene)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing,
        )
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._box_counter   = 0
        self._text_counter  = 0
        self._image_counter = 0
        self._z_counter     = 0

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        dim_pen    = QPen(QColor("#f0f0f0"), 1)
        bright_pen = QPen(QColor("#dddddd"), 1)

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

    def add_box(self):
        offset = (self._box_counter * 24) % 192
        item   = StyledRectItem(60 + offset, 60 + offset)
        item.setZValue(self._z_counter)
        self._z_counter    += 1
        self._box_counter  += 1
        self.scene.addItem(item)

    def add_text(self):
        offset = (self._text_counter * 24) % 192
        item   = DraggableTextItem(f"BLOCK_{self._text_counter + 1:02d}", 80 + offset, 80 + offset)
        item.setZValue(self._z_counter)
        self._z_counter     += 1
        self._text_counter  += 1
        self.scene.addItem(item)

    def add_image(self, file_path: str):
        offset = (self._image_counter * 24) % 192
        item   = DraggableImageItem(file_path, 72 + offset, 72 + offset)
        item.setZValue(self._z_counter)
        self._z_counter     += 1
        self._image_counter += 1
        self.scene.addItem(item)

    def clear_canvas(self):
        self.scene.clear()
        self._box_counter   = 0
        self._text_counter  = 0
        self._image_counter = 0
        self._z_counter     = 0

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        else:
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
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self.dragMode() != QGraphicsView.DragMode.ScrollHandDrag:
            hit = self.itemAt(event.pos())
            self.setDragMode(
                QGraphicsView.DragMode.RubberBandDrag if hit is None
                else QGraphicsView.DragMode.NoDrag
            )
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.dragMode() != QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)


class PropertyInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item  = None
        self._current_items = []
        self._scene         = None
        self.status_callback = None

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 8)
        root.setSpacing(6)

        heading = QLabel("[ PROPERTIES ]")
        heading.setObjectName("heading")
        root.addWidget(heading)
        root.addWidget(_h_rule())

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_empty_page())
        self._stack.addWidget(self._build_rect_controls_page())
        self._stack.addWidget(self._build_text_controls_page())
        self._stack.addWidget(self._build_image_controls_page())
        self._stack.addWidget(self._build_alignment_page())
        root.addWidget(self._stack)

        self._layer_widget = self._build_layer_section()
        root.addWidget(self._layer_widget)
        self._layer_widget.setVisible(False)

        root.addStretch()
        self._show_empty()

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
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(12)
        self.btn_rect_color = self._add_color_btn(layout, "> FILL COLOR", self._on_rect_color_click)
        self.slider_radius, self.lbl_radius_val = self._add_slider_row(
            layout, "> CORNER RAD", 0, 60, 0, self._on_radius_change,
            fmt=lambda v: f"{v}px",
        )
        self.lbl_rect_geometry = self._add_info_block(layout, "> GEOMETRY")
        layout.addStretch()
        return page

    def _build_text_controls_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(10)
        self.btn_text_color = self._add_color_btn(layout, "> TEXT COLOR", self._on_text_color_click)
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
        layout.setSpacing(10)
        layout.addWidget(self._muted("> IMAGE ASSET"))
        layout.addWidget(_h_rule())
        self.lbl_img_path = self._add_info_block(layout, "> FILE PATH")
        layout.addWidget(_h_rule())
        self.lbl_img_geometry = self._add_info_block(layout, "> GEOMETRY")
        layout.addStretch()
        return page

    def _build_alignment_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(8)

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

    @staticmethod
    def _item_size(item) -> tuple:
        br = item.boundingRect()
        return br.width(), br.height()

    def load_multi_select(self, items: list, scene=None):
        self._current_item  = None
        self._current_items = list(items)
        self._scene         = scene
        self._lbl_multi_count.setText(f"> {len(items)} BLOCKS SELECTED")
        self._stack.setCurrentIndex(4)
        self._layer_widget.setVisible(False)

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

    def _emit_status(self, msg: str):
        if callable(self.status_callback):
            self.status_callback(msg)

    def _build_layer_section(self) -> QWidget:
        w      = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
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

    def _update_layer_label(self):
        if self._current_item:
            self.lbl_layer_val.setText(f"Z: {int(self._current_item.zValue())}")

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

    def load_item(self, item, scene=None):
        self._current_item = item
        self._scene        = scene
        if isinstance(item, StyledRectItem):
            self._refresh_rect_controls()
            self._stack.setCurrentIndex(1)
        elif isinstance(item, DraggableTextItem):
            self._refresh_text_controls()
            self._stack.setCurrentIndex(2)
        elif isinstance(item, DraggableImageItem):
            self._refresh_image_controls()
            self._stack.setCurrentIndex(3)
        self._update_layer_label()
        self._layer_widget.setVisible(True)

    def clear(self):
        self._current_item  = None
        self._current_items = []
        self._scene         = None
        self._layer_widget.setVisible(False)
        self._show_empty()

    def _show_empty(self):
        self._stack.setCurrentIndex(0)

    def _refresh_rect_controls(self):
        item = self._current_item
        self._apply_swatch(self.btn_rect_color, item.fill_color())
        self.slider_radius.blockSignals(True)
        self.slider_radius.setValue(int(item.border_radius()))
        self.lbl_radius_val.setText(f"{int(item.border_radius())}px")
        self.slider_radius.blockSignals(False)
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
            f"X:{pos.x():.0f} Y:{pos.y():.0f}  W:{item.img_width():.0f} H:{item.img_height():.0f}"
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

    def _on_size_change(self, value: int):
        self.lbl_size_val.setText(f"{value}pt")
        if self._current_item:
            self._current_item.set_font_size(value)

    def _on_thick_change(self, value: int):
        self.lbl_thick_val.setText(str(DraggableTextItem.WEIGHT_CSS.get(value, value * 100)))
        if self._current_item:
            self._current_item.set_thickness(value)


class DarkMainWindow(QMainWindow, KeyboardShortcutsMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DRAWSCRIPT // WHITE CANVAS EDITION")
        self.resize(1360, 760)
        self.setStatusBar(QStatusBar())

        toolbar_widget = self._build_toolbar()
        self.canvas    = DarkCanvasView()
        right_panel    = self._build_right_panel()

        central     = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(toolbar_widget)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(right_panel)
        self.setCentralWidget(central)

        self._wire_signals()
        self.setup_keyboard_shortcuts()

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("Toolbar")
        widget.setFixedWidth(148)

        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 14, 10, 14)

        section_lbl = QLabel("[ CANVAS ]")
        section_lbl.setObjectName("heading")
        layout.addWidget(section_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        self.btn_box = QPushButton("[+] ADD BOX")
        self.btn_txt = QPushButton("[A] ADD TEXT")
        self.btn_img = QPushButton("[+] ADD IMAGE")
        self.btn_clr = QPushButton("[X] CLEAR")
        self.btn_gen = QPushButton("[/] GENERATE")
        self.btn_exp = QPushButton("[S] EXPORT")

        self.btn_img.setObjectName("btn_img")
        self.btn_clr.setObjectName("btn_clear")
        self.btn_gen.setObjectName("btn_generate")

        for btn in (self.btn_box, self.btn_txt, self.btn_img,
                    self.btn_clr, self.btn_gen, self.btn_exp):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        layout.addSpacing(10)
        persist_lbl = QLabel("[ PROJECT ]")
        persist_lbl.setObjectName("heading")
        layout.addWidget(persist_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        self.btn_save = QPushButton("[↓] SAVE PROJECT")
        self.btn_open = QPushButton("[↑] OPEN PROJECT")
        self.btn_save.setObjectName("btn_save")
        self.btn_open.setObjectName("btn_open")

        for btn in (self.btn_save, self.btn_open):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        layout.addStretch()
        return widget

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("RightPanel")
        panel.setFixedWidth(350)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.inspector = PropertyInspector()
        self.inspector.setFixedHeight(430)
        layout.addWidget(self.inspector)
        layout.addWidget(_h_rule())

        self.tabs            = QTabWidget()
        self.code_editor     = QTextEdit()
        self.preview_browser = QTextBrowser()

        retro_font = QFont("Consolas", 10)
        retro_font.setStyleHint(QFont.StyleHint.TypeWriter)
        retro_font.setBold(True)
        self.code_editor.setFont(retro_font)
        self.preview_browser.setFont(retro_font)

        self.tabs.addTab(self.code_editor,     "RAW CODE")
        self.tabs.addTab(self.preview_browser, "LIVE RENDER")
        layout.addWidget(self.tabs, stretch=1)
        return panel

    def _wire_signals(self):
        self.btn_box .clicked.connect(self.canvas.add_box)
        self.btn_txt .clicked.connect(self.canvas.add_text)
        self.btn_img .clicked.connect(self._on_add_image)
        self.btn_clr .clicked.connect(self._on_clear)
        self.btn_gen .clicked.connect(self._on_generate)
        self.btn_exp .clicked.connect(self._export_html)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_open.clicked.connect(self._open_project)
        self.canvas.scene.selectionChanged.connect(self._on_selection)
        self.inspector.status_callback = self._show_witty

    def _on_add_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "OPEN IMAGE FILE", "",
            "Image Files (*.png *.jpg *.jpeg);;All Files (*)",
        )
        if not path:
            return
        probe = QPixmap(path)
        if probe.isNull():
            self._show_witty("IMAGE LOAD FAILED. UNSUPPORTED FORMAT OR CORRUPT FILE.")
            return
        self.canvas.add_image(path)
        self._show_witty(f"IMAGE ASSET LOADED. SOURCE: {probe.width()}x{probe.height()}px.")

    def _on_clear(self):
        self.canvas.clear_canvas()
        self.inspector.clear()
        self.code_editor.clear()
        self.preview_browser.clear()
        self._show_witty("CANVAS CLEARED. MEMORY WIPED.")

    def _on_selection(self):
        selected = self.canvas.scene.selectedItems()
        if len(selected) == 1 and isinstance(
            selected[0], (StyledRectItem, DraggableTextItem, DraggableImageItem)
        ):
            self.inspector.load_item(selected[0], self.canvas.scene)
        elif len(selected) >= 2:
            self.inspector.load_multi_select(selected, self.canvas.scene)
            self._show_witty(f"{len(selected)} BLOCKS IN SELECTION. ALIGNMENT MODE ACTIVE.")
        else:
            self.inspector.clear()

    def _on_generate(self):
        items = self.canvas.scene.items()
        if not items:
            self._show_witty("CANVAS EMPTY. ADD BLOCKS FIRST.")
            return

        html_map = {
            StyledRectItem: lambda it: {
                "type": "rect",
                "x": it.x(), "y": it.y(),
                "w": it.rect().width(), "h": it.rect().height(),
                "fill": it.fill_color().name(),
                "rad":  it.border_radius(),
                "z":    int(it.zValue()),
            },
            DraggableTextItem: lambda it: {
                "type":   "text",
                "x":      it.x(), "y": it.y(),
                "text":   it.toPlainText(),
                "color":  it.text_color().name(),
                "size":   it.font_size(),
                "weight": it.thickness_css(),
                "z":      int(it.zValue()),
            },
            DraggableImageItem: lambda it: {
                "type": "image",
                "x":    it.x(), "y": it.y(),
                "w":    it.img_width(), "h": it.img_height(),
                "path": it.file_path(),
                "z":    int(it.zValue()),
            },
        }
        shapes = sorted(
            [html_map[type(it)](it) for it in items if type(it) in html_map],
            key=lambda s: s["z"],
        )

        css = [
            "body { margin: 0; padding: 0; background-color: #ffffff; }",
            (
                ".drawscript-canvas { position: relative; width: 100vw; height: 100vh;"
                " overflow: hidden;"
                " font-family: 'Courier New', 'Consolas', monospace; }"
            ),
            ".canvas-item { position: absolute; }",
        ]
        html = ['<div class="drawscript-canvas">']

        for idx, shape in enumerate(shapes):
            item_id = f"item-{idx}"
            if shape["type"] == "text":
                html.append(
                    f'  <div id="{item_id}" class="canvas-item">{shape["text"]}</div>'
                )
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" font-size: {shape['size']}pt; font-weight: {shape['weight']};"
                    f" color: {shape['color']}; white-space: nowrap; z-index: {shape['z']};"
                    f"}}"
                )
            elif shape["type"] == "rect":
                html.append(f'  <div id="{item_id}" class="canvas-item"></div>')
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" background-color: {shape['fill']};"
                    f" border-radius: {shape['rad']:.0f}px;"
                    f" border: 2px solid #000000; z-index: {shape['z']};"
                    f"}}"
                )
            elif shape["type"] == "image":
                abs_uri = pathlib.Path(shape["path"]).as_uri()
                html.append(
                    f'  <img id="{item_id}" class="canvas-item" src="{abs_uri}" alt="">'
                )
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" display: block; z-index: {shape['z']};"
                    f"}}"
                )

        html.append("</div>")
        final_html = (
            "<!DOCTYPE html>\n<html>\n<head>\n"
            f"<style>\n{chr(10).join(css)}\n</style>\n"
            f"</head>\n<body>\n{chr(10).join(html)}\n</body>\n</html>"
        )

        self.code_editor.setPlainText(final_html)
        self.preview_browser.setHtml(final_html)
        self._show_witty(f"COMPILED {len(shapes)} BLOCK(S). OUTPUT READY.")

    def _save_project(self):
        items = self.canvas.scene.items()
        if not items:
            self._show_witty("NOTHING TO SAVE. CANVAS IS EMPTY.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "SAVE PROJECT", "project.draw",
            "DrawScript Project (*.draw);;All Files (*)"
        )
        if not path:
            return

        save_map = {
            StyledRectItem: lambda it: {
                "type":   "rect",
                "x":      it.x(), "y": it.y(),
                "w":      it.rect().width(), "h": it.rect().height(),
                "fill":   it.fill_color().name(QColor.NameFormat.HexArgb),
                "radius": it.border_radius(), "z": it.zValue(),
            },
            DraggableTextItem: lambda it: {
                "type":   "text",
                "x":      it.x(), "y": it.y(),
                "text":   it.toPlainText(),
                "color":  it.text_color().name(QColor.NameFormat.HexArgb),
                "size":   it.font_size(), "weight": it.thickness(), "z": it.zValue(),
            },
            DraggableImageItem: lambda it: {
                "type": "image",
                "x":    it.x(), "y": it.y(),
                "w":    it.img_width(), "h": it.img_height(),
                "path": it.file_path(), "z": it.zValue(),
            },
        }
        payload = [save_map[type(it)](it) for it in items if type(it) in save_map]

        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"version": 2, "items": payload}, fh, indent=2)
            self._show_witty(f"PROJECT ARCHIVED TO DISK. {len(payload)} BLOCK(S) COMMITTED.")
        except OSError as exc:
            self._show_witty(f"WRITE FAILED: {exc}")

    def _load_item_entry(self, entry: dict):
        kind = entry.get("type")
        if kind == "rect":
            item = StyledRectItem(entry["x"], entry["y"], entry["w"], entry["h"])
            c = QColor(entry["fill"])
            if c.isValid():
                item.set_fill_color(c)
            item.set_border_radius(entry.get("radius", 0))
            self.canvas._box_counter += 1
        elif kind == "text":
            item = DraggableTextItem(entry["text"], entry["x"], entry["y"])
            c = QColor(entry["color"])
            if c.isValid():
                item.set_text_color(c)
            item.set_font_size(entry.get("size", 14))
            item.set_thickness(entry.get("weight", 7))
            self.canvas._text_counter += 1
        elif kind == "image":
            item = DraggableImageItem(
                entry.get("path", ""), entry["x"], entry["y"],
                entry.get("w", 192), entry.get("h", 144),
            )
            self.canvas._image_counter += 1
        else:
            return None
        item.setZValue(entry.get("z", 0))
        return item

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "OPEN PROJECT", "",
            "DrawScript Project (*.draw);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            self._show_witty(f"PARSE ERROR: {exc}")
            return

        self.canvas.clear_canvas()
        self.inspector.clear()
        self.code_editor.clear()
        self.preview_browser.clear()

        items_data = data.get("items", [])
        for entry in items_data:
            item = self._load_item_entry(entry)
            if item:
                self.canvas.scene.addItem(item)

        self.canvas._z_counter = int(max((e.get("z", 0) for e in items_data), default=0)) + 1
        self._show_witty(f"DESIGN LOADED FROM ARCHIVE. {len(items_data)} BLOCK(S) RESTORED.")

    def _export_html(self):
        content = self.code_editor.toPlainText().strip()
        if not content:
            self._show_witty("NO OUTPUT TO EXPORT. RUN GENERATE FIRST.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "EXPORT HTML", "index.html", "HTML Files (*.html)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            self._show_witty(f"FILE WRITTEN TO DISK: {path}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    window = DarkMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()