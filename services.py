from datetime import datetime
import os

from models import User, Account, Report, CategorizedTransaction, Budget
from database import DatabaseManager
from exceptions import InsufficientFundsError


class FinanceService:
    """
    Клас-сервіс, що інкапсулює всю бізнес-логіку фінансового асистента.
    Він не залежить від графічного інтерфейсу.
    """

    def __init__(self, user: User, db_manager: DatabaseManager):
        self._user = user
        self._db_manager = db_manager
        self._current_account_name = None

    def set_current_account(self, name: str):
        """Встановлює поточний активний рахунок."""
        if name in self._user.accounts:
            self._current_account_name = name
        else:
            raise ValueError(f"Рахунок з іменем '{name}' не знайдено.")

    def get_current_account(self) -> Account:
        """Повертає об'єкт поточного рахунку."""
        if not self._current_account_name:
            raise ValueError("Поточний рахунок не встановлено.")
        return self._user.accounts[self._current_account_name]

    def add_transaction(self, amount: float, description: str, category: str, is_income: bool):
        """
        Основний метод для додавання транзакції.
        Виконує валідацію, оновлює стан рахунку та зберігає в БД.
        """
        if is_income:
            category = "Дохід"

        date = datetime.now().strftime('%Y-%m-%d')
        transaction = CategorizedTransaction(amount, date, description, category)

        account = self.get_current_account()
        # Логіка перевірки балансу та оновлення стану інкапсульована в Account
        account.add_transaction(transaction, is_income)

        # Збереження в БД
        self._db_manager.save_transaction(self._current_account_name, transaction, is_income)

    def generate_report(self, report_type: type[Report]) -> tuple[str, str]:
        """
        Поліморфний метод для генерації та збереження будь-якого звіту.
        Повертає кортеж (текст_звіту, шлях_до_файлу).
        """
        account = self.get_current_account()
        report_generator = report_type(account)

        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        data = report_generator.generate(start_date, end_date)

        report_title_base = "Звіт про витрати" if report_generator.__class__.__name__ == "SpendingReport" else "Звіт про доходи"
        report_title = f"{report_title_base} з {start_date} по {end_date}"
        report_text = report_title + "\n\n"

        if not data:
            report_text += "Даних за цей період немає."
        else:
            total = sum(data.values())
            for key, value in data.items():
                report_text += f"- {key}: {value:.2f} грн\n"
            report_text += f"\nУсього: {total:.2f} грн"

        # Збереження звіту у файл
        file_prefix = "spending_report" if report_generator.__class__.__name__ == "SpendingReport" else "income_report"
        filename = f"{file_prefix}_{datetime.now().strftime('%Y-%m')}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)

        full_path = os.path.abspath(filename)
        return report_text, full_path