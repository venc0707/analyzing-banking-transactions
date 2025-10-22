import sys
import pytest
import pandas as pd
import os
from unittest.mock import patch, mock_open
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def setup_test_env():
    """Автоматическая настройка тестовой среды"""
    # Сохраняем оригинальные переменные окружения
    original_env = os.environ.copy()

    # Устанавливаем тестовые переменные окружения
    os.environ["API_KEY_RATE"] = "test_rate_key"
    os.environ["API_KEY_STOCK"] = "test_stock_key"

    yield

    # Восстанавливаем оригинальные переменные
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(autouse=True)
def setup_test_env():
    """Автоматическая настройка тестовой среды"""
    os.environ["API_KEY_RATE"] = "test_rate_key"
    os.environ["API_KEY_STOCK"] = "test_stock_key"
    yield


@pytest.fixture
def sample_dataframe():
    """Фикстура с примером DataFrame"""
    data = {
        "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 14:30:00", "25.12.2023 09:15:00"],
        "Номер карты": ["*1234", "*5678", "*1234"],
        "Сумма операции": [-1000, -2500, -500],
        "Бонусы (включая кэшбэк)": [10, 25, 5],
        "Категория": ["Еда", "Транспорт", "Развлечения"],
        "Описание": ["Супермаркет", "Такси", "Кино"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe():
    """Фикстура с пустым DataFrame"""
    return pd.DataFrame()


@pytest.fixture
def sample_settings():
    """Фикстура с примером настроек"""
    return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}


@pytest.fixture
def mock_excel_file():
    """Мок для чтения Excel файла"""
    data = {
        "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 14:30:00"],
        "Номер карты": ["*1234", "*5678"],
        "Сумма операции": [-1000, -2500],
        "Бонусы (включая кэшбэк)": [10, 25],
        "Категория": ["Еда", "Транспорт"],
        "Описание": ["Супермаркет", "Такси"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def complete_mock_data():
    """Более полные тестовые данные"""
    data = {
        "Дата операции": ["01.12.2023 10:00:00", "15.12.2023 14:30:00", "20.12.2023 09:15:00"],
        "Номер карты": ["*1234", "*5678", "*1234"],
        "Сумма операции": [-1000.0, -2500.0, -500.0],
        "Бонусы (включая кэшбэк)": [10.0, 25.0, 5.0],
        "Категория": ["Еда", "Транспорт", "Развлечения"],
        "Описание": ["Супермаркет", "Такси", "Кино"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_translations_data():
    """Фикстура с примером данных для переводов"""
    return pd.DataFrame(
        {
            "Категория": ["Переводы", "Еда", "Переводы"],
            "Описание": ["Иван П. перевод", "Магазин", "Мария С. платеж"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00", "03.01.2023 15:00:00"],
            "Сумма операции": [-1000, -500, -1500],
        }
    )


@pytest.fixture
def dataframe_missing_columns():
    """Фикстура с DataFrame без нужных колонок"""
    return pd.DataFrame({"Неправильная_колонка": [1, 2, 3], "Другая_колонка": ["a", "b", "c"]})
