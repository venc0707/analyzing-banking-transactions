from src.utils import open_file_xlsx, greetings, data_analysis, cards, top_transactions, main_utils
import pytest
import pandas as pd
import json
import numpy as np
from unittest.mock import patch, mock_open, MagicMock


# Тесты для open_file_xlsx
def test_open_file_xlsx_success(mock_excel_file):
    """Тест успешного открытия файла"""
    with patch("pandas.read_excel", return_value=mock_excel_file):
        with patch("builtins.open", mock_open()):
            result = open_file_xlsx("test.xlsx")

    assert result is not None
    assert len(result) == 2
    assert "Дата операции" in result.columns


def test_open_file_xlsx_file_not_found():
    """Тест случая когда файл не найден"""
    with patch("pandas.read_excel", side_effect=FileNotFoundError()):
        result = open_file_xlsx("nonexistent.xlsx")

    assert result is None


def test_open_file_xlsx_empty_path():
    """Тест с пустым путем к файлу"""
    result = open_file_xlsx("")
    assert result is None


# Тесты для greetings
def test_greetings_morning():
    """Тест приветствия для утра"""
    result = greetings("2023-12-01 08:00:00")
    assert result == "Доброе утро"


def test_greetings_afternoon():
    """Тест приветствия для дня"""
    result = greetings("2023-12-01 14:00:00")
    assert result == "Добрый день"


def test_greetings_evening():
    """Тест приветствия для вечера"""
    result = greetings("2023-12-01 20:00:00")
    assert result == "Добрый вечер"


def test_greetings_night():
    """Тест приветствия для ночи"""
    result = greetings("2023-12-01 02:00:00")
    assert result == "Доброй ночи"


def test_greetings_invalid_format():
    """Тест с неверным форматом даты"""
    result = greetings("invalid-date")
    assert result == "Здравствуйте"


# Тесты для data_analysis
def test_data_analysis_success(sample_dataframe):
    """Тест успешного анализа данных"""
    result = data_analysis("2023-12-20 12:00:00", sample_dataframe)

    assert len(result) > 0
    assert "Дата операции" in result.columns


def test_data_analysis_empty_dataframe(empty_dataframe):
    """Тест с пустым DataFrame"""
    result = data_analysis("2023-12-20 12:00:00", empty_dataframe)
    assert result.empty


def test_data_analysis_invalid_date(sample_dataframe):
    """Тест с неверной датой"""
    result = data_analysis("invalid-date", sample_dataframe)
    assert result.empty


# Тесты для cards
def test_cards_success(sample_dataframe):
    """Тест успешного анализа карт"""
    result = cards(sample_dataframe)

    assert len(result) == 2  # Две уникальные карты
    assert "last_digits" in result[0]
    assert "total_spent" in result[0]
    assert "cashback" in result[0]


def test_cards_empty_dataframe(empty_dataframe):
    """Тест с пустым DataFrame"""
    result = cards(empty_dataframe)
    assert result == []


# Тесты для top_transactions
def test_top_transactions_success(sample_dataframe):
    """Тест успешного поиска топ транзакций"""
    result = top_transactions(sample_dataframe)

    assert len(result) <= 5
    if result:  # Если есть результаты
        assert "date" in result[0]
        assert "amount" in result[0]
        assert "category" in result[0]
        assert "description" in result[0]


def test_top_transactions_empty_dataframe(empty_dataframe):
    """Тест с пустым DataFrame"""
    result = top_transactions(empty_dataframe)
    assert result == []


# Тесты для main_utils
def test_main_utils_success():
    """Тест успешного выполнения main_utils с полным мокингом"""
    # Создаем тестовые данные с правильными типами
    test_data = pd.DataFrame(
        {
            "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 14:30:00"],
            "Номер карты": ["*1234", "*5678"],
            "Сумма операции": [1000.0, 2500.0],  # float вместо int64
            "Бонусы (включая кэшбэк)": [10.0, 25.0],  # float вместо int64
            "Категория": ["Еда", "Транспорт"],
            "Описание": ["Супермаркет", "Такси"],
        }
    )

    # Мокаем ВСЕ зависимости
    with patch("src.utils.open_file_xlsx", return_value=test_data):
        with patch("src.utils.data_analysis", return_value=test_data):
            with patch("src.utils.greetings", return_value="Добрый день"):
                with patch(
                    "src.utils.cards", return_value=[{"last_digits": "1234", "total_spent": 1000.0, "cashback": 10.0}]
                ):
                    with patch(
                        "src.utils.top_transactions",
                        return_value=[
                            {"date": "01.12.2023", "amount": 1000.0, "category": "Еда", "description": "Тест"}
                        ],
                    ):
                        with patch(
                            "src.views.get_user_setting",
                            return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]},
                        ):
                            with patch("src.views.exchange_rate", return_value=[{"currency": "USD", "rate": 75.5}]):
                                with patch("src.views.stock_prices", return_value=[{"stock": "AAPL", "price": 150.0}]):
                                    result = main_utils("2023-12-20 12:00:00")

    # Проверяем что результат - валидный JSON
    data = json.loads(result)

    # Проверяем наличие ожидаемых полей
    assert "greeting" in data
    assert "cards" in data
    assert "top_transactions" in data
    assert "currency_rates" in data
    assert "stock_prices" in data


def test_main_utils_file_not_found():
    """Тест когда файл не найден - ИСПРАВЛЕННЫЙ"""
    # Мокаем все чтобы изолировать тест
    with patch("src.utils.open_file_xlsx", return_value=None):
        with patch("src.views.get_user_setting", return_value={}):
            with patch("src.views.exchange_rate", return_value=[]):
                with patch("src.views.stock_prices", return_value=[]):
                    result = main_utils("2023-12-20 12:00:00")

    # Функция должна вернуть JSON с пустым словарем, но нужно проверить тип
    if isinstance(result, dict):
        data = result
    else:
        data = json.loads(result)
    assert data == {}


def test_main_utils_empty_file():
    """Тест с пустым файлом - ИСПРАВЛЕННЫЙ"""
    # Мокаем все зависимости
    with patch("src.utils.open_file_xlsx", return_value=pd.DataFrame()):
        with patch("src.views.get_user_setting", return_value={}):
            with patch("src.views.exchange_rate", return_value=[]):
                with patch("src.views.stock_prices", return_value=[]):
                    result = main_utils("2023-12-20 12:00:00")

    # Обрабатываем оба случая: когда возвращается dict и когда возвращается str
    if isinstance(result, dict):
        data = result
    else:
        data = json.loads(result)
    assert data == {}


def test_main_utils_error_handling():
    """Тест обработки ошибок - ИСПРАВЛЕННЫЙ"""
    # Создаем исключение в одной из функций
    with patch("src.utils.open_file_xlsx", side_effect=Exception("Test error")):
        with patch("src.views.get_user_setting", return_value={}):
            with patch("src.views.exchange_rate", return_value=[]):
                with patch("src.views.stock_prices", return_value=[]):
                    result = main_utils("2023-12-20 12:00:00")

    # Должен вернуться JSON с ошибкой
    data = json.loads(result)
    assert "error" in data


def test_main_utils_json_serialization_error():
    """Тест ошибки сериализации JSON"""
    # Создаем данные с неправильными типами
    with patch("src.utils.open_file_xlsx") as mock_open_file:
        with patch("src.utils.data_analysis") as mock_analysis:
            with patch("src.utils.greetings") as mock_greetings:
                with patch("src.utils.cards") as mock_cards:
                    with patch("src.utils.top_transactions") as mock_top:
                        with patch("src.views.get_user_setting") as mock_settings:
                            with patch("src.views.exchange_rate") as mock_rates:
                                with patch("src.views.stock_prices") as mock_stocks:
                                    # Настраиваем моки
                                    test_df = pd.DataFrame({"test": [1, 2, 3]})
                                    mock_open_file.return_value = test_df
                                    mock_analysis.return_value = test_df
                                    mock_greetings.return_value = "Добрый день"

                                    # Создаем данные с numpy типами которые не сериализуются
                                    mock_cards.return_value = [
                                        {
                                            "last_digits": "1234",
                                            "total_spent": np.int64(1000),  # Проблемный тип
                                            "cashback": np.float64(10.0),  # Проблемный тип
                                        }
                                    ]

                                    mock_top.return_value = [
                                        {
                                            "date": "01.12.2023",
                                            "amount": np.int64(1000),  # Проблемный тип
                                            "category": "Еда",
                                            "description": "Тест",
                                        }
                                    ]

                                    mock_settings.return_value = {}
                                    mock_rates.return_value = []
                                    mock_stocks.return_value = []

                                    result = main_utils("2023-12-20 12:00:00")

    # Должен вернуться JSON с ошибкой из-за проблем с сериализацией
    data = json.loads(result)
    assert "error" in data


def test_main_utils_partial_mocking():
    """Тест с частичным мокингом - только внешние зависимости"""
    # Создаем корректные тестовые данные
    test_data = pd.DataFrame(
        {
            "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 14:30:00"],
            "Номер карты": ["*1234", "*5678"],
            "Сумма операции": [1000.0, 2500.0],
            "Бонусы (включая кэшбэк)": [10.0, 25.0],
            "Категория": ["Еда", "Транспорт"],
            "Описание": ["Супермаркет", "Такси"],
        }
    )

    # Мокаем только внешние зависимости (файлы и API)
    with patch("pandas.read_excel", return_value=test_data):
        with patch("builtins.open", mock_open()):
            with patch("src.views.get_user_setting", return_value={"user_currencies": [], "user_stocks": []}):
                with patch("src.views.exchange_rate", return_value=[]):
                    with patch("src.views.stock_prices", return_value=[]):
                        result = main_utils("2023-12-20 12:00:00")

    # Проверяем базовую структуру
    data = json.loads(result)
    assert "greeting" in data
    assert "cards" in data
    assert "top_transactions" in data


# Простые тесты для основных функций
def test_individual_functions():
    """Тест что все основные функции работают"""
    test_df = pd.DataFrame(
        {
            "Дата операции": ["01.12.2023 10:00:00"],
            "Номер карты": ["*1234"],
            "Сумма операции": [1000.0],
            "Бонусы (включая кэшбэк)": [10.0],
            "Категория": ["Еда"],
            "Описание": ["Тест"],
        }
    )

    # Проверяем что функции не падают
    greeting = greetings("2023-12-20 12:00:00")
    assert greeting == "Добрый день"

    cards_result = cards(test_df)
    assert isinstance(cards_result, list)

    transactions_result = top_transactions(test_df)
    assert isinstance(transactions_result, list)

    analysis_result = data_analysis("2023-12-20 12:00:00", test_df)
    assert isinstance(analysis_result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
