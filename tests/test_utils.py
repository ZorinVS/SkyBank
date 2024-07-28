import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    dataframe_to_dict_with_str,
    determine_time_of_day,
    generate_greeting,
    load_and_extract_user_settings,
    search_transactions,
)


@pytest.mark.parametrize(
    "current_time, expected",
    [
        (datetime(2023, 7, 27, 9, 0, 0), "Доброе утро"),
        (datetime(2023, 7, 27, 13, 0, 0), "Добрый день"),
        (datetime(2023, 7, 27, 19, 0, 0), "Добрый вечер"),
        (datetime(2023, 7, 27, 23, 0, 0), "Доброй ночи"),
    ],
)
def test_determine_time_of_day(current_time, expected):
    """
    Тестирует функцию determine_time_of_day для разных времен суток.
    Проверяет, что функция возвращает правильное приветствие в зависимости от времени суток.
    """
    assert determine_time_of_day(current_time) == expected


@pytest.mark.parametrize(
    "date_time_str, expected",
    [
        ("2023-07-27 09:00:00", "Доброе утро"),
        ("2023-07-27 13:00:00", "Добрый день"),
        ("2023-07-27 19:00:00", "Добрый вечер"),
        ("2023-07-27 23:00:00", "Доброй ночи"),
        ("invalid_date", "Некорректный формат даты и времени"),
    ],
)
def test_generate_greeting(date_time_str, expected):
    """
    Тестирует функцию generate_greeting для различных временных строк.
    Проверяет, что функция возвращает правильное приветствие в зависимости от времени суток.
    """
    assert generate_greeting(date_time_str) == expected


def test_load_and_extract_user_settings_success():
    """
    Тестирует успешную загрузку и извлечение настроек пользователя.
    """
    mock_file_data = json.dumps({"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]})

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        user_currencies, user_stocks = load_and_extract_user_settings("dummy_path")

    assert user_currencies == ["USD", "EUR"]
    assert user_stocks == ["AAPL", "GOOGL"]


def test_load_and_extract_user_settings_file_not_found():
    """
    Тестирует случай, когда файл не найден.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(ValueError, match="Файл 'dummy_path' не найден."):
            load_and_extract_user_settings("dummy_path")


def test_load_and_extract_user_settings_invalid_json():
    """
    Тестирует случай, когда файл не является допустимым JSON.
    """
    invalid_json_data = "{user_currencies: [USD, EUR], user_stocks: [AAPL, GOOGL]}"  # invalid JSON

    with patch("builtins.open", mock_open(read_data=invalid_json_data)):
        with pytest.raises(ValueError, match="Файл 'dummy_path' не является допустимым JSON-файлом."):
            load_and_extract_user_settings("dummy_path")


def test_load_and_extract_user_settings_missing_keys():
    """
    Тестирует случай, когда в файле отсутствуют необходимые ключи.
    """
    mock_file_data = json.dumps(
        {
            "user_currencies": ["USD", "EUR"]
            # Missing "user_stocks"
        }
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        with pytest.raises(ValueError, match="Ключ 'user_stocks' не найден в файле user_settings.json"):
            load_and_extract_user_settings("dummy_path")


def test_load_and_extract_user_settings_invalid_data_types():
    """
    Тестирует случай, когда значения ключей 'user_currencies' и 'user_stocks' не являются списками строк.
    """
    mock_file_data = json.dumps(
        {"user_currencies": "USD, EUR", "user_stocks": ["AAPL", 1234]}  # invalid type  # invalid type
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        with pytest.raises(ValueError, match="Значение 'user_currencies' должно быть списком строк."):
            load_and_extract_user_settings("dummy_path")

    mock_file_data = json.dumps({"user_currencies": ["USD", "EUR"], "user_stocks": "AAPL, GOOGL"})  # invalid type

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        with pytest.raises(ValueError, match="Значение 'user_stocks' должно быть списком строк."):
            load_and_extract_user_settings("dummy_path")


def test_dataframe_to_dict_with_str_valid_data():
    """
    Тестирует преобразование DataFrame с корректными строковыми значениями.
    """
    data = {
        "Категория": ["Продукты", "Развлечения"],
        "Описание": ["Покупка в супермаркете", "Билеты в кино"],
        "Сумма": [150.0, 200.0],
    }
    df = pd.DataFrame(data)
    result = dataframe_to_dict_with_str(df)
    expected = [
        {"Категория": "Продукты", "Описание": "Покупка в супермаркете", "Сумма": 150.0},
        {"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0},
    ]
    assert result == expected


def test_dataframe_to_dict_with_str_mixed_data():
    """
    Тестирует преобразование DataFrame с числовыми и другими значениями в строковые значения.
    """
    data = {"Категория": ["Продукты", 1234], "Описание": [5678, "Билеты в кино"], "Сумма": [150.0, 200.0]}
    df = pd.DataFrame(data)
    result = dataframe_to_dict_with_str(df)
    expected = [
        {"Категория": "Продукты", "Описание": "5678", "Сумма": 150.0},
        {"Категория": "1234", "Описание": "Билеты в кино", "Сумма": 200.0},
    ]
    assert result == expected


def test_dataframe_to_dict_with_str_missing_columns():
    """
    Тестирует преобразование DataFrame с отсутствующими столбцами 'Категория' и 'Описание'.
    """
    data = {"Сумма": [150.0, 200.0]}
    df = pd.DataFrame(data)
    result = dataframe_to_dict_with_str(df)
    expected = [{"Сумма": 150.0}, {"Сумма": 200.0}]
    assert result == expected


def test_search_transactions_found():
    transactions = [
        {"Категория": "Продукты", "Описание": "Покупка в супермаркете", "Сумма": 150.0},
        {"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0},
        {"Категория": "Транспорт", "Описание": "Проезд на автобусе", "Сумма": 50.0},
    ]
    query = "кино"
    result = search_transactions(transactions, query)
    expected = [{"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0}]
    assert json.loads(result) == expected


def test_search_transactions_not_found():
    transactions = [
        {"Категория": "Продукты", "Описание": "Покупка в супермаркете", "Сумма": 150.0},
        {"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0},
        {"Категория": "Транспорт", "Описание": "Проезд на автобусе", "Сумма": 50.0},
    ]
    query = "одежда"
    result = search_transactions(transactions, query)
    expected = []
    assert json.loads(result) == expected


def test_search_transactions_case_insensitive():
    transactions = [
        {"Категория": "Продукты", "Описание": "Покупка в супермаркете", "Сумма": 150.0},
        {"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0},
        {"Категория": "Транспорт", "Описание": "Проезд на автобусе", "Сумма": 50.0},
    ]
    query = "КИНО"
    result = search_transactions(transactions, query)
    expected = [{"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0}]
    assert json.loads(result) == expected


def test_search_transactions_invalid_data():
    transactions = [
        {"Категория": "Продукты", "Описание": "Покупка в супермаркете", "Сумма": 150.0},
        {"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0},
        {"Категория": "Транспорт", "Описание": "Проезд на автобусе", "Сумма": 50.0},
        "Некорректная запись",
    ]
    query = "кино"
    result = search_transactions(transactions, query)
    expected = [{"Категория": "Развлечения", "Описание": "Билеты в кино", "Сумма": 200.0}]
    assert json.loads(result) == expected
