from __future__ import annotations

import ctypes
import json
import sys
from ctypes import wintypes
from pathlib import Path


def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base.joinpath(*parts)
try:
    import winreg  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - non-Windows
    winreg = None

from PySide6.QtCore import QObject, QPoint, QRect, QSize, QTimer, Qt, QStandardPaths
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QLinearGradient,
    QPainter,
    QPen,
    QCursor,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSlider,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]

THEMES = {
    "Papier": """
        #StickyRoot { background-color: #f7f1dc; color: #2f2a1f; font-size: 13px; }
        #StickyRoot QTextEdit {
            background-color: #fff9e8;
            border: 1px solid #dccfa8;
            border-radius: 8px;
            padding: 10px;
            selection-background-color: #d9c88f;
        }
        #StickyRoot QTextEdit QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px 2px 2px 0;
        }
        #StickyRoot QTextEdit QScrollBar::handle:vertical {
            background: rgba(0, 0, 0, 0.25);
            border-radius: 5px;
            min-height: 24px;
        }
        #StickyRoot QTextEdit QScrollBar::add-line:vertical,
        #StickyRoot QTextEdit QScrollBar::sub-line:vertical {
            height: 0px;
        }
        #StickyRoot QTextEdit QScrollBar:horizontal { height: 0px; }
        #StickyRoot QComboBox, #StickyRoot QCheckBox { padding: 4px; }
    """,
    "Sticky": """
        #StickyRoot { background-color: #fff6a8; color: #3b3b2a; font-size: 13px; }
        #StickyRoot QTextEdit {
            background-color: #fff9be;
            border: 1px solid #d7cd63;
            border-radius: 6px;
            padding: 10px;
            selection-background-color: #ebdf73;
        }
        #StickyRoot QTextEdit QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 2px 2px 2px 0;
        }
        #StickyRoot QTextEdit QScrollBar::handle:vertical {
            background: rgba(0, 0, 0, 0.28);
            border-radius: 5px;
            min-height: 24px;
        }
        #StickyRoot QTextEdit QScrollBar::add-line:vertical,
        #StickyRoot QTextEdit QScrollBar::sub-line:vertical {
            height: 0px;
        }
        #StickyRoot QTextEdit QScrollBar:horizontal { height: 0px; }
        #StickyRoot QComboBox, #StickyRoot QCheckBox { padding: 4px; }
    """,
    "Sombre": """
        #StickyRoot { background-color: #23262b; color: #f2f2f2; font-size: 13px; }
        #StickyRoot QTextEdit {
            background-color: #12151a;
            border: 1px solid #3f4550;
            border-radius: 8px;
            padding: 10px;
            selection-background-color: #5b6575;
            color: #f2f2f2;
        }
        #StickyRoot QTextEdit QScrollBar:vertical {
            background: #1a1d21;
            width: 10px;
            margin: 2px 2px 2px 0;
        }
        #StickyRoot QTextEdit QScrollBar::handle:vertical {
            background: #4a5361;
            border-radius: 5px;
            min-height: 24px;
        }
        #StickyRoot QTextEdit QScrollBar::add-line:vertical,
        #StickyRoot QTextEdit QScrollBar::sub-line:vertical {
            height: 0px;
        }
        #StickyRoot QTextEdit QScrollBar:horizontal { height: 0px; }
        #StickyRoot QComboBox, #StickyRoot QCheckBox { padding: 4px; }
    """,
    # Textures gérées dynamiquement (voir apply_theme)
    "Notes": "",
    "Calpin": "",
    "Personnalisé": "",
}


class StickyNoteWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("StickyRoot")
        self.base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        self.data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # writable paths
        self.notes_path = self.data_dir.joinpath("notes.txt")
        self.notes_html_path = self.data_dir.joinpath("notes.html")
        self.custom_style_path = self.data_dir.joinpath("custom_style.json")
        self.layout_config_path = self.data_dir.joinpath("layout.json")
        self.font_config_path = self.data_dir.joinpath("font.json")
        self.color_config_path = self.data_dir.joinpath("color.json")
        self.opacity_config_path = self.data_dir.joinpath("opacity.json")
        self.theme_config_path = self.data_dir.joinpath("theme.json")
        self.autostart_config_path = self.data_dir.joinpath("autostart.json")

        # bundled resources
        self.icon_path = resource_path("icon.ico")
        self.texture1_path = resource_path("app image", "texture1.PNG")
        self.texture2_path = resource_path("app image", "texture2.png")
        self.epingle_on_path = resource_path("nav", "epingle", "epingle_ON.png")
        self.epingle_off_path = resource_path("nav", "epingle", "epingle_OFF.png")
        self.drag_icon_path = resource_path("nav", "drag", "hand.png")
        self.style_icon_path = resource_path("nav", "Style", "s.png")
        self.modify_icon_path = resource_path("nav", "modify", "crayon.png")
        self.color_icon_path = resource_path("nav", "color", "color.png")
        self.size_icon_path = resource_path("nav", "fonts", "t2.png")
        self.hide_icon_path = resource_path("nav", "hide", "hide.png")
        self.see_icon_path = resource_path("nav", "hide", "see.png")
        self.font_icon_path = resource_path("nav", "fonts", "t.png")
        self.opacity_icon_path = resource_path("nav", "opacity", "visible.png")
        self.resize_icon_path = resource_path("nav", "resize", "regle.png")
        self.fonts_dir = resource_path("fonts")
        self._quitting = False
        self._pinned = True
        self._drag_pos: QPoint | None = None
        self._overlay_enabled = False
        self.default_margins = (28, 32, 24, 24)
        self.default_font_size = 13
        self._hotkey_registered = False
        self.hotkey_id = 1
        self.base_size = QSize(420, 420)

        self.setWindowTitle("Bloc note épinglé")
        if self.icon_path.exists():
            self.setWindowIcon(QIcon(str(self.icon_path)))
        self.resize(420, 420)
        self.setWindowFlags(self.compute_flags(self._pinned))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout_config = self.load_layout_config()
        self.font_config = self.load_font_config()
        self.color_config = self.load_color_config()
        self.custom_style = self.load_custom_style()
        self.opacity_value = self.load_opacity_config()
        self.theme_config = self.load_theme_config()
        self.autostart_enabled = self.load_autostart_config()
        self.current_font_name = self.font_config.get("current", "Défaut")
        self.font_families = self.load_fonts()
        self.current_color_mode = self.color_config.get("mode", "solid")
        self.current_colors = self.color_config.get("colors", ["#2f2a1f", "#2f2a1f"])
        self.current_font_size = int(self.font_config.get("size", self.default_font_size))
        self.setWindowOpacity(self.opacity_value)
        # ensure autostart registry matches saved preference
        self.set_autostart(self.autostart_enabled)

        self.pin_button = QPushButton()
        self.pin_button.setCheckable(True)
        self.pin_button.setChecked(True)
        self.pin_button.setFlat(True)
        self.pin_button.setCursor(Qt.PointingHandCursor)
        self.pin_button.setToolTip("Epingler / Désépingler")
        self.pin_button.setIconSize(QSize(24, 24))
        self.set_pin_icon(True)
        self.pin_button.toggled.connect(self.toggle_pin)

        self.drag_button = QPushButton()
        self.drag_button.setFlat(True)
        self.drag_button.setCursor(Qt.OpenHandCursor)
        self.drag_button.setToolTip("Maintenir pour déplacer")
        if self.drag_icon_path.exists():
            self.drag_button.setIcon(QIcon(str(self.drag_icon_path)))
        self.drag_button.setIconSize(QSize(22, 22))
        self.drag_button.installEventFilter(self)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        self.theme_combo.setVisible(False)
        saved_theme = self.theme_config.get("theme", "Papier")
        if saved_theme in THEMES:
            self.theme_combo.setCurrentText(saved_theme)

        self.style_menu = QMenu(self)
        for name in THEMES.keys():
            act = self.style_menu.addAction(name)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, n=name: self.select_theme(n))
        self.style_menu.addSeparator()
        custom_image = self.style_menu.addAction("Image personnalisée…")
        custom_image.triggered.connect(self.choose_custom_image)
        custom_color = self.style_menu.addAction("Couleur personnalisée…")
        custom_color.triggered.connect(self.choose_custom_color)

        self.font_menu = QMenu(self)
        self.font_actions: list[QAction] = []
        self.build_font_menu()

        self.color_menu = QMenu(self)
        self.build_color_menu()

        self.modify_button = QPushButton("")
        self.modify_button.setFlat(True)
        self.modify_button.setCursor(Qt.PointingHandCursor)
        self.modify_button.setToolTip("Ajuster la zone de texte")
        self.modify_button.setCheckable(True)
        self.modify_button.setVisible(False)
        if self.modify_icon_path.exists():
            self.modify_button.setIcon(QIcon(str(self.modify_icon_path)))
            self.modify_button.setIconSize(QSize(18, 18))
        self.modify_button.toggled.connect(self.toggle_overlay_mode)

        self.hide_button = QPushButton("")
        self.hide_button.setFlat(True)
        self.hide_button.setCursor(Qt.PointingHandCursor)
        self.hide_button.setToolTip("Masquer/afficher les commandes")
        self.hide_button.setCheckable(True)
        self.set_hide_icon(expanded=True)
        self.hide_button.toggled.connect(self.toggle_topbar_visibility)

        self.style_button = QPushButton("")
        self.style_button.setFlat(True)
        self.style_button.setCursor(Qt.PointingHandCursor)
        self.style_button.setToolTip("Choisir un style")
        if self.style_icon_path.exists():
            self.style_button.setIcon(QIcon(str(self.style_icon_path)))
            self.style_button.setIconSize(QSize(18, 18))
        self.style_button.setMenu(self.style_menu)

        self.font_button = QPushButton("")
        self.font_button.setFlat(True)
        self.font_button.setCursor(Qt.PointingHandCursor)
        self.font_button.setToolTip("Choisir une police")
        if self.font_icon_path.exists():
            self.font_button.setIcon(QIcon(str(self.font_icon_path)))
            self.font_button.setIconSize(QSize(18, 18))
        self.font_button.setMenu(self.font_menu)

        self.size_button = QPushButton("")
        self.size_button.setFlat(True)
        self.size_button.setCursor(Qt.PointingHandCursor)
        self.size_button.setToolTip("Taille du texte")
        if self.size_icon_path.exists():
            self.size_button.setIcon(QIcon(str(self.size_icon_path)))
            self.size_button.setIconSize(QSize(18, 18))
        self.size_button.clicked.connect(self.open_size_dialog)

        self.resize_button = QPushButton("")
        self.resize_button.setFlat(True)
        self.resize_button.setCursor(Qt.PointingHandCursor)
        self.resize_button.setToolTip("Redimensionner la note")
        if self.resize_icon_path.exists():
            self.resize_button.setIcon(QIcon(str(self.resize_icon_path)))
            self.resize_button.setIconSize(QSize(18, 18))
        else:
            self.resize_button.setText("↕↔")
        self.resize_button.clicked.connect(self.open_resize_dialog)

        self.opacity_button = QPushButton("")
        self.opacity_button.setFlat(True)
        self.opacity_button.setCursor(Qt.PointingHandCursor)
        self.opacity_button.setToolTip("Opacité de la note")
        if self.opacity_icon_path.exists():
            self.opacity_button.setIcon(QIcon(str(self.opacity_icon_path)))
            self.opacity_button.setIconSize(QSize(18, 18))
        else:
            self.opacity_button.setText("Op")
            self.opacity_button.setFixedWidth(32)
        self.opacity_button.clicked.connect(self.open_opacity_dialog)

        self.color_button = QPushButton("")
        self.color_button.setFlat(True)
        self.color_button.setCursor(Qt.PointingHandCursor)
        self.color_button.setToolTip("Couleur / dégradé")
        if self.color_icon_path.exists():
            self.color_button.setIcon(QIcon(str(self.color_icon_path)))
            self.color_button.setIconSize(QSize(18, 18))
        self.color_button.setMenu(self.color_menu)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Écris ici tes notes...")
        self.editor.viewport().setAutoFillBackground(False)
        self.editor.installEventFilter(self)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.hide_button)
        top_bar.addWidget(self.pin_button)
        top_bar.addWidget(self.drag_button)
        top_bar.addStretch(1)
        top_bar.addWidget(self.modify_button)
        top_bar.addWidget(self.font_button)
        top_bar.addWidget(self.size_button)
        top_bar.addWidget(self.resize_button)
        top_bar.addWidget(self.opacity_button)
        top_bar.addWidget(self.color_button)
        top_bar.addWidget(self.style_button)

        self.editor_container = QWidget()
        self.editor_container.setObjectName("EditorContainer")
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(*self.default_margins)
        self.editor_layout.addWidget(self.editor)

        self.overlay = MarginOverlay(self.editor_container, self.get_editor_margins, self.on_overlay_margins_changed)
        self.overlay.hide()

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 16, 12, 12)
        root.addLayout(top_bar)
        root.addWidget(self.editor_container)

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self.save_notes)

        self.editor.textChanged.connect(self.on_text_changed)
        self.setup_format_shortcuts()

        self.tray_icon: QSystemTrayIcon | None = None
        self.setup_tray()

        self.load_notes()
        self.apply_theme(self.theme_combo.currentText())
        self.apply_color_scheme()
        self.register_global_hotkey()

    def toggle_pin(self, pinned: bool) -> None:
        self._pinned = pinned
        self.setWindowFlags(self.compute_flags(pinned))
        self.set_pin_icon(pinned)
        self.show()

    def apply_theme(self, theme_name: str) -> None:
        if theme_name in {"Texture1", "Notes"}:
            # Texture1 est désormais nommé "Notes" (compat rétro)
            self.setStyleSheet(self.texture_stylesheet(self.texture1_path))
            theme_name = "Notes"
        elif theme_name in {"Texture2", "Calpin"}:
            # Texture2 est désormais nommé "Calpin" (compat rétro)
            self.setStyleSheet(self.texture_stylesheet(self.texture2_path))
            theme_name = "Calpin"
        elif theme_name == "Personnalisé":
            mode = self.custom_style.get("mode")
            value = self.custom_style.get("value")
            if mode == "image" and value:
                path = Path(value)
                if path.exists():
                    self.setStyleSheet(self.texture_stylesheet(path))
                else:
                    self.setStyleSheet(THEMES.get("Papier", ""))
            elif mode == "color" and value:
                self.setStyleSheet(self.solid_color_stylesheet(str(value)))
            else:
                self.setStyleSheet(THEMES.get("Papier", ""))
        else:
            self.setStyleSheet(THEMES.get(theme_name, ""))
        self.apply_editor_margins(theme_name)
        self.update_debug_button_visibility(theme_name)
        self.update_style_menu_checks(theme_name)
        self.apply_current_font()
        self.save_theme_config(theme_name)

    def on_text_changed(self) -> None:
        self.save_timer.start()

    def save_notes(self) -> None:
        # Save rich text to HTML for formatting persistence
        html = self.editor.toHtml()
        self.notes_html_path.write_text(html, encoding="utf-8")
        # Also keep plain text as fallback
        self.notes_path.write_text(self.editor.toPlainText(), encoding="utf-8")

    def load_notes(self) -> None:
        if self.notes_html_path.exists():
            self.editor.setHtml(self.notes_html_path.read_text(encoding="utf-8"))
        elif self.notes_path.exists():
            self.editor.setPlainText(self.notes_path.read_text(encoding="utf-8"))

    def setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon = QIcon(str(self.icon_path)) if self.icon_path.exists() else self.style().standardIcon(QStyle.SP_FileIcon)
        tray = QSystemTrayIcon(icon, self)

        show_action = QAction("Ouvrir", self)
        show_action.triggered.connect(self.show_window)

        hide_action = QAction("Masquer", self)
        hide_action.triggered.connect(self.hide)

        autostart_action = QAction("Démarrage automatique", self)
        autostart_action.setCheckable(True)
        autostart_action.setChecked(self.autostart_enabled)
        autostart_action.toggled.connect(self.set_autostart)
        self.autostart_action = autostart_action

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_from_tray)

        menu = QMenu(self)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(autostart_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        tray.setContextMenu(menu)
        tray.activated.connect(self.on_tray_activated)
        tray.show()
        tray.showMessage("Bloc note", "Toujours disponible dans la barre système.", QSystemTrayIcon.Information, 2000)

        self.tray_icon = tray

    def show_window(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in {QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick}:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()

    def quit_from_tray(self) -> None:
        self._quitting = True
        self.unregister_global_hotkey()
        QApplication.quit()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.tray_icon and self.tray_icon.isVisible() and not self._quitting:
            event.ignore()
            self.hide()
            return

        self.save_notes()
        self.unregister_global_hotkey()
        event.accept()

    def set_pin_icon(self, pinned: bool) -> None:
        if pinned and self.epingle_on_path.exists():
            self.pin_button.setIcon(QIcon(str(self.epingle_on_path)))
        elif not pinned and self.epingle_off_path.exists():
            self.pin_button.setIcon(QIcon(str(self.epingle_off_path)))
        else:
            fallback = self.style().standardIcon(QStyle.SP_TitleBarPinButton if pinned else QStyle.SP_TitleBarUnshadeButton)
            self.pin_button.setIcon(fallback)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if hasattr(self, "overlay") and self.overlay:
            self.overlay.setGeometry(self.editor_container.rect())

    def eventFilter(self, watched: QObject, event) -> bool:  # type: ignore[override]
        if watched is self.drag_button and event.type() in {event.Type.MouseButtonPress, event.Type.MouseMove, event.Type.MouseButtonRelease}:
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return True
            if event.type() == event.Type.MouseMove and self._drag_pos and event.buttons() & Qt.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
                return True
            if event.type() == event.Type.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_pos = None
                event.accept()
                return True

        if watched is self.editor and event.type() in {event.Type.MouseButtonPress, event.Type.MouseMove, event.Type.MouseButtonRelease}:
            if not (event.modifiers() & Qt.ControlModifier):
                return super().eventFilter(watched, event)

            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return True

            if event.type() == event.Type.MouseMove and self._drag_pos and event.buttons() & Qt.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
                return True

            if event.type() == event.Type.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_pos = None
                event.accept()
                return True

        return super().eventFilter(watched, event)

    def nativeEvent(self, eventType, message):  # type: ignore[override]
        if sys.platform.startswith("win") and eventType == "windows_generic_MSG":
            msg = MSG.from_address(int(message))
            WM_HOTKEY = 0x0312
            if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                self.toggle_visibility_from_hotkey()
                return True, 0
        return super().nativeEvent(eventType, message)


    def select_theme(self, name: str) -> None:
        if name in THEMES:
            self.theme_combo.setCurrentText(name)

    def select_font(self, family: str | None) -> None:
        if family is None:
            self.current_font_name = "Défaut"
        else:
            self.current_font_name = family
        self.apply_font_family_to_cursor(self.current_font_name)
        self.save_font_config()
        self.apply_current_font()
        self.update_font_menu_checks(self.current_font_name)

    def select_color_mode(self, mode: str) -> None:
        self.current_color_mode = mode
        self.save_color_config()
        self.apply_color_scheme()
        self.update_color_menu_checks(mode)

    def pick_color(self, index: int) -> None:
        initial = QColor(self.current_colors[index]) if 0 <= index < len(self.current_colors) else QColor("#2f2a1f")
        color = QColorDialog.getColor(initial, self, "Choisir une couleur")
        if color.isValid():
            if len(self.current_colors) < 2:
                self.current_colors = [self.current_colors[0], self.current_colors[0]]
            self.current_colors[index] = color.name()
            self.save_color_config()
            self.apply_color_scheme()
            self.update_color_menu_checks(self.current_color_mode)

    def update_style_menu_checks(self, current: str) -> None:
        for act in self.style_menu.actions():
            act.setChecked(act.text() == current)

    def update_font_menu_checks(self, current: str) -> None:
        for act in self.font_menu.actions():
            act.setChecked(act.text() == current)

    def update_color_menu_checks(self, current: str) -> None:
        for act in self.color_menu.actions():
            if act.isSeparator():
                continue
            act.setChecked(act.text() == current)

    def is_image_theme(self, name: str) -> bool:
        if name in {"Texture1", "Texture2", "Notes", "Calpin"}:
            return True
        if name == "Personnalisé" and self.custom_style.get("mode") == "image":
            value = self.custom_style.get("value")
            return bool(value and Path(value).exists())
        return False

    def toggle_topbar_visibility(self, collapsed: bool) -> None:
        # keep the hide_button visible, toggle others
        targets = [
            self.pin_button,
            self.drag_button,
            self.modify_button,
            self.font_button,
            self.size_button,
            self.resize_button,
            self.opacity_button,
            self.color_button,
            self.style_button,
        ]
        for w in targets:
            w.setVisible(not collapsed)
        self.set_hide_icon(expanded=not collapsed)

    def set_hide_icon(self, expanded: bool) -> None:
        icon_path = self.hide_icon_path if expanded else self.see_icon_path
        if icon_path.exists():
            self.hide_button.setIcon(QIcon(str(icon_path)))
            self.hide_button.setIconSize(QSize(18, 18))
        self.hide_button.setToolTip("Masquer les commandes" if expanded else "Afficher les commandes")

    def update_debug_button_visibility(self, theme_name: str) -> None:
        is_image = self.is_image_theme(theme_name)
        self.modify_button.setVisible(is_image)
        if not is_image:
            self._overlay_enabled = False
            self.modify_button.setChecked(False)
            self.overlay.hide()

    def toggle_overlay_mode(self, enabled: bool) -> None:
        if not self.is_image_theme(self.theme_combo.currentText()):
            self.modify_button.setChecked(False)
            self.overlay.hide()
            return
        self._overlay_enabled = enabled
        self.overlay.setVisible(enabled)
        self.overlay.raise_()
        self.overlay.setGeometry(self.editor_container.rect())
        self.overlay.update()

    def get_editor_margins(self) -> tuple[int, int, int, int]:
        theme = self.theme_combo.currentText()
        return self.get_margins_for_theme(theme)

    def apply_current_font(self) -> None:
        fam = QFont().family() if self.current_font_name == "Défaut" else self.current_font_name
        f = QFont(fam, self.current_font_size)
        # setCurrentFont affects new text and caret, not existing formatted runs
        self.editor.setCurrentFont(f)
        self.update_font_menu_checks(self.current_font_name)

    def apply_editor_margins(self, theme_name: str) -> None:
        margins = self.get_margins_for_theme(theme_name)
        self.editor_layout.setContentsMargins(*margins)
        if self._overlay_enabled:
            self.overlay.setGeometry(self.editor_container.rect())
            self.overlay.update()

    def apply_char_format(self, fmt: QTextCharFormat) -> None:
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
            self.editor.setTextCursor(cursor)
        else:
            self.editor.mergeCurrentCharFormat(fmt)

    def apply_font_family_to_cursor(self, family: str) -> None:
        fam = QFont().family() if family == "Défaut" else family
        fmt = QTextCharFormat()
        fmt.setFontFamily(fam)
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
            self.editor.setTextCursor(cursor)
        else:
            self.editor.mergeCurrentCharFormat(fmt)

    def apply_font_size(self, size: int, commit: bool) -> None:
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            self.editor.mergeCurrentCharFormat(fmt)
        else:
            self.editor.mergeCurrentCharFormat(fmt)
        if commit:
            self.current_font_size = size
            self.save_font_config()

    def set_autostart(self, enabled: bool) -> None:
        self.autostart_enabled = enabled
        self.save_autostart_config(enabled)
        if not sys.platform.startswith("win") or winreg is None:
            return
        try:
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    if getattr(sys, "frozen", False):
                        cmd = f'"{sys.executable}"'
                    else:
                        script_path = Path(sys.argv[0]).resolve()
                        cmd = f'"{sys.executable}" "{script_path}"'
                    winreg.SetValueEx(key, "BlocNoteEpinglé", 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, "BlocNoteEpinglé")
                    except FileNotFoundError:
                        pass
        except Exception:
            pass

    def apply_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(alignment)
        if cursor.hasSelection():
            cursor.mergeBlockFormat(block_fmt)
        else:
            cursor.setBlockFormat(block_fmt)
        self.editor.setTextCursor(cursor)

    def get_margins_for_theme(self, theme_name: str) -> tuple[int, int, int, int]:
        data = self.layout_config.get(theme_name)
        if isinstance(data, list) and len(data) == 4:
            return tuple(int(v) for v in data)  # type: ignore[return-value]
        return self.default_margins

    def save_margins_for_theme(self, theme_name: str, margins: tuple[int, int, int, int]) -> None:
        self.layout_config[theme_name] = list(margins)
        self.layout_config_path.write_text(json.dumps(self.layout_config, indent=2), encoding="utf-8")

    def save_theme_config(self, theme_name: str) -> None:
        data = {"theme": theme_name}
        self.theme_config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save_font_config(self) -> None:
        data = {"current": self.current_font_name, "size": self.current_font_size}
        self.font_config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save_color_config(self) -> None:
        data = {"mode": self.current_color_mode, "colors": self.current_colors}
        self.color_config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save_opacity_config(self) -> None:
        data = {"opacity": self.opacity_value}
        self.opacity_config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save_custom_style(self) -> None:
        self.custom_style_path.write_text(json.dumps(self.custom_style, indent=2), encoding="utf-8")

    def save_autostart_config(self, enabled: bool) -> None:
        self.autostart_config_path.write_text(json.dumps({"enabled": enabled}, indent=2), encoding="utf-8")

    def load_layout_config(self) -> dict:
        default = {
            "Notes": list(self.default_margins),
            "Calpin": list(self.default_margins),
        }
        if self.layout_config_path.exists():
            try:
                loaded = json.loads(self.layout_config_path.read_text(encoding="utf-8"))
                # migrate anciens noms
                if "Texture1" in loaded and "Notes" not in loaded:
                    loaded["Notes"] = loaded.get("Texture1")
                if "Texture2" in loaded and "Calpin" not in loaded:
                    loaded["Calpin"] = loaded.get("Texture2")
                default.update(loaded)
            except Exception:
                pass
        return default

    def open_resize_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Redimensionner la note")
        layout = QVBoxLayout(dialog)

        base_w = self.base_size.width()
        base_h = self.base_size.height()
        current_w = self.width()
        current_h = self.height()

        def pct(val, base):
            return max(60, min(200, int(val / base * 100)))

        slider_w = QSlider(Qt.Horizontal)
        slider_w.setMinimum(60)
        slider_w.setMaximum(200)
        slider_w.setValue(pct(current_w, base_w))
        label_w = QLabel(f"Largeur : {slider_w.value()}%")

        slider_h = QSlider(Qt.Horizontal)
        slider_h.setMinimum(60)
        slider_h.setMaximum(200)
        slider_h.setValue(pct(current_h, base_h))
        label_h = QLabel(f"Hauteur : {slider_h.value()}%")

        def apply_preview() -> None:
            w = int(base_w * slider_w.value() / 100)
            h = int(base_h * slider_h.value() / 100)
            self.resize(w, h)
            label_w.setText(f"Largeur : {slider_w.value()}%")
            label_h.setText(f"Hauteur : {slider_h.value()}%")

        slider_w.valueChanged.connect(lambda _: apply_preview())
        slider_h.valueChanged.connect(lambda _: apply_preview())

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)

        def on_cancel():
            self.resize(current_w, current_h)
            dialog.reject()

        buttons.rejected.connect(on_cancel)

        layout.addWidget(label_w)
        layout.addWidget(slider_w)
        layout.addWidget(label_h)
        layout.addWidget(slider_h)
        layout.addWidget(buttons)

        dialog.exec()

    def load_theme_config(self) -> dict:
        default = {"theme": "Papier"}
        if self.theme_config_path.exists():
            try:
                loaded = json.loads(self.theme_config_path.read_text(encoding="utf-8"))
                default.update(loaded)
            except Exception:
                pass
        return default

    def load_font_config(self) -> dict:
        default = {"current": "Défaut"}
        if self.font_config_path.exists():
            try:
                loaded = json.loads(self.font_config_path.read_text(encoding="utf-8"))
                default.update(loaded)
            except Exception:
                pass
        return default

    def load_color_config(self) -> dict:
        default = {"mode": "solid", "colors": ["#2f2a1f", "#2f2a1f"]}
        if self.color_config_path.exists():
            try:
                loaded = json.loads(self.color_config_path.read_text(encoding="utf-8"))
                default.update(loaded)
            except Exception:
                pass
        return default

    def load_opacity_config(self) -> float:
        default_opacity = 1.0
        if self.opacity_config_path.exists():
            try:
                data = json.loads(self.opacity_config_path.read_text(encoding="utf-8"))
                val = float(data.get("opacity", default_opacity))
                return max(0.3, min(1.0, val))
            except Exception:
                pass
        return default_opacity

    def load_custom_style(self) -> dict:
        default = {"mode": "color", "value": "#f7f1dc"}
        if self.custom_style_path.exists():
            try:
                loaded = json.loads(self.custom_style_path.read_text(encoding="utf-8"))
                default.update(loaded)
            except Exception:
                pass
        return default

    def load_autostart_config(self) -> bool:
        if self.autostart_config_path.exists():
            try:
                data = json.loads(self.autostart_config_path.read_text(encoding="utf-8"))
                return bool(data.get("enabled", False))
            except Exception:
                pass
        return False

    def on_overlay_margins_changed(self, margins: tuple[int, int, int, int]) -> None:
        theme = self.theme_combo.currentText()
        if not self.is_image_theme(theme):
            return
        self.editor_layout.setContentsMargins(*margins)
        self.save_margins_for_theme(theme, margins)

    def build_font_menu(self) -> None:
        self.font_menu.clear()
        default_action = self.font_menu.addAction("Défaut")
        default_action.setCheckable(True)
        default_action.triggered.connect(lambda checked: self.select_font(None))
        self.font_menu.addSeparator()

        for fam in sorted(self.font_families.keys()):
            act = self.font_menu.addAction(fam)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, f=fam: self.select_font(f))
        self.update_font_menu_checks(self.current_font_name)

    def build_color_menu(self) -> None:
        self.color_menu.clear()
        modes = [
            ("solid", "Couleur pleine"),
            ("horizontal", "Dégradé horizontal"),
            ("vertical", "Dégradé vertical"),
        ]
        for key, label in modes:
            act = self.color_menu.addAction(label)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, m=key: self.select_color_mode(m))
        self.color_menu.addSeparator()
        pick1 = self.color_menu.addAction("Couleur 1…")
        pick1.triggered.connect(lambda: self.pick_color(0))
        pick2 = self.color_menu.addAction("Couleur 2…")
        pick2.triggered.connect(lambda: self.pick_color(1))
        self.update_color_menu_checks(self.current_color_mode)

    def solid_color_stylesheet(self, color: str) -> str:
        return f'''
        #StickyRoot {{
            background-color: {color};
            color: #2f2a1f;
            font-size: 13px;
        }}
        #StickyRoot #EditorContainer {{
            background-color: {color};
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 8px;
        }}
        #StickyRoot QTextEdit {{
            background: {color};
            border: none;
            border-radius: 6px;
            padding: 12px;
            selection-background-color: rgba(0, 0, 0, 0.12);
        }}
        #StickyRoot QTextEdit QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px 2px 2px 0;
        }}
        #StickyRoot QTextEdit QScrollBar::handle:vertical {{
            background: rgba(0, 0, 0, 0.28);
            border-radius: 5px;
            min-height: 24px;
        }}
        #StickyRoot QTextEdit QScrollBar::add-line:vertical,
        #StickyRoot QTextEdit QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        #StickyRoot QTextEdit QScrollBar:horizontal {{ height: 0px; }}
        #StickyRoot QComboBox, #StickyRoot QCheckBox, #StickyRoot QLabel {{
            background: transparent;
            border: none;
            padding: 4px;
        }}
        '''

    def load_fonts(self) -> dict[str, str]:
        families: dict[str, str] = {}
        if not self.fonts_dir.exists():
            return families
        for ttf in self.fonts_dir.rglob("*.ttf"):
            fid = QFontDatabase.addApplicationFont(str(ttf))
            if fid == -1:
                continue
            for fam in QFontDatabase.applicationFontFamilies(fid):
                families[fam] = fam
        return families

    def setup_format_shortcuts(self) -> None:
        bold_act = QAction("Gras", self.editor)
        bold_act.setShortcut("Ctrl+B")
        bold_act.triggered.connect(self.toggle_bold)
        italic_act = QAction("Italique", self.editor)
        italic_act.setShortcut("Ctrl+I")
        italic_act.triggered.connect(self.toggle_italic)
        underline_act = QAction("Souligné", self.editor)
        underline_act.setShortcut("Ctrl+U")
        underline_act.triggered.connect(self.toggle_underline)
        align_left = QAction("Aligner gauche", self.editor)
        align_left.setShortcut("Ctrl+L")
        align_left.triggered.connect(lambda: self.apply_alignment(Qt.AlignLeft))
        align_center = QAction("Aligner centre", self.editor)
        align_center.setShortcut("Ctrl+C")
        align_center.triggered.connect(lambda: self.apply_alignment(Qt.AlignHCenter))
        align_right = QAction("Aligner droite", self.editor)
        align_right.setShortcut("Ctrl+R")
        align_right.triggered.connect(lambda: self.apply_alignment(Qt.AlignRight))
        align_justify = QAction("Justifier", self.editor)
        align_justify.setShortcut("Ctrl+J")
        align_justify.triggered.connect(lambda: self.apply_alignment(Qt.AlignJustify))

        for act in (bold_act, italic_act, underline_act, align_left, align_center, align_right, align_justify):
            act.setShortcutContext(Qt.WidgetWithChildrenShortcut)
            self.editor.addAction(act)

    def toggle_bold(self) -> None:
        fmt = QTextCharFormat()
        current = self.editor.currentCharFormat().fontWeight()
        fmt.setFontWeight(QFont.Normal if current > QFont.Normal else QFont.Bold)
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_italic(self) -> None:
        fmt = QTextCharFormat()
        current = self.editor.currentCharFormat().fontItalic()
        fmt.setFontItalic(not current)
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_underline(self) -> None:
        fmt = QTextCharFormat()
        current = self.editor.currentCharFormat().fontUnderline()
        fmt.setFontUnderline(not current)
        self.editor.mergeCurrentCharFormat(fmt)

    def apply_color_scheme(self) -> None:
        mode = self.current_color_mode
        colors = self.current_colors
        fmt = QTextCharFormat()
        if mode == "solid":
            fmt.setForeground(QColor(colors[0]))
        else:
            grad = QLinearGradient(0, 0, 1 if mode == "horizontal" else 0, 1 if mode == "vertical" else 0)
            grad.setCoordinateMode(QGradient.ObjectMode)
            grad.setColorAt(0.0, QColor(colors[0]))
            grad.setColorAt(1.0, QColor(colors[1]))
            fmt.setForeground(QBrush(grad))
        self.apply_char_format(fmt)

    def compute_flags(self, pinned: bool) -> Qt.WindowType:
        flags = Qt.FramelessWindowHint | Qt.Window | Qt.CustomizeWindowHint
        if pinned:
            flags |= Qt.WindowStaysOnTopHint
        return flags

    def register_global_hotkey(self) -> None:
        if not sys.platform.startswith("win"):
            return
        MOD_CONTROL = 0x0002
        VK_H = 0x48
        hwnd = int(self.winId())
        if ctypes.windll.user32.RegisterHotKey(hwnd, self.hotkey_id, MOD_CONTROL, VK_H):
            self._hotkey_registered = True

    def unregister_global_hotkey(self) -> None:
        if not sys.platform.startswith("win") or not self._hotkey_registered:
            return
        hwnd = int(self.winId())
        ctypes.windll.user32.UnregisterHotKey(hwnd, self.hotkey_id)
        self._hotkey_registered = False

    def toggle_visibility_from_hotkey(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show_window()

    def open_size_dialog(self) -> None:
        html_before = self.editor.toHtml()
        cursor_before = self.editor.textCursor()

        dialog = QDialog(self)
        dialog.setWindowTitle("Taille et alignement")
        layout = QVBoxLayout(dialog)
        label = QLabel(f"Taille : {self.current_font_size}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(8)
        slider.setMaximum(48)
        slider.setValue(self.current_font_size)
        slider.valueChanged.connect(lambda v: label.setText(f"Taille : {v}"))
        slider.valueChanged.connect(lambda v: self.preview_font_size(v))

        align_row = QHBoxLayout()
        align_label = QLabel("Alignement :")
        btn_left = QPushButton("G")
        btn_center = QPushButton("C")
        btn_right = QPushButton("D")
        btn_justify = QPushButton("J")
        for b in (btn_left, btn_center, btn_right, btn_justify):
            b.setCheckable(True)
            b.setFixedWidth(28)
        align_group = [btn_left, btn_center, btn_right, btn_justify]

        current_align = self.editor.textCursor().blockFormat().alignment()
        if current_align & Qt.AlignJustify:
            btn_justify.setChecked(True)
        elif current_align & Qt.AlignRight:
            btn_right.setChecked(True)
        elif current_align & Qt.AlignHCenter:
            btn_center.setChecked(True)
        else:
            btn_left.setChecked(True)

        def set_align(btn, align):
            def handler():
                for b in align_group:
                    b.setChecked(b is btn)
                self.apply_alignment(align)
            return handler

        btn_left.clicked.connect(set_align(btn_left, Qt.AlignLeft))
        btn_center.clicked.connect(set_align(btn_center, Qt.AlignHCenter))
        btn_right.clicked.connect(set_align(btn_right, Qt.AlignRight))
        btn_justify.clicked.connect(set_align(btn_justify, Qt.AlignJustify))

        align_row.addWidget(align_label)
        for b in align_group:
            align_row.addWidget(b)
        align_row.addStretch(1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        def on_cancel():
            self.editor.setHtml(html_before)
            self.editor.setTextCursor(cursor_before)
            self.apply_current_font()
            dialog.reject()
        buttons.rejected.connect(on_cancel)

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addLayout(align_row)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            size = slider.value()
            self.apply_font_size(size, commit=True)
        else:
            self.preview_font_size(self.current_font_size)

    def choose_custom_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not path:
            return
        self.custom_style = {"mode": "image", "value": path}
        self.save_custom_style()
        self.select_theme("Personnalisé")
        self.apply_theme("Personnalisé")

    def choose_custom_color(self) -> None:
        initial = QColor(self.custom_style.get("value", "#f7f1dc"))
        color = QColorDialog.getColor(initial, self, "Choisir une couleur de fond")
        if not color.isValid():
            return
        self.custom_style = {"mode": "color", "value": color.name()}
        self.save_custom_style()
        self.select_theme("Personnalisé")
        self.apply_theme("Personnalisé")

    def open_opacity_dialog(self) -> None:
        previous = self.opacity_value
        dialog = QDialog(self)
        dialog.setWindowTitle("Opacité de la note")
        layout = QVBoxLayout(dialog)

        label = QLabel(f"Opacité : {int(previous * 100)}%")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(30)
        slider.setMaximum(100)
        slider.setValue(int(previous * 100))

        def preview(val: int) -> None:
            self.opacity_value = val / 100.0
            self.setWindowOpacity(self.opacity_value)
            label.setText(f"Opacité : {val}%")

        slider.valueChanged.connect(preview)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)

        def on_cancel() -> None:
            self.opacity_value = previous
            self.setWindowOpacity(self.opacity_value)
            dialog.reject()

        buttons.rejected.connect(on_cancel)

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            self.save_opacity_config()
        else:
            self.opacity_value = previous
            self.setWindowOpacity(self.opacity_value)

    def preview_font_size(self, size: int) -> None:
        self.apply_font_size(size, commit=False)

    def texture_stylesheet(self, texture_path: Path) -> str:
        if not texture_path.exists():
            return THEMES["Papier"]

        url = texture_path.as_posix()
        return f'''
        #StickyRoot {{
            background: transparent;
            color: #2f2a1f;
            font-size: 13px;
        }}
        #StickyRoot #EditorContainer {{
            border-image: url("{url}") 0 0 0 0 stretch stretch;
            background: transparent;
        }}
        #StickyRoot QTextEdit {{
            background: transparent;
            border: none;
            border-radius: 10px;
            padding: 12px;
            selection-background-color: rgba(217, 200, 143, 0.6);
        }}
        #StickyRoot QTextEdit QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px 2px 2px 0;
        }}
        #StickyRoot QTextEdit QScrollBar::handle:vertical {{
            background: rgba(0, 0, 0, 0.28);
            border-radius: 5px;
            min-height: 24px;
        }}
        #StickyRoot QTextEdit QScrollBar::add-line:vertical,
        #StickyRoot QTextEdit QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        #StickyRoot QTextEdit QScrollBar:horizontal {{ height: 0px; }}
        #StickyRoot QComboBox, #StickyRoot QCheckBox, #StickyRoot QLabel {{
            background: transparent;
            border: none;
            padding: 4px;
        }}
        '''


def main() -> int:
    app = QApplication(sys.argv)
    icon_file = resource_path("icon.ico")
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))
    window = StickyNoteWindow()
    window.show()
    return app.exec()


class MarginOverlay(QWidget):
    HANDLE = 8
    MIN_WIDTH = 120
    MIN_HEIGHT = 120

    def __init__(self, parent: QWidget, get_margins, set_margins) -> None:
        super().__init__(parent)
        self.get_margins = get_margins
        self.set_margins_cb = set_margins
        self.active_edges: set[str] = set()
        self.last_pos: QPoint | None = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        self.raise_()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        inner = self.inner_rect()
        pen = QPen(QColor(38, 118, 255), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(QColor(38, 118, 255, 40))
        painter.drawRect(inner)

    def inner_rect(self) -> QRect:
        l, t, r, b = self.get_margins()
        return self.rect().adjusted(l, t, -r, -b)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            return
        pos = event.position().toPoint()
        rect = self.inner_rect()
        self.active_edges = self.hit_edges(rect, pos)
        self.last_pos = pos
        if self.active_edges:
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if not self.active_edges or self.last_pos is None:
            return super().mouseMoveEvent(event)
        pos = event.position().toPoint()
        l, t, r, b = self.get_margins()
        w, h = self.width(), self.height()

        if "l" in self.active_edges:
            l = max(0, min(pos.x(), w - r - self.MIN_WIDTH))
        if "r" in self.active_edges:
            r = max(0, min(w - pos.x(), w - l - self.MIN_WIDTH))
        if "t" in self.active_edges:
            t = max(0, min(pos.y(), h - b - self.MIN_HEIGHT))
        if "b" in self.active_edges:
            b = max(0, min(h - pos.y(), h - t - self.MIN_HEIGHT))

        self.set_margins_cb((l, t, r, b))
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self.active_edges = set()
            self.last_pos = None
        super().mouseReleaseEvent(event)

    def hit_edges(self, rect: QRect, pos: QPoint) -> set[str]:
        edges: set[str] = set()
        if abs(pos.x() - rect.left()) <= self.HANDLE:
            edges.add("l")
        if abs(pos.x() - rect.right()) <= self.HANDLE:
            edges.add("r")
        if abs(pos.y() - rect.top()) <= self.HANDLE:
            edges.add("t")
        if abs(pos.y() - rect.bottom()) <= self.HANDLE:
            edges.add("b")
        return edges


if __name__ == "__main__":
    raise SystemExit(main())
