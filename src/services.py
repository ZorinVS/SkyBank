import json
import logging
from typing import Any, Dict, List

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
