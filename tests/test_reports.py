from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import report_decorator, spending_by_category  # Замените 'reports' на правильное имя вашего модуля

# Пример данных для тестов
transactions_data = {
    "Дата операции": ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01"],
    "Сумма операции": [100, 200, 300, 400],
    "Категория": ["Food", "Food", "Transport", "Food"],
}
transactions_df = pd.DataFrame(transactions_data)


# Тест для декоратора report_decorator
def test_report_decorator():
    @report_decorator("test_report.txt")
    def dummy_function():
        return pd.DataFrame({"column": [1, 2, 3]})

    with patch("builtins.open", mock_open()) as mock_file:
        result = dummy_function()
        mock_file.assert_called_with("test_report.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with(result.to_string(index=False))


# Тест для функции spending_by_category
def test_spending_by_category():
    result = spending_by_category(transactions_df, "Food", "2023-04-01")
    expected_data = {
        "Дата операции": [datetime(2023, 1, 1), datetime(2023, 2, 1), datetime(2023, 4, 1)],
        "Сумма операции": [100, 200, 400],
        "Категория": ["Food", "Food", "Food"],
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df.reset_index(drop=True))


# Тест для функции spending_by_category с неправильным форматом даты
def test_spending_by_category_invalid_date():
    with pytest.raises(ValueError, match="date должен быть в формате 'YYYY-MM-DD' или 'YYYY-MM-DD HH:MM:SS'"):
        spending_by_category(transactions_df, "Food", "2023-04-01 12:34")


# Тест для функции spending_by_category с неправильным типом данных для transactions
def test_spending_by_category_invalid_transactions():
    with pytest.raises(ValueError, match="Тип аргумента transactions должен быть DataFrame"):
        spending_by_category("not a DataFrame", "Food", "2023-04-01")


# Тест для функции spending_by_category с неправильным типом данных для category
def test_spending_by_category_invalid_category():
    with pytest.raises(ValueError, match="Тип аргумента category должен быть string"):
        spending_by_category(transactions_df, 123, "2023-04-01")


if __name__ == "__main__":
    pytest.main()
