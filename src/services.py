import json
import datetime
import logging
from typing import List, Dict, Any
from functools import reduce

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cashback_categories_analysis(
    data: List[Dict[str, Any]], year: int, month: int
) -> str:
    """
    Анализирует, сколько кешбэка можно получить по каждой категории
    за указанный месяц и год.
    """
    try:
        # Фильтрация по дате
        filtered = filter(
            lambda x: (
                datetime.datetime.strptime(x['Дата операции'], '%Y-%m-%d').year == year and
                datetime.datetime.strptime(x['Дата операции'], '%Y-%m-%d').month == month
            ),
            data
        )
        # Группировка и подсчет кешбэка по категориям (1% от суммы)
        result = {}
        for tx in filtered:
            category = tx['Категория']
            cashback = abs(tx['Сумма операции']) * 0.01
            result[category] = result.get(category, 0) + cashback
        # Округление до целых рублей
        result = {k: round(v) for k, v in result.items()}
        logging.info(f"Кешбэк по категориям за {year}-{month:02}: {result}")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка анализа категорий кешбэка: {e}")
        return json.dumps({})


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> str:
    """
    Рассчитывает сумму, которую можно было бы накопить в "Инвесткопилке"
    за указанный месяц при заданном лимите округления.
    """
    try:
        # Фильтрация по месяцу и только по расходам (отрицательные суммы)
        filtered = filter(
            lambda x: x['Дата операции'].startswith(month) and x['Сумма операции'] < 0,
            transactions
        )
        # Вычисление накоплений через map и reduce
        def round_up(amount: float, limit: int) -> float:
            """Округлить сумму вверх до ближайшего limit."""
            return (int(-amount // limit) + (1 if -amount % limit else 0)) * limit

        savings = list(
            map(
                lambda tx: round_up(tx['Сумма операции'], limit) + tx['Сумма операции'],
                filtered
            )
        )
        total = round(reduce(lambda x, y: x + y, savings, 0), 2)
        logging.info(f"Инвесткопилка за {month} с лимитом {limit}: {total}")
        return json.dumps({"invested": total}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка расчета инвесткопилки: {e}")
        return json.dumps({"invested": 0})
