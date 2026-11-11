# Фінансовий Асистент (Financial Assistant)
Лабораторна робота №1 (a, d) з дисципліни "Об'єктно-орієнтоване проектування"

Це повнофункціональний десктопний додаток для управління особистими фінансами з високим рівнем безпеки. Проєкт розроблений на Python з використанням PyQt5 та демонструє застосування класичних патернів проектування, принципів SOLID та UML-моделювання.

## 1. Глосарій предметної галузі
- **Транзакція (Transaction):** Базова одиниця фінансової операції, що має суму, дату, категорію та опис.
- **Рахунок (Account):** Сутність, що зберігає поточний баланс користувача та історію його транзакцій.
- **Ціль заощадження (Savings Goal):** Фінансова мета користувача з цільовою сумою та відстеженням поточного прогресу накопичення.
- **Дашборд (Dashboard):** Головна панель графічного інтерфейсу, що відображає зведену статистику та баланс.
- **Біометрична аутентифікація (Biometric Auth):** Механізм входу в систему за допомогою системних засобів ОС (Windows Hello) без введення пароля.


## 2. UML Моделювання (Diagram as Code)
Для документування архітектури було використано інструмент PlantUML. Усі 13 згенерованих діаграм повністю покривають структурні та поведінкові аспекти системи. Код діаграм зберігається у репозиторії у форматі `.puml` у директорії [`codes/`](codes/), а згенеровані зображення — у [`image/`](image/).

### Поведінкові діаграми (Behavioral):

- **Use Case Diagram** — Сценарії використання системи користувачем та зовнішніми API ([Код `.puml`](codes/Use-Case-Diagram.puml) | [Зображення `.png`](image/Use-Case-Diagram.png))
- **Activity Diagram** — Алгоритм додавання транзакції з плавальними доріжками (Swimlanes) ([Код `.puml`](codes/Activity-Diagram.puml) | [Зображення `.png`](image/Activity-Diagram.png))
- **State Machine Diagram** — Життєвий цикл цілі заощадження ([Код `.puml`](codes/State-Machine-Diagram.puml) | [Зображення `.png`](image/State-Machine-Diagram.png))
- **Sequence Diagram** — Процес біометричної авторизації у багатопотоковому середовищі (`QThread`) ([Код `.puml`](codes/Sequence-Diagram.puml) | [Зображення `.png`](image/Sequence-Diagram.png))
- **Communication Diagram** — Взаємодія об'єктів при отриманні курсу валют ([Код `.puml`](codes/Communication-Diagram.puml) | [Зображення `.png`](image/Communication-Diagram.png))
- **Timing Diagram** — Часові затримки при мережевих запитах ([Код `.puml`](codes/Timing-Diagram.puml) | [Зображення `.png`](image/Timing-Diagram.png))
- **Interaction Overview Diagram** — Глобальний потік виконання програми ([Код `.puml`](codes/Interaction-Overview-Diagram.puml) | [Зображення `.png`](image/Interaction-Overview-Diagram.png))

### Структурні діаграми (Structural):

- **Class Diagram** — Ієрархія класів моделей та сервісів ([Код `.puml`](codes/Class-Diagram.puml) | [Зображення `.png`](image/Class-Diagram.png))
- **Component Diagram** — Високорівневі модулі та їх інтерфейси ([Код `.puml`](codes/Component-Diagram.puml) | [Зображення `.png`](image/Component-Diagram.png))
- **Deployment Diagram** — Розгортання додатку на ОС та взаємодія з Credential Manager ([Код `.puml`](codes/Deployment-Diagram.puml) | [Зображення `.png`](image/Deployment-Diagram.png))
- **Package Diagram** — Організація файлової структури та імпортів ([Код `.puml`](codes/Package-Diagram.puml) | [Зображення `.png`](image/Package-Diagram.png))
- **Object Diagram** — Знімок системи в оперативній пам'яті (конкретні екземпляри) ([Код `.puml`](codes/Object-Diagram.puml) | [Зображення `.png`](image/Object-Diagram.png))
- **Composite Structure Diagram** — Внутрішня ієрархія віджетів графічного інтерфейсу PyQt5 ([Код `.puml`](codes/Composite-Structure-Diagram.puml) | [Зображення `.png`](image/Composite-Structure-Diagram.png))

## 3. Звіт-ретроспектива щодо UML інструменту (Лабораторна 1d)
**Інструмент:**
PlantUML (PlantText / IDE Plugin).

**Чому обрано?**
PlantUML реалізує підхід "Diagram as Code". Це дозволяє зберігати діаграми у вигляді звичайного тексту в Git, легко відстежувати зміни та генерувати графіку без ручного малювання стрілочок.

**Досвід використання:**
Інструмент виявився надзвичайно швидким для створення Sequence та Class діаграм. Документація вичерпна та зрозуміла.

**Складнощі:**
При побудові Communication та Package діаграм іноді виникали конфлікти синтаксису (наприклад, при змішуванні різних типів вузлів), що вимагало використання суворих псевдонімів (`as`) для компонентів та уникнення директиви `allow_mixing`.

**Висновок:**
PlantUML є ідеальним інструментом для інтеграції документації безпосередньо в CI/CD процес та репозиторій.
