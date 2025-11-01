import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui import FinanceAppGUI


def setup_logging():
    """Налаштовує базову конфігурацію логування."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='w'
    )


def main():
    """Основна функція для запуску програми."""
    setup_logging()
    logging.info("Запуск програми 'Фінансовий Асистент' на PyQt5")

    # Створення QApplication є обов'язковим для будь-якої PyQt5 програми
    app = QApplication(sys.argv)

    # Створюємо та показуємо головне вікно
    window = FinanceAppGUI(app)  # Передаємо 'app' для керування темами
    window.show()

    # Запускаємо головний цикл програми
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()