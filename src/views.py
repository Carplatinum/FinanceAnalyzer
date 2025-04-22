import datetime
import logging
import pandas as pd
from typing import Dict, Any
from .utils import load_user_settings, get_currency_rates, get_stock_prices, get_greeting, analyze_transactions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main_page(date_time_str: str) -> Dict[str, Any]:
    """
    Главная функция для страницы, возвращающая JSON-ответ с данными о транзакциях,
    курсах валют и ценах на акции.
    """
    try:
        date_time = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logging.error("Неверный формат даты и времени.")
        return {"error": "Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS"}

    start_date = date_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = date_time

    # Загрузка данных из Excel
    try:
        df = pd.read_excel(r'C:\\Users\\ANTAQ\\Desktop\\PythonProjects\\PyCharmProjects\\FA\\operations.xlsx')
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')
        df = df[(df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)]
    except FileNotFoundError:
        logging.error("Файл operations.xlsx не найден.")
        return {"error": "Файл operations.xlsx не найден."}
    except Exception as e:
        logging.error(f"Ошибка при чтении файла Excel: {e}")
        return {"error": f"Ошибка при чтении файла Excel: {str(e)}"}

    # Загрузка пользовательских настроек
    user_settings = load_user_settings('user_settings.json')
    user_currencies = user_settings.get('user_currencies', [])
    user_stocks = user_settings.get('user_stocks', [])

    # Получение данных с API
    currency_rates = get_currency_rates(user_currencies)
    stock_prices = get_stock_prices(user_stocks)

    # Анализ транзакций
    transaction_analysis = analyze_transactions(df)

    # Формирование JSON-ответа
    response_data: Dict[str, Any] = {
        "greeting": get_greeting(date_time_str),
        "cards": transaction_analysis["cards"],
        "top_transactions": transaction_analysis["top_transactions"],
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return response_data
