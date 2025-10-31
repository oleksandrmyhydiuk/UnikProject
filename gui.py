# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import os
import logging

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import (User, SavingsAccount, CategorizedTransaction, Budget,
                    Report, SpendingReport, IncomeReport)
from exceptions import InsufficientFundsError
from database import DatabaseManager
from api_handler import APIHandler
from services import FinanceService
from localization import LocalizationManager  # <-- ІМПОРТ

# Отримуємо логер для цього модуля
logger = logging.getLogger(__name__)


class ChartSelectionDialog(tk.Toplevel):
    """Окремий клас для діалогового вікна вибору типу діаграми."""

    def __init__(self, parent, loc: LocalizationManager):  # <-- Приймає LocalizationManager
        super().__init__(parent)
        self.loc = loc
        self.title(self.loc.get("chart_selection"))
        self.geometry("300x120")
        self.resizable(False, False)
        self.transient(parent)
        self.selection = None

        ttk.Label(self, text=self.loc.get("choose_visualization"), font=("Arial", 12)).pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        pie_btn = ttk.Button(btn_frame, text=self.loc.get("pie_chart"), command=lambda: self._select('кругова'))
        pie_btn.pack(side="left", padx=10)

        bar_btn = ttk.Button(btn_frame, text=self.loc.get("bar_chart"), command=lambda: self._select('стовпчикова'))
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
        logger.info("Ініціалізація графічного інтерфейсу.")
        self._root = root

        # Ініціалізація менеджера локалізації
        self._loc = LocalizationManager(default_lang='uk')

        self._root.geometry("1100x700")
        self._root.minsize(1000, 600)

        # Ініціалізація компонентів
        self._user = User("DefaultUser")
        self._db_manager = DatabaseManager()
        self._api_handler = APIHandler()
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
        logger.info(f"Завантажено/створено рахунок за замовчуванням: {name}")

    def _setup_ui(self):
        """Створює та розміщує всі віджети інтерфейсу."""
        logger.debug("Налаштування UI віджетів...")

        # Реєструємо заголовок вікна
        self._loc.register_widget(self._root, 'window_title', 'title')

        # Створення меню
        self._menubar = tk.Menu(self._root)
        self._root.config(menu=self._menubar)

        # Меню "Налаштування"
        self._settings_menu = tk.Menu(self._menubar, tearoff=0)
        # Ключ 'settings' буде використано для оновлення тексту меню
        self._menubar.add_cascade(label=self._loc.get("settings"), menu=self._settings_menu)
        self._loc.register_widget(self._menubar, 'settings', 'text')  # Реєструємо для оновлення

        # Підменю "Мова"
        self._lang_menu = tk.Menu(self._settings_menu, tearoff=0)
        self._settings_menu.add_cascade(label=self._loc.get("language"), menu=self._lang_menu)
        self._lang_menu.add_command(label="Українська", command=lambda: self._loc.set_language('uk'))
        self._lang_menu.add_command(label="English", command=lambda: self._loc.set_language('en'))
        # Реєструємо підменю мови
        self._loc.register_widget(self._settings_menu, 'language', 'text')

        top_frame = ttk.Frame(self._root)
        top_frame.pack(fill="x", padx=10, pady=10)

        input_frame = ttk.LabelFrame(top_frame)
        input_frame.pack(side="left", fill="x", expand=True)
        self._loc.register_widget(input_frame, 'add_transaction', 'labelframe')

        label_amount = ttk.Label(input_frame)
        label_amount.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._loc.register_widget(label_amount, 'amount')

        self._amount_entry = ttk.Entry(input_frame, width=15)
        self._amount_entry.grid(row=0, column=1, padx=5, pady=5)

        label_desc = ttk.Label(input_frame)
        label_desc.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self._loc.register_widget(label_desc, 'description')

        self._desc_entry = ttk.Entry(input_frame, width=30)
        self._desc_entry.grid(row=0, column=3, padx=5, pady=5)

        label_cat = ttk.Label(input_frame)
        label_cat.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self._loc.register_widget(label_cat, 'category')

        self._category_combobox = ttk.Combobox(input_frame,
                                               values=["Продукти", "Транспорт", "Комунальні", "Розваги", "Здоров'я",
                                                       "Одяг", "Дохід"])
        self._category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self._category_combobox.set("Продукти")

        add_income_btn = ttk.Button(input_frame, command=self.add_income)
        add_income_btn.grid(row=0, column=4, padx=10, pady=5, sticky="ew")
        self._loc.register_widget(add_income_btn, 'add_income')

        add_expense_btn = ttk.Button(input_frame, command=self.add_expense)
        add_expense_btn.grid(row=1, column=4, padx=10, pady=5, sticky="ew")
        self._loc.register_widget(add_expense_btn, 'add_expense')

        converter_frame = ttk.LabelFrame(top_frame)
        converter_frame.pack(side="left", padx=20, pady=0)
        self._loc.register_widget(converter_frame, 'currency_converter', 'labelframe')

        label_conv_amount = ttk.Label(converter_frame)
        label_conv_amount.grid(row=0, column=0, padx=5, pady=2)
        self._loc.register_widget(label_conv_amount, 'amount')

        self._converter_amount = ttk.Entry(converter_frame, width=10)
        self._converter_amount.grid(row=0, column=1, padx=5, pady=2)

        label_from = ttk.Label(converter_frame)
        label_from.grid(row=1, column=0, padx=5, pady=2)
        self._loc.register_widget(label_from, 'from')

        self._from_currency = ttk.Combobox(converter_frame, values=["UAH", "USD", "EUR"], width=7)
        self._from_currency.grid(row=1, column=1);
        self._from_currency.set("USD")

        label_to = ttk.Label(converter_frame)
        label_to.grid(row=2, column=0, padx=5, pady=2)
        self._loc.register_widget(label_to, 'to')

        self._to_currency = ttk.Combobox(converter_frame, values=["UAH", "USD", "EUR"], width=7)
        self._to_currency.grid(row=2, column=1);
        self._to_currency.set("UAH")

        convert_btn = ttk.Button(converter_frame, command=self._perform_conversion)
        convert_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        self._loc.register_widget(convert_btn, 'convert')

        self._converter_result = ttk.Label(converter_frame, font=("Arial", 10, "bold"))
        self._converter_result.grid(row=3, column=0, columnspan=3, pady=5)
        self._loc.register_widget(self._converter_result, 'result')

        actions_frame = ttk.LabelFrame(self._root)
        actions_frame.pack(fill="x", padx=10, pady=5)
        self._loc.register_widget(actions_frame, 'toolbox', 'labelframe')

        spending_report_btn = ttk.Button(actions_frame, command=lambda: self._generate_report(SpendingReport))
        spending_report_btn.pack(side="left", padx=5, pady=5)
        self._loc.register_widget(spending_report_btn, 'spending_report')

        income_report_btn = ttk.Button(actions_frame, command=lambda: self._generate_report(IncomeReport))
        income_report_btn.pack(side="left", padx=5, pady=5)
        self._loc.register_widget(income_report_btn, 'income_report')

        chart_btn = ttk.Button(actions_frame, command=self._show_expense_chart)
        chart_btn.pack(side="left", padx=5, pady=5)
        self._loc.register_widget(chart_btn, 'visualization')

        budget_btn = ttk.Button(actions_frame, command=self.manage_budget)
        budget_btn.pack(side="left", padx=5, pady=5)
        self._loc.register_widget(budget_btn, 'manage_budget')

        transactions_frame = ttk.LabelFrame(self._root)
        transactions_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._loc.register_widget(transactions_frame, 'transaction_history', 'labelframe')

        self._tree = ttk.Treeview(transactions_frame, columns=("Дата", "Сума", "Категорія", "Опис"), show="headings")
        self._tree.pack(fill="both", expand=True)
        # Реєструємо заголовки таблиці
        self._loc.register_widget(self._tree, 'date', 'heading', column='Дата')
        self._loc.register_widget(self._tree, 'sum_uah', 'heading', column='Сума')
        self._loc.register_widget(self._tree, 'category', 'heading', column='Категорія')
        self._loc.register_widget(self._tree, 'description', 'heading', column='Опис')

        info_frame = ttk.Frame(self._root)
        info_frame.pack(fill="x", padx=10, pady=5)

        self._balance_label = ttk.Label(info_frame, font=("Arial", 14, "bold"))
        self._balance_label.pack(side="left")
        # Баланс буде оновлюватися через refresh_transactions_view

        logger.debug("Налаштування UI завершено.")

    def _perform_conversion(self):
        """Виконує конвертацію валют."""
        try:
            amount = float(self._converter_amount.get())
            from_cur = self._from_currency.get()
            to_cur = self._to_currency.get()
            logger.info(f"Запит на конвертацію: {amount} {from_cur} -> {to_cur}")
            result = self._api_handler.convert_currency(amount, from_cur, to_cur)
            if isinstance(result, float):
                self._converter_result.config(text=f"{self._loc.get('result')[:-4]} {result:.2f} {to_cur}")
                logger.info(f"Результат конвертації: {result:.2f} {to_cur}")
            else:
                self._converter_result.config(text=self._loc.get('error_api'))
                logger.warning(f"Не вдалося отримати результат конвертації. API повернуло: {result}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Помилка вводу суми для конвертації: {e}")
            self._converter_result.config(text=self._loc.get('error_input'))

    def _generate_report(self, report_type: type[Report]):
        """Обробляє подію генерації звіту з UI."""
        logger.info(f"Користувач запитав звіт: {report_type.__name__}")
        try:
            report_text, file_path = self._service.generate_report(report_type)
            messagebox.showinfo(self._loc.get(report_type.__name__.lower()), report_text)
            messagebox.showinfo(self._loc.get("report_generated_success"),
                                self._loc.get("report_generated_message", path=file_path))
        except Exception as e:
            logger.error(f"Не вдалося згенерувати звіт: {e}", exc_info=True)
            messagebox.showerror(self._loc.get("error_unknown"),
                                 self._loc.get("report_generation_error", error=e))

    def _show_expense_chart(self):
        """Показує діаграму витрат після вибору її типу."""
        logger.info("Користувач запитав візуалізацію.")
        dialog = ChartSelectionDialog(self._root, self._loc)  # Передаємо локалізатор
        chart_type = dialog.selection

        if not chart_type:
            logger.info("Користувач скасував вибір діаграми.")
            return

        logger.info(f"Користувач обрав тип діаграми: {chart_type}")
        account = self._service.get_current_account()
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        spending_data = SpendingReport(account).generate(start_date, end_date)

        if not spending_data:
            logger.info("Немає даних для візуалізації.")
            messagebox.showinfo(self._loc.get("visualization"),
                                self._loc.get("visualization_no_data"))
            return

        self._draw_chart(chart_type, spending_data)

    def _draw_chart(self, chart_type: str, data: dict):
        """Малює діаграму обраного типу."""
        logger.debug(f"Малювання діаграми типу: {chart_type}")
        try:
            chart_win = tk.Toplevel(self._root)
            chart_win.geometry("800x600")

            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            labels = data.keys()
            sizes = data.values()

            if chart_type == 'кругова':
                chart_win.title(self._loc.get("pie_chart"))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                ax.axis('equal')
            elif chart_type == 'стовпчикова':
                chart_win.title(self._loc.get("bar_chart"))
                ax.bar(labels, sizes, color='skyblue')
                ax.set_ylabel(self._loc.get("sum_uah"))
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_win)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            logger.info("Діаграму успішно намальовано.")
        except Exception as e:
            logger.error(f"Помилка при малюванні діаграми: {e}", exc_info=True)
            messagebox.showerror(self._loc.get("visualization"), f"Не вдалося намалювати діаграму: {e}")

    def add_transaction(self, is_income: bool):
        """Обробляє подію додавання транзакції, делегуючи логіку сервісу."""
        try:
            amount = float(self._amount_entry.get())
            description = self._desc_entry.get()
            category = self._category_combobox.get()

            if not description:
                logger.warning("Користувач намагався додати транзакцію з порожнім описом.")
                messagebox.showwarning(self._loc.get("warning"),
                                       self._loc.get("warning_empty_description"))
                return

            self._service.add_transaction(amount, description, category, is_income)

            self.refresh_transactions_view()
            self._amount_entry.delete(0, tk.END)
            self._desc_entry.delete(0, tk.END)

        except InsufficientFundsError as e:
            logger.warning(f"Помилка операції: недостатньо коштів. {e}")
            messagebox.showerror(self._loc.get("error_insufficient_funds"), e)

        except ValueError as e:
            logger.warning(f"Помилка вводу даних користувачем: {e}")
            messagebox.showerror(self._loc.get("error_value"),
                                 self._loc.get("error_value_message"))

        except Exception as e:
            logger.critical("Сталася непередбачувана помилка!", exc_info=True)
            messagebox.showerror(self._loc.get("error_unknown"),
                                 self._loc.get("error_unknown_message", error=e))

    def add_expense(self):
        self.add_transaction(is_income=False)

    def add_income(self):
        self.add_transaction(is_income=True)

    def refresh_transactions_view(self):
        """Оновлює таблицю транзакцій та баланс на екрані."""
        logger.debug("Оновлення списку транзакцій та балансу...")
        for i in self._tree.get_children():
            self._tree.delete(i)

        try:
            account = self._service.get_current_account()
            for t in reversed(account.transactions):
                if isinstance(t, CategorizedTransaction):
                    self._tree.insert("", "end", values=(t.date, f"{t.amount:.2f}", t.category, t.description))
                else:
                    self._tree.insert("", "end", values=(t.date, f"{t.amount:.2f}", "", t.description))

            self._balance_label.config(text=self._loc.get("balance", balance=account.get_balance()))
            logger.debug("Список транзакцій та баланс оновлено.")
        except Exception as e:
            logger.error(f"Не вдалося оновити список транзакцій: {e}", exc_info=True)
            self._balance_label.config(text=self._loc.get("balance_error"))

    def manage_budget(self):
        """Відкриває діалог для керування бюджетом."""
        logger.info("Користувач відкрив менеджер бюджету.")
        category = simpledialog.askstring(self._loc.get("manage_budget"),
                                          self._loc.get("budget_category_prompt"))
        if not category:
            logger.info("Користувач скасував введення категорії бюджету.")
            return

        limit = simpledialog.askfloat(self._loc.get("manage_budget"),
                                      self._loc.get("budget_limit_prompt", category=category))
        if limit is None:
            logger.info("Користувач скасував введення ліміту бюджету.")
            return

        logger.info(f"Користувач встановив бюджет: Категорія={category}, Ліміт={limit}")
        budget = Budget(category, limit)
        account = self._service.get_current_account()
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        transactions = account.get_transactions_by_period(start_date, end_date)
        spent = budget.get_spent_amount(transactions)

        messagebox.showinfo(self._loc.get("budget_status_title"),
                            self._loc.get("budget_status_message", category=category, limit=limit, spent=spent))