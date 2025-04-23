import datetime
import pandas as pd
from typing import Any, Dict, List
from pprint import pprint

from views import main_page
from services import load_transactions, cashback_categories_analysis, investment_bank
from reports import weekly_expenses_report
from utils import (
    load_user_settings,
    get_currency_rates,
    get_stock_prices,
    get_greeting,
    analyze_transactions,
)


def main() -> None:
    """
    Главная функция запуска, которая выполняет вызовы всех основных функций
    из модулей и выводит результаты.
    """
    date_time_str: str = "2025-04-23 10:00:00"
    month_str: str = "2025-04"
    limit: int = 100

    print("=== Вызов из views.py: main_page ===")
    main_page_result: Dict[str, Any] = main_page(date_time_str)
    pprint(main_page_result)

    print("\n=== Вызов из services.py: load_transactions ===")
    transactions: List[Dict[str, Any]] = load_transactions()
    print(f"Загружено транзакций: {len(transactions)}")

    print("\n=== Вызов из services.py: cashback_categories_analysis ===")
    cashback_json: str = cashback_categories_analysis(transactions, year=2025, month=4)
    print(cashback_json)

    print("\n=== Вызов из services.py: investment_bank ===")
    investment_json: str = investment_bank(month_str, limit)
    print(investment_json)

    print("\n=== Вызов из reports.py: weekly_expenses_report ===")
    try:
        df: pd.DataFrame = pd.read_excel(r'C:\Users\ANTAQ\Desktop\PythonProjects\PyCharmProjects\FA\operations.xlsx')
    except Exception as e:
        print(f"Не удалось загрузить данные для отчёта: {e}")
        df = pd.DataFrame()

    report_date: datetime.datetime = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    report_json: str = weekly_expenses_report(df, report_date)
    print(report_json)

    print("\n=== Вызов из utils.py: load_user_settings ===")
    user_settings: Dict[str, List[str]] = load_user_settings('user_settings.json')
    pprint(user_settings)

    print("\n=== Вызов из utils.py: get_currency_rates ===")
    user_currencies: List[str] = user_settings.get('user_currencies', [])
    currency_rates: List[Dict[str, Any]] = get_currency_rates(user_currencies)
    pprint(currency_rates)

    print("\n=== Вызов из utils.py: get_stock_prices ===")
    user_stocks: List[str] = user_settings.get('user_stocks', [])
    stock_prices: List[Dict[str, Any]] = get_stock_prices(user_stocks)
    pprint(stock_prices)

    print("\n=== Вызов из utils.py: get_greeting ===")
    greeting: str = get_greeting(date_time_str)
    print(greeting)

    print("\n=== Вызов из utils.py: analyze_transactions ===")
    try:
        df_analysis: pd.DataFrame = pd.read_excel(r'C:\Users\ANTAQ\Desktop\PythonProjects\PyCharmProjects\FA\operations.xlsx')
    except Exception as e:
        print(f"Не удалось загрузить данные для анализа транзакций: {e}")
        df_analysis = pd.DataFrame()

    analysis_result: Dict[str, List[Dict[str, Any]]] = analyze_transactions(df_analysis)
    pprint(analysis_result)


if __name__ == "__main__":
    main()
