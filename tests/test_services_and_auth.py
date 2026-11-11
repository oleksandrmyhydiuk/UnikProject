import pytest
from models import User, SavingsAccount
from database import DatabaseManager
from services import FinanceService
from auth import AuthManager
from localization import LocalizationManager
from api_handler import APIHandler


def test_auth_manager_registration_and_verification(tmp_path):
    """Перевіряє реєстрацію та верифікацію пароля через Argon2."""
    auth_file = tmp_path / "test_auth.json"
    auth = AuthManager(auth_file=str(auth_file))

    assert not auth.is_registered()
    assert not auth.verify_password("Secret123!")

    with pytest.raises(ValueError):
        auth.register_password("")

    auth.register_password("Secret123!")
    assert auth.is_registered()
    assert auth.verify_password("Secret123!")
    assert not auth.verify_password("WrongPass")


def test_finance_service_debts_and_goals():
    """Перевіряє роботу сервісу з боргами, цілями та базою даних у пам'яті."""
    user = User("TestUser")
    user.add_account(SavingsAccount("Основний", initial_balance=5000.0))

    with DatabaseManager(db_name=":memory:") as db:
        service = FinanceService(user, db)
        service.set_current_account("Основний")

        # Додавання боргу та оновлення статусу
        service.add_debt("Олександр", 1000.0, "2026-12-31", is_loan=True)
        debts = service.load_debts_data()
        assert len(debts) == 1
        assert not debts[0].is_paid

        service.update_debt_status(debts[0].id, is_paid=True)
        assert debts[0].is_paid

        # Додавання цілі та внеску
        service.add_savings_goal("Відпустка", 10000.0)
        goals = service.load_goals_data()
        assert len(goals) == 1

        service.add_contribution_to_goal(goals[0].id, 1500.0)
        assert goals[0].current_amount == 1500.0
        assert service.get_current_account().get_balance() == 3500.0


def test_localization_parity():
    """Перевіряє, що файли локалізації uk.json та en.json мають однаковий набір ключів."""
    loc_uk = LocalizationManager(default_lang="uk")
    loc_en = LocalizationManager(default_lang="en")

    assert set(loc_uk._translations.keys()) == set(loc_en._translations.keys())


def test_api_handler_without_key():
    """Перевіряє безпечну поведінку APIHandler за відсутності API ключа."""
    handler = APIHandler(api_key="")
    assert handler.base_url is None
    assert handler.get_exchange_rate("USD", "UAH") is None
    assert handler.convert_currency(100, "USD", "UAH") == "Не вдалося отримати курс."
