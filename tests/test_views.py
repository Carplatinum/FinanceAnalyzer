import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.views import main_page
from typing import Dict, Any, Generator


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Фикстура с тестовыми данными транзакций."""
    data: Dict[str, list] = {
        'Дата операции': [
            datetime(2021, 12, 15),
            datetime(2021, 12, 20),
            datetime(2021, 12, 25),
        ],
        'Номер карты': ['*7197', '*5091', '*7197'],
        'Сумма платежа': [-100.0, -200.0, -300.0],
        'Категория': ['Фастфуд', 'Каршеринг', 'Фастфуд'],
        'Описание': ['McDonalds', 'Ситидрайв', 'KFC']
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_read_excel(sample_df: pd.DataFrame) -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования чтения Excel-файлов."""
    with patch("pandas.read_excel", return_value=sample_df) as mock:
        yield mock


@pytest.fixture
def mock_utils_api() -> Generator[MagicMock, None, None]:
    """Фикстура для мокирования внешних API и утилит."""
    with patch("src.utils.get_currency_rates", return_value=[{"currency": "USD", "rate": 75.0}]), \
         patch("src.utils.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150.0}]), \
         patch("src.utils.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]}), \
         patch("src.utils.get_greeting", return_value="Добрый день"), \
         patch("src.utils.analyze_transactions") as mock_analyze:
        mock_analyze.return_value = {
            "cards": [{"last_digits": "7197", "total_spent": -400.0, "cashback": -4.0}],
            "top_transactions": []
        }
        yield mock_analyze


def test_main_page_valid_date(
    mock_read_excel: MagicMock,
    mock_utils_api: MagicMock,
) -> None:
    """Проверяет корректную работу главной страницы с валидными данными."""
    result: Dict[str, Any] = main_page("2021-12-20 12:00:00")
    assert isinstance(result, dict)
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["greeting"] == "Добрый день"


def test_main_page_invalid_date() -> None:
    """Проверяет обработку невалидного формата даты."""
    result: Dict[str, Any] = main_page("invalid-date")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Неверный формат даты" in result["error"]


@patch("pandas.read_excel", side_effect=FileNotFoundError)
def test_main_page_file_not_found(mock_read: MagicMock) -> None:
    """Проверяет обработку отсутствия файла с транзакциями."""
    result: Dict[str, Any] = main_page("2021-12-20 12:00:00")
    assert "error" in result
    assert "не найден" in result["error"]
