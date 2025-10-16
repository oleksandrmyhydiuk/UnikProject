import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import (User, SavingsAccount, CategorizedTransaction, Budget,
                    Report, SpendingReport, IncomeReport)
from exceptions import InsufficientFundsError
from database import DatabaseManager
from api_handler import APIHandler
from services import FinanceService

class ChartSelectionDialog(tk.Toplevel):
    """Окремий клас для діалогового вікна вибору типу діаграми."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Вибір діаграми")
        self.geometry("300x120")
        self.resizable(False, False)
        self.transient(parent)

        self.selection = None

        ttk.Label(self, text="Оберіть тип візуалізації:", font=("Arial", 12)).pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        pie_btn = ttk.Button(btn_frame, text="Кругова", command=lambda: self._select('кругова'))
        pie_btn.pack(side="left", padx=10)

        bar_btn = ttk.Button(btn_frame, text="Стовпчикова", command=lambda: self._select('стовпчикова'))
        bar_btn.pack(side="left", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.grab_set()
        self.wait_window()

    def _select(self, chart_type):
        self.selection = chart_type
        self.destroy()

    def _on_close(self):
        self.selection = None
        self.destroy()

class FinanceAppGUI:
    """
    Клас GUI, що відповідає ТІЛЬКИ за відображення та взаємодію з користувачем.
    """
    def __init__(self, root):
        self._root = root
        self._root.title("Фінансовий Асистент (Refactored)")
        self._root.geometry("1100x700")
        self._root.minsize(1000, 600)

        # Ініціалізація компонентів
        self._user = User("DefaultUser")
        self._db_manager = DatabaseManager()
        self._api_handler = APIHandler()

        # Створення сервісного шару
        self._service = FinanceService(self._user, self._db_manager)

        self._create_default_account("Основний")
        self._service.set_current_account("Основний")

        self._setup_ui()
        self.refresh_transactions_view()

    def _create_default_account(self, name):
        """Завантажує або створює рахунок за замовчуванням."""
        transactions, balance = self._db_manager.load_transactions_for_account(name)
        account = SavingsAccount(name, initial_balance=balance)
        account.transactions = transactions
        self._user.add_account(account)
        self.current_account_name = name

    def _setup_ui(self):
        """Створює та розміщує всі віджети інтерфейсу."""
        top_frame = ttk.Frame(self._root)
        top_frame.pack(fill="x", padx=10, pady=10)

        input_frame = ttk.LabelFrame(top_frame, text="Додати транзакцію")
        input_frame.pack(side="left", fill="x", expand=True)

        ttk.Label(input_frame, text="Сума:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._amount_entry = ttk.Entry(input_frame, width=15)
        self._amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Опис:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self._desc_entry = ttk.Entry(input_frame, width=30)
        self._desc_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Категорія:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self._category_combobox = ttk.Combobox(input_frame, values=["Продукти", "Транспорт", "Комунальні", "Розваги", "Здоров'я", "Одяг", "Дохід"])
        self._category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self._category_combobox.set("Продукти")

        add_income_btn = ttk.Button(input_frame, text="✔️ Додати дохід", command=self.add_income)
        add_income_btn.grid(row=0, column=4, padx=10, pady=5, sticky="ew")

        add_expense_btn = ttk.Button(input_frame, text="❌ Додати витрату", command=self.add_expense)
        add_expense_btn.grid(row=1, column=4, padx=10, pady=5, sticky="ew")

        converter_frame = ttk.LabelFrame(top_frame, text="💱 Конвертер валют")
        converter_frame.pack(side="left", padx=20, pady=0)

        ttk.Label(converter_frame, text="Сума:").grid(row=0, column=0, padx=5, pady=2)
        self._converter_amount = ttk.Entry(converter_frame, width=10)
        self._converter_amount.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(converter_frame, text="З:").grid(row=1, column=0, padx=5, pady=2)
        self._from_currency = ttk.Combobox(converter_frame, values=["UAH", "USD", "EUR"], width=7)
        self._from_currency.grid(row=1, column=1); self._from_currency.set("USD")

        ttk.Label(converter_frame, text="В:").grid(row=2, column=0, padx=5, pady=2)
        self._to_currency = ttk.Combobox(converter_frame, values=["UAH", "USD", "EUR"], width=7)
        self._to_currency.grid(row=2, column=1); self._to_currency.set("UAH")

        convert_btn = ttk.Button(converter_frame, text="Конвертувати", command=self._perform_conversion)
        convert_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

        self._converter_result = ttk.Label(converter_frame, text="Результат: 0.00", font=("Arial", 10, "bold"))
        self._converter_result.grid(row=3, column=0, columnspan=3, pady=5)

        actions_frame = ttk.LabelFrame(self._root, text="Панель інструментів")
        actions_frame.pack(fill="x", padx=10, pady=5)

        spending_report_btn = ttk.Button(actions_frame, text="📊 Звіт про витрати", command=lambda: self._generate_report(SpendingReport))
        spending_report_btn.pack(side="left", padx=5, pady=5)

        income_report_btn = ttk.Button(actions_frame, text="📈 Звіт про доходи", command=lambda: self._generate_report(IncomeReport))
        income_report_btn.pack(side="left", padx=5, pady=5)

        chart_btn = ttk.Button(actions_frame, text="🎨 Візуалізація", command=self._show_expense_chart)
        chart_btn.pack(side="left", padx=5, pady=5)

        budget_btn = ttk.Button(actions_frame, text="💰 Керування бюджетом", command=self.manage_budget)
        budget_btn.pack(side="left", padx=5, pady=5)

        transactions_frame = ttk.LabelFrame(self._root, text="Історія транзакцій")
        transactions_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._tree = ttk.Treeview(transactions_frame, columns=("Дата", "Сума", "Категорія", "Опис"), show="headings")
        self._tree.heading("Дата", text="Дата"); self._tree.column("Дата", width=100)
        self._tree.heading("Сума", text="Сума (грн)"); self._tree.column("Сума", width=120, anchor="e")
        self._tree.heading("Категорія", text="Категорія"); self._tree.column("Категорія", width=150)
        self._tree.heading("Опис", text="Опис")
        self._tree.pack(fill="both", expand=True)

        info_frame = ttk.Frame(self._root)
        info_frame.pack(fill="x", padx=10, pady=5)
        self._balance_label = ttk.Label(info_frame, text="Баланс: 0.00 грн", font=("Arial", 14, "bold"))
        self._balance_label.pack(side="left")

    def _perform_conversion(self):
        """Виконує конвертацію валют."""
        try:
            amount = float(self._converter_amount.get())
            from_cur = self._from_currency.get()
            to_cur = self._to_currency.get()
            result = self._api_handler.convert_currency(amount, from_cur, to_cur)
            if isinstance(result, float):
                self._converter_result.config(text=f"Результат: {result:.2f} {to_cur}")
            else:
                self._converter_result.config(text="Помилка API")
        except (ValueError, TypeError):
            self._converter_result.config(text="Помилка вводу")

    def _generate_report(self, report_type: type[Report]):
        """Обробляє подію генерації звіту з UI."""
        try:
            report_text, file_path = self._service.generate_report(report_type)
            messagebox.showinfo("Звіт", report_text)
            messagebox.showinfo("Успіх", f"Звіт також збережено у файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося згенерувати звіт: {e}")

    def _show_expense_chart(self):
        """Показує діаграму витрат після вибору її типу."""
        dialog = ChartSelectionDialog(self._root)
        chart_type = dialog.selection

        if not chart_type:
            return

        account = self._service.get_current_account()
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        # Створюємо екземпляр звіту тут, оскільки сервіс повертає лише текст
        spending_data = SpendingReport(account).generate(start_date, end_date)

        if not spending_data:
            messagebox.showinfo("Візуалізація", "Немає даних про витрати для створення діаграми.")
            return

        self._draw_chart(chart_type, spending_data)

    def _draw_chart(self, chart_type: str, data: dict):
        """Малює діаграму обраного типу."""
        chart_win = tk.Toplevel(self._root)
        chart_win.geometry("800x600")

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        labels = data.keys()
        sizes = data.values()

        if chart_type == 'кругова':
            chart_win.title("Кругова діаграма витрат")
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
        elif chart_type == 'стовпчикова':
            chart_win.title("Стовпчикова діаграма витрат")
            ax.bar(labels, sizes, color='skyblue')
            ax.set_ylabel('Сума (грн)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def add_transaction(self, is_income: bool):
        """Обробляє подію додавання транзакції, делегуючи логіку сервісу."""
        try:
            amount = float(self._amount_entry.get())
            description = self._desc_entry.get()
            category = self._category_combobox.get()

            if not description:
                messagebox.showwarning("Попередження", "Поле 'Опис' не може бути порожнім.")
                return

            self._service.add_transaction(amount, description, category, is_income)

            self.refresh_transactions_view()
            self._amount_entry.delete(0, tk.END)
            self._desc_entry.delete(0, tk.END)
        except InsufficientFundsError as e:
            messagebox.showerror("Помилка операції", e)
        except ValueError:
            messagebox.showerror("Помилка вводу", "Сума має бути коректним числом.")
        except Exception as e:
            messagebox.showerror("Невідома помилка", f"Сталася невідома помилка: {e}")

    def add_expense(self):
        self.add_transaction(is_income=False)

    def add_income(self):
        self.add_transaction(is_income=True)

    def refresh_transactions_view(self):
        """Оновлює таблицю транзакцій та баланс на екрані."""
        for i in self._tree.get_children():
            self._tree.delete(i)

        account = self._service.get_current_account()
        for t in reversed(account.transactions):
            if isinstance(t, CategorizedTransaction):
                self._tree.insert("", "end", values=(t.date, f"{t.amount:.2f}", t.category, t.description))
            else:
                self._tree.insert("", "end", values=(t.date, f"{t.amount:.2f}", "", t.description))

        self._balance_label.config(text=f"Баланс: {account.get_balance():.2f} грн")

    def manage_budget(self):
        """Відкриває діалог для керування бюджетом."""
        category = simpledialog.askstring("Керування бюджетом", "Введіть категорію (напр., Продукти):")
        if not category:
            return

        limit = simpledialog.askfloat("Керування бюджетом", f"Встановіть місячний ліміт для '{category}':")
        if limit is None:
            return

        budget = Budget(category, limit)
        account = self._service.get_current_account()
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        transactions = account.get_transactions_by_period(start_date, end_date)
        spent = budget.get_spent_amount(transactions)

        messagebox.showinfo("Стан бюджету", f"Бюджет для '{category}': {limit:.2f} грн\n"
                                           f"Витрачено цього місяця: {spent:.2f} грн")