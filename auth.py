import os
import json
import logging
import platform
import asyncio  # Потрібно для асинхронних викликів Windows API
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

try:
    import keyring
except ImportError:
    keyring = None

logger = logging.getLogger(__name__)

AUTH_FILE = "auth_config.json"
SERVICE_NAME = "FinancialAssistant"
BIOMETRIC_TOKEN_USER = "biometric_auth_token"


class AuthManager:
    def __init__(self, auth_file: str = AUTH_FILE):
        self.ph = PasswordHasher()
        self.auth_file = auth_file

    def is_registered(self):
        """Перевіряє, чи створено вже пароль."""
        return os.path.exists(self.auth_file)

    def register_password(self, password):
        """Хешує пароль і зберігає хеш у файл."""
        if not password:
            raise ValueError("Пароль не може бути порожнім.")
        password_hash = self.ph.hash(password)
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump({"hash": password_hash}, f, indent=2)
        if keyring is not None:
            try:
                keyring.set_password(SERVICE_NAME, BIOMETRIC_TOKEN_USER, "enabled")
            except Exception as e:
                logger.debug(f"Не вдалося зберегти токен у системному сховищі keyring: {e}")
        logger.info("Пароль зареєстровано успішно.")

    def verify_password(self, password):
        """Перевіряє введений пароль через Argon2."""
        if not password or not self.is_registered():
            return False
        try:
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            stored_hash = data.get("hash")
            if not stored_hash:
                return False
            self.ph.verify(stored_hash, password)
            if self.ph.check_needs_rehash(stored_hash):
                self.register_password(password)
            return True
        except (VerifyMismatchError, InvalidHashError, FileNotFoundError, json.JSONDecodeError):
            return False

    def verify_biometrics(self):
        """
        Викликає системне вікно біометрії (Windows Hello).
        Повертає True, якщо користувач пройшов перевірку.
        """
        system = platform.system()

        if system == "Windows":
            return self._verify_windows_hello()
        else:
            # Для macOS/Linux потрібна інша реалізація (через localauthentication або pam)
            logger.warning("Біометрія наразі реалізована тільки для Windows.")
            return False

    def _verify_windows_hello(self):
        """Реалізація виклику Windows Hello через winsdk."""
        try:
            from winsdk.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerifierAvailability

            async def check_async():
                # 1. Перевіряємо, чи налаштовано Windows Hello на цьому ПК
                availability = await UserConsentVerifier.check_availability_async()

                if availability != UserConsentVerifierAvailability.AVAILABLE:
                    logger.warning(f"Windows Hello недоступний. Код статусу: {availability}")
                    return False

                # 2. Викликаємо вікно перевірки (FaceID, Fingerprint або PIN)
                result = await UserConsentVerifier.request_verification_async(
                    "Будь ласка, підтвердіть вхід у Фінансовий Асистент")

                # 3. Перевіряємо результат (0 = Verified)
                if result == 0:  # UserConsentVerifierResult.VERIFIED
                    logger.info("Біометрична верифікація успішна.")
                    return True
                else:
                    logger.warning(f"Біометрична верифікація не вдалася. Код: {result}")
                    return False

            # Запускаємо асинхронну функцію в синхронному коді
            return asyncio.run(check_async())

        except ImportError:
            logger.error("Бібліотека 'winsdk' не встановлена. Виконайте: pip install winsdk")
            return False
        except Exception as e:
            logger.error(f"Помилка Windows Hello: {e}", exc_info=True)
            return False