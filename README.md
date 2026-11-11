# 💰 Financial Assistant (Фінансовий Асистент)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52?logo=qt&logoColor=white)
![Security](https://img.shields.io/badge/Auth-Argon2%20%2B%20Windows%20Hello-blueviolet)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Financial Assistant** — це повнофункціональний десктопний додаток для управління особистими фінансами, розроблений мовою **Python** з використанням **PyQt5**, **SQLite3**, **Matplotlib** та багаторівневої системи захисту (**Argon2id**, **Windows Hello**, **Keyring**).

Інтерфейс побудовано на основі **PyQt5** та `qtawesome` (Font Awesome 5), з підтримкою динамічного перемикання тем (**Light / Dark**) та локалізації (**Українська / English**) без перезапуску програми.

---

## ✨ Основні можливості (Key Features)

* **📊 Дашборд (Dashboard):** Додавання доходів і витрат, перегляд історії транзакцій у таблиці та відстеження поточного балансу в реальному часі.
* **💱 Конвертер валют (Currency Converter):** Вбудований конвертер, що отримує актуальні курси валют через **ExchangeRate-API**.
* **🤝 Керування боргами (Debt Management):** Окрема вкладка для обліку власних боргів і позик («Я винен» / «Мені винні») з контролем термінів погашення.
* **🎯 Цілі заощаджень (Savings Goals):** Створення фінансових цілей, внесення коштів з автоматичним списанням із основного балансу та візуалізація прогресу через `QProgressBar`.
* **📈 Аналіз фінансових звичок (Habit Analysis):** Автоматичне визначення «Топ-5» найбільших категорій витрат.
* **📄 Звіти (Reports):** Генерація та експорт текстових звітів про доходи та витрати за поточний місяць.
* **📉 Візуалізація (Visualization):** Побудова кругових (`Pie Chart`) та стовпчикових (`Bar Chart`) діаграм витрат за допомогою інтегрованого `Matplotlib`.
* **⚙️ Налаштування (Settings):** Динамічне перемикання мови інтерфейсу (i18n: `uk` / `en`) та візуальної теми (Light / Dark QSS).

---

## 🔐 Безпека та біометрична автентифікація (Security & Biometrics)

Детальна політика безпеки описана у файлі [SECURITY.md](SECURITY.md), а ретроспективний звіт щодо імплементації — у [report.md](report.md).

* **Автентифікація:**
  * Реєстрація та вхід за паролем, захищеним сучасним алгоритмом хешування **Argon2id** (`argon2-cffi`).
  * **Біометричний вхід:** Інтеграція з **Windows Hello** (FaceID, відбиток пальця, PIN) через пакет `winsdk`.
* **Технології захисту:**
  * `argon2-cffi`: Стійке до GPU-атак хешування паролів із автоматичним керуванням сіллю.
  * `keyring`: Збереження токенів у системному сховищі секретів ОС (Windows Credential Manager).
  * `winsdk` + `asyncio`: Асинхронна взаємодія з Windows Runtime API (`UserConsentVerifier`).
  * `QThread` (`BiometricThread`): Виконання біометричної перевірки у фоновому потоці для збереження чутливості графічного інтерфейсу.

---

## 🗂 Структура проєкту (Project Structure)

```text
UnikProject/
├── main.py                  # Точка входу в додаток, налаштування логування та потоку авторизації
├── gui.py                   # Головне вікно додатку (PyQt5) та діалоги графіків (Matplotlib)
├── login_gui.py             # Вікна реєстрації, входу та багатопотокової біометрії (BiometricThread)
├── services.py              # Бізнес-логіка додатку (FinanceService)
├── models.py                # Доменні моделі (Account, Transaction, SavingsGoal, Debt, Budget, Report)
├── database.py              # Керування базою даних SQLite3 (DatabaseManager)
├── auth.py                  # Менеджер автентифікації (Argon2, Keyring, Windows Hello)
├── api_handler.py           # Клієнт ExchangeRate-API для конвертації валют
├── localization.py          # Менеджер інтернаціоналізації (i18n)
├── themes.py                # QSS-стилі для світлої та темної тем (ThemeManager)
├── exceptions.py            # Користувацькі винятки (InsufficientFundsError)
├── langs/                   # Файли перекладів інтерфейсу
│   ├── uk.json              # Українська локалізація
│   └── en.json              # Англійська локалізація
├── tests/                   # Модульні тести та мікробенчмарки
│   ├── test_models.py       # Тести доменних моделей і звітів
│   ├── test_services_and_auth.py # Тести сервісів, БД, авторизації та локалізації
│   └── test_benchmarks.py   # Бенчмарки продуктивності (pytest-benchmark)
├── lab1/                    # Документація та 13 UML-діаграм (PlantUML)
│   ├── README.md            # Опис глосарію, діаграм та ретроспектива PlantUML
│   ├── codes/               # Вихідний код діаграм (.puml)
│   └── image/               # Згенеровані зображення діаграм (.png)
├── report.md                # Звіт-ретроспектива щодо реалізації системи безпеки
├── SECURITY.md              # Політика безпеки проєкту
├── LICENSE                  # Ліцензія MIT
├── requirements.txt         # Залежності проєкту
├── .env.example             # Шаблон змінних оточення
└── pytest.ini               # Конфігурація тестового фреймворку pytest
```

---

## 🛠 Використані технології (Technologies Used)

* **Мова програмування:** Python 3.10+
* **Графічний інтерфейс (GUI):** PyQt5, QtAwesome (Font Awesome 5)
* **Візуалізація даних:** Matplotlib (`FigureCanvasQTAgg`)
* **База даних:** SQLite3 (`sqlite3`)
* **Мережеві запити:** `requests`, `python-dotenv`
* **Безпека та біометрія:** `argon2-cffi`, `keyring`, `winsdk`, `asyncio`, `QThread`
* **Тестування та бенчмаркінг:** `pytest`, `pytest-benchmark`
* **Моделювання архітектури:** PlantUML (13 структурних та поведінкових діаграм у [`lab1/`](lab1/README.md))

---

## 🚀 Встановлення та запуск (Installation & Launch)

1. **Клонуйте репозиторій:**

   ```bash
   git clone https://github.com/oleksandrmyhydiuk/UnikProject.git
   cd UnikProject
   ```

2. **Створіть та активуйте віртуальне середовище (рекомендовано):**

   ```bash
   python -m venv .venv
   # На Windows:
   .venv\Scripts\activate
   # На Linux / macOS:
   source .venv/bin/activate
   ```

3. **Встановіть залежності:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Налаштуйте API-ключ для конвертера валют:**

   * Скопіюйте файл `.env.example` у `.env`:
     ```bash
     cp .env.example .env
     ```
   * Додайте свій безкоштовний ключ від [ExchangeRate-API](https://www.exchangerate-api.com/):
     ```env
     EXCHANGERATE_API_KEY="YOUR_API_KEY"
     ```

5. **Запустіть програму:**

   ```bash
   python main.py
   ```

6. **Запуск тестів та бенчмарків:**

   ```bash
   # Запуск усіх модульних тестів та перевірок
   pytest

   # Запуск виключно мікробенчмарків продуктивності
   pytest --benchmark-only
   ```

---

## 📐 UML-моделювання та документація

* **[Лабораторна робота №1 — UML Моделювання (`lab1/README.md`)](lab1/README.md):** Глосарій предметної галузі та 13 UML-діаграм (Use Case, Activity, State Machine, Sequence, Communication, Timing, Interaction Overview, Class, Component, Deployment, Package, Object, Composite Structure) з кодом у [`lab1/codes/`](lab1/codes/) та зображеннями у [`lab1/image/`](lab1/image/).
* **[Звіт-ретроспектива з безпеки (`report.md`)](report.md):** Детальний аналіз інтеграції `argon2-cffi`, `keyring` та `winsdk` (Windows Hello).

---

## 🎓 Academic Requirements Compliance

The project was developed in accordance with specific academic requirements for OOP and architecture.

### Architecture

* **Separation of Concerns:** A clear separation of responsibilities is implemented.
  * **`gui.py` / `login_gui.py` (View):** Contains code responsible for creating and updating the UI.
  * **`services.py` (Business Logic):** Contains the "brain" of the application. `FinanceService` manages all operations without knowing about the GUI's existence.
  * **`models.py` / `database.py` (Data):** Encapsulate the application state and database interactions.
  * **`auth.py` / `localization.py` / `themes.py` (Managers):** Separate classes for managing security, language, and style.

### GUI Requirements

* **At least 4 windows/forms:** **Met (10+).**
  1. `QMainWindow` (`FinanceAppGUI` — Main window)
  2. `RegistrationDialog` & `LoginDialog` (Authentication dialogs)
  3. "Dashboard" Tab
  4. "Debts" Tab
  5. "Goals" Tab
  6. "Analysis" Tab
  7. `ChartSelectionDialog` (Visualization selection dialog)
  8. `ChartDialog` (Chart display dialog)
  9. `QInputDialog` (for budget & goal contribution)
  10. Numerous `QMessageBox` dialogs (errors, warnings, reports).

* **At least 20 controls:** **Met (60+).**
  Uses `QTabWidget`, `QGroupBox`, `QPushButton`, `QLabel`, `QLineEdit`, `QComboBox`, `QDateEdit`, `QTreeWidget`, `QProgressBar`, `QAction`, `QMenuBar`, `QMenu`, etc.

* **Container control:** **Met.**
  `QTreeWidget` is actively used (4 times: history, debts, goals, analysis) and `QTabWidget` (for navigation).

* **At least 10 event handlers:** **Met (20+).**
  Slots are implemented for all buttons and menu actions (`add_transaction`, `_generate_report`, `_switch_language`, `_apply_theme`, `_add_new_debt`, `_mark_debt_as_paid`, `_add_new_goal`, `_add_contribution_to_goal`, `start_biometric_check`, and many others).

### OOP Requirements

* **At least 9 classes:** **Met (20+).**
  * *GUI:* `FinanceAppGUI`, `ChartDialog`, `ChartSelectionDialog`, `BaseAuthDialog`, `RegistrationDialog`, `LoginDialog`, `BiometricThread`.
  * *Services & Managers:* `FinanceService`, `AuthManager`, `LocalizationManager`, `ThemeManager`, `DatabaseManager`, `APIHandler`.
  * *Models:* `User`, `Account`, `SavingsAccount`, `Debt`, `SavingsGoal`, `Budget`.
  * *Transaction Hierarchy:* `Transaction`, `CategorizedTransaction`, `RecurringTransaction`.
  * *Report Hierarchy:* `Report` (ABC), `SpendingReport`, `IncomeReport`.
  * *Errors:* `InsufficientFundsError`.

* **At least 25 non-trivial methods:** **Met.**
  Most business logic resides in `services.py` (e.g., `add_contribution_to_goal`, `get_spending_analysis`), `auth.py` (`verify_biometrics`, `verify_password`), and `models.py` (`add_transaction`, `get_progress`). GUI methods like `_update_ui_texts` and `refresh_goals_view` are also non-trivial.

* **At least 2 inheritance hierarchies (one 3+):** **Met.**
  * **Depth 3:** `Transaction` → `CategorizedTransaction` → `RecurringTransaction`.
  * **Depth 3 (GUI):** `QDialog` → `BaseAuthDialog` → `LoginDialog` / `RegistrationDialog`.
  * **Depth 2:** `Account` → `SavingsAccount`.
  * **Depth 2 (Abstraction):** `Report` (ABC) → `SpendingReport` / `IncomeReport`.

* **Abstraction / Interfaces:** **Met.**
  The `Report` class is an **Abstract Base Class (ABC)** with an `@abstractmethod` `generate()`, forcing descendant classes `SpendingReport` and `IncomeReport` to implement this method.

* **Polymorphism:** **Met.**
  Dynamic polymorphism is implemented in the `_generate_report` method, which accepts a class type (`SpendingReport` or `IncomeReport`) and polymorphically calls the correct `.generate()` implementation.

---

## 📄 Ліцензія (License)

Цей проєкт ліцензовано на умовах **MIT License** — детальніше дивіться у файлі [LICENSE](LICENSE).
