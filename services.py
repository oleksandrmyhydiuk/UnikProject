# services.py
import logging
from datetime import datetime
import os

from models import (User, Account, Report, SpendingReport, CategorizedTransaction,
                    Budget, Debt, SavingsGoal)
from database import DatabaseManager
from exceptions import InsufficientFundsError

logger = logging.getLogger(__name__)


class FinanceService:
    """
    Клас-сервіс, що інкапсулює всю бізнес-логіку фінансового асистента.
    Він не залежить від графічного інтерфейсу.
    """

    def __init__(self, user: User, db_manager: DatabaseManager):
        self._user = user
        self._db_manager = db_manager
        self._current_account_name = None

        # --- НОВЕ: Завантажуємо борги та цілі при старті ---
        self._debts = self._db_manager.load_debts()
        self._goals = self._db_manager.load_goals()

        logger.info("Сервіс 'FinanceService' успішно ініціалізовано.")
        logger.info(f"Завантажено {len(self._debts)} боргів та {len(self._goals)} цілей.")

    def set_current_account(self, name: str):
        """Встановлює поточний активний рахунок."""
        if name in self._user.accounts:
            self._current_account_name = name
            logger.info(f"Встановлено поточний рахунок: {name}")
        else:
            logger.error(f"Спроба встановити неіснуючий рахунок: {name}")
            raise ValueError(f"Рахунок з іменем '{name}' не знайдено.")

    def get_current_account(self) -> Account:
        """Повертає об'єкт поточного рахунку."""
        if not self._current_account_name:
            logger.error("Спроба отримати рахунок до його встановлення.")
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
        account.add_transaction(transaction, is_income)

        self._db_manager.save_transaction(self._current_account_name, transaction, is_income)

        log_type = "Дохід" if is_income else "Витрата"
        logger.info(
            f"Додано нову транзакцію ({log_type}): Сума={amount}, Категорія='{category}' для рахунку '{self._current_account_name}'")

    def generate_report(self, report_type: type[Report]) -> tuple[str, str]:
        """
        Поліморфний метод для генерації та збереження будь-якого звіту.
        Повертає кортеж (текст_звіту, шлях_до_файлу).
        """
        report_name = report_type.__name__
        logger.info(f"Початок генерації звіту типу '{report_name}' для рахунку '{self._current_account_name}'...")

        account = self.get_current_account()
        report_generator = report_type(account)

        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        data = report_generator.generate(start_date, end_date)

        report_title_base = "Звіт про витрати" if report_name == "SpendingReport" else "Звіт про доходи"
        report_title = f"{report_title_base} з {start_date} по {end_date}"
        report_text = report_title + "\n\n"

        if not data:
            report_text += "Даних за цей період немає."
            logger.info("Для звіту не знайдено даних.")
        else:
            total = sum(data.values())
            for key, value in data.items():
                report_text += f"- {key}: {value:.2f} грн\n"
            report_text += f"\nУсього: {total:.2f} грн"

        file_prefix = "spending_report" if report_name == "SpendingReport" else "income_report"
        filename = f"{file_prefix}_{datetime.now().strftime('%Y-%m')}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_text)
            full_path = os.path.abspath(filename)
            logger.info(f"Звіт '{report_name}' успішно згенеровано та збережено у файл: {filename}")
            return report_text, full_path
        except IOError as e:
            logger.error(f"Помилка запису звіту у файл {filename}: {e}", exc_info=True)
            raise IOError(f"Не вдалося зберегти файл звіту: {e}")

    def load_debts_data(self) -> list[Debt]:
        """Повертає список завантажених боргів."""
        return self._debts

    def add_debt(self, name: str, amount: float, due_date: str, is_loan: bool):
        """Додає новий борг."""
        new_debt = Debt(id=None, name=name, amount=amount, due_date=due_date, is_loan=is_loan, is_paid=False)
        new_id = self._db_manager.save_debt(new_debt)
        new_debt.id = new_id
        self._debts.append(new_debt)
        logger.info(f"Додано новий борг: {name} (Сума: {amount})")

    def update_debt_status(self, debt_id: int, is_paid: bool):
        """Оновлює статус боргу (оплачено/не оплачено)."""
        debt = next((d for d in self._debts if d.id == debt_id), None)
        if debt:
            debt.is_paid = is_paid
            self._db_manager.update_debt(debt)
            logger.info(f"Оновлено статус боргу ID {debt_id} на {'Оплачено' if is_paid else 'Не оплачено'}")
        else:
            logger.warning(f"Спроба оновити неіснуючий борг ID: {debt_id}")
            raise ValueError("Борг не знайдено.")

    def load_goals_data(self) -> list[SavingsGoal]:
        """Повертає список завантажених цілей."""
        return self._goals

    def add_savings_goal(self, name: str, target_amount: float):
        """Додає нову ціль заощаджень."""
        new_goal = SavingsGoal(id=None, name=name, target_amount=target_amount, current_amount=0.0)
        new_id = self._db_manager.save_goal(new_goal)
        new_goal.id = new_id
        self._goals.append(new_goal)
        logger.info(f"Додано нову ціль: {name} (Ціль: {target_amount})")

    def add_contribution_to_goal(self, goal_id: int, amount: float):
        """
        Додає внесок до цілі.
        Це також створює транзакцію витрати в основному рахунку.
        """
        goal = next((g for g in self._goals if g.id == goal_id), None)
        if not goal:
            logger.warning(f"Спроба додати внесок до неіснуючої цілі ID: {goal_id}")
            raise ValueError("Ціль не знайдено.")

        # 1. Створюємо транзакцію витрати
        # InsufficientFundsError буде згенеровано тут, якщо грошей немає
        self.add_transaction(
            amount=amount,
            description=f"Внесок до цілі: {goal.name}",
            category="Заощадження",
            is_income=False
        )

        # 2. Якщо транзакція пройшла, оновлюємо ціль
        goal.add_contribution(amount)
        self._db_manager.update_goal(goal)
        logger.info(f"Додано внесок {amount} грн до цілі '{goal.name}'")

    def get_spending_analysis(self) -> dict:
        """
        Аналізує фінансові звички.
        Повертає топ-5 категорій витрат.
        """
        account = self.get_current_account()
        # Використовуємо існуючий SpendingReport
        start_date = "2000-01-01"  # За весь час
        end_date = datetime.now().strftime('%Y-%m-%d')

        spending_data = SpendingReport(account).generate(start_date, end_date)

        # Сортуємо категорії за сумою витрат
        sorted_spending = sorted(spending_data.items(), key=lambda item: item[1], reverse=True)

        return dict(sorted_spending[:5])  # Повертаємо топ 5