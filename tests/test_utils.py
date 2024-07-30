import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
import requests
import requests_mock

from src.utils import (calculate_card_info, determine_time_of_day, fetch_currency_rates, fetch_stock_prices,
                       filter_transactions_by_date, generate_greeting, get_top_5_transactions,
                       load_and_extract_user_settings, load_transactions)


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


def test_load_transactions_valid_file(data_transactions):
    """
    Тестирует корректную загрузку транзакций из валидного Excel файла.
    """
    df = pd.DataFrame(data_transactions)

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = df
        result = load_transactions("valid_file.xlsx")
        assert result.equals(df)


def test_load_transactions_file_not_found():
    """
    Тестирует возникновение ошибки при отсутствии файла.
    """
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        with pytest.raises(ValueError, match="Файл 'missing_file.xlsx' не найден."):
            load_transactions("missing_file.xlsx")


def test_load_transactions_invalid_excel_file():
    """
    Тестирует возникновение ошибки при некорректном формате Excel файла.
    """
    with patch("pandas.read_excel", side_effect=ValueError):
        with pytest.raises(ValueError, match="Файл 'invalid_file.xlsx' не является допустимым Excel файлом."):
            load_transactions("invalid_file.xlsx")


def test_load_transactions_empty_file():
    """
    Тестирует корректную загрузку при пустом Excel файле.
    """
    empty_df = pd.DataFrame()

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = empty_df
        result = load_transactions("empty_file.xlsx")
        assert result.equals(empty_df)


def test_filter_transactions_by_date_valid_date(data_transactions_date_time):
    """
    Тестирует корректную фильтрацию транзакций по валидной дате.
    """
    df = pd.DataFrame(data_transactions_date_time[0])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date_time_str = "2023-07-27 12:00:00"
    filtered_df = filter_transactions_by_date(df, date_time_str)

    expected_data = data_transactions_date_time[1]
    expected_df = pd.DataFrame(expected_data)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    assert filtered_df.reset_index(drop=True).equals(expected_df.reset_index(drop=True))


def test_filter_transactions_by_date_invalid_date_format(data_transactions_date_time):
    """
    Тестирует возникновение ошибки при некорректном формате даты.
    """
    df = pd.DataFrame(data_transactions_date_time[0])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    invalid_date_time_str = "2023/07/27 12:00:00"
    with pytest.raises(ValueError, match="Некорректный формат даты и времени"):
        filter_transactions_by_date(df, invalid_date_time_str)


def test_filter_transactions_by_date_no_transactions_in_date_range(data_transactions_date_time):
    """
    Тестирует фильтрацию транзакций, если в заданном диапазоне дат нет транзакций.
    """
    df = pd.DataFrame(data_transactions_date_time[0])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date_time_str = "2024-07-27 12:00:00"
    filtered_df = filter_transactions_by_date(df, date_time_str)

    assert filtered_df.empty


def test_filter_transactions_by_date_transactions_near_boundaries():
    """
    Тестирует фильтрацию транзакций на границах диапазона дат.
    """
    data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00", "28.07.2023 12:00:00"],
        "Сумма операции": [100, 200, 300],
        "Категория": ["Продукты", "Развлечения", "Одежда"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    date_time_str = "2023-07-27 12:00:00"
    filtered_df = filter_transactions_by_date(df, date_time_str)

    expected_data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00"],
        "Сумма операции": [100, 200],
        "Категория": ["Продукты", "Развлечения"],
    }
    expected_df = pd.DataFrame(expected_data)
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    assert filtered_df.reset_index(drop=True).equals(expected_df.reset_index(drop=True))


def test_calculate_card_info_valid_data():
    """
    Тестирует корректную обработку валидных данных.
    """
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321"],
        "Сумма операции": [100, 200, 300],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [
        {"last_digits": "5678", "total_spent": 300, "cashback": 3.0},
        {"last_digits": "4321", "total_spent": 300, "cashback": 3.0},
    ]

    assert result == expected_result


def test_calculate_card_info_missing_columns():
    """
    Тестирует обработку данных с отсутствующими необходимыми столбцами.
    """
    data = {"Номер карты": ["1234567812345678", "8765432187654321"]}
    df = pd.DataFrame(data)

    with pytest.raises(ValueError, match="Необходимые столбцы отсутствуют в данных транзакций."):
        calculate_card_info(df)


def test_calculate_card_info_empty_dataframe():
    """
    Тестирует обработку пустого DataFrame.
    """
    df = pd.DataFrame(columns=["Номер карты", "Сумма операции"])

    result = calculate_card_info(df)

    expected_result = []

    assert result == expected_result


def test_calculate_card_info_single_card_multiple_transactions():
    """
    Тестирует обработку данных для одной карты с несколькими транзакциями.
    """
    data = {
        "Номер карты": ["1234567812345678", "1234567812345678", "1234567812345678"],
        "Сумма операции": [50, 150, 200],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [{"last_digits": "5678", "total_spent": 400, "cashback": 4.0}]

    assert result == expected_result


def test_calculate_card_info_multiple_cards_single_transaction_each():
    """
    Тестирует обработку данных для нескольких карт с одной транзакцией для каждой.
    """
    data = {
        "Номер карты": ["1234567812345678", "8765432187654321", "1122334455667788"],
        "Сумма операции": [100, 200, 300],
    }
    df = pd.DataFrame(data)

    result = calculate_card_info(df)

    expected_result = [
        {"last_digits": "5678", "total_spent": 100, "cashback": 1.0},
        {"last_digits": "4321", "total_spent": 200, "cashback": 2.0},
        {"last_digits": "7788", "total_spent": 300, "cashback": 3.0},
    ]

    # Сортировка результатов для корректного сравнения
    result = sorted(result, key=lambda x: x["last_digits"])
    expected_result = sorted(expected_result, key=lambda x: x["last_digits"])

    assert result == expected_result


def test_get_top_5_transactions_valid_data():
    """
    Тестирует определение топ-5 транзакций с корректными данными.
    """
    data = {
        "Дата операции": [
            "26.07.2023 12:00:00",
            "27.07.2023 12:00:00",
            "28.07.2023 12:00:00",
            "29.07.2023 12:00:00",
            "30.07.2023 12:00:00",
            "31.07.2023 12:00:00",
        ],
        "Сумма платежа": [100, 200, 300, 400, 500, 600],
        "Категория": ["Продукты", "Развлечения", "Одежда", "Техника", "Транспорт", "Рестораны"],
        "Описание": [
            "Покупка в супермаркете",
            "Билеты в кино",
            "Покупка одежды",
            "Покупка техники",
            "Такси",
            "Ужин в ресторане",
        ],
    }
    df = pd.DataFrame(data)

    expected_data = [
        {"date": "31.07.2023", "amount": 600, "category": "Рестораны", "description": "Ужин в ресторане"},
        {"date": "30.07.2023", "amount": 500, "category": "Транспорт", "description": "Такси"},
        {"date": "29.07.2023", "amount": 400, "category": "Техника", "description": "Покупка техники"},
        {"date": "28.07.2023", "amount": 300, "category": "Одежда", "description": "Покупка одежды"},
        {"date": "27.07.2023", "amount": 200, "category": "Развлечения", "description": "Билеты в кино"},
    ]

    result = get_top_5_transactions(df)
    assert result == expected_data


def test_get_top_5_transactions_insufficient_data():
    """
    Тестирует определение топ-5 транзакций, если данных меньше пяти.
    """
    data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00"],
        "Сумма платежа": [100, 200],
        "Категория": ["Продукты", "Развлечения"],
        "Описание": ["Покупка в супермаркете", "Билеты в кино"],
    }
    df = pd.DataFrame(data)

    expected_data = [
        {"date": "27.07.2023", "amount": 200, "category": "Развлечения", "description": "Билеты в кино"},
        {"date": "26.07.2023", "amount": 100, "category": "Продукты", "description": "Покупка в супермаркете"},
    ]

    result = get_top_5_transactions(df)
    assert result == expected_data


def test_get_top_5_transactions_missing_columns():
    """
    Тестирует выбрасывание ошибки при отсутствии необходимых столбцов.
    """
    data = {
        "Дата операции": ["26.07.2023 12:00:00", "27.07.2023 12:00:00"],
        "Категория": ["Продукты", "Развлечения"],
        "Описание": ["Покупка в супермаркете", "Билеты в кино"],
    }
    df = pd.DataFrame(data)

    with pytest.raises(ValueError, match="В транзакциях DataFrame отсутствуют требуемые столбцы"):
        get_top_5_transactions(df)


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


def test_fetch_currency_rates_valid_response():
    api_key = "test_api_key"
    base_currency = "RUB"
    target_currencies = ["USD", "EUR", "GBP"]

    # Mock API response
    mock_response = {"conversion_rates": {"USD": 0.013, "EUR": 0.011, "GBP": 0.009}}

    with requests_mock.Mocker() as m:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
        m.get(url, json=mock_response)

        result = fetch_currency_rates(api_key, base_currency, target_currencies)

        expected_result = [
            {"currency": "USD", "rate": round(1 / 0.013, 2)},
            {"currency": "EUR", "rate": round(1 / 0.011, 2)},
            {"currency": "GBP", "rate": round(1 / 0.009, 2)},
        ]

        assert result == expected_result


def test_fetch_currency_rates_missing_currency():
    api_key = "test_api_key"
    base_currency = "RUB"
    target_currencies = ["USD", "EUR", "INR"]

    # Mock API response
    mock_response = {"conversion_rates": {"USD": 0.013, "EUR": 0.011}}

    with requests_mock.Mocker() as m:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
        m.get(url, json=mock_response)

        result = fetch_currency_rates(api_key, base_currency, target_currencies)

        expected_result = [
            {"currency": "USD", "rate": round(1 / 0.013, 2)},
            {"currency": "EUR", "rate": round(1 / 0.011, 2)},
        ]

        assert result == expected_result


def test_fetch_currency_rates_api_error():
    api_key = "test_api_key"
    base_currency = "RUB"
    target_currencies = ["USD", "EUR"]

    with requests_mock.Mocker() as m:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
        m.get(url, status_code=500)

        with pytest.raises(requests.exceptions.RequestException):
            fetch_currency_rates(api_key, base_currency, target_currencies)


def test_fetch_stock_prices_success():
    """
    Тестирует успешное получение цен на акции.
    """
    api_key = "test_api_key"
    stocks = ["AAPL", "GOOGL"]

    # Mock response data
    mock_response_aapl = {"c": 150.0}  # текущая цена акции
    mock_response_googl = {"c": 2800.0}  # текущая цена акции

    with requests_mock.Mocker() as m:
        m.get("https://finnhub.io/api/v1/quote?symbol=AAPL&token=test_api_key", json=mock_response_aapl)
        m.get("https://finnhub.io/api/v1/quote?symbol=GOOGL&token=test_api_key", json=mock_response_googl)

        result = fetch_stock_prices(api_key, stocks)

        expected_result = [{"stock": "AAPL", "price": 150.0}, {"stock": "GOOGL", "price": 2800.0}]

        assert result == expected_result


def test_fetch_stock_prices_error():
    """
    Тестирует обработку ошибок при получении цен на акции.
    """
    api_key = "test_api_key"
    stocks = ["AAPL", "GOOGL"]

    # Mock response data with missing 'c' field
    mock_response_aapl = {"error": "data not found"}
    mock_response_googl = {"c": 2800.0}  # текущая цена акции

    with requests_mock.Mocker() as m:
        m.get("https://finnhub.io/api/v1/quote?symbol=AAPL&token=test_api_key", json=mock_response_aapl)
        m.get("https://finnhub.io/api/v1/quote?symbol=GOOGL&token=test_api_key", json=mock_response_googl)

        result = fetch_stock_prices(api_key, stocks)

        expected_result = [{"stock": "GOOGL", "price": 2800.0}]

        assert result == expected_result
