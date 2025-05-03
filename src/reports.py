import datetime
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

import pandas as pd

F = TypeVar('F', bound=Callable[..., str])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log_and_handle_errors(func: F) -> F:
    """
    Декоратор для логирования вызова функции и обработки исключений.
    Возвращает JSON-строку с пустым словарём в случае ошибки.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        logging.info(f"Вызов функции {func.__name__} с args={args}, kwargs={kwargs}")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Ошибка в {func.__name__}: {e}")
            return json.dumps({}, ensure_ascii=False)
    return cast(F, wrapper)


@log_and_handle_errors
def weekly_expenses_report(df: pd.DataFrame, report_date: Optional[datetime.datetime] = None) -> str:
    """
    Возвращает траты по дням недели за неделю, содержащую report_date, в формате JSON.

    Args:
        df: DataFrame с операциями, должен содержать колонку 'Дата операции' и 'Сумма операции'.
        report_date: Дата, по которой определяется неделя. Если None - используется текущая дата.

    Returns:
        JSON-строка с суммами трат по дням недели на русском языке.
    """
    if report_date is None:
        report_date = datetime.datetime.now()

    df = df.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')

    start_of_week = report_date - datetime.timedelta(days=report_date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    mask = (df['Дата операции'] >= start_of_week) & (df['Дата операции'] <= end_of_week)
    filtered = df.loc[mask]

    if filtered.empty:
        return json.dumps({}, ensure_ascii=False)

    day_name_map = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }

    filtered = filtered.copy()
    filtered['День недели'] = filtered['Дата операции'].dt.day_name().map(day_name_map)

    result = filtered.groupby('День недели')['Сумма операции'].sum().round(2)

    days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    result = result.reindex(days_order).dropna()

    return json.dumps(result.to_dict(), ensure_ascii=False)


@log_and_handle_errors
def expenses_by_category_report(
    df: pd.DataFrame,
    category: str,
    start_date: datetime.datetime
) -> str:
    """
    Формирует отчет о тратах по указанной категории за трёхмесячный период,
    заканчивающийся на start_date.

    Args:
        df: DataFrame с операциями. Ожидаются колонки 'Дата операции', 'Категория', 'Сумма операции'.
        category: Категория для фильтрации.
        start_date: Дата отсчёта (конец периода).

    Returns:
        JSON-строка с суммами трат по месяцам (ключ - 'YYYY-MM', значение - сумма с округлением).
    """
    if df.empty:
        logging.warning("DataFrame пуст, возвращаем пустой JSON.")
        return json.dumps({}, ensure_ascii=False)

    df = df.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')

    period_start = (start_date.replace(day=1) - pd.DateOffset(months=2)).replace(day=1)

    mask = (
        (df['Дата операции'] >= period_start) &
        (df['Дата операции'] <= start_date) &
        (df['Категория'] == category) &
        (df['Сумма операции'] < 0)
    )
    filtered = df.loc[mask]

    if filtered.empty:
        logging.info(f"Нет данных по категории '{category}' за период {period_start.date()} - {start_date.date()}")
        return json.dumps({}, ensure_ascii=False)

    filtered = filtered.copy()
    filtered['Год-Месяц'] = filtered['Дата операции'].dt.to_period('M').astype(str)

    result = filtered.groupby('Год-Месяц')['Сумма операции'].sum().round(2).abs()

    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
