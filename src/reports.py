
import functools
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Union

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def report_decorator(file_name: Optional[str] = None) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Декоратор для записи результата функции-отчета в файл.

    :param file_name: Имя файла для сохранения отчета. Если не указано, будет использовано имя по умолчанию.
    :return: Декоратор для функции, формирующей отчет.
    """

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            result = func(*args, **kwargs)
            if file_name:
                output_file = file_name
            else:
                output_file = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(result)
            return result

        return wrapper

    return decorator


def category_expenses(transactions: pd.DataFrame, category: str, date: Optional[Union[str, datetime]] = None) -> float:
    """
    Рассчитывает траты по заданной категории за последние три месяца от переданной даты.

    :param transactions: DataFrame с транзакциями, содержащий колонки 'Дата операции', 'Сумма операции', 'Категория'.
    :param category: Название категории для расчета трат.
    :param date: Опциональная дата в формате 'YYYY-MM-DD'. Если не передана, берется текущая дата.
    :return: Сумма трат по заданной категории за последние три месяца.
    :raises ValueError: Если входные данные некорректны.
    """
    logging.info("Начало выполнения функции category_expenses")

    # Валидация входных данных
    if not isinstance(transactions, pd.DataFrame):
        logging.error("Тип аргумента transactions должен быть DataFrame")
        raise ValueError("Тип аргумента transactions должен быть DataFrame")
    if not isinstance(category, str):
        logging.error("Тип аргумента category должен быть string")
        raise ValueError("Тип аргумента category должен быть string")
    if date is not None:
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                logging.error("date должен быть в формате 'YYYY-MM-DD'")
                raise ValueError("date должен быть в формате 'YYYY-MM-DD'")
        elif not isinstance(date, datetime):
            logging.error("date должен быть объектом datetime")
            raise ValueError("date должен быть объектом datetime")
    else:
        # Получение текущей даты
        date = datetime.today()

    logging.info("Используемая дата: %s", date)

    # Приведение "Дата операции" к datetime для корректного сравнения
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="mixed", dayfirst=True)

    # Фильтрация транзакций по категории
    filtered_by_category = transactions[transactions["Категория"] == category]

    logging.info("Количество транзакций в категории '%s': %d", category, len(filtered_by_category))

    # Фильтрация транзакций по дате
    start_date = date - timedelta(days=90)
    filtered_by_date = filtered_by_category[
        (filtered_by_category["Дата операции"] >= start_date) & (filtered_by_category["Дата операции"] <= date)
    ]

    logging.info("Количество транзакций в категории '%s' за последние три месяца: %d", category, len(filtered_by_date))

    # Подсчет трат по категории
    total_expenses = filtered_by_date["Сумма операции"].sum()

    logging.info("Общие расходы по категории '%s' за последние три месяца: %.2f", category, total_expenses)

    return float(total_expenses)
