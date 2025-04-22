import json
import datetime
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_transactions() -> List[Dict[str, Any]]:
    """Загружает транзакции из Excel-файла."""
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
    """Считает кешбэк по категориям за указанный месяц."""
    try:
        result: Dict[str, float] = {}
        for tx in data:
            try:
                dt_str: str = tx.get('Дата операции', '')
                dt: Optional[datetime.datetime] = (
                    datetime.datetime.strptime(dt_str, '%Y-%m-%d')
                    if dt_str
                    else None
                )
                if not dt or dt.year != year or dt.month != month:
                    continue

                category: str = tx.get('Категория', 'Неизвестно')
                amount: Union[float, int, str] = tx.get('Сумма операции', 0)
                cashback: float = abs(float(amount)) * 0.01
                result[category] = result.get(category, 0.0) + cashback
            except Exception as inner_e:
                logging.warning(f"Ошибка обработки транзакции {tx}: {inner_e}")

        result_rounded: Dict[str, int] = {k: round(v) for k, v in result.items()}
        return json.dumps(result_rounded, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка анализа категорий кешбэка: {e}")
        return json.dumps({})


def investment_bank(month: str, limit: int) -> str:
    """Считает накопления для инвесткопилки за указанный месяц."""
    transactions: List[Dict[str, Any]] = load_transactions()
    try:
        if limit <= 0:
            return json.dumps({"invested": 0.0}, ensure_ascii=False)

        def round_up(amount: float, limit: int) -> float:
            """Округляет сумму расходов до ближайшего лимита."""
            remainder: float = (-amount) % limit
            return limit - remainder if remainder != 0 else 0

        filtered: List[Dict[str, Any]] = [
            tx for tx in transactions
            if (tx.get('Дата операции', '').startswith(month)
                and isinstance(tx.get('Сумма операции'), (int, float))
                and tx['Сумма операции'] < 0)
        ]

        savings: List[float] = [
            round_up(float(tx['Сумма операции']), limit)
            for tx in filtered
        ]
        total: float = round(sum(savings), 2)
        return json.dumps({"invested": total}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка расчета инвесткопилки: {e}")
        return json.dumps({"invested": 0.0}, ensure_ascii=False)
