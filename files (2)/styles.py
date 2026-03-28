"""
DrawScript — styles.py
Global stylesheet, color tokens, and grid constant.
"""

GRID_STEP: int = 24

THEMES: dict = {
    "WHITE":     ("#ffffff", "#f0f0f0", "#dddddd", "#7B8EA8"),
    "DARK":      ("#111827", "#1f2937", "#374151", "#7B8EA8"),
    "BLUEPRINT": ("#1A365D", "#2A4365", "#2C5282", "#7B8EA8"),
}

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
    background: #3D4F63;             /* Brightened from #1E2A3A to be visible */
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

QLineEdit {
    background-color: #0A0E17;
    color: #A5D8FF;
    border: 2px solid #000000;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", "Lucida Console", monospace;
    font-size: 11px;
    font-weight: bold;
    padding: 4px 6px;
    selection-background-color: #1E3A5F;
    selection-color: #E8EAF0;
}

QLineEdit:focus {
    border: 2px solid #00E5FF;
    color: #E8EAF0;
}

QLineEdit:hover {
    border: 2px solid #253347;
}

QLineEdit[placeholderText] {
    color: #3D4F63;
}
"""
