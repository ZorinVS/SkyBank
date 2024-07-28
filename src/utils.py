import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def determine_time_of_day(current_time: datetime) -> str:
    """
    Определяет время суток на основе текущего времени.

    :param current_time: объект datetime, представляющий текущее время.
    :return: Строка с приветствием.
    """
    logging.info(f"Определение времени суток для времени {current_time}")
    if 5 <= current_time.hour < 12:
        return "Доброе утро"
    elif 12 <= current_time.hour < 18:
        return "Добрый день"
    elif 18 <= current_time.hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def generate_greeting(date_time_str: str) -> str:
    """
    Генерирует приветственное сообщение на основе входной строки с датой и временем.

    :param date_time_str: Строка в формате 'YYYY-MM-DD HH:MM:SS'.
    :return: Строка с приветствием.
    """
    logging.info(f"Генерация приветствия для даты и времени: {date_time_str}")
    try:
        current_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        logging.error(f"Некорректный формат даты и времени: {date_time_str}")
    except ValueError:
        return "Некорректный формат даты и времени"

    greeting = determine_time_of_day(current_time)
    return greeting


def load_and_extract_user_settings(file_path: str) -> Tuple[List[str], List[str]]:
    """
    Загружает настройки пользователя из файла JSON и извлекает валюты и акции.

    :param file_path: Путь к файлу JSON с настройками пользователя.
    :return: Кортеж, содержащий два списка: user_currencies и user_stocks.
    :raises ValueError: Если файл не найден, не является допустимым JSON или отсутствуют необходимые ключи.
    """
    logging.info(f"Загрузка пользовательских настроек из файла: {file_path}")
    try:
        with open(file_path, "r") as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        logging.error(f"Файл '{file_path}' не найден.")
        raise ValueError(f"Файл '{file_path}' не найден.")
    except json.JSONDecodeError:
        logging.error(f"Файл '{file_path}' не является допустимым JSON-файлом.")
        raise ValueError(f"Файл '{file_path}' не является допустимым JSON-файлом.")

    required_keys = ["user_currencies", "user_stocks"]
    for key in required_keys:
        if key not in user_settings:
            logging.error(f"Ключ '{key}' не найден в файле user_settings.json")
            raise ValueError(f"Ключ '{key}' не найден в файле user_settings.json")

    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    # Проверка типов данных
    if not isinstance(user_currencies, list) or not all(isinstance(item, str) for item in user_currencies):
        logging.error("Значение 'user_currencies' должно быть списком строк.")
        raise ValueError("Значение 'user_currencies' должно быть списком строк.")
    if not isinstance(user_stocks, list) or not all(isinstance(item, str) for item in user_stocks):
        logging.error("Значение 'user_stocks' должно быть списком строк.")
        raise ValueError("Значение 'user_stocks' должно быть списком строк.")

    logging.info(f"Успешно загружены пользовательские настройки: {user_currencies}, {user_stocks}")
    return user_currencies, user_stocks


def dataframe_to_dict_with_str(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Преобразует DataFrame в список словарей, где значения полей "Категория" и "Описание"
    представлены в виде строк. Если значение не строка, оно преобразуется в строку.

    :param df: Исходный DataFrame.
    :return: Список словарей с преобразованными значениями полей.
    """
    result = []
    for _, row in df.iterrows():
        transaction = row.to_dict()
        if "Категория" in transaction:
            transaction["Категория"] = str(transaction["Категория"])
        if "Описание" in transaction:
            transaction["Описание"] = str(transaction["Описание"])
        result.append(transaction)
    return result


def search_transactions(transactions: List[Dict[str, Any]], query: str) -> str:
    """
    Ищет транзакции по описанию или категории.

    :param transactions: Список транзакций, каждая из которых содержит 'Описание' и 'Категория'.
    :param query: Строка для поиска.
    :return: JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории.
    """
    logging.info("Начало выполнения функции search_transactions")
    logging.debug("Поисковый запрос: %s", query)

    matching_transactions = [
        transaction
        for transaction in transactions
        if isinstance(transaction, dict)
        and (
            query.lower() in transaction.get("Описание", "").lower()
            or query.lower() in transaction.get("Категория", "").lower()
        )
    ]

    logging.info("Найдено %d подходящих транзакций", len(matching_transactions))
    logging.debug("Подходящие транзакции: %s", matching_transactions)

    json_response = json.dumps(matching_transactions, ensure_ascii=False)
    logging.info("Завершение выполнения функции search_transactions")

    return json_response
