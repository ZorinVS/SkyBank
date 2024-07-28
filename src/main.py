import logging

from src.services import (
    API_KEY_CURRENCY,
    API_KEY_STOCK,
    calculate_card_info,
    fetch_currency_rates,
    fetch_stock_prices,
    filter_transactions_by_date,
    get_top_5_transactions,
    load_transactions,
)
from src.utils import generate_greeting, load_and_extract_user_settings
from src.views import form_json_response

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if API_KEY_CURRENCY is None:
    raise ValueError("API_KEY_CURRENCY не найден в окружении")
if API_KEY_STOCK is None:
    raise ValueError("API_KEY_STOCK не найден в окружении")

if __name__ == "__main__":
    # Заданные значения для выполнения функций
    date_time_str = "2020-04-27 19:30:30"
    file_path_transactions = "data/operations.xlsx"
    file_path_user_settings = "user_settings.json"
    base_currency = "RUB"

    # Загрузка данных транзакций
    all_transactions = load_transactions(file_path_transactions)

    # Фильтрация транзакций по дате
    transactions = filter_transactions_by_date(all_transactions, date_time_str)

    # Загрузка пользовательских настроек
    user_currencies, user_stocks = load_and_extract_user_settings(file_path_user_settings)

    # Генерация приветствия
    greeting = generate_greeting(date_time_str)

    # Вычисление информации по картам
    card_info = calculate_card_info(transactions)

    # Получение топ-5 транзакций
    top_transactions = get_top_5_transactions(transactions)

    # Получение курсов валют
    currency_rates = fetch_currency_rates(API_KEY_CURRENCY, base_currency, user_currencies)

    # Получение цен на акции
    stock_prices = fetch_stock_prices(API_KEY_STOCK, user_stocks)

    # Формирование JSON-ответа
    json_response = form_json_response(greeting, card_info, top_transactions, currency_rates, stock_prices)

    # Печать JSON-ответа
    print(json_response)
