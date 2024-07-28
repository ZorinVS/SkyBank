# SkyBank — анализ банковских операций

## Описание

ююю

## Функциональность

SkyBank включает следующие модули:

- main.py
- reports.py
- services.py
- utils.py
- views.py

### Обзор функциональных модулей:

#### main.py
Основной модуль, который обеспечивает запуск приложения и взаимодействие с другими модулями для обработки данных.

#### reports.py
Модуль, отвечающий за генерацию отчетов на основе данных о транзакциях.

#### services.py
Модуль, обеспечивающий загрузку данных о транзакциях и курсов валют/акций из внешних источников.

#### utils.py
Модуль, содержащий вспомогательные функции для обработки данных.

#### views.py
Модуль, отвечающий за формирование и представление JSON-ответов на основе обработанных данных.

## Зависимости

Python 3.12
requests 2.32.3
types-requests 2.32.0.20249712
flake8 7.0.0
black 24.4.2
isort 5.13.2
mypy 1.10.0
pytest 8.2.2
pytest-cov 5.0.0
python-dotenv 1.0.1
openpyxl 3.1.5
pandas-stubs 2.2.2.240603

## Установка

1. Клонируйте репозиторий:
```bash
git clone git@github.com:ZorinVS/SkyBank.git
```
2. Установите зависимости:
```bash
poetry install
```

## Тестирование проекта

Тестирование проекта проводится с использованием пакета tests, который включает следующие файлы:

- init.py
- conftest.py
- test_reports.py
- test_services.py
- test_utils.py
- test_views.py

### Есть два способа выполнить тестирование проекта:
1. Используя терминал PyCharm:
```bash
pytest tests
```
2. Используя функциональность PyCharm:
- Откройте окно **Edit Configurations**.
- Выберите **pytest**.
- Укажите директорию, содержащую тесты, и директорию проекта.
- Подтвердите изменения, нажав **Apply** и **OK**.
- Запустите **pytest in tests**

## Документация:

Для получения дополнительной информации, пожалуйста, свяжитесь с...

## Лицензия:

Этот проект лицензирован в соответствии с условиями [MIT License](LICENSE).