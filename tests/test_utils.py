from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
import requests

from src.utils import (
    analyze_transactions,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    load_user_settings,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций."""
    data: Dict[str, List[Any]] = {
        'Дата операции': [
            datetime(2021, 12, 15),
            datetime(2021, 12, 20),
            datetime(2021, 12, 25),
        ],
        'Номер карты': ['*7197', '*5091', '*7197'],
        'Сумма операции': [-100.0, -200.0, -300.0],
        'Категория': ['Фастфуд', 'Каршеринг', 'Фастфуд'],
        'Описание': ['McDonalds', 'Ситидрайв', 'KFC']
    }
    return pd.DataFrame(data)


def test_load_user_settings_success() -> None:
    """Проверяет загрузку настроек из валидного JSON-файла."""
    data = '{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}'
    with patch("builtins.open", mock_open(read_data=data)):
        settings: Dict[str, List[str]] = load_user_settings("fake.json")
    assert settings == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


def test_load_user_settings_file_not_found() -> None:
    """Проверяет обработку отсутствия файла настроек."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        settings: Dict[str, List[str]] = load_user_settings("fake.json")
    assert settings == {"user_currencies": [], "user_stocks": []}


def test_load_user_settings_json_error() -> None:
    """Проверяет обработку невалидного JSON в файле настроек."""
    with patch("builtins.open", mock_open(read_data="not json")):
        settings: Dict[str, List[str]] = load_user_settings("fake.json")
    assert settings == {"user_currencies": [], "user_stocks": []}


@patch("src.utils.requests.get")
def test_get_currency_rates_success(mock_get: Any) -> None:
    """Проверяет успешное получение курсов валют через API."""
    mock_get.return_value.json.return_value = {"rates": {"RUB": 75.0}}
    mock_get.return_value.raise_for_status = lambda: None

    rates: List[Dict[str, Any]] = get_currency_rates(["USD"])
    assert rates == [{"currency": "USD", "rate": 75.0}]


@patch("src.utils.requests.get")
def test_get_currency_rates_failure(mock_get: Any) -> None:
    """Проверяет обработку ошибки при получении курсов валют."""
    mock_get.side_effect = requests.exceptions.RequestException()

    rates: List[Dict[str, Any]] = get_currency_rates(["USD"])
    assert rates == [{"currency": "USD", "rate": None}]


@patch("src.utils.requests.get")
def test_get_stock_prices_success(mock_get: Any) -> None:
    """Проверяет успешное получение цен акций через API."""
    mock_get.return_value.json.return_value = {"c": 150.0}
    mock_get.return_value.raise_for_status = lambda: None

    prices: List[Dict[str, Any]] = get_stock_prices(["AAPL"])
    assert prices == [{"stock": "AAPL", "price": 150.0}]


@patch("src.utils.requests.get")
def test_get_stock_prices_failure(mock_get: Any) -> None:
    """Проверяет обработку ошибки при получении цен акций."""
    mock_get.side_effect = requests.exceptions.RequestException()

    prices: List[Dict[str, Any]] = get_stock_prices(["AAPL"])
    assert prices == [{"stock": "AAPL", "price": None}]


@pytest.mark.parametrize(
    "datetime_str, expected",
    [
        ("2021-12-20 08:00:00", "Доброе утро"),
        ("2021-12-20 14:00:00", "Добрый день"),
        ("2021-12-20 20:00:00", "Добрый вечер"),
        ("2021-12-20 02:00:00", "Доброй ночи"),
        ("invalid", "Здравствуйте"),
    ],
)
def test_get_greeting(datetime_str: str, expected: str) -> None:
    """Проверяет определение приветствия в зависимости от времени."""
    assert get_greeting(datetime_str) == expected


def test_analyze_transactions(sample_df: pd.DataFrame) -> None:
    """Проверяет анализ транзакций и агрегацию данных по картам."""
    result: Dict[str, Any] = analyze_transactions(sample_df)

    assert "cards" in result
    assert "top_transactions" in result
    assert len(result["cards"]) == 2
    assert len(result["top_transactions"]) == 3

    card_7197: Dict[str, Any] = next(c for c in result["cards"] if c["last_digits"] == "7197")
    assert card_7197["total_spent"] == -400.0
