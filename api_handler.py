# api_handler.py
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Отримуємо логер для цього модуля
logger = logging.getLogger(__name__)


class APIHandler:
    """Клас для взаємодії з API курсів валют."""

    def __init__(self):
        # Отримуємо ключ зі змінних оточення
        api_key = os.getenv("EXCHANGERATE_API_KEY")
        if not api_key:
            logger.critical("API ключ (EXCHANGERATE_API_KEY) не знайдено! Перевірте ваш .env файл.")
            raise ValueError("API ключ не знайдено! Перевірте ваш .env файл.")

        self.base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
        logger.info("API Handler успішно ініціалізовано.")

    def get_exchange_rate(self, base_currency, target_currency):
        """Отримує обмінний курс між двома валютами."""
        try:
            url = self.base_url + base_currency
            logger.info(f"Надсилання запиту до API: {url}")
            response = requests.get(url)
            response.raise_for_status()  # Перевірка на HTTP помилки
            data = response.json()
            if data['result'] == 'success' and target_currency in data['conversion_rates']:
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