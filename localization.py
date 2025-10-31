# localization.py
import json
import os
import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class LocalizationManager:
    """Керує завантаженням та наданням перекладених рядків."""

    def __init__(self, lang_dir='langs', default_lang='uk'):
        self._lang_dir = lang_dir
        self._translations = {}
        # Словник для зберігання посилань на віджети, які треба оновити
        self._widgets_to_translate = {}

        try:
            self.set_language(default_lang)
        except FileNotFoundError:
            logger.critical(f"Не вдалося знайти файл мови за замовчуванням: {default_lang}.json")
            # Створюємо порожній словник, щоб програма не впала
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
            # Після завантаження нової мови, оновлюємо всі зареєстровані віджети
            self._update_all_widgets()
        except FileNotFoundError:
            logger.error(f"Файл мови не знайдено: {path}")
            if not self._translations:
                raise FileNotFoundError(f"Файл мови не знайдено: {path}")

    def get(self, key: str, **kwargs) -> str:
        """
        Повертає перекладений рядок за ключем.
        Підтримує форматування рядків.
        """
        string = self._translations.get(key, f"_{key}_")  # Повертаємо _key_, якщо переклад не знайдено
        if kwargs:
            try:
                return string.format(**kwargs)
            except KeyError:
                logger.warning(f"Помилка форматування для ключа '{key}'")
                return string
        return string

    def register_widget(self, widget, key, config_type='text', **kwargs):
        """
        Реєструє віджет для автоматичного оновлення при зміні мови.
        config_type: 'text', 'title', 'heading'
        """
        self._widgets_to_translate[widget] = {'key': key, 'type': config_type, 'kwargs': kwargs}
        # Одразу встановлюємо текст при реєстрації
        self._update_widget(widget)

    def _update_widget(self, widget):
        """Оновлює текст одного віджета."""
        if widget in self._widgets_to_translate:
            config = self._widgets_to_translate[widget]
            key = config['key']
            config_type = config['type']
            kwargs = config['kwargs']

            translated_text = self.get(key, **kwargs)

            try:
                if config_type == 'text':
                    widget.config(text=translated_text)
                elif config_type == 'title':
                    widget.title(translated_text)
                elif config_type == 'heading':
                    # Для Treeview.heading(column_id, text="...")
                    # kwargs повинен містити {'column': column_id}
                    widget.heading(kwargs['column'], text=translated_text)
                elif config_type == 'labelframe':
                    widget.config(text=translated_text)
            except tk.TclError as e:
                logger.error(f"Не вдалося оновити віджет {widget}: {e}")
            except KeyError as e:
                logger.error(f"Помилка конфігурації віджета для ключа '{key}': відсутній {e}")

    def _update_all_widgets(self):
        """Оновлює текст на всіх зареєстрованих віджетах."""
        for widget in self._widgets_to_translate:
            self._update_widget(widget)