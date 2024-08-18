import json
import os
from datetime import datetime as dt
from unittest.mock import MagicMock, patch

import pandas as pd

from src.utils import analyze_transactions, date_obj, get_currency_rates, get_stock_prices, read_user_settings


# Тест для функции date_obj
def test_date_obj_morning(monkeypatch):
    # Подмена текущего времени на 9:00 утра
    mock_date = dt(2024, 8, 8, 9, 0, 0)
    monkeypatch.setattr("src.utils.datetime", MagicMock(wraps=dt))
    monkeypatch.setattr("src.utils.datetime.now", lambda: mock_date)

    assert date_obj() == "Доброе утро!"


def test_date_obj_day(monkeypatch):
    mock_date = dt(2024, 8, 8, 15, 0, 0)
    monkeypatch.setattr("src.utils.datetime", MagicMock(wraps=dt))
    monkeypatch.setattr("src.utils.datetime.now", lambda: mock_date)

    assert date_obj() == "Добрый день!"


def test_date_obj_evening(monkeypatch):
    mock_date = dt(2024, 8, 8, 19, 0, 0)
    monkeypatch.setattr("src.utils.datetime", MagicMock(wraps=dt))
    monkeypatch.setattr("src.utils.datetime.now", lambda: mock_date)

    assert date_obj() == "Добрый вечер!"


def test_date_obj_night(monkeypatch):
    mock_date = dt(2024, 8, 8, 23, 0, 0)
    monkeypatch.setattr("src.utils.datetime", MagicMock(wraps=dt))
    monkeypatch.setattr("src.utils.datetime.now", lambda: mock_date)

    assert date_obj() == "Доброй ночи!"


# Тест для функции analyze_transactions
def test_analyze_transactions(tmpdir):
    # Подготовка тестовых данных
    data = {
        "Дата операции": ["01.08.2024 10:00:00", "02.08.2024 11:00:00", "03.08.2024 12:00:00"],
        "Номер карты": ["1234567890124467", "1234567890125907", "1234567890124467"],
        "Сумма операции": [-1000.0, -2000.0, -1500.0],
        "Категория": ["Еда", "Транспорт", "Развлечения"],
        "Описание": ["Кафе", "Метро", "Кино"],
    }
    df = pd.DataFrame(data)

    # Сохранение DataFrame в Excel
    file_path = os.path.join(tmpdir, "operations.xlsx")
    df.to_excel(file_path, index=False)

    # Вызов функции
    result = analyze_transactions(file_path, "08.08.2024")

    # Проверка результата
    expected_result = {
        "cards": [
            {"last_digits": "4467", "total_spent": 2500.0, "cashback": 25.0},
            {"last_digits": "5907", "total_spent": 2000.0, "cashback": 20.0},
        ],
        "top_transactions": [
            {"date": "03.08.2024", "amount": -1500.0, "category": "Развлечения", "description": "Кино"},
            {"date": "02.08.2024", "amount": -2000.0, "category": "Транспорт", "description": "Метро"},
            {"date": "01.08.2024", "amount": -1000.0, "category": "Еда", "description": "Кафе"},
        ],
    }

    # Сортировка top_transactions в ожидаемом результате
    expected_result["top_transactions"] = sorted(
        expected_result["top_transactions"], key=lambda x: x["amount"], reverse=True
    )

    assert result == expected_result


# Тест для функции read_user_settings
def test_read_user_settings(tmpdir):
    # Подготовка тестового JSON файла
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
    file_path = os.path.join(tmpdir, "user_settings.json")
    with open(file_path, "w") as f:
        json.dump(settings, f)

    result = read_user_settings(file_path)
    assert result == settings


# Тест для функции get_stock_prices
@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Time Series (Daily)": {"2024-08-08": {"4. close": "178.67"}}}
    mock_get.return_value = mock_response

    result = get_stock_prices("fake_api_key", ["AAPL"])
    assert result == [{"stock": "AAPL", "price": 178.67}]
