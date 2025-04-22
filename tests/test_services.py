import pytest
import json
from typing import List, Dict, Any
from src.services import cashback_categories_analysis, investment_bank


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"Дата операции": "2021-12-15", "Категория": "Фастфуд", "Сумма операции": -100.0},
        {"Дата операции": "2021-12-20", "Категория": "Каршеринг", "Сумма операции": -200.0},
        {"Дата операции": "2021-12-25", "Категория": "Фастфуд", "Сумма операции": -300.0},
        {"Дата операции": "2021-11-25", "Категория": "Фастфуд", "Сумма операции": -100.0},
        {"Дата операции": "invalid-date", "Категория": "Фастфуд", "Сумма операции": -50.0},
    ]


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (2021, 12, {"Фастфуд": 4, "Каршеринг": 2}),
        (2021, 11, {"Фастфуд": 1}),
        (2020, 1, {}),
    ]
)
def test_cashback_categories_analysis(
    sample_transactions: List[Dict[str, Any]],
    year: int,
    month: int,
    expected: Dict[str, int]
) -> None:
    """Проверяет расчет кешбэка по категориям для разных периодов."""
    result_json = cashback_categories_analysis(sample_transactions, year, month)
    result = json.loads(result_json)
    assert result == expected


def test_cashback_categories_analysis_empty() -> None:
    """Проверяет обработку пустого списка транзакций."""
    result_json = cashback_categories_analysis([], 2021, 12)
    assert result_json == "{}"


def test_investment_bank_valid(sample_transactions: List[Dict[str, Any]]) -> None:
    """Проверяет корректный расчет инвесткопилки для валидных данных."""
    result_json = investment_bank("2021-12", sample_transactions, 50)
    result = json.loads(result_json)
    assert result == {"invested": 0.0}


def test_investment_bank_rounding() -> None:
    """Проверяет правильность округления сумм для инвесткопилки."""
    transactions: List[Dict[str, Any]] = [
        {"Дата операции": "2021-12-15", "Сумма операции": -1712.0},
        {"Дата операции": "2021-12-20", "Сумма операции": -198.0},
    ]
    result_json = investment_bank("2021-12", transactions, 50)
    result = json.loads(result_json)
    assert result == {"invested": 40.0}


def test_investment_bank_empty() -> None:
    """Проверяет обработку пустого списка транзакций в инвесткопилке."""
    result_json = investment_bank("2021-12", [], 50)
    result = json.loads(result_json)
    assert result == {"invested": 0.0}


def test_investment_bank_zero_limit(sample_transactions: List[Dict[str, Any]]) -> None:
    """Проверяет обработку нулевого лимита округления."""
    result_json = investment_bank("2021-12", sample_transactions, 0)
    result = json.loads(result_json)
    assert result == {"invested": 0.0}
