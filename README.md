# Financial Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)
![Tests](https://img.shields.io/badge/Tests-pytest-blue)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

**Financial Assistant** is a desktop personal finance management application written in Python. It combines a responsive **PyQt5** graphical interface, persistent **SQLite3** storage, real-time currency conversion via **ExchangeRate-API**, **Matplotlib** analytics, and a multi-layered authentication system powered by **Argon2id**, **System Keyring**, and **Windows Hello** biometrics.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture and Design Patterns](#system-architecture-and-design-patterns)
4. [Database Schema](#database-schema)
5. [Security and Authentication Architecture](#security-and-authentication-architecture)
6. [Project Structure](#project-structure)
7. [Technology Stack](#technology-stack)
8. [Installation and Setup](#installation-and-setup)
9. [Usage Guide](#usage-guide)
10. [Testing and Benchmarking](#testing-and-benchmarking)
11. [UML Modeling and Documentation](#uml-modeling-and-documentation)
12. [Academic Requirements Compliance](#academic-requirements-compliance)
13. [Troubleshooting](#troubleshooting)
14. [License](#license)

---

## Overview

Managing personal finances often requires tracking multiple data streams simultaneously: daily income and expenses, recurring obligations, personal debts and loans, long-term savings targets, and foreign currency conversions. **Financial Assistant** consolidates these workflows into a single desktop environment while keeping all financial records local on the user's machine rather than on third-party cloud servers.

The application is designed around strict separation of concerns: the presentation layer (`gui.py`, `login_gui.py`) is decoupled from business rules (`services.py`), domain entities (`models.py`), and persistence (`database.py`). It supports runtime switching between **Ukrainian** and **English** locales as well as **Light** and **Dark** QSS themes without restarting the process.

---

## Key Features

### 1. Transaction Ledger and Dashboard
* Record income and categorized expenses (`Groceries`, `Transport`, `Utilities`, `Entertainment`, `Health`, `Clothing`, `Savings`, `Income`).
* Automatic balance recalculation and overdraft protection via custom domain exceptions (`InsufficientFundsError`).
* Chronological transaction history table with color-coded entries (green for income, red for expenses).

### 2. Real-Time Currency Converter
* Integrated currency conversion between `UAH`, `USD`, and `EUR` using the **ExchangeRate-API** v6 endpoint.
* Graceful degradation when offline or when no API key is configured, preventing application crashes and logging diagnostic details to `app.log`.

### 3. Debt and Loan Management
* Dedicated tracking for both liabilities (*"I Owe"*) and receivables (*"They Owe Me"*).
* Tracks counterparty name, principal amount, due date, and settlement status (*Paid* / *Unpaid*).
* One-click status updates persisted directly to SQLite.

### 4. Savings Goals Tracking
* Create named financial targets with custom target amounts.
* Visual progress tracking via embedded `QProgressBar` widgets inside the goals table.
* Contributing to a savings goal automatically validates available account funds, creates a corresponding expense transaction in the main ledger, and updates the goal progress atomically.

### 5. Spending Habits Analysis and Budgeting
* **Top-5 Spending Categories:** Aggregates historical expense records to identify primary cost drivers.
* **Category Budgets:** Interactive monthly budget calculator that compares user-defined category limits against actual current-month expenditures.

### 6. Reporting and Data Visualization
* **Polymorphic Report Generation:** Generates formatted monthly **Spending Reports** and **Income Reports**, displaying them in-app and exporting them to timestamped `.txt` files (`spending_report_YYYY-MM.txt`, `income_report_YYYY-MM.txt`).
* **Interactive Charts:** Renders theme-aware **Pie Charts** (category distribution percentages) and **Bar Charts** (category totals in UAH) using an embedded `FigureCanvasQTAgg` Matplotlib backend.

### 7. Dynamic Internationalization (i18n) and Theming
* Instant language switching between Ukrainian (`langs/uk.json`) and English (`langs/en.json`).
* Custom Qt Style Sheets (`LIGHT_QSS` and `DARK_QSS`) that style all controls, headers, menus, tree views, and Matplotlib chart canvases.

---

## System Architecture and Design Patterns

The codebase follows a layered architecture to ensure maintainability and testability:

```text
+-------------------------------------------------------------------+
|                        Presentation Layer                         |
|         gui.py (FinanceAppGUI, ChartDialog) | login_gui.py        |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      Service / Application Layer                  |
|      services.py (FinanceService) | auth.py | api_handler.py      |
+-----------------+-------------------------------+-----------------+
                  |                               |
                  v                               v
+-----------------------------------+   +---------------------------+
|           Domain Layer            |   |   Infrastructure Layer    |
|   models.py | exceptions.py       |   | database.py | themes.py   |
| (Account, Transaction, Report...) |   |     localization.py       |
+-----------------------------------+   +---------------------------+
```

### Applied Design Patterns
* **Layered Architecture (MVC / MVP variant):** `FinanceService` encapsulates all domain workflows and coordinates with `DatabaseManager` without importing or referencing any `PyQt5` classes.
* **Template Method / Strategy Pattern:** `Report` is an Abstract Base Class (`ABC`) defining the abstract `generate(start_date, end_date)` interface. Concrete subclasses (`SpendingReport`, `IncomeReport`) implement specific aggregation algorithms and are invoked polymorphically by `FinanceService.generate_report()`.
* **Repository / Data Access Object (DAO):** `DatabaseManager` isolates all raw SQL queries and SQLite connection lifecycle management from the rest of the application, supporting Python's context manager protocol (`with DatabaseManager(...) as db:`).
* **Asynchronous Worker Thread (Active Object / Signal-Slot):** `BiometricThread(QThread)` offloads blocking WinRT asynchronous biometric verification (`asyncio.run`) to a background OS thread and communicates results back to the Qt main event loop via a thread-safe `pyqtSignal(bool)`.

---

## Database Schema

All persistent data is stored in a local SQLite3 database (`finance_assistant.db`) managed by `DatabaseManager`:

### Table: `transactions`
| Column         | Type      | Description                                              |
| -------------- | --------- | -------------------------------------------------------- |
| `id`           | `INTEGER` | Primary Key (`AUTOINCREMENT`)                            |
| `account_name` | `TEXT`    | Associated account identifier (e.g., `"Основний"`)       |
| `amount`       | `REAL`    | Positive transaction amount                              |
| `date`         | `TEXT`    | ISO-8601 date string (`YYYY-MM-DD`)                      |
| `description`  | `TEXT`    | User-provided transaction note                           |
| `category`     | `TEXT`    | Transaction category name                                |
| `is_income`    | `INTEGER` | Boolean flag (`1` = Income, `0` = Expense)               |

### Table: `debts`
| Column     | Type      | Description                                              |
| ---------- | --------- | -------------------------------------------------------- |
| `id`       | `INTEGER` | Primary Key (`AUTOINCREMENT`)                            |
| `name`     | `TEXT`    | Counterparty or debt description                         |
| `amount`   | `REAL`    | Debt or loan amount                                      |
| `due_date` | `TEXT`    | Repayment due date (`YYYY-MM-DD`)                        |
| `is_loan`  | `INTEGER` | Boolean flag (`1` = They Owe Me, `0` = I Owe)            |
| `is_paid`  | `INTEGER` | Settlement status (`1` = Paid, `0` = Unpaid)             |

### Table: `savings_goals`
| Column           | Type      | Description                                              |
| ---------------- | --------- | -------------------------------------------------------- |
| `id`             | `INTEGER` | Primary Key (`AUTOINCREMENT`)                            |
| `name`           | `TEXT`    | Name of the savings target                               |
| `target_amount`  | `REAL`    | Target monetary amount to reach                          |
| `current_amount` | `REAL`    | Accumulated amount contributed so far                    |

---

## Security and Authentication Architecture

For full details on vulnerability reporting and security guarantees, see [SECURITY.md](SECURITY.md) and the engineering retrospective in [report.md](report.md).

1. **First-Run Registration:**
   * On startup (`main.py`), `AuthManager.is_registered()` checks for the presence of `auth_config.json`.
   * If absent, `RegistrationDialog` prompts the user to create and confirm a master password.
2. **Argon2id Password Hashing:**
   * Passwords are hashed using `argon2.PasswordHasher` (`argon2-cffi`), which generates a unique cryptographic salt and applies memory-hard Argon2id hashing.
   * On subsequent logins, `AuthManager.verify_password()` verifies the password and checks `check_needs_rehash()` to transparently upgrade hashes if parameters change.
3. **System Credential Manager Integration (`keyring`):**
   * Upon registration, an authentication state token is registered in the operating system's native credential store (Windows Credential Manager / macOS Keychain).
4. **Windows Hello Biometrics (`winsdk`):**
   * Users on Windows 10/11 can authenticate via fingerprint, facial recognition (FaceID), or system PIN using `Windows.Security.Credentials.UI.UserConsentVerifier`.
   * Verification first checks hardware/OS readiness via `check_availability_async()` and then triggers the native OS prompt via `request_verification_async()`.

---

## Project Structure

```text
UnikProject/
├── main.py                         # Application entry point, logging setup, auth flow
├── gui.py                          # Main PyQt5 window, tabs, and Matplotlib chart dialogs
├── login_gui.py                    # Registration, login dialogs, and BiometricThread
├── services.py                     # Business logic layer (FinanceService)
├── models.py                       # Domain models (Account, Transaction, Debt, Goal, Report)
├── database.py                     # SQLite3 persistence layer (DatabaseManager)
├── auth.py                         # Authentication manager (Argon2id, Keyring, Windows Hello)
├── api_handler.py                  # ExchangeRate-API HTTP client with timeout & fallback
├── localization.py                 # JSON translation loader and string formatter
├── themes.py                       # Light and Dark QSS stylesheets (ThemeManager)
├── exceptions.py                   # Custom domain exceptions (InsufficientFundsError)
├── langs/                          # Localization dictionaries
│   ├── uk.json                     # Ukrainian strings
│   └── en.json                     # English strings
├── tests/                          # Automated test suite
│   ├── test_models.py              # Unit tests for accounts, transactions, reports, goals
│   ├── test_services_and_auth.py   # Integration tests for services, SQLite, auth, i18n
│   └── test_benchmarks.py          # Performance microbenchmarks (pytest-benchmark)
├── lab1/                           # Architectural UML documentation (PlantUML)
│   ├── README.md                   # Domain glossary, diagram index, and retrospective
│   ├── codes/                      # 13 PlantUML source files (.puml)
│   └── image/                      # 13 rendered UML diagrams (.png)
├── report.md                       # Technical retrospective on security implementation
├── SECURITY.md                     # Security policy and vulnerability disclosure guide
├── LICENSE                         # MIT License
├── requirements.txt                # Python package dependencies
├── .env.example                    # Template for environment variables
└── pytest.ini                      # Pytest configuration
```

---

## Technology Stack

| Category                  | Library / Tool     | Purpose                                                    |
| ------------------------- | ------------------ | ---------------------------------------------------------- |
| **Language**              | Python 3.10+       | Core programming language                                  |
| **GUI Framework**         | `PyQt5`            | Desktop widgets, layouts, dialogs, signals/slots, threading|
| **Iconography**           | `QtAwesome`        | Font Awesome 5 vector icons for buttons, tabs, and menus   |
| **Data Visualization**    | `matplotlib`       | Pie and bar chart rendering via `FigureCanvasQTAgg`        |
| **Database**              | `sqlite3`          | Embedded relational database for local persistence         |
| **HTTP Client**           | `requests`         | REST API calls to ExchangeRate-API                         |
| **Environment Config**    | `python-dotenv`    | Loading secrets from `.env`                                |
| **Password Hashing**      | `argon2-cffi`      | OWASP-recommended Argon2id password hashing                |
| **Credential Storage**    | `keyring`          | OS-level secret storage (Windows Credential Manager)       |
| **Biometric Auth**        | `winsdk`           | Windows Runtime (`WinRT`) bindings for Windows Hello       |
| **Testing & Benchmarks**  | `pytest`, `pytest-benchmark` | Unit testing, fixtures, and performance profiling |
| **Architecture Modeling** | `PlantUML`         | Diagram-as-Code UML documentation                          |

---

## Installation and Setup

### Prerequisites
* **Python 3.10 or higher** (tested on Python 3.12).
* **Operating System:** Windows 10/11 (recommended for Windows Hello biometric support; password authentication works cross-platform on Windows, Linux, and macOS).

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/oleksandrmyhydiuk/UnikProject.git
   cd UnikProject
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell / CMD):
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Currency Exchange API Key:**
   * Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   * Obtain a free API key from [ExchangeRate-API](https://www.exchangerate-api.com/) and set it in `.env`:
     ```env
     EXCHANGERATE_API_KEY="your_actual_api_key"
     ```
   *(Note: The application will still launch and function normally without an API key, except currency conversion requests will return an offline warning).*

5. **Run the application:**
   ```bash
   python main.py
   ```

---

## Usage Guide

1. **Initial Registration:** On first launch, enter and confirm a master password. This creates `auth_config.json` with your Argon2id hash.
2. **Authentication:** Log in using your password or click **Login via System / FaceID** to authenticate with Windows Hello.
3. **Managing Transactions (Dashboard Tab):**
   * Enter an amount, description, and category, then click **Add Income** or **Add Expense**.
   * Use the **Toolbox** panel to generate monthly text reports, open Pie/Bar charts, or check category budgets.
4. **Tracking Debts (Debts Tab):**
   * Add a counterparty name, amount, due date, and debt direction (*I Owe* / *They Owe Me*).
   * Select any unpaid entry and click **Mark as Paid** once settled.
5. **Savings Goals (Goals Tab):**
   * Define a goal name and target amount.
   * Select a goal and click **Add Contribution** to transfer funds from your active balance toward the goal.
6. **Switching Language and Theme:**
   * Use the top menu bar (**Settings -> Language** or **Settings -> Theme**) to switch between Ukrainian/English and Light/Dark modes at any time.

---

## Testing and Benchmarking

The project includes an automated test suite covering domain models, reports, database persistence, authentication, localization completeness, and performance benchmarks.

### Running Unit Tests
```bash
pytest
```

### Running Performance Benchmarks Only
```bash
pytest --benchmark-only
```

### Test Suite Coverage
* `tests/test_models.py`: Tests `Account` income/expense operations, `InsufficientFundsError` exception handling and message formatting, zero-balance edge cases, `SavingsAccount` interest calculation, `SpendingReport` and `IncomeReport` filtering, `Budget` calculations, and `SavingsGoal` progress capping.
* `tests/test_services_and_auth.py`: Tests `AuthManager` registration and Argon2 verification using temporary files, `FinanceService` CRUD workflows with in-memory SQLite (`:memory:`), key parity between `uk.json` and `en.json`, and `APIHandler` fallback behavior when no API key is present.
* `tests/test_benchmarks.py`: Profiles `FinanceService.add_transaction` and `FinanceService.get_spending_analysis` over an account pre-populated with 1,000 categorized transactions.

### Reference Benchmark Results (Python 3.12, Windows)
| Benchmark Name                         | Min (us) | Median (us) | Mean (us) | Operations / Sec (OPS) |
| -------------------------------------- | -------- | ----------- | --------- | ---------------------- |
| `test_add_transaction_benchmark`       | ~10.5    | ~11.1       | ~11.9     | ~83,700 ops/sec        |
| `test_get_spending_analysis_benchmark` | ~5,764.3 | ~6,329.2    | ~6,575.7  | ~152 ops/sec           |

---

## UML Modeling and Documentation

Complete architectural modeling (13 UML diagrams created with PlantUML following the *Diagram as Code* methodology) is located in the [`lab1/`](lab1/README.md) directory:

* **Behavioral Diagrams:**
  * [Use Case Diagram](lab1/image/Use-Case-Diagram.png) ([source](lab1/codes/Use-Case-Diagram.puml))
  * [Activity Diagram](lab1/image/Activity-Diagram.png) ([source](lab1/codes/Activity-Diagram.puml))
  * [State Machine Diagram](lab1/image/State-Machine-Diagram.png) ([source](lab1/codes/State-Machine-Diagram.puml))
  * [Sequence Diagram](lab1/image/Sequence-Diagram.png) ([source](lab1/codes/Sequence-Diagram.puml))
  * [Communication Diagram](lab1/image/Communication-Diagram.png) ([source](lab1/codes/Communication-Diagram.puml))
  * [Timing Diagram](lab1/image/Timing-Diagram.png) ([source](lab1/codes/Timing-Diagram.puml))
  * [Interaction Overview Diagram](lab1/image/Interaction-Overview-Diagram.png) ([source](lab1/codes/Interaction-Overview-Diagram.puml))
* **Structural Diagrams:**
  * [Class Diagram](lab1/image/Class-Diagram.png) ([source](lab1/codes/Class-Diagram.puml))
  * [Component Diagram](lab1/image/Component-Diagram.png) ([source](lab1/codes/Component-Diagram.puml))
  * [Deployment Diagram](lab1/image/Deployment-Diagram.png) ([source](lab1/codes/Deployment-Diagram.puml))
  * [Package Diagram](lab1/image/Package-Diagram.png) ([source](lab1/codes/Package-Diagram.puml))
  * [Object Diagram](lab1/image/Object-Diagram.png) ([source](lab1/codes/Object-Diagram.puml))
  * [Composite Structure Diagram](lab1/image/Composite-Structure-Diagram.png) ([source](lab1/codes/Composite-Structure-Diagram.puml))

---

## Academic Requirements Compliance

The project was developed in accordance with academic requirements for Object-Oriented Programming (OOP) and software architecture.

### Architecture
* **Separation of Concerns:**
  * **`gui.py` / `login_gui.py` (View):** Responsible strictly for UI construction, user input collection, and view updates.
  * **`services.py` (Business Logic):** `FinanceService` coordinates domain operations without any dependency on the GUI.
  * **`models.py` / `database.py` (Data):** Encapsulate domain state, validation rules, and SQLite CRUD persistence.
  * **`auth.py` / `localization.py` / `themes.py` (Managers):** Dedicated components for authentication, internationalization, and QSS styling.

### GUI Requirements
* **At least 4 windows/forms:** **Met (10+).**
  1. `QMainWindow` (`FinanceAppGUI` — Main application window)
  2. `RegistrationDialog` (First-run password setup dialog)
  3. `LoginDialog` (Password & biometric authentication dialog)
  4. "Dashboard" Tab
  5. "Debts" Tab
  6. "Goals" Tab
  7. "Analysis" Tab
  8. `ChartSelectionDialog` (Visualization type selector)
  9. `ChartDialog` (Matplotlib canvas dialog)
  10. `QInputDialog` & `QMessageBox` modals (budget setup, goal contributions, reports, alerts).
* **At least 20 controls:** **Met (60+).**
  Uses `QTabWidget`, `QGroupBox`, `QPushButton`, `QLabel`, `QLineEdit`, `QComboBox`, `QDateEdit`, `QTreeWidget`, `QProgressBar`, `QAction`, `QMenuBar`, `QMenu`, etc.
* **Container control:** **Met.**
  Uses `QTreeWidget` across 4 views (transactions, debts, goals, habit analysis) and `QTabWidget` for top-level navigation.
* **At least 10 event handlers:** **Met (20+).**
  Dedicated slot methods handle all button clicks, menu triggers, and background thread signals (`add_transaction`, `_generate_report`, `_switch_language`, `_apply_theme`, `_add_new_debt`, `_mark_debt_as_paid`, `_add_new_goal`, `_add_contribution_to_goal`, `start_biometric_check`, `on_biometric_result`, etc.).

### OOP Requirements
* **At least 9 classes:** **Met (20+).**
  * *GUI:* `FinanceAppGUI`, `ChartDialog`, `ChartSelectionDialog`, `BaseAuthDialog`, `RegistrationDialog`, `LoginDialog`, `BiometricThread`.
  * *Services & Managers:* `FinanceService`, `AuthManager`, `LocalizationManager`, `ThemeManager`, `DatabaseManager`, `APIHandler`.
  * *Models:* `User`, `Account`, `SavingsAccount`, `Debt`, `SavingsGoal`, `Budget`.
  * *Transaction Hierarchy:* `Transaction`, `CategorizedTransaction`, `RecurringTransaction`.
  * *Report Hierarchy:* `Report` (ABC), `SpendingReport`, `IncomeReport`.
  * *Exceptions:* `InsufficientFundsError`.
* **At least 25 non-trivial methods:** **Met.**
  Includes business operations in `services.py` (`add_contribution_to_goal`, `get_spending_analysis`, `generate_report`), authentication routines in `auth.py` (`verify_biometrics`, `_verify_windows_hello`), domain methods in `models.py` (`add_transaction`, `get_transactions_by_period`, `get_progress`), and dynamic UI updates in `gui.py`.
* **At least 2 inheritance hierarchies (one 3+ levels deep):** **Met.**
  * **Depth 3 (Domain):** `Transaction` -> `CategorizedTransaction` -> `RecurringTransaction`.
  * **Depth 3 (GUI):** `QDialog` -> `BaseAuthDialog` -> `LoginDialog` / `RegistrationDialog`.
  * **Depth 2 (Domain):** `Account` -> `SavingsAccount`.
  * **Depth 2 (Abstraction):** `Report` (ABC) -> `SpendingReport` / `IncomeReport`.
* **Abstraction / Interfaces:** **Met.**
  `Report` is an Abstract Base Class (`ABC`) with an `@abstractmethod` `generate()`, enforcing a strict contract on `SpendingReport` and `IncomeReport`.
* **Polymorphism:** **Met.**
  `FinanceService.generate_report(report_type: type[Report])` accepts any `Report` subclass and polymorphically invokes its `.generate()` implementation.

---

## Troubleshooting

* **Currency converter displays `API Error`:**
  Verify that `.env` exists in the project root, contains a valid `EXCHANGERATE_API_KEY`, and that your machine has an active internet connection. Check `app.log` for detailed HTTP status codes.
* **Windows Hello biometric login fails or is unavailable:**
  Ensure you are running Windows 10 or 11 with a PIN, fingerprint, or facial recognition configured in Windows Settings (*Accounts -> Sign-in options*), and that `winsdk` is installed (`pip install winsdk`).
* **Resetting forgotten master password:**
  Delete `auth_config.json` from the project root directory and restart `python main.py` to trigger the registration dialog again. Existing financial data in `finance_assistant.db` will remain intact.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
