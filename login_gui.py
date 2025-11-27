from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import qtawesome as qta
from localization import LocalizationManager


class BiometricThread(QThread):
    """
    Окремий потік для виконання біометричної перевірки.
    Це запобігає зависанню вікна програми.
    """
    # Сигнал, який буде відправлено після завершення перевірки (True/False)
    result_signal = pyqtSignal(bool)

    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager

    def run(self):
        success = self.auth_manager.verify_biometrics()
        self.result_signal.emit(success)


class BaseAuthDialog(QDialog):
    """Базовий клас для вікон авторизації."""

    def __init__(self, auth_manager, loc, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.loc = loc
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 280)

        self.setStyleSheet("""
            QDialog { background-color: #282C36; color: #ABB2BF; font-family: 'Segoe UI'; font-size: 14px; }
            QLineEdit { background-color: #3E4451; border: 1px solid #5C6370; border-radius: 5px; padding: 8px; color: white; }
            QPushButton { background-color: #61AFEF; color: white; border-radius: 5px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #52A0DC; }
            QPushButton:disabled { background-color: #4B5263; color: #787C85; } /* Стиль для неактивної кнопки */
            QLabel { color: #ABB2BF; font-weight: bold; }
        """)


class RegistrationDialog(BaseAuthDialog):
    def __init__(self, auth_manager, loc):
        super().__init__(auth_manager, loc)
        self.setWindowTitle(self.loc.get("auth_register_title"))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(self.loc.get("auth_password_label")))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        layout.addWidget(QLabel(self.loc.get("auth_confirm_label")))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        self.btn_save = QPushButton(self.loc.get("auth_register_button"))
        self.btn_save.clicked.connect(self.register)
        layout.addWidget(self.btn_save)

    def register(self):
        p1 = self.pass_input.text()
        p2 = self.confirm_input.text()

        if not p1:
            QMessageBox.warning(self, "Error", self.loc.get("auth_error_empty"))
            return
        if p1 != p2:
            QMessageBox.warning(self, "Error", self.loc.get("auth_error_mismatch"))
            return

        self.auth_manager.register_password(p1)
        QMessageBox.information(self, "Success", self.loc.get("auth_success_register"))
        self.accept()


class LoginDialog(BaseAuthDialog):
    def __init__(self, auth_manager, loc):
        super().__init__(auth_manager, loc)
        self.setWindowTitle(self.loc.get("auth_login_title"))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.lock", color="#61AFEF").pixmap(QSize(40, 40)))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText(self.loc.get("auth_password_label"))
        layout.addWidget(self.pass_input)

        self.btn_login = QPushButton(self.loc.get("auth_login_button"))
        self.btn_login.clicked.connect(self.check_password)
        layout.addWidget(self.btn_login)

        self.btn_bio = QPushButton(self.loc.get("auth_biometric_button"))
        self.btn_bio.setStyleSheet("background-color: #3E4451; border: 1px solid #5C6370;")
        self.btn_bio.setIcon(qta.icon("fa5s.fingerprint", color="#98C379"))
        self.btn_bio.clicked.connect(self.start_biometric_check)  # Змінено слот
        layout.addWidget(self.btn_bio)

        # Лейбл статусу (щоб писати "Перевірка...")
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #98C379; font-size: 12px;")
        layout.addWidget(self.status_label)

    def check_password(self):
        password = self.pass_input.text()
        if self.auth_manager.verify_password(password):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", self.loc.get("auth_error_incorrect"))
            self.pass_input.clear()

    def start_biometric_check(self):
        """Запускає перевірку в окремому потоці."""
        # 1. Блокуємо інтерфейс, щоб користувач не натискав зайвого
        self.btn_bio.setEnabled(False)
        self.btn_login.setEnabled(False)
        self.pass_input.setEnabled(False)
        self.status_label.setText("Очікування Windows Hello...")

        # 2. Створюємо та налаштовуємо потік
        self.bio_thread = BiometricThread(self.auth_manager)
        self.bio_thread.result_signal.connect(self.on_biometric_result)

        # 3. Запускаємо
        self.bio_thread.start()

    def on_biometric_result(self, success):
        """Викликається, коли потік завершив роботу."""
        # Розблокуємо інтерфейс
        self.btn_bio.setEnabled(True)
        self.btn_login.setEnabled(True)
        self.pass_input.setEnabled(True)
        self.status_label.setText("")

        if success:
            self.accept()  # Закриваємо вікно з успіхом
        else:
            QMessageBox.warning(self, "Biometrics", self.loc.get("auth_biometric_failed"))