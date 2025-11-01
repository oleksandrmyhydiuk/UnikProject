import json
import os
import logging

logger = logging.getLogger(__name__)


class LocalizationManager:
    """Керує завантаженням та наданням перекладених рядків."""

    def __init__(self, lang_dir='langs', default_lang='uk'):
        self._lang_dir = lang_dir
        self._translations = {}

        try:
            self.set_language(default_lang)
        except FileNotFoundError:
            logger.critical(f"Не вдалося знайти файл мови за замовчуванням: {default_lang}.json")
            self._translations = {}
            self.current_lang = None

    def set_language(self, lang_code: str):
        """Завантажує файл мови та встановлює її як поточну."""
        path = os.path.join(self._lang_dir, f"{lang_code}.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._translations = json.load(f)
            self.current_lang = lang_code
            logger.info(f"Мову змінено на: {lang_code}")
        except FileNotFoundError:
            logger.error(f"Файл мови не знайдено: {path}")
            if not self._translations:
                raise FileNotFoundError(f"Файл мови не знайдено: {path}")

    def get(self, key: str, **kwargs) -> str:
        """
        Повертає перекладений рядок за ключем.
        Підтримує форматування рядків.
        """
        string = self._translations.get(key, f"_{key}_")
        if kwargs:
            try:
                return string.format(**kwargs)
            except KeyError:
                logger.warning(f"Помилка форматування для ключа '{key}'")
                return string
        return string