import json
import datetime
import logging
import pandas as pd
import requests
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_user_settings(filepath: str) -> Dict[str, List[str]]:
    """Загружает пользовательские настройки из JSON-файла."""
    try:
        with open(filepath, 'r') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        logging.error(f"Файл настроек не найден: {filepath}")
        return {"user_currencies": [], "user_stocks": []}
    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON в файле: {filepath}")
        return {"user_currencies": [], "user_stocks": []}

def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """Получает курсы валют, используя API."""
    currency_rates: List[Dict[str, float]] = []
    for currency in currencies:
        try:
            # Замените на реальный API для получения курса валют
            api_url = f"https://api.exchangerate.host/latest?base={currency}&symbols=RUB"
            response = requests.get(api_url)
            response.raise_for_status()  # Проверка на ошибки HTTP
            data = response.json()
            rate = data['rates']['RUB']
            currency_rates.append({"currency": currency, "rate": rate})
            logging.info(f"Курс {currency} успешно получен")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при получении курса {currency}: {e}")
            currency_rates.append({"currency": currency, "rate": None})
        except (KeyError, TypeError) as e:
            logging.error(f"Ошибка обработки ответа API для {currency}: {e}")
            currency_rates.append({"currency": currency, "rate": None})
    return currency_rates

def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """Получает стоимость акций, используя API."""
    stock_prices: List[Dict[str, float]] = []
    for stock in stocks:
        try:
            # Замените на реальный API для получения цен на акции (например, Finnhub)
            api_url = f"https://finnhub.io/api/v1/quote?symbol={stock}&token=YOUR_API_KEY"
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            price = data['c']  # 'c' означает текущую цену закрытия
            stock_prices.append({"stock": stock, "price": price})
            logging.info(f"Цена акции {stock} успешно получена")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при получении цены акции {stock}: {e}")
            stock_prices.append({"stock": stock, "price": None})
        except (KeyError, TypeError) as e:
            logging.error(f"Ошибка обработки ответа API для {stock}: {e}")
            stock_prices.append({"stock": stock, "price": None})
    return stock_prices

def get_greeting(datetime_str: str) -> str:
    """Определяет приветствие в зависимости от времени суток."""
    hour = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def analyze_transactions(df: pd.DataFrame) -> Dict[str, Any]:
    """Анализирует транзакции и возвращает агрегированные данные."""
    cards_data: List[Dict[str, Any]] = []
    top_transactions: List[Dict[str, Any]] = []

    if df.empty:
        logging.warning("DataFrame is empty, returning default values.")
        return {"cards": [], "top_transactions": []}

    # Преобразуем столбец 'Дата операции' в datetime
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')

    # Группируем по номеру карты, считаем общую сумму расходов и кэшбэк
    card_groups = df.groupby('Номер карты')['Сумма платежа'].sum().reset_index()
    for _, row in card_groups.iterrows():
        card_number = row['Номер карты']
        total_spent = row['Сумма платежа']
        cashback = total_spent * 0.01
        cards_data.append({
            "last_digits": card_number[-4:],
            "total_spent": round(total_spent, 2),
            "cashback": round(cashback, 2)
        })

    # Топ-5 транзакций по сумме платежа
    top_5 = df.nlargest(5, 'Сумма платежа')
    for _, row in top_5.iterrows():
        top_transactions.append({
            "date": row['Дата операции'].strftime('%d.%m.%Y'),
            "amount": round(row['Сумма платежа'], 2),
            "category": row['Категория'],
            "description": row['Описание']
        })

    return {"cards": cards_data, "top_transactions": top_transactions}
