import sqlite3
from models import CategorizedTransaction

class DatabaseManager:
    def __init__(self, db_name="finance_assistant.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT,
            amount REAL,
            date TEXT,
            description TEXT,
            category TEXT,
            is_income INTEGER
        )
        ''')
        self.conn.commit()

    def save_transaction(self, account_name, transaction: CategorizedTransaction, is_income: bool):
        self.cursor.execute('''
        INSERT INTO transactions (account_name, amount, date, description, category, is_income)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (account_name, transaction.amount, transaction.date, transaction.description, transaction.category, 1 if is_income else 0))
        self.conn.commit()

    def load_transactions_for_account(self, account_name):
        self.cursor.execute("SELECT amount, date, description, category, is_income FROM transactions WHERE account_name = ?", (account_name,))
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

    def close(self):
        self.conn.close()