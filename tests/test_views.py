import json

import pytest

from src.views import form_json_response


@pytest.mark.parametrize(
    "greeting, card_info, top_transactions, currency_rates, stock_prices, expected",
    [
        (
            "Доброе утро",
            [{"card": "1234", "balance": 1000}],
            [{"transaction": "Покупка", "amount": 150}],
            [{"currency": "USD", "rate": 75.0}],
            [{"stock": "AAPL", "price": 150.0}],
            {
                "greeting": "Доброе утро",
                "cards": [{"card": "1234", "balance": 1000}],
                "top_transactions": [{"transaction": "Покупка", "amount": 150}],
                "currency_rates": [{"currency": "USD", "rate": 75.0}],
                "stock_prices": [{"stock": "AAPL", "price": 150.0}],
            },
        ),
        (
            "Добрый день",
            [],
            [],
            [],
            [],
            {"greeting": "Добрый день", "cards": [], "top_transactions": [], "currency_rates": [], "stock_prices": []},
        ),
        (
            "Добрый вечер",
            [{"card": "5678", "balance": 2000}],
            [{"transaction": "Снятие", "amount": 300}],
            [{"currency": "EUR", "rate": 90.0}],
            [{"stock": "GOOGL", "price": 2500.0}],
            {
                "greeting": "Добрый вечер",
                "cards": [{"card": "5678", "balance": 2000}],
                "top_transactions": [{"transaction": "Снятие", "amount": 300}],
                "currency_rates": [{"currency": "EUR", "rate": 90.0}],
                "stock_prices": [{"stock": "GOOGL", "price": 2500.0}],
            },
        ),
    ],
)
def test_form_json_response(greeting, card_info, top_transactions, currency_rates, stock_prices, expected):
    """
    Тестирует функцию form_json_response с различными комбинациями входных данных.
    """
    result = form_json_response(greeting, card_info, top_transactions, currency_rates, stock_prices)
    assert json.loads(result) == expected
