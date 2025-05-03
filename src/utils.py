import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()
FINNHUB_API_KEY: Optional[str] = os.getenv('API_KEY')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_user_settings(filepath: str) -> Dict[str, List[str]]:
    """
    Загружает настройки пользователя из JSON-файла.

    Args:
        filepath: Путь к JSON-файлу с настройками.

    Returns:
        Словарь с ключами 'user_currencies' и 'user_stocks'.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            settings: Dict[str, List[str]] = json.load(f)
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": [], "user_stocks": []}


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Union[str, Optional[float]]]]:
    """
    Получает курсы валют к рублю через API exchangerate.host.

    Args:
        currencies: Список кодов валют.

    Returns:
        Список словарей с валютой и курсом (или None при ошибке).
    """
    currency_rates: List[Dict[str, Union[str, Optional[float]]]] = []
    for currency in currencies:
        try:
            api_url: str = f"https://api.exchangerate.host/latest?base={currency}&symbols=RUB"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data: Dict = response.json()
            rate: float = data['rates']['RUB']
            currency_rates.append({"currency": currency, "rate": round(rate, 4)})
            logging.info(f"Курс {currency} успешно получен: {rate}")
        except (requests.exceptions.RequestException, KeyError, TypeError) as e:
            logging.error(f"Ошибка для {currency}: {e}")
            currency_rates.append({"currency": currency, "rate": None})
    return currency_rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Union[str, Optional[float]]]]:
    """
    Получает текущие цены акций через API Finnhub.

    Args:
        stocks: Список тикеров акций.

    Returns:
        Список словарей с тикером и ценой (или None при ошибке).
    """
    stock_prices: List[Dict[str, Union[str, Optional[float]]]] = []
    if not FINNHUB_API_KEY:
        logging.error("API ключ Finnhub не найден в переменных окружения.")
        for stock in stocks:
            stock_prices.append({"stock": stock, "price": None})
        return stock_prices

    for stock in stocks:
        try:
            api_url: str = f"https://finnhub.io/api/v1/quote?symbol={stock}&token={FINNHUB_API_KEY}"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data: Dict = response.json()
            price: Optional[float] = data.get('c')
            if price is None:
                raise KeyError("Цена закрытия 'c' не найдена")
            stock_prices.append({"stock": stock, "price": round(price, 2)})
            logging.info(f"Цена акции {stock} успешно получена: {price}")
        except (requests.exceptions.RequestException, KeyError, TypeError) as e:
            logging.error(f"Ошибка для {stock}: {e}")
            stock_prices.append({"stock": stock, "price": None})
    return stock_prices


def get_greeting(datetime_obj: Union[str, datetime.datetime]) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        datetime_obj: Строка или объект datetime с датой и временем.

    Returns:
        Строка с приветствием.
    """
    if isinstance(datetime_obj, str):
        try:
            dt: datetime.datetime = datetime.datetime.strptime(datetime_obj, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            logging.error("Неверный формат даты и времени для приветствия.")
            return "Здравствуйте"
    elif isinstance(datetime_obj, datetime.datetime):
        dt = datetime_obj
    else:
        logging.error("Неверный тип данных для приветствия.")
        return "Здравствуйте"

    hour: int = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def analyze_transactions(df: pd.DataFrame) -> Dict[str, List[Dict[str, Union[str, float]]]]:
    """
    Анализирует транзакции: суммирует траты по картам и выбирает топ-5 транзакций.

    Args:
        df: DataFrame с транзакциями.

    Returns:
        Словарь с данными по картам и топовыми транзакциями.
    """
    cards_data: List[Dict[str, Union[str, float]]] = []
    top_transactions: List[Dict[str, Union[str, float]]] = []

    if df.empty:
        logging.warning("DataFrame пуст, возвращаем пустые результаты.")
        return {"cards": cards_data, "top_transactions": top_transactions}

    df = df.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')

    card_groups = df.groupby('Номер карты')['Сумма операции'].sum().reset_index()
    for _, row in card_groups.iterrows():
        card_number: Union[str, None] = row['Номер карты']
        total_spent: float = row['Сумма операции']
        cashback: float = total_spent * 0.01
        cards_data.append({
            "last_digits": card_number[-4:] if isinstance(card_number, str) else "",
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2)
        })

    top_5 = df.nlargest(5, 'Сумма операции')
    for _, row in top_5.iterrows():
        date_str: str = row['Дата операции'].strftime('%d.%m.%Y') if pd.notnull(row['Дата операции']) else ""
        top_transactions.append({
            "date": date_str,
            "amount": round(row['Сумма операции'], 2),
            "category": row.get('Категория', ''),
            "description": row.get('Описание', '')
        })

    return {"cards": cards_data, "top_transactions": top_transactions}
