import json
import os
import sys
from unittest.mock import patch
import pandas as pd
from src.views import main

# Добавляем путь к директории src в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@patch("src.views.currency")
@patch("src.views.analyze_transactions")
@patch("src.views.date_obj")
@patch("pandas.read_excel")
def test_main(mock_read_excel, mock_date_obj, mock_analyze_transactions, mock_currency):
    # Настройка фиктивных данных
    mock_date_obj.return_value = "Добрый день!"

    mock_analyze_transactions.return_value = {
        "cards": [
            {"last_digits": "4467", "total_spent": 42893.84, "cashback": 428.0},
            {"last_digits": "5907", "total_spent": 16500.0, "cashback": 165.0},
            {"last_digits": "6790", "total_spent": 2280.0, "cashback": 22.0},
            {"last_digits": "8446", "total_spent": 33731.78, "cashback": 337.0},
        ],
        "top_transactions": [
            {"date": "02.08.2024", "amount": 6850.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "05.08.2024", "amount": 5800.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "01.08.2024", "amount": 4000.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "02.08.2024", "amount": 2336.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "07.08.2024", "amount": 1000.0, "category": "Переводы", "description": "Перевод между счетами"},
        ],
    }

    mock_currency.return_value = json.dumps({"currency_rates": [], "stock_prices": []})

    # Имитация чтения файла Excel
    mock_df = pd.DataFrame(
        {
            "Дата операции": ["09.08.2024 13:03:51", "09.08.2024 12:20:41"],
            "Дата платежа": ["09.08.2024", "09.08.2024"],
            "Номер карты": ["*4467", "*4467"],
            "Статус": ["OK", "OK"],
            "Сумма операции": [-586.92, -1863.78],
            "Валюта операции": ["RUB", "RUB"],
            "Сумма платежа": [-586.92, -1863.78],
            "Валюта платежа": ["RUB", "RUB"],
            "Кэшбэк": [0.0, 0.0],
            "Категория": ["Супермаркеты", "Супермаркеты"],
            "MCC": [5411, 5411],
            "Описание": ["Магнит", "Магнит"],
            "Бонусы (включая кэшбэк)": [0.0, 0.0],
            "Округление на инвесткопилку": [0.0, 0.0],
            "Сумма операции с округлением": [586.92, 1863.78],
        }
    )
    mock_read_excel.return_value = mock_df

    # Входные данные
    dataframe = "2024-08-08 12:34:56"

    # Ожидаемый результат
    expected_result = {
        "greeting": "Добрый день!",
        "cards": [
            {"last_digits": "4467", "total_spent": 42893.84, "cashback": 428.0},
            {"last_digits": "5907", "total_spent": 16500.0, "cashback": 165.0},
            {"last_digits": "6790", "total_spent": 2280.0, "cashback": 22.0},
            {"last_digits": "8446", "total_spent": 33731.78, "cashback": 337.0},
        ],
        "top_transactions": [
            {"date": "02.08.2024", "amount": 6850.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "05.08.2024", "amount": 5800.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "01.08.2024", "amount": 4000.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "02.08.2024", "amount": 2336.0, "category": "Переводы", "description": "Перевод между счетами"},
            {"date": "07.08.2024", "amount": 1000.0, "category": "Переводы", "description": "Перевод между счетами"},
        ],
        "currency_rates": [],
        "stock_prices": [],
    }

    # Вызов тестируемой функции
    result = json.loads(main(dataframe))

    # Проверка результата
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


# Запуск теста
if __name__ == "__main__":
    test_main()
    print("Test passed successfully!")
