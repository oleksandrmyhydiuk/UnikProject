from PyQt5.QtWidgets import QApplication

# QSS (CSS-подібні стилі) для світлої теми
LIGHT_QSS = """
    QWidget {
        background-color: #F8F8F8;
        color: #333333;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }
    QMainWindow {
        background-color: #F8F8F8;
    }
    QGroupBox {
        background-color: #FFFFFF;
        border: 1px solid #C0C0C0; /* <-- ЗРОБЛЕНО ПОМІТНІШУ МЕЖУ */
        border-radius: 8px;
        margin-top: 20px;
        font-weight: bold;
        color: #333333;
        padding-top: 10px;
        padding-bottom: 5px;
        padding-left: 10px;
        padding-right: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        left: 10px;
        background-color: #FFFFFF;
        border: 1px solid #C0C0C0; /* <-- ЗРОБЛЕНО ПОМІТНІШУ МЕЖУ */
        border-radius: 5px;
        color: #555555;
    }
    QLabel {
        background-color: transparent;
        color: #444444;
    }
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
        background-color: #FFFFFF;
        border: 1px solid #C0C0C0;
        border-radius: 5px;
        padding: 8px;
        color: #333333;
        selection-background-color: #ADD8E6;
    }
    /* ... (решта стилів без змін) ... */
    QPushButton {
        background-color: #007ACC;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        font-weight: bold;
        text-align: left; 
        padding-left: 15px; 
    }
    QPushButton:hover {
        background-color: #006BBF;
    }
    QPushButton:pressed {
        background-color: #0056A0;
    }
    QTreeWidget {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        alternate-background-color: #F9F9F9;
        color: #333333;
        padding: 5px;
    }
    QHeaderView::section {
        background-color: #F0F0F0;
        padding: 8px;
        border: 1px solid #E0E0E0;
        font-weight: bold;
        color: #555555;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    QMenuBar {
        background-color: #F0F0F0;
        color: #333333;
    }
    QMenu {
        background-color: #FFFFFF;
        border: 1px solid #D0D0D0;
        color: #333333;
    }
    QMenu::item:selected {
        background-color: #007ACC;
        color: #FFFFFF;
        border-radius: 3px;
    }
    QMessageBox {
        background-color: #FFFFFF;
        color: #333333;
    }
    QMessageBox QPushButton {
        background-color: #007ACC;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 8px 12px;
    }
"""

# QSS (CSS-подібні стилі) для темної теми
DARK_QSS = """
    QWidget {
        background-color: #282C36; 
        color: #ABB2BF; 
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }
    QMainWindow {
        background-color: #282C36;
    }
    QGroupBox {
        background-color: #353A45; 
        border: 1px solid #4C5261;
        border-radius: 8px;
        margin-top: 20px;
        font-weight: bold;
        color: #DDE2E7;
        padding-top: 10px;
        padding-bottom: 5px;
        padding-left: 10px;
        padding-right: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        left: 10px;
        background-color: #353A45;
        border: 1px solid #4C5261;
        border-radius: 5px;
        color: #9DA5B4;
    }
    QLabel {
        background-color: transparent;
        color: #ABB2BF;
    }
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
        background-color: #3E4451;
        border: 1px solid #5C6370;
        border-radius: 5px;
        padding: 8px;
        color: #ABB2BF;
        selection-background-color: #61AFEF;
    }
    /* ... (решта стилів без змін) ... */
    QPushButton {
        background-color: #61AFEF; 
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        font-weight: bold;
        text-align: left;
        padding-left: 15px;
    }
    QPushButton:hover {
        background-color: #52A0DC;
    }
    QPushButton:pressed {
        background-color: #428EC5;
    }
    QTreeWidget {
        background-color: #353A45;
        border: 1px solid #4C5261;
        border-radius: 8px;
        alternate-background-color: #3A404A;
        color: #ABB2BF;
        padding: 5px;
    }
    QHeaderView::section {
        background-color: #4A515E;
        padding: 8px;
        border: 1px solid #4C5261;
        font-weight: bold;
        color: #9DA5B4;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    QMenuBar {
        background-color: #353A45;
        color: #ABB2BF;
    }
    QMenu {
        background-color: #3E4451;
        border: 1px solid #5C6370;
        color: #ABB2BF;
    }
    QMenu::item:selected {
        background-color: #61AFEF;
        color: #FFFFFF;
        border-radius: 3px;
    }
    QMessageBox {
        background-color: #353A45;
        color: #ABB2BF;
    }
    QMessageBox QPushButton {
        background-color: #61AFEF;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 8px 12px;
    }
"""

class ThemeManager:
    """Керує візуальними темами додатку."""
    def __init__(self, app: QApplication):
        self._app = app

    def apply_theme(self, theme_name: str):
        """Застосовує обрану тему (light або dark)."""
        if theme_name == 'light':
            self._app.setStyleSheet(LIGHT_QSS)
        else: # За замовчуванням або 'dark'
            self._app.setStyleSheet(DARK_QSS)