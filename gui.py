import logging
from datetime import datetime
import os

# Імпорти PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QInputDialog, QDialog, QAction, QMenuBar, QMenu,
    QTabWidget, QDateEdit, QProgressBar, QFormLayout, QHeaderView
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QIcon, QPixmap, QColor

# Інтеграція Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Іконки
import qtawesome as qta

# Компоненти нашого проєкту
from models import (User, SavingsAccount, CategorizedTransaction, Budget,
                    Report, SpendingReport, IncomeReport, Debt, SavingsGoal)
from exceptions import InsufficientFundsError
from database import DatabaseManager
from api_handler import APIHandler
from services import FinanceService
from localization import LocalizationManager
from themes import ThemeManager

logger = logging.getLogger(__name__)

# Кольорова палітра для діаграм
CHART_COLORS = [
    '#61AFEF', '#98C379', '#E5C07B', '#C678DD', '#56B6C2', '#E06C75', '#ABB2BF', '#F92672'
]


class ChartDialog(QDialog):
    """Окремий клас-діалог для відображення діаграми Matplotlib."""

    def __init__(self, chart_type, data, loc, current_theme, parent=None):
        super().__init__(parent)
        self.loc = loc
        self._current_theme = current_theme
        self._setup_ui(chart_type, data)

    def _setup_ui(self, chart_type, data):
        self.setWindowTitle(self.loc.get(f"{chart_type}_chart"))
        self.setGeometry(300, 300, 800, 600)

        layout = QVBoxLayout(self)

        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

        is_dark = self._current_theme == 'dark'

        bg_color = '#282C36' if is_dark else '#F8F8F8'
        fg_color = '#ABB2BF' if is_dark else '#333333'
        grid_bg_color = '#353A45' if is_dark else '#FFFFFF'

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(grid_bg_color)

        ax.tick_params(axis='x', colors=fg_color)
        ax.tick_params(axis='y', colors=fg_color)
        ax.yaxis.label.set_color(fg_color)
        ax.xaxis.label.set_color(fg_color)
        ax.title.set_color(fg_color)

        labels = data.keys()
        sizes = data.values()

        if chart_type == 'pie':
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                colors=CHART_COLORS, textprops={'color': fg_color}
            )
            for autotext in autotexts:
                autotext.set_color('#FFFFFF')
            ax.axis('equal')
        elif chart_type == 'bar':
            ax.bar(labels, sizes, color=CHART_COLORS[0])
            ax.set_ylabel(self.loc.get("sum_uah"))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        self.setLayout(layout)


class ChartSelectionDialog(QDialog):
    """Діалог вибору типу діаграми з візуальним прикладом."""

    def __init__(self, loc, parent=None):
        super().__init__(parent)
        self.loc = loc
        self.selection = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self.loc.get("chart_selection"))
        self.setModal(True)
        self.setFixedSize(400, 300)

        main_layout = QVBoxLayout()

        self.label = QLabel(self.loc.get("choose_visualization"))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(self.label)

        grid_layout = QGridLayout()

        pie_preview_label = QLabel()
        pie_icon = qta.icon("fa5s.chart-pie", color='#C678DD', options=[{'transform': 'scale(5.0)'}])
        pie_preview_label.setPixmap(pie_icon.pixmap(QSize(100, 100)))
        pie_preview_label.setAlignment(Qt.AlignCenter)

        self.pie_btn = QPushButton(self.loc.get("pie_chart"))
        self.pie_btn.clicked.connect(lambda: self._select('pie'))

        grid_layout.addWidget(pie_preview_label, 0, 0)
        grid_layout.addWidget(self.pie_btn, 1, 0)

        bar_preview_label = QLabel()
        bar_icon = qta.icon("fa5s.chart-bar", color='#61AFEF', options=[{'transform': 'scale(5.0)'}])
        bar_preview_label.setPixmap(bar_icon.pixmap(QSize(100, 100)))
        bar_preview_label.setAlignment(Qt.AlignCenter)

        self.bar_btn = QPushButton(self.loc.get("bar_chart"))
        self.bar_btn.clicked.connect(lambda: self._select('bar'))

        grid_layout.addWidget(bar_preview_label, 0, 1)
        grid_layout.addWidget(self.bar_btn, 1, 1)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def _select(self, chart_type):
        self.selection = chart_type
        self.accept()


class FinanceAppGUI(QMainWindow):
    """Головне вікно програми на PyQt5"""

    def __init__(self, app: QApplication):
        super().__init__()
        logger.info("Ініціалізація графічного інтерфейсу PyQt5.")

        self._app = app
        self._loc = LocalizationManager(default_lang='uk')
        self._theme_manager = ThemeManager(self._app)

        self._user = User("DefaultUser")
        self._db_manager = DatabaseManager()
        self._api_handler = APIHandler()
        self._service = FinanceService(self._user, self._db_manager)

        self._create_default_account("Основний")
        self._service.set_current_account("Основний")

        self.icon_size = QSize(20, 20)
        self.button_icon_size = QSize(24, 24)
        self._current_theme = 'dark'

        self._setup_ui()
        self._apply_theme(self._current_theme)
        self._update_ui_texts()

    def _setup_ui(self):
        """Налаштовує всі віджети."""
        self.setGeometry(100, 100, 1300, 800)
        self.setMinimumSize(1100, 700)

        self._setup_menu()

        # --- СТВОРЕННЯ QTabWidget ---
        self.tabs = QTabWidget()
        self.tabs.setIconSize(self.icon_size)
        self.setCentralWidget(self.tabs)

        # Створюємо кожну вкладку
        self.dashboard_tab = QWidget()
        self.debts_tab = QWidget()
        self.goals_tab = QWidget()
        self.analysis_tab = QWidget()

        # Додаємо вкладки
        self.tabs.addTab(self.dashboard_tab, "")
        self.tabs.addTab(self.debts_tab, "")
        self.tabs.addTab(self.goals_tab, "")
        self.tabs.addTab(self.analysis_tab, "")

        # Заповнюємо кожну вкладку
        self._create_dashboard_tab_ui()
        self._create_debts_tab_ui()
        self._create_goals_tab_ui()
        self._create_analysis_tab_ui()

    def _create_dashboard_tab_ui(self):
        """Заповнює вкладку 'Дашборд'."""
        main_layout = QVBoxLayout(self.dashboard_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        self.input_group_box = self._create_input_group()
        self.converter_group_box = self._create_converter_group()
        top_layout.addWidget(self.input_group_box)
        top_layout.addWidget(self.converter_group_box)
        top_layout.setStretch(0, 3)
        top_layout.setStretch(1, 2)
        main_layout.addLayout(top_layout)

        self.toolbox_group_box = self._create_toolbox_group()
        main_layout.addWidget(self.toolbox_group_box)

        self.history_group_box = self._create_history_group()
        main_layout.addWidget(self.history_group_box)
        main_layout.setStretch(2, 1)

        self.balance_label = QLabel()
        self.balance_label.setObjectName("balanceLabel")
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #98C379;")
        main_layout.addWidget(self.balance_label, 0, Qt.AlignLeft)

    def _create_debts_tab_ui(self):
        """Заповнює вкладку 'Борги'."""
        main_layout = QHBoxLayout(self.debts_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- Ліва колонка: Додавання боргу ---
        self.debt_add_group = QGroupBox()
        add_layout = QFormLayout(self.debt_add_group)
        add_layout.setSpacing(10)

        self.debt_name_label = QLabel()
        self.debt_name_input = QLineEdit()

        self.debt_amount_label = QLabel()
        self.debt_amount_input = QLineEdit()
        self.debt_amount_input.setPlaceholderText("0.00")

        self.debt_due_date_label = QLabel()
        self.debt_due_date_input = QDateEdit()
        self.debt_due_date_input.setDate(QDate.currentDate())
        self.debt_due_date_input.setCalendarPopup(True)

        self.debt_type_label = QLabel()
        self.debt_type_combo = QComboBox()

        self.debt_add_btn = QPushButton()
        self.debt_add_btn.clicked.connect(self._add_new_debt)

        add_layout.addRow(self.debt_name_label, self.debt_name_input)
        add_layout.addRow(self.debt_amount_label, self.debt_amount_input)
        add_layout.addRow(self.debt_due_date_label, self.debt_due_date_input)
        add_layout.addRow(self.debt_type_label, self.debt_type_combo)
        add_layout.addRow(self.debt_add_btn)

        # --- Права колонка: Список боргів ---
        self.debt_list_group = QGroupBox()
        list_layout = QVBoxLayout(self.debt_list_group)

        self.debt_tree = QTreeWidget()
        self.debt_tree.setColumnCount(5)
        self.debt_tree.header().setStretchLastSection(False)

        self.debt_mark_paid_btn = QPushButton()
        self.debt_mark_paid_btn.clicked.connect(self._mark_debt_as_paid)

        list_layout.addWidget(self.debt_tree)
        list_layout.addWidget(self.debt_mark_paid_btn)

        main_layout.addWidget(self.debt_add_group, 1)
        main_layout.addWidget(self.debt_list_group, 2)

    def _create_goals_tab_ui(self):
        """Заповнює вкладку 'Цілі'."""
        main_layout = QHBoxLayout(self.goals_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- Ліва колонка: Додавання цілі ---
        self.goal_add_group = QGroupBox()
        add_layout = QFormLayout(self.goal_add_group)
        add_layout.setSpacing(10)

        self.goal_name_label = QLabel()
        self.goal_name_input = QLineEdit()
        self.goal_name_input.setPlaceholderText("Ноутбук, Відпустка...")

        self.goal_target_label = QLabel()
        self.goal_target_input = QLineEdit()
        self.goal_target_input.setPlaceholderText("50000.00")

        self.goal_add_btn = QPushButton()
        self.goal_add_btn.clicked.connect(self._add_new_goal)

        add_layout.addRow(self.goal_name_label, self.goal_name_input)
        add_layout.addRow(self.goal_target_label, self.goal_target_input)
        add_layout.addRow(self.goal_add_btn)

        # --- Права колонка: Список цілей ---
        self.goal_list_group = QGroupBox()
        list_layout = QVBoxLayout(self.goal_list_group)

        self.goal_tree = QTreeWidget()
        self.goal_tree.setColumnCount(4)
        self.goal_tree.header().setStretchLastSection(False)

        self.goal_add_contribution_btn = QPushButton()
        self.goal_add_contribution_btn.clicked.connect(self._add_contribution_to_goal)

        list_layout.addWidget(self.goal_tree)
        list_layout.addWidget(self.goal_add_contribution_btn)

        main_layout.addWidget(self.goal_add_group, 1)
        main_layout.addWidget(self.goal_list_group, 2)

    def _create_analysis_tab_ui(self):
        """Заповнює вкладку 'Аналіз'."""
        main_layout = QVBoxLayout(self.analysis_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        self.analysis_group = QGroupBox()
        analysis_layout = QVBoxLayout(self.analysis_group)

        self.analysis_tree = QTreeWidget()
        self.analysis_tree.setColumnCount(2)
        self.analysis_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.analysis_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        analysis_layout.addWidget(self.analysis_tree)
        main_layout.addWidget(self.analysis_group)

    def _setup_menu(self):
        """Створює верхнє меню."""
        menubar = self.menuBar()
        menubar.setObjectName("mainMenuBar")

        self.settings_menu = menubar.addMenu("")

        self.lang_menu = self.settings_menu.addMenu("")

        self.uk_action = QAction("Українська", self)
        self.uk_action.triggered.connect(lambda: self._switch_language('uk'))
        self.lang_menu.addAction(self.uk_action)

        self.en_action = QAction("English", self)
        self.en_action.triggered.connect(lambda: self._switch_language('en'))
        self.lang_menu.addAction(self.en_action)

        self.theme_menu = self.settings_menu.addMenu("")
        self.light_theme_action = QAction("", self)
        self.light_theme_action.triggered.connect(lambda: self._apply_theme('light'))
        self.theme_menu.addAction(self.light_theme_action)

        self.dark_theme_action = QAction("", self)
        self.dark_theme_action.triggered.connect(lambda: self._apply_theme('dark'))
        self.theme_menu.addAction(self.dark_theme_action)

    def _create_input_group(self) -> QGroupBox:
        """Створює групу "Додати транзакцію"."""
        group = QGroupBox()
        group.setObjectName("inputGroupBox")
        layout = QGridLayout(group)
        layout.setContentsMargins(10, 30, 10, 10)
        layout.setSpacing(10)

        self.amount_label = QLabel()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")

        self.desc_label = QLabel()
        self.desc_input = QLineEdit()

        self.cat_label = QLabel()
        self.cat_combobox = QComboBox()
        self.cat_combobox.addItems(
            ["Продукти", "Транспорт", "Комунальні", "Розваги", "Здоров'я", "Одяг", "Заощадження", "Дохід"])

        self.add_income_btn = QPushButton()
        self.add_income_btn.clicked.connect(self.add_income)
        self.add_income_btn.setIconSize(self.button_icon_size)

        self.add_expense_btn = QPushButton()
        self.add_expense_btn.clicked.connect(self.add_expense)
        self.add_expense_btn.setIconSize(self.button_icon_size)

        layout.addWidget(self.amount_label, 0, 0)
        layout.addWidget(self.amount_input, 0, 1)
        layout.addWidget(self.desc_label, 0, 2)
        layout.addWidget(self.desc_input, 0, 3)
        layout.addWidget(self.add_income_btn, 0, 4)

        layout.addWidget(self.cat_label, 1, 0)
        layout.addWidget(self.cat_combobox, 1, 1)
        layout.addWidget(self.add_expense_btn, 1, 4)

        layout.setColumnStretch(3, 1)
        return group

    def _create_converter_group(self) -> QGroupBox:
        """Створює групу "Конвертер валют"."""
        group = QGroupBox()
        group.setObjectName("converterGroupBox")
        layout = QGridLayout(group)
        layout.setContentsMargins(10, 30, 10, 10)
        layout.setSpacing(10)

        self.conv_amount_label = QLabel()
        self.conv_amount_input = QLineEdit()
        self.conv_amount_input.setPlaceholderText("100.00")
        self.conv_from_label = QLabel()
        self.conv_from_combo = QComboBox()
        self.conv_from_combo.addItems(["UAH", "USD", "EUR"])
        self.conv_from_combo.setCurrentText("USD")
        self.conv_to_label = QLabel()
        self.conv_to_combo = QComboBox()
        self.conv_to_combo.addItems(["UAH", "USD", "EUR"])
        self.conv_to_combo.setCurrentText("UAH")
        self.convert_btn = QPushButton()
        self.convert_btn.clicked.connect(self._perform_conversion)
        self.convert_btn.setIconSize(self.button_icon_size)
        self.convert_result_label = QLabel()
        self.convert_result_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.conv_amount_label, 0, 0)
        layout.addWidget(self.conv_amount_input, 0, 1)
        layout.addWidget(self.conv_from_label, 1, 0)
        layout.addWidget(self.conv_from_combo, 1, 1)
        layout.addWidget(self.conv_to_label, 2, 0)
        layout.addWidget(self.conv_to_combo, 2, 1)
        layout.addWidget(self.convert_btn, 0, 2, 3, 1)
        layout.addWidget(self.convert_result_label, 3, 0, 1, 3)

        return group

    def _create_toolbox_group(self) -> QGroupBox:
        """Створює групу "Панель інструментів"."""
        group = QGroupBox()
        group.setObjectName("toolboxGroupBox")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 30, 10, 10)
        layout.setSpacing(10)

        self.spending_report_btn = QPushButton()
        self.spending_report_btn.clicked.connect(lambda: self._generate_report(SpendingReport))
        self.spending_report_btn.setIconSize(self.button_icon_size)

        self.income_report_btn = QPushButton()
        self.income_report_btn.clicked.connect(lambda: self._generate_report(IncomeReport))
        self.income_report_btn.setIconSize(self.button_icon_size)

        self.viz_btn = QPushButton()
        self.viz_btn.clicked.connect(self._show_expense_chart)
        self.viz_btn.setIconSize(self.button_icon_size)

        self.budget_btn = QPushButton()
        self.budget_btn.clicked.connect(self.manage_budget)
        self.budget_btn.setIconSize(self.button_icon_size)

        layout.addWidget(self.spending_report_btn)
        layout.addWidget(self.income_report_btn)
        layout.addWidget(self.viz_btn)
        layout.addWidget(self.budget_btn)
        layout.addStretch()
        return group

    def _create_history_group(self) -> QGroupBox:
        """Створює групу "Історія транзакцій"."""
        group = QGroupBox()
        group.setObjectName("historyGroupBox")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 30, 10, 10)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setStretchLastSection(True)

        layout.addWidget(self.tree)
        return group

    def _set_button_icons(self):
        """Встановлює іконки для кнопок."""

        is_dark = self._current_theme == 'dark'

        menu_icon_color = '#61AFEF' if is_dark else '#007ACC'
        icon_on_button_color = '#FFFFFF'

        icon_color_red = '#E06C75' if is_dark else '#D9534F'
        icon_color_green = '#98C379' if is_dark else '#5CB85C'

        self.add_income_btn.setStyleSheet(f"background-color: {icon_color_green}; color: {icon_on_button_color};")
        self.add_expense_btn.setStyleSheet(f"background-color: {icon_color_red}; color: {icon_on_button_color};")

        self.add_income_btn.setIcon(qta.icon("fa5s.plus-circle", color=icon_on_button_color))
        self.add_expense_btn.setIcon(qta.icon("fa5s.minus-circle", color=icon_on_button_color))

        self.convert_btn.setIcon(qta.icon("fa5s.exchange-alt", color=icon_on_button_color))
        self.spending_report_btn.setIcon(qta.icon("fa5s.chart-pie", color=icon_on_button_color))
        self.income_report_btn.setIcon(qta.icon("fa5s.chart-line", color=icon_on_button_color))
        self.viz_btn.setIcon(qta.icon("fa5s.chart-bar", color=icon_on_button_color))
        self.budget_btn.setIcon(qta.icon("fa5s.money-bill-wave", color=icon_on_button_color))

        self.debt_add_btn.setIcon(qta.icon("fa5s.plus", color=icon_on_button_color))
        self.debt_mark_paid_btn.setIcon(qta.icon("fa5s.check-circle", color=icon_on_button_color))

        self.goal_add_btn.setIcon(qta.icon("fa5s.plus", color=icon_on_button_color))
        self.goal_add_contribution_btn.setIcon(qta.icon("fa5s.piggy-bank", color=icon_on_button_color))

        self.uk_action.setIcon(qta.icon("fa5s.flag", color=menu_icon_color))
        self.en_action.setIcon(qta.icon("fa5s.flag-usa", color=icon_color_red))
        self.light_theme_action.setIcon(qta.icon("fa5s.sun", color=menu_icon_color))
        self.dark_theme_action.setIcon(qta.icon("fa5s.moon", color=menu_icon_color))

        # Іконки для вкладок
        self.tabs.setTabIcon(0, qta.icon("fa5s.home", color=menu_icon_color))
        self.tabs.setTabIcon(1, qta.icon("fa5s.file-invoice-dollar", color=menu_icon_color))
        self.tabs.setTabIcon(2, qta.icon("fa5s.bullseye", color=menu_icon_color))
        self.tabs.setTabIcon(3, qta.icon("fa5s.lightbulb", color=menu_icon_color))

    def _update_ui_texts(self):
        """Оновлює ВЕСЬ текст в інтерфейсі відповідно до обраної мови."""
        self.setWindowTitle(self._loc.get("window_title"))

        self.settings_menu.setTitle(self._loc.get("settings"))
        self.lang_menu.setTitle(self._loc.get("language"))
        self.theme_menu.setTitle(self._loc.get("theme"))
        self.light_theme_action.setText(self._loc.get("light_theme"))
        self.dark_theme_action.setText(self._loc.get("dark_theme"))

        # Вкладки
        self.tabs.setTabText(0, self._loc.get("tab_dashboard"))
        self.tabs.setTabText(1, self._loc.get("tab_debts"))
        self.tabs.setTabText(2, self._loc.get("tab_goals"))
        self.tabs.setTabText(3, self._loc.get("tab_analysis"))

        # --- Вкладка Дашборд ---
        self.input_group_box.setTitle(self._loc.get("add_transaction"))
        self.amount_label.setText(self._loc.get("amount"))
        self.desc_label.setText(self._loc.get("description"))
        self.cat_label.setText(self._loc.get("category"))
        self.add_income_btn.setText(" " + self._loc.get("add_income"))
        self.add_expense_btn.setText(" " + self._loc.get("add_expense"))

        self.converter_group_box.setTitle(self._loc.get("currency_converter"))
        self.conv_amount_label.setText(self._loc.get("amount"))
        self.conv_from_label.setText(self._loc.get("from"))
        self.conv_to_label.setText(self._loc.get("to"))
        self.convert_btn.setText(" " + self._loc.get("convert"))
        self.convert_result_label.setText(self._loc.get("result"))

        self.toolbox_group_box.setTitle(self._loc.get("toolbox"))
        self.spending_report_btn.setText(" " + self._loc.get("spending_report"))
        self.income_report_btn.setText(" " + self._loc.get("income_report"))
        self.viz_btn.setText(" " + self._loc.get("visualization"))
        self.budget_btn.setText(" " + self._loc.get("manage_budget"))

        self.history_group_box.setTitle(self._loc.get("transaction_history"))
        self.tree.setHeaderLabels([
            self._loc.get("date"), self._loc.get("sum_uah"),
            self._loc.get("category"), self._loc.get("description")
        ])

        # --- Вкладка Борги ---
        self.debt_add_group.setTitle(self._loc.get("debts_add_new"))
        self.debt_name_label.setText(self._loc.get("debt_name"))
        self.debt_amount_label.setText(self._loc.get("amount"))
        self.debt_due_date_label.setText(self._loc.get("debt_due_date"))
        self.debt_type_label.setText(self._loc.get("debt_type"))
        self.debt_type_combo.clear()
        self.debt_type_combo.addItems([self._loc.get("debt_type_i_owe"), self._loc.get("debt_type_they_owe")])
        self.debt_add_btn.setText(" " + self._loc.get("debt_add_button"))
        self.debt_list_group.setTitle(self._loc.get("debt_list"))
        self.debt_tree.setHeaderLabels([
            "ID", self._loc.get("debt_column_name"), self._loc.get("debt_column_amount"),
            self._loc.get("debt_column_due_date"), self._loc.get("debt_column_type"),
            self._loc.get("debt_column_status")
        ])
        self.debt_tree.setColumnHidden(0, True)
        self.debt_mark_paid_btn.setText(" " + self._loc.get("debt_mark_as_paid"))

        # --- Вкладка Цілі ---
        self.goal_add_group.setTitle(self._loc.get("goals_add_new"))
        self.goal_name_label.setText(self._loc.get("goal_name"))
        self.goal_target_label.setText(self._loc.get("goal_target_amount"))
        self.goal_add_btn.setText(" " + self._loc.get("goal_add_button"))
        self.goal_list_group.setTitle(self._loc.get("goal_list"))
        self.goal_tree.setHeaderLabels([
            "ID", self._loc.get("goal_column_name"), self._loc.get("goal_column_progress"),
            self._loc.get("goal_column_current"), self._loc.get("goal_column_target")
        ])
        self.goal_tree.setColumnHidden(0, True)
        self.goal_add_contribution_btn.setText(" " + self._loc.get("goal_add_contribution"))

        # --- Вкладка Аналіз ---
        self.analysis_group.setTitle(self._loc.get("analysis_habits"))
        self.analysis_tree.setHeaderLabels([
            self._loc.get("analysis_column_category"),
            self._loc.get("analysis_column_amount")
        ])

        self.refresh_all_views()

    # --- Слоти та Логіка ---

    def _create_default_account(self, name):
        """Завантажує або створює рахунок за замовчуванням."""
        transactions, balance = self._db_manager.load_transactions_for_account(name)
        account = SavingsAccount(name, initial_balance=balance)
        account.transactions = transactions
        self._user.add_account(account)
        self.current_account_name = name
        logger.info(f"Завантажено/створено рахунок за замовчуванням: {name}")

    def _switch_language(self, lang_code):
        """Слот: перемикає мову та оновлює UI."""
        self._loc.set_language(lang_code)
        self._update_ui_texts()
        self._set_button_icons()

    def _apply_theme(self, theme_name):
        """Слот: застосовує обрану тему."""
        self._theme_manager.apply_theme(theme_name)
        self._current_theme = theme_name
        self._set_button_icons()
        logger.info(f"Застосовано тему: {theme_name}")
        self.refresh_all_views()

    def refresh_all_views(self):
        """Оновлює дані на всіх вкладках."""
        self.refresh_transactions_view()
        self.refresh_debts_view()
        self.refresh_goals_view()
        self.refresh_analysis_view()

    # --- Слоти для Дашборду ---
    def add_transaction(self, is_income: bool):
        try:
            amount = float(self.amount_input.text())
            description = self.desc_input.text()
            category = self.cat_combobox.currentText()

            if not description:
                QMessageBox.warning(self, self._loc.get("warning"), self._loc.get("warning_empty_description"))
                return

            self._service.add_transaction(amount, description, category, is_income)

            self.refresh_all_views()
            self.amount_input.clear()
            self.desc_input.clear()

        except InsufficientFundsError as e:
            logger.warning(f"Помилка операції: недостатньо коштів. {e}")
            QMessageBox.critical(self, self._loc.get("error_insufficient_funds"), str(e))
        except ValueError:
            logger.warning(f"Помилка вводу суми: {self.amount_input.text()}")
            QMessageBox.warning(self, self._loc.get("error_value"), self._loc.get("error_value_message"))
        except Exception as e:
            logger.critical("Сталася непередбачувана помилка!", exc_info=True)
            QMessageBox.critical(self, self._loc.get("error_unknown"), self._loc.get("error_unknown_message", error=e))

    def add_expense(self):
        self.add_transaction(is_income=False)

    def add_income(self):
        self.add_transaction(is_income=True)

    def _perform_conversion(self):
        try:
            amount = float(self.conv_amount_input.text())
            from_cur = self.conv_from_combo.currentText()
            to_cur = self.conv_to_combo.currentText()
            result = self._api_handler.convert_currency(amount, from_cur, to_cur)

            if isinstance(result, float):
                self.convert_result_label.setText(
                    f"{self._loc.get('result').replace('0.00', '')} {result:.2f} {to_cur}")
            else:
                self.convert_result_label.setText(self._loc.get('error_api'))
        except (ValueError, TypeError):
            self.convert_result_label.setText(self._loc.get('error_input'))

    def _generate_report(self, report_type: type[Report]):
        try:
            report_text, file_path = self._service.generate_report(report_type)
            QMessageBox.information(self, self._loc.get(f"{report_type.__name__.lower()}"), report_text)
            QMessageBox.information(self, self._loc.get("report_generated_success"),
                                    self._loc.get("report_generated_message", path=file_path))
        except Exception as e:
            logger.error(f"Не вдалося згенерувати звіт: {e}", exc_info=True)
            QMessageBox.critical(self, self._loc.get("error_unknown"),
                                 self._loc.get("report_generation_error", error=e))

    def _show_expense_chart(self):
        dialog = ChartSelectionDialog(self._loc, self)
        if dialog.exec_() == QDialog.Accepted:
            chart_type = dialog.selection
            account = self._service.get_current_account()
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            spending_data = SpendingReport(account).generate(start_date, end_date)

            if not spending_data:
                QMessageBox.information(self, self._loc.get("visualization"), self._loc.get("visualization_no_data"))
                return

            chart_dialog = ChartDialog(chart_type, spending_data, self._loc, self._current_theme, self)
            chart_dialog.exec_()

    def manage_budget(self):
        category, ok = QInputDialog.getText(self, self._loc.get("manage_budget"),
                                            self._loc.get("budget_category_prompt"))
        if not ok or not category:
            return

        limit, ok = QInputDialog.getDouble(self, self._loc.get("manage_budget"),
                                           self._loc.get("budget_limit_prompt", category=category), decimals=2)
        if not ok:
            return

        budget = Budget(category, limit)
        account = self._service.get_current_account()
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        transactions = account.get_transactions_by_period(start_date, end_date)
        spent = budget.get_spent_amount(transactions)

        QMessageBox.information(self, self._loc.get("budget_status_title"),
                                self._loc.get("budget_status_message", category=category, limit=limit, spent=spent))

    def refresh_transactions_view(self):
        self.tree.clear()
        try:
            account = self._service.get_current_account()

            is_dark = self._current_theme == 'dark'
            color_green = QColor("#98C379") if is_dark else QColor(0, 128, 0)
            color_red = QColor("#E06C75") if is_dark else QColor(200, 0, 0)

            for t in reversed(account.transactions):
                if isinstance(t, CategorizedTransaction):
                    item = QTreeWidgetItem([t.date, f"{t.amount:.2f}", t.category, t.description])

                    if t.category == "Дохід":
                        item.setForeground(1, color_green)
                    else:
                        item.setForeground(1, color_red)

                    self.tree.addTopLevelItem(item)

            self.tree.setColumnWidth(0, 100)
            self.tree.setColumnWidth(1, 120)
            self.tree.setColumnWidth(2, 150)

            self.balance_label.setText(self._loc.get("balance", balance=account.get_balance()))
        except Exception as e:
            logger.error(f"Не вдалося оновити список транзакцій: {e}", exc_info=True)
            self.balance_label.setText(self._loc.get("balance_error"))

    # --- Слоти для Боргів ---
    def _add_new_debt(self):
        try:
            name = self.debt_name_input.text()
            amount = float(self.debt_amount_input.text())
            due_date = self.debt_due_date_input.date().toString("yyyy-MM-dd")
            is_loan = self.debt_type_combo.currentText() == self._loc.get("debt_type_they_owe")

            if not name or amount <= 0:
                QMessageBox.warning(self, self._loc.get("error_value"), self._loc.get("error_value_message"))
                return

            self._service.add_debt(name, amount, due_date, is_loan)
            self.refresh_debts_view()

            self.debt_name_input.clear()
            self.debt_amount_input.clear()

        except ValueError:
            QMessageBox.warning(self, self._loc.get("error_value"), self._loc.get("error_value_message"))
        except Exception as e:
            logger.critical("Помилка при додаванні боргу", exc_info=True)
            QMessageBox.critical(self, self._loc.get("error_unknown"), str(e))

    def _mark_debt_as_paid(self):
        selected_item = self.debt_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, self._loc.get("warning_no_selection"), self._loc.get("warning_no_debt_selected"))
            return

        debt_id = int(selected_item.text(0))
        self._service.update_debt_status(debt_id, is_paid=True)
        self.refresh_debts_view()

    def refresh_debts_view(self):
        """Оновлює таблицю боргів."""
        self.debt_tree.clear()
        debts = self._service.load_debts_data()

        is_dark = self._current_theme == 'dark'
        color_green = QColor("#98C379") if is_dark else QColor(0, 128, 0)
        color_red = QColor("#E06C75") if is_dark else QColor(200, 0, 0)
        color_paid = QColor("#888888") if is_dark else QColor(100, 100, 100)

        for debt in debts:
            type_str = self._loc.get("debt_type_they_owe") if debt.is_loan else self._loc.get("debt_type_i_owe")
            status_str = self._loc.get("debt_status_paid") if debt.is_paid else self._loc.get("debt_status_unpaid")

            item = QTreeWidgetItem([
                str(debt.id), debt.name, f"{debt.amount:.2f}",
                debt.due_date, type_str, status_str
            ])

            if debt.is_paid:
                for i in range(1, 6): item.setForeground(i, color_paid)
            elif debt.is_loan:
                item.setForeground(2, color_green)
            else:
                item.setForeground(2, color_red)

            self.debt_tree.addTopLevelItem(item)

        self.debt_tree.setColumnWidth(1, 150)
        self.debt_tree.setColumnWidth(3, 100)

    # --- Слоти для Цілей ---
    def _add_new_goal(self):
        try:
            name = self.goal_name_input.text()
            target_amount = float(self.goal_target_input.text())

            if not name or target_amount <= 0:
                QMessageBox.warning(self, self._loc.get("error_value"), self._loc.get("error_value_message"))
                return

            self._service.add_savings_goal(name, target_amount)
            self.refresh_goals_view()

            self.goal_name_input.clear()
            self.goal_target_input.clear()

        except ValueError:
            QMessageBox.warning(self, self._loc.get("error_value"), self._loc.get("error_value_message"))
        except Exception as e:
            logger.critical("Помилка при додаванні цілі", exc_info=True)
            QMessageBox.critical(self, self._loc.get("error_unknown"), str(e))

    def _add_contribution_to_goal(self):
        selected_item = self.goal_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, self._loc.get("warning_no_selection"), self._loc.get("warning_no_goal_selected"))
            return

        goal_id = int(selected_item.text(0))
        goal_name = selected_item.text(1)

        current_balance = self._service.get_current_account().get_balance()
        prompt_title = self._loc.get("goal_contribution_prompt_title")
        base_prompt_text = self._loc.get("goal_contribution_prompt_text", name=goal_name)
        balance_text = self._loc.get("current_balance_label")
        full_prompt_text = f"{base_prompt_text}\n\n{balance_text}: {current_balance:.2f} грн"

        amount, ok = QInputDialog.getDouble(self,
                                            prompt_title,
                                            full_prompt_text,
                                            decimals=2
                                            )

        if not ok or amount <= 0:
            return

        try:
            self._service.add_contribution_to_goal(goal_id, amount)
            self.refresh_all_views()
        except InsufficientFundsError as e:
            logger.warning(f"Недостатньо коштів для внеску: {e}")
            QMessageBox.critical(self, self._loc.get("error_insufficient_funds"), str(e))
        except Exception as e:
            logger.critical("Помилка при додаванні внеску", exc_info=True)
            QMessageBox.critical(self, self._loc.get("error_unknown"), str(e))

    def refresh_goals_view(self):
        """Оновлює таблицю цілей."""
        self.goal_tree.clear()
        goals = self._service.load_goals_data()

        self.goal_tree.setColumnWidth(1, 250)
        self.goal_tree.setColumnWidth(2, 200)

        for goal in goals:
            item = QTreeWidgetItem([
                str(goal.id),
                goal.name,
                "",  # Пусте місце для прогрес-бару
                f"{goal.current_amount:.2f}",
                f"{goal.target_amount:.2f}"
            ])
            self.goal_tree.addTopLevelItem(item)

            progress = int(goal.get_progress())
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            progress_bar.setFormat(f"{progress}%")
            progress_bar.setAlignment(Qt.AlignCenter)
            # Стилізація прогрес-бару для сучасного вигляду
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #5C6370;
                    border-radius: 5px;
                    text-align: center;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #98C379;
                    border-radius: 5px;
                }
            """)
            self.goal_tree.setItemWidget(item, 2, progress_bar)

    # --- Слоти для Аналізу ---
    def refresh_analysis_view(self):
        """Оновлює вкладку аналізу."""
        self.analysis_tree.clear()
        analysis_data = self._service.get_spending_analysis()

        is_dark = self._current_theme == 'dark'
        color_red = QColor("#E06C75") if is_dark else QColor(200, 0, 0)

        for category, amount in analysis_data.items():
            item = QTreeWidgetItem([category, f"{amount:.2f}"])
            item.setForeground(1, color_red)  # Витрати червоним
            self.analysis_tree.addTopLevelItem(item)