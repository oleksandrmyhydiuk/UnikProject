import pytest
from models import (
    Account, Transaction, CategorizedTransaction, RecurringTransaction,
    SavingsAccount, SavingsGoal, SpendingReport, IncomeReport, Budget, Debt, User
)
from exceptions import InsufficientFundsError

@pytest.fixture
def basic_account() -> Account:
    """
    pytest-фікстура, яка створює чистий Account
    з балансом 100.0 для кожного тесту, який її запросить.
    """
    return Account("Тестовий Рахунок", initial_balance=100.0)


@pytest.fixture
def account_with_transactions() -> Account:
    """Фікстура, що створює рахунок з набором транзакцій для тестування звітів."""
    account = SavingsAccount("Рахунок для звітів", 1000.0)

    # Витрати
    account.add_transaction(
        CategorizedTransaction(100.0, "2025-01-01", "Хліб", "Продукти"), False
    )
    account.add_transaction(
        CategorizedTransaction(50.0, "2025-01-02", "Автобус", "Транспорт"), False
    )
    account.add_transaction(
        CategorizedTransaction(250.0, "2025-01-03", "М'ясо", "Продукти"), False
    )

    # Дохід (не має потрапити у звіт про витрати)
    account.add_transaction(
        CategorizedTransaction(5000.0, "2025-01-05", "Зарплата", "Дохід"), True
    )
    return account


@pytest.fixture
def savings_goal() -> SavingsGoal:
    """Фікстура, що створює тестову ціль заощаджень."""
    return SavingsGoal(id=1, name="Новий ноутбук", target_amount=40000.0, current_amount=0.0)

def test_add_income(basic_account: Account):
    """Перевіряє коректне додавання доходу."""
    income_transaction = Transaction(50.0, "2025-10-26", "Зарплата")
    basic_account.add_transaction(income_transaction, is_income=True)

    # Використовуємо простий 'assert'
    assert basic_account.get_balance() == 150.0


def test_add_valid_expense(basic_account: Account):
    """Перевіряє коректне списання витрати, коли коштів достатньо."""
    expense_transaction = Transaction(30.0, "2025-10-26", "Продукти")
    basic_account.add_transaction(expense_transaction, is_income=False)

    assert basic_account.get_balance() == 70.0


def test_add_expense_insufficient_funds(basic_account: Account):
    """Перевіряє, що генерується помилка InsufficientFundsError при недостачі коштів."""
    expense_transaction = Transaction(120.0, "2025-10-26", "Велика покупка")

    # Використовуємо 'pytest.raises' для перевірки виключень
    with pytest.raises(InsufficientFundsError):
        basic_account.add_transaction(expense_transaction, is_income=False)


def test_balance_unchanged_on_failed_expense(basic_account: Account):
    """Перевіряє, що баланс не змінюється, якщо операція списання не вдалася."""
    initial_balance = basic_account.get_balance()
    expense_transaction = Transaction(120.0, "2025-10-26", "Велика покупка")

    with pytest.raises(InsufficientFundsError):
        basic_account.add_transaction(expense_transaction, is_income=False)

    assert basic_account.get_balance() == initial_balance
    assert initial_balance == 100.0  # Перевіряємо, що це дійсно початковий баланс


def test_transaction_raises_error_on_invalid_amount():
    """
    Перевіряє, що клас Transaction не дозволяє створювати
    операції з нульовою або негативною сумою.
    """
    with pytest.raises(ValueError, match="Сума має бути додатнім числом"):
        Transaction(0.0, "2025-10-27", "Нульова транзакція")

    with pytest.raises(ValueError, match="Сума має бути додатнім числом"):
        Transaction(-50.0, "2025-10-27", "Негативна транзакція")


def test_add_expense_exact_balance(basic_account: Account):
    """
    Перевіряє, що списання точної суми балансу проходить коректно (баланс = 0).
    """
    expense_transaction = Transaction(100.0, "2025-10-26", "Все на нуль")
    basic_account.add_transaction(expense_transaction, is_income=False)

    assert basic_account.get_balance() == 0.0


def test_spending_report_generation(account_with_transactions: Account):
    """
    Перевіряє коректність генерації звіту про витрати:
    суми мають бути згруповані, доходи - проігноровані.
    """
    report = SpendingReport(account_with_transactions)
    # Генеруємо звіт за дуже великий період, щоб захопити всі транзакції
    data = report.generate(start_date="2000-01-01", end_date="2099-12-31")

    assert "Продукти" in data
    assert "Транспорт" in data
    assert "Дохід" not in data  # Дуже важливо: доходи не мають бути у звіті про витрати

    assert data["Продукти"] == 350.0  # 100.0 + 250.0
    assert data["Транспорт"] == 50.0
    assert len(data) == 2  # У звіті має бути лише 2 категорії


def test_savings_goal_contribution(savings_goal: SavingsGoal):
    """
    Перевіряє логіку додавання внеску та розрахунку прогресу в SavingsGoal.
    """
    assert savings_goal.current_amount == 0.0
    assert savings_goal.get_progress() == 0.0

    savings_goal.add_contribution(10000.0)

    assert savings_goal.current_amount == 10000.0
    assert savings_goal.get_progress() == 25.0  # 10 000 / 40 000 * 100


def test_savings_goal_over_contribution(savings_goal: SavingsGoal):
    """
    Перевіряє, що не можна накопичити більше, ніж цільова сума.
    """
    savings_goal.add_contribution(30000.0)
    savings_goal.add_contribution(20000.0)  # Разом 50к, але ціль 40к

    assert savings_goal.current_amount == 40000.0
    assert savings_goal.get_progress() == 100.0


def test_income_report_generation(account_with_transactions: Account):
    """Перевіряє коректність генерації звіту про доходи."""
    report = IncomeReport(account_with_transactions)
    data = report.generate(start_date="2000-01-01", end_date="2099-12-31")

    assert "Зарплата" in data
    assert data["Зарплата"] == 5000.0
    assert len(data) == 1


def test_savings_account_apply_interest():
    """Перевіряє нарахування відсотків на ощадному рахунку та роботу при нульовому балансі."""
    empty_acc = SavingsAccount("Порожній", initial_balance=0.0, interest_rate=0.05)
    empty_acc.apply_interest()
    assert empty_acc.get_balance() == 0.0

    acc = SavingsAccount("Депозит", initial_balance=1000.0, interest_rate=0.10)
    acc.apply_interest()
    assert acc.get_balance() == 1100.0


def test_budget_tracking(account_with_transactions: Account):
    """Перевіряє розрахунок витрат за категорією в межах бюджету."""
    budget = Budget("Продукти", 500.0)
    spent = budget.get_spent_amount(account_with_transactions.transactions)
    assert spent == 350.0

    with pytest.raises(ValueError):
        Budget("Продукти", -10.0)


def test_insufficient_funds_error_message():
    """Перевіряє текстове представлення помилки InsufficientFundsError."""
    err = InsufficientFundsError(balance=50.0, amount=100.0)
    assert "50.00 грн" in str(err)
    assert "100.00 грн" in str(err)
