# Financial Assistant

This is a full-featured desktop application for personal finance management, developed in Python.

The interface is built using **PyQt5** and `qtawesome` for icons, ensuring a modern look and feel. The application supports themes (light/dark) and internationalization (Ukrainian/English) with dynamic switching.

## 🚀 Key Features

  * **Dashboard:** Add income and expenses, view transaction history in a table, and see the current balance.
  * **Currency Converter:** A built-in converter that uses an API to fetch real-time exchange rates.
  * **Debt Management:** A separate tab to track your debts and loans (what you owe and what others owe you).
  * **Savings Goals:** The ability to create goals, make contributions (with automatic deduction from your balance), and track your progress.
  * **Habit Analysis:** A tab that shows your "Top 5" spending categories.
  * **Reports:** Generate text reports for monthly income and expenses.
  * **Visualization:** Build pie and bar charts to analyze spending.
  * **Settings:** Dynamically switch the language (i18n) and theme (Light/Dark mode) without restarting the application.

## 🛠️ Technologies Used

  * **Language:** Python 3
  * **Graphical Interface (GUI):** PyQt5
  * **Icons:** qtawesome (Font Awesome 5)
  * **Visualization:** Matplotlib (integrated with PyQt5)
  * **Database:** SQLite3 (via the built-in `sqlite3` module)
  * **API Requests:** `requests`
  * **Security (API Key):** `python-dotenv`
  * **Testing:** `pytest` (including `unittest` compatibility)
  * **Benchmarking:** `pytest-benchmark`
  * **Logging:** `logging`
  * **Internationalization (i18n):** `json`

## ⚙️ Installation and Launch

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-name/your-repository.git
    cd your-repository
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install PyQt5 qtawesome[font-awesome5] matplotlib requests python-dotenv pytest pytest-benchmark
    ```

4.  **Set up the API key:**

      * Create a `.env` file in the project's root directory.
      * Add your key from [ExchangeRate-API](https://www.exchangerate-api.com/) to it:
        ```
        EXCHANGERATE_API_KEY="YOUR_API_KEY"
        ```

5.  **Run the application:**

    ```bash
    python main.py
    ```

6.  **Run tests:**

    ```bash
    pytest
    ```

7.  **Run benchmarks (performance measurement):**

    ```bash
    pytest --benchmark-only
    ```

-----

## 📋 Academic Requirements Compliance

The project was developed in accordance with specific academic requirements for OOP and architecture.

### Architecture

  * **Separation of Concerns:** A clear separation of responsibilities is implemented.
      * **`gui.py` (View):** Contains only code responsible for creating and updating the UI.
      * **`services.py` (Business Logic):** Contains the "brain" of the application. `FinanceService` manages all operations without knowing about the GUI's existence.
      * **`models.py` / `database.py` (Data):** Encapsulate the application state and database interactions.
      * **`localization.py` / `themes.py` (Managers):** Separate classes for managing language and style.

### GUI Requirements

  * **At least 4 windows/forms:** **Met (9+).**

    1  `QMainWindow` (Main window)
    2  "Dashboard" Tab
    3  "Debts" Tab
    4  "Goals" Tab
    5  "Analysis" Tab
    6  `ChartSelectionDialog` (Visualization selection dialog)
    7  `ChartDialog` (Chart display dialog)
    8  `QInputDialog` (for budget)
    9  `QInputDialog` (for goal contribution)
    10 Numerous `QMessageBox` (errors, warnings).

  * **At least 20 controls:** **Met (60+).**
    Uses `QTabWidget`, `QGroupBox`, `QPushButton`, `QLabel`, `QLineEdit`, `QComboBox`, `QDateEdit`, `QTreeWidget`, `QProgressBar`, `QAction`, `QMenuBar`, `QMenu`, etc.

  * **Container control:** **Met.**
    `QTreeWidget` is actively used (4 times: history, debts, goals, analysis) and `QTabWidget` (for navigation).

  * **At least 10 event handlers:** **Met (20+).**
    Slots are implemented for all buttons and menu actions (`add_transaction`, `_generate_report`, `_switch_language`, `_apply_theme`, `_add_new_debt`, `_mark_debt_as_paid`, `_add_new_goal`, `_add_contribution_to_goal`, and many others).

### OOP Requirements

  * **At least 9 classes:** **Met (20+).**

      * *GUI:* `FinanceAppGUI`, `ChartDialog`, `ChartSelectionDialog`.
      * *Services:* `FinanceService`, `LocalizationManager`, `ThemeManager`, `DatabaseManager`, `APIHandler`.
      * *Models:* `User`, `Account`, `Debt`, `SavingsGoal`, `Budget`.
      * *Transaction Hierarchy:* `Transaction`, `CategorizedTransaction`, `RecurringTransaction`.
      * *Report Hierarchy:* `Report` (ABC), `SpendingReport`, `IncomeReport`.
      * *Errors:* `InsufficientFundsError`.
      * *Tests:* `TestAccount` (in `test_models.py`).

  * **At least 25 non-trivial methods:** **Met.**
    Most business logic resides in `services.py` (e.g., `add_contribution_to_goal`, `get_spending_analysis`) and `models.py` (`add_transaction`, `get_progress`). GUI methods like `_update_ui_texts` and `refresh_goals_view` (which creates a `QProgressBar`) are also non-trivial.

  * **At least 2 inheritance hierarchies (one 3+):** **Met.**

    1  **Depth 3:** `Transaction` → `CategorizedTransaction` → `RecurringTransaction`.
    2  **Depth 2:** `Account` → `SavingsAccount`.
    3  **Depth 2 (Abstraction):** `Report` (ABC) → `SpendingReport` / `IncomeReport`.

  * **Abstraction / Interfaces:** **Met.**
    The `Report` class is an **Abstract Base Class (ABC)** with an `@abstractmethod` `generate()`, forcing descendant classes `SpendingReport` and `IncomeReport` to implement this method.

  * **Polymorphism:** **Met.**
    Dynamic polymorphism is implemented in the `_generate_report` method, which accepts a class type (`SpendingReport` or `IncomeReport`) and polymorphically calls the correct `.generate()` implementation.

### Additional Technologies

  * **Database Interaction:** **Met.**
    Uses `sqlite3` for persistent data storage. The `DatabaseManager` class implements CRUD logic (Create, Read, Update) for all entities (transactions, debts, goals) in three separate tables.

  * **Unit Testing:** **Met.**
    Uses `pytest` (`tests/test_models.py`) to verify the logic of the `Account` model (adding income, expenses, handling `InsufficientFundsError`) and `SavingsGoal` logic.

  * **Microbenchmarking:** **Met.**
    Uses `pytest-benchmark` (`tests/test_benchmarks.py`) to measure the performance of key functions (`get_spending_analysis`, `add_transaction`) and detect performance regressions.

  * **Logging:** **Met.**
    Uses the `logging` module. Logs are configured in `main.py` and written to `app.log`. Loggers are active in all key modules (`gui.py`, `services.py`, `api_handler.py`, `database.py`) to record actions and errors.

  * **i18n (Internationalization):** **Met.**
    Implemented via `LocalizationManager` and `uk.json` / `en.json` files. The application supports dynamic language switching through the menu without a restart.
