import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class APIHandler:
    """Клас для взаємодії з API курсів валют."""

    def __init__(self, api_key: str | None = None):
        # Отримуємо ключ зі змінних оточення
        self.api_key = api_key if api_key is not None else os.getenv("EXCHANGERATE_API_KEY")
        if not self.api_key:
            logger.warning("API ключ (EXCHANGERATE_API_KEY) не знайдено! Перевірте ваш .env файл.")
            self.base_url = None
        else:
            self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/"
            logger.info("API Handler успішно ініціалізовано.")

    def get_exchange_rate(self, base_currency, target_currency):
        """Отримує обмінний курс між двома валютами."""
        if not self.base_url:
            logger.error("Неможливо отримати курс валют: API ключ не налаштовано.")
            return None
        try:
            url = self.base_url + base_currency
            logger.info(f"Надсилання запиту до API: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Перевірка на HTTP помилки
            data = response.json()
            if data.get('result') == 'success' and target_currency in data.get('conversion_rates', {}):
                rate = data['conversion_rates'][target_currency]
                logger.info(f"Отримано курс: 1 {base_currency} = {rate} {target_currency}")
                return rate
            else:
                error_type = data.get('error-type', 'Невідома помилка API')
                logger.warning(f"API повернуло помилку: {error_type}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка під час запиту до API: {e}", exc_info=True)
            return None

    def convert_currency(self, amount, from_currency, to_currency):
        """Конвертує суму з однієї валюти в іншу."""
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        return "Не вдалося отримати курс."