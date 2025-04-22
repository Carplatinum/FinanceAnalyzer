import json
import logging
from datetime import datetime
from typing import Dict
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def weekly_expenses_report(df: pd.DataFrame, report_date: datetime = datetime.now()) -> str:
    """Возвращает траты по дням недели за указанную дату в JSON."""
    try:
        df = df.copy()
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], errors='coerce')
        filtered = df[df['Дата операции'].dt.date == report_date.date()]

        if filtered.empty:
            return json.dumps({}, ensure_ascii=False)

        filtered['День недели'] = filtered['Дата операции'].dt.day_name(locale='ru_RU')
        result = filtered.groupby('День недели')['Сумма операции'].sum().round(2).to_dict()

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка в weekly_expenses_report: {e}")
        return json.dumps({}, ensure_ascii=False)
