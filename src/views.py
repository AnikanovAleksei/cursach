import json
import logging
from datetime import datetime

from src.utils import analyze_transactions, currency, date_obj

DataFrame = "2024-08-08 12:34:56"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main(dataframe):
    """Основная функция для выполнения анализа транзакций, получения приветствия,
       курсов валют и стоимости акций на основе входных данных и пользовательских настроек."""
    file_path = "../data/operations.xlsx"
    setting = "../user_settings.json"

    # Преобразование строки в объект datetime
    check_date = (datetime.strptime(dataframe, "%Y-%m-%d %H:%M:%S")).strftime("%d.%m.%Y")

    greeting = date_obj()
    transactions = analyze_transactions(file_path, check_date)
    currency_data = currency(setting)

    result = {
        "greeting": greeting,
        "cards": transactions["cards"],
        "top_transactions": transactions["top_transactions"],
        "currency_rates": json.loads(currency_data)["currency_rates"],
        "stock_prices": json.loads(currency_data)["stock_prices"],
    }

    logging.info("Successfully executed main function")
    return json.dumps(result, ensure_ascii=False, indent=2)


# Пример использования
logging.info("Starting program")
logging.info("Program finished")
