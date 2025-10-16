from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from exceptions import InsufficientFundsError

class Transaction:
    def __init__(self, amount: float, date: str, description: str):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сума має бути додатнім числом.")
        self.amount = amount
        self.date = date
        self.description = description

    def display(self) -> str:
        return f"Дата: {self.date}, Сума: {self.amount:.2f} грн, Опис: {self.description}"

class CategorizedTransaction(Transaction):
    def __init__(self, amount: float, date: str, description: str, category: str):
        super().__init__(amount, date, description)
        self.category = category

    def display(self) -> str:
        return f"Дата: {self.date}, Сума: {self.amount:.2f} грн, Категорія: {self.category}, Опис: {self.description}"


class RecurringTransaction(CategorizedTransaction):
    def __init__(self, amount: float, date: str, description: str, category: str, frequency_days: int):
        super().__init__(amount, date, description, category)
        self._frequency_days = frequency_days
        self._last_processed_date = datetime.strptime(date, '%Y-%m-%d').date()

    def is_due(self) -> bool:
        return (datetime.now().date() - self._last_processed_date).days >= self._frequency_days

    def get_next_due_date(self) -> datetime.date:
        return self._last_processed_date + timedelta(days=self._frequency_days)


class Account:
    def __init__(self, name: str, initial_balance: float = 0.0):
        self.name = name
        self._balance = float(initial_balance)
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction, is_income: bool):
        if not is_income:
            if transaction.amount > self._balance:
                raise InsufficientFundsError(balance=self._balance, amount=transaction.amount)

            self._balance -= transaction.amount
        else:
            self._balance += transaction.amount

        self.transactions.append(transaction)

    def get_balance(self) -> float:
        return self._balance

    def get_transactions_by_period(self, start_date: str, end_date: str) -> list[Transaction]:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        return [t for t in self.transactions if start <= datetime.strptime(t.date, '%Y-%m-%d').date() <= end]


class SavingsAccount(Account):
    def __init__(self, name: str, initial_balance: float = 0.0, interest_rate: float = 0.05):
        super().__init__(name, initial_balance)
        self._interest_rate = interest_rate

    def apply_interest(self):
        interest_amount = self._balance * self._interest_rate
        interest_transaction = CategorizedTransaction(interest_amount, datetime.now().strftime('%Y-%m-%d'),
                                                      "Нарахування відсотків", "Дохід")
        self.add_transaction(interest_transaction, is_income=True)


class Budget:
    def __init__(self, category: str, limit: float):
        self.category = category
        self.limit = float(limit)

    def get_spent_amount(self, transactions: list[Transaction]) -> float:
        return sum(
            t.amount for t in transactions if isinstance(t, CategorizedTransaction) and t.category == self.category)

    def display(self) -> str:
        return f"Бюджет для '{self.category}': {self.limit:.2f} грн"


class Report(ABC):
    def __init__(self, account: Account):
        self._account = account

    @abstractmethod
    def generate(self, start_date: str, end_date: str) -> dict:
        pass


class SpendingReport(Report):
    def generate(self, start_date: str, end_date: str) -> dict[str, float]:
        transactions = self._account.get_transactions_by_period(start_date, end_date)
        spending = {}
        for t in transactions:
            if isinstance(t, CategorizedTransaction) and t.category != "Дохід":
                spending.setdefault(t.category, 0)
                spending[t.category] += t.amount
        return spending


class IncomeReport(Report):
    def generate(self, start_date: str, end_date: str) -> dict[str, float]:
        transactions = self._account.get_transactions_by_period(start_date, end_date)
        income = {}
        for t in transactions:
            if isinstance(t, CategorizedTransaction) and t.category == "Дохід":
                income.setdefault(t.description, 0)
                income[t.description] += t.amount
        return income


class User:
    def __init__(self, username: str):
        self.username = username
        self.accounts: dict[str, Account] = {}

    def add_account(self, account: Account):
        self.accounts[account.name] = account

    def get_total_balance(self) -> float:
        return sum(acc.get_balance() for acc in self.accounts.values())