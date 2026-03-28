"""
DrawScript — WHITE CANVAS EDITION  (v1.6)
Entry point.  Imports from:
  styles  → DARK_QSS
  items   → StyledRectItem, StyledEllipseItem, DraggableTextItem,
            DraggableImageItem, ButtonComponentItem
  widgets → DarkCanvasView, PropertyInspector, _h_rule

Changes in v1.6:
  - _build_right_panel: removed setFixedHeight(480) on the inspector.
    The inspector uses stretch=2 and the code/preview tabs stretch=1 so the
    property panel gets more vertical space; the inspector scrolls internally.
  - Save/load v6 adds per-item locked; v5 added opacity and shadow.
"""

import sys
import json
import random
import pathlib

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QGraphicsView, QLabel, QTextEdit,
    QTabWidget, QTextBrowser, QFileDialog, QStatusBar, QComboBox,
    QMessageBox, QSlider, QColorDialog, QProgressBar, QSplashScreen,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QColor, QPixmap, QPainter, QLinearGradient

from styles import DARK_QSS, THEMES
from items import (
    StyledRectItem, StyledEllipseItem,
    DraggableTextItem, DraggableImageItem,
    ButtonComponentItem, CanvasGroupItem, CanvasPathItem,
)
from widgets import DarkCanvasView, PropertyInspector, RulerWidget, _h_rule


# ---------------------------------------------------------------------------
# Keyboard-shortcuts mixin
# ---------------------------------------------------------------------------

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
        QShortcut(QKeySequence("Ctrl+D"),    self).activated.connect(self._duplicate_selected)
        QShortcut(QKeySequence("Ctrl+A"),    self).activated.connect(self._select_all)
        QShortcut(QKeySequence("Ctrl+G"),    self).activated.connect(self._toggle_grid)

        esc_sc = QShortcut(QKeySequence("Escape"), self)
        esc_sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
        esc_sc.activated.connect(self._on_escape)

        self.canvas.nudge_callback = self._show_witty

        if self.statusBar() is None:
            self.setStatusBar(QStatusBar())

        self._show_witty(
            "KEYBOARD INTERFACE ONLINE. CTRL+C/V/Z/D/A/E/G · DEL · ARROWS"
        )

    def _toggle_grid(self):
        self.canvas.toggle_grid()
        vis = "ON" if self.canvas._show_grid else "OFF"
        self._show_witty(f"CANVAS GRID {vis}.")

    # ── Copy ──────────────────────────────────────────────────────────

    def _copy_shape(self):
        selected = self.canvas.scene.selectedItems()
        if not selected:
            return
        item = selected[0]

        if isinstance(item, ButtonComponentItem):
            self._clipboard_shape_data = {
                "type":         "button_component",
                "w":            item.rect().width(), "h": item.rect().height(),
                "fill":         item.fill_color(),
                "rad":          item.border_radius(),
                "border_color": item.border_color(),
                "border_width": item.border_width(),
                "label":        item.label(),
                "label_color":  item.label_color(),
                "font_size":    item.label_font_size(),
                "link_url":     item.link_url(),
                "src_x":        item.x(), "src_y": item.y(),
            }
        elif isinstance(item, StyledRectItem):
            self._clipboard_shape_data = {
                "type":         "rect",
                "w":            item.rect().width(), "h": item.rect().height(),
                "fill":         item.fill_color(),
                "rad":          item.border_radius(),
                "border_color": item.border_color(),
                "border_width": item.border_width(),
                "link_url":     item.link_url(),
                "src_x":        item.x(), "src_y": item.y(),
            }
        elif isinstance(item, StyledEllipseItem):
            self._clipboard_shape_data = {
                "type":         "ellipse",
                "w":            item.rect().width(), "h": item.rect().height(),
                "fill":         item.fill_color(),
                "border_color": item.border_color(),
                "border_width": item.border_width(),
                "link_url":     item.link_url(),
                "src_x":        item.x(), "src_y": item.y(),
            }
        elif isinstance(item, DraggableTextItem):
            self._clipboard_shape_data = {
                "type":     "text",
                "text":     item.toPlainText(), "color": item.text_color(),
                "size":     item.font_size(), "weight": item.thickness(),
                "link_url": item.link_url(),
                "src_x":    item.x(), "src_y": item.y(),
            }
        elif isinstance(item, DraggableImageItem):
            self._clipboard_shape_data = {
                "type":     "image",
                "path":     item.file_path(),
                "w":        item.img_width(), "h": item.img_height(),
                "link_url": item.link_url(),
                "src_x":    item.x(), "src_y": item.y(),
            }
        else:
            return
        self._show_witty("BLOCK COPIED TO BUFFER.")

    # ── Paste ─────────────────────────────────────────────────────────

    def _paste_shape(self):
        if not self._clipboard_shape_data:
            self._show_witty("BUFFER IS EMPTY.")
            return
        data   = self._clipboard_shape_data
        offset = 24
        ox, oy = data["src_x"] + offset, data["src_y"] + offset

        if data["type"] == "button_component":
            new_item = ButtonComponentItem(ox, oy, data["w"], data["h"], data["label"])
            new_item.set_fill_color(data["fill"])
            new_item.set_border_radius(data["rad"])
            new_item.set_border_color(data["border_color"])
            new_item.set_border_width(data["border_width"])
            new_item.set_label_color(data["label_color"])
            new_item.set_label_font_size(data["font_size"])
            new_item.set_link_url(data.get("link_url", ""))
        elif data["type"] == "rect":
            new_item = StyledRectItem(ox, oy, data["w"], data["h"])
            new_item.set_fill_color(data["fill"])
            new_item.set_border_radius(data["rad"])
            new_item.set_border_color(data["border_color"])
            new_item.set_border_width(data["border_width"])
            new_item.set_link_url(data.get("link_url", ""))
        elif data["type"] == "ellipse":
            new_item = StyledEllipseItem(ox, oy, data["w"], data["h"])
            new_item.set_fill_color(data["fill"])
            new_item.set_border_color(data["border_color"])
            new_item.set_border_width(data["border_width"])
            new_item.set_link_url(data.get("link_url", ""))
        elif data["type"] == "text":
            new_item = DraggableTextItem(data["text"], ox, oy)
            new_item.set_text_color(data["color"])
            new_item.set_font_size(data["size"])
            new_item.set_thickness(data["weight"])
            new_item.set_link_url(data.get("link_url", ""))
        elif data["type"] == "image":
            new_item = DraggableImageItem(data["path"], ox, oy, data["w"], data["h"])
            new_item.set_link_url(data.get("link_url", ""))
        else:
            return
        self.canvas.scene.addItem(new_item)
        self._show_witty("BLOCK PASTED FROM BUFFER.")

    # ── Delete / Undo ─────────────────────────────────────────────────

    def _delete_selected(self):
        selected = self.canvas.scene.selectedItems()
        if not selected:
            return
        # Tag this action as a "delete" in the history
        self._undo_stack.append(("delete", list(selected)))
        for item in selected:
            self.canvas.scene.removeItem(item)
        count = len(selected)
        self._show_witty(
            f"{count} {'BLOCK' if count == 1 else 'BLOCKS'} DELETED. CTRL+Z TO RESTORE."
        )

    def _undo_delete(self):
        if not self._undo_stack:
            self._show_witty("NOTHING TO UNDO.")
            return

        entry = self._undo_stack.pop()

        # Handle the new tuple format, or fall back if the format is old
        if isinstance(entry, tuple) and len(entry) == 2:
            action, items = entry
        else:
            action, items = "delete", entry

        try:
            if action == "delete":
                # Undo a deletion: put the items back
                for item in items:
                    self.canvas.scene.addItem(item)
                self._show_witty(f"RESTORED {len(items)} BLOCK(S).")
            elif action == "add":
                # Undo an addition (e.g. drawing a stroke): remove the item
                for item in items:
                    self.canvas.scene.removeItem(item)
                self._show_witty("STROKE UNDONE AND REMOVED.")
        except RuntimeError:
            # Catch the C++ deletion crash gracefully
            self._show_witty("CANNOT UNDO. MEMORY WAS PERMANENTLY WIPED.")

    # ── Duplicate (Ctrl+D) ────────────────────────────────────────────

    def _duplicate_selected(self):
        selected = self.canvas.scene.selectedItems()
        if not selected:
            self._show_witty("NO BLOCKS SELECTED. NOTHING TO CLONE.")
            return

        OFFSET    = 24
        new_items = []

        for item in selected:
            new_item = None

            if isinstance(item, ButtonComponentItem):
                new_item = ButtonComponentItem(
                    item.x() + OFFSET, item.y() + OFFSET,
                    item.rect().width(), item.rect().height(),
                    item.label(),
                )
                new_item.set_fill_color(item.fill_color())
                new_item.set_border_radius(item.border_radius())
                new_item.set_border_color(item.border_color())
                new_item.set_border_width(item.border_width())
                new_item.set_label_color(item.label_color())
                new_item.set_label_font_size(item.label_font_size())
                new_item.set_link_url(item.link_url())

            elif isinstance(item, StyledRectItem):
                new_item = StyledRectItem(
                    item.x() + OFFSET, item.y() + OFFSET,
                    item.rect().width(), item.rect().height(),
                )
                new_item.set_fill_color(item.fill_color())
                new_item.set_border_radius(item.border_radius())
                new_item.set_border_color(item.border_color())
                new_item.set_border_width(item.border_width())
                new_item.set_link_url(item.link_url())

            elif isinstance(item, StyledEllipseItem):
                new_item = StyledEllipseItem(
                    item.x() + OFFSET, item.y() + OFFSET,
                    item.rect().width(), item.rect().height(),
                )
                new_item.set_fill_color(item.fill_color())
                new_item.set_border_color(item.border_color())
                new_item.set_border_width(item.border_width())
                new_item.set_link_url(item.link_url())

            elif isinstance(item, DraggableTextItem):
                new_item = DraggableTextItem(
                    item.toPlainText(),
                    item.x() + OFFSET, item.y() + OFFSET,
                )
                new_item.set_text_color(item.text_color())
                new_item.set_font_size(item.font_size())
                new_item.set_thickness(item.thickness())
                new_item.set_link_url(item.link_url())

            elif isinstance(item, DraggableImageItem):
                new_item = DraggableImageItem(
                    item.file_path(),
                    item.x() + OFFSET, item.y() + OFFSET,
                    item.img_width(), item.img_height(),
                )
                new_item.set_link_url(item.link_url())

            if new_item is not None:
                new_item.setZValue(self.canvas._z_counter)
                self.canvas._z_counter += 1
                new_items.append(new_item)

        self.canvas.scene.clearSelection()
        for new_item in new_items:
            self.canvas.scene.addItem(new_item)
            new_item.setSelected(True)

        self._show_witty(
            f"SELECTION CLONED. {len(new_items)} BLOCK(S) OFFSET +{OFFSET}PX."
        )

    # ── Select All (Ctrl+A) ───────────────────────────────────────────

    def _select_all(self):
        items = self.canvas.scene.items()
        if not items:
            self._show_witty("CANVAS IS EMPTY. NOTHING TO SELECT.")
            return
        for item in items:
            item.setSelected(True)
        count = len(self.canvas.scene.selectedItems())
        self._show_witty(f"ALL {count} BLOCK(S) SELECTED. FULL MANIFEST ACQUIRED.")

    # ── Escape ────────────────────────────────────────────────────────

    def _on_escape(self):
        scene = self.canvas.scene

        editing = [
            it for it in scene.items()
            if isinstance(it, DraggableTextItem)
            and it.textInteractionFlags() != Qt.TextInteractionFlag.NoTextInteraction
        ]

        if editing:
            for it in editing:
                it.clearFocus()
            self._show_witty("TEXT EDIT COMMITTED. HIT ESC AGAIN TO DESELECT.")
        else:
            scene.clearSelection()
            self._show_witty("SELECTION CLEARED. ALL BLOCKS DESELECTED.")

    # ── Status bar ────────────────────────────────────────────────────

    def _show_witty(self, message: str):
        prefix = random.choice(self._witty_prefixes)
        self.statusBar().showMessage(prefix + message, 3500)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class DarkMainWindow(QMainWindow, KeyboardShortcutsMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DRAWSCRIPT // WHITE CANVAS EDITION  v1.6")
        self.resize(1360, 760)
        self.setStatusBar(QStatusBar())

        toolbar_widget = self._build_toolbar()
        self.canvas    = DarkCanvasView()
        self.h_ruler   = RulerWidget(Qt.Orientation.Horizontal)
        self.v_ruler   = RulerWidget(Qt.Orientation.Vertical)
        self._canvas_zoom = 1.0
        canvas_frame = self._build_canvas_frame()
        self.combo_theme.blockSignals(True)
        self.combo_theme.setCurrentText(self.canvas._theme_key)
        self.combo_theme.blockSignals(False)
        right_panel    = self._build_right_panel()

        central     = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(toolbar_widget)
        main_layout.addWidget(canvas_frame, stretch=1)
        main_layout.addWidget(right_panel)
        self.setCentralWidget(central)

        self._wire_signals()
        self.setup_keyboard_shortcuts()

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("Toolbar")
        widget.setFixedWidth(160)   # slightly wider than v2.0 (was 148) to
                                    # accommodate slider + color swatch labels

        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 14, 10, 14)

        # ── [ CANVAS ] ───────────────────────────────────────────────
        section_lbl = QLabel("[ CANVAS ]")
        section_lbl.setObjectName("heading")
        layout.addWidget(section_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        self.btn_box    = QPushButton("[+] ADD BOX")
        self.btn_circle = QPushButton("[O] ADD CIRCLE")
        self.btn_txt    = QPushButton("[A] ADD TEXT")
        self.btn_img    = QPushButton("[+] ADD IMAGE")
        self.btn_brush  = QPushButton("[B] PEN MODE")
        self.btn_brush.setObjectName("btn_img")    # green styling
        self.btn_brush.setCheckable(True)
        self.btn_eraser = QPushButton("[E] ERASER")
        self.btn_eraser.setObjectName("btn_clear") # red hover
        self.btn_eraser.setCheckable(True)
        self.btn_group   = QPushButton("[G] GROUP")
        self.btn_ungroup = QPushButton("[U] UNGROUP")
        self.btn_clr     = QPushButton("[X] CLEAR")
        self.btn_gen     = QPushButton("[/] GENERATE")
        self.btn_exp     = QPushButton("[S] EXPORT")

        self.btn_img.setObjectName("btn_img")
        self.btn_clr.setObjectName("btn_clear")
        self.btn_gen.setObjectName("btn_generate")
        self.btn_ungroup.setObjectName("btn_clear")

        for btn in (self.btn_box, self.btn_circle, self.btn_txt, self.btn_img,
                    self.btn_brush, self.btn_eraser,
                    self.btn_group, self.btn_ungroup,
                    self.btn_clr, self.btn_gen, self.btn_exp):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        # ── [ PEN TOOL ] ─────────────────────────────────────────────
        # These controls set the *active* color and width that the NEXT stroke
        # will use.  They affect the live drawForeground() preview as well.
        layout.addSpacing(10)
        pen_lbl = QLabel("[ PEN TOOL ]")
        pen_lbl.setObjectName("heading")
        layout.addWidget(pen_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        # Pen Color swatch button
        self.btn_pen_color = QPushButton("[ PEN COLOR ]")
        self.btn_pen_color.setObjectName("btn_color")
        self.btn_pen_color.setCursor(Qt.CursorShape.PointingHandCursor)
        # Apply default swatch (#A5D8FF) immediately so it renders on launch
        self._apply_pen_color_to_btn(QColor("#A5D8FF"))
        layout.addWidget(self.btn_pen_color)

        # Pen Width slider + live value label
        pw_row = QHBoxLayout()
        pw_lbl = QLabel("> WIDTH")
        pw_lbl.setObjectName("muted")
        pw_row.addWidget(pw_lbl)
        pw_row.addStretch()
        self.lbl_pen_width_val = QLabel("2px")
        self.lbl_pen_width_val.setObjectName("muted")
        pw_row.addWidget(self.lbl_pen_width_val)
        layout.addLayout(pw_row)

        self.slider_pen_width = QSlider(Qt.Orientation.Horizontal)
        self.slider_pen_width.setRange(1, 30)
        self.slider_pen_width.setValue(2)
        self.slider_pen_width.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.slider_pen_width)

        # ── [ ERASER SIZE ] ───────────────────────────────────────────
        layout.addSpacing(6)
        es_row = QHBoxLayout()
        es_lbl = QLabel("> ERASER SZ")
        es_lbl.setObjectName("muted")
        es_row.addWidget(es_lbl)
        es_row.addStretch()
        self.lbl_eraser_size_val = QLabel("20px")
        self.lbl_eraser_size_val.setObjectName("muted")
        es_row.addWidget(self.lbl_eraser_size_val)
        layout.addLayout(es_row)

        self.slider_eraser_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_eraser_size.setRange(4, 120)
        self.slider_eraser_size.setValue(20)
        self.slider_eraser_size.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.slider_eraser_size)

        # ── [ COMPONENTS ] ───────────────────────────────────────────
        layout.addSpacing(10)
        comp_lbl = QLabel("[ COMPONENTS ]")
        comp_lbl.setObjectName("heading")
        layout.addWidget(comp_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        self.btn_comp_button = QPushButton("[+] ADD BUTTON")
        self.btn_comp_button.setObjectName("btn_save")
        self.btn_comp_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_comp_button)

        # ── [ THEME ] ────────────────────────────────────────────────
        layout.addSpacing(10)
        theme_lbl = QLabel("[ THEME ]")
        theme_lbl.setObjectName("heading")
        layout.addWidget(theme_lbl)
        layout.addWidget(_h_rule())
        layout.addSpacing(4)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(list(THEMES.keys()))
        self.combo_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.combo_theme)

        # ── [ PROJECT ] ──────────────────────────────────────────────
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

    # ── Helper for pen-color swatch ───────────────────────────────────────────

    def _apply_pen_color_to_btn(self, color: QColor):
        """
        Renders the pen-color swatch on btn_pen_color.
        Mirrors the PropertyInspector._apply_swatch() pattern.
        Uses perceived luminance to choose readable text (black or white).
        """
        lum = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
        fg  = "#000000" if lum > 127 else "#ffffff"
        self.btn_pen_color.setStyleSheet(
            f"QPushButton#btn_color {{"
            f" background-color: {color.name()};"
            f" color: {fg};"
            f" border-top: 2px solid #000000;"
            f" border-left: 2px solid #000000;"
            f" border-right: 2px solid #000000;"
            f" border-bottom: 4px solid #000000;"
            f" border-radius: 4px;"
            f" font-family: 'Consolas', monospace;"
            f" font-size: 11px; font-weight: bold;"
            f" padding: 0 8px;"
            f"}}"
        )
        self.btn_pen_color.setText(color.name().upper())

    def _build_canvas_frame(self) -> QWidget:
        host = QWidget()
        grid = QGridLayout(host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        corner = QWidget()
        corner.setFixedSize(24, 24)
        corner.setStyleSheet("background-color: #111827; border-right: 1px solid #1f2937;")

        grid.addWidget(corner, 0, 0)
        grid.addWidget(self.h_ruler, 0, 1)
        grid.addWidget(self.v_ruler, 1, 0)
        grid.addWidget(self.canvas, 1, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)
        return host

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("RightPanel")
        panel.setFixedWidth(350)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.inspector = PropertyInspector()
        # No setFixedHeight — the QScrollArea inside PropertyInspector handles overflow.
        # stretch=2 gives the inspector more room than the tabs below.
        layout.addWidget(self.inspector, stretch=2)
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
        # stretch=1 so tabs use less vertical space than the property inspector.
        layout.addWidget(self.tabs, stretch=1)
        return panel

    def _wire_signals(self):
        # ── existing connections (unchanged) ─────────────────────────
        self.btn_box         .clicked.connect(self.canvas.add_box)
        self.btn_circle      .clicked.connect(self.canvas.add_circle)
        self.btn_txt         .clicked.connect(self.canvas.add_text)
        self.btn_img         .clicked.connect(self._on_add_image)
        self.btn_brush       .toggled.connect(self._toggle_brush_mode)
        self.btn_eraser      .toggled.connect(self._toggle_eraser_mode)
        self.btn_group       .clicked.connect(self._group_selected)
        self.btn_ungroup     .clicked.connect(self._ungroup_selected)
        self.btn_clr         .clicked.connect(self._on_clear)
        self.btn_gen         .clicked.connect(self._on_generate)
        self.btn_exp         .clicked.connect(self._export_html)
        self.btn_save        .clicked.connect(self._save_project)
        self.btn_open        .clicked.connect(self._open_project)
        self.btn_comp_button .clicked.connect(self.canvas.add_button_component)
        self.combo_theme.currentTextChanged.connect(self._on_theme_changed)
        self.canvas.scene.selectionChanged.connect(self._on_selection)
        self.canvas.zoomChanged.connect(self._on_canvas_zoom_changed)
        self.canvas.scrollChanged.connect(self._on_canvas_scroll_changed)
        self.inspector.status_callback = self._show_witty
        self._on_canvas_scroll_changed(
            self.canvas.horizontalScrollBar().value(),
            self.canvas.verticalScrollBar().value(),
        )

        # ── NEW: Active Pen Tool controls (Feature 1) ─────────────────
        self.btn_pen_color.clicked.connect(self._on_pen_color_click)
        self.slider_pen_width.valueChanged.connect(self._on_pen_width_change)

        # ── NEW: Eraser size slider (Feature 2) ──────────────────────
        self.slider_eraser_size.valueChanged.connect(self._on_eraser_size_change)

    # ── New slot: pen color picker ────────────────────────────────────────────

    def _on_pen_color_click(self):
        """Open a color picker; update both canvas state and swatch button."""
        color = QColorDialog.getColor(
            self.canvas._pen_color,
            self,
            "CHOOSE PEN COLOR",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self.canvas.set_pen_color(color)
            self._apply_pen_color_to_btn(color)
            self._show_witty(f"PEN COLOR SET: {color.name().upper()}")

    # ── New slot: pen width slider ────────────────────────────────────────────

    def _on_pen_width_change(self, value: int):
        self.lbl_pen_width_val.setText(f"{value}px")
        self.canvas.set_pen_width(float(value))

    # ── New slot: eraser size slider ──────────────────────────────────────────

    def _on_eraser_size_change(self, value: int):
        self.lbl_eraser_size_val.setText(f"{value}px")
        self.canvas.set_eraser_size(float(value))

    # ── Tool Toggle Handlers ──────────────────────────────────────────────────

    def _toggle_brush_mode(self, active: bool):
        self.canvas.set_brush_mode(active)
        if active:
            # Turn off Eraser Mode if it's currently on
            if hasattr(self, 'btn_eraser') and self.btn_eraser.isChecked():
                self.btn_eraser.setChecked(False)
            self._show_witty("PEN MODE ACTIVATED. DRAW FREELY ON THE CANVAS.")
            # Connect the signal so we catch the points when the mouse is released
            self.canvas.stroke_completed.connect(self._on_stroke_completed)
        else:
            self._show_witty("PEN MODE DEACTIVATED. BACK TO COMPOSITION MODE.")
            try:
                self.canvas.stroke_completed.disconnect(self._on_stroke_completed)
            except TypeError:
                pass

    def _toggle_eraser_mode(self, active: bool):
        self.canvas.set_eraser_mode(active)
        if active:
            # Turn off Pen Mode if it's currently on
            if hasattr(self, 'btn_brush') and self.btn_brush.isChecked():
                self.btn_brush.setChecked(False)
            self._show_witty("ERASER ACTIVE. SWIPE TO CUT STROKES OR DELETE BLOCKS.")
        else:
            self._show_witty("ERASER DEACTIVATED.")

    # ── Stroke completed callback ─────────────────────────────────────────────

    def _on_stroke_completed(self, points: list):
        """
        Called when the user lifts the mouse after a freehand stroke.
        Converts the QPointF list to tuples, builds a CanvasPathItem, and
        applies the *currently active* pen color + width from the canvas.
        """
        if len(points) < 2:
            return

        point_tuples = [(pt.x(), pt.y()) for pt in points]

        path_item = CanvasPathItem(point_tuples)

        # Apply active tool state (Feature 1)
        path_item.set_stroke_color(self.canvas._pen_color)
        path_item.set_stroke_width(self.canvas._pen_width)

        path_item.setZValue(self.canvas._z_counter)
        self.canvas._z_counter += 1

        self.canvas.scene.addItem(path_item)
        self._undo_stack.append(("add", [path_item]))   # Tags action so Ctrl+Z removes it
        self._show_witty(
            f"STROKE CREATED. PTS: {len(point_tuples)} "
            f"| COLOR: {self.canvas._pen_color.name().upper()} "
            f"| WIDTH: {self.canvas._pen_width:.0f}PX."
        )

    def _on_canvas_zoom_changed(self, zoom: float):
        self._canvas_zoom = max(0.01, float(zoom))
        self._on_canvas_scroll_changed(
            self.canvas.horizontalScrollBar().value(),
            self.canvas.verticalScrollBar().value(),
        )

    def _on_canvas_scroll_changed(self, x: int, y: int):
        self.h_ruler.set_view_state(x, self._canvas_zoom)
        self.v_ruler.set_view_state(y, self._canvas_zoom)

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

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

    def _on_theme_changed(self, name: str):
        self.canvas.set_theme(name)

    def _on_clear(self):
        self.canvas.clear_canvas()
        self.inspector.clear()
        self.code_editor.clear()
        self.preview_browser.clear()
        self._undo_stack.clear()  # Wipes the undo history to prevent stale-pointer crashes
        self._show_witty("CANVAS CLEARED. MEMORY WIPED.")

    def _group_selected(self):
        selected = [
            it for it in self.canvas.scene.selectedItems()
            if isinstance(it, (StyledRectItem, StyledEllipseItem, DraggableTextItem,
                               DraggableImageItem, ButtonComponentItem))
            and it.parentItem() is None
        ]
        if len(selected) < 2:
            self._show_witty("GROUP NEEDS 2+ TOP-LEVEL ITEMS.")
            return

        min_x = min(it.sceneBoundingRect().left() for it in selected)
        min_y = min(it.sceneBoundingRect().top() for it in selected)
        group = CanvasGroupItem(selected, min_x, min_y)
        group.setZValue(self.canvas._z_counter)
        self.canvas._z_counter += 1
        self.canvas.scene.addItem(group)
        self.canvas.scene.clearSelection()
        group.setSelected(True)
        self._show_witty(f"GROUP FORMED. {len(selected)} ITEMS BOUND.")

    def _ungroup_selected(self):
        """Dissolves the selected group and returns children to the scene."""
        selected = self.canvas.scene.selectedItems()
        if not selected or not isinstance(selected[0], CanvasGroupItem):
            self._show_witty("SELECT A GROUP BLOCK TO DISMANTLE THE SYNDICATE.")
            return

        group = selected[0]
        # IMPORTANT: Create a local list copy because childItems() updates live
        children = list(group.childItems())

        for it in children:
            # 1. Capture the absolute scene position BEFORE detaching
            scene_pos = it.scenePos()

            # 2. Break the bond with the group
            it.setParentItem(None)

            # 3. Explicitly add the item back to the main scene
            self.canvas.scene.addItem(it)

            # 4. Restore the position and selection
            it.setPos(scene_pos)
            it.setSelected(True)

        # 5. Safe removal of the empty container
        self.canvas.scene.removeItem(group)
        self._show_witty(f"SYNDICATE DISMANTLED. {len(children)} BLOCKS SET FREE.")

    def _on_selection(self):
        selected = self.canvas.scene.selectedItems()
        if len(selected) == 1 and isinstance(
            selected[0], (StyledRectItem, StyledEllipseItem,
                          DraggableTextItem, DraggableImageItem,
                          ButtonComponentItem)
        ):
            self.inspector.load_item(selected[0], self.canvas.scene)
        elif len(selected) >= 2:
            self.inspector.load_multi_select(selected, self.canvas.scene)
            self._show_witty(f"{len(selected)} BLOCKS IN SELECTION. ALIGNMENT MODE ACTIVE.")
        else:
            self.inspector.clear()

    # ------------------------------------------------------------------
    # HTML generation
    # ------------------------------------------------------------------

    @staticmethod
    def _link_wrap(inner_html: str, url: str) -> str:
        if url:
            return (
                f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'style="display:contents; text-decoration:none;">'
                f'{inner_html}</a>'
            )
        return inner_html

    def _on_generate(self):
        items = self.canvas.scene.items()
        if not items:
            self._show_witty("CANVAS EMPTY. ADD BLOCKS FIRST.")
            return

        html_map = {
            ButtonComponentItem: lambda it: {
                "type":         "button_component",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(),
                "rad":          it.border_radius(),
                "border_color": it.border_color().name(),
                "border_width": it.border_width(),
                "label":        it.label(),
                "label_color":  it.label_color().name(),
                "font_size":    it.label_font_size(),
                "url":          it.link_url(),
                "z":            int(it.zValue()),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
            },
            StyledRectItem: lambda it: {
                "type":         "rect",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(),
                "rad":          it.border_radius(),
                "border_color": it.border_color().name(),
                "border_width": it.border_width(),
                "url":          it.link_url(),
                "z":            int(it.zValue()),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
            },
            StyledEllipseItem: lambda it: {
                "type":         "ellipse",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(),
                "border_color": it.border_color().name(),
                "border_width": it.border_width(),
                "url":          it.link_url(),
                "z":            int(it.zValue()),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
            },
            DraggableTextItem: lambda it: {
                "type":   "text",
                "x":      it.x(), "y": it.y(),
                "text":   it.toPlainText(),
                "color":  it.text_color().name(),
                "size":   it.font_size(),
                "weight": it.thickness_css(),
                "url":    it.link_url(),
                "z":      int(it.zValue()),
                "opacity": it.opacity(),
                "shadow":       dict(it._shadow_data),
            },
            DraggableImageItem: lambda it: {
                "type": "image",
                "x":    it.x(), "y": it.y(),
                "w":    it.img_width(), "h": it.img_height(),
                "path": it.file_path(),
                "url":  it.link_url(),
                "z":    int(it.zValue()),
                "opacity": it.opacity(),
                "shadow":       dict(it._shadow_data),
            },
            CanvasPathItem: lambda it: {
                "type": "path",
                "x": it.x(), "y": it.y(),
                "bx": it.boundingRect().x(), "by": it.boundingRect().y(),
                "bw": it.boundingRect().width(), "bh": it.boundingRect().height(),
                "d": it.path_to_svg_d(),
                "stroke": it.stroke_color().name(),
                "stroke_width": it.stroke_width(),
                "url": it.link_url(),
                "z": int(it.zValue()),
                "opacity": it.opacity(),
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
            ".canvas-item { position: absolute; box-sizing: border-box; }",
        ]
        html = ['<div class="drawscript-canvas">']

        for idx, shape in enumerate(shapes):
            item_id = f"item-{idx}"
            url     = shape.get("url", "")

            shadow_css = ""
            _sd = shape.get("shadow", {})
            if _sd.get("enabled"):
                _c = QColor(_sd["color"])
                _cblr = int(_sd["blur"]) * 2  # Conversion factor for visual match
                shadow_css = (
                    f" box-shadow: {_sd['x']}px {_sd['y']}px {_cblr}px "
                    f"rgba({_c.red()},{_c.green()},{_c.blue()},{_c.alpha()/255:.2f});"
                )

            if shape["type"] == "text":
                inner = f'<div id="{item_id}" class="canvas-item">{shape["text"]}</div>'
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" font-size: {shape['size']}pt; font-weight: {shape['weight']};"
                    f" color: {shape['color']}; white-space: nowrap; z-index: {shape['z']};"
                    f" opacity: {shape['opacity']:.2f};"
                    f"{shadow_css}"
                    f"}}"
                )
                html.append(f"  {self._link_wrap(inner, url)}")

            elif shape["type"] == "rect":
                inner = f'<div id="{item_id}" class="canvas-item"></div>'
                bw    = shape["border_width"]
                bc    = shape["border_color"]
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" background-color: {shape['fill']};"
                    f" border-radius: {shape['rad']:.0f}px;"
                    f" border: {bw}px solid {bc}; z-index: {shape['z']};"
                    f" opacity: {shape['opacity']:.2f};"
                    f"{shadow_css}"
                    f"}}"
                )
                html.append(f"  {self._link_wrap(inner, url)}")

            elif shape["type"] == "ellipse":
                inner = f'<div id="{item_id}" class="canvas-item"></div>'
                bw    = shape["border_width"]
                bc    = shape["border_color"]
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" background-color: {shape['fill']};"
                    f" border-radius: 50%;"
                    f" border: {bw}px solid {bc}; z-index: {shape['z']};"
                    f" opacity: {shape['opacity']:.2f};"
                    f"{shadow_css}"
                    f"}}"
                )
                html.append(f"  {self._link_wrap(inner, url)}")

            elif shape["type"] == "button_component":
                # Generates a semantic <button> element — production-ready output
                inner = (
                    f'<button id="{item_id}" class="canvas-item">'
                    f'{shape["label"]}</button>'
                )
                bw = shape["border_width"]
                bc = shape["border_color"]
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" background-color: {shape['fill']};"
                    f" border-radius: {shape['rad']:.0f}px;"
                    f" border: {bw}px solid {bc};"
                    f" color: {shape['label_color']};"
                    f" font-size: {shape['font_size']}pt;"
                    f" font-family: 'Consolas', 'Courier New', monospace;"
                    f" font-weight: bold; cursor: pointer;"
                    f" padding: 0; z-index: {shape['z']};"
                    f" opacity: {shape['opacity']:.2f};"
                    f"{shadow_css}"
                    f"}}"
                    f" #{item_id}:hover {{ filter: brightness(1.1); }}"
                    f" #{item_id}:active {{ transform: translateY(1px); }}"
                )
                html.append(f"  {self._link_wrap(inner, url)}")

            elif shape["type"] == "image":
                abs_uri = pathlib.Path(shape["path"]).as_uri()
                inner   = f'<img id="{item_id}" class="canvas-item" src="{abs_uri}" alt="">'
                css.append(
                    f"#{item_id} {{"
                    f" left: {shape['x']:.0f}px; top: {shape['y']:.0f}px;"
                    f" width: {shape['w']:.0f}px; height: {shape['h']:.0f}px;"
                    f" display: block; z-index: {shape['z']};"
                    f" opacity: {shape['opacity']:.2f};"
                    f"{shadow_css}"
                    f"}}"
                )
                html.append(f"  {self._link_wrap(inner, url)}")

            elif shape["type"] == "path":
                abs_x = int(shape["x"] + shape["bx"])
                abs_y = int(shape["y"] + shape["by"])
                bw    = int(shape["bw"])
                bh    = int(shape["bh"])
                svg_html = (
                    f'<svg id="{item_id}" '
                    f'viewBox="{shape["bx"]} {shape["by"]} {bw} {bh}" '
                    f'class="canvas-item" '
                    f'style="left: {abs_x}px; top: {abs_y}px; '
                    f'width: {bw}px; height: {bh}px; z-index: {shape["z"]}; '
                    f'opacity: {shape["opacity"]:.2f};">\n'
                    f'  <path d="{shape["d"]}" stroke="{shape["stroke"]}" '
                    f'stroke-width="{shape["stroke_width"]}" fill="none" '
                    f'stroke-linecap="round" stroke-linejoin="round" />\n'
                    f'</svg>'
                )
                html.append(f"  {self._link_wrap(svg_html, url)}")

        html.append("</div>")
        final_html = (
            "<!DOCTYPE html>\n<html>\n<head>\n"
            f"<style>\n{chr(10).join(css)}\n</style>\n"
            f"</head>\n<body>\n{chr(10).join(html)}\n</body>\n</html>"
        )

        self.code_editor.setPlainText(final_html)
        self.preview_browser.setHtml(final_html)
        self._show_witty(f"COMPILED {len(shapes)} BLOCK(S). OUTPUT READY.")

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

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
            ButtonComponentItem: lambda it: {
                "type":         "button_component",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(QColor.NameFormat.HexArgb),
                "radius":       it.border_radius(),
                "border_color": it.border_color().name(QColor.NameFormat.HexArgb),
                "border_width": it.border_width(),
                "label":        it.label(),
                "label_color":  it.label_color().name(QColor.NameFormat.HexArgb),
                "font_size":    it.label_font_size(),
                "link_url":     it.link_url(),
                "z":            it.zValue(),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
                "locked":       it.locked(),
            },
            StyledRectItem: lambda it: {
                "type":         "rect",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(QColor.NameFormat.HexArgb),
                "radius":       it.border_radius(),
                "border_color": it.border_color().name(QColor.NameFormat.HexArgb),
                "border_width": it.border_width(),
                "link_url":     it.link_url(),
                "z":            it.zValue(),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
                "locked":       it.locked(),
            },
            StyledEllipseItem: lambda it: {
                "type":         "ellipse",
                "x":            it.x(), "y": it.y(),
                "w":            it.rect().width(), "h": it.rect().height(),
                "fill":         it.fill_color().name(QColor.NameFormat.HexArgb),
                "border_color": it.border_color().name(QColor.NameFormat.HexArgb),
                "border_width": it.border_width(),
                "link_url":     it.link_url(),
                "z":            it.zValue(),
                "opacity":      it.opacity(),
                "shadow":       dict(it._shadow_data),
                "locked":       it.locked(),
            },
            DraggableTextItem: lambda it: {
                "type":     "text",
                "x":        it.x(), "y": it.y(),
                "text":     it.toPlainText(),
                "color":    it.text_color().name(QColor.NameFormat.HexArgb),
                "size":     it.font_size(),
                "weight":   it.thickness(),
                "link_url": it.link_url(),
                "z":        it.zValue(),
                "opacity":  it.opacity(),
                "shadow":       dict(it._shadow_data),
                "locked":       it.locked(),
            },
            DraggableImageItem: lambda it: {
                "type":     "image",
                "x":        it.x(), "y": it.y(),
                "w":        it.img_width(), "h": it.img_height(),
                "path":     it.file_path(),
                "link_url": it.link_url(),
                "z":        it.zValue(),
                "opacity":  it.opacity(),
                "shadow":       dict(it._shadow_data),
                "locked":       it.locked(),
            },
        }
        save_map[CanvasPathItem] = lambda it: {
            "type":         "path",
            "x":            it.x(),
            "y":            it.y(),
            "points":       it.get_path_elements_for_save(),
            "stroke_color": it.stroke_color().name(QColor.NameFormat.HexArgb),
            "stroke_width": it.stroke_width(),
            "z":            it.zValue(),
            "opacity":      it.opacity(),
            "locked":       it.locked(),
            "shadow":       dict(it._shadow_data),
            "link_url":     it.link_url(),
        }

        payload = [save_map[type(it)](it) for it in items if type(it) in save_map]

        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"version": 8, "items": payload}, fh, indent=2)
            self._show_witty(
                f"PROJECT ARCHIVED TO DISK. {len(payload)} BLOCK(S) COMMITTED."
            )
        except OSError as exc:
            self._show_witty(f"WRITE FAILED: {exc}")

    def _load_item_entry(self, entry: dict):
        kind = entry.get("type")

        if kind == "button_component":
            item = ButtonComponentItem(
                entry["x"], entry["y"],
                entry.get("w", 160), entry.get("h", 48),
                entry.get("label", "CLICK ME"),
            )
            c = QColor(entry.get("fill", "#FFD166"))
            if c.isValid():
                item.set_fill_color(c)
            item.set_border_radius(entry.get("radius", 8))
            bc = QColor(entry.get("border_color", "#000000"))
            if bc.isValid():
                item.set_border_color(bc)
            item.set_border_width(entry.get("border_width", 3))
            lc = QColor(entry.get("label_color", "#000000"))
            if lc.isValid():
                item.set_label_color(lc)
            item.set_label_font_size(entry.get("font_size", 13))
            item.set_link_url(entry.get("link_url", ""))
            self.canvas._box_counter += 1

        elif kind == "rect":
            item = StyledRectItem(entry["x"], entry["y"], entry["w"], entry["h"])
            c = QColor(entry["fill"])
            if c.isValid():
                item.set_fill_color(c)
            item.set_border_radius(entry.get("radius", 0))
            bc = QColor(entry.get("border_color", "#000000"))
            if bc.isValid():
                item.set_border_color(bc)
            item.set_border_width(entry.get("border_width", 2))
            item.set_link_url(entry.get("link_url", ""))
            self.canvas._box_counter += 1

        elif kind == "ellipse":
            item = StyledEllipseItem(entry["x"], entry["y"], entry["w"], entry["h"])
            c = QColor(entry["fill"])
            if c.isValid():
                item.set_fill_color(c)
            bc = QColor(entry.get("border_color", "#000000"))
            if bc.isValid():
                item.set_border_color(bc)
            item.set_border_width(entry.get("border_width", 2))
            item.set_link_url(entry.get("link_url", ""))
            self.canvas._box_counter += 1

        elif kind == "text":
            item = DraggableTextItem(entry["text"], entry["x"], entry["y"])
            c = QColor(entry["color"])
            if c.isValid():
                item.set_text_color(c)
            item.set_font_size(entry.get("size", 14))
            item.set_thickness(entry.get("weight", 7))
            item.set_link_url(entry.get("link_url", ""))
            self.canvas._text_counter += 1

        elif kind == "image":
            item = DraggableImageItem(
                entry.get("path", ""), entry["x"], entry["y"],
                entry.get("w", 192), entry.get("h", 144),
            )
            item.set_link_url(entry.get("link_url", ""))
            self.canvas._image_counter += 1

        elif kind == "path":
            raw_pts = entry.get("points", [])
            if len(raw_pts) < 2:
                return None          # corrupt / degenerate entry — skip silently

            # Reconstruct the QPainterPath directly from saved [x, y] pairs.
            # We do NOT call _build_path_from_points() because the saved points
            # are *already* RDP-simplified; running simplification again would
            # lose even more detail.
            from PyQt6.QtGui import QPainterPath as _QPP
            from PyQt6.QtCore import QPointF as _QP

            rebuilt = _QPP(_QP(raw_pts[0][0], raw_pts[0][1]))
            for px, py in raw_pts[1:]:
                rebuilt.lineTo(_QP(px, py))

            item = CanvasPathItem()           # __init__(points=None)
            item._painter_path = rebuilt
            item.setPos(entry.get("x", 0.0), entry.get("y", 0.0))

            sc = QColor(entry.get("stroke_color", "#A5D8FF"))
            if sc.isValid():
                item.set_stroke_color(sc)

            item.set_stroke_width(entry.get("stroke_width", 2.0))
            item.set_link_url(entry.get("link_url", ""))

            # Standard mixin state
            saved_shadow = entry.get("shadow")
            if saved_shadow:
                item._shadow_data.update(saved_shadow)
                item.apply_shadow()
            item.set_opacity(entry.get("opacity", 1.0))
            item.set_locked(entry.get("locked", False))
            item.setZValue(entry.get("z", 0))
            return item

        else:
            return None

        saved_shadow = entry.get("shadow")
        if saved_shadow:
            item._shadow_data.update(saved_shadow)
            item.apply_shadow()

        item.set_opacity(entry.get("opacity", 1.0))
        item.set_locked(entry.get("locked", False))
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

        self.canvas._z_counter = int(
            max((e.get("z", 0) for e in items_data), default=0)
        ) + 1
        self._show_witty(
            f"DESIGN LOADED FROM ARCHIVE. {len(items_data)} BLOCK(S) RESTORED."
        )

    # ------------------------------------------------------------------
    # HTML export
    # ------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# SplashWindow  (v2.0 Startup Experience)
# ---------------------------------------------------------------------------

class SplashWindow(QWidget):
    """
    Animated splash screen shown on application startup.
    Displays branding, version, and a loading progress bar,
    then fades out and launches the main window.
    """

    def __init__(self, on_done):
        super().__init__()
        self._on_done = on_done
        self._progress_val = 0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(640, 360)

        # Centre on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

        # ── Layout ──────────────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 36)
        root.setSpacing(0)

        # Top wordmark
        title = QLabel("DRAWSCRIPT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-family: 'Consolas', monospace;"
            "font-size: 52px; font-weight: 900;"
            "color: #00E5FF; letter-spacing: 10px;"
        )
        root.addWidget(title)

        # Subtitle
        sub = QLabel("WHITE CANVAS EDITION  //  v2.0")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            "font-family: 'Consolas', monospace;"
            "font-size: 13px; color: #7B8EA8; letter-spacing: 4px;"
            "margin-top: -6px;"
        )
        root.addWidget(sub)

        root.addStretch(1)

        # Status line
        self._status_lbl = QLabel("INITIALIZING VECTOR ENGINE...")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(
            "font-family: 'Consolas', monospace;"
            "font-size: 11px; color: #4B5E7A; letter-spacing: 2px;"
        )
        root.addWidget(self._status_lbl)
        root.addSpacing(8)

        # Progress bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(4)
        self._bar.setStyleSheet(
            "QProgressBar {"
            "  background: #1B2333;"
            "  border: none; border-radius: 2px;"
            "}"
            "QProgressBar::chunk {"
            "  background: qlineargradient("
            "    x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #00B4D8, stop:1 #00E5FF"
            "  );"
            "  border-radius: 2px;"
            "}"
        )
        root.addWidget(self._bar)
        root.addSpacing(6)

        # Copyright footer
        footer = QLabel("© DRAWSCRIPT PROJECT — VECTOR INK ENGINE")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "font-family: 'Consolas', monospace;"
            "font-size: 10px; color: #2E3D52; letter-spacing: 1px;"
        )
        root.addWidget(footer)

        # ── Opacity effect for the fade-out ──────────────────────────
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(600)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_anim.finished.connect(self._finish)

        # ── Progress sequence timers ──────────────────────────────────
        _STEPS = [
            (120,  20, "LOADING STYLE ENGINE..."),
            (240,  45, "MOUNTING CANVAS WIDGETS..."),
            (400,  65, "WIRING SIGNAL BUSES..."),
            (560,  80, "COMPILING INK RENDERER..."),
            (720, 100, "READY."),
        ]
        for delay, val, msg in _STEPS:
            QTimer.singleShot(delay, lambda v=val, m=msg: self._step(v, m))

        # Start fade-out shortly after the bar completes
        QTimer.singleShot(980, self._start_fade)

    def _step(self, value: int, message: str):
        self._bar.setValue(value)
        self._status_lbl.setText(message)

    def _start_fade(self):
        self._fade_anim.start()

    def _finish(self):
        self.close()
        self._on_done()

    def paintEvent(self, event):
        """Dark rounded background with a subtle top-glow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark background panel
        painter.setBrush(QColor("#0D1117"))
        painter.setPen(QColor("#1E3A5F"))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

        # Subtle cyan top-glow
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor(0, 229, 255, 0))
        grad.setColorAt(0.5, QColor(0, 229, 255, 40))
        grad.setColorAt(1.0, QColor(0, 229, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        from PyQt6.QtGui import QBrush
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, 30), 12, 12)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    def _launch_main():
        window = DarkMainWindow()
        window.show()
        # Keep a reference so Python does not garbage-collect the window
        app._main_window = window

    splash = SplashWindow(on_done=_launch_main)
    splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()