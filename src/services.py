import logging
import os
from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY_CURRENCY = os.getenv("API_KEY_CURRENCY")
API_KEY_STOCK = os.getenv("API_KEY_STOCK")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Загрузка данных из Excel-файла.

    :param file_path: Путь к файлу Excel.
    :return: DataFrame с транзакциями.
    """
    logging.info(f"Загрузка транзакций из файла: {file_path}")
    try:
        transactions = pd.read_excel(file_path)
    except FileNotFoundError:
        logging.error(f"Файл '{file_path}' не найден.")
        raise ValueError(f"Файл '{file_path}' не найден.")
    except ValueError:
        logging.error(f"Файл '{file_path}' не является допустимым Excel файлом.")
        raise ValueError(f"Файл '{file_path}' не является допустимым Excel файлом.")

    logging.info(f"Транзакции успешно загружены. Количество записей: {len(transactions)}")
    return transactions


def filter_transactions_by_date(transactions: pd.DataFrame, date_time_str: str) -> pd.DataFrame:
    """
    Фильтрует транзакции по заданной дате.

    :param transactions: DataFrame с транзакциями.
    :param date_time_str: Строка с датой в формате 'YYYY-MM-DD HH:MM:SS'.
    :return: DataFrame с транзакциями, соответствующими заданной дате.
    """
    logging.info(f"Фильтрация транзакций по дате: {date_time_str}")
    try:
        end_date = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error(f"Некорректный формат даты и времени: {date_time_str}")
        raise ValueError("Некорректный формат даты и времени")

    start_date = end_date - pd.Timedelta(days=1)

    # Создание копии DataFrame перед выполнением операций
    transactions_copy = transactions.copy()

    # Преобразование 'Дата операции' в datetime с использованием .loc
    transactions_copy.loc[:, "Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Фильтрация транзакций по диапазону дат
    filtered_transactions = transactions_copy.loc[
        (transactions_copy["Дата операции"] >= start_date) & (transactions_copy["Дата операции"] <= end_date)
    ]

    logging.info(f"Найдено {len(filtered_transactions)} транзакций в заданном диапазоне дат.")
    return filtered_transactions


def calculate_card_info(transactions: pd.DataFrame) -> list:
    """
    Вычисляет информацию по картам, включая общую сумму расходов и кешбэк.

    :param transactions: DataFrame с транзакциями.
    :return: Список словарей с информацией по картам.
    """
    logging.info("Вычисление информации по картам.")
    if "Номер карты" not in transactions.columns or "Сумма операции" not in transactions.columns:
        logging.error("Необходимые столбцы отсутствуют в данных транзакций.")
        raise ValueError("Необходимые столбцы отсутствуют в данных транзакций.")

    # Вычисление общей суммы расходов и кешбэка по каждой карте
    card_info = (
        transactions.groupby("Номер карты")
        .agg(
            total_spent=pd.NamedAgg(column="Сумма операции", aggfunc="sum"),
            cashback=pd.NamedAgg(column="Сумма операции", aggfunc=lambda x: sum(x) * 0.01),
        )
        .reset_index()
    )

    # Извлечение последних 4 цифр номера карты
    card_info["last_digits"] = card_info["Номер карты"].astype(str).str[-4:]

    # Формирование списка словарей для JSON-ответа
    cards_data = []
    for _, row in card_info.iterrows():
        cards_data.append(
            {"last_digits": row["last_digits"], "total_spent": row["total_spent"], "cashback": row["cashback"]}
        )

    logging.info("Информация по картам успешно вычислена.")
    return cards_data


def get_top_5_transactions(transactions: pd.DataFrame) -> list:
    """
    Определяет топ-5 транзакций по сумме платежа.
    """
    logging.info("Определение топ-5 транзакций по сумме платежа.")
    if "Дата операции" not in transactions.columns or "Сумма платежа" not in transactions.columns:
        logging.error("В транзакциях DataFrame отсутствуют требуемые столбцы")
        raise ValueError("В транзакциях DataFrame отсутствуют требуемые столбцы")

    # Преобразование столбца даты в формат datetime, если это необходимо
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Сортировка по сумме платежа в порядке убывания и выбор топ-5 транзакций
    sorted_transactions = transactions.sort_values(by="Сумма платежа", ascending=False)
    top_5_transactions = sorted_transactions.head(5)

    # Формирование списка словарей для JSON-ответа
    top_transactions_data = top_5_transactions[["Дата операции", "Сумма платежа", "Категория", "Описание"]].copy()
    top_transactions_data["Дата операции"] = top_transactions_data["Дата операции"].dt.strftime("%d.%m.%Y")
    top_transactions_data = top_transactions_data.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )

    logging.info("Топ-5 транзакций успешно определены.")
    return top_transactions_data.to_dict(orient="records")


def fetch_currency_rates(api_key: str, base_currency: str, target_currencies: List[str]) -> List[Dict[str, float]]:
    """
    Получает курсы валют с ExchangeRate-API относительно базовой валюты и преобразует их к рублям.

    :param api_key: Ключ API для доступа к ExchangeRate-API.
    :param base_currency: Базовая валюта для вычислений (например, 'RUB').
    :param target_currencies: Список валют для получения курсов.
    :return: Список словарей с курсами валют относительно базовой валюты.
    """
    logging.info(f"Запрос курсов валют для базовой валюты: {base_currency}")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()

    rates = data.get("conversion_rates", {})
    currency_rates = []

    for currency in target_currencies:
        if currency in rates:
            # Преобразование курса валюты к рублю
            rate_to_rub = round(1 / rates[currency], 2)
            currency_rates.append({"currency": currency, "rate": rate_to_rub})
            logging.info(f"Курс для {currency}: {rate_to_rub} RUB")
        else:
            print(f"Курс для валюты {currency} не найден.")

    logging.info("Курсы валют успешно получены.")
    return currency_rates


def fetch_stock_prices(api_key: str, stocks: List[str]) -> List[Dict[str, object]]:
    """
    Получает цены (USD) на акции с Finnhub API.

    :param api_key: Ключ API для доступа к Finnhub.
    :param stocks: Список акций для получения цен.
    :return: Список словарей с ценами на акции.
    """
    logging.info(f"Запрос цен на акции: {', '.join(stocks)}")
    stock_prices = []

    for stock in stocks:
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": stock, "token": api_key}
        response = requests.get(url, params=params)
        data = response.json()

        if "c" in data:
            stock_prices.append({"stock": stock, "price": float(data["c"])})
            logging.info(f"Цена для {stock}: {data['c']} USD")
        else:
            print(f"Ошибка получения данных для акции: {stock}")

    logging.info("Цены на акции успешно получены.")
    return stock_prices
