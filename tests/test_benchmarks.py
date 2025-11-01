import pytest
from models import User, SavingsAccount, CategorizedTransaction
from database import DatabaseManager
from services import FinanceService
from exceptions import InsufficientFundsError

@pytest.fixture
def finance_service():
    """
    Створює екземпляр FinanceService з БД в пам'яті (:memory:)
    та 1000 тестовими транзакціями для реалістичного бенчмаркінгу.
    """
    user = User("benchmark_user")
    db = DatabaseManager(db_name=":memory:")

    # Встановлюємо дуже великий баланс, щоб він не закінчився під час бенчмаркінгу
    acc = SavingsAccount("test_acc", initial_balance=500_000_000.0)

    # Генеруємо 1000 транзакцій
    for i in range(1000):
        if i % 4 == 0:
            cat = "Продукти"
        elif i % 4 == 1:
            cat = "Транспорт"
        elif i % 4 == 2:
            cat = "Комунальні"
        else:
            cat = "Розваги"

        acc.add_transaction(
            transaction=CategorizedTransaction(
                amount=float(i % 100) + 1.0,
                date="2025-10-27",
                description=f"Тестова транзакція {i}",
                category=cat
            ),
            is_income=False
        )

    user.add_account(acc)

    service = FinanceService(user, db)
    service.set_current_account("test_acc")
    return service

def test_get_spending_analysis_benchmark(benchmark, finance_service):
    """
    Мікробенчмарк для функції get_spending_analysis.
    """
    result = benchmark(finance_service.get_spending_analysis)

    assert "Продукти" in result
    assert "Транспорт" in result
    assert "Комунальні" in result
    assert len(result) == 4


def test_add_transaction_benchmark(benchmark, finance_service):
    """
    Мікробенчмарк для функції add_transaction.
    """
    # Тепер цей тест не впаде, оскільки баланс практично нескінченний
    result = benchmark(
        lambda: finance_service.add_transaction(
            amount=55.5,
            description="Бенчмарк-тест",
            category="Тестування",
            is_income=False
        )
    )

    # Перевіряємо, що баланс дійсно змінився
    assert finance_service.get_current_account().get_balance() < 500_000_000.0