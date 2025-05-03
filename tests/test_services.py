import datetime
import json
from typing import Generator, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import expenses_by_category_report


@pytest.fixture
def sample_data() -> Generator[pd.DataFrame, None, None]:
    """Фикстура с тестовыми данными для expenses_by_category_report."""
    data = {
        'Дата операции': [
            '2025-02-10', '2025-02-15', '2025-03-05',
            '2025-03-20', '2025-04-01', '2025-04-22',
            '2025-01-10', '2025-04-15'
        ],
        'Категория': [
            'Продукты', 'Продукты', 'Транспорт',
            'Продукты', 'Продукты', 'Продукты',
            'Продукты', 'Развлечения'
        ],
        'Сумма операции': [
            -100.50, -200.75, -50.00,
            -300.00, -150.25, -400.00,
            -500.00, -100.00
        ]
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    yield df


@pytest.mark.parametrize(
    "category, expected_months",
    [
        ('Продукты', ['2025-02', '2025-03', '2025-04']),
        ('Транспорт', ['2025-03']),
        ('Неизвестная категория', []),
    ]
)
def test_expenses_by_category_report_basic(
    sample_data: pd.DataFrame,
    category: str,
    expected_months: List[str]
) -> None:
    """Параметризованный тест корректности сумм по категориям за 3 месяца."""
    start_date = datetime.datetime(2025, 4, 23)
    result_json = expenses_by_category_report(
        sample_data,
        category,
        start_date
    )
    result = json.loads(result_json)

    assert set(result.keys()) == set(expected_months)
    if expected_months:
        for month in expected_months:
            assert result.get(month, 0) > 0


def test_expenses_by_category_report_empty_df() -> None:
    """Проверяет обработку пустого DataFrame."""
    empty_df = pd.DataFrame(columns=['Дата операции', 'Категория', 'Сумма операции'])
    start_date = datetime.datetime(2025, 4, 23)
    category = 'Продукты'

    result_json = expenses_by_category_report(empty_df, category, start_date)
    result = json.loads(result_json)

    assert result == {}


def test_expenses_by_category_report_invalid_dates() -> None:
    """Проверяет, что некорректные даты игнорируются, корректные обрабатываются."""
    data = {
        'Дата операции': ['invalid_date', '2025-04-01'],
        'Категория': ['Продукты', 'Продукты'],
        'Сумма операции': [-100, -200]
    }
    df = pd.DataFrame(data)
    start_date = datetime.datetime(2025, 4, 23)
    category = 'Продукты'

    result_json = expenses_by_category_report(df, category, start_date)
    result = json.loads(result_json)

    assert '2025-04' in result
    assert abs(result['2025-04'] - 200) < 0.01


@patch('pandas.core.indexes.accessors.DatetimeProperties.to_period')
def test_expenses_by_category_report_mock_to_period(mock_to_period: MagicMock, sample_data: pd.DataFrame) -> None:
    """Тест с мокированием метода to_period для проверки вызова."""
    mock_to_period.return_value = sample_data['Дата операции']
    start_date = datetime.datetime(2025, 4, 23)
    category = 'Продукты'

    result_json = expenses_by_category_report(sample_data, category, start_date)
    result = json.loads(result_json)

    assert mock_to_period.called
    assert isinstance(result, dict)
