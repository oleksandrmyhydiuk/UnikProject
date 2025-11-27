import sys
import logging
from PyQt5.QtWidgets import QApplication, QDialog
from gui import FinanceAppGUI
from auth import AuthManager
from login_gui import LoginDialog, RegistrationDialog
from localization import LocalizationManager


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='w'
    )


def main():
    setup_logging()
    logging.info("Запуск програми 'Фінансовий Асистент' на PyQt5")

    app = QApplication(sys.argv)

    # Ініціалізація допоміжних менеджерів
    auth_manager = AuthManager()
    loc = LocalizationManager(default_lang='uk')  # Для перекладу вікна входу

    # 1. Перевірка наявності реєстрації
    if not auth_manager.is_registered():
        logging.info("Пароль не знайдено. Запуск реєстрації.")
        reg_dialog = RegistrationDialog(auth_manager, loc)
        if reg_dialog.exec_() != QDialog.Accepted:
            logging.info("Реєстрацію скасовано. Вихід.")
            sys.exit()  # Якщо користувач закрив вікно реєстрації - виходимо

    # 2. Вхід у систему
    logging.info("Запуск вікна входу.")
    login_dialog = LoginDialog(auth_manager, loc)
    if login_dialog.exec_() == QDialog.Accepted:
        logging.info("Авторизація успішна. Запуск головного вікна.")
        window = FinanceAppGUI(app)
        window.show()
        sys.exit(app.exec_())
    else:
        logging.info("Авторизацію скасовано або не пройдено. Вихід.")
        sys.exit()


if __name__ == "__main__":
    main()