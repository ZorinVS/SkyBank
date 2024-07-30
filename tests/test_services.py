import json

import pandas as pd

from src.services import dataframe_to_dict_with_str, search_transactions


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
