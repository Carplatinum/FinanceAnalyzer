from datetime import datetime
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import main_page


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Фикстура с тестовыми данными для операций."""
    data = {
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
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def mock_read_excel(sample_df: pd.DataFrame) -> Generator[MagicMock, None, None]:
    """Мокирует pandas.read_excel, возвращая sample_df."""
    with patch("pandas.read_excel", return_value=sample_df) as mock:
        yield mock


@pytest.fixture
def mock_utils_api() -> Generator[MagicMock, None, None]:
    """Мокирует функции из utils и views, используемые в main_page."""
    with patch("src.utils.get_currency_rates", return_value=[{"currency": "USD", "rate": 75.0}]), \
         patch("src.utils.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150.0}]), \
         patch("src.utils.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]}), \
         patch("src.views.get_greeting", return_value="Добрый день"), \
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
    """Проверяет корректность результата main_page при валидной дате."""
    result: Dict[str, Any] = main_page("2021-12-20 12:00:00")
    assert isinstance(result, dict)
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["greeting"] == "Добрый день"
