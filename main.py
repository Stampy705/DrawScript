"""
DrawScript — WHITE CANVAS EDITION
Now with Bulletproof Text Color & Thickness properties!
"""

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QTextEdit, QSizePolicy, QLabel, QSlider,
    QColorDialog, QFrame, QStackedWidget, QTabWidget, QTextBrowser,
    QFileDialog, QStatusBar,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath,
    QKeySequence, QShortcut, QTextCursor, QTextCharFormat
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
                "type":  "rect",
                "w":     item.rect().width(),
                "h":     item.rect().height(),
                "fill":  item.fill_color(),
                "rad":   item.border_radius(),
                "src_x": item.x(),
                "src_y": item.y(),
            }
        elif isinstance(item, DraggableTextItem):
            self._clipboard_shape_data = {
                "type":   "text",
                "text":   item.toPlainText(),
                "color":  item.text_color(),
                "size":   item.font_size(),
                "weight": item.thickness(),
                "src_x":  item.x(),
                "src_y":  item.y(),
            }
        self._show_witty("BLOCK COPIED TO BUFFER.")

    def _paste_shape(self):
        if not self._clipboard_shape_data:
            self._show_witty("BUFFER IS EMPTY.")
            return
        data   = self._clipboard_shape_data
        offset = 24
        if data["type"] == "rect":
            new_item = StyledRectItem(
                data["src_x"] + offset, data["src_y"] + offset,
                data["w"], data["h"],
            )
            new_item.set_fill_color(data["fill"])
            new_item.set_border_radius(data["rad"])
            self.canvas.scene.addItem(new_item)
        else:
            new_item = DraggableTextItem(
                data["text"],
                data["src_x"] + offset, data["src_y"] + offset,
            )
            new_item.set_text_color(data["color"])
            new_item.set_font_size(data["size"])
            new_item.set_thickness(data["weight"])
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
        noun  = "BLOCK" if count == 1 else "BLOCKS"
        self._show_witty(f"{count} {noun} DELETED. CTRL+Z TO RESTORE.")

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


class StyledRectItem(QGraphicsRectItem):
    HANDLE_SIZE = 12
    ACCENT      = QColor("#00E5FF")
    HANDLE_CLR  = QColor("#FFD166")

    def __init__(self, x: float, y: float, w: float = 180, h: float = 90):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)

        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
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

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)

        body = QPainterPath()
        body.addRoundedRect(self.rect(), self._border_radius, self._border_radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(body, self._fill_color)

        border_pen = QPen(
            self.ACCENT if is_selected else self._border_color,
            2.0 if is_selected else 2.0,
        )
        border_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(border_pen)
        painter.drawPath(body)

        if is_selected:
            glow_rect = self.rect().adjusted(-3, -3, 3, 3)
            glow_path = QPainterPath()
            glow_path.addRect(glow_rect)
            painter.setPen(QPen(QColor(0, 229, 255, 100), 2))
            painter.drawPath(glow_path)

        handle_color = self.HANDLE_CLR if is_selected else QColor("#111827")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(self._handle_rect(), handle_color)

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton
                and self._handle_rect().contains(event.pos())):
            self._resizing          = True
            self._resize_start_pos  = event.scenePos()
            self._resize_start_rect = QRectF(self.rect())
            event.accept()
        else:
            self._resizing = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.scenePos() - self._resize_start_pos
            new_w = max(50, self._resize_start_rect.width()  + delta.x())
            new_h = max(24, self._resize_start_rect.height() + delta.y())
            self.setRect(0, 0, new_w, new_h)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)


class DraggableTextItem(QGraphicsTextItem):
    """
    A movable, selectable, double-click-editable text item.
    Three independently controllable style axes:
      • color  — any QColor via set_text_color()
      • size   — point size 6–96 via set_font_size()
      • weight — nine levels (Thin→Black) via set_thickness()

    _apply_formatting() uses a two-layer approach so all three properties
    survive repeated edits, paste operations, and inline editing sessions:

      Layer 1  setFont / setDefaultTextColor  — covers brand-new unstyled items.
      Layer 2  cursor.setCharFormat() with a FRESH QTextCharFormat built from
               scratch — stamps every existing character, wiping stale per-char
               overrides.  We NEVER read-modify-write cursor.charFormat() because
               that returns an incomplete merged object.
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
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable   |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsTextItem.GraphicsItemFlag.ItemSendsGeometryChanges,
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()


    def _build_font(self) -> QFont:
        """Construct a QFont from the current size + weight state."""
        font = QFont("Courier New", self._font_size)
        font.setWeight(self._WEIGHT_QFONT.get(self._weight_val, QFont.Weight.Bold))
        return font

    def _apply_formatting(self):
        """Stamp color, size, and weight onto the item and every character."""
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
        """Return the CSS font-weight integer for HTML export."""
        return self.WEIGHT_CSS.get(self._weight_val, 700)


    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self._apply_formatting()
        super().focusOutEvent(event)


class DarkCanvasView(QGraphicsView):
    SCENE_W   = 1000
    SCENE_H   = 700
    GRID_STEP = 24

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
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._box_counter  = 0
        self._text_counter = 0
        self._z_counter    = 0

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        step = self.GRID_STEP

        dim_pen    = QPen(QColor("#f0f0f0"), 1)
        bright_pen = QPen(QColor("#dddddd"), 1)

        x = int(rect.left()) - (int(rect.left()) % step)
        while x <= rect.right():
            painter.setPen(bright_pen if (x // step) % 6 == 0 else dim_pen)
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += step

        y = int(rect.top()) - (int(rect.top()) % step)
        while y <= rect.bottom():
            painter.setPen(bright_pen if (y // step) % 6 == 0 else dim_pen)
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += step

    def add_box(self):
        offset = (self._box_counter * 24) % 192
        item   = StyledRectItem(60 + offset, 60 + offset)
        item.setZValue(self._z_counter)
        self._z_counter += 1
        self.scene.addItem(item)
        self._box_counter += 1

    def add_text(self):
        offset = (self._text_counter * 24) % 192
        label  = f"BLOCK_{self._text_counter + 1:02d}"
        item   = DraggableTextItem(label, 80 + offset, 80 + offset)
        item.setZValue(self._z_counter)
        self._z_counter += 1
        self.scene.addItem(item)
        self._text_counter += 1

    def clear_canvas(self):
        self.scene.clear()
        self._box_counter  = 0
        self._text_counter = 0
        self._z_counter    = 0


def _h_rule() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


class PropertyInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item = None
        self._scene        = None

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
        root.addWidget(self._stack)


        self._layer_widget = self._build_layer_section()
        root.addWidget(self._layer_widget)
        self._layer_widget.setVisible(False)

        root.addStretch()
        self._show_empty()

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

        fill_lbl = QLabel("> FILL COLOR")
        fill_lbl.setObjectName("muted")
        layout.addWidget(fill_lbl)

        self.btn_rect_color = QPushButton("[ CHANGE ]")
        self.btn_rect_color.setObjectName("btn_color")
        self.btn_rect_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rect_color.clicked.connect(self._on_rect_color_click)
        layout.addWidget(self.btn_rect_color)
        layout.addWidget(_h_rule())

        radius_row = QHBoxLayout()
        radius_lbl = QLabel("> CORNER RAD")
        radius_lbl.setObjectName("muted")
        radius_row.addWidget(radius_lbl)
        radius_row.addStretch()
        self.lbl_radius_val = QLabel("0px")
        self.lbl_radius_val.setObjectName("muted")
        radius_row.addWidget(self.lbl_radius_val)
        layout.addLayout(radius_row)

        self.slider_radius = QSlider(Qt.Orientation.Horizontal)
        self.slider_radius.setRange(0, 60)
        self.slider_radius.setValue(0)
        self.slider_radius.valueChanged.connect(self._on_radius_change)
        layout.addWidget(self.slider_radius)
        layout.addWidget(_h_rule())

        geo_lbl = QLabel("> GEOMETRY")
        geo_lbl.setObjectName("muted")
        layout.addWidget(geo_lbl)

        self.lbl_rect_geometry = QLabel("--")
        self.lbl_rect_geometry.setObjectName("muted")
        self.lbl_rect_geometry.setWordWrap(True)
        layout.addWidget(self.lbl_rect_geometry)

        layout.addStretch()
        return page

    def _build_text_controls_page(self) -> QWidget:
        page   = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(10)


        color_lbl = QLabel("> TEXT COLOR")
        color_lbl.setObjectName("muted")
        layout.addWidget(color_lbl)

        self.btn_text_color = QPushButton("[ CHANGE ]")
        self.btn_text_color.setObjectName("btn_color")
        self.btn_text_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_text_color.clicked.connect(self._on_text_color_click)
        layout.addWidget(self.btn_text_color)
        layout.addWidget(_h_rule())


        size_row = QHBoxLayout()
        size_lbl = QLabel("> FONT SIZE")
        size_lbl.setObjectName("muted")
        size_row.addWidget(size_lbl)
        size_row.addStretch()
        self.lbl_size_val = QLabel("14pt")
        self.lbl_size_val.setObjectName("muted")
        size_row.addWidget(self.lbl_size_val)
        layout.addLayout(size_row)

        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(6, 96)
        self.slider_size.setValue(14)
        self.slider_size.setTickInterval(6)
        self.slider_size.valueChanged.connect(self._on_size_change)
        layout.addWidget(self.slider_size)
        layout.addWidget(_h_rule())


        thick_row = QHBoxLayout()
        thick_lbl = QLabel("> THICKNESS")
        thick_lbl.setObjectName("muted")
        thick_row.addWidget(thick_lbl)
        thick_row.addStretch()
        self.lbl_thick_val = QLabel("700")
        self.lbl_thick_val.setObjectName("muted")
        thick_row.addWidget(self.lbl_thick_val)
        layout.addLayout(thick_row)

        self.slider_thick = QSlider(Qt.Orientation.Horizontal)
        self.slider_thick.setRange(1, 9)
        self.slider_thick.setValue(7)
        self.slider_thick.valueChanged.connect(self._on_thick_change)
        layout.addWidget(self.slider_thick)
        layout.addWidget(_h_rule())


        geo_lbl = QLabel("> POSITION")
        geo_lbl.setObjectName("muted")
        layout.addWidget(geo_lbl)

        self.lbl_text_geometry = QLabel("--")
        self.lbl_text_geometry.setObjectName("muted")
        self.lbl_text_geometry.setWordWrap(True)
        layout.addWidget(self.lbl_text_geometry)

        layout.addStretch()
        return page

    def _build_layer_section(self) -> QWidget:
        """
        Shared layer-order panel that appears below the per-type controls
        whenever any item is selected.  Uses Qt's native zValue() — every
        button is a direct delta or an absolute repositioning relative to the
        current min/max z in the scene.
        """
        w      = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(_h_rule())


        hdr = QHBoxLayout()
        layer_lbl = QLabel("> LAYER ORDER")
        layer_lbl.setObjectName("muted")
        hdr.addWidget(layer_lbl)
        hdr.addStretch()
        self.lbl_layer_val = QLabel("Z: 0")
        self.lbl_layer_val.setObjectName("muted")
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
        top = max((it.zValue() for it in peers), default=0)
        self._current_item.setZValue(top + 1)
        self._update_layer_label()

    def _on_send_back(self):
        if not self._current_item:
            return
        peers = [it for it in (self._scene.items() if self._scene else [])
                 if it is not self._current_item]
        bottom = min((it.zValue() for it in peers), default=0)
        self._current_item.setZValue(bottom - 1)
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
        self._update_layer_label()
        self._layer_widget.setVisible(True)

    def clear(self):
        self._current_item = None
        self._scene        = None
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
            f"X:{pos.x():.0f} Y:{pos.y():.0f}  "
            f"W:{rect.width():.0f} H:{rect.height():.0f}"
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

    def _apply_swatch(self, btn: QPushButton, color: QColor):
        luminance = (
            0.299 * color.red() +
            0.587 * color.green() +
            0.114 * color.blue()
        )
        text_col = "#00E5FF" if luminance < 140 else "#000000"

        btn.setStyleSheet(
            f"QPushButton#btn_color {{"
            f"  background-color: {color.name()};"
            f"  color: {text_col};"
            f"  border-top:    2px solid #6a6a6a;"
            f"  border-left:   2px solid #6a6a6a;"
            f"  border-bottom: 2px solid #1a1a1a;"
            f"  border-right:  2px solid #1a1a1a;"
            f"  border-radius: 0px;"
            f"}}"
        )
        btn.setText(color.name().upper())

    def _on_rect_color_click(self):
        if not self._current_item: return
        color = QColorDialog.getColor(
            self._current_item.fill_color(), self, "CHOOSE FILL COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_item.set_fill_color(color)
            self._apply_swatch(self.btn_rect_color, color)

    def _on_text_color_click(self):
        if not self._current_item: return
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
        css_weight = DraggableTextItem.WEIGHT_CSS.get(value, value * 100)
        self.lbl_thick_val.setText(str(css_weight))
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
        widget.setFixedWidth(140)

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
        self.btn_clr = QPushButton("[X] CLEAR")
        self.btn_gen = QPushButton("[/] GENERATE")
        self.btn_exp = QPushButton("[S] EXPORT")

        self.btn_clr.setObjectName("btn_clear")
        self.btn_gen.setObjectName("btn_generate")

        for btn in (self.btn_box, self.btn_txt, self.btn_clr,
                    self.btn_gen, self.btn_exp):
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
        self.btn_box.clicked.connect(self.canvas.add_box)
        self.btn_txt.clicked.connect(self.canvas.add_text)
        self.btn_clr.clicked.connect(self._on_clear)
        self.btn_gen.clicked.connect(self._on_generate)
        self.btn_exp.clicked.connect(self._export_html)
        self.canvas.scene.selectionChanged.connect(self._on_selection)

    def _on_clear(self):
        self.canvas.clear_canvas()
        self.inspector.clear()
        self.code_editor.clear()
        self.preview_browser.clear()
        self._show_witty("CANVAS CLEARED. MEMORY WIPED.")

    def _on_selection(self):
        selected = self.canvas.scene.selectedItems()
        if len(selected) == 1 and isinstance(selected[0], (StyledRectItem, DraggableTextItem)):
            self.inspector.load_item(selected[0], self.canvas.scene)
        else:
            self.inspector.clear()

    def _on_generate(self):
        items = self.canvas.scene.items()
        if not items:
            self._show_witty("CANVAS EMPTY. ADD BLOCKS FIRST.")
            return

        shapes = []
        for it in items:
            if isinstance(it, StyledRectItem):
                shapes.append({
                    "type": "rect",
                    "x": it.x(),  "y": it.y(),
                    "w": it.rect().width(), "h": it.rect().height(),
                    "fill": it.fill_color().name(),
                    "rad":  it.border_radius(),
                    "z":    int(it.zValue()),
                })
            elif isinstance(it, DraggableTextItem):
                shapes.append({
                    "type":   "text",
                    "x":      it.x(), "y": it.y(),
                    "text":   it.toPlainText(),
                    "color":  it.text_color().name(),
                    "size":   it.font_size(),
                    "weight": it.thickness_css(),
                    "z":      int(it.zValue()),
                })

        shapes.sort(key=lambda s: s["z"])

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
            else:
                html.append(f'  <div id="{item_id}" class="canvas-item"></div>')
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" background-color: {shape['fill']};"
                    f" border-radius: {shape['rad']:.0f}px;"
                    f" border: 2px solid #000000;"
                    f" z-index: {shape['z']};"
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
