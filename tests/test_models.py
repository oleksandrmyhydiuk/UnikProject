# tests/test_models.py
import unittest
from models import Account, Transaction
from exceptions import InsufficientFundsError


class TestAccount(unittest.TestCase):
    """Набір тестів для перевірки логіки класу Account."""

    def setUp(self):
        """Цей метод викликається перед кожним тестовим методом."""
        self.account = Account("Тестовий Рахунок", initial_balance=100.0)

    def test_add_income(self):
        """Перевіряє коректне додавання доходу."""
        income_transaction = Transaction(50.0, "2025-10-26", "Зарплата")
        self.account.add_transaction(income_transaction, is_income=True)
        self.assertEqual(self.account.get_balance(), 150.0)

    def test_add_valid_expense(self):
        """Перевіряє коректне списання витрати, коли коштів достатньо."""
        expense_transaction = Transaction(30.0, "2025-10-26", "Продукти")
        self.account.add_transaction(expense_transaction, is_income=False)
        self.assertEqual(self.account.get_balance(), 70.0)

    def test_add_expense_insufficient_funds(self):
        """Перевіряє, що генерується помилка InsufficientFundsError при недостачі коштів."""
        expense_transaction = Transaction(120.0, "2025-10-26", "Велика покупка")

        with self.assertRaises(InsufficientFundsError):
            self.account.add_transaction(expense_transaction, is_income=False)

    def test_balance_unchanged_on_failed_expense(self):
        """Перевіряє, що баланс не змінюється, якщо операція списання не вдалася."""
        initial_balance = self.account.get_balance()
        expense_transaction = Transaction(120.0, "2025-10-26", "Велика покупка")

        try:
            self.account.add_transaction(expense_transaction, is_income=False)
        except InsufficientFundsError:
            pass  #Очікуємо цю помилку

        self.assertEqual(self.account.get_balance(), initial_balance)


if __name__ == '__main__':
    unittest.main()