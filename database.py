import sqlite3
import logging
from models import CategorizedTransaction, Debt, SavingsGoal

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Керує всіма операціями з базою даних SQLite."""

    def __init__(self, db_name="finance_assistant.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Створює таблиці, якщо вони не існують."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT, amount REAL, date TEXT,
            description TEXT, category TEXT, is_income INTEGER
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, amount REAL, due_date TEXT,
            is_loan INTEGER, is_paid INTEGER
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, target_amount REAL, current_amount REAL
        )''')

        self.conn.commit()
        logger.info("Таблиці баз даних перевірено/створено.")

    # --- Методи для транзакцій ---
    def save_transaction(self, account_name, transaction: CategorizedTransaction, is_income: bool):
        """Зберігає транзакцію в БД."""
        try:
            self.cursor.execute('''
            INSERT INTO transactions (account_name, amount, date, description, category, is_income)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (account_name, transaction.amount, transaction.date, transaction.description, transaction.category,
                  1 if is_income else 0))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Помилка збереження транзакції в БД: {e}")
            self.conn.rollback()

    def load_transactions_for_account(self, account_name) -> tuple[list[CategorizedTransaction], float]:
        """Завантажує всі транзакції для певного рахунку."""
        try:
            self.cursor.execute(
                "SELECT amount, date, description, category, is_income FROM transactions WHERE account_name = ?",
                (account_name,))
            rows = self.cursor.fetchall()
            transactions = []
            balance = 0
            for row in rows:
                amount, date, desc, cat, is_income = row
                t = CategorizedTransaction(amount, date, desc, cat)
                transactions.append(t)
                if is_income:
                    balance += amount
                else:
                    balance -= amount
            return transactions, balance
        except sqlite3.Error as e:
            logger.error(f"Помилка завантаження транзакцій з БД: {e}")
            return [], 0

    def save_debt(self, debt: Debt) -> int:
        """Зберігає новий борг і повертає його ID."""
        self.cursor.execute('''
        INSERT INTO debts (name, amount, due_date, is_loan, is_paid)
        VALUES (?, ?, ?, ?, ?)''',
                            (debt.name, debt.amount, debt.due_date, int(debt.is_loan), int(debt.is_paid)))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_debt(self, debt: Debt):
        """Оновлює існуючий борг."""
        self.cursor.execute('''
        UPDATE debts SET name = ?, amount = ?, due_date = ?, is_loan = ?, is_paid = ?
        WHERE id = ?''',
                            (debt.name, debt.amount, debt.due_date, int(debt.is_loan), int(debt.is_paid), debt.id))
        self.conn.commit()

    def load_debts(self) -> list[Debt]:
        """Завантажує всі борги з БД."""
        self.cursor.execute("SELECT id, name, amount, due_date, is_loan, is_paid FROM debts")
        rows = self.cursor.fetchall()
        return [Debt(r[0], r[1], r[2], r[3], bool(r[4]), bool(r[5])) for r in rows]

    def save_goal(self, goal: SavingsGoal) -> int:
        """Зберігає нову ціль і повертає її ID."""
        self.cursor.execute('''
        INSERT INTO savings_goals (name, target_amount, current_amount)
        VALUES (?, ?, ?)''', (goal.name, goal.target_amount, goal.current_amount))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_goal(self, goal: SavingsGoal):
        """Оновлює існуючу ціль."""
        self.cursor.execute('''
        UPDATE savings_goals SET name = ?, target_amount = ?, current_amount = ?
        WHERE id = ?''', (goal.name, goal.target_amount, goal.current_amount, goal.id))
        self.conn.commit()

    def load_goals(self) -> list[SavingsGoal]:
        """Завантажує всі цілі з БД."""
        self.cursor.execute("SELECT id, name, target_amount, current_amount FROM savings_goals")
        rows = self.cursor.fetchall()
        return [SavingsGoal(r[0], r[1], r[2], r[3]) for r in rows]

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("З'єднання з базою даних закрито.")