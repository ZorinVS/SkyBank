import functools
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Union

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def report_decorator(
    file_name: Optional[str] = None,
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """
    Декоратор для записи результата функции-отчета в файл.

    :param file_name: Имя файла для сохранения отчета. Если не указано, будет использовано имя по умолчанию.
    :return: Декоратор для функции, формирующей отчет.
    """

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)
            if file_name:
                output_file = file_name
            else:
                output_file = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

            # Преобразование DataFrame в строку
            result_str = result.to_string(index=False)

            with open(output_file, "w", encoding="utf-8") as file:
                file.write(result_str)
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[Union[str, datetime]] = None
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца от переданной даты.

    :param transactions: DataFrame с транзакциями, содержащий колонки 'Дата операции', 'Сумма операции', 'Категория'.
    :param category: Название категории для расчета трат.
    :param date: Опциональная дата в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'.
    Если не передана, берется текущая дата.
    :return: DataFrame с транзакциями по заданной категории за последние три месяца.
    """
    logging.info("Начало выполнения функции spending_by_category")

    # Валидация входных данных
    if not isinstance(transactions, pd.DataFrame):
        logging.error("Тип аргумента transactions должен быть DataFrame")
        raise ValueError("Тип аргумента transactions должен быть DataFrame")
    if not isinstance(category, str):
        logging.error("Тип аргумента category должен быть string")
        raise ValueError("Тип аргумента category должен быть string")

    # Преобразование строки даты в объект datetime
    if date is not None:
        if isinstance(date, str):
            try:
                # Попытка распарсить дату с временем и без времени
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    logging.error("date должен быть в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'")
                    raise ValueError("date должен быть в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'")
        elif not isinstance(date, datetime):
            logging.error("date должен быть объектом datetime")
            raise ValueError("date должен быть объектом datetime")
    else:
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

    # Возвращение DataFrame с транзакциями по категории за последние три месяца
    return filtered_by_date
