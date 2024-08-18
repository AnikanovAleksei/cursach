import json
import logging

import pandas as pd


def search_transactions(query):
    """
        Функция для поиска транзакций по заданному запросу.

        Параметры:
        query (str): Поисковый запрос, по которому производится фильтрация транзакций.

        Возвращает:
        str: JSON-строка с отфильтрованными транзакциями. Если произошла ошибка, возвращается JSON-строка с сообщением об ошибке.

        Исключения:
        Exception: Логгирует и возвращает ошибку в формате JSON в случае возникновения исключения при чтении файла или фильтрации данных.
        """
    try:
        df = pd.read_excel("../data/operations.xlsx")
        filtered_df = df[
            df[["Категория", "Описание"]].apply(lambda row: row.astype(str).str.contains(query).any(), axis=1)
        ]
        result = filtered_df.to_json(orient="records", force_ascii=False)
        logging.info(f"Search query: {query}, Results: {len(filtered_df)}")
        return result
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return json.dumps({"error": str(e)})


print(search_transactions("Магнит"))
