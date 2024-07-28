import json
import logging
from typing import Any, Dict, List

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def form_json_response(
    greeting: str,
    card_info: List[Dict[str, Any]],
    top_transactions: List[Dict[str, Any]],
    currency_rates: List[Dict[str, Any]],
    stock_prices: List[Dict[str, Any]],
) -> str:
    """
    Формирует JSON-ответ из различных частей данных.

    :param greeting: Приветственное сообщение.
    :param card_info: Информация по картам.
    :param top_transactions: Топ-5 транзакций.
    :param currency_rates: Курсы валют.
    :param stock_prices: Цены на акции.
    :return: Сформированный JSON-ответ.
    """
    logging.info("Формирование JSON-ответа")
    response = {
        "greeting": greeting,
        "cards": card_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(response, ensure_ascii=False, indent=4)
