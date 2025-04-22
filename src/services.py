import json
import datetime
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cashback_categories_analysis(
        data: List[Dict[str, Any]], year: int, month: int
) -> str:
    """
    Анализирует, сколько кешбэка можно получить по каждой категории
    за указанный месяц и год.
    """
    try:
        result: Dict[str, float] = {}  # Явная аннотация типа
        for tx in data:
            try:
                dt = datetime.datetime.strptime(tx['Дата операции'], '%Y-%m-%d')
            except (ValueError, KeyError):
                logging.warning(f"Пропущена транзакция с некорректной датой: {tx}")
                continue
            if dt.year == year and dt.month == month:
                category = tx.get('Категория', 'Неизвестно')
                amount = tx.get('Сумма операции', 0)
                cashback = abs(amount) * 0.01
                result[category] = result.get(category, 0) + cashback

        # Округляем до целых рублей
        result_rounded: Dict[str, int] = {k: round(v) for k, v in result.items()}
        logging.info(f"Кешбэк по категориям за {year}-{month:02}: {result_rounded}")
        return json.dumps(result_rounded, ensure_ascii=False)
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
        if limit <= 0:
            logging.warning("Предел округления должен быть положительным числом.")
            return json.dumps({"invested": 0.0}, ensure_ascii=False)

        def round_up(amount: float, limit: int) -> float:
            # Округляет отрицательную сумму расходов вверх до ближайшего лимита
            remainder = (-amount) % limit
            to_add = limit - remainder if remainder != 0 else 0
            return to_add

        filtered = [
            tx for tx in transactions
            if tx.get('Дата операции', '').startswith(month) and tx.get('Сумма операции', 0) < 0
        ]

        savings = [round_up(tx['Сумма операции'], limit) for tx in filtered]
        total = round(sum(savings), 2)
        logging.info(f"Инвесткопилка за {month} с лимитом {limit}: {total}")
        return json.dumps({"invested": total}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка расчета инвесткопилки: {e}")
        return json.dumps({"invested": 0.0}, ensure_ascii=False)
