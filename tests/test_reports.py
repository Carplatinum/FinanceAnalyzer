import pytest
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Any
from src.reports import weekly_expenses_report


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций для анализа расходов."""
    data: Dict[str, Any] = {
        'Дата операции': pd.to_datetime(['2023-10-02', '2023-10-02', '2023-10-03']),
        'Сумма операции': [-150.0, -50.0, -200.0]
    }
    return pd.DataFrame(data)


@pytest.mark.parametrize("date, expected", [
    (datetime(2023, 10, 2), {'Понедельник': -200.0}),
    (datetime(2023, 10, 3), {'Вторник': -200.0}),
])
def test_weekly_expenses_report(
    date: datetime,
    expected: Dict[str, float],
    sample_data: pd.DataFrame
) -> None:
    """Тест формирования недельного отчёта по расходам."""
    result: str = weekly_expenses_report(sample_data, date)
    parsed_result: Dict[str, float] = json.loads(result)
    assert parsed_result == expected


def test_empty_dataframe() -> None:
    """Тест с пустым DataFrame."""
    result: str = weekly_expenses_report(pd.DataFrame(), datetime.now())
    assert result == '{}'
