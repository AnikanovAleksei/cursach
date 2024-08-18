import json
import logging
import os
from datetime import datetime
from datetime import datetime as dt
from datetime import time, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API-ключа из переменной окружения
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def date_obj():
    """
       Функция для определения текущего времени и возвращения соответствующего приветствия.

       Возвращает:
       str: Приветствие в зависимости от текущего времени суток.
       """
    current_time = datetime.now().time()
    if current_time < time(12, 0):
        return "Доброе утро!"
    elif current_time < time(18, 0):
        return "Добрый день!"
    elif current_time < time(22, 0):
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def analyze_transactions(file_path, check_date):
    """Функция для анализа транзакций и вывода информации по картам и топ-5 транзакций"""

    # Чтение файла Excel
    df = pd.read_excel(file_path, engine="openpyxl")

    # Определение интервала дат
    end_date = dt.strptime(check_date, "%d.%m.%Y")
    start_date = end_date - timedelta(days=20)

    # Преобразование строковых дат в datetime и фильтрация по дате
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    result = {"cards": [], "top_transactions": []}

    # Группировка по номеру карты
    for card_num, group in filtered_df.groupby("Номер карты"):
        total_expense = abs(group["Сумма операции"]).sum()
        cashback = total_expense // 100

        result["cards"].append(
            {
                "last_digits": str(card_num)[-4:],  # Convert card_num to string before slicing
                "total_spent": round(total_expense, 2),
                "cashback": round(cashback, 2),
            }
        )

    # Сортировка транзакций по сумме и выбор топ-5
    top_transactions = filtered_df.nlargest(5, "Сумма операции")
    top_transactions = top_transactions[["Дата операции", "Сумма операции", "Категория", "Описание"]]
    top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%d.%m.%Y")
    top_transactions.columns = ["date", "amount", "category", "description"]
    result["top_transactions"] = top_transactions.sort_values(by="amount", ascending=False).to_dict(orient="records")

    return result


# Функция для чтения пользовательских настроек из файла
def read_user_settings(file_path):
    """
       Функция для чтения пользовательских настроек из файла.

       Параметры:
       file_path (str): Путь к файлу с пользовательскими настройками.

       Возвращает:
       dict: Словарь с пользовательскими настройками.
       """
    with open(file_path, "r") as file:
        return json.load(file)


# Функция для получения курсов валют из API Alpha Vantage
def get_currency_rates(api_key, currencies):
    """
       Функция для получения курсов валют из API Alpha Vantage.

       Параметры:
       api_key (str): API ключ для доступа к сервису Alpha Vantage.
       currencies (list): Список валют, для которых нужно получить курс.

       Возвращает:
       list: Список словарей с информацией о курсе валют.

       Исключения:
       Exception: Выбрасывает исключение в случае неудачного запроса к API.
       """
    url = "https://www.alphavantage.co/query"
    currency_data = []
    for currency1 in currencies:
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": currency1,
            "to_currency": "RUB",  # предположим, что мы хотим курс валют к рублю
            "apikey": api_key,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            exchange_rate = data.get("Realtime Currency Exchange Rate", {})
            if exchange_rate:
                currency_data.append({"currency": currency, "rate": float(exchange_rate.get("5. Exchange Rate", 0))})
        else:
            raise Exception(f"Error fetching currency rate for {currency}: {response.status_code}")
    return currency_data


# Функция для получения стоимости акций из API Alpha Vantage
def get_stock_prices(api_key, stocks):
    """ Функция для получения стоимости акций из API Alpha Vantage."""
    url = "https://www.alphavantage.co/query"
    stock_data = []
    for stock in stocks:
        params = {"function": "TIME_SERIES_DAILY", "symbol": stock, "apikey": api_key}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            time_series = data.get("Time Series (Daily)", {})
            if time_series:
                latest_date = sorted(time_series.keys())[0]
                latest_data = time_series[latest_date]
                stock_data.append({"stock": stock, "price": float(latest_data["4. close"])})
        else:
            raise Exception(f"Error fetching stock price for {stock}: {response.status_code}")
    return stock_data


def currency(setting):
    """Функция для обработки пользовательских настроек и получения информации по валютам и акциям."""
    user_settings = read_user_settings(setting)

    user_currencies = user_settings.get("user_currencies", [])
    user_stocks = user_settings.get("user_stocks", [])

    currency_rates = get_currency_rates(API_KEY, user_currencies)
    stock_prices = get_stock_prices(API_KEY, user_stocks)

    # Формирование результирующего JSON-объекта
    result = {"currency_rates": currency_rates, "stock_prices": stock_prices}

    # Вывод результата
    return json.dumps(result, ensure_ascii=False, indent=2)


logging.info("Result generated")
logging.info("Program finished")
