import requests
import os
from dotenv import load_dotenv

load_dotenv()

class APIHandler:
    def __init__(self):
        api_key = os.getenv("EXCHANGERATE_API_KEY")
        if not api_key:
            raise ValueError("API ключ не знайдено! Перевірте ваш .env файл.")

        self.base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"

    def get_exchange_rate(self, base_currency, target_currency):
        try:
            url = self.base_url + base_currency
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['result'] == 'success' and target_currency in data['conversion_rates']:
                return data['conversion_rates'][target_currency]
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Помилка API: {e}")
            return None

    def convert_currency(self, amount, from_currency, to_currency):
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        return "Не вдалося отримати курс."
