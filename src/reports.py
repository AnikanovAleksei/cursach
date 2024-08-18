import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def write_report_to_file(filename=None):
    """
        Декоратор для записи результатов функции в файл.

        Параметры:
        filename (str): Имя файла, в который будет записан результат. Если не передано, используется имя по умолчанию 'report.json'.

        Возвращает:
        wrapper (function): Обёртка, которая выполняет основную функцию и записывает её результат в файл.
        """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Вызов функции и получение результата
            result1 = func(*args, **kwargs)

            # Если имя файла не передано, используем имя по умолчанию
            if filename is None:
                default_filename = "report.json"
            else:
                default_filename = filename

            # Запись результата в файл
            with open(default_filename, "w", encoding="utf-8") as file:
                json.dump(result, file, ensure_ascii=False, indent=4)

            return result1

        return wrapper

    return decorator


# Пример использования декораторов
# @write_report_to_file()  # Использование декоратора без параметра
# @write_report_to_file('custom_report.json')  # Использование декоратора с параметром


def spending_by_category(transactions1: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
       Функция для получения трат по определенной категории за последние 90 дней.

       Параметры:
       transactions1 (pd.DataFrame): Датафрейм с транзакциями, содержащий колонки 'Категория', 'Дата операции', 'Сумма операции'.
       category (str): Категория, по которой нужно отфильтровать транзакции.
       date (str, optional): Дата окончания периода в формате 'dd.mm.yyyy'. Если не указана, используется текущая дата.

       Возвращает:
       str: JSON-строка с отфильтрованными транзакциями.
       """
    # Если дата не передана, используем текущую дату
    if date is None:
        date = datetime.now().strftime("%d.%m.%Y")

    # Преобразуем строку даты в объект datetime
    end_date = datetime.strptime(date, "%d.%m.%Y")
    start_date = end_date - timedelta(days=90)

    # Фильтруем транзакции по категории и дате
    filtered_transactions = transactions1[
        (transactions1["Категория"] == category)
        & (pd.to_datetime(transactions1["Дата операции"], format="%d.%m.%Y %H:%M:%S") >= start_date)
        & (pd.to_datetime(transactions1["Дата операции"], format="%d.%m.%Y %H:%M:%S") <= end_date)
    ]

    # Выбираем только отрицательные суммы (траты)
    expenses = filtered_transactions[filtered_transactions["Сумма операции"] < 0]

    # Логируем количество найденных транзакций
    logging.info(f"Found {len(expenses)} transactions for category '{category}' from {start_date} to {end_date}")

    # Преобразуем датафрейм в словарь
    expenses_dict = expenses.to_dict(orient="records")

    # Преобразуем словарь в JSON
    expenses_json = json.dumps(expenses_dict, ensure_ascii=False, indent=4)

    return expenses_json


# Пример использования
if __name__ == "__main__":
    # Загрузка данных из Excel файла
    transactions = pd.read_excel("../data/operations.xlsx")

    # Вызов функции для категории "Супермаркеты"
    result = spending_by_category(transactions, "Супермаркеты", "03.08.2024")

    # Вывод результата в формате JSON
    print(result)
