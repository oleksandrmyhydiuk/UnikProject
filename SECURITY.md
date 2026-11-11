# Security Policy

## Supported Versions

Security updates and patches are currently provided for the following versions of **Financial Assistant**:

| Version | Supported |
| ------- | --------- |
| 1.x.x   | Yes       |
| < 1.0   | No        |

---

## Security Architecture

**Financial Assistant** implements multiple layers of defense to protect local financial records, credentials, and external API integrations:

### 1. Password Hashing (`argon2-cffi`)
* User passwords are never stored in plain text.
* The application uses **Argon2id** (winner of the Password Hashing Competition and recommended by OWASP) via `argon2.PasswordHasher`.
* Each password hash is automatically salted with a cryptographically random salt.
* During login verification, `check_needs_rehash()` inspects the stored hash parameters and transparently upgrades the hash if security parameters are increased.

### 2. Biometric Authentication (`winsdk` / Windows Hello)
* Passwordless authentication is supported on Windows 10/11 through the native **Windows Hello** subsystem (`Windows.Security.Credentials.UI.UserConsentVerifier`).
* Biometric verification (fingerprint, facial recognition, or system PIN) is executed by the operating system kernel/security subsystem; raw biometric data is never accessed or stored by the application.
* Calls to the asynchronous WinRT API (`asyncio`) are isolated inside a dedicated `QThread` (`BiometricThread`) to prevent UI freezes and race conditions.

### 3. System Credential Storage (`keyring`)
* Authentication tokens are stored in the operating system's native credential manager (**Windows Credential Manager**, **macOS Keychain**, or **Linux Secret Service**) via the `keyring` library rather than in plain configuration files.

### 4. Secret and Environment Isolation (`python-dotenv`)
* Third-party API credentials (such as `EXCHANGERATE_API_KEY`) are loaded from a local `.env` file.
* Both `.env` and `auth_config.json` are excluded from version control via `.gitignore`. Only a sanitized `.env.example` template is tracked in the repository.

### 5. SQL Injection Prevention (`sqlite3`)
* All database operations in `DatabaseManager` (`database.py`) exclusively use parameterized SQL queries (`?` placeholders).
* Database mutations are wrapped in exception handlers that trigger `conn.rollback()` on failure to maintain data integrity.

For an engineering retrospective on the design and implementation of these mechanisms, refer to [report.md](report.md).

---

## Security Best Practices for Users

* **Do not commit sensitive files:** Never force-add `.env`, `auth_config.json`, `finance_assistant.db`, or `app.log` to a public Git repository.
* **Use a strong master password:** Choose a unique password during initial registration.
* **Keep dependencies updated:** Periodically update packages via `pip install --upgrade -r requirements.txt` to receive upstream security fixes in `argon2-cffi`, `requests`, and `PyQt5`.

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please disclose it responsibly:

1. **Do not open a public GitHub Issue** describing the exploit or vulnerability.
2. Contact the maintainer directly via GitHub: [@oleksandrmyhydiuk](https://github.com/oleksandrmyhydiuk).
3. Include the following details in your report:
   * Description of the vulnerability and affected component (`auth.py`, `database.py`, etc.);
   * Step-by-step instructions or proof-of-concept to reproduce the issue;
   * Potential impact and suggested remediation (if applicable).

All vulnerability reports will be reviewed within **48 hours**, and a fix will be prepared and released as quickly as possible.
