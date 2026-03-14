import sys
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QSpacerItem, QSizePolicy, QFileDialog, QFrame,
                             QGridLayout, QGraphicsOpacityEffect)
from PyQt6.QtGui import (QFont, QColor, QKeySequence, QShortcut, QTextCharFormat,
                         QTextListFormat, QDesktopServices, QTextCursor, QPainter,
                         QPainterPath, QLinearGradient, QRadialGradient, QPen, QBrush,
                         QTextFormat)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QVariantAnimation, QEasingCurve, QRectF, QPointF

# --- Theme Data ---
THEMES = {
    "default": {"bg": "#f9f9f9", "text": "#111111", "btn_text": "#888888", "btn_hover": "#e0e0e0", "highlight": "#ffcc00", "highlight_text": "#000000", "modal_bg": "#ffffff", "modal_border": "#dddddd"},
    "grey-black": {"bg": "#d9d9d9", "text": "#1a1a1a", "btn_text": "#555555", "btn_hover": "#cccccc", "highlight": "#999999", "highlight_text": "#ffffff", "modal_bg": "#e6e6e6", "modal_border": "#bbbbbb"},
    "orange-black": {"bg": "#0a0a0a", "text": "#ff8c00", "btn_text": "#cc5500", "btn_hover": "#222222", "highlight": "#ff8c00", "highlight_text": "#0a0a0a", "modal_bg": "#111111", "modal_border": "#331a00"},
    "peach-white": {"bg": "#ffb4a2", "text": "#ffffff", "btn_text": "#ffffff", "btn_hover": "#e5989b", "highlight": "#ffffff", "highlight_text": "#ffb4a2", "modal_bg": "#ffb4a2", "modal_border": "#ffffff"},
    "steam": {"bg": "#171a21", "text": "#c7d5e0", "btn_text": "#66c0f4", "btn_hover": "#2a475e", "highlight": "#66c0f4", "highlight_text": "#171a21", "modal_bg": "#1b2838", "modal_border": "#2a475e"},
    "inverted-default": {"bg": "#111111", "text": "#f9f9f9", "btn_text": "#888888", "btn_hover": "#333333", "highlight": "#f9f9f9", "highlight_text": "#111111", "modal_bg": "#1e1e1e", "modal_border": "#444444"},
    "inverted-peach": {"bg": "#ffffff", "text": "#e88d7d", "btn_text": "#e88d7d", "btn_hover": "#f5f5f5", "highlight": "#e88d7d", "highlight_text": "#ffffff", "modal_bg": "#ffffff", "modal_border": "#e88d7d"},
}

FONTS = [
    ("Courier New", "Courier New", "Courier New, monospace"),
    ("Arial Standard", "Arial", "Arial, sans-serif"),
    ("Times New Roman", "Times New Roman", "Times New Roman, serif"),
    ("Georgia Chronicle", "Georgia", "Georgia, serif"),
    ("Verdana Gazette", "Verdana", "Verdana, sans-serif"),
    ("Comic Sans Funnies", "Comic Sans MS", "Comic Sans MS, cursive, sans-serif")
]

COLORS = [
    ("#e53935", "RED 35"), ("#d81b60", "PINK 60"), ("#8e24aa", "PURP AA"),
    ("#3949ab", "INDG AB"), ("#1e88e5", "BLUE E5"), ("#00897b", "TEAL 7B"),
    ("#43a047", "GRN 47"), ("#fdd835", "YEL 35"), ("#fb8c00", "ORG 00"),
    ("#6d4c41", "BRN 41"), ("#757575", "GRY 75"), ("#111111", "BLK 11"),
    ("#f9f9f9", "WHT F9")
]

# --- Custom Animated Widgets ---

class AnimatedHoverWidget(QWidget):
    """Base class for fluid CSS-like hover animations"""
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_progress = 0.0
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack) # Bouncy CSS cubic-bezier equivalent
        self.anim.valueChanged.connect(self.update_progress)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_progress(self, val):
        self.hover_progress = val
        self.update()

    def enterEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Forward)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setDirection(QVariantAnimation.Direction.Backward)
        self.anim.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class ThemeFlowerWidget(AnimatedHoverWidget):
    """Replicates the .theme-flower CSS animations, SVGs, and Highlights dynamically"""
    def __init__(self, theme_id, fill_color, stroke_color, is_invert_toggle=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.theme_id = theme_id
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.is_selected = False
        self.is_invert_toggle = is_invert_toggle
        self.app_ref = None # Will be set to access main app state for dynamic inversion colors

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        
        # 1. Draw Highlight (scales up if selected)
        if self.is_selected or self.hover_progress > 0:
            scale_hl = 1.0 if self.is_selected else (self.hover_progress * 0.5)
            if scale_hl > 0:
                painter.save()
                painter.translate(center)
                painter.scale(scale_hl, scale_hl)
                painter.translate(-center)
                
                rad = QRadialGradient(center, 30)
                is_inv = self.app_ref.is_inverted if self.app_ref else False
                
                if is_inv:
                    rad.setColorAt(0, QColor(0, 0, 0, 150))
                    rad.setColorAt(0.7, QColor(0, 0, 0, 0))
                else:
                    rad.setColorAt(0, QColor(255, 255, 255, 200))
                    rad.setColorAt(0.7, QColor(255, 255, 255, 0))
                    
                painter.fillRect(self.rect(), rad)
                painter.restore()

        # 2. Draw Flower with Hover Transformations
        painter.save()
        painter.translate(center)
        # Apply hover transform: scale(1.15) rotate(15deg) translateY(-5px)
        scale = 1.0 + (0.15 * self.hover_progress)
        rotate = 15.0 * self.hover_progress
        trans_y = -5.0 * self.hover_progress
        
        painter.translate(0, trans_y)
        painter.scale(scale, scale)
        painter.rotate(rotate)
        
        # Flower Path (from SVG: M 50 20 C 75 -5, 105 25, 80 50 C 105 75, 75 105, 50 80 C 25 105, -5 75, 20 50 C -5 25, 25 -5, 50 20 Z)
        # Scaled to fit widget (SVG viewBox is -10 -10 120 120, we shrink to 50x50 roughly)
        painter.scale(0.5, 0.5) 
        painter.translate(-50, -50) # offset back to path origin
        
        path = QPainterPath()
        path.moveTo(50, 20)
        path.cubicTo(75, -5, 105, 25, 80, 50)
        path.cubicTo(105, 75, 75, 105, 50, 80)
        path.cubicTo(25, 105, -5, 75, 20, 50)
        path.cubicTo(-5, 25, 25, -5, 50, 20)
        
        painter.setPen(QPen(QColor(self.stroke_color), 4))
        
        if self.is_invert_toggle:
            grad = QLinearGradient(0, 0, 100, 100)
            grad.setColorAt(0.49, QColor("#ffffff"))
            grad.setColorAt(0.51, QColor("#000000"))
            painter.setBrush(QBrush(grad))
        else:
            painter.setBrush(QBrush(QColor(self.fill_color)))
            
        # Draw drop shadow manually
        painter.save()
        painter.translate(0, 4 + (4 * self.hover_progress))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, int(60 + 20 * self.hover_progress)))
        painter.drawPath(path)
        painter.restore()
        
        painter.drawPath(path)
        painter.restore()

class NewspaperWidget(AnimatedHoverWidget):
    """Replicates the .newspaper-btn 3D stacked aesthetic"""
    def __init__(self, display_name, qt_font_name, base_rotation, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 60)
        self.display_name = display_name
        self.qt_font_name = qt_font_name
        self.base_rotation = base_rotation
        self.is_active = False
        self.app_ref = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_inv = self.app_ref.is_inverted if self.app_ref else False
        
        # Colors
        bg_col = QColor("#3e2723" if is_inv else "#fff9c4") if self.is_active else QColor("#fdfdf9")
        text_col = QColor("#ffecb3" if is_inv else "#b71c1c") if self.is_active else QColor("#1a1a1a")
        border_col = QColor("#ffb300" if is_inv else "#fbc02d") if self.is_active else QColor("#dcdcdc")
        
        center = QPointF(self.width() / 2, self.height() / 2)
        painter.translate(center)
        
        # Hover Transforms: un-rotate to 0, scale up, translate Y
        cur_rot = self.base_rotation * (1.0 - self.hover_progress)
        cur_scale = 1.0 + (0.05 * self.hover_progress)
        cur_ty = -10.0 * self.hover_progress
        
        painter.translate(0, cur_ty)
        painter.scale(cur_scale, cur_scale)
        painter.rotate(cur_rot)
        painter.translate(-center) # Back to top-left for drawing
        
        # Shadow
        shadow_dist = 4 + (11 * self.hover_progress)
        shadow_rect = QRectF(5, 5 + shadow_dist, self.width()-10, self.height()-10)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, int(30 + 30 * self.hover_progress)))
        
        # Box
        rect = QRectF(5, 5, self.width()-10, self.height()-10)
        painter.setBrush(bg_col)
        painter.setPen(QPen(border_col, 1))
        painter.drawRoundedRect(rect, 2, 2)
        
        # Inner Header "THE DAILY FONT"
        painter.setPen(QColor("#666666"))
        painter.setFont(QFont("Arial", 6))
        painter.drawText(QRectF(15, 8, self.width()-30, 10), Qt.AlignmentFlag.AlignHCenter, "THE DAILY FONT")
        painter.drawLine(20, 19, self.width()-20, 19)
        
        # Font Name
        painter.setPen(text_col)
        font = QFont(self.qt_font_name, 14)
        painter.setFont(font)
        painter.drawText(QRectF(15, 22, self.width()-30, 30), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.display_name)

class PantoneWidget(AnimatedHoverWidget):
    """Replicates the .pantone-swatch aesthetic"""
    def __init__(self, hex_val, name, parent=None):
        super().__init__(parent)
        self.setFixedSize(65, 85)
        self.hex_val = hex_val
        self.name = name
        self.app_ref = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_inv = self.app_ref.is_inverted if self.app_ref else False
        
        center = QPointF(self.width() / 2, self.height() / 2)
        painter.translate(center)
        cur_scale = 1.0 + (0.15 * self.hover_progress)
        cur_ty = -5.0 * self.hover_progress
        painter.translate(0, cur_ty)
        painter.scale(cur_scale, cur_scale)
        painter.translate(-center)
        
        # Shadow
        shadow_rect = QRectF(5, 5 + (5 * self.hover_progress), self.width()-10, self.height()-10)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, int(25 + 25 * self.hover_progress)))
        
        # Main Box
        rect = QRectF(5, 5, self.width()-10, self.height()-10)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#555555" if is_inv else "#e0e0e0"), 1))
        painter.drawRoundedRect(rect, 2, 2)
        
        # Color fill
        color_rect = QRectF(6, 6, self.width()-12, self.height()-32)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.hex_val))
        painter.drawRect(color_rect)
        
        # Text
        painter.setPen(QColor("#333333"))
        painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        text_rect = QRectF(6, self.height()-25, self.width()-12, 19)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.name)


class FlowerShelfWidget(QWidget):
    """Draws the Thymes Shop gradient shelf natively"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(15, 30, 15, 20)
        self.layout.setSpacing(20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 10, self.width(), self.height() - 10)
        
        # Gradient BG
        grad = QLinearGradient(0, 10, 0, self.height())
        grad.setColorAt(0, QColor("#f3ede4"))
        grad.setColorAt(1, QColor("#e2d2ba"))
        
        painter.setBrush(grad)
        painter.setPen(QPen(QColor("#8b5a2b"), 6))
        painter.drawRoundedRect(rect, 6, 6)
        
        # "✿ Thymes ✿" Badge
        badge_w, badge_h = 100, 24
        badge_rect = QRectF((self.width() - badge_w) / 2, 0, badge_w, badge_h)
        painter.setBrush(QColor("#8b5a2b"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 4, 4)
        
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "✿ Thymes ✿")


class OverlayModal(QWidget):
    """Semi-transparent animated backdrop"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.content_widget = None
        self.opacity_anim = QVariantAnimation(self)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setDuration(300)
        self.opacity_anim.valueChanged.connect(self.update_opacity)
        self.current_opacity = 0.0
        self.hide()

    def update_opacity(self, val):
        self.current_opacity = val
        self.update()
        if self.content_widget:
            # Set opacity on child
            op = QGraphicsOpacityEffect(self.content_widget)
            op.setOpacity(val)
            self.content_widget.setGraphicsEffect(op)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(100 * self.current_opacity)))

    def mousePressEvent(self, event):
        self.close_modal()

    def show_modal(self, widget):
        if self.content_widget:
            self.content_widget.setParent(None)
            self.content_widget.deleteLater()
        
        self.content_widget = widget
        widget.setParent(self)
        widget.show()
        self.resizeEvent(None)
        self.show()
        
        self.opacity_anim.setDirection(QVariantAnimation.Direction.Forward)
        self.opacity_anim.start()

    def close_modal(self):
        self.opacity_anim.setDirection(QVariantAnimation.Direction.Backward)
        self.opacity_anim.start()
        # Hide after animation
        self.opacity_anim.finished.connect(self._hide_after_anim)
        
    def _hide_after_anim(self):
        self.opacity_anim.finished.disconnect(self._hide_after_anim)
        self.hide()
        if self.parent() and hasattr(self.parent().parent(), 'editor'):
            self.parent().parent().editor.setFocus()

    def resizeEvent(self, event):
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        if self.content_widget:
            cw = self.content_widget.width()
            ch = self.content_widget.height()
            self.content_widget.setGeometry((self.width() - cw) // 2, (self.height() - ch) // 2, cw, ch)


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 10, 5)
        self.layout.setSpacing(5)

        self.title_label = QLabel("T   JAMN Editor")
        self.title_label.setObjectName("TitleLabel")
        self.layout.addWidget(self.title_label)
        self.layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("✕")
        
        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setObjectName("WinBtn")
            btn.setFixedSize(30, 25)
            self.layout.addWidget(btn)

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        self.start_pos = None

    def toggle_maximize(self):
        if self.parent.isMaximized(): self.parent.showNormal()
        else: self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None

# --- Main Application ---

class JAMNApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(1000, 700)

        # State Variables
        self.current_theme = "default"
        self.is_inverted = False
        self.current_font = "Courier New"
        self.current_text_color = "#e53935"

        self.init_ui()
        self.apply_stylesheet()
        self.setup_shortcuts()

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("Central")
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        self.title_bar.setObjectName("TitleBar")
        main_layout.addWidget(self.title_bar)

        self.toolbar_widget = QWidget()
        self.toolbar_widget.setObjectName("Toolbar")
        tb_layout = QHBoxLayout(self.toolbar_widget)
        tb_layout.setContentsMargins(15, 10, 15, 10)
        
        self.add_tool_btn(tb_layout, "H1", lambda: self.format_block(24))
        self.add_tool_btn(tb_layout, "H2", lambda: self.format_block(18))
        self.add_tool_btn(tb_layout, "H3", lambda: self.format_block(14))
        self.add_divider(tb_layout)
        self.add_tool_btn(tb_layout, "List", lambda: self.format_list(QTextListFormat.Style.ListDisc))
        self.add_tool_btn(tb_layout, "Num", lambda: self.format_list(QTextListFormat.Style.ListDecimal))
        self.add_divider(tb_layout)
        self.add_tool_btn(tb_layout, "Highlight", self.apply_highlight)
        self.add_divider(tb_layout)
        self.add_tool_btn(tb_layout, "Font", lambda: self.open_modal("font"))
        self.add_divider(tb_layout)

        color_layout = QHBoxLayout()
        color_layout.setSpacing(0)
        self.color_btn = QPushButton("Aa")
        self.color_btn.setObjectName("ColorBtnAa")
        self.color_btn.clicked.connect(self.apply_current_color)
        color_down = QPushButton("▼")
        color_down.setObjectName("ColorBtnDown")
        color_down.clicked.connect(lambda: self.open_modal("color"))
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(color_down)
        tb_layout.addLayout(color_layout)

        self.add_divider(tb_layout)
        self.add_tool_btn(tb_layout, "Theme", lambda: self.open_modal("theme"))

        tb_layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.toggle_bar_btn = self.add_tool_btn(tb_layout, "Hide Bar", self.toggle_toolbar)
        self.add_tool_btn(tb_layout, "Save TXT", self.save_document)

        main_layout.addWidget(self.toolbar_widget)

        editor_wrapper = QHBoxLayout()
        editor_wrapper.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.editor = QTextEdit()
        self.editor.setObjectName("Editor")
        self.editor.setPlaceholderText("Start typing... (Win+Shift+H for shortcuts)")
        self.editor.setMaximumWidth(900)
        self.editor.setMinimumWidth(600)
        
        editor_wrapper.addWidget(self.editor)
        editor_wrapper.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(editor_wrapper)

        self.overlay = OverlayModal(self.central_widget)

    def add_tool_btn(self, layout, text, callback):
        btn = QPushButton(text)
        btn.setProperty("class", "ToolBtn")
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def add_divider(self, layout):
        div = QFrame()
        div.setProperty("class", "Divider")
        layout.addWidget(div)

    def get_colors(self):
        base = THEMES.get(self.current_theme, THEMES["default"]).copy()
        if self.is_inverted:
            base["bg"], base["text"] = base["text"], base["bg"]
        return base

    def apply_stylesheet(self):
        c = self.get_colors()
        
        # Using format avoiding f-strings for syntax safety in all IDEs
        qss = """
        QWidget#Central { background-color: @bg; color: @text; transition: background-color 0.6s; }
        QWidget#TitleBar { background-color: @bg; border-bottom: 1px dashed @modal_border; }
        QLabel#TitleLabel { color: @text; font-weight: bold; font-family: 'Courier New'; font-size: 14px; padding-left: 10px; }
        QPushButton#WinBtn { background: transparent; color: @btn_text; border: none; font-size: 12px; }
        QPushButton#WinBtn:hover { background: @btn_hover; color: @text; }
        
        QWidget#Toolbar { background-color: @bg; border-bottom: 1px dashed @modal_border; }
        QPushButton[class="ToolBtn"] { background: transparent; color: @btn_text; border: 1px solid transparent; border-radius: 4px; padding: 6px 10px; font-family: '@font'; font-size: 13px; }
        QPushButton[class="ToolBtn"]:hover { background: @btn_hover; color: @text; border: 1px solid @modal_border; }
        
        QFrame[class="Divider"] { background-color: @modal_border; max-width: 1px; min-width: 1px; margin: 0 4px; }
        
        QPushButton#ColorBtnAa { background: transparent; color: @current_color; font-weight: bold; border-top-left-radius: 4px; border-bottom-left-radius: 4px; padding: 6px 10px; }
        QPushButton#ColorBtnAa:hover { background: @btn_hover; }
        QPushButton#ColorBtnDown { background: transparent; color: @btn_text; border-left: 1px solid @modal_border; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 6px 6px; font-size: 10px; }
        QPushButton#ColorBtnDown:hover { background: @btn_hover; }

        QTextEdit#Editor { background-color: @bg; color: @text; border: none; font-family: '@font'; font-size: 18px; padding: 40px; }
        
        QWidget[class="Modal"] { background-color: @modal_bg; border: 1px solid @modal_border; border-radius: 12px; }
        QLabel[class="ModalTitle"] { color: @text; border-bottom: 1px dashed @modal_border; font-size: 18px; padding-bottom: 10px; }
        QLabel[class="ShortcutText"] { color: @text; font-size: 14px; padding: 5px; }
        QLabel[class="Kbd"] { background: @btn_hover; color: @text; border-radius: 3px; padding: 2px 6px; font-size: 12px; }
        """
        
        for key, value in c.items():
            qss = qss.replace("@" + key, value)
        
        qss = qss.replace("@font", self.current_font)
        qss = qss.replace("@current_color", self.current_text_color)
        self.setStyleSheet(qss)

    # --- Dynamic Document Recolor Engine ---
    def refresh_document_theme(self):
        """Scans the document to update highlights and text colors dynamically matching CSS behavior"""
        c = self.get_colors()
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        doc = self.editor.document()
        block = doc.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                fmt = fragment.charFormat()
                
                # Check for our custom highlight tag
                is_hl = fmt.property(QTextFormat.Property.UserProperty) == "is_highlight"
                has_custom_color = fmt.property(QTextFormat.Property.UserProperty + 1) == "custom_color"
                
                if is_hl:
                    fmt.setBackground(QColor(c['highlight']))
                    fmt.setForeground(QColor(c['highlight_text']))
                elif not has_custom_color:
                    # Standard text, update to new theme text color
                    fmt.setForeground(QColor(c['text']))
                    
                # Apply format
                temp_cursor = QTextCursor(doc)
                temp_cursor.setPosition(fragment.position())
                temp_cursor.setPosition(fragment.position() + fragment.length(), QTextCursor.MoveMode.KeepAnchor)
                temp_cursor.mergeCharFormat(fmt)
                
                iterator += 1
            block = block.next()
            
        cursor.endEditBlock()

    # --- Text Formatting ---
    def format_block(self, size):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        fmt.setFontWeight(QFont.Weight.Bold)
        cursor.mergeCharFormat(fmt)
        self.editor.setFocus()

    def format_list(self, style):
        cursor = self.editor.textCursor()
        cursor.createList(style)
        self.editor.setFocus()

    def apply_highlight(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            is_hl = fmt.property(QTextFormat.Property.UserProperty) == "is_highlight"
            
            if is_hl:
                # Remove highlight
                fmt.clearProperty(QTextFormat.Property.UserProperty)
                fmt.setBackground(Qt.GlobalColor.transparent)
                
                # Restore original text color (custom or theme default)
                if fmt.property(QTextFormat.Property.UserProperty + 1) == "custom_color":
                    pass # Keep its custom color
                else:
                    fmt.setForeground(QColor(self.get_colors()['text']))
            else:
                # Apply highlight
                fmt.setProperty(QTextFormat.Property.UserProperty, "is_highlight")
                fmt.setBackground(QColor(self.get_colors()['highlight']))
                fmt.setForeground(QColor(self.get_colors()['highlight_text']))
                
            cursor.setCharFormat(fmt)
            self.editor.setFocus()

    def apply_current_color(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(self.current_text_color))
            # Tag it as custom so theme changes don't overwrite it
            fmt.setProperty(QTextFormat.Property.UserProperty + 1, "custom_color")
            cursor.mergeCharFormat(fmt)
            self.editor.setFocus()

    def apply_preset_color(self, hex_val):
        self.current_text_color = hex_val
        self.apply_current_color()
        self.apply_stylesheet() 
        self.overlay.close_modal()

    def apply_font(self, font_name):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontFamily(font_name)
            cursor.mergeCharFormat(fmt)
        else:
            self.current_font = font_name
            self.apply_stylesheet()
        self.overlay.close_modal()

    # --- Actions ---
    def toggle_toolbar(self):
        if self.toolbar_widget.isVisible():
            self.toolbar_widget.hide()
            self.toggle_bar_btn.setText("Show Bar")
        else:
            self.toolbar_widget.show()
            self.toggle_bar_btn.setText("Hide Bar")

    def apply_theme_changes(self, theme_name=None, toggle_invert=False):
        """Crossfade animation engine for switching themes natively"""
        # Hide dark overlay temporarily to capture clean background
        was_overlay_visible = self.overlay.isVisible()
        if was_overlay_visible: self.overlay.setVisible(False)
        
        pixmap = self.central_widget.grab()
        
        if was_overlay_visible: self.overlay.setVisible(True)

        # Create overlay label holding old UI image
        self.fade_overlay = QLabel(self.central_widget)
        self.fade_overlay.setPixmap(pixmap)
        self.fade_overlay.setGeometry(self.central_widget.rect())
        self.fade_overlay.show()
        self.fade_overlay.stackUnder(self.overlay) # Keep modal visually on top

        # Update core variables
        if theme_name:
            self.current_theme = theme_name
            self.is_inverted = False
        if toggle_invert:
            self.is_inverted = not self.is_inverted

        # Change styling instantly underneath the screenshot
        self.apply_stylesheet()
        self.refresh_document_theme()
        
        if hasattr(self, 'themes_modal_ref') and self.themes_modal_ref:
            self.themes_modal_ref.update()

        # Animate the old screenshot fading out
        self.fade_effect = QGraphicsOpacityEffect(self.fade_overlay)
        self.fade_overlay.setGraphicsEffect(self.fade_effect)
        
        self.fade_anim = QVariantAnimation(self)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setDuration(600) # Replicates the 0.6s CSS transition
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_anim.valueChanged.connect(self.fade_effect.setOpacity)
        self.fade_anim.finished.connect(self.fade_overlay.deleteLater)
        self.fade_anim.start()

        self.overlay.close_modal()

    def toggle_invert(self):
        self.apply_theme_changes(toggle_invert=True)

    def set_theme(self, theme_name):
        self.apply_theme_changes(theme_name=theme_name)

    def toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

    def save_document(self):
        text = self.editor.toPlainText()
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        filename, _ = QFileDialog.getSaveFileName(self, "Save TXT", "JAMN_" + date_str + ".txt", "Text Files (*.txt)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)

    def setup_shortcuts(self):
        binds = {
            "Alt+1": lambda: self.format_block(24), "Alt+2": lambda: self.format_block(18), "Alt+3": lambda: self.format_block(14),
            "Alt+U": lambda: self.format_list(QTextListFormat.Style.ListDisc), "Alt+O": lambda: self.format_list(QTextListFormat.Style.ListDecimal),
            "Alt+H": self.apply_highlight, "Alt+K": lambda: self.open_modal("color"), "Alt+F": lambda: self.open_modal("font"),
            "Alt+D": lambda: self.open_modal("theme"), "Alt+I": self.toggle_invert, "Alt+B": self.toggle_toolbar,
            "Alt+C": lambda: QDesktopServices.openUrl(QUrl("https://thingscolddid.baby")), "F11": self.toggle_fullscreen,
            "Ctrl+B": lambda: self.editor.setFontWeight(QFont.Weight.Bold if self.editor.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal),
            "Ctrl+I": lambda: self.editor.setFontItalic(not self.editor.fontItalic()), "Ctrl+U": lambda: self.editor.setFontUnderline(not self.editor.fontUnderline()),
            "Meta+Shift+H": lambda: self.open_modal("shortcuts"), "Ctrl+Shift+H": lambda: self.open_modal("shortcuts"),
            "Esc": self.overlay.close_modal
        }
        for key, func in binds.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    # --- Animated Modals ---
    def open_modal(self, modal_type):
        modal = QWidget()
        modal.setProperty("class", "Modal")
        modal.setFixedWidth(400)
        
        layout = QVBoxLayout(modal)
        layout.setContentsMargins(30, 30, 30, 30)

        if modal_type == "shortcuts":
            title = QLabel("Shortcuts")
            title.setProperty("class", "ModalTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            grid = QGridLayout()
            shortcuts = [
                ("Heading 1", "Alt + 1"), ("Heading 2", "Alt + 2"), ("Heading 3", "Alt + 3"),
                ("Bullet Points", "Alt + U"), ("Numbered List", "Alt + O"), ("Highlight Text", "Alt + H"),
                ("Text Color", "Alt + K"), ("Font Menu", "Alt + F"), ("Theme Menu", "Alt + D"),
                ("Invert Theme", "Alt + I"), ("Toggle Bar", "Alt + B"), ("Credits", "Alt + C"),
                ("Bold", "Ctrl + B"), ("Italics", "Ctrl + I"), ("Underline", "Ctrl + U"),
                ("Show Shortcuts", "Win/Cmd + Shift + H"), ("Fullscreen", "F11")
            ]
            for i, (desc, keys) in enumerate(shortcuts):
                l_desc = QLabel(desc)
                l_desc.setProperty("class", "ShortcutText")
                l_keys = QLabel(keys)
                l_keys.setProperty("class", "Kbd")
                l_keys.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid.addWidget(l_desc, i, 0)
                grid.addWidget(l_keys, i, 1, Qt.AlignmentFlag.AlignRight)
            layout.addLayout(grid)

        elif modal_type == "color":
            title = QLabel("Color Palette")
            title.setProperty("class", "ModalTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            grid = QGridLayout()
            grid.setSpacing(15)
            row, col = 0, 0
            for hex_val, name in COLORS:
                swatch = PantoneWidget(hex_val, name)
                swatch.app_ref = self
                swatch.clicked.connect(lambda h=hex_val: self.apply_preset_color(h))
                grid.addWidget(swatch, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            layout.addLayout(grid)

        elif modal_type == "font":
            modal.setStyleSheet("background: transparent; border: none;") 
            title = QLabel("The Daily Font")
            title.setProperty("class", "ModalTitle")
            title.setStyleSheet("color: " + self.get_colors()['text'] + "; font-weight: bold;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            import random
            fonts = FONTS.copy()
            random.shuffle(fonts) # Stack shuffle like HTML

            for idx, (disp_name, qt_font, web_font) in enumerate(fonts):
                rot = -2 if idx % 2 == 0 else 3
                btn = NewspaperWidget(disp_name, qt_font, rot)
                btn.app_ref = self
                btn.is_active = (qt_font == self.current_font)
                btn.clicked.connect(lambda f=qt_font: self.apply_font(f))
                layout.addWidget(btn)

        elif modal_type == "theme":
            self.themes_modal_ref = modal
            title = QLabel("Themes")
            title.setProperty("class", "ModalTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            shelf = FlowerShelfWidget()
            row, col = 0, 0
            
            theme_list = [
                ("default", "#f9f9f9", "#dddddd"), ("grey-black", "#d9d9d9", "#1a1a1a"),
                ("orange-black", "#0a0a0a", "#ff8c00"), ("peach-white", "#ffb4a2", "#ffffff"),
                ("steam", "#171a21", "#66c0f4"), ("inverted-default", "#111111", "#555555"),
                ("inverted-peach", "#ffffff", "#e88d7d")
            ]
            
            for t_name, bg, border in theme_list:
                f_widget = ThemeFlowerWidget(t_name, bg, border)
                f_widget.app_ref = self
                f_widget.is_selected = (self.current_theme == t_name)
                f_widget.clicked.connect(lambda t=t_name: self.set_theme(t))
                shelf.layout.addWidget(f_widget, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
                    
            inv_widget = ThemeFlowerWidget("invert", "#fff", "#888", is_invert_toggle=True)
            inv_widget.app_ref = self
            inv_widget.clicked.connect(self.toggle_invert)
            shelf.layout.addWidget(inv_widget, row, col)
            
            layout.addWidget(shelf)

        self.overlay.show_modal(modal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JAMNApp()
    window.show()
    sys.exit(app.exec())