import json
import datetime
import logging
import pandas as pd
import requests
from typing import List, Dict, Any, Union, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_user_settings(filepath: str) -> Dict[str, List[str]]:
    """Загружает пользовательские настройки из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            settings: Dict[str, List[str]] = json.load(f)
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": [], "user_stocks": []}


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Union[str, Optional[float]]]]:
    """Получает курсы валют, используя API exchangerate.host."""
    currency_rates: List[Dict[str, Union[str, Optional[float]]]] = []
    for currency in currencies:
        try:
            api_url = f"https://api.exchangerate.host/latest?base={currency}&symbols=RUB"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            rate: float = data['rates']['RUB']
            currency_rates.append({
                "currency": currency,  # str
                "rate": rate           # float
            })
            logging.info(f"Курс {currency} успешно получен: {rate}")
        except (requests.exceptions.RequestException, KeyError, TypeError) as e:
            logging.error(f"Ошибка для {currency}: {e}")
            currency_rates.append({
                "currency": currency,  # str
                "rate": None           # Optional[float]
            })
    return currency_rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Union[str, Optional[float]]]]:
    """Получает стоимость акций, используя API Finnhub."""
    stock_prices: List[Dict[str, Union[str, Optional[float]]]] = []
    for stock in stocks:
        try:
            api_url = f"https://finnhub.io/api/v1/quote?symbol={stock}&token=YOUR_API_KEY"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            price: Optional[float] = data.get('c')
            if price is None:
                raise KeyError("Цена закрытия 'c' не найдена")
            stock_prices.append({
                "stock": stock,  # str
                "price": price   # float
            })
            logging.info(f"Цена акции {stock} успешно получена: {price}")
        except (requests.exceptions.RequestException, KeyError, TypeError) as e:
            logging.error(f"Ошибка для {stock}: {e}")
            stock_prices.append({
                "stock": stock,  # str
                "price": None    # Optional[float]
            })
    return stock_prices


def get_greeting(datetime_str: str) -> str:
    """Определяет приветствие в зависимости от времени суток."""
    try:
        hour: int = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').hour
    except ValueError:
        logging.error("Неверный формат даты и времени для приветствия.")
        return "Здравствуйте"

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def analyze_transactions(df: pd.DataFrame) -> Dict[str, List[Dict[str, Union[str, float]]]]:
    """Анализирует транзакции и возвращает агрегированные данные."""
    cards_data: List[Dict[str, Union[str, float]]] = []
    top_transactions: List[Dict[str, Union[str, float]]] = []

    if df.empty:
        logging.warning("DataFrame пуст, возвращаем пустые результаты.")
        return {"cards": cards_data, "top_transactions": top_transactions}

    df = df.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')

    # Группируем по номеру карты, считаем общую сумму расходов и кешбэк (1%)
    card_groups = df.groupby('Номер карты')['Сумма платежа'].sum().reset_index()
    for _, row in card_groups.iterrows():
        card_number: str = row['Номер карты']
        total_spent: float = row['Сумма платежа']
        cashback: float = total_spent * 0.01
        cards_data.append({
            "last_digits": card_number[-4:] if isinstance(card_number, str) else "",
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2)
        })

    # Топ-5 транзакций по сумме платежа (по убыванию)
    top_5 = df.nlargest(5, 'Сумма платежа')
    for _, row in top_5.iterrows():
        date_str: str = row['Дата операции'].strftime('%d.%m.%Y') if pd.notnull(row['Дата операции']) else ""
        top_transactions.append({
            "date": date_str,
            "amount": round(row['Сумма платежа'], 2),
            "category": row.get('Категория', ''),
            "description": row.get('Описание', '')
        })

    return {"cards": cards_data, "top_transactions": top_transactions}
