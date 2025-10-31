# main.py
import tkinter as tk
import logging
from gui import FinanceAppGUI


def setup_logging():
    """Налаштовує базову конфігурацію логування."""
    logging.basicConfig(
        level=logging.INFO,  # Мінімальний рівень логування (INFO, DEBUG, WARNING, ERROR)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='app.log',  # Назва файлу для логів
        filemode='w'  # 'w' - перезаписувати файл при кожному запуску, 'a' - дозаписувати
    )


def main():
    """Основна функція для запуску програми."""
    setup_logging()
    logging.info("Запуск програми 'Фінансовий Асистент'")

    root = tk.Tk()
    app = FinanceAppGUI(root)
    root.mainloop()

    logging.info("Програму закрито коректно.")


if __name__ == "__main__":
    main()