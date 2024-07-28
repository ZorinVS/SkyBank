from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import category_expenses, report_decorator


def test_category_expenses_valid_data(data_transactions):
    """
    Тестирует корректный расчет расходов по категории за последние три месяца.
    """
    df = pd.DataFrame(data_transactions)
    result = category_expenses(df, "Продукты", "2023-06-30")
    assert result == 600.0


def test_category_expenses_invalid_transactions_type():
    """
    Тестирует возникновение ошибки при некорректном типе аргумента transactions.
    """
    with pytest.raises(ValueError, match="Тип аргумента transactions должен быть DataFrame"):
        category_expenses([], "Продукты", "2023-06-30")


def test_category_expenses_invalid_category_type(data_transactions):
    """
    Тестирует возникновение ошибки при некорректном типе аргумента category.
    """
    df = pd.DataFrame(data_transactions)
    with pytest.raises(ValueError, match="Тип аргумента category должен быть string"):
        category_expenses(df, 123, "2023-06-30")


def test_category_expenses_invalid_date_format(data_transactions):
    """
    Тестирует возникновение ошибки при некорректном формате даты.
    """
    df = pd.DataFrame(data_transactions)
    with pytest.raises(ValueError, match="date должен быть в формате 'YYYY-MM-DD'"):
        category_expenses(df, "Продукты", "2023-06-31")


def test_category_expenses_no_date_provided(data_transactions):
    """
    Тестирует корректную работу функции при отсутствии аргумента date.
    """
    df = pd.DataFrame(data_transactions)
    with patch("src.reports.datetime") as mock_datetime:
        mock_datetime.today.return_value = datetime(2023, 6, 30)
        result = category_expenses(df, "Продукты")
        assert result == 600.0


def test_category_expenses_empty_transactions(data_transactions_empty):
    """
    Тестирует корректную работу функции при отсутствии транзакций в переданном DataFrame.
    """
    df = pd.DataFrame(data_transactions_empty)
    result = category_expenses(df, "Продукты", "2023-06-30")
    assert result == 0.0


@report_decorator()
def generate_report() -> str:
    return "Test report content"


def test_report_decorator_with_specified_file(tmp_path):
    """
    Тестирование создания отчета с указанным именем файла.
    """
    output_file = tmp_path / "test_report.txt"

    @report_decorator(output_file)
    def generate_report() -> str:
        return "Test report content"

    generate_report()

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as file:
        content = file.read()
        assert content == "Test report content"


def test_report_decorator_with_default_file_name(tmp_path, monkeypatch):
    """
    Тестирование создания отчета с именем файла по умолчанию.
    """
    monkeypatch.chdir(tmp_path)  # Изменяем текущую директорию на tmp_path

    @report_decorator()
    def generate_report_with_default_name() -> str:
        return "Test report with default name"

    generate_report_with_default_name()

    files = list(tmp_path.iterdir())
    assert len(files) == 1
    generated_file = files[0]

    assert generated_file.read_text(encoding="utf-8") == "Test report with default name"
    assert generated_file.name.startswith("report_")
    assert generated_file.name.endswith(".txt")


if __name__ == "__main__":
    pytest.main([__file__])
