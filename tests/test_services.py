import pytest
import json
from unittest.mock import patch
from typing import List, Dict, Any
from src.services import cashback_categories_analysis, investment_bank


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми данными транзакций."""
    return [
        {'Дата операции': '2023-01-01', 'Категория': 'Фастфуд', 'Сумма операции': -100},
        {'Дата операции': '2023-01-02', 'Категория': 'Фастфуд', 'Сумма операции': -200}
    ]


def test_cashback_analysis(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест анализа кешбэка по категориям."""
    result: str = cashback_categories_analysis(sample_transactions, 2023, 1)
    assert json.loads(result) == {'Фастфуд': 3}


def test_investment_bank() -> None:
    """Тест расчёта инвесткопилки."""
    mock_transactions: List[Dict[str, Any]] = [
        {'Дата операции': '2023-01-01', 'Сумма операции': -171},
        {'Дата операции': '2023-01-02', 'Сумма операции': -199}
    ]

    with patch('src.services.load_transactions') as mock_load:
        mock_load.return_value = mock_transactions
        result: str = investment_bank('2023-01', 100)
        assert json.loads(result) == {'invested': 30.0}
