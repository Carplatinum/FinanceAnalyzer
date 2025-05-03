import datetime
import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .utils import analyze_transactions, get_currency_rates, get_greeting, get_stock_prices, load_user_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main_page(date_time_str: str) -> Dict[str, Any]:
    try:
        date_time = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logging.error("Неверный формат даты и времени.")
        return {"error": "Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS"}

    start_date = date_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = date_time

    try:
        data_file = Path(__file__).parent.parent / 'data' / 'operations.xlsx'
        df = pd.read_excel(data_file)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')
        df = df[(df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)]

        # Учитываем только расходы (сумма операции < 0)
        df = df[df['Сумма операции'] < 0]

    except FileNotFoundError:
        logging.error(f"Файл {data_file} не найден.")
        return {"error": f"Файл {data_file} не найден."}
    except Exception as e:
        logging.error(f"Ошибка при чтении файла Excel: {e}")
        return {"error": f"Ошибка при чтении файла Excel: {str(e)}"}

    user_settings = load_user_settings('user_settings.json')
    user_currencies = user_settings.get('user_currencies', [])
    user_stocks = user_settings.get('user_stocks', [])

    currency_rates = get_currency_rates(user_currencies)
    stock_prices = get_stock_prices(user_stocks)

    transaction_analysis = analyze_transactions(df)

    response_data = {
        "greeting": get_greeting(datetime.datetime.now()),
        "cards": transaction_analysis.get("cards", []),
        "top_transactions": transaction_analysis.get("top_transactions", []),
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return response_data
