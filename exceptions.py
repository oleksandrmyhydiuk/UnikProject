class InsufficientFundsError(Exception):
    """
    Власна помилка, що генерується при спробі виконати операцію,
    на яку недостатньо коштів на балансі.
    """
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        # Формуємо детальне повідомлення про помилку
        self.message = (
            f"Недостатньо коштів на рахунку!\n\n"
            f"Поточний баланс: {balance:.2f} грн\n"
            f"Спроба списання: {amount:.2f} грн"
        )