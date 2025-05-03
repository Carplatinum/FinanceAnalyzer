import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_transactions() -> List[Dict[str, Any]]:
    """
    Загружает транзакции из Excel-файла operations.xlsx.

    Returns:
        Список транзакций в формате списка словарей.
    """
    try:
        operations_path: Path = Path(__file__).parent.parent / 'operations.xlsx'
        df: pd.DataFrame = pd.read_excel(operations_path)
        return [dict((str(k), v) for k, v in item.items()) for item in df.to_dict('records')]
    except Exception as e:
        logging.error(f"Ошибка загрузки транзакций: {e}")
        return []


def cashback_categories_analysis(
    data: List[Dict[str, Any]],
    year: int,
    month: int
) -> str:
    """
    Считает кешбэк по категориям за указанный месяц.

    Args:
        data: Список транзакций (словарей).
        year: Год для фильтрации.
        month: Месяц для фильтрации.

    Returns:
        JSON-строка с суммами кешбэка по категориям, округлёнными до целых.
    """
    try:
        result: Dict[str, float] = {}
        for tx in data:
            try:
                dt_str: str = tx.get('Дата операции', '')
                if not dt_str:
                    continue

                try:
                    dt: datetime.datetime = datetime.datetime.strptime(dt_str, '%d.%m.%Y %H:%M:%S')
                except ValueError:
                    logging.warning(f"Неверный формат даты: {dt_str}")
                    continue

                if dt.year != year or dt.month != month:
                    continue

                category: str = tx.get('Категория', 'Неизвестно')
                amount_raw: Any = tx.get('Сумма операции', 0)

                try:
                    amount_str: str = str(amount_raw).replace(',', '.').strip()
                    amount: float = float(amount_str)
                except (ValueError, TypeError):
                    logging.warning(f"Неверный формат суммы операции: {amount_raw}")
                    continue

                cashback: float = abs(amount) * 0.02  # Кешбэк 2%
                result[category] = result.get(category, 0.0) + cashback

            except Exception as inner_e:
                logging.warning(f"Ошибка обработки транзакции {tx}: {inner_e}")

        result_rounded: Dict[str, int] = {k: round(v) for k, v in result.items()}
        return json.dumps(result_rounded, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка анализа категорий кешбэка: {e}")
        return json.dumps({})
