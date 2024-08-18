import json

import pandas as pd
import pytest

from src.services import search_transactions


@pytest.fixture
def mock_data(monkeypatch):
    data = {
        "Дата операции": ["09.08.2024 13:03:51", "09.08.2024 12:20:41", "07.08.2024 22:07:07"],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "Описание": ["Магнит", "Магнит", "Магнит"],
        "Сумма операции": [-586.92, -1863.78, -516.95],
    }
    df = pd.DataFrame(data)
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: df)
    return df  # Возвращаем df, чтобы он был доступен в тестах


def test_search_transactions(mock_data):
    query = "Магнит"
    result = search_transactions(query)
    expected_result = mock_data[mock_data["Описание"].str.contains(query)].to_json(orient="records", force_ascii=False)
    assert json.loads(result) == json.loads(expected_result)


def test_search_transactions_empty_query(mock_data):
    query = ""
    result = search_transactions(query)
    expected_result = mock_data.to_json(orient="records", force_ascii=False)
    assert json.loads(result) == json.loads(expected_result)


def test_search_transactions_no_results(mock_data):
    query = "Пятерочка"
    result = search_transactions(query)
    expected_result = pd.DataFrame().to_json(orient="records", force_ascii=False)
    assert json.loads(result) == json.loads(expected_result)
